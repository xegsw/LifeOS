#!/usr/bin/env python3
"""Reviewer-owned non-self-referential hash verifier for the supplied P3-143 commit."""

import hashlib
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path.cwd()
CANDIDATE_COMMIT = "767301fb051d11a6bf11488413f8b03aabfc2d99"
MANIFEST = WORKSPACE / "lifeos/engineering/LIFEOS-P3-143/FINAL_MANIFEST.json"
CLOSURE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-143/evidence/root_authority_closure.json"
OUTPUT = WORKSPACE / "lifeos/reviews/LIFEOS-P3-143/independent-re-review-1/evidence/lineage_verification.json"


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    records = []
    category_counts = {category: 0 for category in manifest["categories"]}
    for entry in manifest["files"]:
        absolute = (MANIFEST.parent / entry["path"]).resolve()
        payload = absolute.read_bytes()
        actual_hash = digest(payload)
        item = {
            "category": entry["category"],
            "role": entry.get("role"),
            "path": os.path.relpath(absolute, WORKSPACE),
            "bytes_expected": entry["bytes"],
            "bytes_actual": len(payload),
            "sha256_expected": entry["sha256"],
            "sha256_actual": actual_hash,
            "pass": len(payload) == entry["bytes"] and actual_hash == entry["sha256"],
        }
        records.append(item)
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
    closure_payload = CLOSURE.read_bytes()
    closure = json.loads(closure_payload)
    errors = sum(not record["pass"] for record in records)
    output = {
        "schema": "lifeos.p3-143.independent-lineage-verification.v1",
        "reviewer_owned": True,
        "candidate_commit": CANDIDATE_COMMIT,
        "manifest_self_referential": manifest["self_referential"],
        "manifest_entry_count": len(records),
        "category_counts": category_counts,
        "hash_error_count": errors,
        "root_authority_closure": {
            "sha256": digest(closure_payload),
            "candidate_files": closure["candidate_identity"]["candidate_files"],
            "closure_candidate_sha256": closure["candidate_identity"]["after_root_authority_closure_sha256"],
            "decision": closure["decision"],
        },
        "status": "PASS" if not manifest["self_referential"] and errors == 0 else "FAIL",
        "files": records,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
