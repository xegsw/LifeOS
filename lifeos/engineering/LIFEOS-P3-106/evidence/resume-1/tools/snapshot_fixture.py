#!/usr/bin/env python3
"""Write a structured snapshot of the fixed non-sensitive resume app fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import stat
import sys


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
FIXTURE = Path("/private/tmp/lifeos-p3-104-p3-106-app-resume1-20260823")
DB = FIXTURE / "capture.sqlite"
SENTINEL = FIXTURE / "sentinel.txt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path: Path) -> dict[str, object]:
    try:
        value = path.lstat()
        return {"exists": True, "type": stat.filemode(value.st_mode)[0], "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}
    except FileNotFoundError:
        return {"exists": False}


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].replace("-", "").isalnum():
        raise SystemExit("usage: snapshot_fixture.py SAFE-LABEL")
    label = sys.argv[1]
    if not DB.is_file() or DB.is_symlink():
        raise RuntimeError("fixed DB missing or linked")
    uri = f"file:{DB}?mode=ro&immutable=1"
    with sqlite3.connect(uri, uri=True) as connection:
        quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
        captures = connection.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        audits = connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
        audit_actions = [row[0] for row in connection.execute("SELECT event FROM audit ORDER BY id")]
    payload = {
        "task": "LIFEOS-P3-106",
        "execution": "resume-1",
        "label": label,
        "fixture": str(FIXTURE),
        "fixture_metadata": metadata(FIXTURE),
        "db_metadata": metadata(DB),
        "db_sha256": digest(DB),
        "quick_check": quick_check,
        "captures": captures,
        "audits": audits,
        "audit_actions": audit_actions,
        "sentinel_metadata": metadata(SENTINEL),
        "sentinel_sha256": digest(SENTINEL),
        "sidecars": {suffix: metadata(Path(f"{DB}-{suffix}")) for suffix in ["journal", "wal", "shm"]},
        "status": "PASS" if quick_check == "ok" else "FAIL",
    }
    output = OUT / f"fixture-{label}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "captures": captures, "audits": audits, "quick_check": quick_check, "sentinel": payload["sentinel_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
