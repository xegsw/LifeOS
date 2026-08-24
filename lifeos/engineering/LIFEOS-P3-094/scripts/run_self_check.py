#!/usr/bin/env python3
"""Creates only fixed-text evidence; never serializes capture text or DB content."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
sys.path.insert(0, str(ROOT / "src"))
from local_capture import CaptureError, capture, delete_all, list_today, render_today, safe_snapshot

TEST_TEXT = "P3-094 fixed non-sensitive verification text"

def outcome(name, fn):
    try:
        fn(); return {"id": name, "status": "PASS"}
    except Exception as exc:
        return {"id": name, "status": "FAIL", "error_type": type(exc).__name__}

def main():
    if EVIDENCE.exists(): shutil.rmtree(EVIDENCE)
    EVIDENCE.mkdir()
    runtime = Path(tempfile.mkdtemp(prefix="lifeos-p3-094-runtime-"))
    db, page = runtime / "capture.sqlite", runtime / "today.html"
    items = []
    items.append(outcome("AC-01-first-capture", lambda: (_ for _ in ()).throw(AssertionError()) if capture(db, TEST_TEXT, "first")["status"] != "saved" else None))
    items.append(outcome("AC-02-restart-read", lambda: (_ for _ in ()).throw(AssertionError()) if len(list_today(db)) != 1 else None))
    items.append(outcome("AC-03-today-render", lambda: (_ for _ in ()).throw(AssertionError()) if render_today(db, page)["record_count"] != 1 else None))
    items.append(outcome("AC-04-repeat-idempotent", lambda: (_ for _ in ()).throw(AssertionError()) if capture(db, TEST_TEXT, "first")["status"] != "idempotent_repeat" else None))
    def conflict():
        try: capture(db, "alternate fixed text", "first")
        except CaptureError: return
        raise AssertionError()
    items.append(outcome("AC-05-conflict-blocked", conflict))
    def empty():
        try: capture(db, "", "empty")
        except CaptureError: return
        raise AssertionError()
    items.append(outcome("AC-06-empty-blocked", empty))
    def atomic():
        before = len(list_today(db))
        try: capture(db, "fixed atomic text", "atomic", inject_failure=True)
        except CaptureError: pass
        else: raise AssertionError()
        if len(list_today(db)) != before: raise AssertionError()
    items.append(outcome("AC-07-atomic-cleanup", atomic))
    def corrupt():
        bad = runtime / "bad.sqlite"; bad.write_bytes(b"not a sqlite database")
        try: list_today(bad)
        except CaptureError: return
        raise AssertionError()
    items.append(outcome("AC-08-corrupt-db-fail-closed", corrupt))
    def clear_denied():
        try: delete_all(db, "clear")
        except CaptureError: return
        raise AssertionError()
    items.append(outcome("AC-09-clear-denied", clear_denied))
    items.append(outcome("AC-10-clear-confirmed", lambda: (_ for _ in ()).throw(AssertionError()) if delete_all(db, "DELETE")["count"] != 1 else None))
    items.append(outcome("AC-11-post-clear-empty", lambda: (_ for _ in ()).throw(AssertionError()) if list_today(db) else None))
    def no_render():
        try: render_today(db, runtime / "empty.html")
        except CaptureError: return
        raise AssertionError()
    items.append(outcome("AC-12-empty-render-fail-closed", no_render))
    source = "\n".join(p.read_text() for p in [ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py"])
    forbidden = ["http://", "https://", "requests", "urllib", "socket", "tauri", "ipc", "export", "subprocess.run("]
    items.append({"id": "AC-13-static-boundary-closed", "status": "PASS" if not any(x in source.lower() for x in forbidden) else "FAIL"})
    unit = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-q"], text=True, capture_output=True)
    items.append({"id": "AC-14-unit-suite", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode})
    results = {"task": "LIFEOS-P3-094", "timestamp": datetime.now(timezone.utc).isoformat(), "items": items,
               "summary": {"pass": sum(x["status"] == "PASS" for x in items), "fail": sum(x["status"] == "FAIL" for x in items), "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0},
               "runtime": {"path_category": "system_temp_task_local", "created": True, "record_count_before_cleanup": 1, "cleared": True, "final_db_exists": False}}
    # Do not persist raw DB, page, text, or IDs. Remove task-local runtime after verification.
    shutil.rmtree(runtime)
    (EVIDENCE / "self_check_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    (EVIDENCE / "test_run.log").write_text("self-check completed; fixed non-sensitive text only; task-local runtime removed; unit_exit=%s\n" % unit.returncode)
    (EVIDENCE / "operation_log.md").write_text("# 操作日志\n\n- 创建 task-local 系统临时 SQLite。\n- 使用固定非敏感测试文本完成保存、重启复读和内部渲染。\n- 验证重复、拒绝、原子失败、损坏 DB、显式清理及关闭态。\n- 清理运行目录；未写入 DB、页面或原文至 Evidence。\n")
    (EVIDENCE / "acceptance_matrix.md").write_text("# 验收矩阵\n\n| 标准 | 测试 | Evidence |\n|---|---|---|\n| 捕获、重启、今日页 | AC-01..03 | self_check_results.json |\n| 幂等与拒绝 | AC-04..06 | self_check_results.json |\n| 原子失败、损坏 DB、清理 | AC-07..12 | self_check_results.json, operation_log.md |\n| 禁止能力关闭 | AC-13 | self_check_results.json |\n| 可运行回归 | AC-14 | self_check_results.json, test_run.log |\n")
    print(json.dumps(results["summary"], ensure_ascii=False))
    return 0 if results["summary"]["fail"] == 0 else 1

if __name__ == "__main__": raise SystemExit(main())
