#!/usr/bin/env python3
"""Generate or verify the task-root-only, non-self-referential final manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = TASK_ROOT / "evidence" / "FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(TASK_ROOT.rglob("*")):
        if path.is_file() and path != OUTPUT:
            result[path.relative_to(TASK_ROOT).as_posix()] = sha256(path)
    return result


def document() -> dict[str, object]:
    files = entries()
    tree = hashlib.sha256()
    for name, digest in files.items():
        tree.update(name.encode("utf-8"))
        tree.update(b"\\0")
        tree.update(digest.encode("ascii"))
        tree.update(b"\\n")
    return {
        "schema": "lifeos.p3-141.final-manifest.v3",
        "scope": "task-root only; fixed temporary root is excluded after exact cleanup",
        "self_reference": "excluded: evidence/FINAL_MANIFEST.json",
        "file_count_excluding_manifest": len(files),
        "tree_sha256_excluding_manifest": tree.hexdigest(),
        "phase_status": {"phase_a": "READY_FOR_INDEPENDENT_REVIEW", "phase_b": "PENDING", "phase_c": "PENDING", "phase_d": "PENDING", "phase_e": "PENDING"},
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(document(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.verify:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("final manifest mismatch")
        print("FINAL_MANIFEST_MATCH")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print("FINAL_MANIFEST_WRITTEN")


if __name__ == "__main__":
    main()
