#!/usr/bin/env python3
"""Delete only the exact P3-141 bundle-lineage root after strict marker validation."""

import json
import os
import shutil
import stat
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-revision-3-engineering-bundle-lineage-v1")
MARKER = ROOT / ".lifeos-p3-141-authorized-synthetic-root.json"
EXPECTED = {
    "schema": "lifeos.p3-141.authorized-synthetic-root.v1",
    "task_id": "LIFEOS-P3-141",
    "authorized_root": str(ROOT),
    "mode": "revision_3_synthetic",
    "owner": "lifeos-p3-141-revision-3-synthetic-root-authority",
}

root_stat = ROOT.lstat()
marker_stat = MARKER.lstat()
if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode) or stat.S_IMODE(root_stat.st_mode) != 0o700:
    raise SystemExit("refusing cleanup: root is not an exact 0700 non-symlink directory")
if stat.S_ISLNK(marker_stat.st_mode) or not stat.S_ISREG(marker_stat.st_mode) or stat.S_IMODE(marker_stat.st_mode) != 0o600 or marker_stat.st_nlink != 1:
    raise SystemExit("refusing cleanup: marker is not an exact 0600 non-symlink regular file")
if json.loads(MARKER.read_text(encoding="utf-8")) != EXPECTED:
    raise SystemExit("refusing cleanup: marker does not bind the exact literal root")
shutil.rmtree(ROOT)
try:
    ROOT.lstat()
except FileNotFoundError:
    print(json.dumps({"root": str(ROOT), "literal_absent": True}, sort_keys=True))
    raise SystemExit(0)
raise SystemExit("cleanup failed: literal root still exists")
