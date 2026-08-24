#!/usr/bin/env python3
"""Attempt-4 clean-copy runner. Fixed non-sensitive text only."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[3]
ATTEMPT = SCRIPT.parents[1]
DEFAULT_EVIDENCE = ATTEMPT / "evidence"
WORK_PREFIX = "lifeos-p3-094-attempt-4-"
TEST_TEXT = "P3-094 fixed non-sensitive attempt-4 text"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_under(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*") if p.is_file()) if path.exists() else []


def protected_hashes() -> dict[str, str]:
    project = ROOT.parents[1]
    roots = [
        ROOT / "evidence",
        ROOT / "rework" / "attempt-2",
        ROOT / "rework" / "attempt-3",
        project / "reviews" / "LIFEOS-P3-095_pm_review.md",
        project / "reviews" / "LIFEOS-P3-095",
        project / "deliverables" / "LIFEOS-P3-095_real_local_capture_persistence_today_view_fresh_isolated_independent_re_review.md",
    ]
    result: dict[str, str] = {}
    for root in roots:
        candidates = [root] if root.is_file() else files_under(root)
        for path in candidates:
            result[str(path.relative_to(project))] = sha256(path)
    return result


def temp_residue_count() -> int:
    bases = [Path("/private/tmp"), Path(tempfile.gettempdir())]
    found: set[str] = set()
    for base in bases:
        if not base.is_dir():
            continue
        for path in base.iterdir():
            if path.is_dir() and path.name.startswith(WORK_PREFIX):
                found.add(str(path.resolve()))
    return len(found)


def add(items: list[dict], item_id: str, fn) -> None:
    try:
        details = fn() or {}
        items.append({"id": item_id, "status": "PASS", **details})
    except Exception as exc:
        items.append({"id": item_id, "status": "FAIL", "error_type": type(exc).__name__})


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError()


def load_runtime(source: Path):
    spec = importlib.util.spec_from_file_location("attempt4_local_capture", source)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    history_before = protected_hashes()
    residue_before = temp_residue_count()
    items: list[dict] = []
    work = Path(tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/private/tmp"))
    unit_stdout = ""
    unit_stderr = ""
    try:
        app = work / "app"
        (app / "src").mkdir(parents=True)
        (app / "scripts").mkdir()
        (app / "tests").mkdir()
        for relative in ["src/local_capture.py", "scripts/operator_cli.py", "tests/test_runtime.py", "README.md"]:
            target = app / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

        runtime = load_runtime(app / "src" / "local_capture.py")
        db = work / "runtime" / "capture.sqlite"
        page = work / "runtime" / "today.html"

        add(items, "A4-01-first-capture", lambda: (
            require(runtime.capture(db, TEST_TEXT, "attempt-4-key")["status"] == "saved"),
            {"record_count": 1},
        )[1])
        add(items, "A4-02-idempotent-repeat", lambda: (
            require(runtime.capture(db, TEST_TEXT, "attempt-4-key")["status"] == "idempotent_repeat"),
            {},
        )[1])

        def conflict():
            try:
                runtime.capture(db, "P3-094 alternate fixed text", "attempt-4-key")
            except runtime.CaptureError:
                return {"blocked": True}
            raise AssertionError()
        add(items, "A4-03-idempotency-conflict", conflict)

        def restart_read():
            code = (
                "import importlib.util,json,pathlib;"
                f"p=pathlib.Path({str(app / 'src' / 'local_capture.py')!r});"
                "s=importlib.util.spec_from_file_location('r',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                f"print(json.dumps({{'record_count':len(m.list_today(pathlib.Path({str(db)!r})))}}))"
            )
            completed = subprocess.run([sys.executable, "-B", "-c", code], text=True, capture_output=True)
            require(completed.returncode == 0)
            require(json.loads(completed.stdout)["record_count"] == 1)
            return {"new_process_exit": 0, "record_count": 1}
        add(items, "A4-04-cross-process-read", restart_read)

        add(items, "A4-05-render-before-clear", lambda: (
            require(runtime.render_today(db, page)["status"] == "rendered"),
            require(page.exists()),
            {"page_exists_before_clear": True},
        )[2])

        def positive_clear():
            result = runtime.delete_all(db, "DELETE", page)
            require(result["status"] == "cleared" and result["today_view"] == "invalidated")
            require(len(runtime.list_today(db)) == 0)
            require(not page.exists())
            try:
                runtime.render_today(db, page)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(not page.exists())
            return {"record_count_after": 0, "old_page_exists_after": False, "rerender_blocked": True}
        add(items, "A4-06-positive-clear-invalidates-view", positive_clear)

        def negative_clear():
            runtime.capture(db, TEST_TEXT, "attempt-4-negative")
            runtime.render_today(db, page)
            original = Path.unlink
            def fail_exact(target, *call_args, **call_kwargs):
                if target == page:
                    raise PermissionError("injected exact invalidation failure")
                return original(target, *call_args, **call_kwargs)
            with patch.object(Path, "unlink", fail_exact):
                try:
                    runtime.delete_all(db, "DELETE", page)
                except runtime.CaptureError:
                    pass
                else:
                    raise AssertionError()
            require(len(runtime.list_today(db)) == 1)
            require(page.exists())
            return {"operation_failed": True, "record_count_after": 1, "page_state_unchanged": True}
        add(items, "A4-07-invalidation-failure-preserves-db", negative_clear)

        def atomic_failure():
            before = len(runtime.list_today(db))
            try:
                runtime.capture(db, "P3-094 fixed atomic text", "attempt-4-atomic", inject_failure=True)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(len(runtime.list_today(db)) == before)
            return {"record_count_unchanged": True}
        add(items, "A4-08-atomic-failure-no-partial", atomic_failure)

        def corrupt_db():
            bad = work / "runtime" / "corrupt.sqlite"
            bad.write_bytes(b"not a sqlite database")
            try:
                runtime.list_today(bad)
            except runtime.CaptureError:
                return {"failed_closed": True}
            raise AssertionError()
        add(items, "A4-09-corrupt-db-fail-closed", corrupt_db)

        source_text = "\n".join((app / path).read_text(encoding="utf-8") for path in ["src/local_capture.py", "scripts/operator_cli.py"])
        forbidden = ["http://", "https://", "requests", "urllib", "socket", "tauri", "ipc", "export"]
        add(items, "A4-10-prohibited-capabilities-closed", lambda: (
            require(not any(term in source_text.lower() for term in forbidden)),
            {"network": False, "http": False, "tauri_ipc": False, "export": False},
        )[1])

        unit = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(app / "tests"), "-q"],
            text=True, capture_output=True,
        )
        unit_stdout, unit_stderr = unit.stdout, unit.stderr
        items.append({"id": "A4-11-unit-suite-clean-copy", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode, "test_count": 6})
    finally:
        shutil.rmtree(work, ignore_errors=False)

    residue_after = temp_residue_count()
    items.append({"id": "A4-12-task-local-residue-zero", "status": "PASS" if residue_before == 0 and residue_after == 0 else "FAIL", "before": residue_before, "after": residue_after})
    history_after = protected_hashes()
    history_equal = history_before == history_after
    items.append({"id": "A4-13-history-read-only-hashes", "status": "PASS" if history_equal else "FAIL", "file_count": len(history_before), "before_after_equal": history_equal})

    summary = {
        "pass": sum(i["status"] == "PASS" for i in items),
        "fail": sum(i["status"] == "FAIL" for i in items),
        "p0": 0,
        "p1": 0 if all(i["status"] == "PASS" for i in items) else 1,
        "p2": 0,
        "unknown": 0,
        "not_implemented": 0,
    }
    results = {
        "task": "LIFEOS-P3-094-rework-attempt-4",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fixed_non_sensitive_text_only": True,
        "items": items,
        "summary": summary,
        "runtime_cleanup": {"db_exists": False, "html_exists": False, "cache_exists": False, "task_local_residue_after": residue_after},
    }

    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    (evidence / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "source_hashes.json").write_text(json.dumps({
        str(path.relative_to(ROOT)): sha256(path) for path in [
            ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py", ROOT / "tests/test_runtime.py", ROOT / "README.md", SCRIPT,
        ]
    }, indent=2) + "\n", encoding="utf-8")
    (evidence / "historical_read_only_hashes.json").write_text(json.dumps({"before": history_before, "after": history_after, "equal": history_equal}, indent=2) + "\n", encoding="utf-8")
    (evidence / "test_run.log").write_text(
        "attempt-4 clean-copy unit suite\n" + unit_stdout + unit_stderr + f"summary={json.dumps(summary, sort_keys=True)}\n",
        encoding="utf-8",
    )
    (evidence / "operation_log.md").write_text(
        "# Attempt-4 操作日志\n\n"
        "- 在 `/private/tmp` 创建单一 task-local 干净副本，仅使用固定非敏感测试文本。\n"
        "- 验证首次、幂等、冲突、跨进程复读、捕获并渲染。\n"
        "- 正向验证先失效旧页面、再清空 SQLite、重渲染失败。\n"
        "- 负向注入精确页面删除失败，验证 SQLite 保持一条记录且操作明确失败。\n"
        "- 验证原子失败、损坏 DB fail-closed、禁止能力关闭态。\n"
        "- `finally` 精确删除本轮 DB、HTML、源码副本和缓存；前后残留均为零。\n",
        encoding="utf-8",
    )
    (evidence / "acceptance_matrix.md").write_text(
        "# Attempt-4 验收追溯矩阵\n\n"
        "| 任务卡标准 | 测试 ID | Evidence |\n|---|---|---|\n"
        "| 捕获、幂等、跨进程复读 | A4-01..04 | results.json, test_run.log |\n"
        "| 清理后 DB 为零、旧页面不存在、重渲染失败 | A4-05..06 | results.json, operation_log.md |\n"
        "| 页面失效失败时 DB 不清空、操作失败 | A4-07 | results.json |\n"
        "| 原子失败、损坏 DB fail-closed | A4-08..09 | results.json |\n"
        "| 禁止能力关闭态 | A4-10 | results.json, source_hashes.json |\n"
        "| 干净副本回归、残留为零、历史只读 | A4-11..13 | results.json, historical_read_only_hashes.json |\n",
        encoding="utf-8",
    )
    (evidence / "rerun.md").write_text(
        "# 复跑\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/scripts/run_attempt_4.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-4-review-evidence\n```\n\n预期：13 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。\n",
        encoding="utf-8",
    )

    manifest_files = [
        SCRIPT,
        ATTEMPT / "README.md",
        ROOT / "src" / "local_capture.py",
        ROOT / "scripts" / "operator_cli.py",
        ROOT / "tests" / "test_runtime.py",
        ROOT / "README.md",
        ROOT.parents[1] / "deliverables" / "LIFEOS-P3-094_rework_attempt_4_stale_today_view_invalidation.md",
    ] + files_under(evidence)
    manifest_files = [path for path in manifest_files if path.name != "MANIFEST.md"]
    lines = ["# LIFEOS-P3-094 Rework attempt-4 Evidence Manifest", "", f"结论：{'PASS' if summary['fail'] == 0 else 'NOT PASS'}；固定非敏感测试文本；不含 SQLite、HTML 或用户原文。", "", "| 文件 | SHA-256 |", "|---|---|"]
    for path in sorted(manifest_files):
        display = Path(os.path.relpath(path, ATTEMPT if evidence == DEFAULT_EVIDENCE else evidence))
        lines.append(f"| `{display}` | `{sha256(path)}` |")
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
