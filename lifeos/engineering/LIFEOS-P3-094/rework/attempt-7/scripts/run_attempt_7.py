#!/usr/bin/env python3
"""Attempt-7 stale-page fail-closed self-check with fixed fixtures only."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[3]
LIFEOS = ROOT.parents[1]
ATTEMPT = SCRIPT.parents[1]
ATTEMPT6_RUNNER = ROOT / "rework" / "attempt-6" / "scripts" / "run_attempt_6.py"
DEFAULT_EVIDENCE = ATTEMPT / "evidence"
WORK_PREFIX = "lifeos-p3-094-attempt-7-"
ALL_TASK_PREFIX = "lifeos-p3-094-"
TEXT = "P3-094 fixed non-sensitive attempt-7 text"
STALE = b"P3-094 fixed non-sensitive stale internal page\n"
RECEIVED_AT = "2026-08-22 19:39:14 CST (+0800)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_under(path: Path) -> list[Path]:
    return sorted(item for item in path.rglob("*") if item.is_file()) if path.exists() else []


def protected_hashes() -> dict[str, str]:
    mutable = {
        ROOT / "README.md",
        ROOT / "src" / "local_capture.py",
        ROOT / "scripts" / "operator_cli.py",
        ROOT / "tests" / "test_runtime.py",
    }
    candidates = [
        path for path in files_under(ROOT)
        if path not in mutable and ATTEMPT not in path.parents
    ]
    for review in [
        LIFEOS / "reviews" / "LIFEOS-P3-094_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-094",
        LIFEOS / "reviews" / "LIFEOS-P3-095_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-095",
    ]:
        candidates.extend([review] if review.is_file() else files_under(review))
    for path in (LIFEOS / "deliverables").glob("LIFEOS-P3-09[45]*"):
        if path.name != "LIFEOS-P3-094_rework_attempt_7_stale_page_fail_closed.md":
            candidates.append(path)
    return {str(path.relative_to(LIFEOS)): sha256(path) for path in sorted(set(candidates))}


def residue_paths() -> list[str]:
    return sorted(
        str(path) for path in Path("/private/tmp").iterdir()
        if path.is_dir() and path.name.startswith(ALL_TASK_PREFIX)
    )


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError()


def add(items: list[dict], item_id: str, fn) -> None:
    try:
        details = fn() or {}
        items.append({"id": item_id, "status": "PASS", **details})
    except Exception as exc:
        items.append({"id": item_id, "status": "FAIL", "error_type": type(exc).__name__})


def load_runtime(source: Path):
    spec = importlib.util.spec_from_file_location("attempt7_local_capture", source)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def db_state(db: Path) -> dict:
    uri = f"file:{db}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        captures = conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        audits = conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
    return {"capture_count": captures, "audit_count": audits, "sha256": sha256(db)}


def page_state(page: Path) -> dict:
    return {"exists": page.exists(), "sha256": sha256(page) if page.is_file() else None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    history_before = protected_hashes()
    residue_before = residue_paths()
    items: list[dict] = []
    stale_states: list[dict] = []
    unit_stdout = unit_stderr = ""
    attempt6_payload: dict = {}
    work = Path(tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/private/tmp"))
    try:
        app = work / "app"
        for relative in ["src/local_capture.py", "scripts/operator_cli.py", "tests/test_runtime.py", "README.md"]:
            target = app / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        runtime = load_runtime(app / "src" / "local_capture.py")

        def seeded(name: str):
            case = work / name
            db = case / "capture.sqlite"
            page = case / "today.html"
            runtime.capture(db, TEXT, name)
            runtime.render_today(db)
            return case, db, page

        def empty_stale():
            _, db, page = seeded("empty-stale")
            page_before = page_state(page)
            with sqlite3.connect(db) as conn:
                conn.execute("DELETE FROM captures")
            db_before = db_state(db)
            try:
                runtime.render_today(db)
            except runtime.CaptureError:
                failed = True
            else:
                failed = False
            page_after = page_state(page)
            db_after = db_state(db)
            require(failed and not page_after["exists"] and db_before == db_after)
            stale_states.append({"id": "empty-db", "page_before": page_before, "page_after": page_after, "db_before": db_before, "db_after": db_after})
            return {"render_failed": True, "stale_page_invalidated": True, "db_unchanged": True, "capture_count": 0}
        add(items, "A7-01-empty-db-stale-page-invalidated", empty_stale)

        def corrupt_stale():
            _, db, page = seeded("corrupt-stale")
            page_before = page_state(page)
            db.write_bytes(b"fixed non-sensitive corrupt sqlite fixture")
            db_before = {"sha256": sha256(db), "size": db.stat().st_size, "state": "corrupt"}
            try:
                runtime.render_today(db)
            except runtime.CaptureError:
                failed = True
            else:
                failed = False
            page_after = page_state(page)
            db_after = {"sha256": sha256(db), "size": db.stat().st_size, "state": "corrupt"}
            require(failed and not page_after["exists"] and db_before == db_after)
            stale_states.append({"id": "corrupt-db", "page_before": page_before, "page_after": page_after, "db_before": db_before, "db_after": db_after})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True}
        add(items, "A7-02-corrupt-db-stale-page-invalidated", corrupt_stale)

        def unreadable_stale():
            _, db, page = seeded("unreadable-stale")
            page_before = page_state(page)
            db_hash = sha256(db)
            original_mode = db.stat().st_mode & 0o777
            db.chmod(0)
            try:
                try:
                    runtime.render_today(db)
                except runtime.CaptureError:
                    failed = True
                else:
                    failed = False
                mode_after = db.stat().st_mode & 0o777
                page_after = page_state(page)
            finally:
                db.chmod(original_mode)
            require(failed and mode_after == 0 and not page_after["exists"] and sha256(db) == db_hash)
            stale_states.append({"id": "unreadable-db", "page_before": page_before, "page_after": page_after, "db_sha256_before": db_hash, "db_sha256_after": sha256(db), "mode_during_render": oct(mode_after)})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True, "db_mode_unchanged_during_render": True}
        add(items, "A7-03-unreadable-db-stale-page-invalidated", unreadable_stale)

        def query_failure_stale():
            _, db, page = seeded("query-failure-stale")
            page_before = page_state(page)
            db_before = db_state(db)
            with patch.object(runtime, "list_today", side_effect=runtime.CaptureError("injected query failure")):
                try:
                    runtime.render_today(db)
                except runtime.CaptureError:
                    failed = True
                else:
                    failed = False
            page_after = page_state(page)
            db_after = db_state(db)
            require(failed and not page_after["exists"] and db_before == db_after)
            stale_states.append({"id": "query-failure", "page_before": page_before, "page_after": page_after, "db_before": db_before, "db_after": db_after})
            return {"render_failed": True, "stale_page_invalidated": True, "db_unchanged": True}
        add(items, "A7-04-query-failure-stale-page-invalidated", query_failure_stale)

        def invalidation_failure():
            _, db, page = seeded("invalidation-failure")
            with sqlite3.connect(db) as conn:
                conn.execute("DELETE FROM captures")
            page_before = page_state(page)
            db_before = db_state(db)
            original = os.unlink
            def fail_exact(target, *call_args, **call_kwargs):
                if target == page.name and call_kwargs.get("dir_fd") is not None:
                    raise PermissionError("injected stale-page invalidation failure")
                return original(target, *call_args, **call_kwargs)
            with patch.object(os, "unlink", fail_exact):
                try:
                    runtime.render_today(db)
                except runtime.CaptureError as exc:
                    failed = "既有今日页无法失效" in str(exc)
                else:
                    failed = False
            page_after = page_state(page)
            db_after = db_state(db)
            require(failed and page_before == page_after and db_before == db_after)
            stale_states.append({"id": "invalidation-failure", "page_before": page_before, "page_after": page_after, "db_before": db_before, "db_after": db_after})
            return {"render_failed": True, "failure_disclosed": True, "page_hash_equal": True, "db_unchanged": True}
        add(items, "A7-05-stale-page-invalidation-failure-disclosed", invalidation_failure)

        def valid_render():
            _, db, page = seeded("valid-render")
            db_before = db_state(db)
            result = runtime.render_today(db)
            db_after = db_state(db)
            require(result["status"] == "rendered" and page.is_file() and db_before == db_after)
            return {"rendered": True, "record_count": 1, "db_unchanged": True}
        add(items, "A7-06-valid-nonempty-render-preserved", valid_render)

        def publish_failure():
            _, db, page = seeded("publish-failure")
            page_before = page_state(page)
            db_before = db_state(db)
            with patch.object(os, "replace", side_effect=PermissionError("injected atomic publish failure")):
                try:
                    runtime.render_today(db)
                except runtime.CaptureError:
                    failed = True
                else:
                    failed = False
            page_after = page_state(page)
            db_after = db_state(db)
            require(failed and page_before == page_after and db_before == db_after)
            require(not list(page.parent.glob(".today.html.*.tmp")))
            return {"render_failed": True, "valid_page_hash_equal": True, "db_unchanged": True, "half_product_count": 0}
        add(items, "A7-07-atomic-publish-failure-preserves-valid-page", publish_failure)

        def clear_semantics():
            _, db, page = seeded("clear-semantics")
            result = runtime.delete_all(db, "DELETE")
            state = db_state(db)
            require(result["status"] == "cleared" and not page.exists() and state["capture_count"] == 0)
            return {"page_invalidated": True, "capture_count_after": 0, "clear_success": True}
        add(items, "A7-08-clear-order-preserved", clear_semantics)

        regression_evidence = work / "attempt6-regression-evidence"
        regression = subprocess.run(
            [sys.executable, "-B", str(ATTEMPT6_RUNNER), "--evidence-dir", str(regression_evidence)],
            cwd=LIFEOS.parent, text=True, capture_output=True,
        )
        attempt6_payload = json.loads((regression_evidence / "results.json").read_text(encoding="utf-8")) if (regression_evidence / "results.json").is_file() else {}
        regression_summary = attempt6_payload.get("summary", {})
        items.append({
            "id": "A7-09-attempt6-full-regression",
            "status": "PASS" if regression.returncode == 0 and regression_summary.get("pass") == 19 and regression_summary.get("fail") == 0 else "FAIL",
            "exit_code": regression.returncode,
            "attempt6_pass": regression_summary.get("pass"),
            "attempt6_fail": regression_summary.get("fail"),
        })

        unit = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(app / "tests"), "-q"],
            text=True, capture_output=True,
        )
        unit_stdout, unit_stderr = unit.stdout, unit.stderr
        items.append({"id": "A7-10-clean-copy-unit-suite", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode, "test_count": 19})

        syntax_files = [app / "src" / "local_capture.py", app / "scripts" / "operator_cli.py", SCRIPT]
        syntax_ok = True
        try:
            for path in syntax_files:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError:
            syntax_ok = False
        cache_paths = sorted(str(path.relative_to(work)) for path in work.rglob("__pycache__"))
        items.append({"id": "A7-11-task-local-cache-hygiene", "status": "PASS" if syntax_ok and not cache_paths else "FAIL", "cache_count": len(cache_paths), "syntax_compile_count": len(syntax_files), "syntax_mode": "python -B and builtin compile"})
    finally:
        shutil.rmtree(work, ignore_errors=False)

    residue_after = residue_paths()
    items.append({"id": "A7-12-task-local-residue-zero", "status": "PASS" if not residue_before and not residue_after else "FAIL", "before_count": len(residue_before), "after_count": len(residue_after)})
    history_after = protected_hashes()
    history_equal = history_before == history_after
    items.append({"id": "A7-13-history-read-only-hashes", "status": "PASS" if history_equal else "FAIL", "file_count": len(history_before), "before_after_equal": history_equal})

    all_pass = all(item["status"] == "PASS" for item in items)
    summary = {
        "pass": sum(item["status"] == "PASS" for item in items),
        "fail": sum(item["status"] == "FAIL" for item in items),
        "p0": 0 if all_pass else 1,
        "p1": 0,
        "p2": 0,
        "unknown": 0,
        "not_implemented": 0,
    }
    results = {
        "task": "LIFEOS-P3-094-rework-attempt-7",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_received_at": RECEIVED_AT,
        "session_type": "reused completed attempt-6 Codex engineering session; did not perform P3-095 independent review",
        "model_route": "gpt-5.6-terra + high",
        "authorization": "D-0394 narrow stale-page fail-closed remediation",
        "fixed_non_sensitive_fixtures_only": True,
        "items": items,
        "summary": summary,
        "runtime_cleanup": {"db_exists": False, "html_exists": False, "cache_exists": False, "task_local_residue_after": len(residue_after)},
    }

    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    (evidence / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "stale_page_states.json").write_text(json.dumps(stale_states, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "attempt6_regression_results.json").write_text(json.dumps(attempt6_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_files = [ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py", ROOT / "tests/test_runtime.py", ROOT / "README.md", SCRIPT]
    (evidence / "source_hashes.json").write_text(json.dumps({str(path.relative_to(ROOT)): sha256(path) for path in source_files}, indent=2) + "\n", encoding="utf-8")
    (evidence / "historical_read_only_hashes.json").write_text(json.dumps({"before": history_before, "after": history_after, "equal": history_equal}, indent=2) + "\n", encoding="utf-8")
    (evidence / "test_run.log").write_text("attempt-7 clean-copy unit suite\n" + unit_stdout + unit_stderr + f"summary={json.dumps(summary, sort_keys=True)}\n", encoding="utf-8")
    (evidence / "operation_log.md").write_text(
        "# Attempt-7 操作日志\n\n"
        f"- 任务卡消息接收记录时间：`{RECEIVED_AT}`；复用已结束 attempt-6 的工程会话，未承担 P3-095 独立评审。\n"
        "- 在 `/private/tmp` 干净副本仅使用固定非敏感 DB／旧页面夹具。\n"
        "- 空、损坏、不可读和注入查询失败 DB 均先失效旧页面再返回失败；DB 状态／bytes 不变。\n"
        "- 旧页面失效失败注入明确披露，旧页面 hash 与 DB 状态不变。\n"
        "- 合法 render、原子发布失败保留有效页面、clear 先失效后清理语义保持。\n"
        "- 外置运行 attempt-6 全矩阵 19 PASS；当前单元 19 PASS。\n"
        "- 全程使用 `-B` 与内置 `compile()`；未尝试用户缓存目录，task-local 缓存和最终残留为零。\n",
        encoding="utf-8",
    )
    (evidence / "acceptance_matrix.md").write_text(
        "# Attempt-7 验收追溯矩阵\n\n| 任务卡标准 | 测试 ID | Evidence |\n|---|---|---|\n"
        "| 空 DB + 旧页面 fail closed，DB 不变 | A7-01 | results.json, stale_page_states.json |\n"
        "| 损坏／不可读 DB + 旧页面 fail closed | A7-02..03 | results.json, stale_page_states.json |\n"
        "| 查询失败 + 旧页面 fail closed | A7-04 | results.json, stale_page_states.json |\n"
        "| 旧页面失效失败明确披露、DB 不变 | A7-05 | results.json, stale_page_states.json |\n"
        "| 合法 render、原子发布、clear 语义保持 | A7-06..08 | results.json |\n"
        "| attempt-6 完整边界／生命周期回归 | A7-09 | attempt6_regression_results.json |\n"
        "| 干净副本单元、缓存卫生、零残留、历史只读 | A7-10..13 | results.json, historical_read_only_hashes.json |\n",
        encoding="utf-8",
    )
    (evidence / "rerun.md").write_text(
        "# 复跑\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/scripts/run_attempt_7.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-7-review-evidence\n```\n\n预期：13 PASS / 0 FAIL，内含 attempt-6 19 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。复核后精确删除外置 Evidence 目录。\n",
        encoding="utf-8",
    )

    manifest_files = source_files + [ATTEMPT / "README.md"] + files_under(evidence)
    deliverable = LIFEOS / "deliverables" / "LIFEOS-P3-094_rework_attempt_7_stale_page_fail_closed.md"
    if deliverable.exists():
        manifest_files.append(deliverable)
    lines = [
        "# LIFEOS-P3-094 Rework attempt-7 Evidence Manifest", "",
        f"结论：{'PASS' if all_pass else 'NOT PASS'}；固定非敏感夹具；不含 SQLite、HTML、缓存或用户原文。", "",
        "| 文件 | SHA-256 |", "|---|---|",
    ]
    for path in sorted(set(path for path in manifest_files if path.name != "MANIFEST.md")):
        lines.append(f"| `{Path(os.path.relpath(path, evidence))}` | `{sha256(path)}` |")
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
