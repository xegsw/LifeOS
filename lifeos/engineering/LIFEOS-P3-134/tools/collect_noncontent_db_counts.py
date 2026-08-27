#!/usr/bin/env python3
"""Emit only structural SQLite counts; never read text, payload, IDs, or audit detail."""
from __future__ import annotations

import argparse
import json
import os
import stat
import sqlite3
from pathlib import Path


TABLES = (
    "captures",
    "capture_project_links",
    "candidate_actions",
    "actions",
    "action_results",
    "understandings",
    "feedback",
    "audit",
)


def count(connection: sqlite3.Connection, table: str, where: str = "", params: tuple[object, ...] = ()) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}{where}", params).fetchone()[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", required=True)
    args = parser.parse_args()
    db = args.db.resolve()
    expected_prefix = Path("/private/tmp/lifeos-p3-134-ui-restoration-v1/runtime").resolve()
    if expected_prefix not in db.parents:
        raise SystemExit("database is outside authorized temporary runtime root")
    mode = os.lstat(db).st_mode
    if not stat.S_ISREG(mode):
        raise SystemExit("database is not a regular file")
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.execute("PRAGMA query_only=ON")
    values = {name: count(connection, name) for name in TABLES}
    values.update({
        "open_actions": count(connection, "actions", " WHERE action_state=?", ("open",)),
        "confirmed_context_links": count(connection, "capture_project_links", " WHERE link_status=?", ("confirmed",)),
    })
    result = {
        "task": "LIFEOS-P3-134",
        "kind": "non_content_sqlite_count_receipt",
        "phase": args.phase,
        "db_regular_file": True,
        "db_content_read": False,
        "selected_columns": ["COUNT(*)"],
        "counts": values,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
