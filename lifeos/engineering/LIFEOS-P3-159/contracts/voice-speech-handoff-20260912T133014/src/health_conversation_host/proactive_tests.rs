use super::*;
#[test]
fn proactive_online_quotas_are_separate_persistent_and_nonrefundable(){
 let s=setup();let at=now();for _ in 0..48{Store::proactive_online_budget(&s.c,at).unwrap();}assert!(Store::proactive_online_budget(&s.c,at).is_err());assert!(Store::proactive_online_budget(&s.c,at-1).is_err());
 for _ in 0..48{Store::proactive_online_budget(&s.c,at+DAY).unwrap();}assert!(Store::proactive_online_budget(&s.c,at+2*DAY).is_err());assert_eq!(get(&s.c,"sources","proactive:budget:B").unwrap().unwrap()["unseenReserved"],0);
}
#[test]
fn proactive_constraint_can_adjust_advice_in_same_response_without_second_request(){
 let s=setup();enable(&s);let raw="今天只有二十分钟";let p=response_plan(&s,raw);let span=json!([{"messageRef":"current","start":0,"end":raw.chars().count()}]);
 let v=json!({"feedback":[{"kind":"context_update","subjectRefs":["s0"],"userEvidenceSpans":span,"value":"今天只有二十分钟","validUntil":day_end(now())},{"kind":"discuss","subjectRefs":["s0"],"userEvidenceSpans":span,"answer":"那就先用二十分钟列出报告结论的三个要点，完整安排保持原样。","relatedToSuggestion":true}]});
 let out=s.proactive_finish_response(&p,Ok(v.to_string())).unwrap();assert_eq!(out["status"],"context_updated");assert!(out["reply"].as_str().unwrap().contains("三个要点"));assert_eq!(budget(&s.c,now()).unwrap().response,1);assert_eq!(Store::actions(&s.c).unwrap().len(),0);assert!(s.proactive_reserve(true).unwrap().is_none());
}
#[test]
fn proactive_metadata_never_contains_disclosure_and_read_polling_never_writes(){
 let s=setup();enable(&s);let p=plan(&s);let metadata=get(&s.c,"sources",p["id"].as_str().unwrap()).unwrap().unwrap();assert!(metadata.get("input").is_none());assert!(metadata.get("snapshot").is_none());assert!(request(&s.c,p["id"].as_str().unwrap()).unwrap().unwrap()["input"]["context"].is_array());
 let before:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();for _ in 0..4{s.proactive_view().unwrap();s.proactive_policy_view().unwrap();}let after:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();assert_eq!(before,after);
}
#[test]
fn proactive_current_limit_and_snooze_are_compatible_in_either_order(){
 let s=setup();enable(&s);let raw="今天只有二十分钟，明天下午再看";let p=response_plan(&s,raw);let span=json!([{"messageRef":"current","start":0,"end":raw.chars().count()}]);
 let v=json!({"feedback":[{"kind":"snooze","subjectRefs":["s0"],"userEvidenceSpans":span,"timeText":"明天下午","intervalStart":now()+DAY,"intervalEnd":now()+DAY+3_600_000,"timezone":"Asia/Shanghai"},{"kind":"context_update","subjectRefs":["s0"],"userEvidenceSpans":span,"value":"今天只有二十分钟","validUntil":day_end(now())}]});
 let out=s.proactive_finish_response(&p,Ok(v.to_string())).unwrap();assert_eq!(out["status"],"snoozed");assert_eq!(current_constraints(&s.c,&["work-report".into()],now()).unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());assert_eq!(s.proactive_view().unwrap()["items"],json!([]));
}
#[test]
fn proactive_correction_retains_original_and_supplies_explicit_replacement(){
 let s=setup();enable(&s);let original=get(&s.c,"records","work-report").unwrap().unwrap();let raw="理解错了，报告结论已经整理完";let p=response_plan(&s,raw);
 let v=json!({"feedback":[{"kind":"correct","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":raw.chars().count()}],"replacementFact":"报告结论已经整理完"}]});
 s.proactive_finish_response(&p,Ok(v.to_string())).unwrap();assert_eq!(get(&s.c,"records","work-report").unwrap().unwrap(),original);let constraints=current_constraints(&s.c,&["work-report".into()],now()).unwrap();assert_eq!(constraints[0]["value"],"报告结论已经整理完");assert_eq!(s.proactive_view().unwrap()["items"],json!([]));
}
#[test]
fn proactive_committed_source_cursor_updates_once_and_preserves_scope(){
 use std::io::Write;
 let s=setup();let file=PathBuf::from(ROOT).join("source-engine/fixtures/app-source").join(format!("proactive-cursor-{}.md",crate::conversation_store::uid("case")));
 let body="项目主动游标测试 alphacursor 完善本轮报告";
 let mut f=fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(&file).unwrap();f.write_all(body.as_bytes()).unwrap();drop(f);
 let dispatch=|cmd:&str,payload:Value|lifeos_source_engine::dispatch(cmd,json!({"version":1,"payload":payload}).to_string().as_bytes(),&s.fixture()).unwrap();
 dispatch("connect_source_directory",json!({"requestId":"cursor-connect"}));
 let wait=||{for _ in 0..150{let st=dispatch("get_source_status",json!({}));if st["connectors"][0]["scanComplete"]==true&&st["connectors"][0]["pending"]==0{return;}std::thread::sleep(std::time::Duration::from_millis(100));}panic!("source completion timeout")};wait();
 s.refresh_notes("项目 alphacursor").unwrap();
 let mut q=s.c.prepare("SELECT body FROM records WHERE json_extract(body,'$.engineRef') IS NOT NULL AND instr(json_extract(body,'$.text'),'alphacursor')>0").unwrap();let rows=q.query_map([],|r|r.get::<_,String>(0)).unwrap().collect::<Result<Vec<_>,_>>().unwrap();drop(q);assert_eq!(rows.len(),1);let record:Value=serde_json::from_str(&rows[0]).unwrap();
 let sid=record["id"].as_str().unwrap();let mut g=grant(&s);g["subjectIds"]=json!([sid]);g["sourceIds"]=json!([record["engineRef"]["sourceRef"]]);s.proactive_set_policy(decode(g.clone()).unwrap(),g).unwrap();
 fs::write(&file,"项目主动游标测试 alphacursor 已明确优先完善结论").unwrap();
 dispatch("control_source_job",json!({"requestId":"cursor-refresh","connectorId":"directory","expectedGeneration":record["engineRef"]["authorizationGeneration"],"action":"refresh"}));wait();
 s.proactive_sync_sources().unwrap();let new=get(&s.c,"records",sid).unwrap().unwrap();assert!(new["version"].as_u64().unwrap()>record["version"].as_u64().unwrap());assert!(new["text"].as_str().unwrap().contains("明确优先"));s.proactive_sync_sources().unwrap();let events=control_rows(&s.c,"sources","proactive_event").unwrap();assert_eq!(events.iter().filter(|e|e["type"]=="source_updated").count(),1);assert_eq!(policy(&s.c).unwrap().subject_ids,vec![sid.to_string()]);fs::remove_file(file).unwrap();
}
fn at(t: i64) {
    TEST_NOW.with(|c| c.set(Some(t)));
}
fn setup() -> Store {
    at(1_800_000_000_000);
    super::super::controlled_tests::store()
}
fn grant(s: &Store) -> Value {
    json!({"requestId":crate::conversation_store::uid("grant"),"expectedRevision":policy(&s.c).unwrap().revision,"enabled":true,"subjectIds":["work-report"],"sourceIds":["work-demo"],"analysisPerDay":12,"responsePerDay":20,"showsPerDay":3,"intervalMinutes":30,"quietStart":22,"quietEnd":8})
}
fn enable(s: &Store) {
    let v = grant(s);
    s.proactive_set_policy(decode(v.clone()).unwrap(), v)
        .unwrap();
}
fn plan(s: &Store) -> Value {
    at(now() + 6000);
    s.proactive_reserve(true)
        .unwrap()
        .expect("expected eligible work")
}
fn suggestion() -> String {
    json!({"kind":"suggestion","subjectRefs":["s0"],"proposal":"先补充评审报告结论，再决定下一步。","whyNow":"当前已确认的工作记录提到报告待完善。","evidenceRefs":["s0"],"inferenceFlags":["inference"]}).to_string()
}
fn response_plan(s: &Store, text: &str) -> Value {
    let p = plan(s);
    let out = s.proactive_finish(&p, Ok(suggestion())).unwrap();
    let input = json!({"requestId":crate::conversation_store::uid("response"),"suggestionId":out["suggestionId"],"expectedRevision":1,"text":text});
    s.proactive_prepare_response(decode(input.clone()).unwrap(), input)
        .unwrap();
    s.proactive_reserve_response(true).unwrap().unwrap()
}
fn mixed_action_case(fail_feedback: bool, stale_basis: bool) {
    use crate::model_port::{ModelPort, ModelResponse};
    use std::sync::{Arc, Mutex};
    let s = setup();
    enable(&s);
    let raw = "请把整理报告记为安排，今天只有二十分钟";
    let p = response_plan(&s, raw);
    let span = json!([{"messageRef":"current","start":0,"end":raw.chars().count()}]);
    let candidate = json!({"feedback":[{"kind":"action_intent","subjectRefs":["s0"],"userEvidenceSpans":span,"candidate":{"operation":"create","content":"整理报告"}},{"kind":"context_update","subjectRefs":["s0"],"userEvidenceSpans":span,"value":"今天只有二十分钟","validUntil":day_end(now())}]});
    let r = s
        .proactive_finish_response(&p, Ok(candidate.to_string()))
        .unwrap();
    assert_eq!(r["status"], "awaiting_action_authorization");
    assert!(Store::actions(&s.c).unwrap().is_empty());
    assert!(current_constraints(&s.c, &["work-report".into()], now())
        .unwrap()
        .is_empty());
    let turn = crate::conversation_store::uid("handoff");
    let call = |s: &Store, command: &str, operation: &str, payload: Value| {
        s.dispatch(
            command,
            json!({"version":8,"operation":operation,"payload":payload})
                .to_string()
                .as_bytes(),
        )
        .unwrap()["result"]
            .clone()
    };
    call(
        &s,
        "capture_record",
        "save_coordination_draft",
        json!({"requestId":crate::conversation_store::uid("draft"),"turnId":turn,"expectedDraftRevision":0,"text":raw}),
    );
    s.proactive_action_handoff(p["id"].as_str().unwrap(), &turn)
        .unwrap();
    let prepared = call(
        &s,
        "resolve_request_context",
        "prepare_coordination_turn",
        json!({"requestId":crate::conversation_store::uid("prepare"),"turnId":turn,"expectedDraftRevision":1}),
    );
    if fail_feedback {
        s.c.execute_batch("CREATE TEMP TRIGGER proactive_feedback_fault BEFORE INSERT ON feedback WHEN json_extract(NEW.body,'$.kind')='proactive_feedback' BEGIN SELECT RAISE(ABORT,'synthetic fault'); END;").unwrap();
    }
    if stale_basis {
        let mut source = get(&s.c, "records", "work-report").unwrap().unwrap();
        source["version"] = json!(2);
        put(&s.c, "records", "work-report", &source).unwrap();
    }
    struct Model(Value);
    impl ModelPort for Model {
        fn generate(&mut self, _: &str, _: &[u8]) -> R<ModelResponse> {
            Ok(ModelResponse {
                text: self.0.to_string(),
                usage: None,
            })
        }
    }
    let mut model = Model(
        json!({"schemaVersion":8,"answerText":"","candidate":{"operation":"create","content":"整理报告","evidenceSpans":span,"sourceRefs":[]}}),
    );
    let shared = Arc::new(Mutex::new(s));
    let preview = &prepared["preview"];
    let result=crate::host_gateway::dispatch_with_port(&shared,"send_source_ai_request",json!({"version":8,"operation":"confirm_coordination_model","payload":{"requestId":crate::conversation_store::uid("confirm"),"sendPreviewId":preview["id"],"expectedRevision":preview["revision"]}}).to_string().as_bytes(),&mut model);
    let s = shared.lock().unwrap();
    if fail_feedback || stale_basis {
        assert!(result.is_err() || result.as_ref().unwrap()["result"]["state"] != "committed");
        assert!(Store::actions(&s.c).unwrap().is_empty());
        assert!(current_constraints(&s.c, &["work-report".into()], now())
            .unwrap()
            .is_empty());
    } else {
        assert_eq!(result.unwrap()["result"]["state"], "committed");
        assert_eq!(Store::actions(&s.c).unwrap().len(), 1);
        let related = related_actions(&s.c, &["work-report".into()]).unwrap();
        assert_eq!(related.len(), 1);
        assert!(subject(&s.c, &related[0], now(), &policy(&s.c).unwrap()).unwrap().is_some());
        assert!(related_actions(&s.c, &["unrelated-project".into()]).unwrap().is_empty());
        assert_eq!(
            current_constraints(&s.c, &["work-report".into()], now())
                .unwrap()
                .len(),
            1
        );
        assert_eq!(
            get(&s.c, "sources", p["id"].as_str().unwrap())
                .unwrap()
                .unwrap()["status"],
            "committed"
        );
    }
}
#[test]
fn proactive_mixed_feedback_uses_original_action_transaction() {
    mixed_action_case(false, false)
}
#[test]
fn proactive_mixed_feedback_fault_rolls_back_original_action() {
    mixed_action_case(true, false)
}
#[test]
fn proactive_snooze_persists_and_due_never_restores_old_words() {
    let s = setup();
    enable(&s);
    let p = response_plan(&s, "明天下午再看");
    let until = now() + DAY;
    let v = json!({"feedback":[{"kind":"snooze","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":6}],"timeText":"明天下午","intervalStart":until,"intervalEnd":until+3_600_000,"timezone":"Asia/Shanghai"}]});
    assert_eq!(
        s.proactive_finish_response(&p, Ok(v.to_string())).unwrap()["status"],
        "snoozed"
    );
    assert_eq!(s.proactive_view().unwrap()["items"], json!([]));
    Store::proactive_recover(&s.c).unwrap();
    at(until - 1);
    s.proactive_reconcile().unwrap();
    assert_eq!(s.proactive_view().unwrap()["items"], json!([]));
    at(until);
    s.proactive_reconcile().unwrap();
    assert_eq!(s.proactive_view().unwrap()["items"], json!([]));
    assert!(control_rows(&s.c, "sources", "proactive_event")
        .unwrap()
        .iter()
        .any(|v| v["type"] == "snooze_due"));
}
#[test]
fn proactive_suppression_survives_foreground_and_same_subject_rephrasing() {
    let s = setup();
    enable(&s);
    let p = response_plan(&s, "以后别提这件事");
    let v = json!({"feedback":[{"kind":"suppress","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":7}],"enabled":true}]});
    assert_eq!(
        s.proactive_finish_response(&p, Ok(v.to_string())).unwrap()["status"],
        "suppressed"
    );
    at(now() + 3_600_000);
    s.proactive_foreground().unwrap();
    at(now() + 6000);
    assert!(s.proactive_reserve(true).unwrap().is_none());
    assert_eq!(Store::actions(&s.c).unwrap().len(), 0);
}
#[test]
fn proactive_feedback_rejects_forged_span_without_partial_write() {
    let s = setup();
    enable(&s);
    let p = response_plan(&s, "理解错了");
    let v = json!({"feedback":[{"kind":"correct","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"source","start":0,"end":3}]}]});
    assert_eq!(
        s.proactive_finish_response(&p, Ok(v.to_string())).unwrap()["status"],
        "failed"
    );
    assert!(control_rows(&s.c, "feedback", "proactive_feedback")
        .unwrap()
        .is_empty());
}
#[test]
fn proactive_default_off_and_frontend_cannot_forge_domain_event() {
    let s = setup();
    assert_eq!(s.proactive_view().unwrap()["items"], json!([]));
    assert!(s.proactive_reserve(true).unwrap().is_none());
    assert!(s.proactive_dispatch("resolve_request_context",json!({"version":"proactive-v1","operation":"proactive_event","payload":{"authorized":true,"type":"source_updated"}})).is_err());
}
#[test]
fn proactive_success_is_durable_single_focus_and_shown_only_once() {
    let s = setup();
    enable(&s);
    let p = plan(&s);
    let out = s.proactive_finish(&p, Ok(suggestion())).unwrap();
    assert_eq!(out["status"], "eligible");
    assert_eq!(budget(&s.c, now()).unwrap().shows, 0);
    let sid = out["suggestionId"].as_str().unwrap();
    s.proactive_shown("show-1", sid, 1).unwrap();
    s.proactive_shown("show-2", sid, 1).unwrap();
    assert_eq!(budget(&s.c, now()).unwrap().shows, 1);
    assert_eq!(
        s.proactive_view().unwrap()["items"]
            .as_array()
            .unwrap()
            .len(),
        1
    );
    assert_eq!(Store::actions(&s.c).unwrap().len(), 0);
}
#[test]
fn proactive_generation_change_rejects_late_result_preserves_budget() {
    let s = setup();
    enable(&s);
    let p = plan(&s);
    let mut v = grant(&s);
    v["enabled"] = json!(false);
    s.proactive_set_policy(decode(v.clone()).unwrap(), v)
        .unwrap();
    let out = s.proactive_finish(&p, Ok(suggestion())).unwrap();
    assert_eq!(out["status"], "cancelled");
    assert_eq!(budget(&s.c, now()).unwrap().analysis, 1);
    assert!(control_rows(&s.c, "derivations", "proactive_suggestion")
        .unwrap()
        .is_empty());
}
#[test]
fn proactive_restarts_unknown_send_is_not_retried() {
    let s = setup();
    enable(&s);
    let p = plan(&s);
    Store::proactive_recover(&s.c).unwrap();
    assert_eq!(
        get(&s.c, "sources", p["id"].as_str().unwrap())
            .unwrap()
            .unwrap()["status"],
        "outcome_unknown"
    );
    assert_eq!(budget(&s.c, now()).unwrap().analysis, 1);
    assert!(s.proactive_reserve(true).unwrap().is_none());
}
#[test]
fn proactive_invalid_model_and_source_change_do_not_write_suggestion() {
    let s = setup();
    enable(&s);
    let p = plan(&s);
    let mut r = get(&s.c, "records", "work-report").unwrap().unwrap();
    r["version"] = json!(2);
    put(&s.c, "records", "work-report", &r).unwrap();
    assert_eq!(
        s.proactive_finish(&p, Ok(suggestion())).unwrap()["errorCode"],
        "proactive_context_stale"
    );
    assert!(control_rows(&s.c, "derivations", "proactive_suggestion")
        .unwrap()
        .is_empty());
}
#[test]
fn proactive_controls_do_not_consume_legacy_pagination() {
    let s = setup();
    let before = list(&s.c, "states", 16).unwrap();
    for n in 0..40 {
        put(
            &s.c,
            "states",
            &format!("proactive:control:{n}"),
            &json!({"kind":"proactive_state","status":"suppressed"}),
        )
        .unwrap();
    }
    assert_eq!(list(&s.c, "states", 16).unwrap(), before);
}
#[test]
fn proactive_no_send_when_hidden_or_dnd_and_clock_rollback_does_not_reset() {
    let s = setup();
    enable(&s);
    at(now() + 6000);
    assert!(s.proactive_reserve(false).unwrap().is_none());
    let p = plan(&s);
    s.proactive_finish(&p, Err(error("provider_timeout")))
        .unwrap();
    let current = now();
    at(current - DAY);
    assert_eq!(budget(&s.c, now()).unwrap().analysis, 1);
    assert!(s.proactive_reserve(true).unwrap().is_none());
}
#[test]
fn proactive_unknown_fields_and_health_scope_rejected() {
    let s = setup();
    let mut v = grant(&s);
    v["authorized"] = json!(true);
    assert!(decode::<PolicyInput>(v).is_err());
    let mut v = grant(&s);
    v["subjectIds"] = json!(["sleep-1"]);
    v["sourceIds"] = json!(["health-demo"]);
    assert!(s
        .proactive_set_policy(decode(v.clone()).unwrap(), v)
        .is_err());
}

#[test]
fn proactive_action_handoff_rechecks_basis_before_original_transaction() {
    mixed_action_case(false, true)
}

#[test]
fn proactive_credential_failure_pauses_until_explicit_restore_without_budget_reset() {
    let s=setup();enable(&s);let p=plan(&s);
    s.proactive_finish(&p,Err(error("credential_unavailable"))).unwrap();
    assert_eq!(s.proactive_pause_reason().unwrap().as_deref(),Some("credential_unavailable"));
    at(now()+3_600_000);s.proactive_foreground().unwrap();
    assert!(s.proactive_reserve(true).unwrap().is_none());
    assert_eq!(budget(&s.c,now()).unwrap().analysis,1);
    enable(&s);assert!(s.proactive_pause_reason().unwrap().is_none());
    assert_eq!(budget(&s.c,now()).unwrap().analysis,1);
}

#[test]
fn proactive_response_preserves_second_subject_identity_and_reference_order() {
    let s=setup();let mut other=get(&s.c,"records","work-report").unwrap().unwrap();other["id"]=json!("work-second");other["text"]=json!("另一项目：准备公开演示");put(&s.c,"records","work-second",&other).unwrap();
    let mut g=grant(&s);g["subjectIds"]=json!(["work-report","work-second"]);s.proactive_set_policy(decode(g.clone()).unwrap(),g).unwrap();
    let p=plan(&s);let mut candidate:Value=serde_json::from_str(&suggestion()).unwrap();candidate["subjectRefs"]=json!(["s1"]);candidate["evidenceRefs"]=json!(["s1"]);
    let result=s.proactive_finish(&p,Ok(candidate.to_string())).unwrap();let raw="这个项目以后不必提醒";
    let input=json!({"requestId":"second-response","suggestionId":result["suggestionId"],"expectedRevision":1,"text":raw});s.proactive_prepare_response(decode(input.clone()).unwrap(),input).unwrap();let response=s.proactive_reserve_response(true).unwrap().unwrap();
    assert_eq!(response["input"]["suggestion"]["subjectRefs"],json!(["s1"]));assert_eq!(response["input"]["context"][1]["ref"],"s1");assert_eq!(response["snapshot"][1]["id"],p["snapshot"][1]["id"]);
    let parsed=json!({"feedback":[{"kind":"suppress","subjectRefs":["s1"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":raw.chars().count()}],"enabled":true}]});
    let out=s.proactive_finish_response(&response,Ok(parsed.to_string())).unwrap();assert_eq!(out["status"],"suppressed");
    assert!(suppressed(&s.c,&[p["snapshot"][1]["id"].as_str().unwrap().into()],now()).unwrap());assert!(!suppressed(&s.c,&[p["snapshot"][0]["id"].as_str().unwrap().into()],now()).unwrap());
}

#[test]
fn proactive_each_projection_write_boundary_rolls_back_and_can_retry_same_receipt() {
    for (table, kind) in [("derivations","proactive_suggestion"),("states","proactive_state"),("sources","proactive_request"),("packets","proactive_packet")] {
        let s=setup();enable(&s);let p=plan(&s);
        let revision:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();
        s.c.execute_batch(&format!("CREATE TEMP TRIGGER proactive_fault BEFORE INSERT ON {table} WHEN json_extract(NEW.body,'$.kind')='{kind}' BEGIN SELECT RAISE(ABORT,'synthetic fault'); END;")).unwrap();
        assert!(s.proactive_finish(&p,Ok(suggestion())).is_err(),"{table}");
        assert!(control_rows(&s.c,"derivations","proactive_suggestion").unwrap().is_empty(),"{table}");
        assert!(control_rows(&s.c,"states","proactive_state").unwrap().is_empty(),"{table}");
        assert_eq!(request(&s.c,p["id"].as_str().unwrap()).unwrap().unwrap()["status"],"reserved");
        assert_eq!(s.c.query_row("SELECT revision FROM meta",[],|r|r.get::<_,i64>(0)).unwrap(),revision);
        s.c.execute_batch("DROP TRIGGER proactive_fault").unwrap();
        let first=s.proactive_finish(&p,Ok(suggestion())).unwrap();let second=s.proactive_finish(&p,Ok(suggestion())).unwrap();assert_eq!(first,second);
        assert_eq!(control_rows(&s.c,"derivations","proactive_suggestion").unwrap().len(),1);
        assert_eq!(budget(&s.c,now()).unwrap().analysis,1);
    }
}
#[test]
fn proactive_invalid_candidate_shapes_never_create_visible_state() {
    for bad in [r#"{"kind":"silence","reasonCode":"no_value","extra":true}"#.to_string(),r#"{"kind":"silence","kind":"suggestion"}"#.to_string(),"null".into(),"[{}]".into(),"{".into(),{
        let mut v:Value=serde_json::from_str(&suggestion()).unwrap();v["evidenceRefs"]=json!(["forged-ref"]);v.to_string()
    },{
        let mut v:Value=serde_json::from_str(&suggestion()).unwrap();v["subjectRefs"]=json!(["s0","s0"]);v.to_string()
    }] {
        let s=setup();enable(&s);let p=plan(&s);let result=s.proactive_finish(&p,Ok(bad)).unwrap();assert_eq!(result["status"],"failed");assert_eq!(s.proactive_view().unwrap()["items"],json!([]));assert_eq!(budget(&s.c,now()).unwrap().analysis,1);
    }
}

#[test]
fn proactive_timezone_change_and_clock_rollback_do_not_reset_usage() {
 let s=setup();enable(&s);let p=plan(&s);s.proactive_finish(&p,Err(error("provider_timeout"))).unwrap();
 let instant=now();civil_clock::TEST_ZONE.with(|z|*z.borrow_mut()="America/New_York".into());
 assert_eq!(budget(&s.c,instant).unwrap().analysis,1);assert_eq!(budget(&s.c,instant-DAY).unwrap().analysis,1);
 civil_clock::TEST_ZONE.with(|z|*z.borrow_mut()="Asia/Shanghai".into());
}

#[test]fn proactive_online_unseen_is_separate_and_shares_daily_limit(){let s=setup();let at=now();for _ in 0..32{Store::proactive_online_budget_phase(&s.c,at,"development").unwrap();}for _ in 0..16{Store::proactive_online_budget_phase(&s.c,at,"unseen").unwrap();}assert!(Store::proactive_online_budget_phase(&s.c,at,"unseen").is_err());for _ in 0..32{Store::proactive_online_budget_phase(&s.c,at+DAY,"unseen").unwrap();}assert!(Store::proactive_online_budget_phase(&s.c,at+2*DAY,"unseen").is_err());assert!(Store::proactive_online_budget_phase(&s.c,at+2*DAY,"borrow").is_err());for _ in 0..48{Store::proactive_online_budget_phase(&s.c,at+2*DAY,"development").unwrap();}for _ in 0..16{Store::proactive_online_budget_phase(&s.c,at+3*DAY,"development").unwrap();}let b=get(&s.c,"sources","proactive:budget:B").unwrap().unwrap();assert_eq!(b["developmentReserved"],96);assert_eq!(b["unseenReserved"],48);assert!(Store::proactive_online_budget_phase(&s.c,at+4*DAY,"development").is_err());}

#[test]fn proactive_response_rechecks_changed_current_constraints(){let s=setup();enable(&s);let raw="先讨论一下";let p=response_plan(&s,raw);let rawref=p["rawRef"].as_str().unwrap();put(&s.c,"states","state:new-limit",&json!({"id":"state:new-limit","rawId":rawref,"kind":"current_state","stateKey":"current_limit","value":"只能先讨论","domain":"work","subjectIds":["work-report"],"generation":1,"status":"active","observedAt":now(),"validUntil":now()+1000,"identity":"user_statement"})).unwrap();let value=json!({"feedback":[{"kind":"discuss","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":5}],"answer":"只讨论","relatedToSuggestion":true}]});let out=s.proactive_finish_response(&p,Ok(value.to_string())).unwrap();assert_eq!(out["errorCode"],"proactive_context_stale");assert!(control_rows(&s.c,"feedback","proactive_feedback").unwrap().is_empty());assert!(Store::actions(&s.c).unwrap().is_empty());}
#[test]fn proactive_feedback_transaction_faults_preserve_raw_and_all_prior_state(){for table in ["feedback","states","sources","packets","requests"]{let s=setup();enable(&s);let raw="今天只有二十分钟";let p=response_plan(&s,raw);let before=control_rows(&s.c,"states","proactive_state").unwrap();let revision:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();s.c.execute_batch(&format!("CREATE TEMP TRIGGER feedback_fault BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'A fault'); END;")).unwrap();let value=json!({"feedback":[{"kind":"context_update","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":raw.chars().count()}],"value":"今天只有二十分钟","validUntil":day_end(now())}]});assert!(s.proactive_finish_response(&p,Ok(value.to_string())).is_err(),"{table}");assert_eq!(control_rows(&s.c,"states","proactive_state").unwrap(),before);assert!(control_rows(&s.c,"feedback","proactive_feedback").unwrap().is_empty());assert_eq!(get(&s.c,"records",p["rawRef"].as_str().unwrap()).unwrap().unwrap()["text"],raw);assert_eq!(s.c.query_row("SELECT revision FROM meta",[],|r|r.get::<_,i64>(0)).unwrap(),revision);s.c.execute_batch("DROP TRIGGER feedback_fault").unwrap();s.proactive_finish_response(&p,Ok(value.to_string())).unwrap();assert_eq!(control_rows(&s.c,"feedback","proactive_feedback").unwrap().len(),1);}}

#[test]fn proactive_constraint_expiry_during_response_rejects_late_result(){let s=setup();enable(&s);let expiry=now()+20000;put(&s.c,"states","state:expiry",&json!({"id":"state:expiry","rawId":"work-report","stateKey":"current_limit","value":"有限合成窗口","subjectIds":["work-report"],"generation":1,"status":"active","observedAt":now(),"validUntil":expiry,"identity":"user_statement"})).unwrap();let p=response_plan(&s,"先讨论一下");assert_eq!(p["constraintSnapshot"].as_array().unwrap().len(),1);at(expiry);let out=s.proactive_finish_response(&p,Ok(json!({"feedback":[{"kind":"discuss","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":5}],"answer":"讨论","relatedToSuggestion":true}]}).to_string())).unwrap();assert_eq!(out["errorCode"],"proactive_context_stale");}
#[test]fn proactive_disable_cancels_queued_response_without_replay_after_reenable(){let s=setup();enable(&s);let p=plan(&s);let out=s.proactive_finish(&p,Ok(suggestion())).unwrap();let input=json!({"requestId":"queued-before-disable","suggestionId":out["suggestionId"],"expectedRevision":1,"text":"先讨论一下"});let queued=s.proactive_prepare_response(decode(input.clone()).unwrap(),input).unwrap();let mut g=grant(&s);g["enabled"]=json!(false);s.proactive_set_policy(decode(g.clone()).unwrap(),g).unwrap();assert_eq!(request(&s.c,queued["requestId"].as_str().unwrap()).unwrap().unwrap()["status"],"cancelled");enable(&s);assert!(s.proactive_reserve_response(true).unwrap().is_none());assert_eq!(budget(&s.c,now()).unwrap().response,0);assert_eq!(get(&s.c,"records",queued["rawRef"].as_str().unwrap()).unwrap().unwrap()["text"],"先讨论一下");}
#[test]fn proactive_analysis_reservation_faults_rollback_consumed_events_and_budget(){for table in ["sources","packets","requests"]{let s=setup();enable(&s);at(now()+6000);let prior=control_rows(&s.c,"sources","proactive_event").unwrap();let revision:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();s.c.execute_batch(&format!("CREATE TEMP TRIGGER reserve_fault BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'A reserve fault'); END;")).unwrap();assert!(s.proactive_reserve(true).is_err());assert_eq!(budget(&s.c,now()).unwrap().analysis,0);assert_eq!(control_rows(&s.c,"sources","proactive_event").unwrap(),prior);assert_eq!(s.c.query_row("SELECT revision FROM meta",[],|r|r.get::<_,i64>(0)).unwrap(),revision);s.c.execute_batch("DROP TRIGGER reserve_fault").unwrap();assert!(s.proactive_reserve(true).unwrap().is_some());assert_eq!(budget(&s.c,now()).unwrap().analysis,1);}}

fn write_boundary_snapshot(s:&Store)->Value{
 let mut out=serde_json::Map::new();
 for table in ["records","memories","states","sources","questions","packets","derivations","feedback","drafts"]{let mut q=s.c.prepare(&format!("SELECT id,body FROM {table} ORDER BY id")).unwrap();let rows=q.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?))).unwrap().collect::<Result<Vec<_>,_>>().unwrap();out.insert(table.into(),json!(rows));}
 let mut q=s.c.prepare("SELECT id,operation,payload,result FROM requests ORDER BY id").unwrap();let rows=q.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?,r.get::<_,String>(2)?,r.get::<_,String>(3)?))).unwrap().collect::<Result<Vec<_>,_>>().unwrap();out.insert("requests".into(),json!(rows));out.insert("revision".into(),json!(s.c.query_row("SELECT revision FROM meta",[],|r|r.get::<_,i64>(0)).unwrap()));json!(out)
}
fn write_fault(s:&Store,table:&str){s.c.execute_batch(&format!("CREATE TEMP TRIGGER boundary_fault BEFORE {} ON {table} BEGIN SELECT RAISE(ABORT,'A write boundary'); END;",if table=="meta"{"UPDATE"}else{"INSERT"})).unwrap();}
#[test]fn proactive_policy_each_write_fault_is_atomic_and_same_request_replays(){for table in ["sources","requests","meta"]{let s=setup();let v=grant(&s);let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(s.proactive_set_policy(decode(v.clone()).unwrap(),v.clone()).is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before,"{table}");s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();let a=s.proactive_set_policy(decode(v.clone()).unwrap(),v.clone()).unwrap();let after=write_boundary_snapshot(&s);assert_eq!(s.proactive_set_policy(decode(v.clone()).unwrap(),v).unwrap(),a);assert_eq!(write_boundary_snapshot(&s),after);}}
#[test]fn proactive_shown_each_write_fault_cannot_consume_a_show(){for table in ["sources","states","requests","meta"]{let s=setup();enable(&s);let p=plan(&s);let result=s.proactive_finish(&p,Ok(suggestion())).unwrap();let sid=result["suggestionId"].as_str().unwrap();let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(s.proactive_shown("show-boundary",sid,1).is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before,"{table}");s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();s.proactive_shown("show-boundary",sid,1).unwrap();s.proactive_shown("show-boundary",sid,1).unwrap();assert_eq!(budget(&s.c,now()).unwrap().shows,1);}}
#[test]fn proactive_capture_each_write_fault_preserves_input_and_idempotency(){for table in ["records","sources","packets","requests","meta"]{let s=setup();enable(&s);let p=plan(&s);let result=s.proactive_finish(&p,Ok(suggestion())).unwrap();let input=json!({"requestId":"capture-boundary","suggestionId":result["suggestionId"],"expectedRevision":1,"text":"先讨论一下"});let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(s.proactive_prepare_response(decode(input.clone()).unwrap(),input.clone()).is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before,"{table}");s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();let first=s.proactive_prepare_response(decode(input.clone()).unwrap(),input.clone()).unwrap();let after=write_boundary_snapshot(&s);assert_eq!(s.proactive_prepare_response(decode(input.clone()).unwrap(),input).unwrap(),first);assert_eq!(write_boundary_snapshot(&s),after);}}

#[test]fn proactive_control_history_never_hides_permanent_suppression(){let s=setup();enable(&s);put(&s.c,"states","permanent-first",&json!({"id":"permanent-first","kind":"proactive_state","status":"suppressed","subjectIds":["work-report"]})).unwrap();for n in 0..1200{put(&s.c,"states",&format!("history-{n}"),&json!({"id":format!("history-{n}"),"kind":"proactive_state","status":"superseded","subjectIds":["other"]})).unwrap();}assert!(suppressed(&s.c,&["work-report".into()],now()).unwrap());assert!(!suppressed(&s.c,&["other".into()],now()).unwrap());assert!(active_control_rows(&s.c,"states","proactive_state",&["eligible","surfaced","snoozed"]).unwrap().is_empty());assert_eq!(s.proactive_view().unwrap()["items"],json!([]));}

#[test]fn proactive_due_action_rechecks_completed_cancelled_expired_and_revoked_after_reopen(){
 for change in ["completed","cancelled","expired","revoked","valid"]{
  let s=setup();let source=get(&s.c,"sources","work-demo").unwrap().unwrap();let action=json!({"id":"action:due-test","version":1,"confirmedContent":"整理合成报告","status":"planned","createdAt":now(),"updatedAt":now(),"confirmationRawRef":"work-report","sourceRefs":[{"id":"work-report","version":1,"authorizationGeneration":source["generation"]}]});
  put(&s.c,"records","action-event:due-test",&json!({"id":"action-event:due-test","kind":"action_event","schemaVersion":8,"action":action})).unwrap();
  let mut g=grant(&s);g["subjectIds"]=json!(["action:due-test"]);s.proactive_set_policy(decode(g.clone()).unwrap(),g).unwrap();
  let p=response_plan(&s,"明天下午再看");let until=now()+DAY;
  s.proactive_finish_response(&p,Ok(json!({"feedback":[{"kind":"snooze","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":6}],"timeText":"明天下午","intervalStart":until,"intervalEnd":until+3_600_000,"timezone":"Asia/Shanghai"}]}).to_string())).unwrap();
  if ["completed","cancelled"].contains(&change){let mut a=action.clone();a["version"]=json!(2);a["status"]=json!(change);put(&s.c,"records","action-event:terminal",&json!({"id":"action-event:terminal","kind":"action_event","schemaVersion":8,"action":a})).unwrap();}
  if change=="expired"{let mut r=get(&s.c,"records","work-report").unwrap().unwrap();r["validUntil"]=json!(until);put(&s.c,"records","work-report",&r).unwrap();}
  if change=="revoked"{let mut r=get(&s.c,"sources","conversation").unwrap().unwrap();r["authorized"]=json!(false);put(&s.c,"sources","conversation",&r).unwrap();}
  let path=PathBuf::from(s.c.path().unwrap());drop(s);let s=Store::open(&path).unwrap();at(until-1);s.proactive_reconcile().unwrap();assert_eq!(s.proactive_view().unwrap()["items"],json!([]));at(until);s.proactive_reconcile().unwrap();assert_eq!(s.proactive_view().unwrap()["items"],json!([]));
  let due=control_rows(&s.c,"sources","proactive_event").unwrap().iter().filter(|v|v["type"]=="snooze_due").count();assert_eq!(due,usize::from(change=="valid"),"{change}");let state=get(&s.c,"states",&format!("proactive:state:{}",p["suggestionId"].as_str().unwrap())).unwrap();assert!(state.is_some(),"state remains durable");
 }
}

