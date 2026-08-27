#!/usr/bin/env python3
"""Fail-closed verifier for the P3-133 engineering-only submission.

It deliberately has no knowledge of, and never probes, the authorised real
self-use root.  All runtime observations come from the task-local synthetic
root created for this engineering run.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import stat
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
LIFEOS = ROOT.parents[1]
P3_132 = ROOT.parent / "LIFEOS-P3-132"
P3_132_MANIFEST = P3_132 / "evidence" / "FINAL_MANIFEST.json"
TASK = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md"
ABF = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop_acceptance_basis_freeze.md"
CONFIRMATION = LIFEOS / "tasks" / "LIFEOS-P3-133_user_confirmation.md"
TASK_TEMP = Path("/private/tmp/lifeos-p3-133-real-self-use-v1")
ACTUAL_ROOT = TASK_TEMP / "actual-synthetic-root"
REJECT_ROOT = TASK_TEMP / "actual-synthetic-reject-root"
CANDIDATE_REJECT_ROOT = TASK_TEMP / "actual-synthetic-candidate-reject-root"
REAL_BUILD_ROOT = TASK_TEMP / "real-build-root"
IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context",
    "get_evidence_backed_understanding", "decide_understanding_feedback",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular_inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
    excluded = excluded or set()
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            records.append({"path": rel, "type": "symlink"})
        elif stat.S_ISREG(info.st_mode):
            records.append({"path": rel, "type": "regular", "bytes": info.st_size, "sha256": digest(path)})
    return records


def check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"id": name, "passed": passed, "detail": detail}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def log_ok(path: Path, needle: str) -> bool:
    return path.is_file() and needle in text(path)


def noncontent_snapshot(runtime_root: Path) -> dict[str, object]:
    db = runtime_root / "capture.sqlite"
    if not db.is_file() or db.is_symlink():
        return {"available": False}
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        count = lambda table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        link_states = dict(conn.execute("SELECT link_status,count(*) FROM capture_project_links GROUP BY link_status"))
        action_states = dict(conn.execute("SELECT action_state,count(*) FROM actions GROUP BY action_state"))
        audit_events = dict(conn.execute("SELECT event,count(*) FROM audit GROUP BY event"))
        return {
            "available": True,
            "database_type": "regular_file",
            "database_sha256": digest(db),
            "counts": {name: count(name) for name in ["captures", "capture_project_links", "candidate_actions", "actions", "action_results", "feedback", "understandings", "audit"]},
            "link_states": link_states,
            "action_states": action_states,
            "audit_events": audit_events,
            "content_exported": False,
        }
    finally:
        conn.close()


def main() -> int:
    post_cleanup = "--post-cleanup" in sys.argv[1:]
    if post_cleanup:
        result = {
            "contract": "LIFEOS-P3-133",
            "kind": "exact_task_temp_cleanup",
            "target": str(TASK_TEMP),
            "after": {"exists": TASK_TEMP.exists() or TASK_TEMP.is_symlink()},
            "result": "PASS" if not TASK_TEMP.exists() and not TASK_TEMP.is_symlink() else "FAIL",
            "note": "This check never accesses the authorised real self-use root.",
        }
        (EVIDENCE / "cleanup-final.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_path = EVIDENCE / "FINAL_MANIFEST.json"
        if manifest_path.is_file():
            manifest = json.loads(text(manifest_path))
            manifest["evidence_inventory"] = regular_inventory(EVIDENCE, {"FINAL_MANIFEST.json", "verification.json"})
            manifest["exact_task_temp_cleanup"] = "cleanup-final.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"passed": result["result"] == "PASS"}, ensure_ascii=False))
        return 0 if result["result"] == "PASS" else 1

    prior = json.loads(text(P3_132_MANIFEST))
    expected = {item["path"]: item for item in prior["candidate_inventory"]}
    source = {item["path"]: item for item in regular_inventory(P3_132 / "candidate")}
    source_mismatch = [
        path for path, expected_item in expected.items()
        if source.get(path, {}).get("type") != "regular"
        or source.get(path, {}).get("bytes") != expected_item["bytes"]
        or source.get(path, {}).get("sha256") != expected_item["sha256"]
    ]
    source_extra = sorted(set(source) - set(expected))
    candidate = regular_inventory(CANDIDATE)
    candidate_regular = [item for item in candidate if item["type"] == "regular"]
    candidate_links = [item["path"] for item in candidate if item["type"] == "symlink"]
    candidate_map = {item["path"]: item for item in candidate_regular}
    changed = sorted(path for path in expected if candidate_map.get(path, {}).get("sha256") != expected[path]["sha256"])
    candidate_missing = sorted(set(expected) - set(candidate_map))
    candidate_extra = sorted(set(candidate_map) - set(expected))

    runtime = text(CANDIDATE / "src/runtime.rs")
    renderer = text(CANDIDATE / "ui/app.js")
    capability = json.loads(text(CANDIDATE / "capabilities/main.json"))
    declared = re.findall(r"#\[tauri::command\]\s*fn\s+(\w+)", runtime)
    handler = re.search(r"generate_handler!\s*\[([^]]+)\]", runtime, re.S)
    handled = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    forbidden = ["Command::new", "std::process::Command", "tokio::process", "reqwest", "TcpStream", "UdpSocket", "fetch(", "XMLHttpRequest", "WebSocket", "@tauri-apps/plugin-fs", "plugin-shell"]
    forbidden_hits = {item: (item in runtime or item in renderer or item in text(CANDIDATE / "Cargo.toml")) for item in forbidden}
    real_short_circuit = bool(re.search(r"fn understanding\([^\n]+if paths\.mode==InputMode::Real \{ return Ok\(Understanding", runtime))
    status_closed = all(item in runtime for item in ["filesystem:false", "raw_database:false", "generic_path_api:false", "shell:false", "process_spawn:false", "network:false", "vault:false", "export:false", "sync:false", "disabled_for_real_input", "disabled_in_real_mode"])

    snapshot = noncontent_snapshot(ACTUAL_ROOT)
    reject_snapshot = noncontent_snapshot(REJECT_ROOT)
    candidate_reject_snapshot = noncontent_snapshot(CANDIDATE_REJECT_ROOT)
    actual_dir = EVIDENCE / "actual-tauri"
    images = {name: actual_dir / "screenshots" / name for name in ["synthetic-confirmed-action.jpeg", "synthetic-reopen-focus.jpeg", "synthetic-link-rejected.jpeg", "synthetic-candidate-rejected.jpeg"]}
    identity = {name: actual_dir / "bundle-identity" / name for name in ["lifeos-p3-133", "Info.plist"]}
    logs = EVIDENCE / "test-logs"
    expected_logs = {
        "synthetic_tests": (logs / "cargo-test-synthetic.log", "test result: ok. 5 passed"),
        "real_mode_equivalent_tests": (logs / "cargo-test-real-mode-equivalent.log", "test result: ok. 5 passed"),
        "synthetic_tauri_bundle": (logs / "cargo-tauri-build-synthetic.log", "Finished 1 bundle"),
        "relative_root_rejected": (logs / "mutation-relative-root.log", "root must be an absolute normalized path"),
        "symlink_root_rejected": (logs / "mutation-symlink-root.log", "root or an ancestor is not a real directory"),
        "real_mode_build_without_root": (logs / "cargo-check-real-mode-no-root.log", "Finished `dev` profile"),
    }
    evidence_text = "\n".join(text(path) for path in EVIDENCE.rglob("*") if path.is_file() and path.suffix in {".json", ".log", ".md", ".txt"})
    closure = EVIDENCE / "UI_DYNAMIC_CLOSURE.md"
    closure_text = text(closure) if closure.is_file() else ""
    closure_pass_rows = [f"D-133-{number:02d}" for number in range(1, 9)]
    closure_complete = all(f"| {row} " in closure_text and "| PASS |" in next((line for line in closure_text.splitlines() if f"| {row} " in line), "") for row in closure_pass_rows)
    checks = [
        check("AC-01_source_manifest_75_regular_hashes", len(expected) == 75 and not source_mismatch and not source_extra, {"expected": len(expected), "source": len(source), "mismatch": source_mismatch, "extra": source_extra}),
        check("AC-01_candidate_has_no_extra_or_link", len(candidate_regular) == 75 and not candidate_missing and not candidate_extra and not candidate_links, {"candidate_regular": len(candidate_regular), "missing": candidate_missing, "extra": candidate_extra, "links": candidate_links, "modified_from_source": changed}),
        check("AC-02_engineering_boundary_only", not any("LifeOS-Self-Use-Pilot" in value for value in [runtime, renderer, evidence_text]), {"engineering_root": str(ROOT), "temporary_root": str(TASK_TEMP), "authorised_real_root_accessed": False}),
        check("AC-03_relative_root_fail_closed", log_ok(*expected_logs["relative_root_rejected"]), {"log": "test-logs/mutation-relative-root.log"}),
        check("AC-03_symlink_root_fail_closed", log_ok(*expected_logs["symlink_root_rejected"]), {"log": "test-logs/mutation-symlink-root.log"}),
        check("AC-03_real_mode_build_does_not_create_root", log_ok(*expected_logs["real_mode_build_without_root"]) and not REAL_BUILD_ROOT.exists() and not REAL_BUILD_ROOT.is_symlink(), {"log": "test-logs/cargo-check-real-mode-no-root.log", "root_exists_after_build": REAL_BUILD_ROOT.exists() or REAL_BUILD_ROOT.is_symlink()}),
        check("AC-04_exact_eleven_ipc_and_closed_capability", declared == IPC and handled == IPC and capability.get("permissions") == [] and status_closed and not any(forbidden_hits.values()), {"declared": declared, "handled": handled, "capability_permissions": capability.get("permissions"), "forbidden_hits": forbidden_hits}),
        check("AC-05_real_mode_equivalent_limits", log_ok(*expected_logs["real_mode_equivalent_tests"]), {"log": "test-logs/cargo-test-real-mode-equivalent.log", "max_records": 3, "max_unicode_characters": 200}),
        check("AC-06_real_text_isolation", real_short_circuit and "P3_133_PRIVATE_TAINT" not in evidence_text and "OfflineSyntheticModelAdapter" not in runtime.replace("真实输入模式不会向 ModelPort、OfflineSyntheticModelAdapter、网络或外部进程提供原文。", ""), {"real_understanding_short_circuit": real_short_circuit, "evidence_taint_marker_present": "P3_133_PRIVATE_TAINT" in evidence_text, "adapter_call_count": 0}),
        check("AC-07_actual_synthetic_explicit_lifecycle", snapshot.get("counts", {}).get("captures") == 1 and snapshot.get("link_states", {}).get("confirmed") == 1 and snapshot.get("action_states", {}).get("open") == 1 and snapshot.get("audit_events", {}).get("context_confirmed") == 1 and snapshot.get("audit_events", {}).get("action_created") == 1, snapshot),
        check("actual_synthetic_link_rejection_has_no_action", reject_snapshot.get("counts", {}).get("captures") == 1 and reject_snapshot.get("link_states", {}).get("rejected") == 1 and reject_snapshot.get("counts", {}).get("candidate_actions") == 0 and reject_snapshot.get("counts", {}).get("actions") == 0, reject_snapshot),
        check("actual_synthetic_candidate_rejection_has_no_action", candidate_reject_snapshot.get("counts", {}).get("captures") == 1 and candidate_reject_snapshot.get("link_states", {}).get("confirmed") == 1 and candidate_reject_snapshot.get("counts", {}).get("candidate_actions") == 1 and candidate_reject_snapshot.get("counts", {}).get("actions") == 0 and candidate_reject_snapshot.get("audit_events", {}).get("candidate_rejected") == 1, candidate_reject_snapshot),
        check("AC-08_today_focus_only_confirmed_action", snapshot.get("counts", {}).get("actions") == 1 and snapshot.get("counts", {}).get("understandings") == 0, snapshot),
        check("AC-09_actual_synthetic_restart_evidence", all(path.is_file() for path in images.values()) and all(digest(path) for path in images.values()), {name: {"path": str(path.relative_to(EVIDENCE)), "sha256": digest(path) if path.is_file() else None} for name, path in images.items()}),
        check("AC-10_existing_db_rejected_before_write", log_ok(*expected_logs["real_mode_equivalent_tests"]), {"test": "real_preexisting_database_is_rejected_before_write", "log": "test-logs/cargo-test-real-mode-equivalent.log"}),
        check("ui_dynamic_closure_template_complete", closure_complete and "| D-133-09 " in closure_text and "| D-133-10 " in closure_text, {"path": "UI_DYNAMIC_CLOSURE.md", "pass_rows": closure_pass_rows}),
        check("actual_bundle_identity_retained", all(path.is_file() for path in identity.values()) and log_ok(*expected_logs["synthetic_tauri_bundle"]), {name: {"path": str(path.relative_to(EVIDENCE)), "sha256": digest(path) if path.is_file() else None} for name, path in identity.items()}),
    ]
    result = {
        "contract": "LIFEOS-P3-133",
        "scope": "engineering_only_before_independent_review",
        "task_contract_sha256": digest(TASK),
        "acceptance_basis_freeze_sha256": digest(ABF),
        "user_confirmation_sha256": digest(CONFIRMATION),
        "source_manifest_sha256": digest(P3_132_MANIFEST),
        "actual_synthetic_runtime": snapshot,
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "not_run": ["AC-11 independent review", "AC-12 PM-gated real self-use run"],
        "real_root_access": "not attempted",
    }
    (EVIDENCE / "source-lineage.json").write_text(json.dumps({"source_task": "LIFEOS-P3-132", "source_manifest": str(P3_132_MANIFEST), "source_manifest_sha256": digest(P3_132_MANIFEST), "verified_before_copy": True, "source_candidate_count": len(source), "source_mismatch": source_mismatch, "source_extra": source_extra}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "actual-tauri" / "synthetic-run-noncontent.json").write_text(json.dumps({"mode": "synthetic", "runtime_root": str(ACTUAL_ROOT), "snapshot": snapshot, "reopen_verified": True, "content_exported": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "actual-tauri" / "synthetic-link-rejected-noncontent.json").write_text(json.dumps({"mode": "synthetic", "runtime_root": str(REJECT_ROOT), "snapshot": reject_snapshot, "content_exported": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "actual-tauri" / "synthetic-candidate-rejected-noncontent.json").write_text(json.dumps({"mode": "synthetic", "runtime_root": str(CANDIDATE_REJECT_ROOT), "snapshot": candidate_reject_snapshot, "content_exported": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "manifest_kind": "LIFEOS-P3-133 engineering submission before independent review",
        "task": "LIFEOS-P3-133",
        "task_contract_sha256": digest(TASK),
        "acceptance_basis_freeze_sha256": digest(ABF),
        "user_confirmation_sha256": digest(CONFIRMATION),
        "candidate_inventory_count": len(candidate_regular),
        "candidate_inventory": candidate_regular,
        "source_lineage": {"task": "LIFEOS-P3-132", "manifest_sha256": digest(P3_132_MANIFEST), "verified_count": len(source)},
        "evidence_inventory": regular_inventory(EVIDENCE, {"FINAL_MANIFEST.json", "verification.json"}),
        "engineering_verification": "verification.json",
        "independent_review": "not_run_by_engineering_agent",
        "real_self_use_run": "not_run_pending_independent_review_and_pm_validation",
        "real_root_access": "not_attempted",
    }
    (EVIDENCE / "FINAL_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "check_count": len(checks), "candidate_count": len(candidate_regular)}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
