#!/usr/bin/env python3
"""Marker-gated cleanup for the sole P3-141 Revision-3 synthetic root."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-revision-3-engineering-closure-mode-delete-v1")
MARKER = ROOT / ".lifeos-p3-141-authorized-synthetic-root.json"
EXPECTED = {
    "schema": "lifeos.p3-141.authorized-synthetic-root.v1",
    "task_id": "LIFEOS-P3-141",
    "authorized_root": str(ROOT),
    "mode": "revision_3_synthetic",
    "owner": "lifeos-p3-141-revision-3-synthetic-root-authority",
}


def validate_root() -> None:
    if ROOT.is_symlink() or not ROOT.is_dir() or MARKER.is_symlink() or not MARKER.is_file():
        raise ValueError("authorized root or marker is missing, non-directory, or a symlink")
    if json.loads(MARKER.read_text(encoding="utf-8")) != EXPECTED:
        raise ValueError("marker does not exactly authorize this literal root")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"runtime", "root"}:
        print(json.dumps({"result": "refused", "reason": "scope must be runtime or root"}, ensure_ascii=False))
        return 64
    scope = sys.argv[1]
    try:
        validate_root()
        target = ROOT / "runtime" if scope == "runtime" else ROOT
        if target.is_symlink():
            raise ValueError("cleanup target is a symlink")
        if not target.exists():
            raise ValueError("cleanup target does not exist")
        shutil.rmtree(target)
        print(json.dumps({"result": "removed", "scope": scope, "target": str(target)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"result": "refused", "scope": scope, "reason": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