#[test]fn proactive_due_reconcile_write_faults_keep_snooze_and_event_atomic(){for table in ["sources","states","requests","meta"]{let s=setup();enable(&s);let p=response_plan(&s,"明天下午再看");let until=now()+DAY;s.proactive_finish_response(&p,Ok(json!({"feedback":[{"kind":"snooze","subjectRefs":["s0"],"userEvidenceSpans":[{"messageRef":"current","start":0,"end":6}],"timeText":"明天下午","intervalStart":until,"intervalEnd":until+3_600_000,"timezone":"Asia/Shanghai"}]}).to_string())).unwrap();at(until);let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(s.proactive_reconcile().is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before,"{table}");s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();s.proactive_reconcile().unwrap();let once=write_boundary_snapshot(&s);s.proactive_reconcile().unwrap();assert_eq!(write_boundary_snapshot(&s),once);assert_eq!(control_rows(&s.c,"sources","proactive_event").unwrap().iter().filter(|r|r["type"]=="snooze_due").count(),1);}}
#[test]fn proactive_recovery_write_faults_never_partially_mark_unknown(){for table in ["sources","packets"]{let s=setup();enable(&s);let p=plan(&s);let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(Store::proactive_recover(&s.c).is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before);s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();Store::proactive_recover(&s.c).unwrap();assert_eq!(request(&s.c,p["id"].as_str().unwrap()).unwrap().unwrap()["status"],"outcome_unknown");assert_eq!(budget(&s.c,now()).unwrap().analysis,1);}}
#[test]fn proactive_usage_write_faults_preserve_unknown_and_do_not_resend(){for table in ["sources","packets","requests","meta"]{let s=setup();enable(&s);let p=plan(&s);let before=write_boundary_snapshot(&s);write_fault(&s,table);assert!(s.proactive_usage(p["id"].as_str().unwrap(),None,22,None).is_err(),"{table}");assert_eq!(write_boundary_snapshot(&s),before);s.c.execute_batch("DROP TRIGGER boundary_fault").unwrap();s.proactive_usage(p["id"].as_str().unwrap(),None,22,None).unwrap();let once=write_boundary_snapshot(&s);s.proactive_usage(p["id"].as_str().unwrap(),None,22,None).unwrap();assert_eq!(write_boundary_snapshot(&s),once);assert_eq!(budget(&s.c,now()).unwrap().analysis,1);}}

