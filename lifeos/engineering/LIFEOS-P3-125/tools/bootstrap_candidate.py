#!/usr/bin/env python3
"""Create the P3-125 candidate solely from its frozen positive allowlist."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


ROW = re.compile(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: bootstrap_candidate.py WORKSPACE ALLOWLIST ENGINEERING_ROOT")
    workspace = Path(sys.argv[1]).resolve()
    allowlist = Path(sys.argv[2]).resolve()
    engineering_root = Path(sys.argv[3]).resolve()
    source_root = workspace / "lifeos/engineering/LIFEOS-P3-122/candidate"
    candidate_root = engineering_root / "candidate"
    evidence_path = engineering_root / "evidence/results/source-lineage.json"

    if candidate_root.exists() or evidence_path.exists():
        raise SystemExit("refusing to overwrite existing P3-125 candidate or source-lineage evidence")

    entries: list[tuple[Path, int, str]] = []
    for line_number, line in enumerate(allowlist.read_text(encoding="utf-8").splitlines(), 1):
        match = ROW.match(line)
        if not match:
            continue
        absolute, declared_bytes, declared_hash = match.groups()
        source = workspace / absolute
        try:
            relative = source.relative_to(source_root)
        except ValueError as error:
            raise SystemExit(f"allowlist line {line_number} escapes P3-122 candidate: {absolute}") from error
        if source != source_root / relative or not source.is_file() or source.is_symlink():
            raise SystemExit(f"allowlist line {line_number} is not a regular P3-122 candidate file: {absolute}")
        actual_bytes = source.stat().st_size
        actual_hash = sha256(source)
        if actual_bytes != int(declared_bytes) or actual_hash != declared_hash:
            raise SystemExit(f"allowlist line {line_number} source bytes/hash mismatch: {absolute}")
        entries.append((relative, actual_bytes, actual_hash))

    if len(entries) != 75 or len({item[0] for item in entries}) != 75:
        raise SystemExit(f"frozen allowlist must contain exactly 75 distinct entries, got {len(entries)}")

    for relative, _, _ in entries:
        destination = candidate_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / relative, destination)

    rows = []
    for relative, expected_bytes, expected_hash in entries:
        destination = candidate_root / relative
        actual_bytes = destination.stat().st_size
        actual_hash = sha256(destination)
        if actual_bytes != expected_bytes or actual_hash != expected_hash:
            raise SystemExit(f"candidate copy verification failed: {relative}")
        rows.append(
            {
                "path": str(relative),
                "bytes": actual_bytes,
                "sha256": actual_hash,
                "source_equals_candidate": True,
            }
        )

    evidence_path.parent.mkdir(parents=True, exist_ok=False)
    payload = {
        "task": "LIFEOS-P3-125",
        "result": "PASS",
        "frozen_allowlist": str(allowlist.relative_to(workspace)),
        "allowlist_sha256": sha256(allowlist),
        "source_root": str(source_root.relative_to(workspace)),
        "candidate_root": str(candidate_root.relative_to(workspace)),
        "entry_count": len(rows),
        "candidate_tree_baseline": "ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742",
        "rows": rows,
    }
    evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
