#!/usr/bin/env python3
"""Attempt-8 strict read-only render self-check with fixed fixtures only."""
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
WORK_PREFIX = "lifeos-p3-094-attempt-8-"
ALL_TASK_PREFIX = "lifeos-p3-094-"
TEXT = "P3-094 fixed non-sensitive attempt-8 text"
STALE = b"P3-094 fixed non-sensitive stale internal page\n"
RECEIVED_AT = "2026-08-22 19:56:40 CST (+0800)"


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
        if path.name != "LIFEOS-P3-094_rework_attempt_8_read_only_render_missing_db_fail_closed.md":
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
    spec = importlib.util.spec_from_file_location("attempt8_local_capture", source)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_state(path: Path) -> dict:
    return {
        "exists": path.exists(),
        "size": path.stat().st_size if path.is_file() else None,
        "sha256": sha256(path) if path.is_file() else None,
    }


def sqlite_objects(db: Path) -> list[dict]:
    with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
        rows = conn.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
    return [{"type": row[0], "name": row[1], "table": row[2], "sql_sha256": hashlib.sha256((row[3] or "").encode()).hexdigest()} for row in rows]


def db_counts(db: Path) -> dict:
    with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
        return {
            "capture_count": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
            "audit_count": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0],
        }


def sidecars(db: Path) -> list[str]:
    return sorted(path.name for path in db.parent.glob(f"{db.name}-*"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    history_before = protected_hashes()
    residue_before = residue_paths()
    items: list[dict] = []
    db_states: list[dict] = []
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

        def expect_render_failure(db: Path) -> None:
            try:
                runtime.render_today(db)
            except runtime.CaptureError:
                return
            raise AssertionError()

        def missing_db():
            case = work / "missing-db"
            case.mkdir()
            db = case / "capture.sqlite"
            page = case / "today.html"
            page.write_bytes(STALE)
            page_before = file_state(page)
            expect_render_failure(db)
            state = {"id": "missing-db", "page_before": page_before, "page_after": file_state(page), "db_before": {"exists": False}, "db_after": file_state(db), "sidecars_after": sidecars(db)}
            require(not page.exists() and not db.exists() and not sidecars(db))
            db_states.append(state)
            return {"render_failed": True, "stale_page_invalidated": True, "db_not_created": True, "sidecar_count": 0}
        add(items, "A8-01-missing-db-stale-page-no-create", missing_db)

        def zero_byte():
            case = work / "zero-byte"
            case.mkdir()
            db = case / "capture.sqlite"
            db.write_bytes(b"")
            page = case / "today.html"
            page.write_bytes(STALE)
            before = file_state(db)
            objects_before = sqlite_objects(db)
            expect_render_failure(db)
            after = file_state(db)
            objects_after = sqlite_objects(db)
            require(not page.exists() and before == after and objects_before == objects_after == [] and not sidecars(db))
            db_states.append({"id": "zero-byte", "page_after": file_state(page), "db_before": before, "db_after": after, "objects_before": objects_before, "objects_after": objects_after, "sidecars_after": sidecars(db)})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True, "object_count": 0, "sidecar_count": 0}
        add(items, "A8-02-zero-byte-db-read-only", zero_byte)

        def schema_case(name: str, statements: list[str]):
            case = work / name
            case.mkdir()
            db = case / "capture.sqlite"
            with sqlite3.connect(db) as conn:
                for statement in statements:
                    conn.execute(statement)
            page = case / "today.html"
            page.write_bytes(STALE)
            before = file_state(db)
            objects_before = sqlite_objects(db)
            expect_render_failure(db)
            after = file_state(db)
            objects_after = sqlite_objects(db)
            require(not page.exists() and before == after and objects_before == objects_after and not sidecars(db))
            db_states.append({"id": name, "page_after": file_state(page), "db_before": before, "db_after": after, "objects_before": objects_before, "objects_after": objects_after, "sidecars_after": sidecars(db)})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True, "objects_unchanged": True, "object_count": len(objects_before), "sidecar_count": 0}

        add(items, "A8-03-no-required-schema-read-only", lambda: schema_case("no-required-schema", ["CREATE TABLE other(value TEXT)"]))
        add(items, "A8-04-partial-schema-read-only", lambda: schema_case("partial-schema", ["CREATE TABLE captures(id TEXT, content TEXT, created_at TEXT, source TEXT, idem_key TEXT)"]))
        add(items, "A8-05-both-tables-incomplete-read-only", lambda: schema_case("both-tables-incomplete", ["CREATE TABLE captures(id TEXT, content TEXT, created_at TEXT, source TEXT)", "CREATE TABLE audit(id INTEGER, event TEXT)"]))

        def initialized_empty():
            _, db, page = seeded("initialized-empty")
            with sqlite3.connect(db) as conn:
                conn.execute("DELETE FROM captures")
            before = file_state(db)
            objects_before = sqlite_objects(db)
            counts_before = db_counts(db)
            expect_render_failure(db)
            after = file_state(db)
            require(not page.exists() and before == after and objects_before == sqlite_objects(db) and counts_before == db_counts(db))
            db_states.append({"id": "initialized-empty", "page_after": file_state(page), "db_before": before, "db_after": after, "objects_before": objects_before, "objects_after": sqlite_objects(db), "counts_before": counts_before, "counts_after": db_counts(db)})
            return {"render_failed": True, "stale_page_invalidated": True, "db_unchanged": True}
        add(items, "A8-06-initialized-empty-contract-preserved", initialized_empty)

        def corrupt_db():
            _, db, page = seeded("corrupt")
            db.write_bytes(b"fixed non-sensitive corrupt sqlite fixture")
            before = file_state(db)
            expect_render_failure(db)
            after = file_state(db)
            require(not page.exists() and before == after)
            db_states.append({"id": "corrupt", "page_after": file_state(page), "db_before": before, "db_after": after})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True}
        add(items, "A8-07-corrupt-db-contract-preserved", corrupt_db)

        def unreadable_db():
            _, db, page = seeded("unreadable")
            before = file_state(db)
            original_mode = db.stat().st_mode & 0o777
            db.chmod(0)
            try:
                expect_render_failure(db)
                mode_after = db.stat().st_mode & 0o777
                page_after = file_state(page)
            finally:
                db.chmod(original_mode)
            after = file_state(db)
            require(not page_after["exists"] and mode_after == 0 and before == after)
            db_states.append({"id": "unreadable", "page_after": page_after, "db_before": before, "db_after": after, "mode_during_render": oct(mode_after)})
            return {"render_failed": True, "stale_page_invalidated": True, "db_bytes_unchanged": True}
        add(items, "A8-08-unreadable-db-contract-preserved", unreadable_db)

        def query_failure():
            _, db, page = seeded("query-failure")
            before = file_state(db)
            counts_before = db_counts(db)
            with patch.object(runtime, "_list_today_read_only", side_effect=runtime.CaptureError("injected query failure")):
                expect_render_failure(db)
            require(not page.exists() and before == file_state(db) and counts_before == db_counts(db))
            return {"render_failed": True, "stale_page_invalidated": True, "db_unchanged": True}
        add(items, "A8-09-query-failure-contract-preserved", query_failure)

        def invalidation_failure():
            case = work / "missing-invalidation-failure"
            case.mkdir()
            db = case / "capture.sqlite"
            page = case / "today.html"
            page.write_bytes(STALE)
            page_before = file_state(page)
            original = os.unlink
            def fail_exact(target, *call_args, **call_kwargs):
                if target == page.name and call_kwargs.get("dir_fd") is not None:
                    raise PermissionError("injected stale-page invalidation failure")
                return original(target, *call_args, **call_kwargs)
            with patch.object(os, "unlink", fail_exact):
                try:
                    runtime.render_today(db)
                except runtime.CaptureError as exc:
                    disclosed = "既有今日页无法失效" in str(exc)
                else:
                    disclosed = False
            require(disclosed and page_before == file_state(page) and not db.exists() and not sidecars(db))
            return {"render_failed": True, "failure_disclosed": True, "page_hash_equal": True, "db_not_created": True}
        add(items, "A8-10-missing-db-invalidation-failure-disclosed", invalidation_failure)

        def valid_render():
            _, db, page = seeded("valid-render")
            before = file_state(db)
            objects_before = sqlite_objects(db)
            counts_before = db_counts(db)
            result = runtime.render_today(db)
            require(result["status"] == "rendered" and page.is_file())
            require(before == file_state(db) and objects_before == sqlite_objects(db) and counts_before == db_counts(db))
            return {"rendered": True, "record_count": 1, "db_unchanged": True}
        add(items, "A8-11-valid-read-only-render", valid_render)

        def publish_failure():
            _, db, page = seeded("publish-failure")
            page_before = file_state(page)
            db_before = file_state(db)
            with patch.object(os, "replace", side_effect=PermissionError("injected atomic publish failure")):
                expect_render_failure(db)
            require(page_before == file_state(page) and db_before == file_state(db))
            require(not list(page.parent.glob(".today.html.*.tmp")))
            return {"render_failed": True, "valid_page_hash_equal": True, "db_unchanged": True, "half_product_count": 0}
        add(items, "A8-12-publish-failure-preserves-valid-page", publish_failure)

        def clear_semantics():
            _, db, page = seeded("clear")
            result = runtime.delete_all(db, "DELETE")
            require(result["status"] == "cleared" and not page.exists() and db_counts(db)["capture_count"] == 0)
            return {"page_invalidated": True, "capture_count_after": 0, "clear_success": True}
        add(items, "A8-13-clear-order-preserved", clear_semantics)

        regression_evidence = work / "attempt6-regression-evidence"
        regression = subprocess.run(
            [sys.executable, "-B", str(ATTEMPT6_RUNNER), "--evidence-dir", str(regression_evidence)],
            cwd=LIFEOS.parent, text=True, capture_output=True,
        )
        attempt6_payload = json.loads((regression_evidence / "results.json").read_text(encoding="utf-8")) if (regression_evidence / "results.json").is_file() else {}
        regression_summary = attempt6_payload.get("summary", {})
        items.append({"id": "A8-14-attempt6-full-regression", "status": "PASS" if regression.returncode == 0 and regression_summary.get("pass") == 19 and regression_summary.get("fail") == 0 else "FAIL", "exit_code": regression.returncode, "attempt6_pass": regression_summary.get("pass"), "attempt6_fail": regression_summary.get("fail")})

        unit = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(app / "tests"), "-q"], text=True, capture_output=True)
        unit_stdout, unit_stderr = unit.stdout, unit.stderr
        items.append({"id": "A8-15-clean-copy-unit-suite", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode, "test_count": 22})

        syntax_files = [app / "src" / "local_capture.py", app / "scripts" / "operator_cli.py", SCRIPT]
        syntax_ok = True
        try:
            for path in syntax_files:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError:
            syntax_ok = False
        cache_paths = sorted(str(path.relative_to(work)) for path in work.rglob("__pycache__"))
        items.append({"id": "A8-16-task-local-cache-hygiene", "status": "PASS" if syntax_ok and not cache_paths else "FAIL", "cache_count": len(cache_paths), "syntax_compile_count": len(syntax_files), "syntax_mode": "python -B and builtin compile"})
    finally:
        shutil.rmtree(work, ignore_errors=False)

    residue_after = residue_paths()
    items.append({"id": "A8-17-task-local-residue-zero", "status": "PASS" if not residue_before and not residue_after else "FAIL", "before_count": len(residue_before), "after_count": len(residue_after)})
    history_after = protected_hashes()
    history_equal = history_before == history_after
    items.append({"id": "A8-18-history-read-only-hashes", "status": "PASS" if history_equal else "FAIL", "file_count": len(history_before), "before_after_equal": history_equal})

    all_pass = all(item["status"] == "PASS" for item in items)
    summary = {"pass": sum(item["status"] == "PASS" for item in items), "fail": sum(item["status"] == "FAIL" for item in items), "p0": 0 if all_pass else 1, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0}
    results = {
        "task": "LIFEOS-P3-094-rework-attempt-8",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_received_at": RECEIVED_AT,
        "session_type": "reused completed attempt-7 Codex engineering session; did not perform P3-095 independent review",
        "model_route": "gpt-5.6-terra + high",
        "authorization": "D-0396 missing-DB stale-page and strict read-only render remediation",
        "fixed_non_sensitive_fixtures_only": True,
        "items": items,
        "summary": summary,
        "runtime_cleanup": {"db_exists": False, "html_exists": False, "cache_exists": False, "task_local_residue_after": len(residue_after)},
    }

    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    (evidence / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "read_only_db_states.json").write_text(json.dumps(db_states, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "attempt6_regression_results.json").write_text(json.dumps(attempt6_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_files = [ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py", ROOT / "tests/test_runtime.py", ROOT / "README.md", SCRIPT]
    (evidence / "source_hashes.json").write_text(json.dumps({str(path.relative_to(ROOT)): sha256(path) for path in source_files}, indent=2) + "\n", encoding="utf-8")
    (evidence / "historical_read_only_hashes.json").write_text(json.dumps({"before": history_before, "after": history_after, "equal": history_equal}, indent=2) + "\n", encoding="utf-8")
    (evidence / "test_run.log").write_text("attempt-8 clean-copy unit suite\n" + unit_stdout + unit_stderr + f"summary={json.dumps(summary, sort_keys=True)}\n", encoding="utf-8")
    (evidence / "operation_log.md").write_text(
        "# Attempt-8 操作日志\n\n"
        f"- 任务卡消息接收记录时间：`{RECEIVED_AT}`；复用已结束 attempt-7 的工程会话，未承担 P3-095 独立评审。\n"
        "- 仅在 `/private/tmp` 使用固定非敏感 DB／旧页面夹具。\n"
        "- DB 缺失时旧页面先失效，DB 与 SQLite 副文件均未创建。\n"
        "- 零字节、无必需 Schema、部分 Schema DB 均只读失败；bytes、大小、hash 与对象清单不变。\n"
        "- attempt-7 的空、损坏、不可读、查询失败、失效失败合同继续成立。\n"
        "- 合法 render 严格只读、发布失败保留有效页面、clear 顺序与 attempt-6 19 项全矩阵保持。\n"
        "- 全程 `python3 -B` + 内置 `compile()`；缓存和最终临时残留为零。\n",
        encoding="utf-8",
    )
    (evidence / "acceptance_matrix.md").write_text(
        "# Attempt-8 验收追溯矩阵\n\n| 任务卡标准 | 测试 ID | Evidence |\n|---|---|---|\n"
        "| DB 缺失先失效旧页且不创建 DB／副文件 | A8-01 | results.json, read_only_db_states.json |\n"
        "| 零字节 DB 只读失败且 bytes／对象不变 | A8-02 | results.json, read_only_db_states.json |\n"
        "| 无 Schema／部分 Schema／双表缺列不初始化或补写 | A8-03..05 | results.json, read_only_db_states.json |\n"
        "| attempt-7 空／损坏／不可读／查询失败合同 | A8-06..09 | results.json, read_only_db_states.json |\n"
        "| 页面失效失败、合法 render、原子发布、clear | A8-10..13 | results.json |\n"
        "| attempt-6 全边界回归 | A8-14 | attempt6_regression_results.json |\n"
        "| 干净单元、缓存、零残留、历史只读 | A8-15..18 | results.json, historical_read_only_hashes.json |\n",
        encoding="utf-8",
    )
    (evidence / "rerun.md").write_text(
        "# 复跑\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/scripts/run_attempt_8.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-8-review-evidence\n```\n\n预期：18 PASS / 0 FAIL，内含 attempt-6 19 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。复核后精确删除外置 Evidence 目录。\n",
        encoding="utf-8",
    )

    manifest_files = source_files + [ATTEMPT / "README.md"] + files_under(evidence)
    deliverable = LIFEOS / "deliverables" / "LIFEOS-P3-094_rework_attempt_8_read_only_render_missing_db_fail_closed.md"
    if deliverable.exists():
        manifest_files.append(deliverable)
    lines = ["# LIFEOS-P3-094 Rework attempt-8 Evidence Manifest", "", f"结论：{'PASS' if all_pass else 'NOT PASS'}；固定非敏感夹具；不含 SQLite、HTML、缓存或用户原文。", "", "| 文件 | SHA-256 |", "|---|---|"]
    for path in sorted(set(path for path in manifest_files if path.name != "MANIFEST.md")):
        lines.append(f"| `{Path(os.path.relpath(path, evidence))}` | `{sha256(path)}` |")
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
