#[test]
fn p149_ir001_preview_replay_projects_current_packet() {
    for state in ["cancelled", "stale", "consumed"] {
        let (f, mut c, v) = setup();
        if state == "cancelled" {
            call(
                &f,
                "assemble_global_ai_context",
                "cancel_source_preview",
                json!({"requestId":"cancel-ir","previewId":v["previewId"],"expectedPreviewRevision":1}),
            );
        } else if state == "stale" {
            c.execute("UPDATE connectors SET epoch=epoch+1", [])
                .unwrap();
        } else {
            send_with_port(&mut c, &send_input(&v), &f, &mut recording()).unwrap();
        }
        let replay = call(
            &f,
            "assemble_global_ai_context",
            "prepare_source_preview",
            json!({"requestId":"preview","conversationId":"source-chat","turnId":"turn-1","expectedQuestionVersion":1,"excludedSegmentIds":[]}),
        );
        assert_eq!(replay["state"], state);
        assert!(replay.get("confirmationToken").is_none());
        assert_eq!(
            replay,
            current_preview(&c, v["previewId"].as_str().unwrap(), &f).unwrap()
        );
        assert_eq!(all(&c, "packets").unwrap().len(), 1);
    }
}

#[test]
fn p149_ir002_feedback_turn_and_conversation_recovery() {
    let (f, mut c, v) = setup();
    let out = send_with_port(&mut c, &send_input(&v), &f, &mut recording()).unwrap();
    let aid = out["answerId"].as_str().unwrap();
    for (rid, revision, decision) in [
        ("feedback-help", 1, "helpful"),
        ("feedback-reject", 2, "reject"),
    ] {
        call(
            &f,
            "decide_understanding_feedback",
            "answer_feedback",
            json!({"requestId":rid,"answerId":aid,"expectedAnswerRevision":revision,"decision":decision}),
        );
    }
    // Same turn identity in another conversation must not acquire these relationships.
    let mut q = question(
        &c,
        &json!({"conversationId":"source-chat","turnId":"turn-1"}),
    )
    .unwrap();
    q["id"] = json!("other-question");
    q["conversationId"] = json!("other-chat");
    put(&c, "records", "other-question", &q).unwrap();
    q["id"] = json!("zz-second-question");
    q["conversationId"] = json!("source-chat");
    q["turnId"] = json!("turn-2");
    put(&c, "records", "zz-second-question", &q).unwrap();
    let current = read_conversation(&c, &json!({"conversationId":"source-chat"})).unwrap();
    assert_eq!(
        current["turns"][0]["feedbackIds"],
        json!(["feedback-help", "feedback-reject"])
    );
    assert_eq!(current["turns"][1]["feedbackIds"], json!([]));
    drop(c);
    let c = open(&f).unwrap();
    assert_eq!(
        read_conversation(&c, &json!({"conversationId":"source-chat"})).unwrap()["turns"][0]
            ["feedbackIds"],
        current["turns"][0]["feedbackIds"]
    );
    assert_eq!(
        read_conversation(&c, &json!({"conversationId":"other-chat"})).unwrap()["turns"][0]
            ["feedbackIds"],
        json!([])
    );
}

#[test]
fn p149_ir003_bound_reference_variants_and_epoch_response() {
    let (f, mut c, v) = setup();
    let sr = &v["items"][0]["source"];
    crate::source_store::validate_reference(&c, sr).unwrap();
    for (field, value) in [
        ("segmentId", json!("other")),
        ("recordId", json!("other")),
        ("sourceRef", json!("other")),
        ("connectorId", json!("other")),
        ("version", json!(2)),
        ("authorizationGeneration", json!(2)),
        ("scanEpoch", json!(2)),
        ("locator", json!("wrong")),
        ("startScalar", json!(999)),
        ("endScalar", json!(999)),
    ] {
        let mut bad = sr.clone();
        bad[field] = value;
        assert!(
            crate::source_store::validate_reference(&c, &bad).is_err(),
            "{field}"
        );
    }
    let out = send_handoff(&mut c, &send_input(&v), &f, &mut recording(), || {
        let c = open(&f).unwrap();
        c.execute("UPDATE connectors SET epoch=2", []).unwrap();
        c.execute("UPDATE source_files SET seen_epoch=2", [])
            .unwrap();
    })
    .unwrap();
    let stored = required(
        &c,
        "derivations",
        out["answerId"].as_str().unwrap(),
        "answer_missing",
    )
    .unwrap();
    assert_eq!(stored["status"], "stale");
    assert_eq!(stored["citations"][0]["availability"], "stale");
    assert_eq!(
        answer(&c, out["dispatchId"].as_str().unwrap()).unwrap()["validity"],
        "stale"
    );
}

