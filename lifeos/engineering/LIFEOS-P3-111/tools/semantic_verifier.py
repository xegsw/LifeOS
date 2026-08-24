#!/usr/bin/env python3
"""Recompute raw payload hashes/bytes/missing/extra and independent semantic facts."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "evidence"

def digest(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()

def verify(evidence: Path) -> dict[str, object]:
    manifest_path = evidence / "PAYLOAD_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in manifest["files"]}
    # Evaluate exclusion against the supplied Evidence root, never its absolute
    # ancestors.  A verifier run on /.../disposable/noop must still see noop's
    # payload; only this Evidence root's own temporary child is excluded.
    actual_paths = {
        relative.as_posix()
        for path in evidence.rglob("*")
        if path.is_file()
        for relative in [path.relative_to(evidence)]
        if path.name not in {"PAYLOAD_MANIFEST.json", "MANIFEST.md", "semantic-verifier-result.json"}
        and (not relative.parts or relative.parts[0] != "disposable")
    }
    missing = sorted(set(expected) - actual_paths)
    extra = sorted(actual_paths - set(expected))
    drift = []
    for rel, item in expected.items():
        path = evidence / rel
        if path.exists():
            size, hash_value = digest(path)
            if size != item["bytes"] or hash_value != item["sha256"]:
                drift.append({"path": rel, "expected_bytes": item["bytes"], "actual_bytes": size, "expected_sha256": item["sha256"], "actual_sha256": hash_value})
    raw = {}
    semantic_errors = []
    dynamic_rows: dict[str, dict[str, str]] = {}
    closure = evidence / "UI_DYNAMIC_EVIDENCE_CLOSURE.md"
    try:
        for line in closure.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| D-"):
                continue
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) != 8:
                semantic_errors.append(f"dynamic-row-shape:{line[:32]}")
                continue
            dynamic_rows[cells[0]] = {"sha256": cells[5], "status": cells[6], "evidence": cells[4]}
    except Exception as error:
        semantic_errors.append(f"unreadable:dynamic-closure:{type(error).__name__}")
    required_dynamic = {f"D-{number:03d}" for number in range(1, 13)}
    if set(dynamic_rows) != required_dynamic:
        semantic_errors.append("dynamic-rows")
    for row_id in required_dynamic:
        row = dynamic_rows.get(row_id, {})
        if row.get("status") != "PASS":
            semantic_errors.append(f"dynamic-status:{row_id}")
        if not re.search(r"[0-9a-f]{64}", row.get("sha256", "")) or not row.get("evidence"):
            semantic_errors.append(f"dynamic-evidence:{row_id}")
    for name in ["raw/fixed-lifecycle.json", "raw/negative-results.json", "raw/geometry.json", "raw/cleanup.json", "raw/static-results.json"]:
        path = evidence / name
        try:
            raw[name] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            semantic_errors.append(f"unreadable:{name}:{type(error).__name__}")
    if not semantic_errors:
        lifecycle = raw["raw/fixed-lifecycle.json"]
        negative = raw["raw/negative-results.json"]
        geometry = raw["raw/geometry.json"]
        cleanup = raw["raw/cleanup.json"]
        static = raw["raw/static-results.json"]
        if lifecycle.get("cargo_test_exit") != 0 or lifecycle.get("passed_tests") != 8: semantic_errors.append("lifecycle")
        if negative.get("unknown_ipc_exit") != 1 or negative.get("argument_reject_exit") != 1: semantic_errors.append("negative")
        if geometry.get("three_pages") != 3 or not geometry.get("keyboard_capture"): semantic_errors.append("geometry")
        if cleanup.get("fixture_residue_count") != 0 or cleanup.get("candidate_shadow_residue_count") != 0: semantic_errors.append("cleanup")
        if not static.get("passed"): semantic_errors.append("static")
    passed = not missing and not extra and not drift and not semantic_errors
    return {"verifier": "LIFEOS-P3-111 raw semantic verifier", "passed": passed, "manifest_file_count": manifest.get("file_count"), "missing": missing, "extra": extra, "hash_or_bytes_drift": drift, "semantic_errors": semantic_errors}

def main() -> int:
    evidence = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else DEFAULT
    result = verify(evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
