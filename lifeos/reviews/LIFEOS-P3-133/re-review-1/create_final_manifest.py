#!/usr/bin/env python3
"""Create a non-self-referential SHA-256 inventory for this review directory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW_ROOT = Path(__file__).resolve().parent
OUTPUT = REVIEW_ROOT / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    items = []
    for path in sorted(REVIEW_ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        info = path.stat()
        items.append(
            {
                "path": path.relative_to(REVIEW_ROOT).as_posix(),
                "bytes": info.st_size,
                "sha256": digest(path),
            }
        )
    document = {
        "kind": "lifeos_p3_133_independent_re_review_manifest",
        "round": "re-review-1",
        "scope": "Closure-2 synthetic actual-Tauri independent re-review only",
        "test_design_sha256": "b0cd4c0ff9f65e2db0c9ed1d4ed4e9de4779d474c95a25641556f177b4fb038a",
        "items": items,
        "item_count": len(items),
        "excluded_from_self_hash": "FINAL_MANIFEST.json",
        "verdict": "PASS_LIMITED_SCOPE",
        "does_not_mean": [
            "P3-133 final task acceptance",
            "real self-use execution",
            "R-0053 closure",
            "freeze",
            "Stage 4 entry",
        ],
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
