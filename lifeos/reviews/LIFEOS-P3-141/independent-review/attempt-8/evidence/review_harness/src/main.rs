// This review-owned harness deliberately includes production code without
// enabling its `cfg(test)` modules. All requests and assertions below are
// authored for attempt-8 and use only the disposable controlled root.
include!("/private/tmp/lifeos-p3-141-controlled-pilot-v1/review-harness-source/runtime_under_test.rs");

const BASE: &str = "/private/tmp/lifeos-p3-141-controlled-pilot-v1/review-harness-cases";

fn clean_case(name: &str, mode: InputMode) -> Paths {
    let root = PathBuf::from(BASE).join(name);
    let _ = fs::remove_dir_all(&root);
    let _ = fs::remove_file(&root);
    if mode == InputMode::Synthetic { fs::create_dir_all(&root).expect("synthetic root"); }
    Paths { db: root.join(DB), root, mode }
}

fn real_capture(key: &str) -> CaptureRequest {
    CaptureRequest { text: "attempt-8 synthetic Work verification".into(), key: key.into() }
}

fn memory_request(id: &str, domain: memory_context::Domain, statement: &str, kind: &str) -> memory_context::DurableMemoryRequest {
    memory_context::DurableMemoryRequest {
        operation: memory_context::MemoryOperation::Create, memory_id: id.into(), replacement_id: None,
        statement: Some(statement.into()), memory_type: Some(kind.into()),
        source_refs: Some(vec!["source:synthetic:memory-fixture".into()]), observed_at_ms: None,
        domain, scope: "person".into(), expected_generation: None, idempotency_key: format!("attempt-8-{id}"),
    }
}

fn confirm_memory(paths: &Paths, id: &str, generation: i64) {
    let result = memory_context::upsert(paths, memory_context::DurableMemoryRequest {
        operation: memory_context::MemoryOperation::Confirm, memory_id: id.into(), replacement_id: None,
        statement: None, memory_type: None, source_refs: None, observed_at_ms: None,
        domain: memory_context::Domain::Person, scope: "person".into(), expected_generation: Some(generation),
        idempotency_key: format!("attempt-8-confirm-{id}"),
    }).expect("confirmed synthetic memory");
    assert_eq!(result.validity, "active");
}

fn resolver_counts(paths: &Paths) -> (i64, i64, i64, i64, i64) {
    let conn = read(paths).expect("read review db");
    (
        conn.query_row("SELECT count(*) FROM context_requests", [], |r| r.get(0)).unwrap(),
        conn.query_row("SELECT count(*) FROM context_receipt_items", [], |r| r.get(0)).unwrap(),
        conn.query_row("SELECT count(*) FROM snapshot_slices", [], |r| r.get(0)).unwrap(),
        conn.query_row("SELECT count(*) FROM memory_context_audit", [], |r| r.get(0)).unwrap(),
        conn.query_row("SELECT count(*) FROM durable_memories", [], |r| r.get(0)).unwrap(),
    )
}

fn root_db_link_type_prewrite() {
    let root_file = clean_case("root-file", InputMode::Real);
    fs::write(&root_file.root, b"attempt-8-root-sentinel").unwrap();
    let before = fs::read(&root_file.root).unwrap();
    let error = capture(&root_file, &real_capture("p3-141-real-ui-attempt-8-root-file")).unwrap_err();
    assert_eq!(error.code, "runtime_root_type_rejected");
    assert_eq!(before, fs::read(&root_file.root).unwrap());
    fs::remove_file(&root_file.root).unwrap();

    let db_directory = clean_case("db-directory", InputMode::Real);
    fs::create_dir_all(&db_directory.root).unwrap();
    fs::create_dir(&db_directory.db).unwrap();
    let error = capture(&db_directory, &real_capture("p3-141-real-ui-attempt-8-db-directory")).unwrap_err();
    assert_eq!(error.code, "real_root_ownership_missing");
    assert!(db_directory.db.is_dir());
    fs::remove_dir_all(&db_directory.root).unwrap();
}

