#!/usr/bin/env python3
"""Review-owned, redacted SQLite integrity observations for synthetic P3-141 only."""
import hashlib
import json
import os
import sqlite3
import stat
import sys
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-revision-3-independent-review-final-v4")
DB = ROOT / "runtime" / "capture.sqlite"
KEY = ROOT / "keys" / "credential-aead.key"
CANARIES = {
    "v1": b"review-synthetic-credential-v1-8a2f",
    "v2": b"review-synthetic-credential-v2-6c9d",
}

if len(sys.argv) != 3:
    raise SystemExit("usage: credential_db_probe.py PHASE OUTPUT_JSON")
phase, output = sys.argv[1:]
report = {
    "schema": "lifeos.p3-141.review-credential-db-probe.v1",
    "phase": phase,
    "root_exact": str(ROOT),
    "db_exists": DB.is_file(),
}
if not DB.is_file():
    report["status"] = "blocked"
    report["reason"] = "synthetic review database absent"
else:
    db_stat = DB.stat()
    report["db_mode"] = format(stat.S_IMODE(db_stat.st_mode), "04o")
    report["db_is_regular"] = stat.S_ISREG(db_stat.st_mode)
    report["db_nlink"] = db_stat.st_nlink
    raw = DB.read_bytes()
    report["canary_v1_absent_from_raw_db"] = CANARIES["v1"] not in raw
    report["canary_v2_absent_from_raw_db"] = CANARIES["v2"] not in raw
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as conn:
        credentials = list(conn.execute(
            "SELECT mode, profile, key_id, length(nonce), length(ciphertext), ciphertext "
            "FROM encrypted_provider_credentials ORDER BY mode, profile"
        ))
        report["credential_row_count"] = len(credentials)
        report["credential_rows_redacted"] = [
            {
                "mode": row[0], "profile": row[1], "key_id": row[2],
                "nonce_length": row[3], "ciphertext_length": row[4],
                "ciphertext_sha256": hashlib.sha256(row[5]).hexdigest(),
            }
            for row in credentials
        ]
        report["provider_mode_state_modes"] = [row[0] for row in conn.execute(
            "SELECT mode FROM provider_mode_state ORDER BY mode"
        )]
        active = list(conn.execute("SELECT active_mode FROM provider_runtime_state WHERE id=1"))
        report["active_mode"] = active[0][0] if len(active) == 1 else None
    if KEY.exists() or KEY.is_symlink():
        key_stat = KEY.lstat()
        report["key_is_regular"] = stat.S_ISREG(key_stat.st_mode)
        report["key_is_symlink"] = stat.S_ISLNK(key_stat.st_mode)
        report["key_mode"] = format(stat.S_IMODE(key_stat.st_mode), "04o")
        report["key_size"] = key_stat.st_size
        report["key_nlink"] = key_stat.st_nlink
        report["key_outside_runtime_db_directory"] = KEY.parent != DB.parent
    else:
        report["key_missing"] = True
    report["status"] = "completed"
Path(output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
