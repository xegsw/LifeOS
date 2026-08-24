#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "evidence/dynamic_closure.json"
if not path.is_file():
    print("dynamic closure missing", file=sys.stderr)
    raise SystemExit(1)
data = json.loads(path.read_text())
required = set(data["required_ids"])
rows = data["rows"]
seen = {row["id"] for row in rows}
failures = []
if seen != required or len(seen) != len(rows):
    failures.append("required row IDs missing, extra, or duplicated")
for row in rows:
    evidence = ROOT / row.get("evidence", "")
    if row.get("status") != "PASS": failures.append(f"{row['id']}: status")
    if not row.get("action") or not row.get("observable"): failures.append(f"{row['id']}: action/observable")
    if not evidence.is_file(): failures.append(f"{row['id']}: evidence missing")
    elif hashlib.sha256(evidence.read_bytes()).hexdigest() != row.get("sha256"): failures.append(f"{row['id']}: hash mismatch")
print(json.dumps({"required": len(required), "rows": len(rows), "failures": failures}, ensure_ascii=False))
raise SystemExit(1 if failures else 0)
