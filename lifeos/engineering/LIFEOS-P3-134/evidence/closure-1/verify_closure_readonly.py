#!/usr/bin/env python3
"""Default read-only verifier for the P3-134 Closure-1 Evidence package.

It never creates, updates, or deletes files.  A missing mandatory asset or a
non-PASS acceptance row is a whole-package Not Pass; this deliberately blocks
the false-positive shape found in the initial PM review.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FINAL_MANIFEST.json"
REQUIRED = (
    "closure-verification.json",
    "actual/page-state-matrix.json",
    "visual/geometry.json",
    "visual/comparison.json",
    "mutations/matrix.json",
    "cleanup.json",
)
MANDATORY_AC = tuple(f"AC-{number:02d}" for number in range(1, 17))


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.is_file():
        errors.append("missing FINAL_MANIFEST.json")
        print(json.dumps({"readonly": True, "passed": False, "errors": errors}, ensure_ascii=False))
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    listed = {item["path"]: item for item in manifest.get("assets", [])}
    actual = {str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and path.name != "FINAL_MANIFEST.json"}
    if set(listed) != actual:
        errors.append("manifest asset set differs from stable Evidence files")
    for relative, item in listed.items():
        path = ROOT / relative
        if not path.is_file() or item.get("sha256") != digest(path) or item.get("bytes") != path.stat().st_size:
            errors.append(f"manifest mismatch: {relative}")
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required Evidence: {relative}")
    verification = json.loads((ROOT / "closure-verification.json").read_text(encoding="utf-8")) if (ROOT / "closure-verification.json").is_file() else {}
    acceptance = verification.get("acceptance", {})
    for ac in MANDATORY_AC:
        if acceptance.get(ac) != "PASS":
            errors.append(f"mandatory acceptance not PASS: {ac}")
    result = {"task": "LIFEOS-P3-134", "closure": "closure-1", "readonly": True, "errors": errors, "passed": not errors}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
