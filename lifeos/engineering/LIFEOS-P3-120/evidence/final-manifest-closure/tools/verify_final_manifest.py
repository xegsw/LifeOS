#!/usr/bin/env python3
"""Read-only, fail-closed verifier for the P3-120 final retained-asset manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
FINAL_ROOT = SCRIPT.parents[1]
P3_ROOT = SCRIPT.parents[3]
WORKSPACE = P3_ROOT.parents[2]
CANDIDATE = P3_ROOT / "candidate"
INITIAL_MANIFEST = P3_ROOT / "evidence" / "MANIFEST.md"
CANDIDATE_INVENTORY = P3_ROOT / "evidence" / "candidate-inventory.json"
REWORK_ROOT = P3_ROOT / "evidence" / "rework-1"
REWORK_MANIFEST = REWORK_ROOT / "MANIFEST.md"
DELIVERY = WORKSPACE / "lifeos" / "deliverables" / "LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md"
PM_REVIEW = WORKSPACE / "lifeos" / "reviews" / "LIFEOS-P3-120_pm_review.md"
INITIAL_DELIVERY_HASH = "ef644706a21976053b81fe1019ff9294dce89099e4ab9d199b52df13fda5bdec"
TABLE_ROW = re.compile(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$")
REWORK_ROW = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$")


def sha256(path: Path) -> str | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path, relative_to: Path) -> dict:
    info = path.lstat()
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "type": "regular" if stat.S_ISREG(info.st_mode) else "non-regular",
        "bytes": info.st_size,
        "sha256": sha256(path),
    }


def scan_regular(root: Path, exclusions: set[str]) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        retained_directories: list[str] = []
        for name in directories:
            item = current_path / name
            relative = item.relative_to(root).as_posix()
            if relative in exclusions:
                continue
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode):
                errors.append(f"non-regular directory link: {relative}")
            else:
                retained_directories.append(name)
        directories[:] = retained_directories
        for name in filenames:
            item = current_path / name
            relative = item.relative_to(root).as_posix()
            if relative in exclusions:
                continue
            info = item.lstat()
            if not stat.S_ISREG(info.st_mode):
                errors.append(f"non-regular file: {relative}")
                continue
            records.append(file_record(item, root))
    return sorted(records, key=lambda item: item["path"]), errors


def parse_initial_manifest() -> list[dict]:
    rows: list[dict] = []
    for line in INITIAL_MANIFEST.read_text(encoding="utf-8").splitlines():
        match = TABLE_ROW.match(line)
        if match:
            path, byte_count, digest = match.groups()
            rows.append({"path": path, "type": "regular", "bytes": int(byte_count), "sha256": digest, "lineage": "historical_initial"})
    if len(rows) != 101:
        raise ValueError(f"initial manifest table has {len(rows)} rows, expected 101")
    return rows


def parse_rework_manifest() -> list[dict]:
    rows: list[dict] = []
    for line in REWORK_MANIFEST.read_text(encoding="utf-8").splitlines():
        match = REWORK_ROW.match(line)
        if match:
            path, digest = match.groups()
            item = REWORK_ROOT / path
            info = item.lstat()
            rows.append({"path": path, "type": "regular" if stat.S_ISREG(info.st_mode) else "non-regular", "bytes": info.st_size, "sha256": digest, "lineage": "rework_1"})
    if len(rows) != 59:
        raise ValueError(f"rework manifest table has {len(rows)} rows, expected 59")
    return rows


def records_equal(left: list[dict], right: list[dict]) -> bool:
    return sorted(left, key=lambda item: item["path"]) == sorted(right, key=lambda item: item["path"])


def add(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def verify_record(record: object, root: Path, errors: list[str], label: str) -> None:
    if not isinstance(record, dict):
        errors.append(f"{label}: record missing")
        return
    relative = record.get("path")
    if not isinstance(relative, str) or not relative or relative.startswith("/") or ".." in Path(relative).parts:
        errors.append(f"{label}: unsafe path")
        return
    actual = root / relative
    try:
        info = actual.lstat()
    except FileNotFoundError:
        errors.append(f"{label}: missing {relative}")
        return
    add(stat.S_ISREG(info.st_mode), errors, f"{label}: non-regular {relative}")
    if not stat.S_ISREG(info.st_mode):
        return
    add(record.get("type") == "regular", errors, f"{label}: type mismatch {relative}")
    add(record.get("bytes") == info.st_size, errors, f"{label}: byte mismatch {relative}")
    add(record.get("sha256") == sha256(actual), errors, f"{label}: sha256 mismatch {relative}")


def expected_closure_exclusions(mode: str) -> set[str]:
    if mode == "draft":
        return {"FINAL_MANIFEST.json", "scope-payload.json", "verification-results.json", "mutation-results.json"}
    return {"FINAL_MANIFEST.json"}


def verify_manifest(payload: object, mode: str, closure_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["manifest is not a JSON object"]
    add(payload.get("schema") == "lifeos-p3-120/final-retained-manifest-v1", errors, "wrong manifest schema")
    add(payload.get("manifest_phase") == mode, errors, "wrong manifest phase")
    exclusions = expected_closure_exclusions(mode)
    add(set(payload.get("non_self_exclusions", [])) == exclusions, errors, "manifest exclusions do not match phase")
    required = {"current_candidate", "initial_historical", "rework_1", "current_delivery", "authority_pm_review", "final_closure"}
    add(set(payload.get("layers", {}).keys()) == required, errors, "manifest layers are missing or extra")
    layers = payload.get("layers", {})
    candidate_layer = layers.get("current_candidate", {})
    verify_record(candidate_layer.get("inventory_file"), WORKSPACE, errors, "candidate inventory")
    inventory = json.loads(CANDIDATE_INVENTORY.read_text(encoding="utf-8"))
    expected_candidate = []
    for item in inventory.get("files", []):
        expected_candidate.append({"path": item["path"], "type": item["type"], "bytes": item["bytes"], "sha256": item["sha256"], "lineage": "current_candidate"})
    candidate_records, candidate_scan_errors = scan_regular(CANDIDATE, set())
    candidate_live = [{**item, "lineage": "current_candidate"} for item in candidate_records]
    errors.extend(f"candidate: {error}" for error in candidate_scan_errors)
    add(records_equal(candidate_layer.get("entries", []), expected_candidate), errors, "candidate inventory records differ from frozen inventory")
    add(records_equal(candidate_live, expected_candidate), errors, "candidate live files have missing/extra/type/hash/byte drift")
    initial_layer = layers.get("initial_historical", {})
    initial_rows = parse_initial_manifest()
    add(records_equal(initial_layer.get("entries", []), initial_rows), errors, "initial historical rows differ from the initial Manifest")
    initial_manifest_record = initial_layer.get("manifest_file")
    verify_record(initial_manifest_record, WORKSPACE, errors, "initial Manifest")
    old_delivery_rows = [item for item in initial_rows if item["path"] == "lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md"]
    add(len(old_delivery_rows) == 1 and old_delivery_rows[0]["sha256"] == INITIAL_DELIVERY_HASH, errors, "initial delivery historical hash is absent or changed")
    for item in initial_rows:
        if item["path"] == "lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md":
            continue
        verify_record(item, WORKSPACE, errors, "initial historical payload")
    rework_layer = layers.get("rework_1", {})
    rework_rows = parse_rework_manifest()
    add(records_equal(rework_layer.get("entries", []), rework_rows), errors, "Rework-1 rows differ from its retained Manifest")
    verify_record(rework_layer.get("manifest_file"), WORKSPACE, errors, "Rework-1 Manifest")
    for item in rework_rows:
        verify_record(item, REWORK_ROOT, errors, "Rework-1 payload")
    verify_record(layers.get("current_delivery"), WORKSPACE, errors, "current delivery")
    delivery_record = layers.get("current_delivery", {})
    add(delivery_record.get("sha256") != INITIAL_DELIVERY_HASH, errors, "current delivery is incorrectly identified as the initial historical delivery")
    verify_record(layers.get("authority_pm_review"), WORKSPACE, errors, "PM Review authority")
    review_text = PM_REVIEW.read_text(encoding="utf-8")
    add("Final Manifest Closure Authorized" in review_text, errors, "PM Review lacks final Manifest closure authority")
    closure_layer = layers.get("final_closure", {})
    closure_base = closure_root or FINAL_ROOT
    add(not (closure_base / "disposable").exists() and not (closure_base / "disposable").is_symlink(), errors, "final closure disposable root remains")
    closure_records, closure_scan_errors = scan_regular(closure_base, exclusions)
    closure_expected = closure_layer.get("entries", [])
    add(records_equal(closure_expected, closure_records), errors, "final closure inventory has missing/extra/type/hash/byte drift")
    errors.extend(f"final closure: {error}" for error in closure_scan_errors)
    for item in closure_expected:
        verify_record(item, closure_base, errors, "final closure payload")
    if mode == "final":
        own_paths = [item.get("path") for item in closure_expected if isinstance(item, dict)]
        add("FINAL_MANIFEST.json" not in own_paths, errors, "final Manifest is self-referential")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    payload = json.loads(arguments.manifest.read_text(encoding="utf-8"))
    mode = "draft" if arguments.draft else "final"
    errors = verify_manifest(payload, mode)
    result = {"schema": "lifeos-p3-120/final-manifest-verification-v1", "mode": mode, "manifest": arguments.manifest.name, "error_count": len(errors), "errors": errors, "result": "PASS" if not errors else "NOT PASS"}
    if arguments.output:
        arguments.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": result["result"], "mode": mode, "error_count": len(errors)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
