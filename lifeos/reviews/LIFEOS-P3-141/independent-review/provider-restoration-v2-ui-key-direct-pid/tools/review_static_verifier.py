#!/usr/bin/env python3
"""Independent, source-only verifier for the frozen P3-141 v2 candidate."""
import hashlib
import json
import re
import sys
from pathlib import Path

EXPECTED_KEY = "p3-141-synthetic-capture-001"
EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding",
    "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings",
    "set_ai_provider_session_credential", "test_ai_provider_connection", "set_ai_provider_enabled",
    "upsert_durable_memory", "update_current_state", "resolve_request_context",
    "get_context_disclosure_receipt",
]
EXPECTED_PROFILES = ["Openai", "Anthropic", "Ollama", "LmStudio", "CustomOpenaiCompatible"]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> tuple[int, str]:
    """Match the frozen Phase-C build.rs candidate_tree_sha256 algorithm."""
    # Keep pathlib's component-aware ordering, which matches Rust PathBuf::Ord
    # in build.rs (src/runtime/* precedes src/runtime.rs).
    files = sorted(path for path in root.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for item in files:
        relative = item.relative_to(root).as_posix().encode("utf-8")
        content = item.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return len(files), digest.hexdigest()


def check(root: Path) -> dict:
    runtime = (root / "src/runtime.rs").read_text(encoding="utf-8")
    adapter = (root / "ui/runtime-adapter.js").read_text(encoding="utf-8")
    build_rs = (root / "build.rs").read_text(encoding="utf-8")
    handler = re.search(r"tauri::generate_handler!\s*\[([^\]]+)\]", runtime, re.S)
    ipc = re.findall(r"\b([a-z][a-z0-9_]*)\b", handler.group(1)) if handler else []
    profile = re.search(r"enum ProviderProfile\s*\{([^}]+)\}", runtime, re.S)
    profiles = re.findall(r"\b([A-Z][A-Za-z0-9_]*)\b", profile.group(1)) if profile else []
    count, digest = tree_digest(root)
    checks = {
        "runtime_key_exact": f'const SYN_KEY: &str = "{EXPECTED_KEY}"' in runtime,
        "ui_key_exact": f'const SYN_KEY = "{EXPECTED_KEY}"' in adapter,
        "legacy_ui_key_absent": "p3-130-capture-001" not in adapter and "p3-130-synthetic-capture-001" not in adapter,
        "ipc_exactly_20_in_order": ipc == EXPECTED_IPC,
        "five_profiles_exact": profiles == EXPECTED_PROFILES,
        "custom_cloud_semantics_visible": "DeepSeek、Kimi 或 OpenAI-compatible 服务" in adapter,
        "custom_adapter_is_openai_compatible": "impl ModelPort for CustomOpenAiCompatibleAdapter" in runtime and "openai_inference(input)" in runtime,
        "test_select_enable_order_present": "await invoke(\"test_ai_provider_connection\", {})" in adapter and "await invoke(\"set_ai_provider_enabled\", { enabled: true })" in adapter,
        "first_send_lock_present": "provider_locked_after_first_send" in runtime and "locked_profile" in runtime,
        "phase_c_v2_receipt_gate_present": "LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH" in build_rs and re.search(r"BuildMode::PhaseCReal\s*\{\s*Some\(validate_phase_c_v2_receipt\(\)\)", build_rs) is not None,
        "phase_c_v1_rejected": "P3_141_PHASE_B_RECEIPT" in build_rs and "PhaseCReal" in build_rs,
    }
    return {
        "schema": "lifeos.p3-141.independent-static-verifier.v1",
        "candidate": str(root),
        "candidate_file_count": count,
        "independent_tree_sha256": digest,
        "ipc": ipc,
        "profiles": profiles,
        "checks": checks,
        "pass": all(checks.values()),
    }


if len(sys.argv) != 2:
    raise SystemExit("usage: review_static_verifier.py <candidate-root>")
candidate = Path(sys.argv[1]).resolve()
if not (candidate / "src/runtime.rs").is_file() or not (candidate / "ui/runtime-adapter.js").is_file():
    raise SystemExit("candidate root shape rejected")
print(json.dumps(check(candidate), ensure_ascii=False, sort_keys=True))
