#!/usr/bin/env python3
"""Fail closed unless every Frozen actual-app action has complete Evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "evidence" / "dynamic_closure.json"
OUTPUT = ROOT / "evidence" / "dynamic_closure_verification.json"
REQUIRED = {
    "APP-01", "APP-02", "CAP-01", "CAP-02", "CAP-03", "CAP-04",
    "STATE-01", "REST-01", "IPC-01", "IPC-02", "UI-NS-01",
    "A11Y-01", "A11Y-02", "VIS-01", "VIS-02", "MOTION-01", "CLEAN-01",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


failures = []
rows = json.loads(CLOSURE.read_text())
ids = [row.get("acceptance_id") for row in rows]
if set(ids) != REQUIRED or len(ids) != len(REQUIRED):
    failures.append("required action IDs are missing, extra, or duplicated")
result_ids = [row.get("structured_result_id") for row in rows]
if len(set(result_ids)) != len(result_ids) or any(not item for item in result_ids):
    failures.append("structured result IDs must be non-empty and unique")
for row in rows:
    action_id = row.get("acceptance_id", "UNKNOWN")
    if row.get("status") != "PASS":
        failures.append(f"{action_id}: status is not PASS")
    for field in ("precondition", "operation", "observable_result", "structured_result_id", "evidence_path", "sha256"):
        if not row.get(field):
            failures.append(f"{action_id}: missing {field}")
    evidence_path = ROOT / row.get("evidence_path", "missing")
    if not evidence_path.is_file():
        failures.append(f"{action_id}: evidence file missing")
    elif digest(evidence_path) != row.get("sha256"):
        failures.append(f"{action_id}: evidence hash mismatch")

payload = {
    "task": "LIFEOS-P3-104",
    "required": len(REQUIRED),
    "rows": len(rows),
    "passed": len(REQUIRED) if not failures else len(REQUIRED) - len({item.split(":", 1)[0] for item in failures}),
    "failed": len(failures),
    "p0": 0,
    "p1": 0,
    "p2": 0,
    "unknown": 0,
    "not_implemented": 0 if not failures else len(failures),
    "failures": failures,
}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(1 if failures else 0)

