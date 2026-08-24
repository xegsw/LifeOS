#!/usr/bin/env python3
"""Create the exact fixed non-sensitive resume-1 app fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
FIXTURE = Path("/private/tmp/lifeos-p3-104-p3-106-app-resume1-20260823")
DB = FIXTURE / "capture.sqlite"
SENTINEL = FIXTURE / "sentinel.txt"


def metadata(path: Path) -> dict[str, object]:
    try:
        value = path.lstat()
        return {"exists": True, "type": stat.filemode(value.st_mode)[0], "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}
    except FileNotFoundError:
        return {"exists": False}


def main() -> None:
    before = metadata(FIXTURE)
    if before["exists"]:
        raise RuntimeError(f"fixture must lstat missing: {FIXTURE}")
    for ancestor in [Path("/"), Path("/private"), Path("/private/tmp")]:
        value = ancestor.lstat()
        if stat.S_ISLNK(value.st_mode):
            raise RuntimeError(f"linked ancestor rejected: {ancestor}")
    FIXTURE.mkdir(mode=0o700)
    SENTINEL.write_text("LIFEOS-P3-106 resume-1 fixed non-sensitive sentinel\n", encoding="utf-8")
    payload = {
        "task": "LIFEOS-P3-106",
        "execution": "resume-1",
        "fixture": str(FIXTURE),
        "db": str(DB),
        "pre_lstat": before,
        "post_lstat": metadata(FIXTURE),
        "sentinel": str(SENTINEL),
        "sentinel_sha256": hashlib.sha256(SENTINEL.read_bytes()).hexdigest(),
        "database_pre_lstat": metadata(DB),
        "allowed_contents": sorted(path.name for path in FIXTURE.iterdir()),
        "status": "PASS",
    }
    (OUT / "main_fixture_before.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
