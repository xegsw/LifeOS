//! P3-148 closed request contracts. No filesystem, provider or credential effects.
use crate::repository::{Error, Request};
use serde_json::Value;
pub type R<T> = Result<T, Error>;
pub fn fail<T>(code: &str) -> R<T> {
    Err(Error::new(code))
}
pub fn fields(v: &Value, required: &[&str], optional: &[&str]) -> R<()> {
    let o = v.as_object().ok_or_else(|| Error::new("dto_rejected"))?;
    if o.keys()
        .any(|k| !required.contains(&k.as_str()) && !optional.contains(&k.as_str()))
    {
        return fail("unknown_field");
    }
    if required.iter().any(|k| !o.contains_key(*k)) || o.values().any(Value::is_null) {
        return fail("dto_rejected");
    }
    Ok(())
}
pub fn id(v: &Value, k: &str) -> R<String> {
    let s = v[k]
        .as_str()
        .ok_or_else(|| Error::new("identity_rejected"))?;
    if s.is_empty()
        || s.len() > 120
        || !s
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"_:-".contains(&b))
    {
        return fail("identity_rejected");
    }
    Ok(s.into())
}
pub fn num(v: &Value, k: &str, min: u64) -> R<u64> {
    v[k].as_u64()
        .filter(|n| *n >= min && *n <= 9007199254740991)
        .ok_or_else(|| Error::new("integer_rejected"))
}
pub fn text(v: &Value, k: &str, empty: bool) -> R<String> {
    let s = v[k].as_str().ok_or_else(|| Error::new("text_rejected"))?;
    if (!empty && s.trim().is_empty()) || s.chars().count() > 2000 || s.len() > 8192 {
        return fail("text_rejected");
    }
    Ok(s.into())
}
pub fn ids(v: &Value, k: &str, max: usize) -> R<Vec<String>> {
    let a = v[k].as_array().ok_or_else(|| Error::new("dto_rejected"))?;
    if a.len() > max {
        return fail("dto_rejected");
    }
    let mut out = Vec::new();
    for s in a {
        let x = id(&serde_json::json!({"id":s}), "id")?;
        if out.contains(&x) {
            return fail("dto_rejected");
        }
        out.push(x)
    }
    Ok(out)
}
pub fn validate(command: &str, r: &Request) -> R<()> {
    if (command == "send_source_ai_request" && r.version != 1)
        || (command != "send_source_ai_request" && r.version != 3)
    {
        return fail("version_rejected");
    }
    let p = &r.payload;
    let (required, optional): (&[&str], &[&str]) = match (command, r.operation.as_str()) {
        ("capture_record", "draft_question") => (
            &[
                "requestId",
                "draftId",
                "conversationId",
                "turnId",
                "revision",
                "text",
            ],
            &[],
        ),
        ("capture_record", "save_question") => (
            &[
                "requestId",
                "draftId",
                "conversationId",
                "turnId",
                "expectedDraftRevision",
            ],
            &[],
        ),
        ("get_context_recovery", "open_conversation") => (&["requestId", "conversationId"], &[]),
        ("get_context_recovery", "read_conversation") => (&["conversationId"], &["cursor"]),
        ("assemble_global_ai_context", "prepare_source_preview") => (
            &[
                "requestId",
                "conversationId",
                "turnId",
                "expectedQuestionVersion",
                "excludedSegmentIds",
            ],
            &[],
        ),
        ("assemble_global_ai_context", "cancel_source_preview") => {
            (&["requestId", "previewId", "expectedPreviewRevision"], &[])
        }
        ("get_context_disclosure_receipt", "read_preview") => (&["previewId"], &[]),
        ("send_source_ai_request", "confirm_send") => (
            &[
                "requestId",
                "previewId",
                "expectedPreviewRevision",
                "confirmationToken",
            ],
            &[],
        ),
        ("get_evidence_backed_understanding", "read_answer") => (&["dispatchId"], &[]),
        ("decide_understanding_feedback", "answer_feedback") if p["decision"] == "correct" => (
            &[
                "requestId",
                "answerId",
                "expectedAnswerRevision",
                "decision",
                "correctionText",
                "affectedCitationIds",
            ],
            &[],
        ),
        ("decide_understanding_feedback", "answer_feedback") => (
            &[
                "requestId",
                "answerId",
                "expectedAnswerRevision",
                "decision",
            ],
            &[],
        ),
        ("get_ai_provider_settings", "read_settings") => (&[], &[]),
        ("save_ai_provider_credential", "replace_credential") => (
            &[
                "requestId",
                "profileId",
                "expectedCredentialRevision",
                "apiKey",
            ],
            &[],
        ),
        ("save_ai_provider_credential", "delete_credential" | "recover_credentials") => (
            &[
                "requestId",
                "profileId",
                "expectedCredentialRevision",
                "confirmation",
            ],
            &[],
        ),
        ("test_ai_provider_connection", "test_connection") => (
            &[
                "requestId",
                "profileId",
                "expectedCredentialRevision",
                "confirmation",
            ],
            &[],
        ),
        ("save_ai_provider_settings", "select_model") => (
            &[
                "requestId",
                "profileId",
                "expectedProfileRevision",
                "testReceiptId",
                "modelId",
            ],
            &[],
        ),
        ("set_ai_provider_enabled", "set_enabled") => (
            &[
                "requestId",
                "profileId",
                "expectedProfileRevision",
                "enabled",
            ],
            &[],
        ),
        _ => return fail("operation_rejected"),
    };
    fields(p, required, optional)?;
    for k in required.iter().chain(optional) {
        if p.get(*k).is_none() {
            continue;
        }
        if k.ends_with("Id") && *k != "modelId" || *k == "cursor" || *k == "confirmationToken" {
            id(p, k)?;
        }
        if k.contains("Revision") || *k == "revision" || *k == "expectedQuestionVersion" {
            num(
                p,
                k,
                if *k == "expectedCredentialRevision"
                    && r.operation != "test_connection"
                    && r.operation != "delete_credential"
                {
                    0
                } else {
                    1
                },
            )?;
        }
    }
    if p.get("profileId").is_some() && p["profileId"] != "deepseek-default" {
        return fail("real_capability_denied");
    }
    if r.operation == "replace_credential" {
        let secret = p["apiKey"].as_str().ok_or_else(|| Error::new("credential_invalid"))?;
        if !(8..=512).contains(&secret.len()) || !secret.bytes().all(|b| b.is_ascii_graphic() && b != b'"' && b != b'\\') {
            return fail("credential_invalid");
        }
    }
    if r.operation == "draft_question" {
        text(p, "text", true)?;
    }
    if p["decision"] == "correct" {
        text(p, "correctionText", false)?;
        ids(p, "affectedCitationIds", 3)?;
    }
    if r.operation == "answer_feedback"
        && !matches!(
            p["decision"].as_str(),
            Some("helpful" | "reject" | "correct")
        )
    {
        return fail("feedback_scope_rejected");
    }
    if r.operation == "prepare_source_preview" {
        ids(p, "excludedSegmentIds", 8)?;
    }
    if p.get("enabled").is_some() && !p["enabled"].is_boolean() {
        return fail("dto_rejected");
    }
    let confirm = match r.operation.as_str() {
        "delete_credential" => Some("delete_this_credential"),
        "recover_credentials" => Some("recover_owned_credential_operations"),
        "test_connection" => Some("test_deepseek_models_once"),
        _ => None,
    };
    if confirm.is_some_and(|s| p["confirmation"] != s) {
        return fail("confirmation_rejected");
    }
    if p.get("modelId").is_some() {
        let s = p["modelId"]
            .as_str()
            .ok_or_else(|| Error::new("model_not_tested"))?;
        if s.is_empty()
            || s.len() > 128
            || !s
                .bytes()
                .all(|c| c.is_ascii_alphanumeric() || b"_.:-".contains(&c))
        {
            return fail("model_not_tested");
        }
    }
    Ok(())
}

