#!/usr/bin/env python3
"""Read-only inventory of prior review attempts, excluding this attempt."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
PARENT = REVIEW.parent
OUTPUT = REVIEW / "evidence" / "prior_attempt_history.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    expected = Path(sys.argv[1]).resolve()
    if expected != PARENT.resolve():
        raise SystemExit("prior-attempt parent does not match the local review parent")
    entries = []
    for path in sorted(PARENT.rglob("*")):
        if REVIEW in path.parents or path == REVIEW:
            continue
        if path.is_symlink() or not path.is_file():
            continue
        entries.append(
            {
                "path": str(path.relative_to(PARENT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "schema": "lifeos-p3-141-prior-attempt-history-v1",
        "source_parent_read_only": str(PARENT),
        "excluded_current_attempt": REVIEW.name,
        "prior_regular_file_count": len(entries),
        "entries": entries,
        "preserved": len(entries) > 0,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["preserved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
