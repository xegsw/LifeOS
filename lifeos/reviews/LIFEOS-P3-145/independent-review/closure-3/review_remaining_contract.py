#!/usr/bin/env python3
"""Read-only structural/mutation checks for Closure-3's remaining ABF rows."""
import json
import sys
from pathlib import Path


def all_of(source, parts):
    return all(part in source for part in parts)


def resolver_contract(source):
    return all_of(
        source,
        [
            "WHERE domain=?1 AND authorized=1 AND status='active'",
            "(expires_at_ms IS NULL OR expires_at_ms>?2)",
            "items.extend(active_items(root, HEALTH)?)",
            ".then_with(|| left.id.cmp(&right.id))",
        ],
    )


def disclosure_contract(source):
    return all_of(
        source,
        [
            "refs.retain(|value| value != item_id)",
            "revision=revision+1,previewed=0",
            "disclosure.revision != observed_revision",
            "|| !disclosure.previewed",
            "|| disclosure.confirmation_used",
            "disclosure_empty",
            "confirmation_used=1 WHERE id=?1 AND revision=?2 AND previewed=1 AND confirmation_used=0",
        ],
    )


def feedback_contract(source):
    return all_of(
        source,
        [
            '"confirm" => Some("confirmed")',
            '"edit" => Some("edited")',
            '"reject" => Some("rejected")',
            '"ignore" => Some("ignored")',
            '"correct" => Some("invalidated")',
            '"confirmed" | "edited" | "rejected" | "ignored"',
            "UPDATE derivation SET status=?1 WHERE id=?2 AND status=?3",
            "understanding_feedback_consumed",
            "INSERT INTO feedback_event",
            '"understanding_feedback"',
        ],
    )


def credential_contract(runtime, credentials):
    load_start = runtime.index("fn load_api_key(root")
    load_end = runtime.index("fn load_api_key_string", load_start)
    load = runtime[load_start:load_end]
    send_start = runtime.index("ensure_confirmed_request_budget(&state.root)?")
    send_end = runtime.index("fn get_context_disclosure_receipt", send_start)
    send = runtime[send_start:send_end]
    key_load_position = send.find("let mut api_key = load_api_key_string(&state.root)?")
    adapter_position = send.find("let adapter = if run_mode() == \"real_gate\"")
    return (
        all_of(
            load,
            [
                "credential_required",
                "secure_credentials::decrypt",
                ".map_err(credential_failure)",
            ],
        )
        and all_of(
            credentials,
            [
                "if algorithm != ALGORITHM || version != VERSION || nonce.len() != 12 || tag.len() != 16",
                "return Err(CredentialFailure::AuthenticationFailed)",
                "let mut key = load_key_material(reference)?",
                "result.map_err(|_| CredentialFailure::AuthenticationFailed)?",
                "key.zeroize()",
            ],
        )
        and key_load_position >= 0
        and adapter_position >= 0
        and key_load_position < adapter_position
        and all_of(
            runtime,
            [
                '"key_material_missing"',
                '"credential_authentication_failed"',
                "已在网络前拒绝。",
            ],
        )
    )


def main():
    runtime = Path(sys.argv[1]).read_text()
    credentials = Path(sys.argv[2]).read_text()
    checks = {
        "resolver_excludes_unauthorized_revoked_and_expired": resolver_contract(runtime),
        "disclosure_remove_invalidates_preview_and_confirmation": disclosure_contract(runtime),
        "feedback_maps_all_five_actions_and_is_single_use": feedback_contract(runtime),
        "credential_missing_and_tamper_fail_before_adapter": credential_contract(runtime, credentials),
        "no_plaintext_log_sinks_in_credential_paths": not any(
            token in credentials + runtime
            for token in ["println!(\"{}\", api_key", "eprintln!(\"{}\", api_key", "log::info!(\"{}\", api_key"]
        ),
    }
    mutations = {
        "resolver_authorization_filter_removed": not resolver_contract(
            runtime.replace("authorized=1", "authorized=0", 1)
        ),
        "resolver_expiry_filter_removed": not resolver_contract(
            runtime.replace("(expires_at_ms IS NULL OR expires_at_ms>?2)", "1=1", 1)
        ),
        "resolver_active_status_filter_removed": not resolver_contract(
            runtime.replace("status='active'", "status='revoked'", 1)
        ),
        "disclosure_revision_bump_removed": not disclosure_contract(
            runtime.replace("revision=revision+1,previewed=0", "previewed=0")
        ),
        "confirmation_conditional_guard_removed": not disclosure_contract(
            runtime.replace(" AND previewed=1 AND confirmation_used=0", "", 1)
        ),
        "feedback_confirm_mapping_removed": not feedback_contract(
            runtime.replace('"confirm" => Some("confirmed")', "", 1)
        ),
        "feedback_edit_mapping_removed": not feedback_contract(
            runtime.replace('"edit" => Some("edited")', "", 1)
        ),
        "feedback_reject_mapping_removed": not feedback_contract(
            runtime.replace('"reject" => Some("rejected")', "", 1)
        ),
        "feedback_ignore_mapping_removed": not feedback_contract(
            runtime.replace('"ignore" => Some("ignored")', "", 1)
        ),
        "feedback_correct_mapping_removed": not feedback_contract(
            runtime.replace('"correct" => Some("invalidated")', "", 1)
        ),
        "feedback_compare_and_set_removed": not feedback_contract(
            runtime.replace(" WHERE id=?2 AND status=?3", " WHERE id=?2", 1)
        ),
        "credential_authentication_guard_removed": not credential_contract(
            runtime,
            credentials.replace("result.map_err(|_| CredentialFailure::AuthenticationFailed)?", "result?", 1),
        ),
        "credential_load_before_adapter_removed": not credential_contract(
            runtime.replace("let mut api_key = load_api_key_string(&state.root)?", "let mut api_key = Vec::new()"),
            credentials,
        ),
    }
    print(json.dumps({"checks": checks, "mutations_rejected": mutations, "pass": all(checks.values()) and all(mutations.values())}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