/// Closed public v3 error contract; legacy adapter details never leave this boundary.
pub fn public_error(e: Error) -> Error {
    const CODES: &[&str] = &[
        "dto_rejected",
        "unknown_field",
        "duplicate_field",
        "identity_rejected",
        "integer_rejected",
        "operation_rejected",
        "version_rejected",
        "local_activation_required",
        "source_database_missing",
        "store_contract_mismatch",
        "database_unavailable",
        "database_path_rejected",
        "draft_stale",
        "draft_conflict",
        "draft_missing",
        "text_rejected",
        "turn_conflict",
        "idempotency_conflict",
        "source_missing",
        "authorization_rejected",
        "context_stale",
        "context_budget_rejected",
        "sensitive_content_rejected",
        "query_rejected",
        "cursor_stale",
        "preview_missing",
        "preview_expired",
        "preview_stale",
        "preview_consumed",
        "confirmation_rejected",
        "provider_not_enabled",
        "provider_revision_conflict",
        "model_not_tested",
        "real_capability_denied",
        "external_targets_disabled",
        "source_scan_disabled",
        "credential_invalid",
        "credential_reference_rejected",
        "credential_revision_conflict",
        "credential_unavailable",
        "credential_missing",
        "credential_authentication_failed",
        "credential_cleanup_pending",
        "provider_authentication",
        "provider_model",
        "provider_protocol",
        "provider_unavailable",
        "response_too_large",
        "answer_missing",
        "answer_revision_conflict",
        "feedback_scope_rejected",
        "dispatch_persistence_failed",
        "dispatch_outcome_unknown",
    ];
    if CODES.contains(&e.code.as_str()) { e } else { Error::new("database_unavailable") }
}
