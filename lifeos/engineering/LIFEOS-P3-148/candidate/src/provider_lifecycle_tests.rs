//! Test-only independent in-memory OS key store wired through the provider lifecycle.
use super::*;
use crypto::CredentialPort;
use std::cell::RefCell;
#[derive(Default)]
struct State {
    port: crypto::MemoryCredentialPort,
    trace: Vec<(String, String, String)>,
    fault: &'static str,
    delete_fail: bool,
}
thread_local! {static STATE:RefCell<Option<State>>=const{RefCell::new(None)};}
pub(super) fn add(s: &str, r: &str, m: &[u8]) -> Option<Result<(), crypto::CredentialFailure>> {
    STATE.with(|x| {
        x.borrow_mut().as_mut().map(|x| {
            x.trace.push(("add".into(), s.into(), r.into()));
            x.port.add_generic_password(s, r, m)
        })
    })
}
pub(super) fn find(s: &str, r: &str) -> Option<Result<Vec<u8>, crypto::CredentialFailure>> {
    STATE.with(|x| {
        x.borrow_mut().as_mut().map(|x| {
            x.trace.push(("find".into(), s.into(), r.into()));
            x.port.find_generic_password(s, r)
        })
    })
}
pub(super) fn delete(s: &str, r: &str) -> Option<Result<(), crypto::CredentialFailure>> {
    STATE.with(|x| {
        x.borrow_mut().as_mut().map(|x| {
            x.trace.push(("delete".into(), s.into(), r.into()));
            if x.delete_fail {
                Err(crypto::CredentialFailure::KeychainUnavailable)
            } else {
                x.port.delete_generic_password(s, r)
            }
        })
    })
}
pub(super) fn checkpoint(point: &str) -> R<()> {
    STATE.with(|x| {
        if x.borrow().as_ref().is_some_and(|s| s.fault == point) {
            fail("database_unavailable")
        } else {
            Ok(())
        }
    })
}
pub(super) fn models() -> Option<R<Vec<String>>> {
    STATE.with(|x| {
        x.borrow_mut().as_mut().map(|x| {
            x.trace.push((
                "GET".into(),
                "https://api.deepseek.com/models".into(),
                String::new(),
            ));
            Ok(vec!["deepseek-synthetic-v1".into()])
        })
    })
}
fn trace() -> Vec<(String, String, String)> {
    STATE.with(|x| x.borrow().as_ref().unwrap().trace.clone())
}
fn fault(s: &'static str) {
    STATE.with(|x| x.borrow_mut().as_mut().unwrap().fault = s)
}
struct Reset;
impl Drop for Reset {
    fn drop(&mut self) {
        STATE.with(|x| *x.borrow_mut() = None)
    }
}
fn start() -> Reset {
    STATE.with(|x| *x.borrow_mut() = Some(State::default()));
    Reset
}
fn req(op: &str, payload: Value) -> Request {
    Request {
        version: 3,
        operation: op.into(),
        payload,
    }
}
fn replace(f: &str, id: &str, rev: u64, key: &str) -> R<Value> {
    dispatch(
        &req(
            "replace_credential",
            json!({"requestId":id,"profileId":"deepseek-default","expectedCredentialRevision":rev,"apiKey":key}),
        ),
        f,
    )
}
fn recover(f: &str, id: &str, rev: u64) -> R<Value> {
    dispatch(
        &req(
            "recover_credentials",
            json!({"requestId":id,"profileId":"deepseek-default","expectedCredentialRevision":rev,"confirmation":"recover_owned_credential_operations"}),
        ),
        f,
    )
}
fn no_secret(f: &str) {
    let c = open(f, false).unwrap().unwrap();
    let mut q=c.prepare("SELECT config_json || coalesce(envelope_json,'') FROM provider_profile UNION ALL SELECT metadata_json FROM provider_operations").unwrap();
    for row in q.query_map([], |r| r.get::<_, String>(0)).unwrap() {
        let s = row.unwrap();
        assert!(!s.contains("synthetic-first-secret") && !s.contains("synthetic-next-secret"));
    }
    assert!(!serde_json::to_string(&settings(f).unwrap())
        .unwrap()
        .contains("synthetic-first-secret"));
}

