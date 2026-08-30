#!/usr/bin/env python3
"""Create the non-self-referential Attempt-4 FINAL_MANIFEST.json."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "FINAL_MANIFEST.json"
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": digest(path),
            "bytes": path.stat().st_size,
        })
    manifest = {
        "schema": "lifeos-p3-141-attempt-4-final-manifest-v1",
        "task_id": "LIFEOS-P3-141",
        "attempt": 4,
        "candidate_commit": "d35a72bf6fbcb9d6cdc905eac100679b69c97e61",
        "self_reference": {
            "excluded_path": "FINAL_MANIFEST.json",
            "reason": "A manifest cannot include its own final byte hash; every other review artifact is individually hashed."
        },
        "files": files,
    }
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files_hashed": len(files), "manifest": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
