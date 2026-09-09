use super::*;
use std::fs;
fn db() -> Connection {
    let c = Connection::open_in_memory().unwrap();
    c.execute_batch("CREATE TABLE records(id TEXT PRIMARY KEY,body TEXT NOT NULL); CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT NOT NULL);CREATE TABLE states(id TEXT PRIMARY KEY,body TEXT NOT NULL);CREATE TABLE meta(id INTEGER,revision INTEGER);INSERT INTO meta VALUES(1,0);").unwrap();
    c
}
fn call(c: &mut Connection, n: &str) -> R<Value> {
    import(c, n, 1788912000000, &json!({}), |_| {}, None)
}
fn dump(c: &Connection) -> String {
    let mut all = vec![];
    for t in ["records", "sources", "states"] {
        let mut q = c
            .prepare(&format!("SELECT body FROM {t} ORDER BY id"))
            .unwrap();
        all.extend(
            q.query_map([], |r| r.get::<_, String>(0))
                .unwrap()
                .map(Result::unwrap),
        );
    }
    all.join("\n")
}
fn fixture(name: &str, content: &[u8]) -> String {
    let d = Dir::root().unwrap().child("inputs", false).unwrap();
    let name = format!(
        "test-{}-{}-{}.xml",
        name,
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    );
    let mut f = d.create(&name).unwrap();
    f.write_all(content).unwrap();
    f.sync().unwrap();
    name
}
#[test]
fn xml_zip_and_byte_replay() {
    let mut c = db();
    let a = call(&mut c, "01-synthetic-export.xml").unwrap();
    assert_eq!(a["inserted"], 3);
    assert_eq!(a["unsupported"], 1);
    let before = dump(&c);
    let r = call(&mut c, "01-synthetic-export.xml").unwrap();
    assert_eq!(r["status"], "duplicate");
    assert_eq!(dump(&c), before);
    let z = call(&mut c, "02-synthetic-export.zip").unwrap();
    assert_eq!(z["inserted"], 0);
    assert_eq!(z["duplicates"], 3);
    assert_eq!(z["attachments"], 1);
}
#[test]
fn overlapping_export_no_double_count() {
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let r = call(&mut c, "03-overlap.xml").unwrap();
    assert_eq!(r["inserted"], 1);
    assert_eq!(r["duplicates"], 1);
    let count:i64=c.query_row("SELECT count(*) FROM records WHERE json_extract(body,'$.kind')='health_apple_observation'",[],|r|r.get(0)).unwrap();
    assert_eq!(count, 4);
}
#[test]
fn conflict_not_revision() {
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    call(&mut c, "05-conflict.xml").unwrap();
    let mut q = c
        .prepare("SELECT body FROM states WHERE json_extract(body,'$.metric')='steps'")
        .unwrap();
    for raw in q.query_map([], |r| r.get::<_, String>(0)).unwrap() {
        let s: Value = serde_json::from_str(&raw.unwrap()).unwrap();
        assert!(s["value"].is_null());
    }
    let n:i64=c.query_row("SELECT count(*) FROM records WHERE json_extract(body,'$.kind')='health_apple_observation'",[],|r|r.get(0)).unwrap();
    assert_eq!(n, 4);
}
#[test]
fn malformed_tail_rolls_back_and_retry() {
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let before = dump(&c);
    assert!(call(&mut c, "04-broken.xml").is_err());
    assert_eq!(dump(&c), before);
    assert!(call(&mut c, "03-overlap.xml").is_ok());
}
#[test]
fn interrupted_then_retry() {
    let mut c = db();
    let before = dump(&c);
    assert_eq!(
        import(
            &mut c,
            "01-synthetic-export.xml",
            1,
            &json!({}),
            |_| {},
            Some(2)
        )
        .unwrap_err()
        .code,
        "health_test_interrupted"
    );
    assert_eq!(dump(&c), before);
    assert_eq!(
        call(&mut c, "01-synthetic-export.xml").unwrap()["inserted"],
        3
    );
}
#[test]
fn resource_limit_rollback() {
    for limits in [
        json!({"fileBytes":10}),
        json!({"records":1}),
        json!({"xmlBytes":50}),
        json!({"fileBytes":999999999999u64}),
    ] {
        let mut c = db();
        assert!(import(&mut c, "01-synthetic-export.xml", 1, &limits, |_| {}, None).is_err());
        assert!(dump(&c).is_empty());
    }
}
#[test]
fn cross_day_units_and_observation_time() {
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let mut q = c.prepare("SELECT body FROM states").unwrap();
    let rows = q
        .query_map([], |r| r.get::<_, String>(0))
        .unwrap()
        .map(|r| serde_json::from_str::<Value>(&r.unwrap()).unwrap())
        .collect::<Vec<_>>();
    let sleep: Vec<_> = rows.iter().filter(|s| s["metric"] == "sleep").collect();
    assert_eq!(sleep.len(), 2);
    assert_eq!(
        sleep
            .iter()
            .map(|s| s["value"].as_f64().unwrap())
            .sum::<f64>(),
        480.0
    );
    assert_eq!(
        rows.iter().find(|s| s["metric"] == "exercise").unwrap()["value"],
        10.0
    );
    for s in rows {
        assert!(s["observedAt"].as_i64().unwrap() < s["receivedAt"].as_i64().unwrap());
        assert_eq!(s["modelEligible"], false);
    }
}
#[test]
fn empty_does_not_delete() {
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let n: i64 = c
        .query_row("SELECT count(*) FROM states", [], |r| r.get(0))
        .unwrap();
    call(&mut c, "06-empty.xml").unwrap();
    assert_eq!(
        n,
        c.query_row::<i64, _, _>("SELECT count(*) FROM states", [], |r| r.get(0))
            .unwrap()
    );
}
#[test]
fn large_stream_progress() {
    let mut c = db();
    let mut progress_count = 0;
    let v = import(
        &mut c,
        "07-large.xml",
        1788912000000,
        &json!({}),
        |_| progress_count += 1,
        None,
    )
    .unwrap();
    assert_eq!(v["inserted"], 1000);
    assert!(progress_count >= 10);
}
#[test]
fn duplicated_content_ambiguous() {
    let row=b"<Record type=\"HKQuantityTypeIdentifierStepCount\" sourceName=\"Synth\" unit=\"count\" value=\"10\" startDate=\"2026-09-08 01:00:00 +0800\" endDate=\"2026-09-08 01:01:00 +0800\"/>";
    let data = [b"<HealthData>".as_slice(), row, row, b"</HealthData>"].concat();
    let n = fixture("duplicate", &data);
    let mut c = db();
    let v = call(&mut c, &n).unwrap();
    assert_eq!(v["inserted"], 1);
    assert_eq!(v["duplicates"], 1);
    let s: String = c
        .query_row("SELECT body FROM states", [], |r| r.get(0))
        .unwrap();
    assert!(serde_json::from_str::<Value>(&s).unwrap()["value"].is_null());
}
#[test]
fn file_paths_and_symlinks_denied() {
    for n in ["../no.xml", "/no.xml", "a/b.xml", "a\\b.xml", "missing.txt"] {
        assert!(selected(n).is_err());
    }
    let dir = std::path::Path::new(crate::runtime_root::ROOT).join("inputs");
    let link = dir.join(format!("test-link-{}.xml", std::process::id()));
    std::os::unix::fs::symlink(dir.join("not-opened.xml"), &link).unwrap();
    assert!(selected(link.file_name().unwrap().to_str().unwrap()).is_err());
}
#[test]
fn hardlink_denied() {
    let dir = std::path::Path::new(crate::runtime_root::ROOT).join("inputs");
    let name = fixture("hardlink", b"<HealthData/>");
    let link = dir.join(format!("test-hard-{}.xml", std::process::id()));
    fs::hard_link(dir.join(name), &link).unwrap();
    assert!(selected(link.file_name().unwrap().to_str().unwrap()).is_err());
}
#[test]
fn restart_retains_all() {
    let name = format!("apple-restart-{}-{}", std::process::id(), now());
    let mut c = repository::open(&name).unwrap();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let before = dump(&c);
    drop(c);
    let mut c = repository::open(&name).unwrap();
    assert_eq!(dump(&c), before);
    assert_eq!(
        call(&mut c, "01-synthetic-export.xml").unwrap()["status"],
        "duplicate"
    );
    assert_eq!(dump(&c), before);
}
#[test]
fn non_sleep_and_unsupported_not_zero() {
    let n=fixture("unknown",b"<HealthData><Record type=\"HKCategoryTypeIdentifierSleepAnalysis\" value=\"unknown\"/><Workout/><Record type=\"Other\"/></HealthData>");
    let mut c = db();
    let v = call(&mut c, &n).unwrap();
    assert_eq!(v["unsupported"], 3);
    assert_eq!(
        c.query_row::<i64, _, _>("SELECT count(*) FROM states", [], |r| r.get(0))
            .unwrap(),
        0
    );
}

