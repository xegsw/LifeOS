#!/usr/bin/env python3
"""Exact, review-owned cleanup for the only P3-143 re-review-3 runtime root."""

import json
import os
import shutil
import stat
import sys
from pathlib import Path

ALLOWED_ROOT_RUN_IDS = {
    "/private/tmp/lifeos-p3-143-independent-review-rereview3-20260902": "rereview3-20260902",
    "/private/tmp/lifeos-p3-143-independent-review-bundleui-20260902": "bundleui-20260902",
}
RECEIPT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-3/cleanup_receipt.json")


def mode(path: Path) -> int:
    return stat.S_IMODE(os.lstat(path).st_mode)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("exact_literal_root_required")
    root = Path(sys.argv[1])
    run_id = ALLOWED_ROOT_RUN_IDS.get(str(root))
    if run_id is None:
        raise SystemExit("root_allowlist_gate_rejected")
    marker = root / ".lifeos-p3-143-owner.json"
    expected = {
        "schema": "lifeos.p3-143.independent-review-root.v1",
        "task": "LIFEOS-P3-143",
        "owner": "lifeos-p3-143-independent-review",
        "runId": run_id,
    }
    root_meta = os.lstat(root)
    if not stat.S_ISDIR(root_meta.st_mode) or stat.S_ISLNK(root_meta.st_mode) or mode(root) != 0o700:
        raise SystemExit("root_marker_gate_rejected")
    marker_meta = os.lstat(marker)
    if not stat.S_ISREG(marker_meta.st_mode) or stat.S_ISLNK(marker_meta.st_mode) or mode(marker) != 0o600:
        raise SystemExit("marker_type_gate_rejected")
    if json.loads(marker.read_text(encoding="utf-8")) != expected:
        raise SystemExit("marker_payload_gate_rejected")
    for parent, directories, filenames in os.walk(root, followlinks=False):
        for name in directories + filenames:
            path = Path(parent) / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise SystemExit("nested_symlink_gate_rejected")
    shutil.rmtree(root)
    if root.exists() or root.is_symlink():
        raise SystemExit("post_cleanup_absence_failed")
    RECEIPT.write_text(json.dumps({
        "schema": "lifeos.p3-143.independent-rereview-3.cleanup.v1",
        "literal_root": str(root),
        "marker": str(marker.name),
        "marker_mode": "0600",
        "root_mode": "0700",
        "writers_stopped": True,
        "result": "CLEANED_AND_ABSENT",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("CLEANED_AND_ABSENT")


if __name__ == "__main__":
    main()
