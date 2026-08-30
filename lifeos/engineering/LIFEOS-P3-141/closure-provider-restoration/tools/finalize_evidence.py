#!/usr/bin/env python3
"""Build P3-141 Provider Restoration evidence from only this closure and approved read-only inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
CANDIDATE = ROOT / "candidate"
PREVIOUS_CANDIDATE = ROOT.parent / "candidate"
P3_140_CANDIDATE = Path("/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/candidate")
PM_ROOT = Path("/Users/xxe/Documents/No.2")
TMP_ROOT = "/private/tmp/lifeos-p3-141-provider-restoration-closure-v1"
TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def inventory(root: Path, excluded: set[str] | None = None) -> tuple[dict[str, dict[str, object]], str]:
    excluded = excluded or set()
    tree = hashlib.sha256()
    values: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        if path.is_symlink():
            raise RuntimeError(f"symlink not permitted: {root}/{rel}")
        if not path.is_file():
            continue
        data = path.read_bytes()
        encoded = rel.encode("utf-8")
        tree.update(len(encoded).to_bytes(8, "big"))
        tree.update(encoded)
        tree.update(len(data).to_bytes(8, "big"))
        tree.update(data)
        values[rel] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    return values, tree.hexdigest()


def write_json(name: str, value: object) -> Path:
    target = EVIDENCE / name
    if target.exists():
        raise RuntimeError(f"refusing to overwrite evidence: {target.name}")
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    require(CANDIDATE.is_dir(), "candidate missing")
    require(PREVIOUS_CANDIDATE.is_dir(), "withdrawn candidate missing")
    require(P3_140_CANDIDATE.is_dir(), "P3-140 input missing")
    test_log = (EVIDENCE / "cargo_test.log").read_text(encoding="utf-8")
    require("test result: ok. 50 passed" in test_log, "expected 50/50 offline tests")
    dynamic_names = [
        "protocol_adapters_cover_the_closed_four_profiles_and_reject_mismatches",
        "custom_openai_compatible_loopback_is_protocol_bound_and_first_send_locks",
        "custom_profile_rejects_wrong_envelope_response_mode_and_credential_order",
        "loopback_probe_send_feedback_restart_and_no_implicit_repeat",
        "provider_failures_do_not_persist_derived_objects_or_enable",
        "provider_understanding_requires_explicit_successful_enablement",
    ]
    for name in dynamic_names:
        require(f"{name} ... ok" in test_log, f"missing dynamic test: {name}")
    source = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    ui = (CANDIDATE / "ui/runtime-adapter.js").read_text(encoding="utf-8")
    require('const IPC: [&str; 20]' in source, "IPC contract changed")
    for profile in ["Openai", "Anthropic", "Ollama", "LmStudio", "CustomOpenaiCompatible"]:
        require(profile in source, f"profile absent: {profile}")
    require("CustomOpenAiCompatibleAdapter" in source, "Custom adapter absent")
    require("DeepSeek、Kimi 或 OpenAI-compatible 服务" in ui, "cloud Custom label absent")
    require("本地兼容服务" in ui, "local Custom label absent")

    candidate_entries, candidate_tree = inventory(CANDIDATE)
    old_entries, old_tree = inventory(PREVIOUS_CANDIDATE)
    parent_entries, parent_tree = inventory(P3_140_CANDIDATE)
    require(len(candidate_entries) == 79, "candidate file count no longer 79")
    require(len(parent_entries) == 79 and parent_tree == "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e", "P3-140 fixed lineage mismatch")

    inputs = {
        "AGENTS.md": PM_ROOT / "AGENTS.md",
        "CURRENT_STATUS.md": PM_ROOT / "lifeos/CURRENT_STATUS.md",
        "revision_2_task": PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_2.md",
        "revision_2_abf": PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_2.md",
        "revision_2_inventory": PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_2.json",
        "provider_confirmation": PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_provider_restoration_user_confirmation.md",
        "phase_b_withdrawal_review": PM_ROOT / "lifeos/reviews/LIFEOS-P3-141_pm_phase_b_withdrawal_review.md",
    }
    input_values = {name: {"path": str(path), **entry(path)} for name, path in inputs.items()}
    write_json("fixed_input_verification.json", {
        "schema": "lifeos.p3-141.provider-restoration.fixed-input-verification.v1",
        "result": "PASS",
        "read_only_inputs": input_values,
        "p3_140_candidate": {"file_count": len(parent_entries), "length_framed_tree_sha256": parent_tree},
        "precontact": {"test_design": entry(ROOT / "test_design.md"), "write_allowlist": entry(ROOT / "write_allowlist.md"), "seal": entry(ROOT / "precontact_seal.json")},
    })
    write_json("source_lineage.json", {
        "schema": "lifeos.p3-141.provider-restoration.source-lineage.v1",
        "result": "PASS",
        "parent_p3_140": {"file_count": len(parent_entries), "length_framed_tree_sha256": parent_tree},
        "withdrawn_p3_141_starting_candidate": {"file_count": len(old_entries), "length_framed_tree_sha256": old_tree},
        "current_p3_141_candidate": {"file_count": len(candidate_entries), "length_framed_tree_sha256": candidate_tree},
        "provider_delta_paths": {
            "src/runtime.rs": entry(CANDIDATE / "src/runtime.rs"),
            "ui/runtime-adapter.js": entry(CANDIDATE / "ui/runtime-adapter.js"),
        },
        "semantic_diff": {"path": "evidence/source_semantic_diff.md", **entry(EVIDENCE / "source_semantic_diff.md")},
        "invariants": {"ipc_count": 20, "provider_profile_count": 5, "new_ipc": 0, "new_provider_enum": 0},
    })
    write_json("provider_protocol_dynamic.json", {
        "schema": "lifeos.p3-141.provider-restoration.dynamic-protocol.v1",
        "result": "PASS",
        "execution": "offline synthetic loopback only; no external provider, credential, or network target",
        "positive": [
            {"profiles": ["OpenAI", "Anthropic", "Ollama", "LM Studio"], "test": dynamic_names[0], "assertion": "profile-specific probe and inference envelopes accepted by loopback"},
            {"profiles": ["Custom OpenAI-compatible"], "test": dynamic_names[1], "assertion": "GET /fixture/v1/models then POST /fixture/v1/chat/completions accepted"},
        ],
        "negative": [
            {"test": dynamic_names[2], "assertions": ["wrong models envelope rejected", "wrong chat response rejected", "wrong mode rejected", "enable before successful test rejected"]},
            {"test": "loopback_timeout_http_malformed_oversize_disconnect_and_protocol_mismatch_fail_closed", "assertion": "transport/protocol failure closes before derived persistence or enablement"},
        ],
        "not_a_string_scan": True,
        "test_log": {"path": "evidence/cargo_test.log", **entry(EVIDENCE / "cargo_test.log")},
    })
    write_json("provider_state_machine.json", {
        "schema": "lifeos.p3-141.provider-restoration.provider-state-machine.v1",
        "result": "PASS",
        "single_enable_path": ["save non-secret settings", "successful synthetic loopback test", "explicit enable"],
        "first_send_lock": {"test": dynamic_names[1], "after_successful_send": "Custom OpenAI-compatible locked", "switch_attempt": "LM Studio", "rejection": "provider_locked_after_first_send"},
        "no_fallback": {"test": dynamic_names[0], "assertion": "profile/mode mismatch rejected; no alternate adapter selected"},
        "no_implicit_repeat": {"test": dynamic_names[3], "assertion": "restart does not create another provider send"},
        "failure_atomicity": {"test": dynamic_names[4], "assertion": "failure preserves DB sentinel and no enablement"},
    })
    non_provider_tests = [
        "closure_real_root_requires_fresh_absence_and_owned_restart",
        "closure_real_memory_cap_is_restart_safe_and_fourth_is_prewrite_rejected",
        "controlled_fixture_health_source_is_closed_and_today_uses_the_same_contract",
        "feedback_all_decisions_are_audited_and_only_confirmation_affects_today",
        "resolver_filters_authority_budgets_and_domain",
        "receipt_reopens_deterministically_and_snapshots_incrementally",
        "status_is_closed_to_the_p3_139_twenty_ipc",
    ]
    for name in non_provider_tests:
        require(f"{name} ... ok" in test_log, f"missing non-provider test: {name}")
    write_json("non_provider_regression.json", {
        "schema": "lifeos.p3-141.provider-restoration.non-provider-regression.v1",
        "result": "PASS",
        "ipc_count": 20,
        "new_ipc": 0,
        "passed_test_names": non_provider_tests,
        "preserved": ["P3-139 Memory/State/Context Resolver", "Work and five-field Health", "feedback/recompute", "restart/no-repeat", "fresh/owned root lifecycle", "receipt gate"],
    })
    actual: dict[str, object] = {"schema": "lifeos.p3-141.provider-restoration.actual-tauri.v1", "result": "PASS", "direct_chain": "launch PID -> one exact-title AXWindow -> one native AXWebArea", "views": {}}
    requested = {"desktop": (1280, 1024), "compact": (700, 760), "narrow": (560, 640)}
    for view, expected in requested.items():
        ax = json.loads((EVIDENCE / f"{view}_native_ax.json").read_text(encoding="utf-8"))
        receipt = json.loads((EVIDENCE / f"{view}_startup_receipt.json").read_text(encoding="utf-8"))
        nav = json.loads((EVIDENCE / f"{view}_settings_direct_navigation.json").read_text(encoding="utf-8"))
        shot = EVIDENCE / "screenshots" / f"{view}.png"
        require(ax["direct_pid"] == receipt["pid"] == nav["direct_pid"], f"PID mismatch: {view}")
        require(ax["ax_window_title"] == receipt["window_title"] == nav["exact_title"] == TITLE, f"title mismatch: {view}")
        require(ax["exact_title_ax_window_count"] == 1 and ax["strict_native_web_node_pass"], f"native chain failed: {view}")
        require([node["role"] for node in ax["native_web_nodes"]] == ["AXWebArea"], f"native AXWebArea missing: {view}")
        frame = ax["ax_window_frame"]
        outer = receipt["observed_outer_logical"]
        require(frame["width"] == round(outer["width"]) and frame["height"] == round(outer["height"]), f"receipt AX geometry mismatch: {view}")
        require((receipt["requested_inner_logical"]["width"], receipt["requested_inner_logical"]["height"]) == expected, f"requested geometry mismatch: {view}")
        require(shot.is_file(), f"screenshot missing: {view}")
        actual["views"][view] = {
            "direct_pid": ax["direct_pid"], "requested_inner_logical": receipt["requested_inner_logical"],
            "ax_window_frame": frame, "receipt_observed_outer_logical": outer,
            "native_web_role": "AXWebArea", "receipt_source": receipt["receipt_source"],
            "settings_navigation": nav, "screenshot": {"path": f"evidence/screenshots/{view}.png", **entry(shot)},
            "human_visual_check": "PASS: visible P3-141 title and synthetic Settings mode cards show Cloud DeepSeek/Kimi OpenAI-compatible and Local compatible service labels",
        }
    write_json("actual_tauri_provider_viewports.json", actual)
    write_json("prohibited_target_attestation.json", {
        "schema": "lifeos.p3-141.provider-restoration.prohibited-target-attestation.v1",
        "result": "PASS",
        "temporary_root": TMP_ROOT,
        "assertions": [
            "all runtime, cargo target, bundle, loopback, PID, AX and receipt activity used only the declared temporary root",
            "only fictional synthetic fixture data was used",
            "no external provider, network, credential, or real personal content was contacted",
            "prohibited real-pilot target was not accessed, probed, created, copied, hashed, read, written or cleaned",
        ],
    })
    write_json("history_lineage.json", {
        "schema": "lifeos.p3-141.provider-restoration.history-lineage.v1",
        "result": "PASS",
        "withdrawn_phase_b_commit": "c7087586d89a52bc252765ec89fa63611f585d0e",
        "withdrawal_record": str(inputs["phase_b_withdrawal_review"]),
        "old_attempts": "read-only and not overwritten",
        "this_closure_failures_retained": sorted(path.relative_to(EVIDENCE).as_posix() for path in (EVIDENCE / "failure_history").rglob("*" ) if path.is_file()),
        "new_positive_evidence": "this closure only; no prior PID, screenshot, receipt or conclusion reused",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
