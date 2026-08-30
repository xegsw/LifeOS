#!/usr/bin/env python3
"""Verify Revision-2 immutable inputs without writing outside this closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PM_ROOT = Path("/Users/xxe/Documents/No.2")
ROOT = Path(__file__).resolve().parent.parent
inventory_path = PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_2.json"
inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
values = []
for expected in inventory["entries"]:
    raw_path = Path(expected["path"])
    actual_path = raw_path if raw_path.is_absolute() else PM_ROOT / raw_path
    raw = actual_path.read_bytes()
    actual = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    matched = actual["bytes"] == expected["bytes"] and actual["sha256"] == expected["sha256"]
    if not matched:
        raise RuntimeError(f"fixed input mismatch: {expected['role']}")
    values.append({"role": expected["role"], "path": expected["path"], "expected": {"bytes": expected["bytes"], "sha256": expected["sha256"]}, "actual": actual, "matched": True})
output = ROOT / "evidence/fixed_input_inventory_assertion.json"
if output.exists():
    raise RuntimeError("refusing to overwrite assertion")
output.write_text(json.dumps({"schema": "lifeos.p3-141.provider-restoration.fixed-input-assertion.v1", "result": "PASS", "entries": values, "candidate_lineage": inventory["candidate_lineage"], "governance": inventory["governance"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
