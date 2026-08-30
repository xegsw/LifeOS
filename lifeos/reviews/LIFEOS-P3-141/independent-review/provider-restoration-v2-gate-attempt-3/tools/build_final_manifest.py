#!/usr/bin/env python3
"""Build a non-self-referential manifest for this review-owned directory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "FINAL_MANIFEST.json"
EXCLUDED = {"FINAL_MANIFEST.json", "FINAL_MANIFEST.verification.json"}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> None:
    entries = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED:
            continue
        entries.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    manifest = {
        "schema": "lifeos.p3-141.provider-restoration-v2-attempt-3.final-manifest.v1",
        "review_conclusion": "REWORK",
        "candidate_commit": "26c08409e83a01caea7388223e51a76182a22a3c",
        "engineering_source_commit": "5837fb4ffd4203a24d5908d990d1996b3aae4dcf",
        "self_excluded": sorted(EXCLUDED),
        "entry_count": len(entries),
        "entries": entries,
    }
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(OUT), "entry_count": len(entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
