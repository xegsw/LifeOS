#!/usr/bin/env python3
"""Read-only, count-only inspector for this review's synthetic runtime database."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-ui-key-direct-pid-review-v1").resolve()


def fail(reason: str) -> None:
    print(json.dumps({"success": False, "reason": reason}, ensure_ascii=False))
    raise SystemExit(2)


if len(sys.argv) != 2:
    fail("usage: synthetic_runtime_db_summary.py <synthetic-capture.sqlite>")

target = Path(sys.argv[1]).resolve()
if ROOT not in target.parents or target.name != "capture.sqlite":
    fail("refusing non-review synthetic capture.sqlite path")
if not target.is_file():
    fail("synthetic runtime database does not exist")

connection = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
try:
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )]
    counts = {}
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        counts[table] = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
finally:
    connection.close()

print(json.dumps({
    "success": True,
    "schema": "lifeos.p3-141.synthetic-runtime-db-summary.v1",
    "database": str(target),
    "tables": tables,
    "counts": counts,
    "content_read": False,
}, ensure_ascii=False, sort_keys=True))
