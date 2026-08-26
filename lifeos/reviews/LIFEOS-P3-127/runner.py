#!/usr/bin/env python3
"""Task-local, standard-library-only verifier for LIFEOS-P3-127.

This module intentionally contains no import, copy, execution, or subprocess
reference to a P3-126 runner. It parses the P3-127 Frozen allowlist itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
from pathlib import Path


ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*`([0-9a-f]{64})`\s*\|\s*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_allowlist(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|") or "Candidate-relative path" in line or "---" in line:
            continue
        match = ROW.fullmatch(line)
        if not match:
            invalid.append({"line": number, "raw": line})
            continue
        relative, byte_count, digest = match.groups()
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            invalid.append({"line": number, "raw": line, "reason": "unsafe-relative-path"})
            continue
        rows.append({"line": number, "path": relative, "bytes": int(byte_count), "sha256": digest})
    if invalid:
        raise ValueError(json.dumps({"invalid_allowlist_rows": invalid}, ensure_ascii=False))
    if len({row["path"] for row in rows}) != len(rows):
        raise ValueError("duplicate candidate path in allowlist")
    return rows


def lineage(allowlist: Path, candidate: Path) -> dict[str, object]:
    rows = parse_allowlist(allowlist)
    evidence: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for row in rows:
        target = candidate / str(row["path"])
        item = {"line": row["line"], "path": row["path"], "expected_bytes": row["bytes"], "expected_sha256": row["sha256"]}
        metadata = target.lstat() if target.exists() else None
        if metadata is None or not stat.S_ISREG(metadata.st_mode) or target.is_symlink():
            item["error"] = "missing-or-not-regular-file"
            failures.append(item)
            continue
        item["actual_bytes"] = target.stat().st_size
        item["actual_sha256"] = sha256(target)
        item["pass"] = item["actual_bytes"] == item["expected_bytes"] and item["actual_sha256"] == item["expected_sha256"]
        evidence.append(item)
        if not item["pass"]:
            failures.append(item)
    return {
        "allowlist": str(allowlist),
        "candidate": str(candidate),
        "physical_markdown_data_rows": len(rows),
        "files_verified": len(evidence),
        "failures": failures,
        "result": "PASS" if not failures and len(evidence) == 75 else "FAIL",
        "rows": evidence,
    }


def copy_exact(allowlist: Path, source: Path, destination: Path) -> dict[str, object]:
    if destination.exists():
        raise ValueError(f"copy destination already exists: {destination}")
    rows = parse_allowlist(allowlist)
    destination.mkdir(parents=True)
    copied: list[str] = []
    try:
        for row in rows:
            relative = Path(str(row["path"]))
            origin = source / relative
            metadata = origin.lstat() if origin.exists() else None
            if metadata is None or not stat.S_ISREG(metadata.st_mode) or origin.is_symlink():
                raise ValueError(f"source is not a regular non-symlink file: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origin, target, follow_symlinks=False)
            copied.append(str(relative))
        verified = lineage(allowlist, destination)
        verified["copy_destination"] = str(destination)
        verified["copied_paths"] = copied
        return verified
    except Exception:
        # No broad cleanup: this caller records a failed copy and keeps artifacts for inspection.
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allowlist", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--copy-destination", type=Path)
    args = parser.parse_args()
    try:
        result = copy_exact(args.allowlist, args.candidate, args.copy_destination) if args.copy_destination else lineage(args.allowlist, args.candidate)
    except Exception as exc:  # evidence must be machine-readable even on parse failure
        result = {"result": "FAIL", "error": str(exc)}
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
