#!/usr/bin/env python3
"""Verify every listed hash and the explicit non-self exclusion of the manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
MANIFEST = REVIEW / "FINAL_MANIFEST.json"
OUTPUT = REVIEW / "evidence" / "final_manifest_verification.json"
EXCLUDED = {"FINAL_MANIFEST.json", "evidence/final_manifest_verification.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest["entries"]
    listed = {row["path"] for row in rows}
    observed = {
        path.relative_to(REVIEW).as_posix()
        for path in REVIEW.rglob("*")
        if path.is_file() and not path.is_symlink() and path.relative_to(REVIEW).as_posix() not in EXCLUDED
    }
    checks = []
    for row in rows:
        path = REVIEW / row["path"]
        checks.append(
            {
                "path": row["path"],
                "exists": path.is_file() and not path.is_symlink(),
                "bytes_match": path.is_file() and path.stat().st_size == row["bytes"],
                "sha256_match": path.is_file() and sha256(path) == row["sha256"],
            }
        )
    framed = "".join(f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n" for row in rows).encode()
    structural = (
        manifest.get("non_self_referential") is True
        and set(manifest.get("excluded_from_manifest", [])) == EXCLUDED
        and not (listed & EXCLUDED)
        and listed == observed
        and len(listed) == len(rows)
        and manifest.get("length_framed_tree_sha256") == hashlib.sha256(framed).hexdigest()
    )
    payload = {
        "schema": "lifeos-p3-141-attempt-2-final-manifest-verification-v1",
        "manifest": str(MANIFEST),
        "entry_count": len(rows),
        "entry_checks": checks,
        "structural_pass": structural,
        "pass": structural and all(all(item.values()) for item in checks),
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
