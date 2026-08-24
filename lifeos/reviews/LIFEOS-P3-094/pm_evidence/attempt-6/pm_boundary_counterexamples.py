#!/usr/bin/env python3
"""PM-only attempt-6 boundary checks using fixed non-sensitive fixtures."""
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
TEXT = "P3-094 PM fixed non-sensitive attempt-6 fixture"
SENTINEL = b"P3-094 PM fixed non-sensitive sentinel\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_094_pm_attempt_6", SOURCE)
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
    work = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-pm-attempt-6-", dir="/private/tmp"))
    items: list[dict] = []
    try:
        case = work / "direct-boundary"
        db = case / "capture.sqlite"
        runtime.capture(db, TEXT, "direct-boundary")
        page = case / "today.html"
        runtime.render_today(db)
        page_before = sha256(page)
        outside = work / "outside.html"
        outside.write_bytes(SENTINEL)
        outside_before = sha256(outside)
        was_rejected = rejected(lambda: runtime.render_today(db, outside), runtime.CaptureError)
        ok = was_rejected and sha256(outside) == outside_before and sha256(page) == page_before and len(runtime.list_today(db)) == 1
        items.append({"id": "PM-A6-01-render-outside-rejected", "status": "PASS" if ok else "FAIL", "outside_hash_equal": sha256(outside) == outside_before, "page_hash_equal": sha256(page) == page_before, "db_unchanged": len(runtime.list_today(db)) == 1})

        real = work / "ancestor-real"
        real_db = real / "nested" / "capture.sqlite"
        runtime.capture(real_db, TEXT, "ancestor")
        runtime.render_today(real_db)
        real_page = real / "nested" / "today.html"
        real_page_before = sha256(real_page)
        alias = work / "ancestor-alias"
        alias.symlink_to(real, target_is_directory=True)
        linked_db = alias / "nested" / "capture.sqlite"
        render_rejected = rejected(lambda: runtime.render_today(linked_db), runtime.CaptureError)
        clear_rejected = rejected(lambda: runtime.delete_all(linked_db, "DELETE"), runtime.CaptureError)
        ok = render_rejected and clear_rejected and real_page.exists() and sha256(real_page) == real_page_before and len(runtime.list_today(real_db)) == 1
        items.append({"id": "PM-A6-02-ancestor-chain-rejected", "status": "PASS" if ok else "FAIL", "render_rejected": render_rejected, "clear_rejected": clear_rejected, "page_hash_equal": real_page.exists() and sha256(real_page) == real_page_before, "db_unchanged": len(runtime.list_today(real_db)) == 1})

        empty_case = work / "empty-stale-page"
        empty_db = empty_case / "capture.sqlite"
        runtime.capture(empty_db, TEXT, "empty-stale")
        runtime.render_today(empty_db)
        empty_page = empty_case / "today.html"
        empty_before = sha256(empty_page)
        with sqlite3.connect(empty_db) as conn:
            conn.execute("DELETE FROM captures")
        render_failed = rejected(lambda: runtime.render_today(empty_db), runtime.CaptureError)
        stale_survived = empty_page.exists() and sha256(empty_page) == empty_before
        items.append({"id": "PM-A6-03-empty-db-stale-page-fail-closed", "status": "FAIL" if render_failed and stale_survived else "PASS", "render_failed": render_failed, "stale_page_exists_after": empty_page.exists(), "stale_page_hash_equal": stale_survived, "db_record_count": len(runtime.list_today(empty_db))})

        corrupt_case = work / "corrupt-stale-page"
        corrupt_db = corrupt_case / "capture.sqlite"
        runtime.capture(corrupt_db, TEXT, "corrupt-stale")
        runtime.render_today(corrupt_db)
        corrupt_page = corrupt_case / "today.html"
        corrupt_before = sha256(corrupt_page)
        corrupt_db.write_bytes(b"not a sqlite database")
        render_failed = rejected(lambda: runtime.render_today(corrupt_db), runtime.CaptureError)
        stale_survived = corrupt_page.exists() and sha256(corrupt_page) == corrupt_before
        items.append({"id": "PM-A6-04-corrupt-db-stale-page-fail-closed", "status": "FAIL" if render_failed and stale_survived else "PASS", "render_failed": render_failed, "stale_page_exists_after": corrupt_page.exists(), "stale_page_hash_equal": stale_survived})
    finally:
        shutil.rmtree(work)

    fail = sum(item["status"] == "FAIL" for item in items)
    summary = {"pass": len(items) - fail, "fail": fail, "p0": 0, "p1_findings": 1 if fail else 0, "p2": 0, "unknown": 0, "not_implemented": 0}
    payload = {"fixed_non_sensitive_fixtures_only": True, "items": items, "summary": summary, "temporary_work_cleaned": not work.exists()}
    Path(__file__).with_name("pm_boundary_counterexamples.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
