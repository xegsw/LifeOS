#!/usr/bin/env python3
"""Default read-only verifier for P3-133 Closure-2 engineering evidence.

It reads only the candidate, the P3-132 frozen source, and Closure-2 assets.
It never opens a runtime database, a temporary root, or a real self-use root,
and it has no write mode.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
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
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding",
    "decide_understanding_feedback",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
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


def check(identifier: str, passed: bool, detail: object) -> dict[str, object]:
    return {"id": identifier, "passed": passed, "detail": detail}


def text_evidence() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in CLOSURE.rglob("*")
        if path.is_file() and not path.is_symlink() and path.suffix in {".json", ".md", ".log", ".txt"}
    )


def verify() -> dict[str, object]:
    if not CLOSURE.is_dir() or CLOSURE.is_symlink():
        raise ValueError("Closure-2 evidence directory is absent or invalid")
    source_manifest = read_json(P3_132_MANIFEST)
    if not isinstance(source_manifest, dict) or not isinstance(source_manifest.get("candidate_inventory"), list):
        raise ValueError("P3-132 manifest lacks candidate inventory")
    expected = {item["path"]: item for item in source_manifest["candidate_inventory"]}
    source_items = {item["path"]: item for item in inventory(P3_132 / "candidate") if item["type"] == "regular"}
    candidate_records = inventory(CANDIDATE)
    candidate_items = {item["path"]: item for item in candidate_records if item["type"] == "regular"}
    source_mismatch = sorted(path for path, item in expected.items() if source_items.get(path, {}).get("bytes") != item.get("bytes") or source_items.get(path, {}).get("sha256") != item.get("sha256"))
    candidate_missing = sorted(set(expected) - set(candidate_items))
    candidate_extra = sorted(set(candidate_items) - set(expected))
    candidate_links = sorted(item["path"] for item in candidate_records if item["type"] == "symlink")

    renderer = (CANDIDATE / "ui" / "app.js").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src" / "runtime.rs").read_text(encoding="utf-8")
    capability = read_json(CANDIDATE / "capabilities" / "main.json")
    read_offset = renderer.find('const realCaptureText = name === "capture-real"')
    render_offset = renderer.find("state.busy = true; state.error = null; render();")
    old_lookup_after_render = 'if (name === "capture-real") { const input = document.getElementById("real-capture-text")' in renderer
    declared = re.findall(r"#\[tauri::command\]\s*fn\s+(\w+)", runtime)
    handler = re.search(r"generate_handler!\s*\[([^]]+)\]", runtime, re.S)
    handled = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    forbidden = ["Command::new", "std::process::Command", "reqwest", "TcpStream", "UdpSocket", "fetch(", "XMLHttpRequest", "WebSocket", "plugin-shell"]
    forbidden_hits = {item: item in runtime or item in renderer for item in forbidden}

    actual = read_json(CLOSURE / "actual-tauri.json")
    limits = read_json(CLOSURE / "input-limit.json")
    lifecycle = read_json(CLOSURE / "lifecycle-noncontent.json")
    privacy = read_json(CLOSURE / "privacy-taint.json")
    failures = read_json(CLOSURE / "failure-sentinel.json")
    commands = read_json(CLOSURE / "command-inventory.json")
    boundary = read_json(CLOSURE / "write-boundary.json")
    bundle = read_json(CLOSURE / "bundle-identity.json")
    cleanup = read_json(CLOSURE / "cleanup.json") if (CLOSURE / "cleanup.json").is_file() else None
    logs = {
        "real_tests": CLOSURE / "test-logs" / "cargo-test-real-mode.log",
        "bundle_build": CLOSURE / "test-logs" / "cargo-tauri-build-real-mode-positive.log",
    }
    logs_pass = logs["real_tests"].is_file() and "test result: ok. 5 passed" in logs["real_tests"].read_text(encoding="utf-8") and logs["bundle_build"].is_file() and "Finished 1 bundle" in logs["bundle_build"].read_text(encoding="utf-8")
    evidence = text_evidence()
    taint_absent = "P3_133_PRIVATE_TAINT" not in evidence
    actual_observations = actual.get("observations", []) if isinstance(actual, dict) else []
    actual_pass = isinstance(actual, dict) and len(actual_observations) == 6 and all(isinstance(item, dict) and item.get("status") == "PASS" for item in actual_observations)
    post = actual.get("post_run_noncontent", {}) if isinstance(actual, dict) else {}
    counts = post.get("counts", {}) if isinstance(post, dict) else {}
    close_inventory = inventory(CLOSURE, {"FINAL_MANIFEST.json"})
    manifest_path = CLOSURE / "FINAL_MANIFEST.json"
    final_manifest = read_json(manifest_path) if manifest_path.is_file() and not manifest_path.is_symlink() else None
    manifest_pass = isinstance(final_manifest, dict) and final_manifest.get("manifest_kind") == "LIFEOS-P3-133 Closure-2 engineering evidence manifest (non-self)" and final_manifest.get("closure_evidence_inventory") == close_inventory and final_manifest.get("candidate_inventory") == inventory(CANDIDATE)

    checks = [
        check("C2-01_frozen_source_75_regular_hashes", len(expected) == 75 and len(source_items) == 75 and not source_mismatch and not (set(source_items) - set(expected)), {"expected": len(expected), "source_regular": len(source_items), "mismatch": source_mismatch}),
        check("C2-02_candidate_75_regular_no_extra_or_link", len(candidate_items) == 75 and not candidate_missing and not candidate_extra and not candidate_links, {"candidate_regular": len(candidate_items), "missing": candidate_missing, "extra": candidate_extra, "links": candidate_links}),
        check("CL_IR_01_input_is_saved_before_busy_render", read_offset >= 0 and render_offset >= 0 and read_offset < render_offset and not old_lookup_after_render, {"read_offset": read_offset, "busy_render_offset": render_offset, "old_lookup_after_render": old_lookup_after_render}),
        check("C2-03_exact_eleven_ipc_and_closed_capability", declared == EXPECTED_IPC and handled == EXPECTED_IPC and isinstance(capability, dict) and capability.get("permissions") == [] and not any(forbidden_hits.values()) and isinstance(commands, dict) and commands.get("declared_ipc") == EXPECTED_IPC, {"declared": declared, "handled": handled, "forbidden_hits": forbidden_hits}),
        check("C2-04_actual_real_mode_ui_chain", actual_pass and actual.get("real_self_use") == "not run; no authorised real self-use root was accessed" and actual.get("input_body_or_hash_retained") is False and actual.get("screenshots_retained") is False and counts.get("captures") == 3 and counts.get("actions") == 1 and counts.get("open_actions") == 1, {"observations": len(actual_observations), "post_counts": counts}),
        check("C2-05_limits_and_prewrite_rejections", isinstance(limits, dict) and limits.get("maximum_unicode_characters") == 200 and limits.get("maximum_records") == 3 and limits.get("actual_ui", {}).get("attempted_characters") == 201 and limits.get("actual_ui", {}).get("accepted_characters") == 200 and limits.get("actual_ui", {}).get("two_hundred_first_character_blocked_before_invoke") is True and limits.get("runtime_test", {}).get("201_character_request") == "rejected_before_write" and limits.get("quota_ui", {}).get("fourth_write_invocation_available") is False, limits),
        check("C2-06_explicit_lifecycle_today_and_restart", isinstance(lifecycle, dict) and all(lifecycle.get("assertions", {}).values()) and lifecycle.get("post_restart", {}).get("counts", {}).get("understandings") == 0, lifecycle.get("assertions", {})),
        check("C2-07_real_mode_model_disabled_and_zero_taint", isinstance(privacy, dict) and privacy.get("input_body_or_hash_retained") is False and privacy.get("screenshots_retained") is False and privacy.get("model_port") == "disabled_for_real_input" and privacy.get("model_adapter") == "disabled_in_real_mode" and privacy.get("understanding_count") == 0 and taint_absent, {"taint_marker_present": not taint_absent, "privacy": privacy}),
        check("C2-08_failure_sentinel_noncontent_unchanged", isinstance(failures, dict) and failures.get("over_200", {}).get("ui_prevented_201st_character") is True and failures.get("fourth_record", {}).get("quota_control_absent_before_write") is True and failures.get("runtime_fail_closed_regression", {}).get("preexisting_non_sqlite_db_unchanged") is True, failures),
        check("C2-09_actual_bundle_and_offline_regression_logs", logs_pass and isinstance(bundle, dict) and all((CLOSURE / record["path"]).is_file() for record in bundle.get("records", {}).values()), {"logs": {key: str(path.relative_to(CLOSURE)) for key, path in logs.items()}}),
        check("C2-10_write_boundary_and_real_run_prohibited", isinstance(boundary, dict) and boundary.get("protected_assets_modified") is False and boundary.get("real_self_use_access") == "not attempted" and boundary.get("new_ipc") is False and boundary.get("real_self_use_run") == "not run pending new independent review and PM validation", boundary),
        check("C2-11_exact_temp_cleanup_receipt", isinstance(cleanup, dict) and cleanup.get("result") == "PASS" and cleanup.get("after", {}).get("exists") is False and cleanup.get("glob_used") is False and cleanup.get("find_used") is False, cleanup),
        check("C2-12_nonself_final_manifest_covers_all_stable_closure_assets", manifest_pass, {"closure_inventory_count": len(close_inventory), "manifest_present": manifest_path.is_file()}),
    ]
    return {
        "contract": "LIFEOS-P3-133",
        "kind": "Closure-2 default read-only engineering verification",
        "default_mode_writes": False,
        "task_contract_sha256": digest(TASK),
        "acceptance_basis_freeze_sha256": digest(ABF),
        "source_manifest_sha256": digest(P3_132_MANIFEST),
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "runtime_database_access": "not attempted",
        "temporary_root_access": "not attempted",
        "real_self_use_access": "not attempted",
        "independent_review": "not run by engineering agent",
        "real_self_use_run": "not run pending a new isolated independent review and PM validation",
    }


def main() -> int:
    try:
        result = verify()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
