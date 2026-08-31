#!/usr/bin/env python3
"""Marker-gated exact cleanup for the single synthetic root authorized here."""
from __future__ import annotations
import json
import os
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-revision-3-independent-review-final-v4")
MARKER = ROOT / ".lifeos-p3-141-authorized-synthetic-root.json"
EXPECTED = {
    "schema": "lifeos.p3-141.authorized-synthetic-root.v1",
    "task_id": "LIFEOS-P3-141",
    "authorized_root": str(ROOT),
    "mode": "revision_3_synthetic",
    "owner": "lifeos-p3-141-revision-3-synthetic-root-authority",
}

def failure(reason: str) -> dict[str, object]:
    return {"schema": "lifeos.p3-141.review-exact-cleanup.v1", "root": str(ROOT), "status": "refused", "reason": reason, "root_still_exists": ROOT.exists()}

def validate() -> dict[str, object] | None:
    if ROOT.parent != Path("/private/tmp") or ROOT.name != "lifeos-p3-141-revision-3-independent-review-final-v4": return failure("root_literal_mismatch")
    try: root_meta = ROOT.lstat()
    except FileNotFoundError: return failure("root_missing")
    if not stat.S_ISDIR(root_meta.st_mode) or stat.S_ISLNK(root_meta.st_mode): return failure("root_not_real_directory")
    try: marker_meta = MARKER.lstat()
    except FileNotFoundError: return failure("marker_missing")
    if not stat.S_ISREG(marker_meta.st_mode): return failure("marker_not_regular")
    if stat.S_ISLNK(marker_meta.st_mode): return failure("marker_symlink")
    if marker_meta.st_nlink != 1: return failure("marker_nlink_not_one")
    if stat.S_IMODE(marker_meta.st_mode) != 0o600: return failure("marker_mode_not_0600")
    try: parsed = json.loads(MARKER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return failure("marker_unreadable")
    if parsed != EXPECTED: return failure("marker_content_mismatch")
    return None

if len(sys.argv) != 3 or sys.argv[1] not in {"validate", "cleanup"}:
    raise SystemExit("usage: cleanup_exact.py {validate|cleanup} OUTPUT_JSON")
action, target = sys.argv[1:]
result = validate()
if result is not None:
    Path(target).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(74)
if action == "validate":
    Path(target).write_text(json.dumps({"schema": "lifeos.p3-141.review-exact-cleanup.v1", "root": str(ROOT), "status": "validated", "root_still_exists": True}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0)
shutil.rmtree(ROOT)
result = {"schema": "lifeos.p3-141.review-exact-cleanup.v1", "root": str(ROOT), "status": "cleaned", "root_absent_after_cleanup": not ROOT.exists()}
Path(target).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
raise SystemExit(0 if result["root_absent_after_cleanup"] else 75)
