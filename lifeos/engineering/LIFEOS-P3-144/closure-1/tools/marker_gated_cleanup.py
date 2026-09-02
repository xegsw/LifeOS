#!/usr/bin/env python3
"""Delete only the P3-144 engineering closure root after exact marker checks."""

import json
import os
import shutil
import stat
import sys
from pathlib import Path


ROOT = Path("/private/tmp/lifeos-p3-144-engineering-v1")
MARKER = ROOT / ".lifeos-p3-144-owner.json"
EXPECTED = {
    "schema": "lifeos.p3-144.engineering-root.v1",
    "task": "LIFEOS-P3-144",
    "owner": "lifeos-p3-144-engineering-v1",
}


def fail(code: str) -> None:
    print(json.dumps({"status": "REFUSED", "code": code}, ensure_ascii=False))
    raise SystemExit(1)


if ROOT != Path("/private/tmp/lifeos-p3-144-engineering-v1") or ROOT.parent != Path("/private/tmp"):
    fail("root_literal_rejected")

try:
    root_stat = os.lstat(ROOT)
except FileNotFoundError:
    fail("root_missing")
if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode) or stat.S_IMODE(root_stat.st_mode) != 0o700:
    fail("root_type_rejected")

try:
    marker_stat = os.lstat(MARKER)
except FileNotFoundError:
    fail("marker_missing")
if not stat.S_ISREG(marker_stat.st_mode) or stat.S_ISLNK(marker_stat.st_mode) or stat.S_IMODE(marker_stat.st_mode) != 0o600:
    fail("marker_type_rejected")

try:
    observed = json.loads(MARKER.read_text(encoding="utf-8"))
except (OSError, ValueError):
    fail("marker_payload_rejected")
if observed != EXPECTED:
    fail("marker_payload_rejected")

shutil.rmtree(ROOT)
if os.path.lexists(ROOT):
    fail("root_absence_rejected")

print(json.dumps({"status": "PASS", "root": str(ROOT), "marker": str(MARKER), "root_absent": True}))
