#!/usr/bin/env python3
"""PM-only attempt-5 boundary counterexamples with fixed non-sensitive fixtures."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "engineering/LIFEOS-P3-094/src/local_capture.py"
CLI = ROOT / "engineering/LIFEOS-P3-094/scripts/operator_cli.py"
FIXED_TEXT = "P3-094 PM fixed non-sensitive attempt-5 fixture"
SENTINEL = b"P3-094 PM fixed non-sensitive sentinel\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_094_pm_attempt_5", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runtime = load_runtime()
    work = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-pm-attempt-5-", dir="/private/tmp"))
    results: list[dict] = []
    try:
        app = work / "app"
        db = app / "capture.sqlite"
        runtime.capture(db, FIXED_TEXT, "render-boundary")

        outside = work / "outside"
        outside.mkdir()
        api_sentinel = outside / "api-sentinel.html"
        api_sentinel.write_bytes(SENTINEL)
        api_before = sha256(api_sentinel)
        api_result = runtime.render_today(db, api_sentinel)
        api_after = sha256(api_sentinel)
        results.append({
            "id": "PM-A5-CE-01-render-api-outside-task-local",
            "expected": "reject before file change",
            "observed_status": api_result.get("status"),
            "outside_file_hash_changed": api_before != api_after,
            "db_record_count": len(runtime.list_today(db)),
            "status": "FAIL" if api_result.get("status") == "rendered" and api_before != api_after else "PASS",
        })

        cli_sentinel = outside / "cli-sentinel.html"
        cli_sentinel.write_bytes(SENTINEL)
        cli_before = sha256(cli_sentinel)
        completed = subprocess.run(
            [sys.executable, "-B", str(CLI), "--db", str(db), "render", "--output", str(cli_sentinel)],
            text=True,
            capture_output=True,
        )
        cli_after = sha256(cli_sentinel)
        results.append({
            "id": "PM-A5-CE-02-render-cli-outside-task-local",
            "expected": "reject before file change",
            "observed_exit": completed.returncode,
            "outside_file_hash_changed": cli_before != cli_after,
            "db_record_count": len(runtime.list_today(db)),
            "status": "FAIL" if completed.returncode == 0 and cli_before != cli_after else "PASS",
        })

        symlink_target = outside / "symlink-target.html"
        symlink_target.write_bytes(SENTINEL)
        symlink_before = sha256(symlink_target)
        render_link = app / "render-link.html"
        render_link.symlink_to(symlink_target)
        link_result = runtime.render_today(db, render_link)
        symlink_after = sha256(symlink_target)
        results.append({
            "id": "PM-A5-CE-03-render-follows-file-symlink",
            "expected": "reject before target change",
            "observed_status": link_result.get("status"),
            "target_hash_changed": symlink_before != symlink_after,
            "link_preserved": render_link.is_symlink(),
            "db_record_count": len(runtime.list_today(db)),
            "status": "FAIL" if link_result.get("status") == "rendered" and symlink_before != symlink_after else "PASS",
        })

        real_root = work / "real-root"
        real_task = real_root / "task"
        real_db = real_task / "capture.sqlite"
        runtime.capture(real_db, FIXED_TEXT, "ancestor-link")
        real_page = real_task / "today.html"
        runtime.render_today(real_db, real_page)
        alias = work / "alias-root"
        alias.symlink_to(real_root, target_is_directory=True)
        linked_db = alias / "task" / "capture.sqlite"
        clear_result = runtime.delete_all(linked_db, "DELETE")
        results.append({
            "id": "PM-A5-CE-04-clear-ancestor-directory-symlink-chain",
            "expected": "reject before page or DB change",
            "observed_status": clear_result.get("status"),
            "real_page_exists_after": real_page.exists(),
            "real_db_record_count_after": len(runtime.list_today(real_db)),
            "status": "FAIL" if clear_result.get("status") == "cleared" and not real_page.exists() and len(runtime.list_today(real_db)) == 0 else "PASS",
        })
    finally:
        shutil.rmtree(work)

    summary = {
        "pass": sum(item["status"] == "PASS" for item in results),
        "fail": sum(item["status"] == "FAIL" for item in results),
        "p0_findings": 2 if any(item["id"].startswith("PM-A5-CE-0") and item["status"] == "FAIL" for item in results) else 0,
        "p1": 0,
        "p2": 0,
        "unknown": 0,
        "not_implemented": 0,
    }
    payload = {"fixed_non_sensitive_fixtures_only": True, "items": results, "summary": summary, "temporary_work_cleaned": not work.exists()}
    output = Path(__file__).with_name("pm_boundary_counterexamples.json")
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if summary["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
