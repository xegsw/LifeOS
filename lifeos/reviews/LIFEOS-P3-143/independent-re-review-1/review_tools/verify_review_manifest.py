#!/usr/bin/env python3
"""Independent verifier for this review's non-self-referential final manifest."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-1")
MANIFEST = ROOT / "FINAL_MANIFEST.json"
OUTPUT = ROOT / "evidence/review_manifest_verification.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    files = []
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        payload = path.read_bytes()
        files.append({
            "path": entry["path"],
            "expected_bytes": entry["bytes"],
            "actual_bytes": len(payload),
            "expected_sha256": entry["sha256"],
            "actual_sha256": sha256(payload),
        })
    mismatches = [
        entry
        for entry in files
        if entry["expected_bytes"] != entry["actual_bytes"]
        or entry["expected_sha256"] != entry["actual_sha256"]
    ]
    result = {
        "schema": "lifeos.p3-143.independent-review-manifest-verifier.v1",
        "reviewer_owned": True,
        "self_exclusion_declared": manifest["self_exclusion"],
        "manifest_listed_as_input": any(entry["path"] == "FINAL_MANIFEST.json" for entry in manifest["files"]),
        "entry_count": len(files),
        "mismatch_count": len(mismatches),
        "status": "PASS" if manifest["self_exclusion"] and not any(entry["path"] == "FINAL_MANIFEST.json" for entry in manifest["files"]) and not mismatches else "FAIL",
        "files": files,
        "mismatches": mismatches,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
