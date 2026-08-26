#!/usr/bin/env python3
"""P3-127 read-only integrity check for the P3-126 final inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_path(workspace: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or not relative.startswith("lifeos/"):
        raise ValueError("manifest_path_rejected")
    resolved = (workspace / candidate).resolve()
    if os.path.commonpath([str(workspace), str(resolved)]) != str(workspace):
        raise ValueError("manifest_path_rejected")
    return workspace / candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    manifest_path = Path(args.manifest)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for entry in payload.get("entries", []):
        relative = entry.get("path")
        expected_bytes = entry.get("bytes")
        expected_sha256 = entry.get("sha256")
        try:
            path = safe_path(workspace, relative)
            stat = path.lstat()
            if not path.is_file() or path.is_symlink():
                raise ValueError("protected_object_rejected")
            actual_bytes = stat.st_size
            actual_sha256 = sha256(path)
            result = actual_bytes == expected_bytes and actual_sha256 == expected_sha256
            row = {
                "path": relative,
                "role": entry.get("role"),
                "expected_bytes": expected_bytes,
                "actual_bytes": actual_bytes,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual_sha256,
                "pass": result,
            }
        except (OSError, ValueError) as error:
            row = {"path": relative, "role": entry.get("role"), "pass": False, "error": str(error)}
        rows.append(row)
    result = "PASS" if rows and all(row["pass"] for row in rows) else "FAIL"
    Path(args.output).write_text(
        json.dumps(
            {
                "test_id": "P127-M009",
                "historical_manifest": str(manifest_path),
                "entries_checked": len(rows),
                "failures": [row for row in rows if not row["pass"]],
                "result": result,
                "rows": rows,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
