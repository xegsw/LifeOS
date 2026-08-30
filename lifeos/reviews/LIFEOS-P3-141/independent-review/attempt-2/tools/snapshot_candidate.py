#!/usr/bin/env python3
"""Write a deterministic read-only candidate snapshot for this review."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: snapshot_candidate.py CANDIDATE OUTPUT_JSON")
    candidate = Path(sys.argv[1]).resolve(strict=True)
    output = Path(sys.argv[2]).resolve()
    if not candidate.is_dir() or candidate.is_symlink():
        raise SystemExit("candidate_must_be_real_directory")
    records = []
    for root, dirs, names in os.walk(candidate, followlinks=False):
        dirs[:] = sorted(name for name in dirs if not (Path(root) / name).is_symlink())
        for name in sorted(names):
            path = Path(root) / name
            if path.is_symlink() or not path.is_file():
                raise SystemExit(f"candidate_non_regular_file:{path.relative_to(candidate)}")
            records.append({
                "path": path.relative_to(candidate).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_hash(path),
            })
    tree = hashlib.sha256("".join(
        f"{item['path']}\\0{item['bytes']}\\0{item['sha256']}\\n" for item in records
    ).encode()).hexdigest()
    payload = {
        "schema_version": "lifeos.p3_141.phase_b.candidate_snapshot.v1",
        "candidate": str(candidate),
        "file_count": len(records),
        "tree_sha256": tree,
        "files": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
