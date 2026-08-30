#!/usr/bin/env python3
"""Verify the review-owned manifest without contacting the candidate."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "FINAL_MANIFEST.json"
OUTPUT = ROOT / "FINAL_MANIFEST.verification.json"
SELF_FILES = {"FINAL_MANIFEST.json", "FINAL_MANIFEST.verification.json"}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    paths = []
    for entry in manifest["entries"]:
        relative = entry["path"]
        paths.append(relative)
        path = ROOT / relative
        if not path.is_file():
            failures.append({"path": relative, "failure": "missing"})
            continue
        actual_bytes = path.stat().st_size
        actual_sha256 = digest(path)
        if actual_bytes != entry["bytes"] or actual_sha256 != entry["sha256"]:
            failures.append({
                "path": relative,
                "failure": "digest_or_size_mismatch",
                "actual_bytes": actual_bytes,
                "actual_sha256": actual_sha256,
            })
    excluded_ok = not (SELF_FILES & set(paths)) and set(manifest["self_excluded"]) == SELF_FILES
    result = {
        "schema": "lifeos.p3-141.provider-restoration-v2-attempt-3.manifest-verification.v1",
        "manifest": "FINAL_MANIFEST.json",
        "declared_entries": manifest["entry_count"],
        "verified_entries": len(paths) - len(failures),
        "self_excluded": excluded_ok,
        "failures": failures,
        "pass": not failures and excluded_ok and manifest["entry_count"] == len(paths),
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
