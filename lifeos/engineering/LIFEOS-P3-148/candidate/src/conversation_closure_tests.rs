// Same authorized synthetic fixture helpers as p148_tests. No real adapters.
fn request(op: &str, payload: Value) -> Request {
    Request {
        version: if op == "confirm_send" { 1 } else { 3 },
        operation: op.into(),
        payload,
    }
}
fn preview_input(name: &str) -> Value {
    json!({"requestId":name,"conversationId":"source-chat","turnId":"turn-1","expectedQuestionVersion":1,"excludedSegmentIds":[]})
}
fn recording() -> Recording {
    Recording {
        calls: 0,
        body: String::new(),
        failure: None,
        output: "Answer [C1]".into(),
    }
}

#[test]
fn p148_closure_preview_operations_and_no_match() {
    for action in [
        "cancel",
        "remove",
        "rebuild",
        "replace",
        "select",
        "question-version",
    ] {
        let (f, mut c, v) = setup();
        match action {
            "cancel" => {
                call(
                    &f,
                    "assemble_global_ai_context",
                    "cancel_source_preview",
                    json!({"requestId":"cancel-action","previewId":v["previewId"],"expectedPreviewRevision":1}),
                );
            }
            "remove" | "rebuild" => {
                let mut p = preview_input("rebuild-action");
                if action == "remove" {
                    p["excludedSegmentIds"] = json!([v["items"][0]["source"]["segmentId"]]);
                }
                let fresh = call(
                    &f,
                    "assemble_global_ai_context",
                    "prepare_source_preview",
                    p,
                );
                if action == "remove" {
                    assert_eq!(fresh["state"], "no_match");
                }
            }
            "replace" => {
                call(
                    &f,
                    "save_ai_provider_credential",
                    "replace_credential",
                    json!({"requestId":"replace-action","profileId":"deepseek-default","expectedCredentialRevision":1,"apiKey":"synthetic-replacement"}),
                );
            }
            "select" => {
                let s = provider_store::settings(&f).unwrap();
                call(
                    &f,
                    "save_ai_provider_settings",
                    "select_model",
                    json!({"requestId":"select-action","profileId":"deepseek-default","expectedProfileRevision":s["profileRevision"],"testReceiptId":"test","modelId":"deepseek-synthetic-v1"}),
                );
            }
            _ => {
                c.execute("UPDATE records SET body=json_set(body,'$.version',2) WHERE json_extract(body,'$.kind')='source_ai_question'",[]).unwrap();
            }
        }
        let mut port = recording();
        assert!(
            send_with_port(&mut c, &send_input(&v), &f, &mut port).is_err(),
            "{action}"
        );
        assert_eq!(port.calls, 0);
    }
    for text in ["!!!", "unrelated gardening"] {
        let (f, mut c, _) = setup();
        c.execute("UPDATE records SET body=json_set(body,'$.text',?1) WHERE json_extract(body,'$.kind')='source_ai_question'",[text]).unwrap();
        let v = prepare(&c, &preview_input("no-match"), &f).unwrap();
        assert_eq!(v["state"], "no_match");
        assert!(v.get("confirmationToken").is_none());
        let mut input = send_input(&v);
        input["confirmationToken"] = json!("fictional-token");
        let mut port = recording();
        assert!(send_with_port(&mut c, &input, &f, &mut port).is_err());
        assert_eq!(port.calls, 0);
    }
}

