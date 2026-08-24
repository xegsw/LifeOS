#!/usr/bin/env python3
"""PM-only attempt-7 lifecycle checks with fixed non-sensitive fixtures."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path


LIFEOS = Path(__file__).resolve().parents[4]
SOURCE = LIFEOS / "engineering/LIFEOS-P3-094/src/local_capture.py"
TEXT = "P3-094 PM fixed non-sensitive attempt-7 fixture"
PAGE = b"P3-094 PM fixed non-sensitive stale page\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_094_pm_attempt_7", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejected(fn, error_type) -> bool:
    try:
        fn()
    except error_type:
        return True
    return False


def main() -> int:
    runtime = load_runtime()
    work = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-pm-attempt-7-", dir="/private/tmp"))
    items: list[dict] = []
    try:
        initialized = work / "initialized-empty"
        initialized_db = initialized / "capture.sqlite"
        runtime.capture(initialized_db, TEXT, "initialized")
        runtime.render_today(initialized_db)
        initialized_page = initialized / "today.html"
        with sqlite3.connect(initialized_db) as conn:
            conn.execute("DELETE FROM captures")
        db_before = sha256(initialized_db)
        failed = rejected(lambda: runtime.render_today(initialized_db), runtime.CaptureError)
        ok = failed and not initialized_page.exists() and sha256(initialized_db) == db_before
        items.append({"id": "PM-A7-01-initialized-empty-invalidates-stale", "status": "PASS" if ok else "FAIL", "render_failed": failed, "page_absent_after": not initialized_page.exists(), "db_hash_equal": sha256(initialized_db) == db_before})

        corrupt = work / "corrupt"
        corrupt.mkdir()
        corrupt_db = corrupt / "capture.sqlite"
        corrupt_db.write_bytes(b"fixed non-sensitive corrupt sqlite fixture")
        corrupt_page = corrupt / "today.html"
        corrupt_page.write_bytes(PAGE)
        corrupt_before = sha256(corrupt_db)
        failed = rejected(lambda: runtime.render_today(corrupt_db), runtime.CaptureError)
        ok = failed and not corrupt_page.exists() and sha256(corrupt_db) == corrupt_before
        items.append({"id": "PM-A7-02-corrupt-invalidates-stale", "status": "PASS" if ok else "FAIL", "render_failed": failed, "page_absent_after": not corrupt_page.exists(), "db_hash_equal": sha256(corrupt_db) == corrupt_before})

        missing = work / "missing-db"
        missing.mkdir()
        missing_db = missing / "capture.sqlite"
        missing_page = missing / "today.html"
        missing_page.write_bytes(PAGE)
        page_before = sha256(missing_page)
        failed = rejected(lambda: runtime.render_today(missing_db), runtime.CaptureError)
        stale_survived = missing_page.exists() and sha256(missing_page) == page_before
        items.append({"id": "PM-A7-03-missing-db-stale-page-fail-closed", "status": "FAIL" if failed and stale_survived else "PASS", "render_failed": failed, "stale_page_exists_after": missing_page.exists(), "stale_page_hash_equal": stale_survived, "db_still_missing": not missing_db.exists()})

        uninitialized = work / "uninitialized-empty"
        uninitialized.mkdir()
        uninitialized_db = uninitialized / "capture.sqlite"
        uninitialized_db.write_bytes(b"")
        uninitialized_page = uninitialized / "today.html"
        uninitialized_page.write_bytes(PAGE)
        db_before_bytes = uninitialized_db.read_bytes()
        db_before_hash = sha256(uninitialized_db)
        failed = rejected(lambda: runtime.render_today(uninitialized_db), runtime.CaptureError)
        db_changed = uninitialized_db.read_bytes() != db_before_bytes or sha256(uninitialized_db) != db_before_hash
        items.append({"id": "PM-A7-04-uninitialized-empty-db-not-mutated", "status": "FAIL" if failed and db_changed else "PASS", "render_failed": failed, "stale_page_absent_after": not uninitialized_page.exists(), "db_hash_changed": db_changed, "db_size_before": len(db_before_bytes), "db_size_after": uninitialized_db.stat().st_size})
    finally:
        shutil.rmtree(work)

    fail = sum(item["status"] == "FAIL" for item in items)
    summary = {"pass": len(items) - fail, "fail": fail, "p0": 0, "p1_findings": fail, "p2": 0, "unknown": 0, "not_implemented": 0}
    payload = {"fixed_non_sensitive_fixtures_only": True, "items": items, "summary": summary, "temporary_work_cleaned": not work.exists()}
    Path(__file__).with_name("pm_lifecycle_counterexamples.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
