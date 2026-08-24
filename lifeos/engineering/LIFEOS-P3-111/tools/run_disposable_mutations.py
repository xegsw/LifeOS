#!/usr/bin/env python3
"""Produce P3-111 Rework-1 mutation-specific Evidence without touching initial Evidence."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INITIAL = ROOT / "evidence"
EVIDENCE = INITIAL / "rework-1"
VERIFIER = ROOT / "tools" / "semantic_verifier.py"
EXCLUDE_NAMES = {"PAYLOAD_MANIFEST.json", "MANIFEST.md", "semantic-verifier-result.json"}
NAMES = ["missing_file", "hash_changed", "cleanup_residue", "negative_exit_zero", "db_count_wrong", "geometry_wrong"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_files(root: Path) -> list[dict[str, object]]:
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if path.name in EXCLUDE_NAMES or (relative.parts and relative.parts[0] == "disposable"):
            continue
        data = path.read_bytes()
        files.append({"path": relative.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return files


def build_manifest(root: Path, scope: str) -> dict[str, object]:
    payload = {"scope": scope, "file_count": 0, "files": []}
    payload["files"] = payload_files(root)
    payload["file_count"] = len(payload["files"])
    (root / "PAYLOAD_MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def summary(result: dict[str, object]) -> dict[str, object]:
    return {
        "passed": result.get("passed"),
        "missing": result.get("missing"),
        "extra": result.get("extra"),
        "drift_paths": [item["path"] for item in result.get("hash_or_bytes_drift", [])],
        "semantic_errors": result.get("semantic_errors"),
    }


EXPECTED = {
    "missing_file": {"missing": ["raw/geometry.json"], "extra": [], "drift_paths": [], "semantic_errors": ["unreadable:raw/geometry.json:FileNotFoundError"]},
    "hash_changed": {"missing": [], "extra": [], "drift_paths": ["raw/static-results.json"], "semantic_errors": []},
    "cleanup_residue": {"missing": [], "extra": [], "drift_paths": ["raw/cleanup.json"], "semantic_errors": ["cleanup"]},
    "negative_exit_zero": {"missing": [], "extra": [], "drift_paths": ["raw/negative-results.json"], "semantic_errors": ["negative"]},
    "db_count_wrong": {"missing": [], "extra": [], "drift_paths": ["raw/fixed-lifecycle.json"], "semantic_errors": ["lifecycle"]},
    "geometry_wrong": {"missing": [], "extra": [], "drift_paths": ["raw/geometry.json"], "semantic_errors": ["geometry"]},
}

def mutate(copy_root: Path, name: str) -> None:
    if name == "missing_file": (copy_root / "raw/geometry.json").unlink()
    elif name == "hash_changed": (copy_root / "raw/static-results.json").write_bytes((copy_root / "raw/static-results.json").read_bytes() + b" ")
    elif name == "cleanup_residue":
        path = copy_root / "raw/cleanup.json"; value = json.loads(path.read_text()); value["fixture_residue_count"] = 1; path.write_text(json.dumps(value) + "\n")
    elif name == "negative_exit_zero":
        path = copy_root / "raw/negative-results.json"; value = json.loads(path.read_text()); value["unknown_ipc_exit"] = 0; path.write_text(json.dumps(value) + "\n")
    elif name == "db_count_wrong":
        path = copy_root / "raw/fixed-lifecycle.json"; value = json.loads(path.read_text()); value["passed_tests"] = 6; path.write_text(json.dumps(value) + "\n")
    elif name == "geometry_wrong":
        path = copy_root / "raw/geometry.json"; value = json.loads(path.read_text()); value["three_pages"] = 2; path.write_text(json.dumps(value) + "\n")
    else: raise ValueError(name)

def run_verifier(root: Path) -> tuple[int, dict[str, object]]:
    process = subprocess.run([sys.executable, str(VERIFIER), str(root)], text=True, capture_output=True)
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"verifier-json:{type(error).__name__}") from error
    return process.returncode, result


def run_copy(label: str, mutation: str | None) -> dict[str, object]:
    disposable = EVIDENCE / "disposable"
    target = disposable / label
    if target.exists() or target.is_symlink():
        raise RuntimeError(f"temporary-target-exists:{target}")
    try:
        shutil.copytree(EVIDENCE, target, ignore=shutil.ignore_patterns("disposable"))
        if mutation:
            mutate(target, mutation)
        exit_code, result = run_verifier(target)
        return {
            "copy": f"disposable/{label}",
            "exit_code": exit_code,
            "result": summary(result),
            "verifier_result": result,
        }
    finally:
        shutil.rmtree(target, ignore_errors=True)


def assert_control(record: dict[str, object]) -> None:
    result = record["result"]
    if record["exit_code"] != 0 or result != {"passed": True, "missing": [], "extra": [], "drift_paths": [], "semantic_errors": []}:
        raise RuntimeError(f"unchanged-control-failed:{json.dumps(record, ensure_ascii=False)}")


def assert_mutation(name: str, record: dict[str, object]) -> None:
    observed = record["result"]
    expected = {"passed": False, **EXPECTED[name]}
    if record["exit_code"] != 1 or observed != expected:
        raise RuntimeError(f"mutation-specificity-failed:{name}:{json.dumps({'expected': expected, 'observed': observed}, ensure_ascii=False)}")


def prepare_rework_root() -> dict[str, object]:
    if EVIDENCE.exists() or EVIDENCE.is_symlink():
        raise RuntimeError(f"rework-target-must-be-absent:{EVIDENCE}")
    EVIDENCE.mkdir(parents=True)
    for name in ["raw", "screenshots"]:
        shutil.copytree(INITIAL / name, EVIDENCE / name)
    shutil.copy2(INITIAL / "UI_DYNAMIC_EVIDENCE_CLOSURE.md", EVIDENCE / "UI_DYNAMIC_EVIDENCE_CLOSURE.md")
    snapshot = {
        "rework": "LIFEOS-P3-111 Rework 1/2 Evidence-only mutation specificity",
        "initial_evidence_read_only": True,
        "source_payload_manifest_sha256": sha256(INITIAL / "PAYLOAD_MANIFEST.json"),
        "source_semantic_result_sha256": sha256(INITIAL / "semantic-verifier-result.json"),
        "copied_inputs": ["raw/", "screenshots/", "UI_DYNAMIC_EVIDENCE_CLOSURE.md"],
        "candidate_runtime_or_ui_modified": False,
        "pilot2_accessed": False,
        "network_used": False,
    }
    (EVIDENCE / "raw" / "rework-source-snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snapshot


def main() -> int:
    snapshot = prepare_rework_root()
    source_manifest = build_manifest(EVIDENCE, "P3-111 rework-1 source payload before mutation-result artifacts")
    source_exit, source_result = run_verifier(EVIDENCE)
    if source_exit != 0 or not source_result.get("passed"):
        raise RuntimeError(f"source-payload-failed:{json.dumps(source_result, ensure_ascii=False)}")

    source_control = run_copy("noop-source", None)
    assert_control(source_control)
    source_mutations = []
    try:
        for name in NAMES:
            record = run_copy(name, name)
            assert_mutation(name, record)
            source_mutations.append({"mutation": name, **record})
    finally:
        shutil.rmtree(EVIDENCE / "disposable", ignore_errors=True)

    mutations_dir = EVIDENCE / "mutations"
    mutations_dir.mkdir()
    for item in source_mutations:
        (mutations_dir / f"{item['mutation']}.json").write_text(json.dumps(item["verifier_result"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contract = {
        "runner": "same semantic verifier, unchanged control, and six real disposable mutations",
        "source_manifest_sha256": sha256(EVIDENCE / "PAYLOAD_MANIFEST.json"),
        "source_baseline": summary(source_result),
        "unchanged_disposable_copy": source_control,
        "mutations": [{key: value for key, value in item.items() if key != "verifier_result"} for item in source_mutations],
        "all_source_mutations_exact": True,
        "disposable_residue": (EVIDENCE / "disposable").exists(),
        "pilot2_accessed": False,
    }
    (EVIDENCE / "mutation-results.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    final_manifest = build_manifest(EVIDENCE, "P3-111 rework-1 evidence payload; excludes only manifest/index and this root's disposable children")
    final_exit, final_root = run_verifier(EVIDENCE)
    if final_exit != 0 or not final_root.get("passed"):
        raise RuntimeError(f"final-payload-failed:{json.dumps(final_root, ensure_ascii=False)}")
    final_control = run_copy("noop-final", None)
    assert_control(final_control)
    final_mutations = []
    try:
        for name in NAMES:
            record = run_copy(f"final-{name}", name)
            assert_mutation(name, record)
            final_mutations.append({"mutation": name, **record})
    finally:
        shutil.rmtree(EVIDENCE / "disposable", ignore_errors=True)

    final_semantic = {
        "verifier": "LIFEOS-P3-111 raw semantic verifier",
        "rework": "1/2",
        "final_payload_manifest_sha256": sha256(EVIDENCE / "PAYLOAD_MANIFEST.json"),
        "final_payload": summary(final_root),
        "unchanged_disposable_copy": final_control,
        "six_final_mutations_exact": [{"mutation": item["mutation"], "copy": item["copy"], "exit_code": item["exit_code"], "result": item["result"]} for item in final_mutations],
        "all_final_mutations_exact": True,
        "disposable_residue": (EVIDENCE / "disposable").exists(),
        "initial_evidence_modified": False,
        "pilot2_accessed": False,
        "network_used": False,
        "source_snapshot": snapshot,
    }
    (EVIDENCE / "semantic-verifier-result.json").write_text(json.dumps(final_semantic, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "file_count": final_manifest["file_count"], "all_final_mutations_exact": True, "disposable_residue": False}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
