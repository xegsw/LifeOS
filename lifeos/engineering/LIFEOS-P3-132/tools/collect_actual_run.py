#!/usr/bin/env python3
"""Emit a read-only, row-level SQLite/audit snapshot for one actual P3-132 run."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


TABLES = (
    "captures",
    "projects",
    "capture_project_links",
    "derivations",
    "understandings",
    "feedback",
    "candidate_actions",
    "actions",
    "action_results",
    "audit",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(connection: sqlite3.Connection, table: str) -> list[dict[str, object]]:
    cursor = connection.execute(f"SELECT * FROM {table} ORDER BY rowid")
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, record)) for record in cursor.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runtime_root = args.runtime_root.resolve(strict=True)
    database = runtime_root / "capture.sqlite"
    if not database.is_file():
        raise SystemExit(f"missing database: {database}")
    if database.is_symlink():
        raise SystemExit(f"database must not be a link: {database}")

    uri = f"file:{database}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        table_rows = {table: rows(connection, table) for table in TABLES}
    finally:
        connection.close()

    output = {
        "contract": "LIFEOS-P3-132",
        "evidence_kind": "actual_tauri_sqlite_audit_snapshot",
        "case": args.case,
        "runtime_root": str(runtime_root),
        "database": {
            "filename": database.name,
            "bytes": database.stat().st_size,
            "sha256": digest(database),
            "read_mode": "sqlite_uri_mode_ro",
        },
        "row_counts": {table: len(table_rows[table]) for table in TABLES},
        "rows": table_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
