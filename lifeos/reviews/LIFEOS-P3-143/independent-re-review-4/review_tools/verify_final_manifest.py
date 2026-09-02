#!/usr/bin/env python3
"""Verify the explicitly declared non-self-referential re-review-4 manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    manifest = json.loads((ROOT / "FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    errors = []
    forbidden = {"FINAL_MANIFEST.json", "review_tools/verify_final_manifest.py", "manifest_verification.json"}
    for entry in manifest.get("entries", []):
        relative = entry.get("path", "")
        path = ROOT / relative
        if relative in forbidden or not path.is_file():
            errors.append(f"invalid_entry:{relative}")
        elif path.stat().st_size != entry.get("bytes"):
            errors.append(f"size_mismatch:{relative}")
        elif digest(path) != entry.get("sha256"):
            errors.append(f"hash_mismatch:{relative}")
    output = {"schema": "lifeos.p3-143.independent-rereview4.manifest-verification.v1", "entry_count": len(manifest.get("entries", [])), "errors": errors, "result": "PASS" if not errors else "FAIL"}
    (ROOT / "manifest_verification.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output))
    raise SystemExit(0 if not errors else 1)

if __name__ == "__main__":
    main()
