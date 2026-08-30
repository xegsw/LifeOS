#!/usr/bin/env python3
"""Generate the non-self-referential attempt-7 final manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    entries = {}
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != OUTPUT:
            name = path.relative_to(ROOT).as_posix()
            entries[name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    tree = hashlib.sha256()
    for name, item in entries.items():
        tree.update(name.encode("utf-8"))
        tree.update(b"\0")
        tree.update(str(item["bytes"]).encode("ascii"))
        tree.update(b"\0")
        tree.update(item["sha256"].encode("ascii"))
        tree.update(b"\n")
    document = {
        "schema": "lifeos.p3_141.attempt_7.independent_final_manifest.v1",
        "attempt": "attempt-7",
        "scope": "attempt-7 only",
        "self_reference": "excluded: FINAL_MANIFEST.json",
        "file_count_excluding_manifest": len(entries),
        "tree_sha256_excluding_manifest": tree.hexdigest(),
        "review_conclusion": "REWORK_P0",
        "p0": ["P0-IR-141-01"],
        "files": entries,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
