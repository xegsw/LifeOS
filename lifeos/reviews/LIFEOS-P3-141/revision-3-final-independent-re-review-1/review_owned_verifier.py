#!/usr/bin/env python3
"""Review-owned static and mutation verifier for P3-141 Revision 3.

It deliberately reads only the fixed candidate sources named below and writes
only JSON results/mutable source copies beneath its own review directory.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parent
ROOT = Path("/Users/xxe/.codex/worktrees/506c/No.2")
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate"
RUNTIME = CANDIDATE / "src/runtime.rs"
ADAPTER = CANDIDATE / "ui/runtime-adapter.js"
BUILD = CANDIDATE / "build.rs"

EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context",
    "get_evidence_backed_understanding", "decide_understanding_feedback",
    "get_ai_provider_settings", "save_ai_provider_settings",
    "save_ai_provider_credential", "test_ai_provider_connection",
    "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state",
    "resolve_request_context", "get_context_disclosure_receipt",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_inputs(base: Path) -> dict[str, str]:
    return {
        "runtime": (base / "src/runtime.rs").read_text(),
        "adapter": (base / "ui/runtime-adapter.js").read_text(),
        "build": (base / "build.rs").read_text(),
    }


def check(base: Path) -> list[dict[str, object]]:
    text = source_inputs(base)
    runtime, adapter, build = text["runtime"], text["adapter"], text["build"]
    ipc_match = re.search(r"const IPC: \[&str; 20\] = \[(.*?)\];", runtime, re.S)
    ipc = re.findall(r'"([a-z_]+)"', ipc_match.group(1)) if ipc_match else []
    cloud_profiles = ["Openai", "Anthropic", "Deepseek", "Kimi", "CloudCustomOpenaiCompatible"]
    local_profiles = ["Ollama", "LmStudio", "LocalCustomCompatible"]
    checks: list[tuple[str, bool, str]] = [
        ("exact_20_ipc", ipc == EXPECTED_IPC, f"actual_count={len(ipc)}"),
        ("session_credential_absent", "set_ai_provider_session_credential" not in runtime + adapter, "legacy IPC must be absent"),
        ("cloud_five_source", all(name in runtime for name in cloud_profiles) and "ProviderMode::Cloud => matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::Deepseek | ProviderProfile::Kimi | ProviderProfile::CloudCustomOpenaiCompatible)" in runtime and all(label in adapter for label in ["OpenAI", "Anthropic", "DeepSeek", "Kimi", "自定义 OpenAI-compatible"]), "five independent Cloud profiles"),
        ("local_three_source", all(name in runtime for name in local_profiles) and all(label in adapter for label in ["Ollama", "LM Studio", "自定义本地兼容服务"]), "three Local profiles"),
        ("mode_isolation", "ProviderMode::Local => matches!(profile, ProviderProfile::Ollama | ProviderProfile::LmStudio | ProviderProfile::LocalCustomCompatible)" in runtime and "ProviderMode::Cloud => matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::Deepseek | ProviderProfile::Kimi | ProviderProfile::CloudCustomOpenaiCompatible)" in runtime and "provider_mode_state" in runtime and "active_mode" in runtime, "separate mode state"),
        ("credential_schema_ciphertext_only", "encrypted_provider_credentials" in runtime and "key_id TEXT NOT NULL,nonce BLOB NOT NULL,ciphertext BLOB NOT NULL" in runtime and "api_key TEXT" not in runtime, "no plaintext credential column"),
        ("credential_key_separated", "parent.join(\"keys\")" in runtime and "CREDENTIAL_KEY_FILE" in runtime and "paths.root.join(\"keys\")" not in runtime, "key material outside runtime SQLite directory"),
        ("credential_lifecycle", "CredentialOperation::StoreOrUpdate" in runtime and "CredentialOperation::Delete" in runtime and "ON CONFLICT(mode,profile) DO UPDATE" in runtime and "DELETE FROM encrypted_provider_credentials" in runtime, "store/update/delete lifecycle"),
        ("write_before_failure_closed", "credential_input_rejected" in runtime and "credential_ciphertext_rejected" in runtime and "credential_key_provider_unavailable" in runtime, "credential failure codes"),
        ("separate_user_actions", all(action in adapter for action in ["provider:save", "provider:credential-save", "provider:test", "provider:model-select", "provider:enable"]) and "保存、测试、选择、启用和发送是彼此分离的操作" in adapter, "UI action separation"),
        ("no_implicit_fallback", "provider_locked_after_first_send" in runtime and "provider_enablement_rejected" in runtime and "model_request_count" in runtime, "locked explicit enabled flow"),
        ("strict_marker", "authorized synthetic root marker must be a 0600 ordinary non-symlink file" in build and "marker_metadata.permissions().mode() & 0o777 != 0o600" in build and "marker != expected" in build and "authorized synthetic root name is outside the strict P3-141 Revision-3 format" in build, "marker/root validation"),
        ("literal_tmp_root", "root.parent() != Some(Path::new(\"/private/tmp\"))" in build, "strict direct child root"),
        ("ui_masks_only", "API Key 已加密保存" in adapter and "provider-credential\" type=\"password" in adapter and "provider.credential?.masked" in adapter, "masked UI only"),
    ]
    return [{"id": ident, "pass": passed, "detail": detail} for ident, passed, detail in checks]


def static_result() -> int:
    results = check(CANDIDATE)
    candidate_files = sorted(path for path in CANDIDATE.rglob("*") if path.is_file())
    payload = {
        "schema": "lifeos.p3-141.revision-3.review-owned-static.v1",
        "candidate_commit": "476e5f069671dc7d0dc53be88f9d328901d6d543",
        "candidate_file_count": len(candidate_files),
        "candidate_sha256": {str(path.relative_to(CANDIDATE)): sha256(path) for path in candidate_files},
        "results": results,
        "pass_count": sum(bool(row["pass"]) for row in results),
        "fail_count": sum(not bool(row["pass"]) for row in results),
    }
    (REVIEW / "static_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0 if payload["fail_count"] == 0 else 1


def mutation_result() -> int:
    source = source_inputs(CANDIDATE)
    mutations: list[tuple[str, str, str, str]] = [
        ("provider_set_fallback", "runtime", "ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::Deepseek | ProviderProfile::Kimi | ProviderProfile::CloudCustomOpenaiCompatible", "ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::CloudCustomOpenaiCompatible"),
        ("session_credential_fallback", "runtime", '"save_ai_provider_credential"', '"set_ai_provider_session_credential"'),
        ("cloud_local_cross_use", "runtime", "ProviderMode::Local => matches!(profile, ProviderProfile::Ollama | ProviderProfile::LmStudio | ProviderProfile::LocalCustomCompatible)", "ProviderMode::Local => matches!(profile, ProviderProfile::Openai | ProviderProfile::Ollama)"),
        ("generic_root", "build", "root.parent() != Some(Path::new(\"/private/tmp\"))", "false"),
        ("marker_bypass", "build", "marker_metadata.permissions().mode() & 0o777 != 0o600", "false"),
    ]
    mutation_root = REVIEW / "mutations"
    mutation_root.mkdir(exist_ok=True)
    records: list[dict[str, object]] = []
    for name, target, old, new in mutations:
        copied = mutation_root / name
        (copied / "src").mkdir(parents=True, exist_ok=True)
        (copied / "ui").mkdir(exist_ok=True)
        (copied / "src/runtime.rs").write_text(source["runtime"])
        (copied / "ui/runtime-adapter.js").write_text(source["adapter"])
        (copied / "build.rs").write_text(source["build"])
        destination = {"runtime": copied / "src/runtime.rs", "adapter": copied / "ui/runtime-adapter.js", "build": copied / "build.rs"}[target]
        before = destination.read_text()
        if before.count(old) != 1:
            records.append({"id": name, "pass": False, "detail": "mutation_anchor_not_unique", "anchor_count": before.count(old)})
            continue
        destination.write_text(before.replace(old, new, 1))
        rows = check(copied)
        detected = any(not bool(row["pass"]) for row in rows)
        failures = [str(row["id"]) for row in rows if not bool(row["pass"])]
        records.append({"id": name, "pass": detected, "detected_failures": failures})
    payload = {
        "schema": "lifeos.p3-141.revision-3.review-owned-mutations.v1",
        "control_static_pass": all(bool(row["pass"]) for row in check(CANDIDATE)),
        "results": records,
        "pass_count": sum(bool(row["pass"]) for row in records),
        "fail_count": sum(not bool(row["pass"]) for row in records),
    }
    (REVIEW / "mutation_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0 if payload["control_static_pass"] and payload["fail_count"] == 0 else 1


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"static", "mutations"}:
        print("usage: review_owned_verifier.py {static|mutations}", file=sys.stderr)
        return 64
    return static_result() if sys.argv[1] == "static" else mutation_result()


if __name__ == "__main__":
    raise SystemExit(main())
