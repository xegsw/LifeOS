#!/usr/bin/env python3
"""Read-only replay for the retained P3-133 independent-review evidence.

This script does not create files, run a candidate, open a database, or access
engineering evidence.  It only checks this directory's final manifest and the
recorded non-Pass conclusion.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    manifest = json.loads((ROOT / "FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    verification = json.loads((ROOT / "verification.json").read_text(encoding="utf-8"))
    actual = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.name != "FINAL_MANIFEST.json":
            actual.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)})
    listed = manifest.get("entries", [])
    checks = {
        "manifest_inventory_exact": listed == actual,
        "recorded_verification_is_non_pass": verification.get("pass") is False and manifest.get("verification_pass") is False,
        "recorded_p0_is_actual_tauri": verification.get("checks", {}).get("actual_tauri") is False,
        "recorded_real_run_not_executed": manifest.get("real_self_use") == "not_run",
    }
    output = {"kind": "independent review readonly replay", "checks": checks, "pass": all(checks.values())}
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0 if output["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
