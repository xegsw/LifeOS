#!/usr/bin/env python3
"""Emit only non-content state for an authorized synthetic re-review runtime."""
from __future__ import annotations

import json
import sqlite3
import stat
import sys
from pathlib import Path


BASE = Path("/private/tmp/lifeos-p3-133-independent-re-review-v1")
REVIEW = Path("/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-133/re-review-1")
TABLES = ["captures", "capture_project_links", "candidate_actions", "actions", "feedback", "audit", "understandings"]


def noncontent_state(name: str) -> dict[str, object]:
    runtime = BASE / name
    if runtime.parent != BASE or name not in {"runtime", "runtime-201", "runtime-201check", "runtime-existingdb"}:
        raise SystemExit("unauthorized runtime label")
    data: dict[str, object] = {"runtime_label": name, "runtime_exists": runtime.exists()}
    if runtime.exists():
        meta = runtime.lstat()
        data["runtime_type"] = "directory" if stat.S_ISDIR(meta.st_mode) else "other"
        data["runtime_symlink"] = stat.S_ISLNK(meta.st_mode)
    db = runtime / "capture.sqlite"
    data["database_exists"] = db.exists()
    if not db.exists():
        return data
    meta = db.lstat()
    data["database_type"] = "regular" if stat.S_ISREG(meta.st_mode) else "other"
    data["database_symlink"] = stat.S_ISLNK(meta.st_mode)
    data["database_bytes"] = meta.st_size
    data["database_inode"] = meta.st_ino
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        try:
            data["counts"] = {
                table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in TABLES
            }
            data["open_actions"] = conn.execute("SELECT count(*) FROM actions WHERE action_state='open'").fetchone()[0]
            data["database_contract_readable"] = True
        except sqlite3.DatabaseError as error:
            data["database_contract_readable"] = False
            data["database_error_class"] = type(error).__name__
    finally:
        conn.close()
    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: runtime_probe.py RUNTIME_LABEL OUTPUT_NAME")
    state = noncontent_state(sys.argv[1])
    output = REVIEW / sys.argv[2]
    if output.parent != REVIEW or output.name != sys.argv[2]:
        raise SystemExit("unauthorized output")
    output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