#[test]
fn p148_closure_feedback_decisions_and_transaction_rollback() {
    let (f, mut c, v) = setup();
    let out = send_with_port(&mut c, &send_input(&v), &f, &mut recording()).unwrap();
    let a = answer(&c, out["dispatchId"].as_str().unwrap()).unwrap();
    let records_before = all(&c, "records").unwrap();
    for (i, decision) in ["helpful", "reject"].iter().enumerate() {
        call(
            &f,
            "decide_understanding_feedback",
            "answer_feedback",
            json!({"requestId":format!("decision-{i}"),"answerId":a["answerId"],"expectedAnswerRevision":i+1,"decision":decision}),
        );
        assert_eq!(all(&c, "records").unwrap(), records_before);
        assert_eq!(
            answer(&c, out["dispatchId"].as_str().unwrap()).unwrap()["confirmed"],
            false
        );
    }
    let counts = |c: &Connection| {
        ["records", "feedback", "derivations", "packets"].map(|t| all(c, t).unwrap())
    };
    let before = counts(&c);
    let p = json!({"requestId":"atomic-correct","answerId":a["answerId"],"expectedAnswerRevision":3,"decision":"correct","correctionText":"Sort by material","affectedCitationIds":["C1"]});
    c.execute_batch("CREATE TRIGGER fail_feedback BEFORE INSERT ON feedback BEGIN SELECT RAISE(ABORT,'synthetic feedback failure'); END;").unwrap();
    assert!(dispatch(
        "decide_understanding_feedback",
        request("answer_feedback", p.clone()),
        &f
    )
    .is_err());
    assert_eq!(counts(&c), before);
    c.execute_batch("DROP TRIGGER fail_feedback").unwrap();
    let mut stale = p.clone();
    stale["expectedAnswerRevision"] = json!(1);
    assert_eq!(
        dispatch(
            "decide_understanding_feedback",
            request("answer_feedback", stale),
            &f
        )
        .unwrap_err()
        .code,
        "answer_revision_conflict"
    );
    assert_eq!(counts(&c), before);
    // Another answer owns C2; target answer only owns C1.
    let mut other = get(&c, "derivations", a["answerId"].as_str().unwrap())
        .unwrap()
        .unwrap();
    other["id"] = json!("other");
    other["citations"][0]["citationId"] = json!("C2");
    put(&c, "derivations", "other", &other).unwrap();
    let before = counts(&c);
    let mut foreign = p.clone();
    foreign["affectedCitationIds"] = json!(["C2"]);
    assert_eq!(
        dispatch(
            "decide_understanding_feedback",
            request("answer_feedback", foreign),
            &f
        )
        .unwrap_err()
        .code,
        "feedback_scope_rejected"
    );
    assert_eq!(counts(&c), before);
    call(&f, "decide_understanding_feedback", "answer_feedback", p);
}

#[test]
fn p148_closure_configuration_private_key_and_restricted_filters() {
    for variant in ["configuration", "private-key", "restricted"] {
        let (f, c, _) = setup();
        match variant {
            "configuration" => {
                c.execute(
                    "UPDATE source_files SET external_ref='.obsidian/config.json'",
                    [],
                )
                .unwrap();
            }
            "private-key" => {
                c.execute("UPDATE records SET body=json_set(body,'$.text','paper crane -----BEGIN PRIVATE KEY----- fictional') WHERE json_extract(body,'$.sourceFile') IS NOT NULL",[]).unwrap();
            }
            _ => {
                c.execute("UPDATE source_files SET parse_state='restricted'", [])
                    .unwrap();
            }
        }
        let v = prepare(&c, &preview_input("filter"), &f).unwrap();
        assert_eq!(v["state"], "no_match");
        assert!(v["items"].as_array().unwrap().is_empty());
    }
}

