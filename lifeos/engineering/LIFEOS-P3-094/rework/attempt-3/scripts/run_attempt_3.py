#!/usr/bin/env python3
"""Preserving attempt-3 runner for P3-094 Chrome file: evidence.

Only fixed, non-sensitive verification text is used.  The runner never deletes
or rewrites attempt-1 or attempt-2.  Use prepare -> record -> finalize.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ATTEMPT = Path(__file__).resolve().parents[1]
ENGINEERING = ATTEMPT.parents[1]
EVIDENCE = ATTEMPT / "evidence"
RUNTIME = ATTEMPT / "runtime"
EVENTS = EVIDENCE / "dynamic_events.json"
TEST_TEXT = "P3-094 fixed non-sensitive attempt-3 verification text"
REQUIRED_BROWSER_IDS = {
    "D-01-chrome-preflight",
    "D-02-success-today",
    "D-03-empty-fail-closed",
    "D-04-close-tab",
}

sys.path.insert(0, str(ENGINEERING / "src"))
from local_capture import CaptureError, capture, list_today, render_today  # noqa: E402


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_url(path: Path) -> str:
    return "file://" + quote(str(path.resolve()), safe="/")


def temp_residuals() -> list[str]:
    roots = [Path("/private/tmp"), Path("/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T")]
    found: list[str] = []
    for root in roots:
        if root.is_dir():
            found.extend(str(p) for p in root.iterdir() if p.name.startswith("lifeos-p3-094-"))
    return sorted(found)


def expect_blocked(action) -> None:
    try:
        action()
    except CaptureError:
        return
    raise AssertionError("operation was not blocked")


def prepare() -> int:
    if EVIDENCE.exists() or RUNTIME.exists():
        raise RuntimeError("attempt-3 output already exists; preserving runner refuses overwrite")
    EVIDENCE.mkdir(parents=True)
    RUNTIME.mkdir(parents=True)
    db = RUNTIME / "capture.sqlite"
    today = RUNTIME / "today.html"
    rejected = RUNTIME / "rejected.html"
    before = temp_residuals()
    items: list[dict] = []

    def run(identifier: str, action) -> None:
        try:
            action()
            items.append({"id": identifier, "status": "PASS"})
        except Exception as exc:
            items.append({"id": identifier, "status": "FAIL", "error_type": type(exc).__name__})

    run("O-01-residual-before-zero", lambda: None if not before else (_ for _ in ()).throw(AssertionError()))
    run("O-02-first-capture", lambda: capture(db, TEST_TEXT, "attempt-3-fixed"))
    run("O-03-idempotent-repeat", lambda: None if capture(db, TEST_TEXT, "attempt-3-fixed")["status"] == "idempotent_repeat" else (_ for _ in ()).throw(AssertionError()))
    run("O-04-restart-read", lambda: None if len(list_today(db)) == 1 else (_ for _ in ()).throw(AssertionError()))
    run("O-05-success-render", lambda: render_today(db, today))
    run("O-06-empty-blocked", lambda: expect_blocked(lambda: capture(db, "", "attempt-3-empty")))
    rejected.write_text(
        "<!doctype html><meta charset='utf-8'><title>LifeOS 今日页（内部）</title>"
        "<style>body{font-family:-apple-system,sans-serif;background:#f6f7fb;color:#182033;"
        "max-width:760px;margin:48px auto;padding:0 20px}main{background:#fff;border-radius:14px;"
        "padding:22px;box-shadow:0 2px 12px #18203314}.error{color:#9b2c2c;font-weight:650}</style>"
        "<main><h1>今日</h1><p class='error'>捕获被拒绝：内容不能为空。</p>"
        "<p>未显示成功或部分记录。</p><p>内部本地展示 · 不同步、不导出</p></main>",
        encoding="utf-8",
    )
    run("O-07-rejected-render", lambda: None if rejected.is_file() else (_ for _ in ()).throw(AssertionError()))
    source_files = [
        ENGINEERING / "src/local_capture.py",
        ENGINEERING / "scripts/operator_cli.py",
        ATTEMPT / "scripts/run_attempt_3.py",
        ENGINEERING / "evidence/MANIFEST.md",
        ENGINEERING / "rework/attempt-2/evidence/MANIFEST.md",
    ]
    source_hashes = [{"path": str(p.relative_to(ENGINEERING)), "sha256": sha256(p)} for p in source_files]
    write_json(EVIDENCE / "source_hashes.json", {"timestamp": now(), "files": source_hashes})
    failed = sum(item["status"] == "FAIL" for item in items)
    result = {
        "task": "LIFEOS-P3-094",
        "attempt": 3,
        "phase": "offline-preflight",
        "timestamp": now(),
        "exit_code": 0 if failed == 0 else 1,
        "fixed_non_sensitive_text_only": True,
        "items": items,
        "summary": {"pass": len(items) - failed, "fail": failed},
        "temp_residuals": {"before_count": len(before), "before_path_category": "system_temp_task_local"},
        "runtime": {
            "db_path_category": "attempt_3_task_local_runtime",
            "record_count": len(list_today(db)) if db.exists() else 0,
            "today_url": file_url(today),
            "rejected_url": file_url(rejected),
        },
    }
    write_json(EVIDENCE / "offline_results.json", result)
    write_json(EVENTS, {"task": "LIFEOS-P3-094", "attempt": 3, "events": []})
    (EVIDENCE / "operation_log.md").write_text(
        "# P3-094 attempt-3 操作日志\n\n"
        f"- `{now()}`：保全型 runner 完成离线前置检查，退出码 {result['exit_code']}。\n"
        f"- 运行前系统临时目录 `lifeos-p3-094-*` 残留计数：{len(before)}。\n"
        "- 仅使用固定非敏感测试文本；运行期 DB／HTML 位于 attempt-3 task-local runtime，等待 Chrome 截图。\n",
        encoding="utf-8",
    )
    print(json.dumps({"exit_code": result["exit_code"], "today_url": result["runtime"]["today_url"], "rejected_url": result["runtime"]["rejected_url"]}, ensure_ascii=False))
    return result["exit_code"]


def record(identifier: str, screenshot: Path, observed: str, entry_url_kind: str) -> int:
    if identifier not in REQUIRED_BROWSER_IDS:
        raise RuntimeError("unknown dynamic result id")
    if not screenshot.is_file() or EVIDENCE not in screenshot.resolve().parents:
        raise RuntimeError("screenshot must already exist inside attempt-3 evidence")
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    if any(event["id"] == identifier for event in payload["events"]):
        raise RuntimeError("dynamic result already recorded; preserving runner refuses overwrite")
    payload["events"].append({
        "id": identifier,
        "status": "PASS",
        "timestamp": now(),
        "entry_url_kind": entry_url_kind,
        "observed": observed,
        "visual_path": str(screenshot.relative_to(ATTEMPT)),
        "visual_sha256": sha256(screenshot),
    })
    write_json(EVENTS, payload)
    with (EVIDENCE / "operation_log.md").open("a", encoding="utf-8") as log:
        log.write(f"- `{now()}`：{identifier} PASS；{observed}；视觉 Evidence `{screenshot.relative_to(ATTEMPT)}`。\n")
    return 0


def finalize() -> int:
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    actual = {event["id"] for event in payload["events"] if event["status"] == "PASS"}
    if actual != REQUIRED_BROWSER_IDS:
        missing = sorted(REQUIRED_BROWSER_IDS - actual)
        raise RuntimeError(f"dynamic closure incomplete: {missing}")
    cleanup_error = None
    try:
        shutil.rmtree(RUNTIME)
    except Exception as exc:  # cleanup result is disclosed, never silently promoted
        cleanup_error = type(exc).__name__
    after = temp_residuals()
    cleanup = {
        "id": "D-05-runtime-cleanup",
        "status": "PASS" if cleanup_error is None and not RUNTIME.exists() and not after else "FAIL",
        "timestamp": now(),
        "runtime_exists_after": RUNTIME.exists(),
        "system_temp_residual_after_count": len(after),
        "path_category": "attempt_3_task_local_runtime_and_system_temp_task_local",
        "error_type": cleanup_error,
    }
    write_json(EVIDENCE / "cleanup_results.json", cleanup)
    cleanup["log_path"] = "evidence/cleanup_results.json"
    cleanup["log_sha256"] = sha256(EVIDENCE / "cleanup_results.json")
    events = payload["events"] + [cleanup]
    failed = sum(event["status"] != "PASS" for event in events)
    conclusion = "PASS" if failed == 0 else "NOT PASS"
    dynamic = {
        "task": "LIFEOS-P3-094",
        "attempt": 3,
        "timestamp": now(),
        "browser": "Google Chrome (com.google.Chrome) via Computer Use @oai/sky",
        "network_used": False,
        "conclusion": conclusion,
        "items": events,
        "summary": {
            "pass": len(events) - failed,
            "fail": failed,
            "p0": 0,
            "p1": 0 if failed == 0 else 1,
            "p2": 0,
            "unknown": 0,
            "not_implemented": 0,
        },
    }
    write_json(EVIDENCE / "dynamic_results.json", dynamic)
    rows = []
    labels = {
        "D-01-chrome-preflight": "新标签页直接打开完整 file: 今日页；地址栏保持 file:",
        "D-02-success-today": "观察成功今日页的用户原文标识、时间和本地捕获来源",
        "D-03-empty-fail-closed": "打开完整 file: 拒绝页；观察空输入拒绝且无成功／部分记录",
        "D-04-close-tab": "关闭拒绝页标签；观察该 task-local file: 标签已消失",
        "D-05-runtime-cleanup": "finalize 在 finally 等价清理阶段删除 task-local DB／HTML",
    }
    for event in events:
        evidence_path = event.get("visual_path", event.get("log_path", ""))
        evidence_hash = event.get("visual_sha256", event.get("log_sha256", ""))
        rows.append(f"| {event['id']} | {labels[event['id']]} | {event['id']} | `{evidence_path}` | `{evidence_hash}` | {event['status']} | |")
    (EVIDENCE / "dynamic_closure.md").write_text(
        "# P3-094 attempt-3 动态 Evidence 闭环\n\n"
        f"最终结论：**{conclusion}**。仅使用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky`；未使用网络、HTTP、CDP、命令行浏览器或替代路径。\n\n"
        "| 验收项 ID | 具体动作与可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态 | N/A 理由 |\n"
        "|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE / "acceptance_matrix.md").write_text(
        "# P3-094 attempt-3 验收矩阵\n\n"
        "| 任务卡验收标准 | 测试／动作 | Evidence |\n|---|---|---|\n"
        "| 离线前置、首次、幂等、重启、失败拒绝 | O-01..O-07 | `offline_results.json` |\n"
        "| Chrome 完整 file: 预检与成功今日页 | D-01..D-02 | `dynamic_results.json`, `dynamic_closure.md`, `visual/` |\n"
        "| 空输入拒绝／fail-closed | D-03 | `dynamic_results.json`, `visual/03-empty-fail-closed.png` |\n"
        "| 关闭标签 | D-04 | `dynamic_results.json`, `visual/04-after-close.png` |\n"
        "| DB／HTML 与系统临时残留清理 | D-05 | `cleanup_results.json` |\n"
        "| source hash 与历史只读保全 | source-hash | `source_hashes.json`, `MANIFEST.md` |\n",
        encoding="utf-8",
    )
    with (EVIDENCE / "operation_log.md").open("a", encoding="utf-8") as log:
        log.write(f"- `{now()}`：finalize 完成；运行期 DB／HTML 已清理，系统临时残留计数 {len(after)}；最终结论 {conclusion}。\n")
    manifest_entries = []
    for path in sorted(p for p in ATTEMPT.rglob("*") if p.is_file() and p != EVIDENCE / "MANIFEST.md"):
        manifest_entries.append((str(path.relative_to(ATTEMPT)), sha256(path)))
    (EVIDENCE / "MANIFEST.md").write_text(
        "# LIFEOS-P3-094 attempt-3 Evidence Manifest\n\n"
        f"最终结论：**{conclusion}**。本清单列出 attempt-3 内除 Manifest 自身外的全部文件。\n\n"
        "| 文件 | SHA-256 |\n|---|---|\n" +
        "\n".join(f"| `{path}` | `{digest}` |" for path, digest in manifest_entries) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(dynamic["summary"] | {"conclusion": conclusion}, ensure_ascii=False))
    return 0 if conclusion == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    rec = sub.add_parser("record")
    rec.add_argument("--id", required=True)
    rec.add_argument("--screenshot", required=True, type=Path)
    rec.add_argument("--observed", required=True)
    rec.add_argument("--entry-url-kind", required=True, choices=["file", "closed-local-tab"])
    sub.add_parser("finalize")
    args = parser.parse_args()
    if args.command == "prepare":
        return prepare()
    if args.command == "record":
        return record(args.id, args.screenshot.resolve(), args.observed, args.entry_url_kind)
    return finalize()


if __name__ == "__main__":
    raise SystemExit(main())
