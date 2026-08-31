#!/usr/bin/env python3
"""Create the non-self-referential review artifact manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW_DIR = Path(__file__).resolve().parent
MANIFEST = REVIEW_DIR / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    entries = []
    for path in sorted(REVIEW_DIR.rglob("*")):
        if path == MANIFEST:
            continue
        if path.is_symlink():
            raise SystemExit(f"symlink forbidden in review package: {path}")
        if path.is_file():
            entries.append(
                {
                    "path": path.relative_to(REVIEW_DIR).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
    payload = {
        "schema": "lifeos.p3-141.revision-3.mode-delete.final-manifest.v1",
        "self_reference": "excluded: FINAL_MANIFEST.json only",
        "artifact_root": str(REVIEW_DIR),
        "entry_count": len(entries),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pass": True, "entry_count": len(entries), "manifest": str(MANIFEST)}, sort_keys=True))


if __name__ == "__main__":
    main()
