#!/usr/bin/env python3
"""Verify P3-116 dynamic evidence from raw action logs, not summary claims."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "results" / "evidence_verification.json"
MATRIX = [f"ABF-M-{number:03d}" for number in range(1, 19)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(reason: str) -> None:
    raise ValueError(reason)


def relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        fail(f"unsafe evidence path: {value}")
    return ROOT / path


def load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def main() -> int:
    checks = []
    try:
        actions = load("raw/dynamic_actions.json")
        closure = load("dynamic_closure.json")
        matrix = load("results/matrix_results.json")
        preflight = load("results/chrome_preflight.json")
        action_map = {item["action_id"]: item for item in actions["actions"]}
        if len(action_map) < 38 or len(action_map) != len(actions["actions"]):
            fail("dynamic action IDs are missing, duplicate, or fewer than 38")
        if preflight.get("status") != "PASS" or preflight.get("attempt") != 1:
            fail("Chrome file preflight did not pass on first recorded attempt")
        closure_rows = closure["rows"]
        if len(closure_rows) < 38:
            fail("closure does not enumerate every dynamic action")
        seen = set()
        for row in closure_rows:
            if row.get("status") != "PASS":
                fail(f"closure is not PASS: {row.get('closure_id')}")
            action_id = row.get("action_id")
            if action_id not in action_map or action_id in seen:
                fail(f"closure action link invalid: {action_id}")
            seen.add(action_id)
            for path_key, hash_key in (("raw_log", "raw_log_sha256"), ("screenshot", "screenshot_sha256")):
                evidence_path = relative_path(row[path_key])
                if not evidence_path.is_file():
                    fail(f"missing {path_key}: {row[path_key]}")
                if sha256(evidence_path) != row[hash_key]:
                    fail(f"hash mismatch {path_key}: {row[path_key]}")
        if seen != set(action_map):
            fail("closure and raw action ledger do not have the same IDs")
        row_map = {item["row_id"]: item for item in matrix["rows"]}
        if set(row_map) != set(MATRIX):
            fail("matrix must contain exactly ABF-M-001 through ABF-M-018")
        for row_id, row in row_map.items():
            if row.get("status") != "PASS" or not row.get("test_id") or not row.get("evidence"):
                fail(f"matrix row incomplete: {row_id}")
        checks.append({"id": "P116-E-001", "status": "PASS", "detail": "raw action ledger, closure hashes, preflight, and 18 ABF rows are complete"})
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as err:
        checks.append({"id": "P116-E-001", "status": "FAIL", "detail": str(err)})
    payload = {"runner": "tests/verify_evidence.py", "overall": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "checks": checks}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
