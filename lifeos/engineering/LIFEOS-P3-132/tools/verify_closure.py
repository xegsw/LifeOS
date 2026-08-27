#!/usr/bin/env python3
"""Fail-closed structural and row-level verifier for LIFEOS-P3-132 evidence."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
PROJECT = ROOT.parent
P3_131_MANIFEST = PROJECT / "LIFEOS-P3-131" / "evidence" / "FINAL_MANIFEST.json"
COMMANDS = [
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
    excluded = excluded or set()
    result = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded or any(rel.startswith(prefix + "/") for prefix in excluded):
            continue
        result.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path)})
    return result


def check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"name": name, "passed": passed, "detail": detail}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def main() -> int:
    checks: list[dict[str, object]] = []
    old_manifest = load(P3_131_MANIFEST)
    expected = {
        Path(item["path"]).relative_to("lifeos/engineering/LIFEOS-P3-131/candidate").as_posix(): item
        for item in old_manifest["candidate_inventory"]
    }
    current = {item["path"]: item for item in inventory(CANDIDATE, {"target"})}
    inherited = []
    for rel, item in sorted(expected.items()):
        actual = current.get(rel)
        inherited.append({
            "path": rel,
            "source_bytes": item["bytes"],
            "source_sha256": item["sha256"],
            "candidate_bytes": actual["bytes"] if actual else None,
            "candidate_sha256": actual["sha256"] if actual else None,
            "status": "unchanged" if actual and actual["sha256"] == item["sha256"] else "modified" if actual else "missing",
        })
    extras = sorted(set(current) - set(expected))
    checks.append(check("source_exact_file_set", len(expected) == 75 and not extras and len(current) == 75, {
        "expected_count": len(expected), "candidate_count": len(current), "extra_paths": extras,
    }))

    runtime = (CANDIDATE / "src/runtime.rs").read_text()
    ipc_source = runtime
    declared = re.findall(r"#\[tauri::command\]\s*(?:pub\s+)?fn\s+(\w+)", ipc_source)
    handler_match = re.search(r"generate_handler!\s*\[([^]]+)\]", ipc_source, re.S)
    handled = re.findall(r"\b([a-z_]+)\b", handler_match.group(1)) if handler_match else []
    capability = load(CANDIDATE / "capabilities/main.json")
    checks.append(check("strict_eleven_ipc", declared == COMMANDS and handled == COMMANDS and capability.get("permissions") == [], {
        "declared": declared, "handled": handled, "expected": COMMANDS, "capability_permissions": capability.get("permissions"),
    }))

    renderer = (CANDIDATE / "ui/app.js").read_text()
    forbidden_patterns = {
        "network_api": r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(",
        "node_filesystem": r"(?:from\s+[\"']node:fs|require\s*\(\s*[\"']fs[\"'])",
        "tauri_fs_plugin": r"@tauri-apps/plugin-fs",
        "direct_sql": r"\b(?:SELECT|INSERT|UPDATE|DELETE)\s+\w+",
    }
    findings = {name: re.findall(pattern, renderer) for name, pattern in forbidden_patterns.items()}
    checks.append(check("renderer_semantic_boundary", not any(findings.values()) and "invoke(" in renderer, findings))
    checks.append(check("offline_adapter_contract", all(token in runtime for token in ["trait ModelPort", "OfflineSyntheticModelAdapter", "offline_synthetic_model:p3-132-v1"]) and "Offline synthetic adapter" in renderer, {
        "model_port": "trait ModelPort" in runtime,
        "adapter": "OfflineSyntheticModelAdapter" in runtime,
        "visible_label": "Offline synthetic adapter" in renderer,
    }))

    runs = {
        "confirm": load(EVIDENCE / "actual-runs/confirm.json"),
        "edit_confirm": load(EVIDENCE / "actual-runs/edit-confirm.json"),
        "reject": load(EVIDENCE / "actual-runs/reject.json"),
        "correct": load(EVIDENCE / "actual-runs/correct.json"),
        "ignore_no_auto_action": load(EVIDENCE / "actual-runs/ignore-no-auto-action.json"),
        "ignore_and_explicit_action": load(EVIDENCE / "actual-runs/ignore-and-explicit-action.json"),
        "bound_confirm": load(EVIDENCE / "actual-runs/bound-confirm.json"),
    }
    feedback_cases = ["confirm", "edit_confirm", "reject", "correct", "ignore_no_auto_action"]
    expected_decisions = {
        "confirm": "confirm",
        "edit_confirm": "edit_confirm",
        "reject": "reject",
        "correct": "correct",
        "ignore_no_auto_action": "ignore",
    }
    feedback_summary = {}
    decision_ok = True
    for case_name in feedback_cases:
        run = runs[case_name]
        feedback = [row for row in run["rows"]["feedback"] if row["target_kind"] == "understanding"]
        actions = run["rows"]["actions"]
        feedback_summary[case_name] = {"feedback": feedback, "action_count": len(actions), "db_sha256": run["database"]["sha256"]}
        decision_ok = decision_ok and len(feedback) == 1 and feedback[0]["decision"] == expected_decisions[case_name] and not actions
    checks.append(check("five_actual_feedback_cases_no_auto_action", decision_ok, feedback_summary))

    explicit = runs["ignore_and_explicit_action"]
    explicit_actions = explicit["rows"]["actions"]
    explicit_feedback = explicit["rows"]["feedback"]
    checks.append(check("explicit_candidate_action_only", len(explicit_actions) == 1 and explicit_actions[0]["action_state"] == "open" and any(row["target_kind"] == "candidate_action" and row["decision"] == "accept" for row in explicit_feedback), {
        "actions": explicit_actions,
        "feedback": explicit_feedback,
    }))
    checks.append(check("understanding_provenance", all(len(runs[name]["rows"]["understandings"]) == 1 and len(runs[name]["rows"]["derivations"]) >= 2 for name in feedback_cases), {
        name: {"understandings": len(runs[name]["rows"]["understandings"]), "derivations": len(runs[name]["rows"]["derivations"])} for name in feedback_cases
    }))

    screenshot_names = [
        "confirm-final.jpeg", "edit-confirm-final.jpeg", "reject-final.jpeg", "correct-final.jpeg",
        "ignore-no-auto-final.jpeg", "explicit-action-focus-final.jpeg", "request-local-removal-final.jpeg", "reopen-focus.jpeg",
    ]
    screenshot_root = EVIDENCE / "actual-runs/screenshots"
    screenshots = {name: {"exists": (screenshot_root / name).is_file(), "sha256": sha(screenshot_root / name) if (screenshot_root / name).is_file() else None} for name in screenshot_names}
    checks.append(check("visible_actual_tauri_states_retained", all(item["exists"] for item in screenshots.values()), screenshots))

    identity_binary = EVIDENCE / "bundle-identities/confirm/lifeos-p3-132"
    identity_info = EVIDENCE / "bundle-identities/confirm/Info.plist"
    checks.append(check("current_bundle_identity_retained", identity_binary.is_file() and identity_info.is_file(), {
        "binary": {"path": str(identity_binary.relative_to(ROOT)), "sha256": sha(identity_binary) if identity_binary.is_file() else None},
        "info_plist": {"path": str(identity_info.relative_to(ROOT)), "sha256": sha(identity_info) if identity_info.is_file() else None},
        "bound_run": runs["bound_confirm"]["runtime_root"],
    }))

    closure_ui = load(EVIDENCE / "actual-runs/closure-ui-observations.json")
    cl01_before = load(EVIDENCE / "actual-runs/closure-cl01-before-second-reopen.json")
    cl01_after = load(EVIDENCE / "actual-runs/closure-cl01-after-second-reopen.json")
    cl01_rows = cl01_before["rows"]
    cl01_counts = cl01_before["row_counts"]
    cl01_visible = closure_ui["cl01_insufficient_reopen"]
    cl01_screenshot = EVIDENCE / "actual-runs" / cl01_visible["screenshot"]
    cl01_pass = (
        cl01_before["database"]["sha256"] == cl01_after["database"]["sha256"]
        and cl01_counts == {"captures": 1, "projects": 1, "capture_project_links": 0, "derivations": 0, "understandings": 0, "feedback": 0, "candidate_actions": 0, "actions": 0, "action_results": 0, "audit": 1}
        and cl01_rows["captures"][0]["content"] == "LifeOS Context Recovery 合成记录。"
        and cl01_visible["visible_link_state"] == "Project link: none · evidence insufficient"
        and cl01_visible["forbidden_visible_link"] == "typed link: candidate"
        and cl01_visible["restart_verified"] is True
        and cl01_screenshot.is_file()
        and sha(cl01_screenshot) == cl01_visible["screenshot_sha256"]
    )
    checks.append(check("cl01_actual_insufficient_identity_and_reopen", cl01_pass, {
        "before_sha256": cl01_before["database"]["sha256"],
        "after_sha256": cl01_after["database"]["sha256"],
        "row_counts": cl01_counts,
        "capture": cl01_rows["captures"],
        "visible": cl01_visible,
    }))

    storage_mapping = "confirmed_at_ms INTEGER GENERATED ALWAYS AS (created_at_ms) STORED" in runtime and "ORDER BY confirmed_at_ms,id" in runtime
    checks.append(check("cl02_confirmed_at_storage_mapping", storage_mapping, {
        "storage": "confirmed_at_ms generated from action creation transaction",
        "today_order": "confirmed_at_ms ASC, id ASC",
    }))

    fixture = load(EVIDENCE / "actual-runs/closure-cl02-fixture.json")
    cl02_states = closure_ui["cl02_multi_open_actions"]["actual_states"]
    cl02_runs = [load(EVIDENCE / "actual-runs" / state["sqlite_snapshot"]) for state in cl02_states]
    cl02_actions = cl02_runs[0]["rows"]["actions"]
    sorted_actions = [row["id"] for row in sorted(cl02_actions, key=lambda row: (row["confirmed_at_ms"], row["id"]))]
    cl02_hashes = [run["database"]["sha256"] for run in cl02_runs]
    cl02_screenshots = []
    for state in cl02_states:
        screenshot = EVIDENCE / "actual-runs" / state["screenshot"]
        cl02_screenshots.append({"phase": state["phase"], "path": str(screenshot.relative_to(ROOT)), "exists": screenshot.is_file(), "sha256": sha(screenshot) if screenshot.is_file() else None})
    cl02_pass = (
        fixture["insert_order"] == [row["id"] for row in cl02_actions]
        and fixture["expected_open_order"] == sorted_actions
        and fixture["expected_todays_focus"] == sorted_actions[0]
        and len(cl02_actions) == 3
        and all(row["action_state"] == "open" for row in cl02_actions)
        and [row["confirmed_at_ms"] for row in cl02_actions] == [7002, 7000, 7000]
        and len(set(cl02_hashes)) == 1
        and closure_ui["cl02_multi_open_actions"]["expected_focus"] == sorted_actions[0]
        and all(item["exists"] and item["sha256"] == state["screenshot_sha256"] for item, state in zip(cl02_screenshots, cl02_states))
    )
    checks.append(check("cl02_actual_multi_open_stable_focus_refresh_reopen", cl02_pass, {
        "fixture": fixture,
        "database_sha256_by_phase": dict(zip([state["phase"] for state in cl02_states], cl02_hashes)),
        "insertion_order": [row["id"] for row in cl02_actions],
        "sorted_order": sorted_actions,
        "screenshots": cl02_screenshots,
    }))

    closure_bundles = [
        EVIDENCE / "bundle-identities/closure-cl01/lifeos-p3-132",
        EVIDENCE / "bundle-identities/closure-cl01/Info.plist",
        EVIDENCE / "bundle-identities/closure-cl02/lifeos-p3-132",
        EVIDENCE / "bundle-identities/closure-cl02/Info.plist",
    ]
    checks.append(check("closure_actual_bundle_identity_retained_per_run", all(path.is_file() for path in closure_bundles), {
        str(path.relative_to(ROOT)): sha(path) if path.is_file() else None for path in closure_bundles
    }))

    closure_cleanup = load(EVIDENCE / "closure-cleanup-final.json")
    checks.append(check("closure_exact_task_temp_cleanup", closure_cleanup["before"]["exists"] is True and closure_cleanup["before"]["regular_file_count"] > 0 and closure_cleanup["after"] == {"exists": False, "verification": "exact absolute path check after task-authorized cleanup"}, closure_cleanup))

    result = {
        "contract": "LIFEOS-P3-132",
        "verifier": "verify_closure.py",
        "candidate_source_lineage": inherited,
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "warning": "Verifier consumes structured rows and hashes; it does not infer PASS from Markdown text.",
    }
    output = EVIDENCE / "verification.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    lineage = {
        "contract": "LIFEOS-P3-132",
        "source_task": "LIFEOS-P3-131",
        "source_manifest": str(P3_131_MANIFEST),
        "source_manifest_sha256": sha(P3_131_MANIFEST),
        "candidate_inventory_count": len(current),
        "candidate_source_lineage": inherited,
        "extra_candidate_paths": extras,
        "verification": "P3-131 manifest path, byte count and SHA-256 checked before copy; current source state is recorded without rewriting P3-131.",
    }
    (EVIDENCE / "source-lineage.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "check_count": len(checks)}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
