use super::*;
fn packet() -> Value {
    json!({"schema":"health-window-snapshot-v1","batchId":"b1","capturedAtMs":1788912000000i64,"windowStartMs":1788825600000i64,"windowEndMs":1788912000000i64,"timezoneOffsetMinutes":0,"metric":"steps","source":{"key":"logical-watch-group","name":"Watch","identityStrategy":"configured-name-group"},"query":{"key":"steps-contained","intervalRule":"fully-contained","sleepCategory":"not-applicable"},"completeness":"complete","pagination":"complete","completenessEvidence":"synthetic-fixture","samples":[{"startMs":1788825600000i64,"endMs":1788829200000i64,"value":1000,"unit":"count"}]})
}
fn db() -> Connection {
    let c = Connection::open_in_memory().unwrap();
    c.execute_batch("CREATE TABLE meta(id INTEGER PRIMARY KEY,revision INTEGER);INSERT INTO meta VALUES(1,0);CREATE TABLE records(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE states(id TEXT PRIMARY KEY,body TEXT);").unwrap();
    c
}
fn send(c: &mut Connection, v: &Value) -> R<Value> {
    receive(c, &serde_json::to_vec(v).unwrap(), 1789000000000)
}
fn states(c: &Connection) -> Vec<Value> {
    rows(c, "states", "health_current_state").unwrap()
}
fn next() -> Value {
    let mut v = packet();
    v["batchId"] = json!("b2");
    v["capturedAtMs"] = json!(1788912001000i64);
    v
}
#[test]
fn replay_is_zero_writes() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let original = states(&c);
    assert_eq!(send(&mut c, &packet()).unwrap()["state"], "duplicate");
    assert_eq!(original, states(&c));
    assert_eq!(rows(&c, "records", "health_batch").unwrap().len(), 1);
}
#[test]
fn complete_same_scope_replaces_atomically_with_batch_lineage() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let old = states(&c)[0].clone();
    let mut v = next();
    v["samples"][0]["value"] = json!(1200);
    send(&mut c, &v).unwrap();
    let s = &states(&c)[0];
    assert_eq!(s["value"], 1200.0);
    assert_eq!(s["generation"], 2);
    assert_eq!(s["supersedesBatch"], old["refs"][0]["id"]);
    assert_eq!(s["observedAt"], old["observedAt"]);
    assert_eq!(rows(&c, "records", "health_batch").unwrap().len(), 2);
    assert_eq!(rows(&c, "records", "health_sample").unwrap().len(), 0);
}
#[test]
fn unknown_partial_empty_or_incomplete_pagination_never_replace() {
    for (k, x) in [
        ("completeness", json!("unknown")),
        ("completeness", json!("partial")),
        ("pagination", json!("incomplete")),
        ("pagination", json!("unknown")),
        ("samples", json!([])),
    ] {
        let mut c = db();
        send(&mut c, &packet()).unwrap();
        let before = states(&c);
        let mut v = next();
        v[k] = x;
        assert_eq!(send(&mut c, &v).unwrap()["changed"], 0);
        assert_eq!(before, states(&c));
        assert_eq!(rows(&c, "records", "health_batch").unwrap().len(), 2);
    }
}
#[test]
fn older_and_same_time_conflicts_never_replace() {
    let mut c = db();
    let mut newer = next();
    newer["samples"][0]["value"] = json!(1200);
    send(&mut c, &newer).unwrap();
    let before = states(&c);
    assert_eq!(send(&mut c, &packet()).unwrap()["state"], "ignored_older");
    let mut conflict = newer;
    conflict["batchId"] = json!("conflict");
    conflict["samples"][0]["value"] = json!(1);
    assert_eq!(
        send(&mut c, &conflict).unwrap_err().code,
        "health_snapshot_time_conflict"
    );
    assert_eq!(before, states(&c));
}
#[test]
fn equal_content_new_capture_advances_watermark_not_freshness() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let before = states(&c);
    assert_eq!(send(&mut c, &next()).unwrap()["state"], "unchanged");
    assert_eq!(before, states(&c));
    let mut late = packet();
    late["batchId"] = json!("late");
    late["capturedAtMs"] = json!(1788912000500i64);
    late["samples"][0]["value"] = json!(999);
    assert_eq!(send(&mut c, &late).unwrap()["state"], "ignored_older");
    assert_eq!(before, states(&c));
}
#[test]
fn partial_overlap_query_offset_and_same_named_source_cannot_double_count() {
    for kind in ["window", "query", "offset", "source"] {
        let mut c = db();
        send(&mut c, &packet()).unwrap();
        let mut v = next();
        match kind {
            "window" => v["windowStartMs"] = json!(1788825600000i64 - 3600000),
            "query" => v["query"]["key"] = json!("other-query"),
            "offset" => v["timezoneOffsetMinutes"] = json!(480),
            _ => v["source"]["key"] = json!("other-logical-group"),
        };
        let before = states(&c);
        assert_eq!(
            send(&mut c, &v).unwrap_err().code,
            "health_snapshot_overlap"
        );
        assert_eq!(before, states(&c));
    }
}
#[test]
fn source_name_is_not_unique_identity_and_policy_cannot_silently_change() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let mut v = next();
    v["source"]["name"] = json!("Renamed");
    assert_eq!(
        send(&mut c, &v).unwrap_err().code,
        "health_source_policy_conflict"
    );
    v["source"]["identityStrategy"] = json!("device-uuid");
    assert!(send(&mut c, &v).is_err());
    let s = &states(&c)[0];
    assert_eq!(s["sources"][0]["identityStrategy"], "configured-name-group");
}
#[test]
fn nonoverlap_is_separate_not_added_to_one_total() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let mut v = next();
    for key in ["windowStartMs", "windowEndMs", "capturedAtMs"] {
        v[key] = json!(v[key].as_i64().unwrap() + domain::DAY);
    }
    for key in ["startMs", "endMs"] {
        v["samples"][0][key] = json!(v["samples"][0][key].as_i64().unwrap() + domain::DAY);
    }
    send(&mut c, &v).unwrap();
    assert_eq!(states(&c).len(), 2);
    assert!(states(&c).iter().all(|s| s["value"] == 1000.0));
}
#[test]
fn duplicate_rows_without_ids_are_uncertain_not_deduplicated() {
    let mut c = db();
    let mut v = packet();
    let x = v["samples"][0].clone();
    v["samples"].as_array_mut().unwrap().push(x);
    send(&mut c, &v).unwrap();
    assert!(states(&c)[0]["value"].is_null());
}
#[test]
fn strict_bounds_category_and_fields_reject_without_truncation() {
    let mut c = db();
    for kind in ["limit", "unknown", "unit", "sleep", "permission"] {
        let mut v = packet();
        match kind {
            "limit" => v["samples"] = json!(vec![v["samples"][0].clone(); 257]),
            "unknown" => v["samples"][0]["sampleId"] = json!("fake"),
            "unit" => v["samples"][0]["unit"] = json!("km"),
            "sleep" => v["metric"] = json!("sleep"),
            _ => v["completenessEvidence"] = json!("real-healthkit-verified"),
        };
        assert!(send(&mut c, &v).is_err());
    }
    assert!(receive(&mut c, &vec![b' '; domain::LIMIT + 1], 1).is_err());
    assert!(states(&c).is_empty());
    assert!(rows(&c, "records", "health_batch").unwrap().is_empty());
}
#[test]
fn sleep_requires_explicit_category_and_uses_union() {
    let mut c = db();
    let mut v = packet();
    v["metric"] = json!("sleep");
    v["query"]["sleepCategory"] = json!("explicit-asleep");
    v["samples"][0]["unit"] = json!("milliseconds");
    v["samples"][0]["value"] = json!(3600000);
    let x = v["samples"][0].clone();
    v["samples"].as_array_mut().unwrap().push(x);
    send(&mut c, &v).unwrap();
    assert_eq!(states(&c)[0]["value"], 60.0);
}
fn v1() -> Value {
    let p = packet();
    json!({"schema":"health-envelope-v1","batchId":"old-v1","exportedAtMs":p["capturedAtMs"],"windowStartMs":p["windowStartMs"],"windowEndMs":p["windowEndMs"],"timezoneOffsetMinutes":0,"source":{"id":"v1-source","name":"Legacy synthetic"},"samples":[{"sampleId":"stable-id","revision":1,"metric":"steps","startMs":p["samples"][0]["startMs"],"endMs":p["samples"][0]["endMs"],"value":1000,"unit":"count"}]})
}
#[test]
fn v1_compatibility_and_bidirectional_protocol_fence() {
    for old_first in [true, false] {
        let mut c = db();
        let old = serde_json::to_vec(&v1()).unwrap();
        if old_first {
            crate::health_ingestion::receive_bytes(&mut c, &old, 1).unwrap();
            assert_eq!(
                send(&mut c, &packet()).unwrap_err().code,
                "health_protocol_overlap"
            );
            assert_eq!(
                crate::health_ingestion::receive_bytes(&mut c, &old, 2).unwrap()["state"],
                "duplicate"
            );
        } else {
            send(&mut c, &packet()).unwrap();
            assert_eq!(
                crate::health_ingestion::receive_bytes(&mut c, &old, 2)
                    .unwrap_err()
                    .code,
                "health_protocol_overlap"
            );
            assert!(rows(&c, "records", "health_sample").unwrap().is_empty());
        }
        assert_eq!(states(&c).len(), 1);
    }
}
#[test]
fn transaction_interruption_keeps_prior_and_retry_succeeds() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let before = states(&c);
    c.execute_batch("CREATE TRIGGER interrupted BEFORE UPDATE ON states BEGIN SELECT RAISE(ABORT,'synthetic interruption'); END;").unwrap();
    let mut v = next();
    v["samples"][0]["value"] = json!(1200);
    assert!(send(&mut c, &v).is_err());
    assert_eq!(before, states(&c));
    assert_eq!(rows(&c, "records", "health_batch").unwrap().len(), 1);
    c.execute_batch("DROP TRIGGER interrupted").unwrap();
    send(&mut c, &v).unwrap();
}
#[test]
fn restart_retains_watermark_and_observation() {
    let name = format!(
        "s1-restart-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    );
    let mut c = crate::repository::open(&name).unwrap();
    send(&mut c, &next()).unwrap();
    let before = states(&c);
    drop(c);
    let mut c = crate::repository::open(&name).unwrap();
    assert_eq!(before, states(&c));
    assert_eq!(send(&mut c, &packet()).unwrap()["state"], "ignored_older");
    assert_eq!(before, states(&c));
}
#[test]
fn row_order_is_not_sample_identity() {
    let mut c = db();
    let mut v = packet();
    let mut x = v["samples"][0].clone();
    x["startMs"] = json!(1788829200000i64);
    x["endMs"] = json!(1788832800000i64);
    v["samples"].as_array_mut().unwrap().push(x);
    send(&mut c, &v).unwrap();
    v["samples"].as_array_mut().unwrap().reverse();
    assert_eq!(send(&mut c, &v).unwrap()["state"], "duplicate");
}
#[test]
fn historical_accepted_same_timestamp_conflict_rejects_even_after_newer() {
    let mut c = db();
    send(&mut c, &packet()).unwrap();
    let mut v = next();
    v["samples"][0]["value"] = json!(2000);
    send(&mut c, &v).unwrap();
    let mut conflict = packet();
    conflict["batchId"] = json!("old-conflict");
    conflict["samples"][0]["value"] = json!(1);
    assert_eq!(
        send(&mut c, &conflict).unwrap_err().code,
        "health_snapshot_time_conflict"
    );
}
#[test]
fn public_prepare_rejects_snapshot_refs() {
    let name = format!(
        "s1-deny-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    );
    let mut c = crate::repository::open(&name).unwrap();
    crate::source_store::init(&c).unwrap();
    send(&mut c, &packet()).unwrap();
    drop(c);
    crate::conversation_store::dispatch(
        "get_context_recovery",
        crate::repository::Request {
            version: 3,
            operation: "open_conversation".into(),
            payload: json!({"requestId":"s1-open","conversationId":"source-chat"}),
        },
        &name,
    )
    .unwrap();
    let call = |ipc: &str, op: &str, payload: Value| {
        crate::repository::dispatch(
            ipc,
            crate::repository::Request {
                version: 2,
                operation: op.into(),
                payload,
            },
            &name,
        )
    };
    let snap = call("get_today", "snapshot", json!({})).unwrap();
    let raw = snap["records"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["protocol"] == "snapshot-v1")
        .unwrap();
    let packet = json!({"id":"s1-forged-context","purpose":"health","budget":256,"usedBudget":8,"topK":3,"inputRefs":[{"id":raw["id"],"version":1,"authorizationGeneration":1}],"included":[{"id":raw["id"],"text":"snapshot content","layer":"L3","domain":"Health"}],"excluded":[],"states":[],"feedback":[],"createdAt":1788912000000i64});
    assert_eq!(
        call(
            "assemble_global_ai_context",
            "local_prepare",
            json!({"requestId":"s1-forged","expectedGeneration":snap["revision"],"packet":packet})
        )
        .unwrap_err()
        .code,
        "context_stale"
    );
}