#[test]
fn p148_closure_exact_serialized_budget_and_multiple_corrections() {
    let (f, c, v) = setup();
    for len in [800, 801] {
        let raw = format!("paper crane{}", "x".repeat(len - 11));
        c.execute("UPDATE records SET body=json_set(body,'$.text',?1) WHERE json_extract(body,'$.sourceFile') IS NOT NULL",[&raw]).unwrap();
        c.execute("UPDATE source_segments SET text=?1", [&raw])
            .unwrap();
        let p = prepare(&c, &preview_input("window"), &f).unwrap();
        assert_eq!(p["items"][0]["text"].as_str().unwrap().chars().count(), 800);
        assert_eq!(p["items"][0]["source"]["endScalar"], 800);
    }
    let raw = format!("paper crane{}", "\u{1}".repeat(789));
    c.execute("UPDATE records SET body=json_set(body,'$.text',?1) WHERE json_extract(body,'$.sourceFile') IS NOT NULL",[&raw]).unwrap();
    c.execute("UPDATE source_segments SET text=?1", [&raw])
        .unwrap();
    let correction = json!({"id":"budget-correction","schemaVersion":3,"kind":"source_ai_correction","status":"active","conversationId":"source-chat","text":"\u{1}".repeat(2000),"affectedInputRefs":[{"id":v["items"][0]["source"]["recordId"]}]});
    put(&c, "records", "budget-correction", &correction).unwrap();
    let set_question = |s: String| {
        c.execute("UPDATE records SET body=json_set(body,'$.text',?1) WHERE json_extract(body,'$.kind')='source_ai_question'",[s]).unwrap()
    };
    let mut low = 0;
    let mut high = 1901;
    while low + 1 < high {
        let mid = (low + high) / 2;
        set_question(format!("paper crane{}", "\u{1}".repeat(mid)));
        match prepare(&c, &preview_input("exact-budget"), &f) {
            Ok(_) => low = mid,
            Err(e) => {
                assert_eq!(e.code, "context_budget_rejected");
                high = mid;
            }
        }
    }
    let base = format!("paper crane{}", "\u{1}".repeat(low));
    set_question(base.clone());
    let p = prepare(&c, &preview_input("last-fit"), &f).unwrap();
    let padding = 24576 - p["bodyJson"].as_str().unwrap().len();
    assert!(padding < 6);
    set_question(format!("{base}{}", "x".repeat(padding)));
    let p = prepare(&c, &preview_input("exact-fit"), &f).unwrap();
    assert_eq!(p["bodyJson"].as_str().unwrap().len(), 24576);
    set_question(format!("{base}{}", "x".repeat(padding + 1)));
    assert_eq!(
        prepare(&c, &preview_input("over-one"), &f)
            .unwrap_err()
            .code,
        "context_budget_rejected"
    );
    set_question("paper crane".into());
    let mut second = correction;
    second["id"] = json!("second-correction");
    second["text"] = json!("x");
    put(&c, "records", "second-correction", &second).unwrap();
    assert_eq!(
        prepare(&c, &preview_input("correction-sum"), &f)
            .unwrap_err()
            .code,
        "context_budget_rejected"
    );
}

#[test]
fn p148_closure_crash_child() {
    let Ok(f) = std::env::var("P148_TEST_CRASH_FIXTURE") else {
        return;
    };
    // Test executable only; the production App contains neither this entry nor env switch.
    call(
        &f,
        "get_context_recovery",
        "open_conversation",
        json!({"requestId":"child-open","conversationId":"source-chat"}),
    );
    let v = call(
        &f,
        "assemble_global_ai_context",
        "prepare_source_preview",
        preview_input("child-preview"),
    );
    struct ExitAtModel;
    impl ModelPort for ExitAtModel {
        fn generate(&mut self, _: &str, _: &[u8]) -> R<ModelResponse> {
            println!("SYNTHETIC_MODEL_ENTERED_ONCE");
            std::process::exit(77)
        }
    }
    let _ = dispatch_using(
        "send_source_ai_request",
        request("confirm_send", send_input(&v)),
        &f,
        Some(&mut ExitAtModel),
    );
    panic!("expected controlled child exit");
}

#[test]
fn p148_closure_process_exit_after_dispatch_commit_and_explicit_retry() {
    let (f, c, _) = setup();
    drop(c);
    INSTANCE_LOCKS.get().unwrap().lock().unwrap().remove(&f);
    ACTIVE_CONVERSATIONS
        .get()
        .unwrap()
        .lock()
        .unwrap()
        .remove(&f);
    let child = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "conversation_store::p148_tests::p148_closure_crash_child",
            "--nocapture",
            "--test-threads=1",
        ])
        .env("P148_TEST_CRASH_FIXTURE", &f)
        .output()
        .unwrap();
    assert_eq!(child.status.code(), Some(77));
    assert_eq!(
        String::from_utf8_lossy(&child.stdout)
            .matches("SYNTHETIC_MODEL_ENTERED_ONCE")
            .count(),
        1
    );
    let c = open(&f).unwrap();
    let interrupted = all(&c, "packets")
        .unwrap()
        .into_iter()
        .find(|p| p["deliveryState"] == "dispatching")
        .unwrap();
    drop(c);
    call(
        &f,
        "get_context_recovery",
        "open_conversation",
        json!({"requestId":"parent-resume","conversationId":"source-chat"}),
    );
    let mut port = recording();
    for _ in 0..3 {
        let a = dispatch_using(
            "get_evidence_backed_understanding",
            request(
                "read_answer",
                json!({"dispatchId":interrupted["dispatchId"]}),
            ),
            &f,
            Some(&mut port),
        )
        .unwrap();
        assert_eq!(a["state"], "outcome_unknown");
    }
    let replay = dispatch_using(
        "send_source_ai_request",
        request("confirm_send", send_input(&interrupted)),
        &f,
        Some(&mut port),
    )
    .unwrap();
    assert_eq!(replay["state"], "outcome_unknown");
    assert_eq!(port.calls, 0);
    let fresh = call(
        &f,
        "assemble_global_ai_context",
        "prepare_source_preview",
        preview_input("manual-new-preview"),
    );
    let mut p = send_input(&fresh);
    p["requestId"] = json!("manual-new-attempt");
    assert_eq!(
        dispatch_using(
            "send_source_ai_request",
            request("confirm_send", p),
            &f,
            Some(&mut port)
        )
        .unwrap()["state"],
        "succeeded"
    );
    assert_eq!(port.calls, 1);
}

