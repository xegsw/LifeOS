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
#[cfg(test)]thread_local!{static LOOKUP_FAILURE:std::cell::Cell<Option<crypto::CredentialFailure>>=const{std::cell::Cell::new(None)};}
#[cfg(test)]pub(crate) fn fail_next_synthetic_lookup(e:crypto::CredentialFailure){LOOKUP_FAILURE.with(|c|c.set(Some(e)));}

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
        self.find_generic_password(s, r).map(|_| ())
    }
    fn find_generic_password(
        &mut self,
        s: &str,
        r: &str,
    ) -> Result<Vec<u8>, crypto::CredentialFailure> {
        #[cfg(test)]
        MOCK_KEY_CALLS.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        if crate::runtime_root::network_enabled()
            || s != crypto::KEYCHAIN_SERVICE
            || crypto::reference_lineage(r).is_err()
        {
            return Err(crypto::CredentialFailure::KeyReferenceRejected);
        }
        #[cfg(test)]if let Some(e)=LOOKUP_FAILURE.with(|c|c.take()){return Err(e);}
        // Deterministic synthetic material permits restart fixtures without any OS call.
        Ok(Sha256::digest(format!("P3-152-INSECURE-SYNTHETIC-ONLY:{r}").as_bytes()).to_vec())
    }
    fn delete_generic_password(
        &mut self,
        s: &str,
        r: &str,
    ) -> Result<(), crypto::CredentialFailure> {
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
    if crate::runtime_root::is_real(){if fixture!="conversation"{return fail("database_path_rejected");}return Ok(crate::runtime_root::verify()?.join("provider.sqlite"));}
    if fixture.is_empty()
        || !fixture
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || c == b'-')
    {
        return fail("identity_rejected");
    }
    Ok(crate::runtime_root::verify()?.join(if fixture == "app" {
        "p3-152-provider.sqlite".into()
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
                || m.nlink()!=1
                || m.uid() != unsafe { libc::getuid() }
                || m.permissions().mode() & 0o777 != 0o600 =>
        {
            return fail("database_path_rejected")
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            if crate::runtime_root::is_real(){return fail("store_contract_mismatch");}
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
            Ok(m) if !m.is_file() || m.file_type().is_symlink() || m.nlink()!=1 || m.uid()!=unsafe{libc::getuid()} || m.mode()&0o777!=0o600 => {
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
    if crate::runtime_root::is_online(){return online_settings();}
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
    format!("LIFEOS-P3-152|credential|v1|deepseek-default|{revision}|{reference}").into_bytes()
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
    let b = if crate::runtime_root::network_enabled() {
        crypto::decrypt(&c, &n, &t, r, alg, ver, &a)
    } else {
        crypto::decrypt_with_port(&mut SyntheticKeyPort, &c, &n, &t, r, alg, ver, &a)
    }
    .map_err(ce)?;
    Ok(Zeroizing::new(b))
}
pub fn credential(fixture: &str) -> R<Zeroizing<Vec<u8>>> {
    if crate::runtime_root::is_online(){let c=online_provider()?;let (s,e)=row(&c)?;return decode(&e.ok_or_else(||Error::new("credential_missing"))?,s["credentialRevision"].as_u64().ok_or_else(||Error::new("store_contract_mismatch"))?);}
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
    if crate::runtime_root::is_online(){return fail("online_configuration_not_authorized");}
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
            metadata = json!({"input":{"profileId":"deepseek-default","expectedCredentialRevision":cr},"newReference":reference,"oldReference":old_reference,"newRevision":cr+1});
            c.execute(
                "INSERT INTO provider_operations VALUES(?1,?2,'prepared',?3)",
                params![rid, op, metadata.to_string()],
            )?;
            prepared = true;
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
            envelope = Some(
                json!({"ciphertext":crate::wire_encoding::encode(&enc.ciphertext),"nonce":crate::wire_encoding::encode(&enc.nonce),"tag":crate::wire_encoding::encode(&enc.tag),"keyReference":enc.key_reference,"algorithm":enc.algorithm,"version":enc.version,"aadVersion":1}),
            );
            s["enabled"] = json!(false);
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
        "test_connection" => return fail("real_capability_denied"),
        "select_model" => {
            let model=p["modelId"].as_str().ok_or_else(|| Error::new("model_rejected"))?;
            if model.is_empty()||model.len()>128||!model.bytes().all(|b|b.is_ascii_alphanumeric()||b"_.:-".contains(&b)){return fail("model_rejected");}
            if !s["models"].as_array().unwrap().contains(&p["modelId"]){if s["models"].as_array().unwrap().len()>=256{return fail("model_limit_reached");}s["models"].as_array_mut().unwrap().push(p["modelId"].clone());}
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

#[cfg(test)]mod p152_tests {
 use super::*;
 fn req(op:&str,payload:Value)->Request{Request{version:5,operation:op.into(),payload}}
 #[test]fn persistent_encrypted_key_and_local_model_without_network(){let f=crate::conversation_store::uid("credential");let key="p152-fictional-secret-canary";dispatch(&req("replace_credential",json!({"requestId":"save","expectedCredentialRevision":0,"apiKey":key})),&f).unwrap();dispatch(&req("select_model",json!({"requestId":"model","modelId":"user-selected-model"})),&f).unwrap();let p=path(&f).unwrap();let bytes=std::fs::read(p).unwrap();assert!(!bytes.windows(key.len()).any(|w|w==key.as_bytes()));let s=settings(&f).unwrap();assert_eq!(s["modelId"],"user-selected-model");assert_eq!(s["enabled"],false);assert!(!s.to_string().contains(key));assert_eq!(credential(&f).unwrap().as_slice(),key.as_bytes());assert_eq!(dispatch(&req("test_connection",json!({"requestId":"test"})),&f).unwrap_err().code,"real_capability_denied");dispatch(&req("delete_credential",json!({"requestId":"delete","expectedCredentialRevision":1})),&f).unwrap();assert_eq!(credential(&f).unwrap_err().code,"credential_missing");}
 #[test]fn tampered_cipher_revision_and_foreign_key_reference_fail_closed(){let f=crate::conversation_store::uid("tamper");dispatch(&req("replace_credential",json!({"requestId":"save","expectedCredentialRevision":0,"apiKey":"p152-fictional-key"})),&f).unwrap();let c=open(&f,false).unwrap().unwrap();let(_,env)=row(&c).unwrap();let mut e=env.unwrap();assert_eq!(decode(&e,2).unwrap_err().code,"credential_authentication_failed");e["tag"]=json!(crate::wire_encoding::encode(&[0u8;16]));assert_eq!(decode(&e,1).unwrap_err().code,"credential_authentication_failed");e["keyReference"]=json!("p3-148-key-0123456789abcdef0123456789abcdef");assert_eq!(decode(&e,1).unwrap_err().code,"credential_reference_rejected");}
 #[test]fn replacement_retains_local_model_options(){let f=crate::conversation_store::uid("replace");dispatch(&req("replace_credential",json!({"requestId":"first","expectedCredentialRevision":0,"apiKey":"p152-fictional-first"})),&f).unwrap();dispatch(&req("select_model",json!({"requestId":"m1","modelId":"model-one"})),&f).unwrap();dispatch(&req("select_model",json!({"requestId":"m2","modelId":"model-two"})),&f).unwrap();dispatch(&req("replace_credential",json!({"requestId":"second","expectedCredentialRevision":1,"apiKey":"p152-fictional-second"})),&f).unwrap();let s=settings(&f).unwrap();assert_eq!(s["models"],json!(["model-one","model-two"]));assert_eq!(s["modelId"],"model-two");}
}

#[cfg(test)]mod credential_fixed_error_tests {
 use super::*;
 #[test]fn keychain_failure_is_fixed_and_contains_no_backend_detail(){
  assert_eq!(ce(crypto::CredentialFailure::KeychainUnavailable).code,"credential_unavailable");
  assert_eq!(ce(crypto::CredentialFailure::KeychainMissing).code,"credential_missing");
 }
}

// D-0666: fixed Host-only read-only configuration access. Never copy or enumerate the real store.
fn online_readonly(name:&str)->R<Connection>{
 if !crate::runtime_root::is_online()||!["provider.sqlite","conversation.sqlite"].contains(&name){return fail("online_configuration_not_authorized")}
 let root=std::path::Path::new(crate::runtime_root::REAL_ROOT);let mut parent=std::path::PathBuf::new();for part in root.components(){parent.push(part);let m=std::fs::symlink_metadata(&parent).map_err(|_|Error::new("readonly_path_rejected"))?;if !m.is_dir()||m.file_type().is_symlink(){return fail("readonly_path_rejected")}}
 let rm=std::fs::symlink_metadata(root).map_err(|_|Error::new("readonly_path_rejected"))?;if rm.uid()!=unsafe{libc::getuid()}||rm.mode()&0o777!=0o700{return fail("readonly_path_rejected")}let p=root.join(name);let m=std::fs::symlink_metadata(&p).map_err(|_|Error::new("readonly_database_unavailable"))?;if !m.is_file()||m.file_type().is_symlink()||m.nlink()!=1||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o600{return fail("readonly_path_rejected")}
 Connection::open_with_flags(p,rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY|rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW).map_err(|_|Error::new("readonly_database_unavailable"))
}
fn online_provider()->R<Connection>{let c=online_readonly("provider.sqlite")?;let pending:i64=c.query_row("SELECT count(*) FROM provider_operations WHERE state IN ('prepared','cleanup_pending')",[],|r|r.get(0)).map_err(|_|Error::new("store_contract_mismatch"))?;if pending!=0{return fail("credential_cleanup_pending")}Ok(c)}
fn online_settings()->R<Value>{let c=online_provider()?;let mut p=row(&c).map_err(|_|Error::new("online_provider_profile_rejected"))?.0;p.as_object_mut().unwrap().remove("maskedTail");Ok(p)}
fn fixed_configuration_rows(c:&Connection)->R<(Value,Value)>{
 // No dynamic row ID, projection, full-table scan, or conversation content query.
 let lifecycle:String=c.query_row("SELECT body FROM sources WHERE id='_provider_lifecycle' AND length(body)<=16384",[],|r|r.get(0)).map_err(|_|Error::new("online_lifecycle_unavailable"))?;
 let catalog:Option<String>=c.query_row("SELECT CASE WHEN length(body)<=16384 THEN body ELSE '' END FROM sources WHERE id='_settings_catalog'",[],|r|r.get(0)).optional().map_err(|_|Error::new("online_catalog_unavailable"))?;
 let a=crate::strict_json::parse(&lifecycle).map_err(|_|Error::new("store_contract_mismatch"))?;
 let b=match catalog{None=>json!({"revision":0,"settings":null}),Some(text)=>{if text.len()>16384{return fail("online_catalog_rejected")}crate::strict_json::parse(&text).map_err(|_|Error::new("online_catalog_rejected"))?}};Ok((a,b))
}
pub(crate) fn online_configuration()->R<(Value,Value)>{let c=online_readonly("conversation.sqlite")?;c.execute_batch("BEGIN DEFERRED").map_err(|_|Error::new("readonly_database_unavailable"))?;let result=fixed_configuration_rows(&c);let _=c.execute_batch("ROLLBACK");result}
#[cfg(test)]mod online_configuration_tests{
 use super::*;
 #[test]fn only_two_fixed_metadata_rows_are_returned(){let c=Connection::open_in_memory().unwrap();c.execute_batch(r#"CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);INSERT INTO sources VALUES('_provider_lifecycle','{"state":"succeeded"}'),('_settings_catalog','{"revision":7}'),('conversation','private-body-canary');"#).unwrap();let (a,b)=fixed_configuration_rows(&c).unwrap();assert_eq!(a["state"],"succeeded");assert_eq!(b["revision"],7);assert!(!format!("{a}{b}").contains("private-body-canary"));assert_eq!(c.total_changes(),3);}
 #[test]fn missing_or_oversized_metadata_fails_closed(){let c=Connection::open_in_memory().unwrap();c.execute_batch("CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);").unwrap();assert!(fixed_configuration_rows(&c).is_err());c.execute("INSERT INTO sources VALUES('_provider_lifecycle',?1)",["x".repeat(16385)]).unwrap();c.execute("INSERT INTO sources VALUES('_settings_catalog','{}')",[]).unwrap();assert!(fixed_configuration_rows(&c).is_err());}
 #[test]fn offline_cannot_open_real_configuration(){assert_eq!(online_readonly("conversation.sqlite").unwrap_err().code,"online_configuration_not_authorized");}
}

#[cfg(test)]mod optional_online_catalog_test{use super::*;#[test]fn absent_catalog_preserves_existing_default_without_writes(){let c=Connection::open_in_memory().unwrap();c.execute_batch(r#"CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);INSERT INTO sources VALUES('_provider_lifecycle','{"state":"succeeded"}');"#).unwrap();let (_,b)=fixed_configuration_rows(&c).unwrap();assert_eq!(b,json!({"revision":0,"settings":null}));assert_eq!(c.total_changes(),1);}}
