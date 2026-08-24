#!/usr/bin/env python3
"""Remove only ABF-authorized P3-110 temporary work and fixtures, then record residue."""
from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
WORK = Path("/private/tmp/lifeos-p3-110-review-work-v1")
NAMES = ["nominal", "reopen", "failure", "dangling-final", "dangling-journal", "dangling-wal", "dangling-shm", "path", "link", "hardlink", "tamper", "a11y", "narrow"]
FIXTURES = [Path(f"/private/tmp/lifeos-p3-104-p3-110-review-{name}-v1") for name in NAMES]
UNIT = [
    re.compile(r"^lifeos-p3-104-unit-(lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+$"),
    re.compile(r"^lifeos-p3-104-unit-link-target-[0-9]+$"),
    re.compile(r"^lifeos-p3-104-unit-link-[0-9]+$"),
]

def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)

removed = []
for target in [WORK, *FIXTURES]:
    existed = os.path.lexists(target)
    if existed:
        remove(target)
        removed.append(str(target))
names = os.listdir("/private/tmp")
unit_residue = sorted(name for name in names if any(pattern.fullmatch(name) for pattern in UNIT))
fixture_residue = [str(path) for path in FIXTURES if os.path.lexists(path)]
payload = {
    "cleaned_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "removed": removed,
    "work": str(WORK),
    "work_exists": os.path.lexists(WORK),
    "authorized_fixture_residue": fixture_residue,
    "unit_regex_residue": unit_residue,
    "external_path_created": os.path.lexists("/private/tmp/lifeos-p3-110-outside"),
}
(EVIDENCE / "cleanup.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if payload["work_exists"] or fixture_residue or unit_residue or payload["external_path_created"]:
    raise SystemExit(1)
