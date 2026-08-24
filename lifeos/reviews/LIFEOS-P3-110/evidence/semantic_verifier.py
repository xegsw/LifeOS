#!/usr/bin/env python3
"""P3-110 semantic verifier: derives outcomes from raw JSON/log/fixture evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
TARGET_TITLE = "LifeOS 今日 · 高保真受控候选"


def load(relative: str) -> object:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def issue(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": passed, "detail": detail})


def candidate_rect(data: dict[str, object], key: str, fields: tuple[str, str]) -> dict[str, object] | None:
    for item in data[key]:
        if item.get("title") == TARGET_TITLE:
            return item.get(fields[0]) or item.get(fields[1])
    return None


def validate(mutation: str | None = None) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    fixed = load("fixed-inputs.json")
    fixed_ok = fixed.get("input_count") == 10 and fixed.get("all_match") is True and all(item.get("match") is True for item in fixed["inputs"])
    if mutation == "hash_changed": fixed_ok = False
    issue(checks, "fixed-input-hashes", fixed_ok, "all fixed-input entries match their recorded hashes")

    build = load("build-results.json")
    build_ok = all(build[name]["exit_code"] == 0 for name in ["test", "build", "tauri_build"]) and build["network"] == "CARGO_NET_OFFLINE=true"
    issue(checks, "offline-locked-build", build_ok, "three recorded commands exited zero under CARGO_NET_OFFLINE=true")

    negative = load("negative-path-results.json")["startup_rejections"]
    if mutation == "negative_exit_zero": negative = copy.deepcopy(negative); next(iter(negative.values()))["exit_code"] = 0
    negative_ok = len(negative) == 8 and all(entry["exit_code"] != 0 and entry["panic_boundary_rejected"] for entry in negative.values())
    issue(checks, "negative-path-rejections", negative_ok, "all raw negative launches fail non-zero with controlled boundary rejection")

    snapshots = {name: load(f"snapshot-{name}.json") for name in ["nominal-after-first", "nominal-after-repeat", "nominal-after-conflict", "nominal-after-injected-failure", "nominal-after-ipc-negative", "nominal-before-sentinel-failure", "nominal-after-sentinel-failure", "nominal-after-reopen", "nominal-refresh-after-capture", "nominal-refresh-after"]}
    if mutation == "db_count_wrong": snapshots["nominal-after-repeat"] = copy.deepcopy(snapshots["nominal-after-repeat"]); snapshots["nominal-after-repeat"]["record_count"] = 2
    state_ok = (
        snapshots["nominal-after-first"].get("record_count") == 1 and snapshots["nominal-after-first"].get("audit_count") == 1 and
        snapshots["nominal-after-repeat"].get("record_count") == 1 and snapshots["nominal-after-repeat"].get("audit_count") == 2 and
        all(snapshots[name].get("record_count") == 1 and snapshots[name].get("audit_count") == 2 for name in ["nominal-after-conflict", "nominal-after-injected-failure", "nominal-after-ipc-negative", "nominal-after-reopen"]) and
        snapshots["nominal-before-sentinel-failure"].get("sentinel_sha256") == snapshots["nominal-after-sentinel-failure"].get("sentinel_sha256") and
        snapshots["nominal-before-sentinel-failure"].get("record_count") == snapshots["nominal-after-sentinel-failure"].get("record_count") and
        snapshots["nominal-before-sentinel-failure"].get("audit_count") == snapshots["nominal-after-sentinel-failure"].get("audit_count") and
        snapshots["nominal-refresh-after-capture"].get("record_count") == 1 and snapshots["nominal-refresh-after-capture"].get("audit_count") == 1 and
        snapshots["nominal-refresh-after-capture"].get("sentinel_sha256") == snapshots["nominal-refresh-after"].get("sentinel_sha256") and
        snapshots["nominal-refresh-after"].get("record_count") == 1 and snapshots["nominal-refresh-after"].get("audit_count") == 1
    )
    issue(checks, "lifecycle-and-sentinel", state_ok, "snapshots show commit-before-success, repeat audit only, negatives unchanged, refresh/reopen persisted")

    geometry_ok = True
    for name in ["geometry-nominal-700x760-default.json", "geometry-no-suggestion-700x760.json", "geometry-restricted-700x760.json"]:
        geometry = load(name)
        if mutation == "geometry_wrong" and name == "geometry-nominal-700x760-default.json": geometry = copy.deepcopy(geometry); geometry["ax_windows"][-1]["rect"]["width"] = 699
        ax = candidate_rect(geometry, "ax_windows", ("rect", "rect"))
        cg = candidate_rect(geometry, "cg_windows", ("bounds", "bounds"))
        geometry_ok = geometry_ok and geometry.get("ax_status") == 0 and ax is not None and cg is not None and ax.get("width") == 700 and ax.get("height") == 760 and cg.get("Width") == 700 and cg.get("Height") == 760
    issue(checks, "native-geometry", geometry_ok, "both native APIs report 700 by 760 for all three states")

    scan = load("static-scan.json")
    issue(checks, "static-privacy-network", scan.get("network_zero") is True and scan.get("only_expected_ipc") is True, "code/UI scan has no network marker and exactly three Tauri commands")

    required = ["visual/fixed-comparison.json", "screenshots/m015-skip-focus.png", "screenshots/m014-tamper.png", "screenshots/m014-schema-tamper.png"]
    evidence_ok = all((EVIDENCE / relative).is_file() for relative in required)
    if mutation == "missing_file": evidence_ok = False
    issue(checks, "required-raw-evidence", evidence_ok, "fixed comparison, keyboard, content and schema tamper artifacts exist")

    cleanup = load("cleanup.json")
    cleanup_ok = cleanup.get("work_exists") is False and cleanup.get("authorized_fixture_residue") == [] and cleanup.get("unit_regex_residue") == []
    if mutation == "cleanup_residue": cleanup_ok = False
    issue(checks, "authorized-path-cleanup", cleanup_ok, "work copy, fixtures, and unit-regex residue are all absent")

    passed = all(bool(item["passed"]) for item in checks)
    return {"verifier": "LIFEOS-P3-110 semantic verifier", "mutation": mutation, "passed": passed, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation", choices=["missing_file", "hash_changed", "cleanup_residue", "negative_exit_zero", "db_count_wrong", "geometry_wrong"])
    args = parser.parse_args()
    result = validate(args.mutation)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
