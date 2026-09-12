//! Dedicated encrypted provider store. Synthetic key material is never a production fallback.
use crate::{
    conversation_contract::*,
    repository::{Error, Request},
    secure_credentials as crypto,
};
use rusqlite::{params, Connection, OptionalExtension};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt, PermissionsExt};
use zeroize::Zeroizing;

struct SyntheticKeyPort;
#[cfg(test)]
#[path = "provider_lifecycle_tests.rs"]
mod lifecycle_mock;
#[cfg(test)]
static MOCK_DELETE_FAIL: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
#[cfg(test)]
static MOCK_KEY_CALLS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
impl crypto::CredentialPort for SyntheticKeyPort {
    fn add_generic_password(
        &mut self,
        s: &str,
        r: &str,
        _m: &[u8],
    ) -> Result<(), crypto::CredentialFailure> {
        #[cfg(test)]
        if let Some(result) = lifecycle_mock::add(s, r, _m) {
            return result;
        }
        self.find_generic_password(s, r).map(|_| ())
    }
    fn find_generic_password(
        &mut self,
        s: &str,
        r: &str,
    ) -> Result<Vec<u8>, crypto::CredentialFailure> {
        #[cfg(test)]
        if let Some(result) = lifecycle_mock::find(s, r) {
            return result;
        }
        #[cfg(test)]
        MOCK_KEY_CALLS.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        if crate::runtime_root::is_real()
            || s != crypto::KEYCHAIN_SERVICE
            || crypto::reference_lineage(r).is_err()
        {
            return Err(crypto::CredentialFailure::KeyReferenceRejected);
        }
        // Deterministic synthetic material permits restart fixtures without any OS call.
        Ok(Sha256::digest(format!("P3-148-INSECURE-SYNTHETIC-ONLY:{r}").as_bytes()).to_vec())
    }
    fn delete_generic_password(
        &mut self,
        s: &str,
        r: &str,
    ) -> Result<(), crypto::CredentialFailure> {
        #[cfg(test)]
        if let Some(result) = lifecycle_mock::delete(s, r) {
            return result;
        }
        #[cfg(test)]
        if MOCK_DELETE_FAIL.load(std::sync::atomic::Ordering::SeqCst) {
            return Err(crypto::CredentialFailure::KeychainUnavailable);
        }
        self.find_generic_password(s, r).map(|_| ())
    }
}
fn ce(e: crypto::CredentialFailure) -> Error {
    Error::new(match e {
        crypto::CredentialFailure::InvalidInput => "credential_invalid",
        crypto::CredentialFailure::KeyReferenceRejected => "credential_reference_rejected",
        crypto::CredentialFailure::KeychainMissing => "credential_missing",
        crypto::CredentialFailure::AuthenticationFailed => "credential_authentication_failed",
        _ => "credential_unavailable",
    })
}
fn path(fixture: &str) -> R<std::path::PathBuf> {
    if fixture.is_empty()
        || !fixture
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || c == b'-')
    {
        return fail("identity_rejected");
    }
    Ok(crate::runtime_root::verify()?.join(if fixture == "app" {
        "p3-148-provider.sqlite".into()
    } else {
        format!("{fixture}-provider.sqlite")
    }))
}
fn open(fixture: &str, create: bool) -> R<Option<Connection>> {
    let p = path(fixture)?;
    let mut newly_created = false;
    match std::fs::symlink_metadata(&p) {
        Ok(m)
            if !m.is_file()
                || m.file_type().is_symlink()
                || m.uid() != unsafe { libc::getuid() }
                || m.permissions().mode() & 0o777 != 0o600 =>
        {
            return fail("database_path_rejected")
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            if !create {
                return Ok(None);
            }
            let file = std::fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .mode(0o600)
                .custom_flags(libc::O_NOFOLLOW)
                .open(&p)
                .map_err(|_| Error::new("database_path_rejected"))?;
            file.sync_all()
                .map_err(|_| Error::new("database_unavailable"))?;
            newly_created = true;
        }
        Err(e) if e.kind() != std::io::ErrorKind::NotFound => return fail("database_unavailable"),
        _ => (),
    }
    for suffix in ["-wal", "-shm", "-journal"] {
        match std::fs::symlink_metadata(format!("{}{suffix}", p.display())) {
            Ok(m) if !m.is_file() || m.file_type().is_symlink() => {
                return fail("database_path_rejected")
            }
            Err(e) if e.kind() != std::io::ErrorKind::NotFound => {
                return fail("database_path_rejected")
            }
            _ => (),
        }
    }
    let flags =
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE | rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW;
    let c = Connection::open_with_flags(&p, flags)?;
    if newly_created {
        c.execute_batch("CREATE TABLE IF NOT EXISTS provider_profile(id TEXT PRIMARY KEY CHECK(id='deepseek-default'),revision INTEGER NOT NULL CHECK(revision>=1),credential_revision INTEGER NOT NULL CHECK(credential_revision>=0),config_json TEXT NOT NULL CHECK(json_valid(config_json)),envelope_json TEXT CHECK(envelope_json IS NULL OR json_valid(envelope_json))); CREATE TABLE IF NOT EXISTS provider_operations(id TEXT PRIMARY KEY,operation TEXT NOT NULL,state TEXT NOT NULL,metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)));")?;
    }
    let count:i64=c.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('provider_profile','provider_operations')",[],|r|r.get(0))?;
    if count != 2 {
        return fail("store_contract_mismatch");
    }
    Ok(Some(c))
}
fn default_profile() -> Value {
    json!({"profileId":"deepseek-default","profileRevision":1,"credentialRevision":0,"credentialState":"absent","enabled":false,"models":[]})
}
fn row(c: &Connection) -> R<(Value, Option<Value>)> {
    let row:Option<(i64,i64,String,Option<String>)>=c.query_row("SELECT revision,credential_revision,config_json,envelope_json FROM provider_profile WHERE id='deepseek-default'",[],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).optional()?;
    if let Some((rev, cr, cfg, env)) = row {
        let cfg: Value =
            serde_json::from_str(&cfg).map_err(|_| Error::new("store_contract_mismatch"))?;
        fields(
            &cfg,
            &["schemaVersion", "enabled", "models", "updatedAt"],
            &["modelId", "testReceiptId", "testedCredentialRevision"],
        )?;
        if cfg["schemaVersion"] != 1 {
            return fail("store_contract_mismatch");
        }
        let mut v = default_profile();
        for k in ["enabled", "models", "modelId", "testReceiptId"] {
            if let Some(value) = cfg.get(k) {
                v[k] = value.clone();
            }
        }
        v["profileId"] = json!("deepseek-default");
        v["profileRevision"] = json!(rev);
        v["credentialRevision"] = json!(cr);
        let e: Option<Value> = env
            .map(|s| serde_json::from_str(&s))
            .transpose()
            .map_err(|_| Error::new("store_contract_mismatch"))?;
        if let Some(e) = &e {
            fields(
                e,
                &[
                    "algorithm",
                    "version",
                    "ciphertext",
                    "nonce",
                    "tag",
                    "keyReference",
                    "maskedTail",
                    "aadVersion",
                ],
                &[],
            )?;
            v["credentialState"] = json!("stored");
            v["maskedTail"] = e["maskedTail"].clone();
        }
        Ok((v, e))
    } else {
        Ok((default_profile(), None))
    }
}
fn save(c: &Connection, s: &Value, e: Option<&Value>) -> R<()> {
    let mut cfg = json!({"schemaVersion":1,"enabled":s["enabled"],"models":s["models"],"updatedAt":crate::conversation_store::now()});
    for k in ["modelId", "testReceiptId"] {
        if let Some(value) = s.get(k) {
            cfg[k] = value.clone();
        }
    }
    if s.get("testReceiptId").is_some() {
        cfg["testedCredentialRevision"] = s["credentialRevision"].clone();
    }
    c.execute("INSERT INTO provider_profile VALUES('deepseek-default',?1,?2,?3,?4) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,credential_revision=excluded.credential_revision,config_json=excluded.config_json,envelope_json=excluded.envelope_json",params![s["profileRevision"].as_i64(),s["credentialRevision"].as_i64(),cfg.to_string(),e.map(Value::to_string)])?;
    Ok(())
}
pub fn settings(fixture: &str) -> R<Value> {
    match open(fixture, false)? {
        Some(c) => {
            let mut s = row(&c)?.0;
            let pending:i64=c.query_row("SELECT count(*) FROM provider_operations WHERE state IN ('prepared','cleanup_pending')",[],|r|r.get(0))?;
            if pending > 0 {
                s["credentialState"] = json!("cleanup_pending");
            }
            Ok(s)
        }
        None => Ok(default_profile()),
    }
}
fn aad(revision: u64, reference: &str) -> Vec<u8> {
    format!("LIFEOS-P3-148|credential|v1|deepseek-default|{revision}|{reference}").into_bytes()
}
fn bytes(v: &Value, k: &str) -> R<Vec<u8>> {
    crate::wire_encoding::decode(
        v[k].as_str()
            .ok_or_else(|| Error::new("credential_authentication_failed"))?,
    )
}
fn decode(e: &Value, revision: u64) -> R<Zeroizing<Vec<u8>>> {
    let r = e["keyReference"]
        .as_str()
        .ok_or_else(|| Error::new("credential_reference_rejected"))?;
    crypto::reference_lineage(r).map_err(ce)?;
    let a = aad(revision, r);
    let c = bytes(e, "ciphertext")?;
    let n = bytes(e, "nonce")?;
    let t = bytes(e, "tag")?;
    let alg = e["algorithm"].as_str().unwrap_or("");
    let ver = e["version"].as_u64().unwrap_or(0) as u8;
    let b = if crate::runtime_root::is_real() {
        crypto::decrypt(&c, &n, &t, r, alg, ver, &a)
    } else {
        crypto::decrypt_with_port(&mut SyntheticKeyPort, &c, &n, &t, r, alg, ver, &a)
    }
    .map_err(ce)?;
    Ok(Zeroizing::new(b))
}
pub fn credential(fixture: &str) -> R<Zeroizing<Vec<u8>>> {
    let c = open(fixture, false)?.ok_or_else(|| Error::new("credential_missing"))?;
    let (s, e) = row(&c)?;
    decode(
        &e.ok_or_else(|| Error::new("credential_missing"))?,
        s["credentialRevision"].as_u64().unwrap(),
    )
}

