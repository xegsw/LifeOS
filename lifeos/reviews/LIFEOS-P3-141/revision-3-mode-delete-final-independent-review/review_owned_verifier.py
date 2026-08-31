#!/usr/bin/env python3
"""Read-only structural verifier authored for this independent re-review."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree(candidate: Path) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    for directory, dirs, names in os.walk(candidate, followlinks=False):
        dirs.sort()
        for name in sorted(names):
            path = Path(directory, name)
            if path.is_symlink() or not path.is_file():
                continue
            rel = path.relative_to(candidate).as_posix()
            records.append({"path": rel, "sha256": sha256(path), "bytes": str(path.stat().st_size)})
    aggregate = hashlib.sha256()
    for item in records:
        encoded = (item["path"] + "\0" + item["bytes"] + "\0" + item["sha256"] + "\n").encode()
        aggregate.update(encoded)
    return aggregate.hexdigest(), records


def check(name: str, value: bool, results: list[dict[str, object]], detail: str) -> None:
    results.append({"id": name, "status": "PASS" if value else "FAIL", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fixed-inputs", required=True)
    args = parser.parse_args()
    candidate = Path(args.candidate).resolve()
    fixed = Path(args.fixed_inputs).resolve()
    runtime = (candidate / "src/runtime.rs").read_text(encoding="utf-8")
    adapter = (candidate / "ui/runtime-adapter.js").read_text(encoding="utf-8")
    build = (candidate / "build.rs").read_text(encoding="utf-8")
    main_rs = (candidate / "src/main.rs").read_text(encoding="utf-8")
    tree_hash, files = tree(candidate)
    results: list[dict[str, object]] = []

    check("IRV-01-ipc-exact", all(f'"{name}"' in runtime for name in EXPECTED_IPC)
          and runtime.count('"save_ai_provider_credential"') >= 1
          and "set_ai_provider_session_credential" not in runtime,
          results, "all 20 names must be present and the retired session IPC absent")
    check("IRV-02-cloud-set", all(token in runtime for token in [
          "Openai", "Anthropic", "Deepseek", "Kimi", "CloudCustomOpenaiCompatible"]) and
          all(token in adapter for token in [
          '"openai"', '"anthropic"', '"deepseek"', '"kimi"', '"cloud_custom_openai_compatible"']),
          results, "five independent Cloud profile identities")
    check("IRV-03-local-set", all(token in runtime for token in [
          "Ollama", "LmStudio", "LocalCustomCompatible"]) and
          all(token in adapter for token in [
          '"ollama"', '"lm_studio"', '"local_custom_compatible"']),
          results, "three independent Local profile identities")
    cloud_match = "ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::Deepseek | ProviderProfile::Kimi | ProviderProfile::CloudCustomOpenaiCompatible"
    local_match = "ProviderProfile::Ollama | ProviderProfile::LmStudio | ProviderProfile::LocalCustomCompatible"
    mode_contract = f"ProviderMode::Local => matches!(profile, {local_match}), ProviderMode::Cloud => matches!(profile, {cloud_match})"
    check("IRV-04-mode-segregation", mode_contract in runtime
          and "provider_mode_state(mode TEXT PRIMARY KEY CHECK(mode IN ('cloud','local'))" in runtime,
          results, "Cloud and Local profile matches plus durable per-mode state")
    check("IRV-05-encrypted-credential", all(token in runtime for token in [
          "encrypted_provider_credentials", "Aes256Gcm", "credential-aead.key",
          "CREATE TABLE IF NOT EXISTS encrypted_provider_credentials", "credential_key_dir"]),
          results, "ciphertext table and external 0600 key material are both required")
    check("IRV-06-no-session-fallback", all(token not in runtime + adapter for token in [
          "sessionCredential", "set_ai_provider_session_credential", "environment credential"]),
          results, "no product session or environment credential fallback symbol")
    check("IRV-07-action-separation", all(token in adapter for token in [
          'data-action="provider:save"', 'data-action="provider:credential-save"',
          'data-action="provider:test"', 'data-action="provider:model-select"',
          'data-action="provider:enable"']) and "save_ai_provider_settings" in adapter
          and "test_ai_provider_connection" in adapter and "set_ai_provider_enabled" in adapter,
          results, "save, credential save, test, select and enable remain distinct UI/runtime actions")
    check("IRV-08-draft-delete-guard", "const requirePersistedProviderMode = () => {\n    if (providerModePending()) throw" in adapter
          and all(token in adapter for token in [
          "providerModePending", "requirePersistedProviderMode", "data-pending-mode=\"save-required\"",
          "先保存 Cloud 配置后管理 API Key", "provider-clear-credential"]) and
          adapter.count("requirePersistedProviderMode();") >= 4,
          results, "unsaved mode draft must disable/delete-guard credentials and other dependent actions")
    check("IRV-09-root-authority", 'root.parent() != Some(Path::new("/private/tmp"))' in build
          and 'root.parent() != Some(Path::new("/private/tmp"))' in runtime
          and "runtime_root.parent()" in build and "AUTHORIZED_ROOT_MARKER" in build,
          results, "build and runtime must both bind a literal /private/tmp direct authorized root")
    check("IRV-10-marker-binding", "marker != expected" in build and "marker != expected" in runtime
          and "AUTHORIZED_ROOT_MARKER" in build and "AUTHORIZED_ROOT_MARKER" in runtime,
          results, "build and runtime both reject a mismatched root marker")
    check("IRV-11-native-launch-contract", all(token in runtime for token in [
          "configure_native_webview_accessibility", "NSAccessibilityWebAreaRole",
          "write_controlled_viewport_receipt", "LifeOS · P3-141 Controlled Pilot Candidate"]),
          results, "direct native WebView/AXWebArea setup and exact title")
    check("IRV-12-main-runtime", "mod runtime;" in main_rs and "runtime::run();" in main_rs,
          results, "candidate executable invokes reviewed runtime")

    inventory = json.loads(fixed.read_text(encoding="utf-8"))
    fixed_results = []
    for item in inventory["inputs"]:
        path = fixed.parents[2] / item["path"]
        actual = sha256(path)
        fixed_results.append({"path": item["path"], "expected": item["sha256"], "actual": actual,
                              "status": "PASS" if actual == item["sha256"] else "FAIL"})
    payload = {
        "schema": "lifeos.p3-141.revision-3.review-owned-verifier.v1",
        "candidate": str(candidate), "candidate_tree_sha256": tree_hash,
        "candidate_file_count": len(files), "candidate_files": files,
        "fixed_inputs": fixed_results, "checks": results,
        "pass": all(entry["status"] == "PASS" for entry in results + fixed_results),
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