#[test]
fn p148_closure_source_query_returns_eight_at_most() {
    let (f, c, _) = setup();
    let original: Value = c
        .query_row(
            "SELECT body FROM records WHERE json_extract(body,'$.sourceFile') IS NOT NULL LIMIT 1",
            [],
            |r| r.get::<_, String>(0),
        )
        .map(|s| serde_json::from_str(&s).unwrap())
        .unwrap();
    for i in 1..30 {
        let id = format!("extra-record-{i}");
        let mut row = original.clone();
        row["id"] = json!(id);
        row["externalId"] = json!(format!("extra-{i}"));
        row["text"] = json!("paper crane drawings");
        put(&c, "records", &id, &row).unwrap();
        c.execute("INSERT INTO source_segments VALUES(?1,'fiction-file',1,?2,'line:1','paper crane drawings',?3)",params![format!("extra-segment-{i}"),i,id]).unwrap();
    }
    let lease = crate::source_api::lease(&c, "directory").unwrap();
    let rows = crate::source_store::search(&c, &lease, "paper crane").unwrap();
    assert_eq!(rows.len(), 8);
    let v = prepare(&c, &preview_input("bounded-query"), &f).unwrap();
    assert_eq!(v["items"].as_array().unwrap().len(), 3);
}

#[test]
fn p148_closure_revocation_barrier_before_permission_consumption() {
    let (f, c, v) = setup();
    drop(c);
    let ready = std::sync::Arc::new(std::sync::Barrier::new(2));
    let rr = ready.clone();
    let ff = f.clone();
    let revoker = std::thread::spawn(move || {
        let _guard = COORDINATOR.lock().unwrap();
        let mut c = open(&ff).unwrap();
        let l = crate::source_api::lease(&c, "directory").unwrap();
        crate::source_store::control(&mut c, &l, "ordered-revoke", "disconnect").unwrap();
        rr.wait();
    });
    ready.wait();
    let mut port = recording();
    let result = dispatch_using(
        "send_source_ai_request",
        request("confirm_send", send_input(&v)),
        &f,
        Some(&mut port),
    );
    revoker.join().unwrap();
    assert!(result.is_err());
    assert_eq!(port.calls, 0);
}

#[test]
fn p148_closure_draft_revision_and_cross_session_writes() {
    let (f, c, _) = setup();
    let p = json!({"requestId":"pending-draft","draftId":"pending-draft","conversationId":"source-chat","turnId":"pending-turn","revision":2,"text":"fiction pending"});
    call(&f, "capture_record", "draft_question", p.clone());
    let before = all(&c, "drafts").unwrap();
    let mut stale = p.clone();
    stale["requestId"] = json!("old-revision");
    stale["revision"] = json!(1);
    assert_eq!(
        dispatch("capture_record", request("draft_question", stale), &f)
            .unwrap_err()
            .code,
        "draft_stale"
    );
    let mut cross = p.clone();
    cross["requestId"] = json!("cross-session");
    cross["conversationId"] = json!("other-chat");
    assert_eq!(
        dispatch("capture_record", request("draft_question", cross), &f)
            .unwrap_err()
            .code,
        "authorization_rejected"
    );
    let mut conflict = p;
    conflict["text"] = json!("changed same request");
    assert_eq!(
        dispatch("capture_record", request("draft_question", conflict), &f)
            .unwrap_err()
            .code,
        "idempotency_conflict"
    );
    assert_eq!(all(&c, "drafts").unwrap(), before);
    for t in ["", "   "] {
        assert!(text(&json!({"text":t}), "text", false).is_err());
    }
    assert!(text(&json!({"text":""}), "text", true).is_ok());
}

