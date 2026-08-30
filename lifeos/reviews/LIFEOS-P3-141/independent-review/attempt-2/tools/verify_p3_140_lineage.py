#!/usr/bin/env python3
"""Verify P3-140's published 79-file candidate lineage without mutation."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_p3_140_lineage.py MANIFEST CANDIDATE OUTPUT_JSON")
    manifest_path = Path(sys.argv[1]).resolve(strict=True)
    candidate = Path(sys.argv[2]).resolve(strict=True)
    output = Path(sys.argv[3]).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest["candidate"]
    actual_paths = {
        path.relative_to(candidate).as_posix()
        for path in candidate.rglob("*") if path.is_file() and not path.is_symlink()
    }
    expected_paths = set(expected["entries"])
    rows = []
    for rel in sorted(expected_paths | actual_paths):
        path = candidate / rel
        item = expected["entries"].get(rel)
        actual = None
        if path.is_file() and not path.is_symlink():
            actual = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        rows.append({
            "path": rel,
            "expected": item,
            "actual": actual,
            "pass": item == actual,
        })
    published_tree = expected["length_framed_tree_sha256"]
    payload = {
        "schema_version": "lifeos.p3_141.phase_b.p3_140_lineage.v1",
        "manifest_sha256": sha256(manifest_path),
        "published_file_count": expected["file_count"],
        "actual_file_count": len(actual_paths),
        "published_length_framed_tree_sha256": published_tree,
        "expected_inventory_tree_sha256": "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e",
        "entry_pass_count": sum(1 for row in rows if row["pass"]),
        "entry_fail_count": sum(1 for row in rows if not row["pass"]),
        "pass": (
            expected["file_count"] == 79
            and len(actual_paths) == 79
            and published_tree == "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e"
            and all(row["pass"] for row in rows)
        ),
        "entries": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