fn remove_material(reference: &str) -> R<()> {
    crypto::reference_lineage(reference).map_err(ce)?;
    let result = if crate::runtime_root::is_real() {
        crypto::delete_key_material(reference)
    } else {
        crypto::delete_key_material_with_port(&mut SyntheticKeyPort, reference)
    };
    match result {
        Ok(()) | Err(crypto::CredentialFailure::KeychainMissing) => Ok(()),
        Err(e) => Err(ce(e)),
    }
}
// This function is called only by an explicit recover/save/delete action.
fn recover_pending(c: &Connection) -> R<()> {
    let (_, envelope) = row(c)?;
    let current = envelope.as_ref().and_then(|e| e["keyReference"].as_str());
    let mut q=c.prepare("SELECT id,state,metadata_json FROM provider_operations WHERE state IN ('prepared','cleanup_pending') ORDER BY id")?;
    let rows = q
        .query_map([], |r| {
            Ok((
                r.get::<_, String>(0)?,
                r.get::<_, String>(1)?,
                r.get::<_, String>(2)?,
            ))
        })?
        .collect::<Result<Vec<_>, _>>()?;
    for (id, state, raw) in rows {
        let mut m: Value =
            serde_json::from_str(&raw).map_err(|_| Error::new("store_contract_mismatch"))?;
        let reference = if state == "prepared" {
            m["newReference"].as_str()
        } else {
            m["oldReference"].as_str()
        };
        if let Some(reference) = reference {
            if Some(reference) == current {
                return fail("credential_cleanup_pending");
            }
            remove_material(reference).map_err(|_| Error::new("credential_cleanup_pending"))?;
        }
        if state == "prepared" {
            m["result"] = json!({"errorCode":"credential_revision_conflict"});
        } else if m["result"].is_object() {
            m["result"]["state"] = json!(if envelope.is_some() {
                "stored"
            } else {
                "deleted"
            });
        }
        c.execute(
            "UPDATE provider_operations SET state=?2,metadata_json=?3 WHERE id=?1",
            params![
                id,
                if state == "prepared" {
                    "failed"
                } else {
                    "committed"
                },
                m.to_string()
            ],
        )?;
    }
    Ok(())
}
fn credential_result(s: &Value, state: &str) -> Value {
    let mut result = json!({"profileId":"deepseek-default","credentialRevision":s["credentialRevision"],"state":state});
    if s.get("maskedTail").is_some() {
        result["maskedTail"] = s["maskedTail"].clone();
    }
    result
}
pub fn dispatch(r: &Request, fixture: &str) -> R<Value> {
    if r.operation == "read_settings" {
        return settings(fixture);
    }
    let p = &r.payload;
    let op = r.operation.as_str();
    let rid = id(p, "requestId")?;
    let mut c = open(fixture, op == "replace_credential")?
        .ok_or_else(|| Error::new("credential_missing"))?;
    let (mut s, mut envelope) = row(&c)?;
    let old: Option<(String, String, String)> = c
        .query_row(
            "SELECT operation,state,metadata_json FROM provider_operations WHERE id=?",
            [&rid],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()?;
    if let Some((prior_op, state, raw)) = old {
        let m: Value =
            serde_json::from_str(&raw).map_err(|_| Error::new("store_contract_mismatch"))?;
        if prior_op != op {
            return fail("idempotency_conflict");
        }
        if op == "replace_credential" {
            if m["newRevision"] != s["credentialRevision"]
                || m["input"]["expectedCredentialRevision"] != p["expectedCredentialRevision"]
                || state == "prepared"
                || state == "failed"
            {
                return fail("credential_revision_conflict");
            }
            let plain = decode(
                envelope
                    .as_ref()
                    .ok_or_else(|| Error::new("credential_revision_conflict"))?,
                s["credentialRevision"].as_u64().unwrap(),
            )?;
            let submitted = p["apiKey"]
                .as_str()
                .ok_or_else(|| Error::new("credential_invalid"))?
                .as_bytes();
            let mut difference = plain.len() ^ submitted.len();
            for i in 0..plain.len().max(submitted.len()) {
                difference |=
                    (*plain.get(i).unwrap_or(&0) ^ *submitted.get(i).unwrap_or(&0)) as usize;
            }
            if difference != 0 {
                return fail("idempotency_conflict");
            }
        } else if m["input"] != *p {
            return fail("idempotency_conflict");
        }
        if state == "prepared" || state == "failed" {
            return fail("credential_revision_conflict");
        }
        return Ok(m["result"].clone());
    }
    let cr = s["credentialRevision"].as_u64().unwrap();
    let pr = s["profileRevision"].as_u64().unwrap();
    if p.get("expectedCredentialRevision").is_some() && p["expectedCredentialRevision"] != cr {
        return fail("credential_revision_conflict");
    }
    if p.get("expectedProfileRevision").is_some() && p["expectedProfileRevision"] != pr {
        return fail("provider_revision_conflict");
    }
    if matches!(
        op,
        "replace_credential" | "delete_credential" | "recover_credentials"
    ) {
        if let Err(e) = recover_pending(&c) {
            if op != "recover_credentials" {
                return Err(e);
            }
            let result = credential_result(&s, "cleanup_pending");
            c.execute(
                "INSERT INTO provider_operations VALUES(?1,?2,'committed',?3)",
                params![rid, op, json!({"input":p,"result":result}).to_string()],
            )?;
            return Ok(result);
        }
    }
    let old_reference = envelope
        .as_ref()
        .and_then(|e| e["keyReference"].as_str())
        .map(str::to_owned);
    let mut metadata = json!({"input":p,"oldReference":old_reference});
    let mut prepared = false;
    let result = match op {
        "replace_credential" => {
            let secret = Zeroizing::new(
                p["apiKey"]
                    .as_str()
                    .ok_or_else(|| Error::new("credential_invalid"))?
                    .to_owned(),
            );
            if secret.len() < 8
                || secret.len() > 512
                || !secret
                    .bytes()
                    .all(|b| b.is_ascii_graphic() && b != b'"' && b != b'\\')
            {
                return fail("credential_invalid");
            }
            let reference = crypto::new_key_reference();
            #[cfg(test)]
            lifecycle_mock::checkpoint("before_prepared")?;
            metadata = json!({"input":{"profileId":"deepseek-default","expectedCredentialRevision":cr},"newReference":reference,"oldReference":old_reference,"newRevision":cr+1});
            c.execute(
                "INSERT INTO provider_operations VALUES(?1,?2,'prepared',?3)",
                params![rid, op, metadata.to_string()],
            )?;
            prepared = true;
            #[cfg(test)]
            lifecycle_mock::checkpoint("after_prepared")?;
            let enc = if crate::runtime_root::is_real() {
                crypto::encrypt_new_reference_real(&secret, &aad(cr + 1, &reference), reference)
            } else {
                crypto::encrypt_new_reference(
                    &mut SyntheticKeyPort,
                    &secret,
                    &aad(cr + 1, &reference),
                    reference,
                )
            }
            .map_err(ce)?;
            #[cfg(test)]
            lifecycle_mock::checkpoint("after_key_creation")?;
            envelope = Some(
                json!({"ciphertext":crate::wire_encoding::encode(&enc.ciphertext),"nonce":crate::wire_encoding::encode(&enc.nonce),"tag":crate::wire_encoding::encode(&enc.tag),"keyReference":enc.key_reference,"algorithm":enc.algorithm,"version":enc.version,"aadVersion":1}),
            );
            s = default_profile();
            s["credentialRevision"] = json!(cr + 1);
            s["credentialState"] = json!("stored");
            s["maskedTail"] = json!(secret
                .chars()
                .rev()
                .take(4)
                .collect::<String>()
                .chars()
                .rev()
                .collect::<String>());
            envelope.as_mut().unwrap()["maskedTail"] = s["maskedTail"].clone();
            credential_result(&s, "stored")
        }
        "delete_credential" => {
            envelope = None;
            s = default_profile();
            s["credentialRevision"] = json!(cr + 1);
            credential_result(&s, "deleted")
        }
        "recover_credentials" => credential_result(
            &s,
            if envelope.is_some() {
                "stored"
            } else {
                "deleted"
            },
        ),
        "test_connection" => {
            let _secret = decode(
                envelope
                    .as_ref()
                    .ok_or_else(|| Error::new("credential_missing"))?,
                cr,
            )?;
            metadata["result"] = json!({"testReceiptId":rid,"profileId":"deepseek-default","credentialRevision":cr,"state":"outcome_unknown","models":[],"errorCode":"dispatch_outcome_unknown"});
            c.execute(
                "INSERT INTO provider_operations VALUES(?1,?2,'outcome_unknown',?3)",
                params![rid, op, metadata.to_string()],
            )?;
            prepared = true;
            let models = if crate::runtime_root::is_real() {
                crate::provider_transport::models(&_secret)
            } else {
                #[cfg(test)]
                {
                    lifecycle_mock::models()
                        .unwrap_or_else(|| Ok(vec!["deepseek-synthetic-v1".to_owned()]))
                }
                #[cfg(not(test))]
                Ok(vec!["deepseek-synthetic-v1".to_owned()])
            };
            let models = match models {
                Ok(m) => m,
                Err(e) => {
                    metadata["result"]["state"] = json!(if e.code == "dispatch_outcome_unknown" {
                        "outcome_unknown"
                    } else {
                        "failed"
                    });
                    metadata["result"]["errorCode"] = json!(e.code);
                    c.execute(
                        "UPDATE provider_operations SET metadata_json=?2 WHERE id=?1",
                        params![rid, metadata.to_string()],
                    )?;
                    return Ok(metadata["result"].clone());
                }
            };
            s["models"] = json!(models);
            s["testReceiptId"] = json!(rid);
            json!({"testReceiptId":rid,"profileId":"deepseek-default","credentialRevision":cr,"state":"succeeded","models":s["models"]})
        }
        "select_model" => {
            if s["testReceiptId"] != p["testReceiptId"]
                || !s["models"].as_array().unwrap().contains(&p["modelId"])
            {
                return fail("model_not_tested");
            }
            s["modelId"] = p["modelId"].clone();
            s["enabled"] = json!(false);
            s.clone()
        }
        "set_enabled" => {
            if envelope.is_none() || s.get("modelId").is_none() {
                return fail("model_not_tested");
            }
            s["enabled"] = p["enabled"].clone();
            s.clone()
        }
        _ => return fail("operation_rejected"),
    };
    s["profileRevision"] = json!(pr + 1);
    let mut result = if matches!(op, "select_model" | "set_enabled") {
        s.clone()
    } else {
        result
    };
    let cleanup =
        matches!(op, "replace_credential" | "delete_credential") && old_reference.is_some();
    metadata["result"] = result.clone();
    #[cfg(test)]
    lifecycle_mock::checkpoint("before_commit")?;
    let tx = c.transaction()?;
    save(&tx, &s, envelope.as_ref())?;
    if prepared {
        tx.execute(
            "UPDATE provider_operations SET state=?2,metadata_json=?3 WHERE id=?1",
            params![
                rid,
                if cleanup {
                    "cleanup_pending"
                } else {
                    "committed"
                },
                metadata.to_string()
            ],
        )?;
    } else {
        tx.execute(
            "INSERT INTO provider_operations VALUES(?1,?2,?3,?4)",
            params![
                rid,
                op,
                if cleanup {
                    "cleanup_pending"
                } else {
                    "committed"
                },
                metadata.to_string()
            ],
        )?;
    }
    tx.commit()?;
    #[cfg(test)]
    lifecycle_mock::checkpoint("after_commit")?;
    if cleanup && recover_pending(&c).is_err() {
        result["state"] = json!("cleanup_pending");
        metadata["result"] = result.clone();
        c.execute(
            "UPDATE provider_operations SET metadata_json=?2 WHERE id=?1",
            params![rid, metadata.to_string()],
        )?;
    }
    Ok(result)
}

#[cfg(test)]
mod p148_tests {
    use super::*;
    fn req(op: &str, payload: Value) -> Request {
        Request {
            version: 3,
            operation: op.into(),
            payload,
        }
    }
    #[test]
    fn p148_persistent_ciphertext_tamper_and_new_namespace_only() {
        let f = crate::conversation_store::uid("provider").replace(':', "-");
        dispatch(&req("replace_credential",json!({"requestId":"first","profileId":"deepseek-default","expectedCredentialRevision":0,"apiKey":"synthetic-only-secret"})),&f).unwrap();
        assert_eq!(credential(&f).unwrap().as_slice(), b"synthetic-only-secret");
        let c = open(&f, false).unwrap().unwrap();
        let (_, e) = row(&c).unwrap();
        let e = e.unwrap();
        assert!(e["keyReference"]
            .as_str()
            .unwrap()
            .starts_with("p3-148-key-"));
        let mut bad = e.clone();
        bad["tag"] = json!(crate::wire_encoding::encode(&[0; 16]));
        assert_eq!(
            decode(&bad, 1).unwrap_err().code,
            "credential_authentication_failed"
        );
        assert_eq!(
            decode(&e, 2).unwrap_err().code,
            "credential_authentication_failed"
        );
        let calls = MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst);
        bad = e;
        bad["keyReference"] = json!("p3-145-key-0123456789abcdef0123456789abcdef");
        assert_eq!(
            decode(&bad, 1).unwrap_err().code,
            "credential_reference_rejected"
        );
        assert_eq!(
            MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst),
            calls
        );
    }
    #[test]
    fn p148_prepared_failure_passive_read_no_key_recovery_explicit() {
        let f = crate::conversation_store::uid("provider").replace(':', "-");
        dispatch(&req("replace_credential",json!({"requestId":"first","profileId":"deepseek-default","expectedCredentialRevision":0,"apiKey":"synthetic-first-secret"})),&f).unwrap();
        let c = open(&f, false).unwrap().unwrap();
        c.execute_batch("CREATE TRIGGER fail_profile BEFORE UPDATE ON provider_profile BEGIN SELECT RAISE(ABORT,'synthetic database failure'); END;").unwrap();
        assert!(dispatch(&req("replace_credential",json!({"requestId":"replacement","profileId":"deepseek-default","expectedCredentialRevision":1,"apiKey":"synthetic-second-secret"})),&f).is_err());
        assert_eq!(
            credential(&f).unwrap().as_slice(),
            b"synthetic-first-secret"
        );
        let calls = MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst);
        assert_eq!(settings(&f).unwrap()["credentialState"], "cleanup_pending");
        assert_eq!(
            MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst),
            calls
        );
        c.execute_batch("DROP TRIGGER fail_profile").unwrap();
        let p = json!({"requestId":"recover","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"recover_owned_credential_operations"});
        assert_eq!(
            dispatch(&req("recover_credentials", p.clone()), &f).unwrap()["state"],
            "stored"
        );
        let calls = MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst);
        dispatch(&req("recover_credentials", p), &f).unwrap();
        assert_eq!(
            MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst),
            calls
        );
        assert_eq!(
            credential(&f).unwrap().as_slice(),
            b"synthetic-first-secret"
        );
        dispatch(&req("delete_credential",json!({"requestId":"delete","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"delete_this_credential"})),&f).unwrap();
        assert_eq!(settings(&f).unwrap()["credentialState"], "absent");
        assert_eq!(credential(&f).unwrap_err().code, "credential_missing");
    }
    #[test]
    fn p148_delete_cleanup_pending_is_explicit_and_replay_safe() {
        let f = crate::conversation_store::uid("provider").replace(':', "-");
        dispatch(&req("replace_credential",json!({"requestId":"first","profileId":"deepseek-default","expectedCredentialRevision":0,"apiKey":"synthetic-only-secret"})),&f).unwrap();
        MOCK_DELETE_FAIL.store(true, std::sync::atomic::Ordering::SeqCst);
        let deleted=dispatch(&req("delete_credential",json!({"requestId":"delete","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"delete_this_credential"})),&f).unwrap();
        assert_eq!(deleted["state"], "cleanup_pending");
        assert!(credential(&f).is_err());
        assert_eq!(settings(&f).unwrap()["enabled"], false);
        let p = json!({"requestId":"recover-failed","profileId":"deepseek-default","expectedCredentialRevision":2,"confirmation":"recover_owned_credential_operations"});
        assert_eq!(
            dispatch(&req("recover_credentials", p.clone()), &f).unwrap()["state"],
            "cleanup_pending"
        );
        MOCK_DELETE_FAIL.store(false, std::sync::atomic::Ordering::SeqCst);
        let calls = MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst);
        assert_eq!(
            dispatch(&req("recover_credentials", p), &f).unwrap()["state"],
            "cleanup_pending"
        );
        assert_eq!(
            MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst),
            calls
        );
        assert_eq!(dispatch(&req("recover_credentials",json!({"requestId":"recover-again","profileId":"deepseek-default","expectedCredentialRevision":2,"confirmation":"recover_owned_credential_operations"})),&f).unwrap()["state"],"deleted");
    }
    #[test]
    fn p148_model_selection_and_no_network_build() {
        let f = crate::conversation_store::uid("provider").replace(':', "-");
        dispatch(&req("replace_credential",json!({"requestId":"first","profileId":"deepseek-default","expectedCredentialRevision":0,"apiKey":"synthetic-only-secret"})),&f).unwrap();
        let st = settings(&f).unwrap();
        assert!(dispatch(&req("set_enabled",json!({"requestId":"early-enable","profileId":"deepseek-default","expectedProfileRevision":st["profileRevision"],"enabled":true})),&f).is_err());
        assert!(dispatch(&req("select_model",json!({"requestId":"untested","profileId":"deepseek-default","expectedProfileRevision":st["profileRevision"],"testReceiptId":"missing","modelId":"other-model"})),&f).is_err());
        let p = json!({"requestId":"test","profileId":"deepseek-default","expectedCredentialRevision":1,"confirmation":"test_deepseek_models_once"});
        let result = dispatch(&req("test_connection", p.clone()), &f).unwrap();
        let calls = MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst);
        assert_eq!(dispatch(&req("test_connection", p), &f).unwrap(), result);
        assert_eq!(
            MOCK_KEY_CALLS.load(std::sync::atomic::Ordering::SeqCst),
            calls
        );
        let st = settings(&f).unwrap();
        assert!(dispatch(&req("select_model",json!({"requestId":"wrong-model","profileId":"deepseek-default","expectedProfileRevision":st["profileRevision"],"testReceiptId":"test","modelId":"other-model"})),&f).is_err());
        assert!(dispatch(&req("test_connection",json!({"requestId":"old-version","profileId":"deepseek-default","expectedCredentialRevision":0,"confirmation":"test_deepseek_models_once"})),&f).is_err());
        assert_eq!(
            crate::provider_transport::models(b"synthetic-only-secret")
                .unwrap_err()
                .code,
            "real_capability_denied"
        );
    }
}

#[cfg(test)]
mod p148_e03_checks {
    use super::*;
    use crate::model_port::ModelPort;
    use crypto::CredentialPort;
    #[test]
    fn p148_e03_synthetic_ports_without_root_or_os() {
        assert!(!crate::runtime_root::is_real());
        let reference = crypto::new_key_reference();
        let mut port = SyntheticKeyPort;
        let key = port
            .find_generic_password(crypto::KEYCHAIN_SERVICE, &reference)
            .unwrap();
        assert_eq!(key.len(), 32);
        assert_eq!(
            key,
            port.find_generic_password(crypto::KEYCHAIN_SERVICE, &reference)
                .unwrap()
        );
        let body =
            json!({"messages":[{}, {"content":"[C1] source\nfictional-E03\n\n"}]}).to_string();
        let reply = crate::model_port::SyntheticModel
            .generate(&body, b"synthetic-only")
            .unwrap();
        assert!(reply.text.contains("fictional-E03"));
        assert!(crate::provider_transport::models(b"synthetic-only").is_err());
    }
}
