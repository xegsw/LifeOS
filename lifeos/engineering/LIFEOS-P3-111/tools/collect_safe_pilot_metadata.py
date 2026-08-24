#!/usr/bin/env python3
"""Collect only filesystem metadata for the authorized Pilot-2 database; never read its bytes."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = Path("/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2")
DB = PILOT / "capture.sqlite"
payload = {
    "authorized_path": str(PILOT),
    "directory_is_real": PILOT.is_dir() and not PILOT.is_symlink(),
    "database_is_regular": DB.is_file() and not DB.is_symlink(),
    "database_bytes": DB.stat().st_size if DB.exists() else None,
    "database_content_read": False,
    "raw_sql_or_shell_used": False,
    "sidecars_absent": {suffix: not Path(f"{DB}{suffix}").exists() for suffix in ["-journal", "-wal", "-shm"]},
}
payload["passed"] = payload["directory_is_real"] and payload["database_is_regular"] and all(payload["sidecars_absent"].values())
out = ROOT / "evidence" / "raw" / "actual-pilot-metadata.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(0 if payload["passed"] else 1)
