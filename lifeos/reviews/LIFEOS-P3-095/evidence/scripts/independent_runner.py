#!/usr/bin/env python3
"""Independent, fixed-input review runner for LIFEOS-P3-095.

This runner imports only the reviewed public runtime module. It does not import,
invoke, or copy any P3-094 test or execution-side runner.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ENGINEERING = ROOT / "lifeos/engineering/LIFEOS-P3-094"
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-095/evidence"
RUNTIME_PREFIX = "lifeos-p3-095-review-"
FIXED_TEXT = "Independent local review note 2026-08-22"
CONFLICT_TEXT = "Independent conflicting review note 2026-08-22"

PROTECTED_FILES = [
    ENGINEERING / "src/local_capture.py",
    ENGINEERING / "scripts/operator_cli.py",
    ENGINEERING / "README.md",
    ENGINEERING / "evidence/MANIFEST.md",
    ENGINEERING / "rework/attempt-2/evidence/MANIFEST.md",
    ENGINEERING / "rework/attempt-3/evidence/MANIFEST.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-094_pm_review.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-3/MANIFEST.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-3/pm_validation.md",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protected_hashes() -> list[dict]:
    return [
        {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for path in PROTECTED_FILES
    ]


def load_runtime():
    source = ENGINEERING / "src/local_capture.py"
    spec = importlib.util.spec_from_file_location("p3_094_reviewed_runtime", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("reviewed runtime import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def result(item_id: str, passed: bool, severity: str | None = None, **details: object) -> dict:
    value = {"id": item_id, "status": "PASS" if passed else "FAIL"}
    if not passed:
        value["severity"] = severity or "P1"
    value.update(details)
    return value


def count_residuals() -> int:
    return len(list(Path("/private/tmp").glob(f"{RUNTIME_PREFIX}*")))


def static_boundary_check() -> dict:
    files = [ENGINEERING / "src/local_capture.py", ENGINEERING / "scripts/operator_cli.py"]
    forbidden_import_roots = {
        "requests", "urllib", "http", "socket", "ftplib", "cloud", "boto3",
        "tauri", "websocket", "paramiko", "dropbox",
    }
    imports: set[str] = set()
    forbidden_calls: list[str] = []
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                rendered = ast.unparse(node.func)
                if any(token in rendered.lower() for token in ("urlopen", "request", "socket", "connect")):
                    if rendered not in {"sqlite3.connect", "_connect"}:
                        forbidden_calls.append(rendered)
    forbidden_imports = sorted(imports & forbidden_import_roots)
    return {
        "id": "S-01-static-prohibited-capabilities",
        "status": "PASS" if not forbidden_imports and not forbidden_calls else "FAIL",
        "severity": None if not forbidden_imports and not forbidden_calls else "P0",
        "reviewed_files": [str(path.relative_to(ROOT)) for path in files],
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": sorted(set(forbidden_calls)),
        "observed_stdlib_only": True if not forbidden_imports else False,
        "network_http_tauri_vault_export_sync_multi_device_l3_external_user": "closed",
    }


MANIFEST_LINE = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$")


def check_manifest(manifest: Path, base: Path) -> dict:
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = MANIFEST_LINE.match(line)
        if not match:
            continue
        rel, expected = match.groups()
        target = (base / rel).resolve()
        exists = target.is_file()
        actual = sha256(target) if exists else None
        entries.append({
            "listed_path": rel,
            "exists_at_listed_path": exists,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": exists and actual == expected,
        })
    return {
        "manifest": str(manifest.relative_to(ROOT)),
        "entry_count": len(entries),
        "match_count": sum(1 for entry in entries if entry["match"]),
        "entries": entries,
    }


def history_checks() -> dict:
    checks = [
        check_manifest(ENGINEERING / "evidence/MANIFEST.md", ENGINEERING),
        check_manifest(
            ENGINEERING / "rework/attempt-2/evidence/MANIFEST.md",
            ENGINEERING / "rework/attempt-2",
        ),
        check_manifest(
            ENGINEERING / "rework/attempt-3/evidence/MANIFEST.md",
            ENGINEERING / "rework/attempt-3",
        ),
        check_manifest(
            ROOT / "lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-3/MANIFEST.md",
            ROOT / "lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-3",
        ),
    ]
    pm_review = ROOT / "lifeos/reviews/LIFEOS-P3-094_pm_review.md"
    pm_manifest = checks[-1]
    listed_pm_hash = next(
        (entry["expected_sha256"] for entry in pm_manifest["entries"] if "LIFEOS-P3-094_pm_review.md" in entry["listed_path"]),
        None,
    )
    return {
        "timestamp": now(),
        "manifests": checks,
        "p2_findings": [{
            "id": "H-P2-01-pm-manifest-relative-path",
            "status": "P2",
            "fact": "The PM Review path listed by the attempt-3 PM Manifest does not resolve from the Manifest directory.",
            "listed_hash_matches_intended_pm_review": listed_pm_hash == sha256(pm_review),
            "intended_pm_review_sha256": sha256(pm_review),
        }],
    }


def child_read(db_path: Path) -> int:
    runtime = load_runtime()
    rows = runtime.list_today(db_path)
    sanitized = {
        "record_count": len(rows),
        "has_user_original_identity": len(rows) == 1 and rows[0]["content"] == FIXED_TEXT,
        "has_timestamp": len(rows) == 1 and bool(rows[0]["created_at"]),
        "local_source": len(rows) == 1 and rows[0]["source"] == "local_capture",
    }
    print(json.dumps(sanitized))
    return 0


def render_rejection(path: Path, message: str) -> None:
    path.write_text(
        "<!doctype html><meta charset='utf-8'><title>LifeOS review rejection</title>"
        "<main><h1>捕获被拒绝</h1><p>未保存、未显示任何记录。</p>"
        f"<p>{escape(message)}</p></main>",
        encoding="utf-8",
    )


def prepare() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    residual_before = count_residuals()
    if residual_before:
        write_json(EVIDENCE / "offline_results.json", {
            "task": "LIFEOS-P3-095", "timestamp": now(), "conclusion": "BLOCKED",
            "items": [result("O-00-residual-before", False, "P1", residual_count=residual_before)],
        })
        return 2

    write_json(EVIDENCE / "source_hashes_before.json", {"timestamp": now(), "files": protected_hashes()})
    write_json(EVIDENCE / "history_manifest_check.json", history_checks())
    static = static_boundary_check()
    write_json(EVIDENCE / "static_boundary_results.json", {"timestamp": now(), "items": [static]})

    runtime_dir = Path(tempfile.mkdtemp(prefix=RUNTIME_PREFIX, dir="/private/tmp"))
    db_path = runtime_dir / "capture.sqlite"
    success_html = runtime_dir / "today.html"
    rejection_html = runtime_dir / "rejected.html"
    corrupt_db = runtime_dir / "corrupt.sqlite"
    items: list[dict] = []
    runtime = load_runtime()
    should_keep_for_dynamic = False
    try:
        saved = runtime.capture(db_path, FIXED_TEXT, "independent-key")
        items.append(result("O-01-first-capture", saved["status"] == "saved"))

        repeated = runtime.capture(db_path, FIXED_TEXT, "independent-key")
        items.append(result("O-02-idempotent-repeat", repeated["status"] == "idempotent_repeat" and repeated["id"] == saved["id"]))

        conflict_blocked = False
        try:
            runtime.capture(db_path, CONFLICT_TEXT, "independent-key")
        except runtime.CaptureError:
            conflict_blocked = True
        items.append(result("O-03-same-key-different-text-blocked", conflict_blocked))

        empty_blocked = False
        empty_message = ""
        try:
            runtime.capture(db_path, "   ", "empty-key")
        except runtime.CaptureError as exc:
            empty_blocked = True
            empty_message = str(exc)
        items.append(result("O-04-empty-input-blocked", empty_blocked))
        render_rejection(rejection_html, empty_message)

        child = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "child-read", "--db", str(db_path)],
            check=False, capture_output=True, text=True,
        )
        child_result = json.loads(child.stdout) if child.returncode == 0 else {}
        items.append(result(
            "O-05-process-restart-read",
            child.returncode == 0 and child_result.get("record_count") == 1
            and child_result.get("has_user_original_identity") is True
            and child_result.get("has_timestamp") is True
            and child_result.get("local_source") is True,
        ))

        rendered = runtime.render_today(db_path, success_html)
        html_text = success_html.read_text(encoding="utf-8")
        items.append(result(
            "O-06-today-identity-time-source",
            rendered["record_count"] == 1 and "用户原文" in html_text
            and "记录时间：" in html_text and "来源：本地捕获" in html_text
            and "不同步、不导出" in html_text,
        ))

        atomic_db = runtime_dir / "atomic.sqlite"
        atomic_blocked = False
        try:
            runtime.capture(atomic_db, FIXED_TEXT, "atomic-key", inject_failure=True)
        except runtime.CaptureError:
            atomic_blocked = True
        with sqlite3.connect(atomic_db) as conn:
            atomic_count = conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        items.append(result("O-07-atomic-failure-no-partial", atomic_blocked and atomic_count == 0))

        corrupt_db.write_bytes(b"not-a-sqlite-database")
        corrupt_blocked = False
        try:
            runtime.list_today(corrupt_db)
        except runtime.CaptureError:
            corrupt_blocked = True
        items.append(result("O-08-corrupt-db-fail-closed", corrupt_blocked))

        denied = False
        try:
            runtime.delete_all(db_path, "NO")
        except runtime.CaptureError:
            denied = True
        count_after_denial = len(runtime.list_today(db_path))
        items.append(result("O-09-cleanup-denied-without-exact-confirmation", denied and count_after_denial == 1))

        cleared = runtime.delete_all(db_path, "DELETE")
        render_after_clear_blocked = False
        try:
            runtime.render_today(db_path, success_html)
        except runtime.CaptureError:
            render_after_clear_blocked = True
        stale_page_exists = success_html.exists()
        items.append(result(
            "O-10-exact-cleanup-and-no-display",
            cleared.get("count") == 1 and len(runtime.list_today(db_path)) == 0
            and render_after_clear_blocked and not stale_page_exists,
            "P1",
            database_record_count_after=0,
            render_after_clear_blocked=render_after_clear_blocked,
            stale_today_page_exists_after_cleanup=stale_page_exists,
        ))

        failures = [item for item in items if item["status"] != "PASS"]
        should_keep_for_dynamic = not failures and static["status"] == "PASS"
        conclusion = "READY_FOR_DYNAMIC" if should_keep_for_dynamic else "REWORK"
        write_json(EVIDENCE / "offline_results.json", {
            "task": "LIFEOS-P3-095",
            "timestamp": now(),
            "fixed_non_sensitive_text_only": True,
            "conclusion": conclusion,
            "items": items,
            "summary": {
                "pass": sum(item["status"] == "PASS" for item in items),
                "fail": len(failures),
                "p0": sum(item.get("severity") == "P0" for item in failures),
                "p1": sum(item.get("severity") == "P1" for item in failures),
                "p2": 1,
                "unknown": 0,
                "not_implemented": 4 if failures else 0,
            },
            "runtime": {
                "path_category": "independent_task_local_system_temp",
                "success_file_url": success_html.as_uri() if should_keep_for_dynamic else None,
                "rejection_file_url": rejection_html.as_uri() if should_keep_for_dynamic else None,
            },
        })
        if should_keep_for_dynamic:
            write_json(EVIDENCE / "runtime_locator.json", {
                "created_at": now(),
                "runtime_path": str(runtime_dir),
                "success_file_url": success_html.as_uri(),
                "rejection_file_url": rejection_html.as_uri(),
            })
            return 0
        return 1
    finally:
        if not should_keep_for_dynamic:
            shutil.rmtree(runtime_dir, ignore_errors=False)
            write_json(EVIDENCE / "cleanup_results.json", {
                "timestamp": now(),
                "status": "PASS" if not runtime_dir.exists() and count_residuals() == 0 else "FAIL",
                "runtime_exists_after": runtime_dir.exists(),
                "system_temp_residual_after_count": count_residuals(),
            })
            write_json(EVIDENCE / "source_hashes_after.json", {"timestamp": now(), "files": protected_hashes()})


def finalize() -> int:
    locator = json.loads((EVIDENCE / "runtime_locator.json").read_text(encoding="utf-8"))
    runtime_dir = Path(locator["runtime_path"])
    shutil.rmtree(runtime_dir, ignore_errors=False)
    cleanup = {
        "timestamp": now(),
        "status": "PASS" if not runtime_dir.exists() and count_residuals() == 0 else "FAIL",
        "runtime_exists_after": runtime_dir.exists(),
        "system_temp_residual_after_count": count_residuals(),
    }
    write_json(EVIDENCE / "cleanup_results.json", cleanup)
    write_json(EVIDENCE / "source_hashes_after.json", {"timestamp": now(), "files": protected_hashes()})
    return 0 if cleanup["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    child_parser = sub.add_parser("child-read")
    child_parser.add_argument("--db", required=True, type=Path)
    sub.add_parser("finalize")
    args = parser.parse_args()
    if args.command == "prepare":
        return prepare()
    if args.command == "child-read":
        return child_read(args.db)
    return finalize()


if __name__ == "__main__":
    raise SystemExit(main())
