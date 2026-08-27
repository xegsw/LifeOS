#!/usr/bin/env python3
"""Record exact pre/post state for the task-owned temporary runtime root."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage", choices=("before", "after"), required=True)
    args = parser.parse_args()
    if args.stage == "before":
        root = args.root.resolve(strict=True)
        files = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                files.append({"relative_path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
        record = {"contract": "LIFEOS-P3-132", "temporary_root": str(root), "before": {"exists": True, "regular_file_count": len(files), "files": files}, "after": None}
    else:
        record = json.loads(args.output.read_text())
        record["after"] = {"exists": args.root.exists(), "verification": "exact absolute path check after task-authorized cleanup"}
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
