#!/usr/bin/env python3
"""PM-only fixed-fixture counterexamples for P3-094 final invariant closure."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch


TEXT = "P3-094 PM fixed non-sensitive final closure fixture"
STALE = b"P3-094 PM fixed non-sensitive stale page\n"


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_runtime(path: Path):
    spec = importlib.util.spec_from_file_location("p3_094_pm_final", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime load failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def db_counts(db: Path) -> dict:
    if not db.is_file():
        return {"captures": None, "audit": None}
    with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
        return {
            "captures": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
            "audit": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0],
        }


def call_capture(runtime, db: Path, text: str, key: str) -> str:
    try:
        runtime.capture(db, text, key)
    except runtime.CaptureError:
        return "CaptureError"
    return "success"


def post_commit_cleanup_existing(runtime, root: Path) -> dict:
    case = root / "post-commit-existing"
    case.mkdir()
    db = case / "capture.sqlite"
    page = case / "today.html"
    runtime.capture(db, TEXT, "one")
    runtime.render_today(db)
    before = {"db_hash": sha256(db), "counts": db_counts(db), "page_hash": sha256(page)}
    original_unlink = os.unlink

    def fail_staged(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".today.html.") and name.endswith(".stale"):
            raise PermissionError("fixed injected persistent stale cleanup failure")
        return original_unlink(name, *args, **kwargs)

    with patch.object(runtime.os, "unlink", fail_staged):
        outcome = call_capture(runtime, db, TEXT + " second", "two")
    after = {
        "db_hash": sha256(db),
        "counts": db_counts(db),
        "page_exists": page.exists(),
        "staged_count": len(list(case.glob(".today.html.*.stale"))),
    }
    held = outcome == "CaptureError" and before["db_hash"] == after["db_hash"] and before["counts"] == after["counts"] and page.is_file() and after["staged_count"] == 0
    return {"id": "PM-A9-01-existing-capture-post-commit-cleanup", "expected": "reported failure leaves DB/page unchanged and no staging residue", "outcome": outcome, "before": before, "after": after, "pm_status": "PASS" if held else "FAIL"}


def post_publish_cleanup_new(runtime, root: Path) -> dict:
    case = root / "post-publish-new"
    case.mkdir()
    db = case / "capture.sqlite"
    page = case / "today.html"
    page.write_bytes(STALE)
    before = {"db_exists": False, "page_hash": sha256(page)}
    original_unlink = os.unlink

    def fail_staged(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".today.html.") and name.endswith(".stale"):
            raise PermissionError("fixed injected persistent stale cleanup failure")
        return original_unlink(name, *args, **kwargs)

    with patch.object(runtime.os, "unlink", fail_staged):
        outcome = call_capture(runtime, db, TEXT, "one")
    after = {
        "db_exists": db.exists(),
        "db_hash": sha256(db),
        "counts": db_counts(db),
        "page_hash": sha256(page),
        "staged_count": len(list(case.glob(".today.html.*.stale"))),
    }
    held = outcome == "CaptureError" and not db.exists() and before["page_hash"] == after["page_hash"] and after["staged_count"] == 0
    return {"id": "PM-A9-02-new-capture-post-publish-cleanup", "expected": "reported initialization failure leaves no DB and restores page", "outcome": outcome, "before": before, "after": after, "pm_status": "PASS" if held else "FAIL"}


def audit_semantics(runtime, root: Path) -> list[dict]:
    cases = []

    case = root / "future-saved-audit"
    case.mkdir()
    db = case / "capture.sqlite"
    page = case / "today.html"
    runtime.capture(db, TEXT, "one")
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE audit SET created_at='2099-01-01T00:00:00+00:00' WHERE event='capture_saved'")
    page.write_bytes(STALE)
    db_hash = sha256(db)
    try:
        records = runtime.list_today(db)
        list_outcome = "accepted"
    except runtime.CaptureError:
        records = []
        list_outcome = "rejected"
    try:
        runtime.render_today(db)
        render_outcome = "accepted"
    except runtime.CaptureError:
        render_outcome = "rejected"
    held = list_outcome == "rejected" and render_outcome == "rejected" and not page.exists() and sha256(db) == db_hash
    cases.append({"id": "PM-A9-03-future-capture-saved-audit", "expected": "forged future audit is rejected as semantically inconsistent", "list_outcome": list_outcome, "render_outcome": render_outcome, "record_count_if_accepted": len(records), "page_exists": page.exists(), "db_unchanged": sha256(db) == db_hash, "pm_status": "PASS" if held else "FAIL"})

    case = root / "repeat-before-save"
    case.mkdir()
    db = case / "capture.sqlite"
    runtime.capture(db, TEXT, "one")
    with sqlite3.connect(db) as conn:
        capture_id = conn.execute("SELECT id FROM captures").fetchone()[0]
        conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_repeat',?,'2000-01-01T00:00:00+00:00','same_idempotency_key')", (capture_id,))
    try:
        runtime.list_today(db)
        outcome = "accepted"
    except runtime.CaptureError:
        outcome = "rejected"
    cases.append({"id": "PM-A9-04-repeat-before-save-audit", "expected": "repeat audit earlier than saved capture is rejected", "outcome": outcome, "pm_status": "PASS" if outcome == "rejected" else "FAIL"})

    case = root / "clear-count"
    case.mkdir()
    db = case / "capture.sqlite"
    runtime.capture(db, TEXT, "one")
    runtime.delete_all(db, "DELETE")
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE audit SET detail='count=999;today_view=invalidated' WHERE event='captures_cleared'")
    try:
        runtime.safe_snapshot(db)
        outcome = "accepted"
    except runtime.CaptureError:
        outcome = "rejected"
    cases.append({"id": "PM-A9-05-clear-count-semantic-mismatch", "expected": "forged clear count is rejected", "outcome": outcome, "pm_status": "PASS" if outcome == "rejected" else "FAIL"})
    return cases


def coverage_claims(test_source: Path) -> dict:
    text = test_source.read_text(encoding="utf-8")
    checks = {
        "source_case_empty_null_blob_independently_executed": all(token in text for token in ("source-case", "source-empty", "source-null", "source-blob")),
        "duplicate_id_and_idem_independently_executed": "duplicate-id" in text and "duplicate-idem" in text,
        "capture_commit_failure_injected": "capture-commit-failure" in text,
        "capture_post_commit_cleanup_failure_injected": "post-commit-cleanup" in text,
        "clear_commit_failure_injected": "clear-commit-failure" in text,
    }
    return {
        "id": "PM-A9-06-evidence-row-execution-coverage",
        "expected": "each claimed mandatory mutation/failure row has an independently executed fixture",
        "checks": checks,
        "pm_status": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = load_runtime(args.source.resolve())
    work = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-pm-attempt-9-", dir="/private/tmp"))
    try:
        cases = [post_commit_cleanup_existing(runtime, work), post_publish_cleanup_new(runtime, work)]
        cases.extend(audit_semantics(runtime, work))
        cases.append(coverage_claims(args.tests.resolve()))
    finally:
        shutil.rmtree(work)
    payload = {
        "task": "LIFEOS-P3-094 final invariant closure PM counterexamples",
        "fixed_non_sensitive_fixtures_only": True,
        "network_used": False,
        "real_user_data_used": False,
        "cases": cases,
        "summary": {"pass": sum(item["pm_status"] == "PASS" for item in cases), "fail": sum(item["pm_status"] == "FAIL" for item in cases)},
        "temporary_fixture_removed": not work.exists(),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
