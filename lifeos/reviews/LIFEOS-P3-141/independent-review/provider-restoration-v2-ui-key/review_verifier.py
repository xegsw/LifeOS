#!/usr/bin/env python3
"""Read-only verifier for this failed independent-review package."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:  # fail closed on any unreadable/invalid manifest
        print(json.dumps({"verdict": "FAIL", "error": f"manifest_read:{exc}"}, ensure_ascii=False))
        return 1
    if data.get("schema") != "lifeos.p3-141.independent-review-manifest.v2":
        errors.append("schema")
    if data.get("review_conclusion") != "NOT_PASS":
        errors.append("review_conclusion")
    if data.get("counts") != {"P0": 1, "P1": 0, "P2": 0, "Unknown": 1, "Not Implemented": 9}:
        errors.append("counts")
    if data.get("candidate_commit") != "01b08f7877ba1b657218ab1d0aaa1e495a7d92fb":
        errors.append("candidate_commit")
    if data.get("phase_c_v2_pass_receipt_created") is not False:
        errors.append("pass_receipt_must_be_absent")
    pass_receipt = ROOT / "phase_c_v2_independent_pass_receipt.json"
    if pass_receipt.exists():
        errors.append("unexpected_pass_receipt")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        errors.append("files")
    else:
        seen: set[str] = set()
        for item in files:
            relative = item.get("path") if isinstance(item, dict) else None
            expected = item.get("sha256") if isinstance(item, dict) else None
            if not isinstance(relative, str) or not isinstance(expected, str):
                errors.append("file_entry_shape")
                continue
            if relative in seen or relative == "FINAL_MANIFEST.json":
                errors.append("duplicate_or_self_reference")
                continue
            seen.add(relative)
            path = ROOT / relative
            if not path.is_file() or path.is_symlink():
                errors.append(f"missing_or_link:{relative}")
            elif sha256(path) != expected:
                errors.append(f"sha256:{relative}")
    result = {
        "schema": "lifeos.p3-141.review-verifier-result.v1",
        "verdict": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "errors": errors,
        "manifest": "FINAL_MANIFEST.json",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
