#!/usr/bin/env python3
"""Prepare the single authorized P3-110 tamper fixture with schema drift."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
NOMINAL = Path("/private/tmp/lifeos-p3-104-p3-110-review-nominal-v1/capture.sqlite")
TAMPER = Path("/private/tmp/lifeos-p3-104-p3-110-review-tamper-v1")

if not NOMINAL.is_file():
    raise SystemExit("nominal fixture missing")
if TAMPER.is_symlink() or TAMPER.is_file():
    TAMPER.unlink()
elif TAMPER.exists():
    shutil.rmtree(TAMPER)
TAMPER.mkdir()
db = TAMPER / "capture.sqlite"
shutil.copy2(NOMINAL, db)
source_hash = hashlib.sha256(NOMINAL.read_bytes()).hexdigest()
connection = sqlite3.connect(db)
connection.execute("CREATE TABLE p3_110_unexpected_schema (id INTEGER PRIMARY KEY, note TEXT)")
connection.commit()
connection.close()
sentinel = TAMPER / "sentinel.txt"
sentinel.write_text("P3-110 SCHEMA TAMPER SENTINEL\n", encoding="utf-8")
payload = {
    "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "fixture": str(TAMPER),
    "db": str(db),
    "nominal_sha256": source_hash,
    "schema_tamper_sha256": hashlib.sha256(db.read_bytes()).hexdigest(),
    "sentinel_sha256": hashlib.sha256(sentinel.read_bytes()).hexdigest(),
    "mutation": "added unexpected table p3_110_unexpected_schema",
}
(EVIDENCE / "schema-tamper-prepare.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
