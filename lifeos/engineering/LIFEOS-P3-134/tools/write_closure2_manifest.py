#!/usr/bin/env python3
"""Generate Closure-2's non-self-referential manifest; no historical path is read."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "evidence" / "closure-2"
OUT = ROOT / "FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assets = []
for path in sorted(ROOT.rglob("*")):
    if path.is_file() and path != OUT:
        assets.append({
            "path": str(path.relative_to(ROOT)),
            "type": "regular",
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
OUT.write_text(json.dumps({
    "task": "LIFEOS-P3-134",
    "closure": "closure-2",
    "kind": "non-self-referential fail-closed evidence manifest",
    "excluded": ["FINAL_MANIFEST.json (self)"],
    "assets": assets,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
