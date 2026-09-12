//! Internal connector storage. Reuses the 146 repository connection and records authority.
use crate::repository::Error;
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
type R<T> = Result<T, Error>;
const MAX: i64 = 9007199254740991;
fn fail<T>(s: &str) -> R<T> {
    Err(Error::new(s))
}
pub fn valid_id(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 120
        && s.bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"-_:".contains(&b))
}
// One bound-reference check shared by preview creation, send, response, and citation use.
// Consults existing source authority only; no filesystem or additional grant store.
pub fn validate_reference(c: &Connection, sr: &Value) -> R<()> {
    let connector = sr["connectorId"]
        .as_str()
        .ok_or_else(|| Error::new("context_stale"))?;
    let current =
        crate::source_api::lease(c, connector).map_err(|_| Error::new("authorization_rejected"))?;
    check(c, &current).map_err(|_| Error::new("authorization_rejected"))?;
    if json!(current.generation) != sr["authorizationGeneration"] {
        return fail("authorization_rejected");
    }
    if json!(current.epoch) != sr["scanEpoch"] {
        return fail("context_stale");
    }
    let row: Option<(String, String, String)> = c.query_row(
        "SELECT s.locator,s.text,r.body FROM source_segments s JOIN source_files f ON f.id=s.file_id JOIN records r ON r.id=s.record_id WHERE s.id=?1 AND s.record_id=?2 AND s.file_id=?3 AND f.connector_id=?4 AND s.version=?5 AND f.version=s.version AND f.parse_state='parsed' AND f.seen_epoch=?6",
        params![sr["segmentId"].as_str(),sr["recordId"].as_str(),sr["sourceRef"].as_str(),connector,sr["version"].as_i64(),current.epoch],
        |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
    let Some((locator, text, raw)) = row else {
        return fail("context_stale");
    };
    let r: Value = serde_json::from_str(&raw).map_err(|_| Error::new("context_stale"))?;
    if r["status"] != "active"
        || r["version"] != sr["version"]
        || r["sourceId"] != connector
        || r["sourceFile"] != sr["sourceRef"]
        || r["text"] != text
        || sr["locator"] != locator
    {
        return fail("context_stale");
    }
    let start = sr["startScalar"]
        .as_u64()
        .ok_or_else(|| Error::new("context_stale"))?;
    let end = sr["endScalar"]
        .as_u64()
        .ok_or_else(|| Error::new("context_stale"))?;
    if start >= end || end > text.chars().count() as u64 || end - start > 800 {
        return fail("context_stale");
    }
    Ok(())
}
pub fn validate_existing(c:&Connection)->R<()>{
 c.prepare("SELECT id,grant_generation,epoch,state,root_ref FROM connectors LIMIT 0")?;
 c.prepare("SELECT id,connector_id,target_ref,generation,state FROM connector_grants LIMIT 0")?;
 c.prepare("SELECT id,connector_id,parent_ref,cursor,scan_epoch,state FROM scan_entries LIMIT 0")?;
 c.prepare("SELECT id,connector_id,external_ref,version,identity,fingerprint,artifact_ref,parse_state,reason,seen_epoch FROM source_files LIMIT 0")?;
 c.prepare("SELECT id,connector_id,epoch,state,counters,checkpoint FROM import_jobs LIMIT 0")?;
 c.prepare("SELECT id,opaque_ref,mime,bytes,version FROM source_artifacts LIMIT 0")?;
 c.prepare("SELECT id,parent_file,parent_version,target_ref,grant_id,state,fetched_at,final_ref,target_version FROM source_links LIMIT 0")?;
 c.prepare("SELECT id,file_id,version,ordinal,locator,text,record_id FROM source_segments LIMIT 0")?;
 c.prepare("SELECT segment_id,text FROM source_fts LIMIT 0")?;
 c.prepare("SELECT id,epoch FROM source_cursor_epochs LIMIT 0")?;
 c.prepare("SELECT id,connector_id,source_ref,version,generation,offset FROM source_cursors LIMIT 0")?;
 c.prepare("SELECT id,identity FROM scan_identities LIMIT 0")?;
 c.prepare("SELECT id,payload,result FROM connector_requests LIMIT 0")?;

 Ok(())
}
pub fn init(c: &Connection) -> R<()> {
    if crate::runtime_root::is_real(){return validate_existing(c);}

    c.execute_batch("PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS connectors(id TEXT PRIMARY KEY,grant_generation INTEGER NOT NULL,epoch INTEGER NOT NULL,state TEXT NOT NULL,root_ref TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS connector_grants(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL REFERENCES connectors(id),target_ref TEXT NOT NULL,generation INTEGER NOT NULL,state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scan_entries(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL REFERENCES connectors(id),parent_ref TEXT NOT NULL,cursor INTEGER NOT NULL,scan_epoch INTEGER NOT NULL,state TEXT NOT NULL,UNIQUE(connector_id,parent_ref,scan_epoch));
CREATE TABLE IF NOT EXISTS source_files(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL REFERENCES connectors(id),external_ref TEXT NOT NULL,version INTEGER NOT NULL,identity TEXT NOT NULL,fingerprint TEXT NOT NULL,artifact_ref TEXT NOT NULL,parse_state TEXT NOT NULL,reason TEXT,seen_epoch INTEGER NOT NULL,UNIQUE(connector_id,external_ref));
CREATE TABLE IF NOT EXISTS import_jobs(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL REFERENCES connectors(id),epoch INTEGER NOT NULL,state TEXT NOT NULL,counters TEXT NOT NULL,checkpoint TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_artifacts(id TEXT PRIMARY KEY,opaque_ref TEXT UNIQUE NOT NULL,mime TEXT NOT NULL,bytes INTEGER NOT NULL,version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS source_links(id TEXT PRIMARY KEY,parent_file TEXT NOT NULL REFERENCES source_files(id),parent_version INTEGER NOT NULL,target_ref TEXT NOT NULL,grant_id TEXT,state TEXT NOT NULL,fetched_at INTEGER,final_ref TEXT,target_version INTEGER);
CREATE TABLE IF NOT EXISTS source_segments(id TEXT PRIMARY KEY,file_id TEXT NOT NULL REFERENCES source_files(id),version INTEGER NOT NULL,ordinal INTEGER NOT NULL,locator TEXT NOT NULL,text TEXT NOT NULL,record_id TEXT NOT NULL,UNIQUE(file_id,version,ordinal));
CREATE VIRTUAL TABLE IF NOT EXISTS source_fts USING fts5(segment_id UNINDEXED,text);
CREATE TABLE IF NOT EXISTS source_cursor_epochs(id TEXT PRIMARY KEY,epoch INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS source_cursors(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL,source_ref TEXT NOT NULL,version INTEGER NOT NULL,generation INTEGER NOT NULL,offset INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS scan_identities(id TEXT PRIMARY KEY,identity TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS connector_requests(id TEXT PRIMARY KEY,payload TEXT NOT NULL,result TEXT NOT NULL);")?;
    Ok(())
}
#[derive(Debug, Clone)]
pub struct Lease {
    pub connector: String,
    pub generation: i64,
    pub epoch: i64,
}
pub fn check(c: &Connection, l: &Lease) -> R<()> {
    if !valid_id(&l.connector)
        || l.generation < 1
        || l.generation > MAX
        || l.epoch < 1
        || l.epoch > MAX
    {
        return fail("identity_rejected");
    }
    let row: Option<(i64, i64, String)> = c
        .query_row(
            "SELECT grant_generation,epoch,state FROM connectors WHERE id=?",
            [&l.connector],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()?;
    if row != Some((l.generation, l.epoch, "active".into())) {
        return fail("grant_or_worker_stale");
    }
    let authorized: bool = c.query_row(
        "SELECT json_extract(body,'$.authorized') FROM sources WHERE id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    let generation: i64 = c.query_row(
        "SELECT json_extract(body,'$.generation') FROM sources WHERE id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    if !authorized || generation != l.generation || !crate::source_targets::valid(c, &l.connector)?
    {
        return fail("authorization_rejected");
    }
    Ok(())
}
pub fn connect(c: &mut Connection, request: &str, connector: &str, root_ref: &str) -> R<Lease> {
    if !valid_id(request) || !valid_id(connector) || !valid_id(root_ref) {
        return fail("identity_rejected");
    }
    let payload =
        json!({"operation":"connect","connector":connector,"rootRef":root_ref}).to_string();
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    if let Some((p, r)) = tx
        .query_row(
            "SELECT payload,result FROM connector_requests WHERE id=?",
            [request],
            |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)),
        )
        .optional()?
    {
        if p != payload {
            return fail("idempotency_conflict");
        };
        let v: Value = serde_json::from_str(&r).map_err(|_| Error::new("receipt_corrupt"))?;
        return Ok(Lease {
            connector: connector.into(),
            generation: v["generation"].as_i64().unwrap(),
            epoch: v["epoch"].as_i64().unwrap(),
        });
    }
    let old: Option<(i64, i64, String)> = tx
        .query_row(
            "SELECT grant_generation,epoch,state FROM connectors WHERE id=?",
            [connector],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()?;
    let (generation, epoch) = match old {
        Some((g, e, s)) => {
            if s != "disconnected" || g >= MAX || e >= MAX {
                return fail("connector_state_rejected");
            }
            (g + 1, e + 1)
        }
        None => (1, 1),
    };
    tx.execute("INSERT INTO connectors VALUES(?1,?2,?3,'active',?4) ON CONFLICT(id) DO UPDATE SET grant_generation=excluded.grant_generation,epoch=excluded.epoch,state='active',root_ref=excluded.root_ref",params![connector,generation,epoch,root_ref])?;
    tx.execute("INSERT INTO sources VALUES(?1,?2) ON CONFLICT(id) DO UPDATE SET body=excluded.body",params![connector,json!({"id":connector,"sourceType":"local_file","authorized":true,"generation":generation}).to_string()])?;
    let reply = json!({"generation":generation,"epoch":epoch}).to_string();
    tx.execute(
        "INSERT INTO connector_requests VALUES(?1,?2,?3)",
        params![request, payload, reply],
    )?;
    tx.commit()?;
    Ok(Lease {
        connector: connector.into(),
        generation,
        epoch,
    })
}
pub fn control(c: &mut Connection, l: &Lease, request: &str, action: &str) -> R<Lease> {
    if !valid_id(request)
        || !valid_id(&l.connector)
        || !matches!(
            action,
            "pause" | "resume" | "cancel" | "refresh" | "disconnect"
        )
    {
        return fail("dto_rejected");
    }
    let p =
        json!({"connector":l.connector,"generation":l.generation,"epoch":l.epoch,"action":action})
            .to_string();
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    if let Some((old, r)) = tx
        .query_row(
            "SELECT payload,result FROM connector_requests WHERE id=?",
            [request],
            |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)),
        )
        .optional()?
    {
        if old != p {
            return fail("idempotency_conflict");
        };
        let v: Value = serde_json::from_str(&r).map_err(|_| Error::new("receipt_corrupt"))?;
        return Ok(Lease {
            connector: l.connector.clone(),
            generation: v["generation"].as_i64().unwrap(),
            epoch: v["epoch"].as_i64().unwrap(),
        });
    }
    let (g, e, s): (i64, i64, String) = tx.query_row(
        "SELECT grant_generation,epoch,state FROM connectors WHERE id=?",
        [&l.connector],
        |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
    )?;
    if g != l.generation || e != l.epoch || g >= MAX || e >= MAX || s == "disconnected" {
        return fail("grant_or_worker_stale");
    }
    if action == "resume" && s != "paused" {
        return fail("connector_state_rejected");
    }
    let state = match action {
        "pause" => "paused",
        "cancel" => "cancelled",
        "disconnect" => "disconnected",
        _ => "active",
    };
    let generation = if action == "disconnect" {
        tx.execute(
            "UPDATE source_files SET parse_state='revoked' WHERE connector_id=?",
            [&l.connector],
        )?;
        g + 1
    } else {
        g
    };
    let epoch = e + 1;
    tx.execute(
        "UPDATE connectors SET grant_generation=?2,epoch=?3,state=?4 WHERE id=?1",
        params![l.connector, generation, epoch, state],
    )?;
    if action != "refresh" {
        tx.execute(
            "UPDATE import_jobs SET epoch=?2 WHERE connector_id=?1 AND epoch=?3",
            params![l.connector, epoch, e],
        )?;
        tx.execute(
            "UPDATE scan_entries SET scan_epoch=?2 WHERE connector_id=?1 AND scan_epoch=?3",
            params![l.connector, epoch, e],
        )?;
    }
    if action == "disconnect" {
        tx.execute(
            "UPDATE source_files SET parse_state='revoked' WHERE connector_id=?",
            [&l.connector],
        )?;
        tx.execute("UPDATE sources SET body=json_set(body,'$.authorized',json('false'),'$.generation',?2) WHERE id=?1",params![l.connector,generation])?;
        tx.execute("UPDATE connector_grants SET state='revoked',generation=generation+1 WHERE connector_id=?",[&l.connector])?;
        let mut q = tx.prepare("SELECT id FROM records WHERE json_extract(body,'$.sourceId')=?")?;
        let ids = q
            .query_map([&l.connector], |r| r.get::<_, String>(0))?
            .collect::<Result<Vec<_>, _>>()?;
        drop(q);
        for id in ids {
            invalidate(&tx, &id)?;
            tx.execute(
                "UPDATE records SET body=json_set(body,'$.status','revoked') WHERE id=?",
                [id],
            )?;
        }
    }
    let reply = json!({"generation":generation,"epoch":epoch}).to_string();
    tx.execute(
        "INSERT INTO connector_requests VALUES(?1,?2,?3)",
        params![request, p, reply],
    )?;
    tx.commit()?;
    Ok(Lease {
        connector: l.connector.clone(),
        generation,
        epoch,
    })
}
pub(crate) fn invalidate(c: &Connection, rid: &str) -> R<()> {
    for table in ["packets", "derivations", "memories", "states"] {
        c.execute(&format!("UPDATE {table} SET body=json_set(body,'$.status','stale') WHERE json_extract(body,'$.rawId')=?1 OR EXISTS(SELECT 1 FROM json_each(json_extract({table}.body,'$.inputRefs')) WHERE json_extract(value,'$.id')=?1)"),[rid])?;
    }
    Ok(())
}
#[derive(Clone)]
pub struct Imported {
    pub id: String,
    pub external_ref: String,
    pub version: i64,
    pub identity: String,
    pub fingerprint: String,
    pub artifact_ref: String,
    pub mime: String,
    pub bytes: i64,
    pub observed_at: i64,
    pub status: String,
    pub reason: Option<String>,
    pub segments: Vec<(String, String)>,
    pub links: Vec<String>,
}
pub fn commit_batch(c: &mut Connection, l: &Lease, items: &[Imported], request: &str) -> R<()> {
    if items.len() > 50 || !valid_id(request) {
        return fail("batch_rejected");
    }
    let signature = json!(items
        .iter()
        .map(|v| json!([
            v.id,
            v.external_ref,
            v.version,
            v.identity,
            v.fingerprint,
            v.artifact_ref,
            v.mime,
            v.bytes,
            v.observed_at,
            v.status,
            v.reason,
            v.segments,
            v.links
        ]))
        .collect::<Vec<_>>())
    .to_string();
    let payload = json!([l.connector, l.generation, l.epoch, signature]).to_string();
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    check(&tx, l)?;
    if let Some(old) = tx
        .query_row(
            "SELECT payload FROM connector_requests WHERE id=?",
            [request],
            |r| r.get::<_, String>(0),
        )
        .optional()?
    {
        if old == payload {
            return Ok(());
        }
        return fail("idempotency_conflict");
    }
    for item in items {
        if !valid_id(&item.id)
            || !valid_id(&item.artifact_ref)
            || item.version < 1
            || item.version > MAX
            || item.bytes < 0
            || item.bytes > MAX
            || !matches!(
                item.status.as_str(),
                "parsed" | "restricted" | "unparsed" | "pending"
            )
        {
            return fail("item_rejected");
        }
        if item.status != "parsed" && (!item.segments.is_empty() || !item.links.is_empty()) {
            return fail("restricted_content_rejected");
        }
        let old:Option<(i64,String,String)>=tx.query_row("SELECT version,fingerprint,id FROM source_files WHERE connector_id=?1 AND external_ref=?2",params![l.connector,item.external_ref],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
        if let Some((v, hash, id)) = old {
            if item.version < v {
                return fail("source_version_stale");
            }
            if id != item.id {
                return fail("source_identity_conflict");
            }
            if item.version == v {
                if hash == item.fingerprint {
                    continue;
                }
                return fail("source_version_conflict");
            }
            if matches!(item.status.as_str(), "pending" | "unparsed")
                && item.reason.as_deref() != Some("original_only")
            {
                tx.execute(
                    "INSERT INTO source_artifacts VALUES(?1,?1,?2,?3,?4)",
                    params![item.artifact_ref, item.mime, item.bytes, item.version],
                )?;
                tx.execute(
                    "UPDATE source_files SET reason=?2,seen_epoch=?3 WHERE id=?1",
                    params![item.id, item.reason, l.epoch],
                )?;
                tx.execute(
                    "UPDATE import_jobs SET state='failed',counters=?2 WHERE id=?1",
                    params![item.id, json!({"reason":item.reason}).to_string()],
                )?;
                continue;
            }
            invalidate_targets(&tx, &item.id)?;
            tx.execute("UPDATE source_links SET state='awaiting_target_grant',target_version=NULL WHERE final_ref=?",[&item.id])?;
            let mut q = tx.prepare("SELECT record_id FROM source_segments WHERE file_id=?")?;
            let ids = q
                .query_map([&item.id], |r| r.get::<_, String>(0))?
                .collect::<Result<Vec<_>, _>>()?;
            drop(q);
            for rid in ids {
                invalidate(&tx, &rid)?;
                tx.execute(
                    "UPDATE records SET body=json_set(body,'$.status','superseded') WHERE id=?",
                    [rid],
                )?;
            }
        }
        tx.execute(
            "INSERT INTO source_artifacts VALUES(?1,?1,?2,?3,?4)",
            params![item.artifact_ref, item.mime, item.bytes, item.version],
        )?;
        tx.execute("INSERT INTO source_files VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10) ON CONFLICT(id) DO UPDATE SET version=excluded.version,identity=excluded.identity,fingerprint=excluded.fingerprint,artifact_ref=excluded.artifact_ref,parse_state=excluded.parse_state,reason=excluded.reason,seen_epoch=excluded.seen_epoch",params![item.id,l.connector,item.external_ref,item.version,item.identity,item.fingerprint,item.artifact_ref,item.status,item.reason,l.epoch])?;
        tx.execute(
            "UPDATE import_jobs SET state='done' WHERE id=?1 AND epoch=?2",
            params![item.id, l.epoch],
        )?;
        for (i, target) in item.links.iter().enumerate() {
            let link = format!("link:{}:{}:{i}", item.id, item.version);
            tx.execute("INSERT INTO source_links(id,parent_file,parent_version,target_ref,state) VALUES(?1,?2,?3,?4,'awaiting_target_grant')",params![link,item.id,item.version,target])?;
        }
        for (i, (locator, text)) in item.segments.iter().enumerate() {
            let rid = format!("seg:{}:{}:{i}", item.id, item.version);
            let ext = format!("{}:{i}", item.id);
            let body = json!({"id":rid,"sourceId":l.connector,"externalId":ext,"version":item.version,"text":text,"domain":"person","intent":"source","status":"active","observedAt":item.observed_at,"validUntil":null,"confirmed":false,"sourceFile":item.id,"locator":locator,"contentHash":format!("{:x}",Sha256::digest(text.as_bytes()))});
            tx.execute(
                "INSERT INTO records VALUES(?1,?2)",
                params![rid, body.to_string()],
            )?;
            tx.execute(
                "INSERT INTO source_segments VALUES(?1,?2,?3,?4,?5,?6,?1)",
                params![rid, item.id, item.version, i as i64, locator, text],
            )?;
            tx.execute(
                "INSERT INTO source_fts(segment_id,text) VALUES(?1,?2)",
                params![rid, text],
            )?;
        }
    }
    check(&tx, l)?;
    for item in items {
        tx.execute("UPDATE source_links SET state='fetched',final_ref=?1,target_version=?2,fetched_at=?3 WHERE id=(SELECT root_ref FROM connectors WHERE id=?4) AND grant_id=?4 AND state='fetch_pending'", params![item.id,item.version,item.observed_at,l.connector])?;
    }
    tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1", [])?;
    tx.execute(
        "INSERT INTO connector_requests VALUES(?1,?2,'{}')",
        params![request, payload],
    )?;
    tx.commit()?;
    Ok(())
}
pub fn evidence(c: &Connection, l: &Lease, file: &str, version: i64, offset: i64) -> R<Value> {
    check(c, l)?;
    if !valid_id(file) || version < 1 || version > MAX || offset < 0 || offset > MAX {
        return fail("dto_rejected");
    }
    let row: Option<(String, i64, String)> = c
        .query_row(
            "SELECT connector_id,version,parse_state FROM source_files WHERE id=?",
            [file],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()?;
    if row
        .as_ref()
        .is_none_or(|r| r.0 != l.connector || r.1 != version)
    {
        return fail("source_ref_stale");
    }
    let state = row.unwrap().2;
    if state != "parsed" {
        return Ok(json!({"status":state,"segments":[]}));
    }
    let mut q=c.prepare("SELECT text,locator FROM source_segments WHERE file_id=?1 AND version=?2 ORDER BY ordinal LIMIT 50 OFFSET ?3")?;
    let items = q
        .query_map(params![file, version, offset], |r| {
            Ok(json!({"text":r.get::<_,String>(0)?,"locator":r.get::<_,String>(1)?}))
        })?
        .collect::<Result<Vec<_>, _>>()?;
    Ok(json!({"status":"available","segments":items}))
}
fn invalidate_targets(c: &Connection, parent: &str) -> R<()> {
    let mut q=c.prepare("SELECT r.id FROM records r JOIN source_links sl ON sl.grant_id=json_extract(r.body,'$.sourceId') WHERE sl.parent_file=?")?;
    let ids = q
        .query_map([parent], |r| r.get::<_, String>(0))?
        .collect::<Result<Vec<_>, _>>()?;
    drop(q);
    for id in ids {
        invalidate(c, &id)?;
        c.execute(
            "UPDATE records SET body=json_set(body,'$.status','revoked') WHERE id=?",
            [id],
        )?;
    }
    c.execute("UPDATE connector_grants SET state='revoked' WHERE id IN(SELECT grant_id FROM source_links WHERE parent_file=?)",[parent])?;
    c.execute("UPDATE sources SET body=json_set(body,'$.authorized',json('false')) WHERE id IN(SELECT grant_id FROM source_links WHERE parent_file=?)",[parent])?;
    c.execute(
        "UPDATE source_links SET state='parent_stale' WHERE parent_file=?",
        [parent],
    )?;
    Ok(())
}
pub fn missing(c: &mut Connection, l: &Lease, file: &str) -> R<()> {
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    check(&tx, l)?;
    let owner: String = tx.query_row(
        "SELECT connector_id FROM source_files WHERE id=?",
        [file],
        |r| r.get(0),
    )?;
    if owner != l.connector {
        return fail("source_ref_rejected");
    }
    invalidate_targets(&tx, file)?;
    let mut q = tx.prepare("SELECT record_id FROM source_segments WHERE file_id=?")?;
    let ids = q
        .query_map([file], |r| r.get::<_, String>(0))?
        .collect::<Result<Vec<_>, _>>()?;
    drop(q);
    for id in ids {
        invalidate(&tx, &id)?;
        tx.execute(
            "UPDATE records SET body=json_set(body,'$.status','missing') WHERE id=?",
            [id],
        )?;
    }
    tx.execute(
        "UPDATE source_files SET parse_state='missing' WHERE id=?",
        [file],
    )?;
    tx.execute(
        "UPDATE source_links SET state='target_missing' WHERE final_ref=?",
        [file],
    )?;
    tx.commit()?;
    Ok(())
}

pub fn make_cursor(
    c: &Connection,
    l: &Lease,
    file: &str,
    version: i64,
    offset: i64,
    token: &str,
) -> R<()> {
    evidence(c, l, file, version, offset)?;
    if !valid_id(token) {
        return fail("cursor_rejected");
    }
    c.execute(
        "INSERT INTO source_cursors VALUES(?1,?2,?3,?4,?5,?6)",
        params![token, l.connector, file, version, l.generation, offset],
    )?;
    c.execute(
        "INSERT INTO source_cursor_epochs VALUES(?1,?2)",
        params![token, l.epoch],
    )?;
    Ok(())
}
pub fn consume_cursor(
    c: &Connection,
    l: &Lease,
    file: &str,
    version: i64,
    token: &str,
) -> R<Value> {
    check(c, l)?;
    if !valid_id(token) {
        return fail("cursor_rejected");
    }
    let epoch: Option<i64> = c
        .query_row(
            "SELECT epoch FROM source_cursor_epochs WHERE id=?",
            [token],
            |r| r.get(0),
        )
        .optional()?;
    if epoch != Some(l.epoch) {
        return fail("cursor_stale");
    }
    let row:Option<(String,String,i64,i64,i64)>=c.query_row("SELECT connector_id,source_ref,version,generation,offset FROM source_cursors WHERE id=?",[token],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).optional()?;
    match row {
        Some((owner, source, v, g, offset))
            if owner == l.connector && source == file && v == version && g == l.generation =>
        {
            evidence(c, l, file, version, offset)
        }
        _ => fail("cursor_stale"),
    }
}
pub fn search(c: &Connection, l: &Lease, query: &str) -> R<Vec<Value>> {
    check(c, l)?;
    if query.is_empty() || query.len() > 1024 {
        return fail("query_rejected");
    }
    // A bounded lexical query; only matching segments leave SQLite. No model inference.
    let mut terms = std::collections::BTreeSet::new();
    for word in query.split(|ch: char| !ch.is_alphanumeric()) {
        if word.is_ascii() {
            if !word.is_empty() {
                terms.insert(word.to_lowercase());
            }
        } else {
            let chars = word.chars().collect::<Vec<_>>();
            for pair in chars.windows(2) {
                terms.insert(pair.iter().collect::<String>());
            }
        }
    }
    if terms.is_empty() {
        return Ok(vec![]);
    }
    let literal = serde_json::to_string(&terms).map_err(|_| Error::new("query_rejected"))?;
    let mut q=c.prepare("SELECT r.body,(SELECT count(*) FROM json_each(?1) term WHERE instr(lower(s.text),term.value)>0) score FROM source_segments s JOIN source_files sf ON sf.id=s.file_id JOIN records r ON r.id=s.record_id WHERE (sf.connector_id=?2 OR sf.connector_id IN(SELECT tc.id FROM connectors tc JOIN connector_grants cg ON cg.id=tc.id JOIN source_links sl ON sl.id=tc.root_ref JOIN source_files pf ON pf.id=sl.parent_file WHERE cg.connector_id=?2 AND cg.state='active' AND tc.state='active' AND pf.version=sl.parent_version AND pf.parse_state='parsed')) AND sf.version=s.version AND sf.seen_epoch=(SELECT epoch FROM connectors WHERE id=sf.connector_id) AND sf.parse_state='parsed' AND json_extract(r.body,'$.version')=s.version AND json_extract(r.body,'$.status')='active' AND score>0 ORDER BY score DESC,s.ordinal,s.id LIMIT 8")?;
    let raw = q
        .query_map(params![literal, l.connector], |r| r.get::<_, String>(0))?
        .collect::<Result<Vec<_>, _>>()?;
    let rows = raw
        .iter()
        .map(|body| {
            let mut v: Value =
                serde_json::from_str(body).map_err(|_| Error::new("source_corrupt"))?;
            let owner = v["sourceId"]
                .as_str()
                .ok_or_else(|| Error::new("source_corrupt"))?;
            let generation: i64 = c.query_row(
                "SELECT grant_generation FROM connectors WHERE id=?",
                [owner],
                |r| r.get(0),
            )?;
            v["authorizationGeneration"] = json!(generation);
            v["sourceRef"] = v["sourceFile"].clone();
            Ok(v)
        })
        .collect::<R<Vec<_>>>()?;
    Ok(rows)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn db() -> Connection {
        let c = Connection::open_in_memory().unwrap();
        c.execute_batch("CREATE TABLE meta(id INTEGER PRIMARY KEY,revision INTEGER);INSERT INTO meta VALUES(1,0);").unwrap();
        for t in [
            "sources",
            "records",
            "packets",
            "derivations",
            "memories",
            "states",
        ] {
            c.execute_batch(&format!(
                "CREATE TABLE {t}(id TEXT PRIMARY KEY,body TEXT NOT NULL CHECK(json_valid(body)))"
            ))
            .unwrap()
        }
        init(&c).unwrap();
        c
    }
    fn item(id: &str, v: i64) -> Imported {
        Imported {
            id: id.into(),
            external_ref: format!("{id}.md"),
            version: v,
            identity: format!("identity-{v}"),
            fingerprint: format!("fp-{v}"),
            artifact_ref: format!("artifact-{id}-{v}"),
            mime: "text/markdown".into(),
            bytes: 9999,
            observed_at: 1000,
            status: "parsed".into(),
            reason: None,
            segments: vec![("line:1".into(), format!("synthetic content version {v}"))],
            links: vec![],
        }
    }
    #[test]
    fn target_publication_parent_replacement_and_receipt_failure_are_atomic() {
        let mut c = db();
        let parent = connect(&mut c, "connect", "directory", "fixture").unwrap();
        let mut original = item("parent", 1);
        original.links = vec!["https://synthetic.invalid/article".into()];
        commit_batch(&mut c, &parent, &[original], "parent1").unwrap();
        let link = "link:parent:1:0";
        let tx = c.transaction().unwrap();
        crate::source_targets::grant(&tx,&json!({"connectorId":"directory","expectedGeneration":1,"linkId":link,"decision":"grant"})).unwrap();
        tx.commit().unwrap();
        let sid = format!("target:{}", &crate::source_api::hex(link)[..32]);
        let target = crate::source_api::lease(&c, &sid).unwrap();
        let mut body = item("target-file", 1);
        body.external_ref = link.into();
        c.execute_batch("CREATE TRIGGER target_receipt_fail BEFORE INSERT ON connector_requests WHEN NEW.id='target1' BEGIN SELECT RAISE(ABORT,'synthetic failure'); END").unwrap();
        assert!(commit_batch(&mut c, &target, &[body.clone()], "target1").is_err());
        assert_eq!(
            c.query_row("SELECT state FROM source_links WHERE id=?", [link], |r| {
                r.get::<_, String>(0)
            })
            .unwrap(),
            "fetch_pending"
        );
        assert!(search(&c, &target, "synthetic").unwrap().is_empty());
        c.execute_batch("DROP TRIGGER target_receipt_fail").unwrap();
        commit_batch(&mut c, &target, &[body], "target1").unwrap();
        let (state, time): (String, i64) = c
            .query_row(
                "SELECT state,fetched_at FROM source_links WHERE id=?",
                [link],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .unwrap();
        assert_eq!(state, "fetched");
        assert_eq!(time, 1000);
        c.execute(
            "INSERT INTO packets VALUES('packet',?1)",
            [json!({"status":"prepared","inputRefs":[{"id":"seg:target-file:1:0"}]}).to_string()],
        )
        .unwrap();
        commit_batch(&mut c, &parent, &[item("parent", 2)], "parent2").unwrap();
        assert!(check(&c, &target).is_err());
        assert!(evidence(&c, &target, "target-file", 1, 0).is_err());
        assert_eq!(
            c.query_row(
                "SELECT json_extract(body,'$.status') FROM packets WHERE id='packet'",
                [],
                |r| r.get::<_, String>(0)
            )
            .unwrap(),
            "stale"
        );
    }
    #[test]
    fn transactions_versions_and_fault() {
        let mut c = db();
        let l = connect(&mut c, "c1", "connector", "fixture").unwrap();
        commit_batch(&mut c, &l, &[item("file", 1)], "r1").unwrap();
        commit_batch(&mut c, &l, &[item("file", 1)], "r1").unwrap();
        assert_eq!(
            c.query_row("SELECT count(*) FROM records", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            1
        );
        let mut altered = item("file", 1);
        altered.fingerprint = "different".into();
        assert!(commit_batch(&mut c, &l, &[altered.clone()], "r1").is_err());
        assert!(commit_batch(&mut c, &l, &[altered], "r2").is_err());
        c.execute_batch("CREATE TRIGGER fail_receipt BEFORE INSERT ON connector_requests WHEN NEW.id='fault' BEGIN SELECT RAISE(ABORT,'synthetic fault'); END;").unwrap();
        assert!(commit_batch(&mut c, &l, &[item("file", 2)], "fault").is_err());
        assert_eq!(
            evidence(&c, &l, "file", 1, 0).unwrap()["segments"][0]["text"],
            "synthetic content version 1"
        );
        commit_batch(&mut c, &l, &[item("file", 2)], "r3").unwrap();
        assert!(commit_batch(&mut c, &l, &[item("file", 1)], "r4").is_err());
        assert_eq!(
            c.query_row("SELECT count(*) FROM records", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            2
        );
    }
    #[test]
    fn worker_pause_cancel_disconnect_replay() {
        let mut c = db();
        let l = connect(&mut c, "c1", "connector", "fixture").unwrap();
        let paused = control(&mut c, &l, "p1", "pause").unwrap();
        assert!(commit_batch(&mut c, &l, &[item("file", 1)], "r1").is_err());
        assert!(check(&c, &paused).is_err());
        let resumed = control(&mut c, &paused, "p2", "resume").unwrap();
        commit_batch(&mut c, &resumed, &[item("file", 1)], "r1").unwrap();
        let disconnected = control(&mut c, &resumed, "d1", "disconnect").unwrap();
        assert!(search(&c, &resumed, "synthetic").is_err());
        assert!(evidence(&c, &resumed, "file", 1, 0).is_err());
        assert!(commit_batch(&mut c, &resumed, &[item("file", 2)], "late").is_err());
        assert!(check(&c, &disconnected).is_err());
        let reconnect = connect(&mut c, "c2", "connector", "fixture").unwrap();
        assert!(reconnect.generation > l.generation);
        assert!(check(&c, &l).is_err());
        let cancelled = control(&mut c, &reconnect, "cancel", "cancel").unwrap();
        assert!(check(&c, &cancelled).is_err());
    }
    #[test]
    fn cursor_owner_version_generation_and_restricted() {
        let mut c = db();
        let l = connect(&mut c, "c1", "connector", "fixture").unwrap();
        let other = connect(&mut c, "c2", "other", "fixture2").unwrap();
        commit_batch(&mut c, &l, &[item("file", 1)], "r1").unwrap();
        make_cursor(&c, &l, "file", 1, 0, "cursor").unwrap();
        assert!(consume_cursor(&c, &other, "file", 1, "cursor").is_err());
        assert!(evidence(&c, &other, "file", 1, 0).is_err());
        assert!(consume_cursor(&c, &l, "file", 2, "cursor").is_err());
        control(&mut c, &l, "d", "disconnect").unwrap();
        assert!(consume_cursor(&c, &l, "file", 1, "cursor").is_err());
        let fresh = connect(&mut c, "c3", "connector", "fixture").unwrap();
        assert!(consume_cursor(&c, &fresh, "file", 1, "cursor").is_err());
        let mut secret = item("config", 1);
        secret.status = "restricted".into();
        assert!(commit_batch(&mut c, &fresh, &[secret.clone()], "secret").is_err());
        secret.segments.clear();
        commit_batch(&mut c, &fresh, &[secret], "secret").unwrap();
        assert_eq!(
            evidence(&c, &fresh, "config", 1, 0).unwrap(),
            json!({"status":"restricted","segments":[]})
        );
    }
    #[test]
    fn long_source_is_not_confirmation_and_missing_invalidates() {
        let mut c = db();
        let l = connect(&mut c, "c1", "connector", "fixture").unwrap();
        let mut long = item("long", 1);
        long.segments = vec![("char:0".into(), "synthetic ".repeat(100000))];
        commit_batch(&mut c, &l, &[long.clone()], "r1").unwrap();
        assert_eq!(
            evidence(&c, &l, "long", 1, 0).unwrap()["segments"][0]["text"]
                .as_str()
                .unwrap()
                .len(),
            long.segments[0].1.len()
        );
        assert_eq!(
            c.query_row("SELECT count(*) FROM memories", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            0
        );
        assert_eq!(search(&c, &l, "synthetic").unwrap().len(), 1);
        assert!(search(&c, &l, "notfound").unwrap().is_empty());
        c.execute(
            "INSERT INTO packets VALUES('p',?1)",
            [json!({"inputRefs":[{"id":"seg:long:1:0"}],"status":"active"}).to_string()],
        )
        .unwrap();
        missing(&mut c, &l, "long").unwrap();
        assert!(search(&c, &l, "synthetic").unwrap().is_empty());
        let status: String = c
            .query_row(
                "SELECT json_extract(body,'$.status') FROM packets",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(status, "stale");
    }
    #[test]
    fn dto_boundaries_and_batch_atomicity() {
        let mut c = db();
        for s in ["", "../bad", "with space", "路径"] {
            assert!(!valid_id(s));
            assert!(connect(&mut c, "c", s, "fixture").is_err());
        }
        assert!(!valid_id(&"a".repeat(121)));
        let l = connect(&mut c, "c1", "connector", "fixture").unwrap();
        let items = vec![item("x", 1); 51];
        assert!(commit_batch(&mut c, &l, &items, "r").is_err());
        let mut invalid = item("b", 1);
        invalid.version = MAX + 1;
        assert!(commit_batch(&mut c, &l, &[item("a", 1), invalid], "r").is_err());
        assert_eq!(
            c.query_row("SELECT count(*) FROM records", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            0
        );
    }
}
#[cfg(test)]
mod failure_tests {
    use super::*;
    #[test]
    fn failed_new_parse_preserves_old_effective_version() {
        let c = Connection::open_in_memory().unwrap();
        c.execute_batch("CREATE TABLE meta(id INTEGER PRIMARY KEY,revision INTEGER);INSERT INTO meta VALUES(1,0);").unwrap();
        for t in [
            "sources",
            "records",
            "packets",
            "derivations",
            "memories",
            "states",
        ] {
            c.execute_batch(&format!(
                "CREATE TABLE {t}(id TEXT PRIMARY KEY,body TEXT NOT NULL)"
            ))
            .unwrap()
        }
        init(&c).unwrap();
        let mut c = c;
        let l = connect(&mut c, "c", "connector", "fixture").unwrap();
        let good = Imported {
            id: "file".into(),
            external_ref: "file.md".into(),
            version: 1,
            identity: "first".into(),
            fingerprint: "hash1".into(),
            artifact_ref: "artifact1".into(),
            mime: "text/markdown".into(),
            bytes: 5,
            observed_at: 1000,
            status: "parsed".into(),
            reason: None,
            segments: vec![("line:1".into(), "old effective content".into())],
            links: vec![],
        };
        commit_batch(&mut c, &l, &[good.clone()], "r1").unwrap();
        let mut bad = good;
        bad.version = 2;
        bad.identity = "second".into();
        bad.fingerprint = "hash2".into();
        bad.artifact_ref = "artifact2".into();
        bad.status = "unparsed".into();
        bad.reason = Some("unsupported_encoding".into());
        bad.segments.clear();
        commit_batch(&mut c, &l, &[bad], "r2").unwrap();
        assert_eq!(search(&c, &l, "effective").unwrap().len(), 1);
        assert!(evidence(&c, &l, "file", 1, 0).is_ok());
        assert!(evidence(&c, &l, "file", 2, 0).is_err());
        assert_eq!(
            c.query_row("SELECT count(*) FROM source_artifacts", [], |r| r
                .get::<_, i64>(0))
                .unwrap(),
            2
        );
    }
}