#[test]fn proactive_post_credential_rechecks_grant_basis_and_profile(){for change in ["grant","basis","profile"]{let s=setup();enable(&s);let p=plan(&s);let mut expected=s.proactive_transport_profile(&p).unwrap();match change{"grant"=>{let mut v=grant(&s);v["enabled"]=json!(false);s.proactive_set_policy(decode(v.clone()).unwrap(),v).unwrap();},"basis"=>{let mut r=get(&s.c,"records","work-report").unwrap().unwrap();r["version"]=json!(2);put(&s.c,"records","work-report",&r).unwrap();},_=>{expected["revision"]=json!(987654);}}assert!(s.proactive_transport(&p,&expected,zeroize::Zeroizing::new(b"fictional-only".to_vec())).is_err(),"{change}");assert!(get(&s.c,"sources","proactive:budget:B").unwrap().is_none());assert_eq!(budget(&s.c,now()).unwrap().analysis,1);}}

#[test]fn proactive_credential_worker_diagnostic_reaches_noncontent_receipt(){
 for (stage,status) in [("single_item_read",Some(-25308)),("single_item_read",Some(-25293)),("default_keychain",Some(-25294)),("concurrent_busy",None)] {
  let s=setup();enable(&s);let p=plan(&s);let rid=p["id"].as_str().unwrap();
  let (r,d)=crate::host_gateway::proactive_credential_wait(move||{crate::secure_credentials::read_stage(stage,status);Err(error("credential_unavailable"))},std::time::Duration::from_secs(1));assert!(r.is_err());
  s.proactive_usage(rid,None,10,Some(d)).unwrap();s.proactive_finish(&p,r.map(|_|String::new())).unwrap();
  let metadata=get(&s.c,"sources",rid).unwrap().unwrap();assert_eq!(metadata["credentialDiagnostic"],json!({"stage":stage,"osStatus":status}));assert!(metadata.get("input").is_none());assert_eq!(budget(&s.c,now()).unwrap().analysis,1);assert!(get(&s.c,"sources","proactive:budget:B").unwrap().is_none());assert_eq!(request(&s.c,rid).unwrap().unwrap()["outcome"]["errorCode"],"credential_unavailable");
 }
}
#[test]fn proactive_speech_requires_current_surface_visibility_and_rechecks_before_sink(){
 use crate::interaction_contract::Ref;use crate::voice::{gateway::{Gateway,Transport},mimo::RequestBody,budget::Ledger};
 struct Fake;impl Transport for Fake{fn start(&mut self,_:&str,_:&str,_:RequestBody)->Result<(),&'static str>{Ok(())}fn cancel(&mut self,_:&str){}}
 let s=setup();enable(&s);let p=plan(&s);let result=s.proactive_finish(&p,Ok(suggestion())).unwrap();let sid=result["suggestionId"].as_str().unwrap();
 put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"tts":true,"revision":1})).unwrap();put(&s.c,"sources","voice:session:surface-test",&json!({"state":"active","generation":1,"policyRevision":1})).unwrap();put(&s.c,"sources","voice:budget",&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();let reference=Ref{id:format!("assistant:{sid}"),revision:1};
 assert!(s.voice_register_speech("surface-test",1,1,&reference,true).is_err());s.proactive_shown("surface-for-speech",sid,1).unwrap();assert!(s.voice_register_speech("surface-test",1,1,&reference,false).is_err());let request=s.voice_register_speech("surface-test",1,1,&reference,true).unwrap();assert!(request.proactive_decision_ref.as_ref().unwrap().id.starts_with("voice-decision:"));let mut g=Gateway::new();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut Fake).unwrap();assert!(s.voice_validate_playback(&request,true).is_ok());assert!(s.voice_validate_playback(&request,false).is_err());let mut policy=grant(&s);policy["enabled"]=json!(false);s.proactive_set_policy(decode(policy.clone()).unwrap(),policy).unwrap();assert!(s.voice_validate_playback(&request,true).is_err());assert!(Store::actions(&s.c).unwrap().is_empty());
}
