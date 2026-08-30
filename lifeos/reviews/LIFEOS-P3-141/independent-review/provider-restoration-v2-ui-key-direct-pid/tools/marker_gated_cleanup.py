#!/usr/bin/env python3
"""Delete only the one review-owned temporary root after strict marker checks."""
import argparse
import json
import os
import shutil
import stat
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-ui-key-direct-pid-review-v1")
MARKER = "REVIEW_OWNED_MARKER.json"
EXPECTED = {
    "schema": "lifeos.p3-141.provider-restoration-v2-ui-key-direct-pid.review-temp-marker.v1",
    "task_id": "LIFEOS-P3-141",
    "purpose": "review-owned isolated synthetic actual-Tauri verification",
    "cleanup_policy": "literal-path marker-gated only",
}


def reject(message):
    raise SystemExit(message)


def checked_root():
    if ROOT.absolute() != ROOT or ROOT.is_symlink():
        reject("literal temporary root rejected")
    root_meta = ROOT.lstat()
    if not stat.S_ISDIR(root_meta.st_mode):
        reject("temporary root is not a directory")
    marker = ROOT / MARKER
    marker_meta = marker.lstat()
    if stat.S_ISLNK(marker_meta.st_mode) or not stat.S_ISREG(marker_meta.st_mode):
        reject("marker is not a regular file")
    if json.loads(marker.read_text(encoding="utf-8")) != EXPECTED:
        reject("marker content rejected")
    return marker


parser = argparse.ArgumentParser()
parser.add_argument("--execute", action="store_true")
parser.add_argument("--receipt", type=Path, required=True)
args = parser.parse_args()
if not args.execute:
    reject("refusing cleanup without --execute")
marker = checked_root()
receipt = args.receipt.resolve()
if ROOT in receipt.parents or receipt == ROOT:
    reject("cleanup receipt must be outside temporary root")
receipt.parent.mkdir(parents=True, exist_ok=True)
receipt.write_text(json.dumps({
    "schema": "lifeos.p3-141.marker-gated-cleanup-receipt.v1",
    "literal_root": str(ROOT),
    "marker": str(marker),
    "marker_validated": True,
    "operation": "shutil.rmtree literal root",
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
shutil.rmtree(ROOT)
if ROOT.exists() or ROOT.is_symlink():
    reject("cleanup postcondition failed")
print(json.dumps({"success": True, "removed_literal_root": str(ROOT), "receipt": str(receipt)}))