#[test]
fn file_replacement_during_parse_has_no_commit() {
    let bytes =
        fs::read(std::path::Path::new(crate::runtime_root::ROOT).join("inputs/07-large.xml"))
            .unwrap();
    let name = fixture("race", &bytes);
    let root = std::path::Path::new(crate::runtime_root::ROOT).join("inputs");
    let mut changed = false;
    let mut c = db();
    let result = import(
        &mut c,
        &name,
        1788912000000,
        &json!({}),
        |_| {
            if !changed {
                fs::rename(root.join(&name), root.join(format!("{name}.retained"))).unwrap();
                std::os::unix::fs::symlink(root.join("not-opened.xml"), root.join(&name)).unwrap();
                changed = true;
            }
        },
        None,
    );
    assert!(changed);
    assert!(result.is_err());
    assert!(dump(&c).is_empty());
}
#[test]
fn old_export_does_not_refresh_later_observation() {
    let mut c = db();
    call(&mut c, "03-overlap.xml").unwrap();
    let mut q = c.prepare("SELECT id,body FROM states").unwrap();
    let previous = q
        .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
        .unwrap()
        .map(Result::unwrap)
        .collect::<Vec<_>>();
    drop(q);
    call(&mut c, "01-synthetic-export.xml").unwrap();
    for (id, old) in previous {
        let old: Value = serde_json::from_str(&old).unwrap();
        let now = get(&c, "states", &id).unwrap().unwrap();
        assert_eq!(now["observedAt"], old["observedAt"]);
        assert_eq!(now["value"], old["value"]);
    }
}
#[test]
fn same_name_group_different_offsets_are_separate() {
    let d=b"<HealthData><Record type=\"HKQuantityTypeIdentifierStepCount\" sourceName=\"Synth\" unit=\"count\" value=\"10\" startDate=\"2026-09-08 01:00:00 +0800\" endDate=\"2026-09-08 01:01:00 +0800\"/><Record type=\"HKQuantityTypeIdentifierStepCount\" sourceName=\"Synth\" unit=\"count\" value=\"10\" startDate=\"2026-09-08 01:00:00 -0500\" endDate=\"2026-09-08 01:01:00 -0500\"/></HealthData>";
    let n = fixture("offsets", d);
    let mut c = db();
    call(&mut c, &n).unwrap();
    assert_eq!(
        c.query_row::<i64, _, _>("SELECT count(*) FROM states", [], |r| r.get(0))
            .unwrap(),
        2
    );
}
#[test]
fn default_snapshot_omits_raw_apple_records() {
    let name = format!("apple-snapshot-{}-{}", std::process::id(), now());
    let mut c = repository::open(&name).unwrap();
    crate::source_store::init(&c).unwrap();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    drop(c);
    crate::conversation_store::dispatch(
        "get_context_recovery",
        repository::Request {
            version: 3,
            operation: "open_conversation".into(),
            payload: json!({"requestId":"apple-open","conversationId":"source-chat"}),
        },
        &name,
    )
    .unwrap();
    let v = repository::dispatch(
        "get_today",
        repository::Request {
            version: 2,
            operation: "snapshot".into(),
            payload: json!({}),
        },
        &name,
    )
    .unwrap();
    assert!(
        !v["records"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["kind"] == "health_apple_observation"
                || r["kind"] == "health_apple_membership")
    );
    assert!(v["states"]
        .as_array()
        .unwrap()
        .iter()
        .any(|r| r["protocol"] == "apple-file-v1"));
}

