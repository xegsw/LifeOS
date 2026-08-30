#!/usr/bin/env python3
"""Create a hash manifest that intentionally does not include itself."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
MANIFEST = REVIEW / "FINAL_MANIFEST.json"
VERIFICATION = REVIEW / "evidence" / "final_manifest_verification.json"
EXCLUDED = {MANIFEST.resolve(), VERIFICATION.resolve()}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    entries = []
    for path in sorted(REVIEW.rglob("*")):
        if path.resolve() in EXCLUDED:
            continue
        if path.is_symlink() or not path.is_file():
            continue
        entries.append(
            {
                "path": path.relative_to(REVIEW).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    framed = "".join(f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n" for row in entries).encode()
    candidate_after = json.loads((REVIEW / "evidence" / "candidate_after.json").read_text(encoding="utf-8"))
    payload = {
        "schema": "lifeos-p3-141-attempt-2-final-manifest-v1",
        "scope": "Phase B synthetic independent review only",
        "non_self_referential": True,
        "excluded_from_manifest": ["FINAL_MANIFEST.json", "evidence/final_manifest_verification.json"],
        "candidate_read_only_snapshot": {
            "file_count": candidate_after["file_count"],
            "tree_sha256": candidate_after["tree_sha256"],
        },
        "file_count": len(entries),
        "length_framed_tree_sha256": hashlib.sha256(framed).hexdigest(),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