fn work_limit_and_restart_no_duplicate() {
    // Contract values are mode-specific: real controlled use permits fourteen
    // total Work records but still caps a day at one; the isolated synthetic
    // fixture remains deliberately narrower.
    assert_eq!(InputMode::Real.limit(), 14);
    assert_eq!(InputMode::Synthetic.limit(), 2);
    let paths = clean_case("work-limit", InputMode::Real);
    let first = capture(&paths, &real_capture("p3-141-real-ui-attempt-8-work-one")).expect("first Work capture");
    let before: i64 = read(&paths).unwrap().query_row("SELECT count(*) FROM captures", [], |r| r.get(0)).unwrap();
    let repeated = capture(&paths, &real_capture("p3-141-real-ui-attempt-8-work-one")).expect("same request idempotency");
    assert_eq!(first.record.id, repeated.record.id);
    let after_repeat: i64 = read(&paths).unwrap().query_row("SELECT count(*) FROM captures", [], |r| r.get(0)).unwrap();
    assert_eq!(before, after_repeat);
    let daily = capture(&paths, &real_capture("p3-141-real-ui-attempt-8-work-two")).unwrap_err();
    assert_eq!(daily.code, "daily_work_limit_rejected");
    let after_reject: i64 = read(&paths).unwrap().query_row("SELECT count(*) FROM captures", [], |r| r.get(0)).unwrap();
    assert_eq!(before, after_reject);
    let reopened = read(&paths).expect("restart read");
    let captures: i64 = reopened.query_row("SELECT count(*) FROM captures", [], |r| r.get(0)).unwrap();
    drop(reopened);
    assert_eq!(captures, 1);
    fs::remove_dir_all(&paths.root).unwrap();
}

fn resolver_health_and_fail_closed() {
    let paths = clean_case("resolver", InputMode::Synthetic);
    let person = memory_context::upsert(&paths, memory_request("memory:synthetic:person", memory_context::Domain::Person, "Synthetic Person: prefers concise daily planning.", "identity")).unwrap();
    confirm_memory(&paths, "memory:synthetic:person", person.generation);
    let work = memory_context::upsert(&paths, memory_request("memory:synthetic:work", memory_context::Domain::Work, "Synthetic Work: weekday focus block supports review planning.", "preference")).unwrap();
    confirm_memory(&paths, "memory:synthetic:work", work.generation);
    let health = memory_context::upsert(&paths, memory_request("memory:synthetic:health", memory_context::Domain::Health, "Synthetic Health: low-impact recovery only when explicitly authorized.", "constraint")).unwrap();
    confirm_memory(&paths, "memory:synthetic:health", health.generation);
    let resolved = memory_context::resolve(&paths, memory_context::ResolveRequest {
        request_id: "request:synthetic:attempt-8-work".into(), task_type: memory_context::TaskType::Work,
        query_text: "planning".into(), authorization_id: "AUTH-SYN-PERSON-GRANTED".into(), health_necessary: false,
        removed_domains: None, top_k: Some(3), token_budget: Some(256),
    }).expect("authorized minimum disclosure");
    assert_eq!(resolved.model_dispatch_count, 0);
    assert!(resolved.included.len() <= 3);
    assert!(!resolved.included.iter().any(|item| item.reference == "memory:synthetic:health"));
    assert!(resolved.excluded.iter().any(|item| item.reference == "memory:synthetic:health" && item.reason == "domain_not_necessary"));
    let before = resolver_counts(&paths);
    let budget = memory_context::resolve(&paths, memory_context::ResolveRequest {
        request_id: "request:synthetic:attempt-8-budget".into(), task_type: memory_context::TaskType::CrossDomain,
        query_text: "recovery".into(), authorization_id: "AUTH-SYN-CROSS-GRANTED".into(), health_necessary: true,
        removed_domains: None, top_k: Some(3), token_budget: Some(1),
    }).unwrap_err();
    assert_eq!(budget.code, "context_budget_rejected");
    assert_eq!(before, resolver_counts(&paths));
    let denied = memory_context::resolve(&paths, memory_context::ResolveRequest {
        request_id: "request:synthetic:attempt-8-denied".into(), task_type: memory_context::TaskType::Work,
        query_text: "planning".into(), authorization_id: "AUTH-SYN-REVOKED".into(), health_necessary: false,
        removed_domains: None, top_k: Some(3), token_budget: Some(256),
    }).unwrap_err();
    assert_eq!(denied.code, "authorization_rejected");
    assert_eq!(before, resolver_counts(&paths));
    let five = r#"{"operation":"set","state_id":"state:synthetic:health","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:synthetic:memory-fixture"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"attempt-8-health","structured_health":{"sleep_duration_range":"seven_to_nine_hours","energy":3,"soreness_or_pain":false,"training_load":"low","available_time":"under_thirty_minutes"}}"#;
    assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(five).is_ok());
    let free_text = five.replacen("}}", ",\"free_text\":\"rejected\"}}", 1);
    assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(&free_text).is_err());
    fs::remove_dir_all(&paths.root).unwrap();
}

