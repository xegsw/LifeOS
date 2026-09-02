#!/usr/bin/env python3
"""Verify the P3-144 Closure-3 manifest."""

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MANIFEST = REPO / "lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
errors = []
declared = []
if payload.get("self_exclusion") is not True:
    errors.append("self_exclusion_missing")
for category in ("candidate", "fixed_inputs", "preserved_history", "closure_evidence"):
    for entry in payload.get(category, []):
        path = entry["path"]
        declared.append(path)
        if path.endswith("closure-3/FINAL_MANIFEST.json") or path.endswith("closure-3/evidence/manifest_verification.json"):
            errors.append(f"self_reference:{path}")
            continue
        absolute = REPO / path
        if not absolute.is_file():
            errors.append(f"missing:{path}")
        elif digest(absolute) != entry["sha256"]:
            errors.append(f"hash_mismatch:{path}")
if len(declared) != len(set(declared)):
    errors.append("duplicate_path")
print(json.dumps({"schema": "lifeos.p3-144.closure-3.manifest-verification.v1", "declared_entries": len(declared), "errors": errors, "result": "PASS" if not errors else "FAIL"}, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if not errors else 1)
