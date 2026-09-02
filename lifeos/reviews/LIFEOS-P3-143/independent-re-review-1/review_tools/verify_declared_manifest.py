#!/usr/bin/env python3
"""Verify a declared non-self-referential LifeOS file manifest without invoking candidate tooling."""

import hashlib
import json
import os
import sys
from pathlib import Path


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_declared_manifest.py MANIFEST OUTPUT")
    manifest_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()
    manifest = json.loads(manifest_path.read_text())
    records = []
    counts = {category: 0 for category in manifest.get("categories", [])}
    for entry in manifest["files"]:
        target = (manifest_path.parent / entry["path"]).resolve()
        payload = target.read_bytes()
        actual = sha256(payload)
        records.append({
            "category": entry.get("category"),
            "role": entry.get("role"),
            "path": os.path.relpath(target, Path.cwd()),
            "bytes_expected": entry["bytes"],
            "bytes_actual": len(payload),
            "sha256_expected": entry["sha256"],
            "sha256_actual": actual,
            "pass": len(payload) == entry["bytes"] and actual == entry["sha256"],
        })
        counts[entry.get("category")] = counts.get(entry.get("category"), 0) + 1
    mismatches = sum(not record["pass"] for record in records)
    output = {
        "schema": "lifeos.independent-declared-manifest-verification.v1",
        "reviewer_owned": True,
        "manifest": os.path.relpath(manifest_path, Path.cwd()),
        "manifest_self_referential": manifest.get("self_referential"),
        "entry_count": len(records),
        "category_counts": counts,
        "hash_error_count": mismatches,
        "status": "PASS" if not manifest.get("self_referential") and mismatches == 0 else "FAIL",
        "files": records,
    }
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
