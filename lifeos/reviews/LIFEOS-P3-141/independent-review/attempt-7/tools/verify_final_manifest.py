#!/usr/bin/env python3
"""Read-only validator for the attempt-7 final manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    actual = {
        path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": digest(path)}
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and path != MANIFEST_PATH
    }
    declared = manifest["files"]
    mismatched = sorted(name for name in set(actual) & set(declared) if actual[name] != declared[name])
    result = {
        "declared_count": manifest["file_count_excluding_manifest"],
        "actual_count": len(actual),
        "missing": sorted(set(declared) - set(actual)),
        "extra": sorted(set(actual) - set(declared)),
        "mismatched": mismatched,
        "self_excluded": "FINAL_MANIFEST.json" not in declared,
    }
    result["pass"] = result["declared_count"] == result["actual_count"] and not result["missing"] and not result["extra"] and not mismatched and result["self_excluded"]
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