fn provider_closed_set_no_implicit_dispatch() {
    assert_eq!(provider_profiles(), vec!["openai", "anthropic", "ollama", "lm_studio"]);
    let mut state = default_provider_state();
    let error = set_provider_enabled(&mut state, SetProviderEnabledRequest { enabled: true }).unwrap_err();
    assert_eq!(error.code, "provider_enablement_rejected");
    assert!(!state.enabled && state.model_request_count == 0 && state.locked_profile.is_none());
}

fn today_feedback_recompute_and_restart() {
    let paths = clean_case("today", InputMode::Synthetic);
    let first = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
        scenario: Some("normal".into()), counterfactual_case: None, request_id: Some("p3-140:attempt-8-first".into()),
        health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()), feedback: None,
        expected_generation: None, fault: None,
    }).expect("first synthetic Today");
    assert_eq!(first.dispatch.network_dispatch_count, 0);
    let same = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
        scenario: Some("normal".into()), counterfactual_case: None, request_id: Some("p3-140:attempt-8-first".into()),
        health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()), feedback: None,
        expected_generation: None, fault: None,
    }).expect("restart-safe cache");
    assert_eq!(same.request_id, first.request_id);
    let second = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
        scenario: Some("normal".into()), counterfactual_case: None, request_id: Some("p3-140:attempt-8-feedback".into()),
        health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()),
        feedback: Some(today_intelligence::TodayFeedback { result_id: first.results[0].result_id.clone(), decision: today_intelligence::FeedbackDecision::Correct, detail: None }),
        expected_generation: Some(first.snapshot_generation), fault: None,
    }).expect("stale and recompute");
    assert!(second.recomputation.invalidated_refs.contains(&first.results[0].result_id));
    assert_eq!(second.dispatch.model_dispatch_count, 0);
    let safety = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
        scenario: Some("health_stop".into()), counterfactual_case: None, request_id: Some("p3-140:attempt-8-safety".into()),
        health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()), feedback: None,
        expected_generation: None, fault: None,
    }).expect("synthetic safety-stop");
    assert_eq!(safety.results[0].identity, "health_safety_stop");
    assert!(safety.results[0].stop_condition.is_some());
    assert_eq!(safety.dispatch.network_dispatch_count, 0);
    fs::remove_dir_all(&paths.root).unwrap();
}

fn main() {
    fs::create_dir_all(BASE).expect("review base");
    root_db_link_type_prewrite();
    work_limit_and_restart_no_duplicate();
    resolver_health_and_fail_closed();
    provider_closed_set_no_implicit_dispatch();
    today_feedback_recompute_and_restart();
    println!("{{\"verdict\":\"Pass\",\"suite\":\"attempt-8-review-owned-runtime-harness\",\"cases\":[\"root_db_type_prewrite\",\"work_daily_restart\",\"resolver_budget_authorization_health\",\"provider_closed_set_no_implicit_dispatch\",\"today_feedback_recompute_safety_stop\"]}}");
}
