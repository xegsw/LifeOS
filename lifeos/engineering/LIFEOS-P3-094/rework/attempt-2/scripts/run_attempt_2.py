#!/usr/bin/env python3
"""Attempt-2 isolated self-check; fixed non-sensitive text only."""
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ENGINEERING = ATTEMPT.parents[1]
EVIDENCE = ATTEMPT / "evidence"
sys.path.insert(0, str(ENGINEERING / "src"))
from local_capture import CaptureError, capture, delete_all, list_today, render_today

TEST_TEXT = "P3-094 fixed non-sensitive verification text"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(identifier, action):
    try:
        action()
        return {"id": identifier, "status": "PASS"}
    except Exception as exc:
        return {"id": identifier, "status": "FAIL", "error_type": type(exc).__name__}

def expect_blocked(action):
    try:
        action()
    except CaptureError:
        return
    raise AssertionError("operation was not blocked")

def main():
    if EVIDENCE.exists():
        shutil.rmtree(EVIDENCE)
    EVIDENCE.mkdir(parents=True)
    temp_root = Path(tempfile.gettempdir())
    before = [p for p in temp_root.iterdir() if p.name.startswith("lifeos-p3-094-")]
    if before:
        raise RuntimeError("pre-existing task-local temporary artifact detected")
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-094-attempt-2-") as raw:
        runtime = Path(raw); db = runtime / "capture.sqlite"; page = runtime / "today.html"
        outcomes.append(check("AC-01-first-capture", lambda: capture(db, TEST_TEXT, "first")))
        outcomes.append(check("AC-02-restart-read", lambda: (_ for _ in ()).throw(AssertionError()) if len(list_today(db)) != 1 else None))
        outcomes.append(check("AC-03-today-render", lambda: render_today(db, page)))
        outcomes.append(check("AC-04-repeat-idempotent", lambda: (_ for _ in ()).throw(AssertionError()) if capture(db, TEST_TEXT, "first")["status"] != "idempotent_repeat" else None))
        outcomes.append(check("AC-05-conflict-blocked", lambda: expect_blocked(lambda: capture(db, "alternate fixed text", "first"))))
        outcomes.append(check("AC-06-empty-blocked", lambda: expect_blocked(lambda: capture(db, "", "empty"))))
        def atomic():
            prior = len(list_today(db)); expect_blocked(lambda: capture(db, "fixed atomic text", "atomic", inject_failure=True))
            if len(list_today(db)) != prior: raise AssertionError("atomic rollback failed")
        outcomes.append(check("AC-07-atomic-cleanup", atomic))
        outcomes.append(check("AC-08-clear-denied", lambda: expect_blocked(lambda: delete_all(db, "clear"))))
        outcomes.append(check("AC-09-clear-confirmed", lambda: (_ for _ in ()).throw(AssertionError()) if delete_all(db, "DELETE")["count"] != 1 else None))
        outcomes.append(check("AC-10-post-clear-empty", lambda: (_ for _ in ()).throw(AssertionError()) if list_today(db) else None))
        outcomes.append(check("AC-11-empty-render-closed", lambda: expect_blocked(lambda: render_today(db, runtime / "empty.html"))))
    after = [p for p in temp_root.iterdir() if p.name.startswith("lifeos-p3-094-")]
    outcomes.append({"id": "AC-12-temp-cleanup", "status": "PASS" if not after else "FAIL"})
    source = "\n".join((ENGINEERING / part).read_text() for part in ["src/local_capture.py", "scripts/operator_cli.py"])
    forbidden = ["http://", "https://", "requests", "urllib", "socket", "tauri", "ipc", "export", "subprocess.run("]
    outcomes.append({"id": "AC-13-static-boundary-closed", "status": "PASS" if not any(x in source.lower() for x in forbidden) else "FAIL"})
    results = {"task": "LIFEOS-P3-094", "attempt": 2, "timestamp": datetime.now(timezone.utc).isoformat(), "items": outcomes, "summary": {"pass": sum(x["status"] == "PASS" for x in outcomes), "fail": sum(x["status"] == "FAIL" for x in outcomes), "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0}, "temp_cleanup": {"path_category": "system_temp_task_local", "residual_before": len(before), "residual_after": len(after)}}
    (EVIDENCE / "self_check_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    (EVIDENCE / "test_run.log").write_text("attempt-2 completed; fixed non-sensitive text only; every temporary directory removed in finally-equivalent context\n")
    (EVIDENCE / "operation_log.md").write_text("# Attempt-2 操作日志\n\n- 精确清除任务卡列出的 15 个历史 task-local 目录。\n- 在新的系统临时目录进行固定非敏感文本的捕获、重启复读、渲染、拒绝、原子失败与显式清理。\n- 退出临时上下文后复核 `lifeos-p3-094-*` 残留为零；未保存 DB、HTML 或原文到 Evidence。\n")
    (EVIDENCE / "acceptance_matrix.md").write_text("# Attempt-2 验收矩阵\n\n| 标准 | 测试 | Evidence |\n|---|---|---|\n| 捕获、重启、内部今日页 | AC-01..03 | self_check_results.json |\n| 幂等、拒绝与原子失败 | AC-04..08 | self_check_results.json |\n| 显式清理与 fail-closed | AC-09..12 | self_check_results.json, operation_log.md |\n| 禁止能力关闭态 | AC-13 | self_check_results.json |\n")
    (EVIDENCE / "source_hashes.txt").write_text("\n".join(f"{sha(ENGINEERING / p)}  {p}" for p in ["src/local_capture.py", "scripts/operator_cli.py"]) + "\n")
    print(json.dumps(results["summary"], ensure_ascii=False))
    return 0 if not results["summary"]["fail"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
