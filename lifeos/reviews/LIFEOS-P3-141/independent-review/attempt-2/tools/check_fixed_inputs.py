#!/usr/bin/env python3
"""Independently validate the 12 frozen P3-141 input entries."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(entry_path: str, pm_root: Path) -> Path:
    path = Path(entry_path)
    return path if path.is_absolute() else pm_root / path


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: check_fixed_inputs.py PM_ROOT INVENTORY OUTPUT_JSON")
    pm_root = Path(sys.argv[1]).resolve(strict=True)
    inventory_path = Path(sys.argv[2]).resolve(strict=True)
    output_path = Path(sys.argv[3]).resolve()
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    results = []
    for entry in inventory["entries"]:
        path = resolve(entry["path"], pm_root)
        actual_bytes = path.stat().st_size
        actual_sha256 = sha256(path)
        results.append({
            "role": entry["role"],
            "path": str(path),
            "expected_bytes": entry["bytes"],
            "actual_bytes": actual_bytes,
            "expected_sha256": entry["sha256"],
            "actual_sha256": actual_sha256,
            "pass": actual_bytes == entry["bytes"] and actual_sha256 == entry["sha256"],
        })
    payload = {
        "schema_version": "lifeos.p3_141.phase_b.fixed_input_verification.v1",
        "entry_count": len(results),
        "pass_count": sum(1 for item in results if item["pass"]),
        "fail_count": sum(1 for item in results if not item["pass"]),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
