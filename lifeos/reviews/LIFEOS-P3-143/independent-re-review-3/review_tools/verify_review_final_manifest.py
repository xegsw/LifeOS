#!/usr/bin/env python3
"""Verify the review-owned final manifest without trusting a candidate verifier."""

import hashlib
import json
from pathlib import Path

ROOT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-3")
MANIFEST = ROOT / "FINAL_MANIFEST.json"
OUTPUT = ROOT / "final_manifest_verification.json"


def main() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    if document.get("self_referential") is not False:
        errors.append("self_reference_not_false")
    if "FINAL_MANIFEST.json" not in document.get("self_exclusion", []):
        errors.append("final_manifest_not_excluded")
    for item in document.get("files", []):
        path = ROOT / item["path"]
        if not path.is_file() or path.is_symlink():
            errors.append({"path": item["path"], "kind": "missing_or_nonregular"})
            continue
        content = path.read_bytes()
        if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
            errors.append({"path": item["path"], "kind": "hash_or_size_mismatch"})
    output = {"schema": "lifeos.p3-143.independent-rereview-3.final-manifest-verification.v1", "entries": len(document.get("files", [])), "errors": errors, "result": "PASS" if not errors else "FAIL"}
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": output["result"], "entries": output["entries"], "error_count": len(errors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
