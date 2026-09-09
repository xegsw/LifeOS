//! Direct target grants; only explicit synthetic fixture transports are executable.
use crate::{
    repository::{self, Error},
    source_api,
    source_file::FileGrant,
    source_store::{self, Imported},
};
use rusqlite::{params, Connection, OptionalExtension};
use serde_json::{json, Value};
use std::io::Write;
type R<T> = Result<T, Error>;
fn err(s: &str) -> Error {
    Error::new(s)
}
fn bound(c: &Connection, link: &str) -> R<(String, i64, String, String)> {
    c.query_row("SELECT f.connector_id,f.version,l.target_ref,l.parent_file FROM source_links l JOIN source_files f ON f.id=l.parent_file WHERE l.id=? AND f.version=l.parent_version AND f.parse_state='parsed'",[link],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(|_|err("target_parent_stale"))
}
pub fn grant(c: &Connection, p: &Value) -> R<Value> {
    let link = p["linkId"]
        .as_str()
        .filter(|s| source_store::valid_id(s))
        .ok_or_else(|| err("identity_rejected"))?;
    let (owner, _, _, _) = bound(c, link)?;
    if p["connectorId"] != owner {
        return Err(err("target_owner_rejected"));
    }
    let parent = source_api::lease(c, &owner)?;
    source_store::check(c, &parent)?;
    if p["expectedGeneration"] != parent.generation {
        return Err(err("stale_generation"));
    }
    let decision = p["decision"]
        .as_str()
        .filter(|s| matches!(*s, "grant" | "revoke"))
        .ok_or_else(|| err("dto_rejected"))?;
    let sid = format!("target:{}", &source_api::hex(link)[..32]);
    let old: Option<i64> = c
        .query_row(
            "SELECT grant_generation FROM connectors WHERE id=?",
            [&sid],
            |r| r.get(0),
        )
        .optional()?;
    let g = old.unwrap_or(0) + 1;
    if g > 9007199254740991 {
        return Err(err("integer_rejected"));
    }
    let active = decision == "grant";
    c.execute("INSERT INTO connectors VALUES(?1,?2,?2,?3,?4) ON CONFLICT(id) DO UPDATE SET grant_generation=?2,epoch=?2,state=?3",params![sid,g,if active{"active"}else{"disconnected"},link])?;
    c.execute("INSERT INTO connector_grants VALUES(?1,?2,?3,?4,?5) ON CONFLICT(id) DO UPDATE SET generation=?4,state=?5",params![sid,owner,link,g,if active{"active"}else{"revoked"}])?;
    c.execute(
        "INSERT INTO sources VALUES(?1,?2) ON CONFLICT(id) DO UPDATE SET body=?2",
        params![
            sid,
            json!({"id":sid,"sourceType":"external_reference","authorized":active,"generation":g})
                .to_string()
        ],
    )?;
    let mut q = c.prepare("SELECT id FROM records WHERE json_extract(body,'$.sourceId')=?")?;
    let ids = q
        .query_map([&sid], |r| r.get::<_, String>(0))?
        .collect::<Result<Vec<_>, _>>()?;
    drop(q);
    for id in ids {
        source_store::invalidate(c, &id)?;
        c.execute(
            "UPDATE records SET body=json_set(body,'$.status','revoked') WHERE id=?",
            [id],
        )?;
    }
    c.execute(
        "UPDATE source_links SET state=?2,grant_id=?3 WHERE id=?1",
        params![link, if active { "fetch_pending" } else { "revoked" }, sid],
    )?;
    Ok(
        json!({"linkId":link,"grantGeneration":g,"status":if active{"fetch_pending"}else{"revoked"}}),
    )
}
pub fn valid(c: &Connection, sid: &str) -> R<bool> {
    let root: Option<String> = c
        .query_row("SELECT root_ref FROM connectors WHERE id=?", [sid], |r| {
            r.get(0)
        })
        .optional()?;
    let Some(link) = root.filter(|s| s.starts_with("link:")) else {
        return Ok(true);
    };
    let Ok((owner, _, _, _)) = bound(c, &link) else {
        return Ok(false);
    };
    let parent = source_api::lease(c, &owner)?;
    if source_store::check(c, &parent).is_err() {
        return Ok(false);
    }
    let state: Option<String> = c
        .query_row(
            "SELECT state FROM connector_grants WHERE id=?",
            [sid],
            |r| r.get(0),
        )
        .optional()?;
    Ok(state.as_deref() == Some("active"))
}
static SLOTS: std::sync::OnceLock<(std::sync::Mutex<usize>, std::sync::Condvar)> =
    std::sync::OnceLock::new();
pub fn run(fixture: &str, link: &str, generation: i64) {
    let fixture = fixture.to_string();
    let link = link.to_string();
    std::thread::spawn(move || {
        let (lock, wake) =
            SLOTS.get_or_init(|| (std::sync::Mutex::new(0), std::sync::Condvar::new()));
        let mut count = lock.lock().unwrap();
        while *count >= 2 {
            count = wake.wait(count).unwrap()
        }
        *count += 1;
        drop(count);
        let Ok(_publish)=crate::gate() else {return};
        let result = fetch(&fixture, &link, generation);
        if let Err(e) = result {
            if let Ok(c) = repository::open(&fixture) {
                let _ = c.execute(
                    "UPDATE source_links SET state=?2 WHERE id=?1 AND state='fetch_pending' AND grant_id IN(SELECT id FROM connectors WHERE grant_generation=?3)",
                    params![link, format!("unavailable:{}", e.code),generation],
                );
            }
        }
        *lock.lock().unwrap() -= 1;
        wake.notify_one();
    });
}
fn fetch(fixture: &str, link: &str, generation: i64) -> R<()> {
    let mut c = repository::open(fixture)?;
    source_store::init(&c)?;
    let (_, _, target, _) = bound(&c, link)?;
    let sid = format!("target:{}", &source_api::hex(link)[..32]);
    let l = source_api::lease(&c, &sid)?;
    if l.generation != generation {
        return Err(err("target_grant_stale"));
    }
    if !valid(&c, &sid)? {
        return Err(err("target_grant_stale"));
    }
    source_store::check(&c, &l)?;
    let root = crate::runtime_root::verify()?;
    let dir = crate::artifact_io::Dir::root()?
        .child("artifacts", false)?
        .child(&format!("target-{}", &source_api::hex(fixture)[..16]), true)?;
    let token = format!("target-{}-{}", &source_api::hex(link)[..32], l.generation);
    let mut staging = dir.create(&format!("{token}.staging"))?;
    let mut bytes = vec![];
    if target == "../external/approved.txt" {
        let grant = FileGrant::synthetic(&root.join("fixtures/external"))?;
        let identity = grant.identity("approved.txt")?;
        grant.copy("approved.txt", &identity, &mut staging)?;
        bytes = staging.read_limit(64 * 1024 * 1024)?;
    } else {
        // This transport is injected into the same WebSourceAdapter exercised by policy tests.
        let mut child = std::process::Command::new(
            "/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
        )
        .args([concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/tools/fetch_source.mjs"
        )])
        .env("TMPDIR", root.join(".runtime"))
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null())
        .spawn()
        .map_err(|_| err("transport_unavailable"))?;
        child
            .stdin
            .take()
            .ok_or_else(|| err("transport_unavailable"))?
            .write_all(target.as_bytes())
            .map_err(|_| err("transport_unavailable"))?;
        let output = child
            .wait_with_output()
            .map_err(|_| err("transport_unavailable"))?;
        if !output.status.success() {
            return Err(err("target_unavailable"));
        }
        let response: Value =
            serde_json::from_slice(&output.stdout).map_err(|_| err("transport_unavailable"))?;
        if response["status"] != "fetched" {
            return Err(err("target_unavailable"));
        }
        bytes = response["body"]
            .as_str()
            .ok_or_else(|| err("target_unavailable"))?
            .as_bytes()
            .to_vec();
        staging.write_all(&bytes)?;
        staging.sync()?;
    }
    if bytes.len() > 64 * 1024 * 1024 {
        return Err(err("parse_memory_budget"));
    }
    let text = String::from_utf8(bytes).map_err(|_| err("unsupported_encoding"))?;
    let mut segments = vec![];
    let mut chunk = String::new();
    let mut count = 0usize;
    let mut start = 0usize;
    for ch in text.chars() {
        chunk.push(ch);
        count += 1;
        if count == 1024 {
            segments.push((format!("target:char:{start}"), std::mem::take(&mut chunk)));
            start += count;
            count = 0;
        }
    }
    if !chunk.is_empty() {
        segments.push((format!("target:char:{start}"), chunk));
    }
    if !valid(&c, &sid)? {
        return Err(err("target_grant_stale"));
    }
    let file = format!("file:{}", &source_api::hex(link)[..32]);
    let imported = Imported {
        id: file.clone(),
        external_ref: link.into(),
        version: l.generation,
        identity: format!("target:{}", l.generation),
        fingerprint: source_api::hex(&text),
        artifact_ref: token,
        mime: "text/plain".into(),
        bytes: text.len() as i64,
        observed_at: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64,
        status: "parsed".into(),
        reason: None,
        segments,
        links: vec![],
    };
    let published = staging.publish(&dir, &imported.artifact_ref)?;
    published.validate()?;
    source_store::commit_batch(
        &mut c,
        &l,
        &[imported],
        &format!("fetch:{}:{}", &source_api::hex(link)[..32], l.generation),
    )?;
    Ok(())
}
