#!/usr/bin/env python3
"""PM-only fixed-fixture checks for attempt-8 schema fail-closed behavior."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path


FIXED_TEXT = "P3-094 PM fixed non-sensitive schema fixture"
STALE_PAGE = b"P3-094 PM fixed non-sensitive stale page\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_state(path: Path) -> dict:
    return {
        "exists": path.exists(),
        "size": path.stat().st_size if path.is_file() else None,
        "sha256": sha256(path) if path.is_file() else None,
    }


def load_runtime(source: Path):
    spec = importlib.util.spec_from_file_location("p3_094_attempt8_pm", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime load failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_schema(db: Path, *, missing_all_constraints: bool) -> None:
    with sqlite3.connect(db) as conn:
        if missing_all_constraints:
            conn.executescript(
                """
                CREATE TABLE captures (
                  id TEXT, content TEXT, created_at TEXT, source TEXT, idem_key TEXT
                );
                CREATE TABLE audit (
                  id INTEGER, event TEXT, capture_id TEXT, created_at TEXT, detail TEXT
                );
                """
            )
            source = "external_fixture"
        else:
            conn.executescript(
                """
                CREATE TABLE captures (
                  id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at TEXT NOT NULL,
                  source TEXT NOT NULL CHECK(source = 'local_capture'), idem_key TEXT NOT NULL
                );
                CREATE TABLE audit (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, capture_id TEXT,
                  created_at TEXT NOT NULL, detail TEXT NOT NULL
                );
                """
            )
            source = "local_capture"
        conn.execute(
            "INSERT INTO captures(id, content, created_at, source, idem_key) VALUES(?, ?, ?, ?, ?)",
            ("fixed-id", FIXED_TEXT, "2026-08-22T12:00:00+00:00", source, "fixed-key"),
        )


def run_case(runtime, root: Path, name: str, *, missing_all_constraints: bool) -> dict:
    case = root / name
    case.mkdir()
    db = case / "capture.sqlite"
    page = case / "today.html"
    create_schema(db, missing_all_constraints=missing_all_constraints)
    page.write_bytes(STALE_PAGE)
    db_before = file_state(db)
    page_before = file_state(page)
    try:
        result = runtime.render_today(db)
        error_type = None
    except runtime.CaptureError as exc:
        result = None
        error_type = type(exc).__name__
    db_after = file_state(db)
    page_after = file_state(page)
    page_bytes = page.read_bytes() if page.is_file() else b""
    rejected = result is None
    stale_invalidated = not page.exists()
    return {
        "id": name,
        "expected": "reject incomplete schema and invalidate stale page",
        "pm_status": "PASS" if rejected and stale_invalidated and db_before == db_after else "FAIL",
        "render_result_status": result.get("status") if result else None,
        "error_type": error_type,
        "stale_page_invalidated": stale_invalidated,
        "page_hash_changed": page_before.get("sha256") != page_after.get("sha256"),
        "rendered_page_contains_fixed_fixture": FIXED_TEXT.encode() in page_bytes,
        "rendered_page_claims_local_capture": "来源：本地捕获".encode() in page_bytes,
        "db_bytes_unchanged": db_before == db_after,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = load_runtime(args.source.resolve())
    work = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-pm-attempt-8-", dir="/private/tmp"))
    try:
        cases = [
            run_case(runtime, work, "missing-all-constraints-external-source", missing_all_constraints=True),
            run_case(runtime, work, "missing-idempotency-unique", missing_all_constraints=False),
        ]
    finally:
        shutil.rmtree(work)
    payload = {
        "task": "LIFEOS-P3-094 attempt-8 PM schema constraint counterexamples",
        "fixed_non_sensitive_fixtures_only": True,
        "network_used": False,
        "real_user_data_used": False,
        "cases": cases,
        "summary": {
            "pass": sum(item["pm_status"] == "PASS" for item in cases),
            "fail": sum(item["pm_status"] == "FAIL" for item in cases),
        },
        "temporary_fixture_removed": not work.exists(),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