#[test]
fn p149_ir004_transport_receipt_holds_then_releases_coordinator() {
    struct ReceiptPort {
        f: String,
        expected: String,
        calls: usize,
    }
    impl ModelPort for ReceiptPort {
        fn generate(&mut self, _: &str, _: &[u8]) -> R<ModelResponse> {
            panic!("receipt entry required")
        }
        fn generate_with_receipt(
            &mut self,
            body: &str,
            _: &[u8],
            received: &mut dyn FnMut(),
        ) -> R<ModelResponse> {
            assert_eq!(body, self.expected);
            assert!(matches!(
                COORDINATOR.try_lock(),
                Err(std::sync::TryLockError::WouldBlock)
            ));
            let c = open(&self.f).unwrap();
            assert!(all(&c, "packets")
                .unwrap()
                .iter()
                .any(|p| p["deliveryState"] == "dispatching"));
            assert!(c.is_autocommit());
            self.calls += 1; // Explicit bounded in-memory receipt, before any response work.
            received();
            {
                let _guard = COORDINATOR.try_lock().expect("lock released on receipt");
                let mut c = open(&self.f).unwrap();
                let lease = crate::source_api::lease(&c, "directory").unwrap();
                crate::source_store::control(&mut c, &lease, "ir-late-revoke", "disconnect")
                    .unwrap();
            }
            Ok(ModelResponse {
                text: "History [C1]".into(),
                usage: None,
            })
        }
    }
    let (f, c, v) = setup();
    drop(c);
    let mut port = ReceiptPort {
        f: f.clone(),
        expected: v["bodyJson"].as_str().unwrap().into(),
        calls: 0,
    };
    let out = dispatch_using(
        "send_source_ai_request",
        request("confirm_send", send_input(&v)),
        &f,
        Some(&mut port),
    )
    .unwrap();
    assert_eq!(port.calls, 1);
    let c = open(&f).unwrap();
    let stored = required(
        &c,
        "derivations",
        out["answerId"].as_str().unwrap(),
        "answer_missing",
    )
    .unwrap();
    assert_eq!(stored["status"], "stale");
    assert_eq!(stored["citations"][0]["availability"], "revoked");
}

#[test]
fn p149_ir003_epoch_change_after_success_invalidates_read() {
    let (f, mut c, v) = setup();
    let out = send_with_port(&mut c, &send_input(&v), &f, &mut recording()).unwrap();
    let dispatch = out["dispatchId"].as_str().unwrap();
    assert_eq!(answer(&c, dispatch).unwrap()["validity"], "candidate");
    c.execute("UPDATE connectors SET epoch=2", []).unwrap();
    c.execute("UPDATE source_files SET seen_epoch=2", [])
        .unwrap();
    let current = answer(&c, dispatch).unwrap();
    assert_eq!(current["validity"], "stale");
    assert_eq!(current["citations"][0]["availability"], "stale");
}

#[test]
fn p149_health_samples_are_not_disclosed_by_public_source_preview() {
 let (f,mut c,original)=setup();
 let e=json!({"schema":"health-envelope-v1","batchId":"health-guard","exportedAtMs":1788825600000i64,"windowStartMs":1788739200000i64,"windowEndMs":1788825600000i64,"timezoneOffsetMinutes":0,"source":{"id":"healthwatch","name":"Paper crane health only"},"samples":[{"sampleId":"sleep","revision":1,"metric":"sleep","startMs":1788739200000i64,"endMs":1788742800000i64,"value":3600000,"unit":"milliseconds"}]});
 crate::health_ingestion::ingest(&mut crate::health_ingestion::SqliteHealth(&mut c),&serde_json::to_vec(&e).unwrap(),1788825601000).unwrap();
 let preview=call(&f,"assemble_global_ai_context","prepare_source_preview",json!({"requestId":"health-guard-preview","conversationId":"source-chat","turnId":"turn-1","expectedQuestionVersion":1,"excludedSegmentIds":[]}));
 assert_eq!(preview["items"],original["items"]);
 assert!(!preview["bodyJson"].as_str().unwrap().contains("healthwatch"));
 assert!(!preview["bodyJson"].as_str().unwrap().contains("3600000"));
 // Remove the only notebook segment: the health source must not fill the empty context.
 let absent=call(&f,"assemble_global_ai_context","prepare_source_preview",json!({"requestId":"health-guard-absent","conversationId":"source-chat","turnId":"turn-1","expectedQuestionVersion":1,"excludedSegmentIds":[original["items"][0]["source"]["segmentId"]]}));
 assert_eq!(absent["state"],"no_match");assert!(absent.get("confirmationToken").is_none());
}
