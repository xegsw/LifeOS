#!/usr/bin/env python3
"""Exact, marker-gated cleanup for this one independent-review attempt."""
from __future__ import annotations

import os
import shutil
from pathlib import Path


REVIEW_ROOT = Path("/Users/xxe/.codex/worktrees/2c4f/No.2/lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-3")
TEMP_ROOT = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1")
MARKER = TEMP_ROOT / ".lifeos-p3-141-review-marker"
EXPECTED_MARKER = "LIFEOS-P3-141 independent-review attempt-3 synthetic-only disposable root\n"
BUILD_TARGETS = (REVIEW_ROOT / "build", REVIEW_ROOT / "build-real")


def ordinary_dir(path: Path) -> bool:
    try:
        return os.path.isdir(path) and not os.path.islink(path)
    except OSError:
        return False


def remove_tree(path: Path) -> None:
    if path.exists() or path.is_symlink():
        shutil.rmtree(path)
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"cleanup did not remove {path}")


def main() -> None:
    if not ordinary_dir(REVIEW_ROOT):
        raise RuntimeError("review root is not the expected ordinary directory")
    for target in BUILD_TARGETS:
        if target.parent != REVIEW_ROOT:
            raise RuntimeError("build target escapes literal review root")
        if target.is_symlink():
            raise RuntimeError("refusing symlink build target")
        remove_tree(target)

    if not ordinary_dir(TEMP_ROOT):
        raise RuntimeError("temporary root is not the expected ordinary directory")
    if MARKER.parent != TEMP_ROOT or MARKER.is_symlink() or not MARKER.is_file():
        raise RuntimeError("missing or unsafe review marker")
    if MARKER.read_text(encoding="utf-8") != EXPECTED_MARKER:
        raise RuntimeError("review marker does not match the literal expected value")
    remove_tree(TEMP_ROOT)
    print("review-build-cache=absent")
    print("unique-temporary-root=absent")


if __name__ == "__main__":
    main()
