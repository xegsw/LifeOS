#!/usr/bin/env python3
"""Read-only verifier for the non-self-referential Closure-2 manifest."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    listed = {item["path"]: item for item in data.get("assets", [])}
    actual = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path != MANIFEST
    }
    errors: list[dict[str, str]] = []
    for relative, item in sorted(listed.items()):
        path = ROOT / relative
        try:
            if not stat.S_ISREG(os.lstat(path).st_mode):
                errors.append({"path": relative, "error": "not_regular"})
            elif path.stat().st_size != item["bytes"]:
                errors.append({"path": relative, "error": "bytes"})
            elif sha256(path) != item["sha256"]:
                errors.append({"path": relative, "error": "sha256"})
        except FileNotFoundError:
            errors.append({"path": relative, "error": "missing"})
    matrix = (ROOT / "AC_MATRIX.md").read_text(encoding="utf-8")
    capability = json.loads((ROOT / "CAPABILITY_PRECHECK.json").read_text(encoding="utf-8"))
    completeness = sorted(actual) == sorted(listed)
    fail_closed = (
        capability["acceptance_effect"]["overall"] == "NOT_PASS"
        and "**Package result: NOT PASS.**" in matrix
        and not errors
        and completeness
    )
    result = {
        "task": "LIFEOS-P3-134",
        "closure": "closure-2",
        "readonly": True,
        "manifest_asset_count": len(listed),
        "asset_errors": errors,
        "manifest_complete": completeness,
        "outcome": "NOT_PASS" if fail_closed else "VERIFIER_ERROR",
        "reason": "Required actual-Tauri geometry/baseline evidence is unavailable; verifier refuses PASS.",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