#[test]
fn p148_closure_real_coordinator_duplicate_and_revocation_barriers() {
    use std::sync::{
        atomic::{AtomicUsize, Ordering},
        mpsc, Arc, Barrier,
    };
    struct Blocking {
        calls: Arc<AtomicUsize>,
        entered: mpsc::Sender<()>,
        release: Arc<Barrier>,
    }
    impl ModelPort for Blocking {
        fn generate(&mut self, _: &str, _: &[u8]) -> R<ModelResponse> {
            self.calls.fetch_add(1, Ordering::SeqCst);
            self.entered.send(()).unwrap();
            self.release.wait();
            Ok(ModelResponse {
                text: "Answer [C1]".into(),
                usage: None,
            })
        }
    }
    for revoke in [false, true] {
        let (f, c, v) = setup();
        drop(c);
        let calls = Arc::new(AtomicUsize::new(0));
        let release = Arc::new(Barrier::new(2));
        let start = Arc::new(Barrier::new(2));
        let (tx, rx) = mpsc::channel();
        let ff = f.clone();
        let vv = v.clone();
        let cc = calls.clone();
        let rr = release.clone();
        let ss = start.clone();
        let first = std::thread::spawn(move || {
            ss.wait();
            let mut port = Blocking {
                calls: cc,
                entered: tx,
                release: rr,
            };
            dispatch_using(
                "send_source_ai_request",
                request("confirm_send", send_input(&vv)),
                &ff,
                Some(&mut port),
            )
        });
        start.wait();
        rx.recv_timeout(std::time::Duration::from_secs(5)).unwrap();
        // First dispatch has committed and released the actual coordinator while ModelPort waits.
        let mut second = send_input(&v);
        second["requestId"] = json!("concurrent-second");
        let mut port = recording();
        let duplicate = dispatch_using(
            "send_source_ai_request",
            request("confirm_send", second),
            &f,
            Some(&mut port),
        )
        .unwrap();
        assert_eq!(duplicate["state"], "dispatching");
        assert_eq!(port.calls, 0);
        if revoke {
            let _guard = COORDINATOR.lock().unwrap();
            let mut c = open(&f).unwrap();
            let lease = crate::source_api::lease(&c, "directory").unwrap();
            crate::source_store::control(&mut c, &lease, "revoke-during-model", "disconnect")
                .unwrap();
        }
        release.wait();
        let out = first.join().unwrap().unwrap();
        assert_eq!(out["dispatchId"], duplicate["dispatchId"]);
        assert_eq!(calls.load(Ordering::SeqCst), 1);
        let c = open(&f).unwrap();
        assert_eq!(
            answer(&c, out["dispatchId"].as_str().unwrap()).unwrap()["validity"],
            if revoke { "stale" } else { "candidate" }
        );
    }
}

#[test]
fn p148_closure_structure_and_citation_version_rejection() {
    for mutation in ["missing-table", "unknown-schema"] {
        let (f, c, _) = setup();
        if mutation == "missing-table" {
            c.execute_batch("DROP TABLE source_cursors").unwrap();
        } else {
            c.execute(
                "UPDATE records SET body=json_set(body,'$.schemaVersion',999)",
                [],
            )
            .unwrap();
        }
        assert_eq!(open(&f).unwrap_err().code, "store_contract_mismatch");
    }
    let (f, mut c, v) = setup();
    let sr = &v["items"][0]["source"];
    let lease = crate::source_api::lease(&c, "directory").unwrap();
    assert!(
        crate::source_store::evidence(&c, &lease, sr["sourceRef"].as_str().unwrap(), 1, 0).is_ok()
    );
    c.execute("UPDATE source_files SET version=2", []).unwrap();
    assert!(
        crate::source_store::evidence(&c, &lease, sr["sourceRef"].as_str().unwrap(), 1, 0).is_err()
    );
    crate::source_store::control(&mut c, &lease, "revoke-detail", "disconnect").unwrap();
    assert!(
        crate::source_store::evidence(&c, &lease, sr["sourceRef"].as_str().unwrap(), 2, 0).is_err()
    );
    drop(f);
}
