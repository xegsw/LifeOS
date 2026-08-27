#!/usr/bin/env python3
"""Generate the non-self-referential Closure-1 Final Manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "evidence" / "closure-1"
OUT = ROOT / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


assets = []
for path in sorted(item for item in ROOT.rglob("*") if item.is_file() and item != OUT):
    assets.append({"path": str(path.relative_to(ROOT)), "type": "regular", "bytes": path.stat().st_size, "sha256": digest(path)})
OUT.write_text(json.dumps({"kind": "LIFEOS-P3-134 Closure-1 non-self Final Manifest", "task": "LIFEOS-P3-134", "excluded": ["FINAL_MANIFEST.json (self)"], "assets": assets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
