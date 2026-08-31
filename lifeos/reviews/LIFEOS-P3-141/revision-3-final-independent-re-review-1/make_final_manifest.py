#!/usr/bin/env python3
"""Build a non-self-referential manifest for this review directory."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
EXCLUDED = {
    "FINAL_MANIFEST.json",
    "final_manifest_verification.json",
    "make_final_manifest.py",
    "verify_final_manifest.py",
}

def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

entries = []
for path in sorted(REVIEW.rglob("*")):
    if not path.is_file() or path.is_symlink(): continue
    relative = path.relative_to(REVIEW).as_posix()
    if relative in EXCLUDED: continue
    entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
payload = {
    "schema": "lifeos.p3-141.final-independent-re-review-manifest.v1",
    "task_id": "LIFEOS-P3-141",
    "review_id": "revision-3-final-independent-re-review-1",
    "candidate_commit": "476e5f069671dc7d0dc53be88f9d328901d6d543",
    "conclusion": "Rework",
    "counts": {"P0": 0, "P1": 0, "P2": 1, "Unknown": 0, "NotImplemented": 0},
    "non_self_referential_excluded_paths": sorted(EXCLUDED),
    "entries": entries,
    "entry_count": len(entries),
}
(REVIEW / "FINAL_MANIFEST.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
