#!/usr/bin/env python3
"""Fail-closed final verifier for P3-108's independent matrix."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
matrix = json.loads((root / "matrix-results.json").read_text(encoding="utf-8"))
required = [row for row in matrix["rows"] if row["id"] != "ABF-M-016"]
nonpass = [{"id": row["id"], "status": row["status"], "reason": row.get("reason")} for row in required if row["status"] != "PASS"]
closure = root / "dynamic_closure.md"
result = {
    "id": "P3108-M016-final-verifier",
    "closure_sha256": hashlib.sha256(closure.read_bytes()).hexdigest(),
    "matrix_sha256": hashlib.sha256((root / "matrix-results.json").read_bytes()).hexdigest(),
    "required_rows": len(required),
    "nonpass_rows": nonpass,
    "pass": not nonpass,
    "rule": "Every ABF row and every required dynamic action must be PASS; PARTIAL, NOT_IMPLEMENTED, UNKNOWN and pending cleanup fail closed."
}
(root / "final-verifier.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result["pass"] else 1)
