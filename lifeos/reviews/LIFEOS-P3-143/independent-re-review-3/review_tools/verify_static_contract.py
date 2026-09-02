#!/usr/bin/env python3
"""Review-owned offline checks and in-memory mutations for P3-143 contract drift."""

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


def section(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def check(runtime: str, deepseek: str, app: str) -> list[str]:
    errors: list[str] = []
    ipc_block = re.search(r"const IPC: \[&str; 20\] = \[(.*?)\];", runtime, re.S)
    values = re.findall(r'"([^"]+)"', ipc_block.group(1)) if ipc_block else []
    if values != EXPECTED_IPC or len(values) != 20 or len(set(values)) != 20:
        errors.append("exact_20_ipc_drift")
    registry = section(runtime, "fn provider_registry()", "fn cloud_capabilities")
    cloud = re.findall(r'\("([^"]+)", "[^"]+"\)', re.search(r"let cloud = \[(.*?)\];", registry, re.S).group(1))
    local = re.findall(r'\("([^"]+)", "[^"]+"\)', re.search(r"let local = \[(.*?)\];", registry, re.S).group(1))
    if cloud != EXPECTED_CLOUD or len(cloud) != 8:
        errors.append("cloud8_registry_drift")
    if local != EXPECTED_LOCAL or len(local) != 4:
        errors.append("local4_registry_drift")
    if 'pub const AUTHORITY: &str = "https://api.deepseek.com";' not in deepseek:
        errors.append("deepseek_authority_drift")
    for required in ['.arg("--max-redirs")', '.arg("0")', '.arg("--noproxy")', '.arg("*")', '.arg("--proxy")', '.arg("")']:
        if required not in deepseek:
            errors.append("network_authority_or_proxy_guard_missing")
            break
    save = section(runtime, "fn save_ai_provider_credential", "fn test_ai_provider_connection")
    test = section(runtime, "fn test_ai_provider_connection", "fn set_ai_provider_enabled")
    enabled = section(runtime, "fn set_ai_provider_enabled", "fn unavailable")
    canary = section(runtime, "fn assemble_global_ai_context", "fn get_evidence_backed_understanding")
    if "deepseek::real_models" in save or "deepseek::real_canary" in save:
        errors.append("credential_save_implicitly_networked")
    if "match request.operation.as_str()" not in save or '"store" =>' not in save or '"delete" if request.api_key.is_none()' not in save:
        errors.append("credential_action_separation_missing")
    if 'request.user_action != "user_test"' not in test or "deepseek::real_models" not in test:
        errors.append("explicit_test_action_missing")
    if '"select_model" if request.enabled.is_none()' not in enabled or '"set_enabled" if request.model_id.is_none()' not in enabled:
        errors.append("select_enable_separation_missing")
    if 'request.operation != "send_fixed_canary"' not in canary or "deepseek::real_canary" not in canary:
        errors.append("explicit_canary_action_missing")
    if 'input.value = ""' not in app or 'operation: "store"' not in app or 'operation: "send_fixed_canary"' not in app:
        errors.append("ui_credential_or_action_boundary_missing")
    production_runtime = runtime.split("#[cfg(test)]", 1)[0]
    if 'const TASK_ROOT: &str = "/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1"' in production_runtime:
        errors.append("runtime_literal_root_bypass")
    for required in ["compiled_root_authority", "task_marker_missing", "verify_runtime_child", "database_path_rejected"]:
        if required not in production_runtime:
            errors.append("root_authority_guard_missing")
            break
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
    baseline_errors = check(runtime, deepseek, app)
    mutations = {
        "remove_missing_marker_rejection": check(runtime.replace("task_marker_missing", "removed_marker_guard", 1), deepseek, app),
        "duplicate_ipc": check(runtime.replace('"get_today"', '"capture_record"', 1), deepseek, app),
        "evil_authority": check(runtime, deepseek.replace("https://api.deepseek.com", "https://api.deepseek.com.evil.invalid", 1), app),
        "remove_noproxy": check(runtime, deepseek.replace('.arg("--noproxy")', '.arg("removed-noproxy")', 1), app),
    }
    mutation_detected = {name: bool(errors) for name, errors in mutations.items()}
    output = {
        "schema": "lifeos.p3-143.independent-rereview-3.static-contract.v1",
        "candidate": str(candidate),
        "baseline_errors": baseline_errors,
        "mutations": mutations,
        "mutation_detected": mutation_detected,
        "network": "not_executed",
        "result": "PASS" if not baseline_errors and all(mutation_detected.values()) else "FAIL",
    }
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": output["result"], "baseline_errors": len(baseline_errors), "mutations_detected": sum(mutation_detected.values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
