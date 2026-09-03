#!/usr/bin/env python3
"""Review-owned, read-only source-contract checks for LIFEOS-P3-145 Closure-1."""
import json
import re
import sys
from pathlib import Path

EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context",
    "get_evidence_backed_understanding", "decide_understanding_feedback",
    "get_ai_provider_settings", "save_ai_provider_settings", "save_ai_provider_credential",
    "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory",
    "update_current_state", "resolve_request_context", "get_context_disclosure_receipt",
]

root = Path(sys.argv[1])
runtime = (root / "src/runtime.rs").read_text()
build = (root / "build.rs").read_text()

def ipc_contract(text: str) -> bool:
    block = re.search(r"const IPC: \[&str; (\d+)\] = \[(.*?)\];", text, re.S)
    if not block:
        return False
    declared = int(block.group(1))
    observed = re.findall(r'"([a-z_]+)"', block.group(2))
    handler = re.search(r"generate_handler!\[(.*?)\]\)", text, re.S)
    if not handler:
        return False
    handler_names = re.findall(r"\b([a-z_]+)\b", handler.group(1))
    return (declared == 20 and observed == EXPECTED_IPC and
            handler_names == EXPECTED_IPC)

def guard_contract(text: str) -> bool:
    return ("fn contains_medical_risk" in text and
            "if domain == HEALTH && contains_medical_risk(&text) {" in text and
            "health_medical_boundary_rejected" in text)

def feedback_contract(text: str) -> bool:
    return ("fn feedback_target_status" in text and
            'if current_status == "pending"' in text and
            "understanding_feedback_consumed" in text)

def review_root_contract(text: str) -> bool:
    return ('const REVIEW_BASENAME: &str = "lifeos-p3-145-independent-review-v1";' in text and
            '"lifeos.p3-145.independent-review-root.v1"' in text and
            '"independent-review uses the frozen v1 root and rejects dynamic review run ids"' in text and
            '"synthetic".to_owned()' in text)

checks = {
    "exact_20_ipc_and_handler": ipc_contract(runtime),
    "non_medical_health_guard": guard_contract(runtime),
    "feedback_single_use_guard": feedback_contract(runtime),
    "compiled_review_root_and_synthetic_mode": review_root_contract(build),
}
mutations = {
    "remove_one_ipc": not ipc_contract(runtime.replace('const IPC: [&str; 20]', 'const IPC: [&str; 19]', 1)),
    "remove_health_guard": not guard_contract(runtime.replace('if domain == HEALTH && contains_medical_risk(&text) {', 'if false {', 1)),
    "remove_feedback_pending_gate": not feedback_contract(runtime.replace('if current_status == "pending"', 'if false', 1)),
    "change_compiled_review_root": not review_root_contract(build.replace('lifeos-p3-145-independent-review-v1', 'wrong-review-root', 1)),
}
result = {
    "runner": "closure-1/review_static_contract.py",
    "candidate_root": str(root),
    "checks": checks,
    "mutations_rejected": mutations,
    "pass": all(checks.values()) and all(mutations.values()),
}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
sys.exit(0 if result["pass"] else 1)
