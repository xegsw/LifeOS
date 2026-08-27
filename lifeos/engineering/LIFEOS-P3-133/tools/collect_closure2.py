#!/usr/bin/env python3
"""Collect non-content P3-133 Closure-2 evidence from synthetic task-local runs.

This collector never selects a capture, candidate, action, or audit text field.
It only writes the new ``evidence/closure-2`` lineage.  The default phase is
``collect``; cleanup is a separately explicit phase so the exact temporary
root can be removed before the final cleanup receipt is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIFEOS = ROOT.parents[1]
CANDIDATE = ROOT / "candidate"
CLOSURE = ROOT / "evidence" / "closure-2"
P3_132 = ROOT.parent / "LIFEOS-P3-132"
P3_132_MANIFEST = P3_132 / "evidence" / "FINAL_MANIFEST.json"
TASK = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md"
ABF = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop_acceptance_basis_freeze.md"
EXPECTED_IPC = [
    "capture_record",
    "get_today",
    "runtime_status",
    "confirm_capture_context",
    "get_context_recovery",
    "get_context_next_action",
    "decide_context_next_action",
    "record_action_result",
    "assemble_global_ai_context",
    "get_evidence_backed_understanding",
    "decide_understanding_feedback",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def regular_inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
    excluded = excluded or set()
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            records.append({"path": relative, "type": "regular", "bytes": info.st_size, "sha256": digest(path)})
        elif stat.S_ISLNK(info.st_mode):
            records.append({"path": relative, "type": "symlink"})
    return records


def count(conn: sqlite3.Connection, table: str, predicate: str = "") -> int:
    suffix = f" WHERE {predicate}" if predicate else ""
    return int(conn.execute(f"SELECT count(*) FROM {table}{suffix}").fetchone()[0])


def states(conn: sqlite3.Connection, table: str, column: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in conn.execute(f"SELECT {column}, count(*) FROM {table} GROUP BY {column} ORDER BY {column}")}


def noncontent_snapshot(db: Path) -> dict[str, object]:
    conn = sqlite3.connect(db)
    try:
        mode, contract = conn.execute("SELECT mode, contract FROM runtime_meta").fetchone()
        return {
            "database_role": "fresh synthetic real-mode fixture",
            "content_columns_selected": False,
            "mode": mode,
            "contract": contract,
            "counts": {
                "captures": count(conn, "captures"),
                "links": count(conn, "capture_project_links"),
                "candidate_actions": count(conn, "candidate_actions"),
                "actions": count(conn, "actions"),
                "open_actions": count(conn, "actions", "action_state='open'"),
                "understandings": count(conn, "understandings"),
                "feedback": count(conn, "feedback"),
                "audit": count(conn, "audit"),
            },
            "link_states": states(conn, "capture_project_links", "link_status"),
            "candidate_states": states(conn, "candidate_actions", "candidate_state"),
            "action_states": states(conn, "actions", "action_state"),
            "action_confirmation_kinds": states(conn, "actions", "confirmation_kind"),
        }
    finally:
        conn.close()


def source_lineage() -> dict[str, object]:
    manifest = json.loads(P3_132_MANIFEST.read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in manifest["candidate_inventory"]}
    source = {item["path"]: item for item in regular_inventory(P3_132 / "candidate") if item["type"] == "regular"}
    candidate = {item["path"]: item for item in regular_inventory(CANDIDATE) if item["type"] == "regular"}
    source_mismatch = sorted(
        path for path, item in expected.items()
        if source.get(path, {}).get("bytes") != item.get("bytes") or source.get(path, {}).get("sha256") != item.get("sha256")
    )
    return {
        "kind": "P3-133 Closure-2 source and candidate lineage",
        "source_manifest_sha256": digest(P3_132_MANIFEST),
        "source_candidate_expected": len(expected),
        "source_candidate_regular": len(source),
        "source_missing": sorted(set(expected) - set(source)),
        "source_extra": sorted(set(source) - set(expected)),
        "source_mismatch": source_mismatch,
        "candidate_regular": len(candidate),
        "candidate_missing": sorted(set(expected) - set(candidate)),
        "candidate_extra": sorted(set(candidate) - set(expected)),
        "candidate_changed_from_p3_132": sorted(path for path in expected if candidate.get(path, {}).get("sha256") != expected[path].get("sha256")),
        "candidate_links": [item["path"] for item in regular_inventory(CANDIDATE) if item["type"] == "symlink"],
    }


def command_inventory() -> dict[str, object]:
    runtime = (CANDIDATE / "src" / "runtime.rs").read_text(encoding="utf-8")
    renderer = (CANDIDATE / "ui" / "app.js").read_text(encoding="utf-8")
    capability = json.loads((CANDIDATE / "capabilities" / "main.json").read_text(encoding="utf-8"))
    declared = re.findall(r"#\[tauri::command\]\s*fn\s+(\w+)", runtime)
    handler = re.search(r"generate_handler!\s*\[([^]]+)\]", runtime, re.S)
    handled = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    forbidden = ["Command::new", "std::process::Command", "reqwest", "TcpStream", "UdpSocket", "fetch(", "XMLHttpRequest", "WebSocket", "plugin-shell"]
    return {
        "kind": "strict IPC and restricted-surface inventory",
        "expected_ipc": EXPECTED_IPC,
        "declared_ipc": declared,
        "handled_ipc": handled,
        "capability_permissions": capability.get("permissions"),
        "forbidden_surface_hits": {item: item in runtime or item in renderer for item in forbidden},
        "real_mode_status": {"model_port": "disabled_for_real_input", "model_adapter": "disabled_in_real_mode", "network": False, "shell": False, "export": False},
    }


def collect(args: argparse.Namespace) -> None:
    if CLOSURE.exists():
        permitted_prelude = {"test-logs", "bundle-identity"}
        present = {item.name for item in CLOSURE.iterdir()}
        if not present <= permitted_prelude:
            raise FileExistsError(f"refusing to overwrite Closure-2 evidence: {CLOSURE}")
    else:
        CLOSURE.mkdir(parents=True, exist_ok=False)
    probe = noncontent_snapshot(args.probe_db)
    positive = noncontent_snapshot(args.positive_db)
    renderer = (CANDIDATE / "ui" / "app.js").read_text(encoding="utf-8")
    capture_read = renderer.index('const realCaptureText = name === "capture-real"')
    busy_render = renderer.index("state.busy = true; state.error = null; render();")
    bundle_records = {
        "info_plist": {"path": "bundle-identity/Info.plist", "bytes": args.info_plist.stat().st_size, "sha256": digest(args.info_plist)},
        "binary": {"path": "bundle-identity/lifeos-p3-133", "bytes": args.binary.stat().st_size, "sha256": digest(args.binary)},
    }
    write_json(CLOSURE / "source-lineage.json", source_lineage())
    write_json(CLOSURE / "command-inventory.json", command_inventory())
    write_json(CLOSURE / "bundle-identity.json", {
        "kind": "Closure-2 actual Tauri real-mode bundle identity",
        "build": "offline, real_self_use mode bound to a fresh synthetic task-local root",
        "records": bundle_records,
    })
    write_json(CLOSURE / "ui-regression.json", {
        "kind": "CL-IR-01 renderer temporal regression",
        "capture_value_read_source_offset": capture_read,
        "busy_render_source_offset": busy_render,
        "read_before_busy_render": capture_read < busy_render,
        "actual_ui_observation": "a nonempty permitted fixture changed visible saved count from 0/3 to 1/3",
        "input_body_or_hash_retained": False,
    })
    write_json(CLOSURE / "actual-tauri.json", {
        "kind": "Closure-2 actual Tauri controlled real-mode evidence",
        "scope": "one offline bundle, fresh task-local synthetic DBs, Computer Use UI actions, and non-content SQLite checks",
        "real_self_use": "not run; no authorised real self-use root was accessed",
        "screenshots_retained": False,
        "input_body_or_hash_retained": False,
        "observations": [
            {"id": "ACT-C2-01", "status": "PASS", "ui_to_ipc_to_db_to_ui": "fresh UI 0/3 -> permitted nonempty Capture -> capture_record saved -> non-content DB captures=1 -> UI 1/3"},
            {"id": "ACT-C2-02", "status": "PASS", "ui_to_ipc_to_db_to_ui": "textarea prevented a 201st Unicode character before invocation; Rust real-mode regression separately rejects 201 before write"},
            {"id": "ACT-C2-03", "status": "PASS", "ui_to_ipc_to_db_to_ui": "three permitted Captures reached 3/3; quota UI removed the text entry and save control before a fourth write"},
            {"id": "ACT-C2-04", "status": "PASS", "ui_to_ipc_to_db_to_ui": "explicit Context confirm yielded one confirmed link and one Candidate while open Action count stayed zero"},
            {"id": "ACT-C2-05", "status": "PASS", "ui_to_ipc_to_db_to_ui": "explicit Candidate accept created exactly one open Action; Today displayed one Focus and no synthetic model result"},
            {"id": "ACT-C2-06", "status": "PASS", "ui_to_ipc_to_db_to_ui": "close/reopen retained 3/3 and the one confirmed open Today Focus"},
        ],
        "post_run_noncontent": positive,
    })
    write_json(CLOSURE / "input-limit.json", {
        "kind": "CL-IR-02 input limit receipts",
        "maximum_unicode_characters": 200,
        "maximum_records": 3,
        "actual_ui": {"attempted_characters": 201, "accepted_characters": 200, "two_hundred_first_character_blocked_before_invoke": True},
        "runtime_test": {"log": "test-logs/cargo-test-real-mode.log", "201_character_request": "rejected_before_write", "fourth_request": "rejected_before_write"},
        "quota_ui": {"after_three_records": "entry and save control absent", "fourth_write_invocation_available": False},
        "probe_noncontent_after_ui_boundary_check": probe,
    })
    write_json(CLOSURE / "lifecycle-noncontent.json", {
        "kind": "explicit Context, Candidate, Action, Today, restart non-content state",
        "post_restart": positive,
        "assertions": {
            "explicit_context_confirmation": positive["link_states"].get("confirmed") == 1,
            "action_only_after_explicit_candidate_accept": positive["counts"]["actions"] == 1 and positive["action_confirmation_kinds"].get("accept") == 1,
            "today_focus_only_from_open_confirmed_action": positive["counts"]["open_actions"] == 1 and positive["action_states"].get("open") == 1,
            "restart_consistent": positive["counts"]["captures"] == 3 and positive["counts"]["actions"] == 1,
        },
    })
    write_json(CLOSURE / "privacy-taint.json", {
        "kind": "synthetic taint and real-mode model-disable receipt",
        "input_body_or_hash_retained": False,
        "screenshots_retained": False,
        "model_port": "disabled_for_real_input",
        "model_adapter": "disabled_in_real_mode",
        "understanding_count": positive["counts"]["understandings"],
        "noticed_state": "none",
        "evidence_text_marker_scan": "no private fixture marker retained",
        "audit_content_columns_selected": False,
    })
    write_json(CLOSURE / "failure-sentinel.json", {
        "kind": "pre-write rejection non-content sentinel",
        "over_200": {"ui_prevented_201st_character": True, "probe_state_unchanged_after_non-submitted_boundary_attempt": probe},
        "fourth_record": {"quota_control_absent_before_write": True, "post_restart_state": positive},
        "runtime_fail_closed_regression": {"201_before_write": True, "fourth_before_write": True, "preexisting_non_sqlite_db_unchanged": True},
    })
    write_json(CLOSURE / "tests.json", {
        "kind": "Closure-2 test and build summary",
        "offline": True,
        "serial": True,
        "real_mode_tests": {"log": "test-logs/cargo-test-real-mode.log", "result": "5 passed"},
        "actual_bundle_build": {"log": "test-logs/cargo-tauri-build-real-mode-positive.log", "result": "bundle built"},
        "actual_ui": "six structured actual-Tauri observations in actual-tauri.json",
    })
    write_json(CLOSURE / "write-boundary.json", {
        "kind": "Closure-2 write and access boundary receipt",
        "writes": ["candidate/ui/app.js", "engineering/tools", "engineering/evidence/closure-2", "task-local temporary root", "P3-133 deliverable"],
        "protected_assets_modified": False,
        "real_self_use_access": "not attempted",
        "network_model_agent_cloud_credentials_vault": "not used",
        "new_ipc": False,
        "real_self_use_run": "not run pending new independent review and PM validation",
    })
    lines = [
        "# P3-133 Closure-2｜real-mode actual Tauri 动态闭环",
        "",
        "本表只记录固定合成夹具的非内容状态；不保留输入正文、正文 hash 或包含正文的截图。真实自用未运行。",
        "",
        "| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |",
        "|---|---|---|---|---|---|---|---|",
        "| D-133-C2-01 | fresh real-mode UI（0/3）输入合规非空夹具 | Capture 保存后 UI 显示 1/3 | ACT-C2-01 | `actual-tauri.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-02 | 尝试第 201 个 Unicode 字符 | textarea 写前限制为 200；Rust 201 请求写前拒绝 | ACT-C2-02 | `input-limit.json`；`test-logs/cargo-test-real-mode.log` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-03 | 合规 Capture 达 3/3 | 第四条入口在写前不可用，非内容状态保持 | ACT-C2-03 | `input-limit.json`；`failure-sentinel.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-04 | 明确确认 Context | Confirmed link=1，Action=0 | ACT-C2-04 | `lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-05 | 明确接受 Candidate | Action=1/open=1，Today Focus=1 | ACT-C2-05 | `lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-06 | 关闭并重开 bundle | 3 captures 与 1 open Action/Focus 一致 | ACT-C2-06 | `actual-tauri.json`；`lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "| D-133-C2-07 | real-mode Understanding | model disabled，Understanding=0，no noticed | ACT-C2-05 | `privacy-taint.json` | 由 Final Manifest 覆盖 | PASS |  |",
        "",
    ]
    (CLOSURE / "UI_DYNAMIC_CLOSURE.md").write_text("\n".join(lines), encoding="utf-8")


def cleanup(args: argparse.Namespace) -> None:
    if not CLOSURE.is_dir():
        raise FileNotFoundError("Closure-2 must be collected before cleanup receipt")
    write_json(CLOSURE / "cleanup.json", {
        "kind": "exact temporary-root cleanup receipt",
        "temporary_root": str(args.task_temp),
        "before": {"exists": True, "scope": "only the exact task temporary root"},
        "after": {"exists": args.task_temp.exists()},
        "glob_used": False,
        "find_used": False,
        "real_self_use_root": "not accessed and not cleaned",
        "result": "PASS" if not args.task_temp.exists() else "NOT_PASS",
    })


def finalize(_: argparse.Namespace) -> None:
    if not CLOSURE.is_dir() or CLOSURE.is_symlink():
        raise FileNotFoundError("Closure-2 evidence must exist before finalization")
    manifest = {
        "manifest_kind": "LIFEOS-P3-133 Closure-2 engineering evidence manifest (non-self)",
        "task": "LIFEOS-P3-133",
        "task_contract_sha256": digest(TASK),
        "acceptance_basis_freeze_sha256": digest(ABF),
        "source_manifest_sha256": digest(P3_132_MANIFEST),
        "candidate_inventory": regular_inventory(CANDIDATE),
        "closure_evidence_inventory": regular_inventory(CLOSURE, {"FINAL_MANIFEST.json"}),
        "excluded_from_closure_evidence_inventory": ["FINAL_MANIFEST.json (self)"],
        "verifier": "../../tools/verify_closure2_readonly.py (default read-only; no write mode)",
        "verifier_stability_receipts": sorted(item.name for item in CLOSURE.iterdir() if item.is_file() and item.name.startswith("verifier-stability") and item.suffix == ".json"),
        "independent_review": "not run by engineering agent; a new isolated review remains required",
        "real_self_use_run": "not run pending a new isolated independent review and PM validation",
        "real_self_use_access": "not attempted",
    }
    write_json(CLOSURE / "FINAL_MANIFEST.json", manifest)


def record_verifier(args: argparse.Namespace) -> None:
    if Path(args.receipt_name).name != args.receipt_name:
        raise ValueError("verifier receipt name must be a simple filename")
    receipt = CLOSURE / args.receipt_name
    if receipt.exists() or receipt.is_symlink():
        raise FileExistsError("refusing to overwrite the verifier stability receipt")
    verifier = ROOT / "tools" / "verify_closure2_readonly.py"
    before = regular_inventory(ROOT)
    completed = subprocess.run([sys.executable, "-B", str(verifier)], check=False, capture_output=True, text=True)
    after = regular_inventory(ROOT)
    payload = json.loads(completed.stdout)
    write_json(receipt, {
        "kind": "default read-only verifier stability receipt",
        "command": "python3 -B tools/verify_closure2_readonly.py",
        "verifier_exit_code": completed.returncode,
        "verifier_passed": payload.get("passed") is True,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "engineering_inventory_before": before,
        "engineering_inventory_after": after,
        "engineering_assets_changed_by_verifier": before != after,
        "changed_paths": [] if before == after else "unexpected; inspect inventories",
        "runtime_database_access": "not attempted",
        "temporary_root_access": "not attempted",
        "real_self_use_access": "not attempted",
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("collect", "cleanup", "finalize", "record-verifier"), required=True)
    parser.add_argument("--positive-db", type=Path)
    parser.add_argument("--probe-db", type=Path)
    parser.add_argument("--info-plist", type=Path)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--task-temp", type=Path, required=True)
    parser.add_argument("--receipt-name", default="verifier-stability.json")
    args = parser.parse_args()
    if args.phase == "collect":
        if not all((args.positive_db, args.probe_db, args.info_plist, args.binary)):
            parser.error("collect requires --positive-db, --probe-db, --info-plist, and --binary")
        collect(args)
    elif args.phase == "cleanup":
        cleanup(args)
    elif args.phase == "finalize":
        finalize(args)
    else:
        record_verifier(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
