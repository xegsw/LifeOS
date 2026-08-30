#!/usr/bin/env python3
"""Render the immutable pre-receipt review evidence Manifest to stdout."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


COMMIT = "c7087586d89a52bc252765ec89fa63611f585d0e"
CANDIDATE_TREE = "ffde1eaa9d595441ee96bc50dbbfbffab933a53f0c6feac7c94ab45a3938d6ef"
EXCLUDED = {"FINAL_MANIFEST.json", "phase_b_pass_receipt.json"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_review_manifest.py ATTEMPT_ROOT")
    root = Path(sys.argv[1]).resolve(strict=True)
    records: dict[str, dict[str, object]] = {}
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs.sort()
        for name in sorted(names):
            item = Path(current) / name
            rel = item.relative_to(root).as_posix()
            if rel in EXCLUDED:
                continue
            if item.is_symlink() or not item.is_file():
                raise SystemExit(f"non-regular-or-linked review artifact: {rel}")
            body = item.read_bytes()
            records[rel] = {"bytes": len(body), "sha256": sha256(body)}
    digest = hashlib.sha256()
    for rel in sorted(records, key=lambda value: tuple(value.split("/"))):
        body = (root / rel).read_bytes()
        encoded = rel.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(body).to_bytes(8, "big"))
        digest.update(body)
    manifest = {
        "schema": "lifeos.p3-141.phase-b-independent-manifest.v1",
        "task_id": "LIFEOS-P3-141",
        "review_identity": {"role": "independent_review", "attempt_id": "attempt-8"},
        "review_conclusion": "PASS",
        "candidate_commit": COMMIT,
        "candidate_tree_sha256": CANDIDATE_TREE,
        "file_count_excluding_manifest": len(records),
        "tree_sha256_excluding_manifest": digest.hexdigest(),
        "files": records,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
