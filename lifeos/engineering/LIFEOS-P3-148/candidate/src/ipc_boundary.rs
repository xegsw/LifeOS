//! E02: strict raw business JSON, before any store/credential/transport dispatch.
use crate::repository::{Error, Request};
use serde_json::Value;
use tauri::ipc::InvokeBody;

// Largest legal request is <= 2000 scalars (at most 12 ASCII escape bytes each),
// plus bounded identifiers/field names. 32 KiB leaves room without admitting
// unbounded binary input. This is a wire cap, not the 24 KiB model-body budget.
pub const MAX_RAW_BYTES: usize = 32768;

pub fn dispatch_with<T>(
    command: &str,
    body: InvokeBody,
    dispatch: impl FnOnce(Request, bool) -> Result<T, Error>,
) -> Result<T, Error> {
    let (request, modern) = match body {
        InvokeBody::Raw(bytes) => {
            if bytes.len() > MAX_RAW_BYTES {
                return Err(Error::new("dto_rejected"));
            }
            let raw = std::str::from_utf8(&bytes).map_err(|_| Error::new("dto_rejected"))?;
            let value = crate::strict_json::parse(raw)?;
            crate::conversation_contract::fields(
                &value,
                &["version", "operation", "payload"],
                &[],
            )?;
            let request: Request =
                serde_json::from_value(value).map_err(|_| Error::new("dto_rejected"))?;
            crate::conversation_contract::validate(command, &request)?;
            (request, true)
        }
        InvokeBody::Json(value) => {
            // JSON has already lost duplicate information. It may only carry
            // the legacy v2 contract, never any new operation or send command.
            if command == "send_source_ai_request" {
                return Err(Error::new("dto_rejected"));
            }
            let request: Request =
                serde_json::from_value(value.get("request").cloned().unwrap_or(Value::Null))
                    .map_err(|_| Error::new("dto_rejected"))?;
            if request.version != 2 {
                return Err(Error::new("version_rejected"));
            }
            (request, false)
        }
    };
    dispatch(request, modern)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::cell::Cell;
    #[test]
    fn p148_public_errors_are_closed() {
        assert_eq!(crate::conversation_contract::public_error(Error::new("synthetic adapter detail")).code,"database_unavailable");
        assert_eq!(crate::conversation_contract::public_error(Error::new("confirmation_rejected")).code,"confirmation_rejected");
    }

    #[test]
    fn p148_raw_operation_contract_table() {
        // Examples transcribed from sealed 01, including each feedback branch.
        let cases = [
            (
                "capture_record",
                "draft_question",
                json!({"requestId":"r","draftId":"d","conversationId":"c","turnId":"t","revision":1,"text":"fiction"}),
            ),
            (
                "capture_record",
                "save_question",
                json!({"requestId":"r","draftId":"d","conversationId":"c","turnId":"t","expectedDraftRevision":1}),
            ),
            (
                "get_context_recovery",
                "open_conversation",
                json!({"requestId":"r","conversationId":"c"}),
            ),
            (
                "get_context_recovery",
                "read_conversation",
                json!({"conversationId":"c"}),
            ),
            (
                "assemble_global_ai_context",
                "prepare_source_preview",
                json!({"requestId":"r","conversationId":"c","turnId":"t","expectedQuestionVersion":1,"excludedSegmentIds":[]}),
            ),
            (
                "assemble_global_ai_context",
                "cancel_source_preview",
                json!({"requestId":"r","previewId":"p","expectedPreviewRevision":1}),
            ),
            (
                "get_context_disclosure_receipt",
                "read_preview",
                json!({"previewId":"p"}),
            ),
            (
                "send_source_ai_request",
                "confirm_send",
                json!({"requestId":"r","previewId":"p","expectedPreviewRevision":1,"confirmationToken":"c"}),
            ),
            (
                "get_evidence_backed_understanding",
                "read_answer",
                json!({"dispatchId":"d"}),
            ),
            (
                "decide_understanding_feedback",
                "answer_feedback",
                json!({"requestId":"r","answerId":"a","expectedAnswerRevision":1,"decision":"helpful"}),
            ),
            (
                "decide_understanding_feedback",
                "answer_feedback",
                json!({"requestId":"r","answerId":"a","expectedAnswerRevision":1,"decision":"reject"}),
            ),
            (
                "decide_understanding_feedback",
                "answer_feedback",
                json!({"requestId":"r","answerId":"a","expectedAnswerRevision":1,"decision":"correct","correctionText":"fiction","affectedCitationIds":[]}),
            ),
            ("get_ai_provider_settings", "read_settings", json!({})),
            (
                "save_ai_provider_credential",
                "replace_credential",
                json!({"requestId":"r","profileId":"deepseek-default","expectedCredentialRevision":0,"apiKey":"synthetic-only-key"}),
            ),
            (
                "save_ai_provider_credential",
                "delete_credential",
                json!({"requestId":"r","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"delete_this_credential"}),
            ),
            (
                "save_ai_provider_credential",
                "recover_credentials",
                json!({"requestId":"r","profileId":"deepseek-default","expectedCredentialRevision":0,"confirmation":"recover_owned_credential_operations"}),
            ),
            (
                "test_ai_provider_connection",
                "test_connection",
                json!({"requestId":"r","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"test_deepseek_models_once"}),
            ),
            (
                "save_ai_provider_settings",
                "select_model",
                json!({"requestId":"r","profileId":"deepseek-default","expectedProfileRevision":1,"testReceiptId":"test","modelId":"model-one"}),
            ),
            (
                "set_ai_provider_enabled",
                "set_enabled",
                json!({"requestId":"r","profileId":"deepseek-default","expectedProfileRevision":1,"enabled":true}),
            ),
        ];
        for (cmd, op, payload) in cases {
            let value = json!({"version":if cmd=="send_source_ai_request"{1}else{3},"operation":op,"payload":payload});
            let calls = Cell::new(0);
            let check = |v: &Value| {
                dispatch_with(
                    cmd,
                    InvokeBody::Raw(v.to_string().into_bytes()),
                    |_, modern| {
                        assert!(modern);
                        calls.set(calls.get() + 1);
                        Ok(())
                    },
                )
            };
            check(&value).unwrap();
            assert_eq!(calls.get(), 1);
            if payload.get("apiKey").is_some() {
                for secret in [json!(7), json!("short"), json!("x".repeat(513))] {
                    let mut bad=value.clone();bad["payload"]["apiKey"]=secret;assert!(check(&bad).is_err());
                }
            }
            if payload.get("profileId").is_some() {
                let mut bad = value.clone();
                bad["payload"]["profileId"] = json!("other-provider");
                assert!(check(&bad).is_err());
            }
            let mut bad = value.clone();
            bad["version"] = json!(2);
            assert!(check(&bad).is_err());
            for layer in ["outer", "payload"] {
                let mut bad = value.clone();
                let o = if layer == "outer" {
                    bad.as_object_mut().unwrap()
                } else {
                    bad["payload"].as_object_mut().unwrap()
                };
                o.insert("prompt".into(), json!("fiction"));
                assert!(check(&bad).is_err());
            }
            for key in payload.as_object().unwrap().keys() {
                let mut bad = value.clone();
                bad["payload"][key] = Value::Null;
                assert!(check(&bad).is_err());
                let mut bad = value.clone();
                bad["payload"].as_object_mut().unwrap().remove(key);
                assert!(check(&bad).is_err());
            }
            for key in payload.as_object().unwrap().keys().filter(|k| {
                k.contains("Revision")
                    || k.as_str() == "revision"
                    || k.as_str() == "expectedQuestionVersion"
            }) {
                let mut bad = value.clone();
                bad["payload"][key] = json!("1");
                assert!(check(&bad).is_err());
                bad["payload"][key] = json!(9007199254740992_u64);
                assert!(check(&bad).is_err());
            }
            assert_eq!(calls.get(), 1, "rejected {cmd}/{op} dispatched");
        }
    }

    #[test]
    fn p148_raw_entry_rejects_before_dispatch_and_preserves_legacy() {
        let calls = Cell::new(0);
        let invoke = |cmd: &str, body| {
            dispatch_with(cmd, body, |r, modern| {
                calls.set(calls.get() + 1);
                Ok((r.version, modern))
            })
        };
        let raw = |s: &str| InvokeBody::Raw(s.as_bytes().to_vec());
        assert_eq!(
            invoke(
                "get_ai_provider_settings",
                raw(r#"{"version":3,"operation":"read_settings","payload":{}}"#)
            )
            .unwrap(),
            (3, true)
        );
        let before = calls.get();
        for (cmd, body) in [
            (
                "get_ai_provider_settings",
                raw(r#"{"version":3,"version":3,"operation":"read_settings","payload":{}}"#),
            ),
            (
                "get_context_recovery",
                raw(
                    r#"{"version":3,"operation":"read_conversation","payload":{"conversationId":"a","conversationId":"b"}}"#,
                ),
            ),
            (
                "get_ai_provider_settings",
                raw(r#"{"version":3,"operation":"read_settings","payload":{},"extra":1}"#),
            ),
            (
                "get_ai_provider_settings",
                raw(
                    r#"{"version":3,"operation":"read_settings","payload":{"prompt":"fiction","path":"fiction","provider":"fiction"}}"#,
                ),
            ),
            (
                "get_ai_provider_settings",
                raw(r#"{"version":3,"operation":"read_settings"}"#),
            ),
            (
                "get_ai_provider_settings",
                raw(r#"{"version":2,"operation":"snapshot","payload":{}}"#),
            ),
            ("get_ai_provider_settings", raw("null")),
            ("get_ai_provider_settings", raw("[]")),
            ("get_ai_provider_settings", InvokeBody::Raw(vec![0xff])),
            (
                "get_ai_provider_settings",
                InvokeBody::Raw(vec![b' '; MAX_RAW_BYTES + 1]),
            ),
            (
                "get_ai_provider_settings",
                InvokeBody::Json(
                    json!({"request":{"version":3,"operation":"read_settings","payload":{}}}),
                ),
            ),
            (
                "send_source_ai_request",
                InvokeBody::Json(
                    json!({"request":{"version":1,"operation":"confirm_send","payload":{}}}),
                ),
            ),
            (
                "get_today",
                raw(r#"{"version":3,"operation":"read_settings","payload":{}}"#),
            ),
        ] {
            assert!(invoke(cmd, body).is_err());
            assert_eq!(calls.get(), before);
        }
        assert_eq!(
            invoke(
                "get_today",
                InvokeBody::Json(
                    json!({"request":{"version":2,"operation":"snapshot","payload":{}}})
                )
            )
            .unwrap(),
            (2, false)
        );
    }
}
