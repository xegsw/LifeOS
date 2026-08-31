#!/usr/bin/env python3
"""Marker-gated cleanup for this review's sole authorized temporary root."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys

LITERAL_ROOT = "/private/tmp/lifeos-p3-141-revision-3-independent-review-mode-delete-v1"
MARKER_NAME = ".lifeos-p3-141-independent-review-cleanup-marker"
MARKER_BYTES = b"lifeos-p3-141-revision-3-independent-review-mode-delete-v1\n"


def report(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reject(root: Path, output: Path, code: str) -> int:
    report(output, {"schema": "lifeos.p3-141.review-cleanup.v1", "root": str(root), "status": "refused", "code": code, "root_exists_after": os.path.lexists(root)})
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root)
    output = Path(args.output)
    if str(root) != LITERAL_ROOT or root.parent != Path("/private/tmp"):
        return reject(root, output, "literal_root_rejected")
    try:
        root_stat = os.lstat(root)
    except FileNotFoundError:
        return reject(root, output, "root_absent")
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode) or stat.S_IMODE(root_stat.st_mode) != 0o700:
        return reject(root, output, "root_type_or_mode_rejected")
    marker = root / MARKER_NAME
    try:
        marker_stat = os.lstat(marker)
        marker_bytes = marker.read_bytes()
    except FileNotFoundError:
        return reject(root, output, "marker_missing")
    if stat.S_ISLNK(marker_stat.st_mode) or not stat.S_ISREG(marker_stat.st_mode) or marker_stat.st_nlink != 1 or stat.S_IMODE(marker_stat.st_mode) != 0o600:
        return reject(root, output, "marker_type_or_mode_rejected")
    if marker_bytes != MARKER_BYTES:
        return reject(root, output, "marker_content_rejected")
    shutil.rmtree(root)
    removed = not os.path.lexists(root)
    report(output, {"schema": "lifeos.p3-141.review-cleanup.v1", "root": str(root), "status": "removed" if removed else "failed", "literal_root_absent": removed})
    return 0 if removed else 1


if __name__ == "__main__":
    raise SystemExit(main())