#[test]
fn p148_lifecycle_independent_key_persistence_and_replace_windows() {
    for point in [
        "before_prepared",
        "after_prepared",
        "after_key_creation",
        "before_commit",
        "after_commit",
    ] {
        let _reset = start();
        let f = crate::conversation_store::uid("lifecycle").replace(':', "-");
        replace(&f, "initial", 0, "synthetic-first-secret").unwrap();
        let c = open(&f, false).unwrap().unwrap();
        let first = row(&c).unwrap().1.unwrap();
        let first_ref = first["keyReference"].as_str().unwrap();
        drop(c);
        // The same independent OS mock outlives every reopened SQLite connection.
        assert_eq!(
            credential(&f).unwrap().as_slice(),
            b"synthetic-first-secret"
        );
        let actual = find(crypto::KEYCHAIN_SERVICE, first_ref).unwrap().unwrap();
        let derived =
            Sha256::digest(format!("P3-148-INSECURE-SYNTHETIC-ONLY:{first_ref}").as_bytes());
        assert_ne!(actual.as_slice(), derived.as_slice());
        fault(point);
        assert!(replace(&f, "replacement", 1, "synthetic-next-secret").is_err());
        fault("");
        let before = trace();
        let s = settings(&f).unwrap();
        assert_eq!(trace(), before, "passive settings must not query OS");
        // Activate/recover the local conversation against the same pending provider journal.
        let business = crate::repository::open(&f).unwrap();
        crate::source_store::init(&business).unwrap();
        drop(business);
        crate::conversation_store::dispatch(
            "get_context_recovery",
            req(
                "open_conversation",
                json!({"requestId":"passive-open","conversationId":"source-chat"}),
            ),
            &f,
        )
        .unwrap();
        crate::conversation_store::dispatch(
            "get_context_recovery",
            req("read_conversation", json!({"conversationId":"source-chat"})),
            &f,
        )
        .unwrap();
        crate::conversation_store::dispatch(
            "get_ai_provider_settings",
            req("read_settings", json!({})),
            &f,
        )
        .unwrap();
        assert_eq!(
            trace(),
            before,
            "activation and reads must not touch OS/models"
        );
        let committed = point == "after_commit";
        let rev = if committed { 2 } else { 1 };
        assert_eq!(s["credentialRevision"], rev);
        let recovered = recover(&f, "explicit-recover", rev).unwrap();
        assert_eq!(recovered["state"], "stored");
        let before = trace();
        assert_eq!(recover(&f, "explicit-recover", rev).unwrap(), recovered);
        assert_eq!(trace(), before);
        assert_eq!(
            credential(&f).unwrap().as_slice(),
            if committed {
                b"synthetic-next-secret".as_slice()
            } else {
                b"synthetic-first-secret".as_slice()
            }
        );
        no_secret(&f);
        for (_, service, reference) in trace() {
            assert_eq!(service, crypto::KEYCHAIN_SERVICE);
            assert!(reference.starts_with("p3-148-key-"));
        }
    }
}

#[test]
fn p148_lifecycle_delete_windows_passive_and_explicit_recovery() {
    for point in ["before_commit", "after_commit", "os_delete_failure"] {
        let _reset = start();
        let f = crate::conversation_store::uid("delete").replace(':', "-");
        replace(&f, "initial", 0, "synthetic-first-secret").unwrap();
        if point == "os_delete_failure" {
            STATE.with(|x| x.borrow_mut().as_mut().unwrap().delete_fail = true);
        } else {
            fault(point);
        }
        let p = json!({"requestId":"delete","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"delete_this_credential"});
        let result = dispatch(&req("delete_credential", p), &f);
        if point == "os_delete_failure" {
            assert_eq!(result.unwrap()["state"], "cleanup_pending");
        } else {
            assert!(result.is_err());
        }
        fault("");
        STATE.with(|x| x.borrow_mut().as_mut().unwrap().delete_fail = false);
        let before = trace();
        let s = settings(&f).unwrap();
        assert_eq!(trace(), before);
        let rev = if point == "before_commit" { 1 } else { 2 };
        assert_eq!(s["credentialRevision"], rev);
        assert_eq!(s["enabled"], false);
        if rev == 2 {
            assert!(credential(&f).is_err());
        }
        let r = recover(&f, "recover", rev).unwrap();
        assert_eq!(r["state"], if rev == 1 { "stored" } else { "deleted" });
        let before = trace();
        recover(&f, "recover", rev).unwrap();
        assert_eq!(trace(), before);
        no_secret(&f);
    }
}

#[test]
fn p148_lifecycle_models_only_on_explicit_test_and_no_creation_on_reads() {
    let _reset = start();
    let f = crate::conversation_store::uid("trace").replace(':', "-");
    assert_eq!(settings(&f).unwrap()["credentialState"], "absent");
    assert!(trace().is_empty());
    assert!(!path(&f).unwrap().exists());
    for (op, p) in [
        (
            "test_connection",
            json!({"requestId":"no-test","expectedCredentialRevision":0}),
        ),
        ("select_model", json!({"requestId":"no-select"})),
        ("set_enabled", json!({"requestId":"no-enable"})),
        ("delete_credential", json!({"requestId":"no-delete"})),
        ("recover_credentials", json!({"requestId":"no-recover"})),
    ] {
        assert!(dispatch(&req(op, p), &f).is_err());
        assert!(!path(&f).unwrap().exists());
        assert!(trace().is_empty());
    }
    replace(&f, "initial", 0, "synthetic-first-secret").unwrap();
    assert!(!trace().iter().any(|t| t.0 == "GET"));
    let p = json!({"requestId":"test","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"test_deepseek_models_once"});
    dispatch(&req("test_connection", p.clone()), &f).unwrap();
    dispatch(&req("test_connection", p), &f).unwrap();
    assert_eq!(trace().iter().filter(|t| t.0 == "GET").count(), 1);
    let s = settings(&f).unwrap();
    dispatch(&req("select_model",json!({"requestId":"select","profileId":"deepseek-default","expectedProfileRevision":s["profileRevision"],"testReceiptId":"test","modelId":"deepseek-synthetic-v1"})),&f).unwrap();
    let s = settings(&f).unwrap();
    dispatch(&req("set_enabled",json!({"requestId":"enable","profileId":"deepseek-default","expectedProfileRevision":s["profileRevision"],"enabled":true})),&f).unwrap();
    assert_eq!(trace().iter().filter(|t| t.0 == "GET").count(), 1);
    no_secret(&f);
}