#[test]
fn legacy_protocols_cannot_mix_in_either_direction() {
    let mut c = db();
    put(
        &c,
        "states",
        &json!({"id":"synthetic-legacy","kind":"health_current_state","metric":"steps"}),
    )
    .unwrap();
    let before = dump(&c);
    assert_eq!(
        call(&mut c, "01-synthetic-export.xml").unwrap_err().code,
        "health_protocol_overlap"
    );
    assert_eq!(dump(&c), before);
    let mut c = db();
    call(&mut c, "01-synthetic-export.xml").unwrap();
    let before = dump(&c);
    assert_eq!(
        crate::health_snapshot::receive(
            &mut c,
            include_bytes!("../../../fixtures/s1-01-full.json"),
            1788912000000
        )
        .unwrap_err()
        .code,
        "health_protocol_overlap"
    );
    assert_eq!(dump(&c), before);
}

#[test]
fn sqlite_projection_failure_rolls_back_batch_and_sources(){
    let mut c=db();c.execute_batch("CREATE TRIGGER fail_projection BEFORE INSERT ON states BEGIN SELECT RAISE(ABORT,'synthetic failure');END;").unwrap();
    assert!(call(&mut c,"01-synthetic-export.xml").is_err());assert!(dump(&c).is_empty());
    c.execute_batch("DROP TRIGGER fail_projection;").unwrap();assert_eq!(call(&mut c,"01-synthetic-export.xml").unwrap()["inserted"],3);
}
