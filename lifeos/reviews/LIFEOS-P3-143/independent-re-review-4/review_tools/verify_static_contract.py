#!/usr/bin/env python3
"""Review-owned static and mutation checks for the immutable P3-143 candidate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding",
    "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings",
    "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled",
    "upsert_durable_memory", "update_current_state", "resolve_request_context",
    "get_context_disclosure_receipt",
]
EXPECTED_CLOUD = ["openai", "anthropic", "google_gemini", "deepseek", "kimi", "openrouter", "cloud_openai_compatible", "cloud_custom"]
EXPECTED_LOCAL = ["ollama", "lm_studio", "local_openai_compatible", "local_custom"]


def between(source: str, start: str, end: str) -> str:
    return source[source.index(start): source.index(end, source.index(start))]


def check(runtime: str, deepseek: str, app: str, build: str) -> list[str]:
    errors: list[str] = []
    ipc_match = re.search(r"const IPC: \[&str; 20\] = \[(.*?)\];", runtime, re.S)
    ipc = re.findall(r'"([^"]+)"', ipc_match.group(1)) if ipc_match else []
    if ipc != EXPECTED_IPC or len(set(ipc)) != 20:
        errors.append("exact_20_ipc_drift")
    registry = between(runtime, "fn provider_registry()", "fn cloud_capabilities")
    cloud = re.findall(r'\("([^"]+)", "[^"]+"\)', re.search(r"let cloud = \[(.*?)\];", registry, re.S).group(1))
    local = re.findall(r'\("([^"]+)", "[^"]+"\)', re.search(r"let local = \[(.*?)\];", registry, re.S).group(1))
    if cloud != EXPECTED_CLOUD:
        errors.append("cloud8_registry_drift")
    if local != EXPECTED_LOCAL:
        errors.append("local4_registry_drift")
    required_network = [
        'pub const AUTHORITY: &str = "https://api.deepseek.com";',
        '.arg("--proto-redir")', '.arg("=https")', '.arg("--max-redirs")', '.arg("0")',
        '.arg("--noproxy")', '.arg("*")', '.arg("--proxy")', '.arg("")', '.env_clear()',
    ]
    if any(value not in deepseek for value in required_network):
        errors.append("deepseek_authority_proxy_redirect_guard_drift")
    save = between(runtime, "fn save_ai_provider_credential", "fn test_ai_provider_connection")
    test = between(runtime, "fn test_ai_provider_connection", "fn apply_tested_model_directory")
    enable = between(runtime, "fn set_ai_provider_enabled", "fn unavailable")
    send = between(runtime, "fn assemble_global_ai_context", "fn get_evidence_backed_understanding")
    if "deepseek::real_models" in save or "deepseek::real_canary" in save:
        errors.append("save_action_implicitly_networked")
    if 'request.user_action != "user_test"' not in test or "deepseek::real_models" not in test:
        errors.append("test_action_not_explicit")
    if '"select_model" if request.enabled.is_none()' not in enable or '"set_enabled" if request.model_id.is_none()' not in enable:
        errors.append("selection_enablement_not_separated")
    if 'request.operation != "send_fixed_canary"' not in send or "deepseek::real_canary" not in send:
        errors.append("send_action_not_explicit")
    if 'input.value = ""' not in app:
        errors.append("ui_secret_clear_missing")
    required_root = [
        '"independent-review"', 'LIFEOS_P3_143_REVIEW_RUN_ID', 'valid_review_run_id',
        'format!("{REVIEW_PREFIX}{run_id}")', 'root profile must be engineering or independent-review',
    ]
    if any(value not in build for value in required_root):
        errors.append("build_profile_root_guard_drift")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = Path(args.candidate)
    runtime = (candidate / "src/runtime.rs").read_text(encoding="utf-8")
    deepseek = (candidate / "src/deepseek.rs").read_text(encoding="utf-8")
    app = (candidate / "ui/app.js").read_text(encoding="utf-8")
    build = (candidate / "build.rs").read_text(encoding="utf-8")
    mutations = {
        "semantic_duplicate_ipc": check(runtime.replace('"get_today"', '"capture_record"', 1), deepseek, app, build),
        "semantic_wrong_deepseek_authority": check(runtime, deepseek.replace("https://api.deepseek.com", "https://api.deepseek.com.evil.invalid", 1), app, build),
    }
    document = {
        "schema": "lifeos.p3-143.independent-rereview4.static-contract.v1",
        "mode": "synthetic_offline",
        "candidate": str(candidate),
        "baseline_errors": check(runtime, deepseek, app, build),
        "mutation_errors": mutations,
        "mutation_detected": {key: bool(value) for key, value in mutations.items()},
        "network_requests": 0,
    }
    document["result"] = "PASS" if not document["baseline_errors"] and all(document["mutation_detected"].values()) else "FAIL"
    Path(args.output).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": document["result"], "mutations_detected": sum(document["mutation_detected"].values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
