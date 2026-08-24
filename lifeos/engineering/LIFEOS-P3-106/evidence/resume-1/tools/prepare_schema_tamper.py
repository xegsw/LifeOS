#!/usr/bin/env python3
"""Replace only the exact fixed tamper DB with a schema-tampered variant."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
SOURCE = Path("/private/tmp/lifeos-p3-104-p3-106-app-resume1-20260823/capture.sqlite")
TAMPER_ROOT = Path("/private/tmp/lifeos-p3-104-p3-106-tamper-resume1-20260823")
TARGET = TAMPER_ROOT / "capture.sqlite"
SENTINEL = TAMPER_ROOT / "sentinel.txt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if TAMPER_ROOT.is_symlink() or not TAMPER_ROOT.is_dir() or not SOURCE.is_file() or not SENTINEL.is_file():
        raise RuntimeError("exact tamper fixture boundary unavailable")
    before_sentinel = digest(SENTINEL)
    TARGET.unlink()
    shutil.copyfile(SOURCE, TARGET)
    with sqlite3.connect(TARGET) as connection:
        connection.execute("DROP TABLE audit")
        connection.commit()
    with sqlite3.connect(f"file:{TARGET}?mode=ro", uri=True) as connection:
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    payload = {
        "task": "LIFEOS-P3-106",
        "execution": "resume-1",
        "fixture": str(TAMPER_ROOT),
        "db": str(TARGET),
        "db_sha256": digest(TARGET),
        "tables": tables,
        "expected_missing_table": "audit",
        "sentinel_before": before_sentinel,
        "sentinel_after": digest(SENTINEL),
        "status": "PASS" if "captures" in tables and "audit" not in tables and before_sentinel == digest(SENTINEL) else "FAIL",
    }
    (OUT / "schema_tamper_prepared.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
