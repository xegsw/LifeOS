#!/usr/bin/env python3
"""Verify the Closure-1 non-self-referential SHA-256 manifest."""

import hashlib
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
MANIFEST = REPO / "lifeos/engineering/LIFEOS-P3-144/closure-1/FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
if payload.get("self_exclusion") is not True:
    raise SystemExit("self_exclusion_missing")

declared = []
errors = []
for category in ("candidate", "fixed_inputs", "preserved_history", "closure_evidence"):
    for entry in payload.get(category, []):
        path = entry["path"]
        declared.append(path)
        if path.endswith("closure-1/FINAL_MANIFEST.json"):
            errors.append(f"self_reference:{path}")
            continue
        absolute = REPO / path
        if not absolute.is_file():
            errors.append(f"missing:{path}")
        elif digest(absolute) != entry["sha256"]:
            errors.append(f"hash_mismatch:{path}")
if len(declared) != len(set(declared)):
    errors.append("duplicate_path")
print(json.dumps({
    "schema": "lifeos.p3-144.closure-1.manifest-verification.v1",
    "manifest": str(MANIFEST.relative_to(REPO)),
    "declared_entries": len(declared),
    "errors": errors,
    "result": "PASS" if not errors else "FAIL"
}, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if not errors else 1)
