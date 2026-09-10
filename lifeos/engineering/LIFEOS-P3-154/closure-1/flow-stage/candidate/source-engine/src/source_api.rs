//! Approved five source IPC, synthetic-only host adapter.
use crate::{
    repository::{self, Error},
    source_store::{self, Lease},
    source_worker,
};
use rusqlite::{params, Connection, OptionalExtension};
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    sync::{Mutex, OnceLock},
};
type R<T> = Result<T, Error>;
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub version: u8,
    pub payload: Value,
}
pub const COMMANDS: [&str; 5] = [
    "connect_source_directory",
    "control_source_job",
    "get_source_status",
    "authorize_source_target",
    "get_source_evidence",
];
fn error(s: &str) -> Error {
    Error::new(s)
}
fn fields(p: &Value, names: &[&str]) -> R<()> {
    if !p.is_object()
        || p.as_object()
            .unwrap()
            .keys()
            .any(|k| !names.contains(&k.as_str()))
    {
        return Err(error("unknown_field"));
    }
    Ok(())
}
fn id<'a>(p: &'a Value, k: &str) -> R<&'a str> {
    p[k].as_str()
        .filter(|s| source_store::valid_id(s))
        .ok_or_else(|| error("identity_rejected"))
}
fn num(p: &Value, k: &str) -> R<i64> {
    p[k].as_i64()
        .filter(|n| *n >= 1 && *n <= 9007199254740991)
        .ok_or_else(|| error("integer_rejected"))
}
pub fn lease(c: &Connection, s: &str) -> R<Lease> {
    if !source_store::valid_id(s) {
        return Err(error("identity_rejected"));
    }
    c.query_row(
        "SELECT grant_generation,epoch FROM connectors WHERE id=?",
        [s],
        |r| {
            Ok(Lease {
                connector: s.into(),
                generation: r.get(0)?,
                epoch: r.get(1)?,
            })
        },
    )
    .map_err(|_| error("connector_unavailable"))
}
fn readable(c: &Connection, l: &Lease) -> R<()> {
    let state: String = c.query_row(
        "SELECT state FROM connectors WHERE id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    if state == "disconnected" {
        return Err(error("authorization_rejected"));
    }
    Ok(())
}
static RUNNING: OnceLock<Mutex<HashMap<String, bool>>> = OnceLock::new();
fn run(fixture: &str) {
    let key = fixture.to_owned();
    let mut map = RUNNING.get_or_init(Default::default).lock().unwrap();
    if let Some(dirty) = map.get_mut(&key) {
        *dirty = true;
        return;
    }
    map.insert(key.clone(), false);
    drop(map);
    std::thread::spawn(move || {
        let result = (|| -> R<()> {
            let mut c = repository::open(&key)?;
            source_store::init(&c)?;
            {let _publish = crate::gate()?;
            if let Ok(l) = lease(&c, "directory") {
                if source_store::check(&c, &l).is_ok() {
                    source_worker::recover(&c, &l)?;
                }
            }
            }
            loop {
                let _publish = crate::gate()?;
                let l = lease(&c, "directory")?;
                if source_store::check(&c, &l).is_err() {
                    break;
                }
                let scanned = source_worker::scan_page(&mut c, &l)?;
                let imported = source_worker::import_one(&mut c, &l)?;
                if !scanned && !imported {
                    source_worker::finalize_scan(&mut c, &l)?;
                    source_worker::resolve_local_links(&c, &l)?;
                    break;
                }
            }
            Ok(())
        })();
        if let Err(e) = result {
            if !["grant_or_worker_stale", "authorization_rejected"].contains(&e.code.as_str()) {
                if let Ok(c) = repository::open(&key) {
                    let _ = c.execute(
                        "INSERT OR REPLACE INTO source_runtime_errors VALUES('directory',?1)",
                        [e.code],
                    );
                }
            }
        }
        let again = RUNNING
            .get()
            .unwrap()
            .lock()
            .unwrap()
            .remove(&key)
            .unwrap_or(false);
        if again {
            run(&key)
        }
    });
}
fn summary(c: &Connection, l: &Lease) -> R<Value> {
    readable(c, l)?;
    let state: String = c.query_row(
        "SELECT state FROM connectors WHERE id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    let count = |sql: &str| -> R<i64> { Ok(c.query_row(sql, [&l.connector], |r| r.get(0))?) };
    let discovered = count("SELECT count(*) FROM import_jobs WHERE connector_id=? AND epoch=(SELECT epoch FROM connectors WHERE id=import_jobs.connector_id)")?;
    let pending=count("SELECT count(*) FROM import_jobs WHERE connector_id=? AND epoch=(SELECT epoch FROM connectors WHERE id=import_jobs.connector_id) AND state IN('pending','pending_recovery')")?;
    let failed=count("SELECT count(*) FROM import_jobs WHERE connector_id=? AND epoch=(SELECT epoch FROM connectors WHERE id=import_jobs.connector_id) AND state IN('failed','special_file_rejected')")?;
    let parsed =
        count("SELECT count(*) FROM source_files WHERE connector_id=? AND parse_state='parsed'")?;
    let unparsed=count("SELECT count(*) FROM source_files WHERE connector_id=? AND parse_state IN('unparsed','restricted','pending')")?;
    let scan:i64=c.query_row("SELECT count(*) FROM scan_entries WHERE connector_id=?1 AND scan_epoch=?2 AND state='pending'",params![l.connector,l.epoch],|r|r.get(0))?;
    let mut q=c.prepare("SELECT id,version,parse_state,reason,external_ref FROM source_files WHERE connector_id=? ORDER BY external_ref LIMIT 256")?;
    let files=q.query_map([&l.connector],|r|Ok(json!({"sourceRef":r.get::<_,String>(0)?,"version":r.get::<_,i64>(1)?,"status":r.get::<_,String>(2)?,"reason":r.get::<_,Option<String>>(3)?,"title":r.get::<_,String>(4)?})))?.collect::<Result<Vec<_>,_>>()?;
    let mut q=c.prepare("SELECT sl.id,sl.target_ref,sl.state FROM source_links sl JOIN source_files f ON f.id=sl.parent_file WHERE f.connector_id=? AND f.version=sl.parent_version ORDER BY sl.id LIMIT 256")?;
    let links=q.query_map([&l.connector],|r|Ok(json!({"linkId":r.get::<_,String>(0)?,"target":r.get::<_,String>(1)?,"status":r.get::<_,String>(2)?})))?.collect::<Result<Vec<_>,_>>()?;
    let issue: Option<String> = c
        .query_row(
            "SELECT code FROM source_runtime_errors WHERE connector_id=?",
            [&l.connector],
            |r| r.get(0),
        )
        .optional()?;
    Ok(
        json!({"connectorId":l.connector,"grantGeneration":l.generation,"status":state,"jobId":format!("job:{}:{}",l.connector,l.epoch),"discovered":discovered,"processed":discovered-pending,"parsed":parsed,"unparsed":unparsed,"failed":failed,"pending":pending,"scanComplete":scan==0,"files":files,"links":links,"error":issue}),
    )
}
fn receipts(c: &Connection, request: &str, payload: &str) -> R<Option<Value>> {
    let old: Option<(String, String)> = c
        .query_row(
            "SELECT payload,result FROM source_api_requests WHERE id=?",
            [request],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .optional()?;
    if let Some((p, r)) = old {
        if p != payload {
            return Err(error("idempotency_conflict"));
        }
        return serde_json::from_str(&r)
            .map(Some)
            .map_err(|_| error("receipt_corrupt"));
    }
    Ok(None)
}
pub fn dispatch(command: &str, r: Request, fixture: &str) -> R<Value> {
    if r.version != 1 || !COMMANDS.contains(&command) {
        return Err(error("source_contract_rejected"));
    }
    let p = &r.payload;
    match command {
        "connect_source_directory" => fields(p, &["requestId"])?,
        "control_source_job" => fields(
            p,
            &["requestId", "connectorId", "expectedGeneration", "action"],
        )?,
        "get_source_status" => fields(p, &["connectorId"])?,
        "authorize_source_target" => fields(
            p,
            &[
                "requestId",
                "connectorId",
                "expectedGeneration",
                "linkId",
                "decision",
            ],
        )?,
        "get_source_evidence" => match p["mode"].as_str() {
            Some("detail") => fields(
                p,
                &[
                    "mode",
                    "connectorId",
                    "sourceRef",
                    "expectedVersion",
                    "cursor",
                ],
            )?,
            Some("search") => fields(p, &["mode", "connectorId", "query", "expectedGeneration"])?,
            _ => return Err(error("dto_rejected")),
        },
        _ => unreachable!(),
    }
    if crate::runtime_root::is_real() {
        if command == "authorize_source_target" {
            return Err(error("external_targets_disabled"));
        }
        if command == "connect_source_directory" {
            id(p, "requestId")?;
            crate::runtime_root::activate_from_user_click()?;
        }
    }
    let mut c = repository::open(fixture)?;
    source_store::init(&c)?;
    if !crate::runtime_root::is_real(){c.execute_batch("CREATE TABLE IF NOT EXISTS source_api_requests(id TEXT PRIMARY KEY,payload TEXT NOT NULL,result TEXT NOT NULL);CREATE TABLE IF NOT EXISTS source_runtime_errors(connector_id TEXT PRIMARY KEY,code TEXT NOT NULL);")?;}else{c.prepare("SELECT id,payload,result FROM source_api_requests LIMIT 0")?;c.prepare("SELECT connector_id,code FROM source_runtime_errors LIMIT 0")?;}
    if crate::runtime_root::is_real() && command == "connect_source_directory" {
        if let Ok(l) = lease(&c, "directory") {
            if readable(&c, &l).is_ok() {
                let state: String = c.query_row(
                    "SELECT state FROM connectors WHERE id='directory'",
                    [],
                    |r| r.get(0),
                )?;
                if state == "active" {
                    run(fixture);
                }
                return Ok(
                    json!({"connectorId":"directory","grantGeneration":l.generation,"status":state,"jobId":format!("job:directory:{}",l.epoch)}),
                );
            }
        }
    }
    if matches!(
        command,
        "connect_source_directory" | "control_source_job" | "authorize_source_target"
    ) {
        return mutate(&mut c, command, p, fixture);
    }
    let result = match command {
        "get_source_status" => {
            let ids = if let Some(s) = p.get("connectorId") {
                let s = s
                    .as_str()
                    .filter(|s| source_store::valid_id(s))
                    .ok_or_else(|| error("identity_rejected"))?;
                vec![s.to_string()]
            } else {
                let mut q=c.prepare("SELECT id FROM connectors WHERE state!='disconnected' AND id='directory' ORDER BY id")?;
                let rows = q
                    .query_map([], |r| r.get::<_, String>(0))?
                    .collect::<Result<Vec<_>, _>>()?;
                rows
            };
            let mut out = vec![];
            for s in ids {
                out.push(summary(&c, &lease(&c, &s)?)?)
            }
            json!({"connectors":out})
        }
        "get_source_evidence" => {
            let l = lease(&c, id(p, "connectorId")?)?;
            readable(&c, &l)?;
            if p["mode"] == "search" {
                if l.generation != num(p, "expectedGeneration")? {
                    return Err(error("stale_generation"));
                }
                let query = p["query"].as_str().ok_or_else(|| error("query_rejected"))?;
                let rows = source_store::search(&c, &l, query)?;
                json!({"results":rows})
            } else {
                let f = id(p, "sourceRef")?;
                let v = num(p, "expectedVersion")?;
                let mut result = if let Some(cursor) = p.get("cursor") {
                    source_store::consume_cursor(
                        &c,
                        &l,
                        f,
                        v,
                        cursor
                            .as_str()
                            .filter(|s| source_store::valid_id(s))
                            .ok_or_else(|| error("cursor_rejected"))?,
                    )?
                } else {
                    source_store::evidence(&c, &l, f, v, 0)?
                };
                let offset = if let Some(cursor) = p["cursor"].as_str() {
                    c.query_row(
                        "SELECT offset FROM source_cursors WHERE id=?",
                        [cursor],
                        |r| r.get::<_, i64>(0),
                    )?
                } else {
                    0
                };
                let count: i64 = c.query_row(
                    "SELECT count(*) FROM source_segments WHERE file_id=?1 AND version=?2",
                    params![f, v],
                    |r| r.get(0),
                )?;
                if result["status"] == "available" && offset + 50 < count {
                    let token = format!(
                        "cursor:{}",
                        hex(&format!(
                            "{}:{f}:{v}:{}:{}:{}",
                            l.connector,
                            l.epoch,
                            l.generation,
                            offset + 50
                        ))
                    );
                    c.execute(
                        "INSERT OR IGNORE INTO source_cursors VALUES(?1,?2,?3,?4,?5,?6)",
                        params![token, l.connector, f, v, l.generation, offset + 50],
                    )?;
                    c.execute(
                        "INSERT OR IGNORE INTO source_cursor_epochs VALUES(?1,?2)",
                        params![token, l.epoch],
                    )?;
                    result["nextCursor"] = json!(token);
                }
                result["sourceIdentity"] = json!({"sourceRef":f,"connectorId":l.connector});
                result["version"] = json!(v);
                let(title,identity,reason,mime):(String,String,Option<String>,String)=c.query_row("SELECT f.external_ref,f.identity,f.reason,a.mime FROM source_files f JOIN source_artifacts a ON a.opaque_ref=f.artifact_ref WHERE f.id=?",[f],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?)))?;
                let observed=c.query_row("SELECT json_extract(body,'$.observedAt') FROM records WHERE json_extract(body,'$.sourceFile')=? ORDER BY json_extract(body,'$.version') DESC LIMIT 1",[f],|r|r.get::<_,i64>(0)).optional()?.or_else(||serde_json::from_str::<Value>(&identity).ok().and_then(|i|i["modified"].as_i64().map(|n|n.saturating_mul(1000))));
                result["title"] = json!(title);
                result["mimeType"] = json!(mime);
                result["reason"] = json!(reason);
                result["observedAt"] = json!(observed);
                result
            }
        }
        _ => unreachable!(),
    };
    Ok(result)
}
pub fn hex(s: &str) -> String {
    format!("{:x}", Sha256::digest(s.as_bytes()))
}
fn mutate(c: &mut Connection, command: &str, p: &Value, fixture: &str) -> R<Value> {
    let request = id(p, "requestId")?;
    let signature = json!([command, p]).to_string();
    let tx = c.transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)?;
    if let Some(reply) = receipts(&tx, request, &signature)? {
        return Ok(reply);
    }
    let mut schedule = false;
    let mut target = None;
    let result = match command {
        "connect_source_directory" => {
            let directory = crate::runtime_root::source_path();
            let identity =
                crate::source_file::FileGrant::for_source(&directory)?.root_identity()?;
            let old: Option<(i64, i64, String)> = tx
                .query_row(
                    "SELECT grant_generation,epoch,state FROM connectors WHERE id='directory'",
                    [],
                    |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
                )
                .optional()?;
            let (g, e) = match old {
                Some((g, e, s))
                    if s == "disconnected" && g < 9007199254740991 && e < 9007199254740991 =>
                {
                    (g + 1, e + 1)
                }
                Some(_) => return Err(error("connector_state_rejected")),
                None => (1, 1),
            };
            tx.execute("INSERT INTO connectors VALUES('directory',?1,?2,'active','app-source') ON CONFLICT(id) DO UPDATE SET grant_generation=?1,epoch=?2,state='active'",params![g,e])?;
            tx.execute("INSERT INTO sources VALUES('directory',?1) ON CONFLICT(id) DO UPDATE SET body=?1",[json!({"id":"directory","sourceType":"local_file","authorized":true,"generation":g}).to_string()])?;
            tx.execute("INSERT INTO connector_grants VALUES('root:directory','directory',?1,?2,'active') ON CONFLICT(id) DO UPDATE SET target_ref=?1,generation=?2,state='active'",params![json!([identity.dev,identity.ino]).to_string(),g])?;
            tx.execute(
                "INSERT INTO scan_entries VALUES(?1,'directory','',0,?2,'pending')",
                params![format!("scan:directory:{e}"), e],
            )?;
            schedule = true;
            json!({"connectorId":"directory","grantGeneration":g,"jobId":format!("job:directory:{e}"),"status":"active"})
        }
        "control_source_job" => {
            let l = lease(&tx, id(p, "connectorId")?)?;
            if l.connector != "directory"
                || l.generation != num(p, "expectedGeneration")?
                || l.generation >= 9007199254740991
                || l.epoch >= 9007199254740991
            {
                return Err(error("stale_generation"));
            }
            readable(&tx, &l)?;
            let action = p["action"]
                .as_str()
                .filter(|s| matches!(*s, "pause" | "resume" | "cancel" | "disconnect" | "refresh"))
                .ok_or_else(|| error("dto_rejected"))?;
            let old: String = tx.query_row(
                "SELECT state FROM connectors WHERE id='directory'",
                [],
                |r| r.get(0),
            )?;
            if action == "resume" && old != "paused" {
                return Err(error("connector_state_rejected"));
            }
            let state = match action {
                "pause" => "paused",
                "cancel" => "cancelled",
                "disconnect" => "disconnected",
                _ => "active",
            };
            let e = l.epoch + 1;
            let g = l.generation + i64::from(action == "disconnect");
            tx.execute(
                "UPDATE connectors SET epoch=?1,grant_generation=?2,state=?3 WHERE id='directory'",
                params![e, g, state],
            )?;
            if action == "refresh" {
                tx.execute(
                    "DELETE FROM source_runtime_errors WHERE connector_id='directory'",
                    [],
                )?;
                tx.execute(
                    "INSERT INTO scan_entries VALUES(?1,'directory','',0,?2,'pending')",
                    params![format!("scan:directory:{e}"), e],
                )?;
            } else {
                tx.execute("UPDATE scan_entries SET scan_epoch=?1 WHERE connector_id='directory' AND scan_epoch=?2",params![e,l.epoch])?;
                tx.execute(
                    "UPDATE import_jobs SET epoch=?1 WHERE connector_id='directory' AND epoch=?2",
                    params![e, l.epoch],
                )?;
            }
            if action == "disconnect" {
                tx.execute("UPDATE sources SET body=json_set(body,'$.authorized',json('false'),'$.generation',json_extract(body,'$.generation')+1) WHERE id='directory' OR id IN(SELECT id FROM connectors WHERE root_ref LIKE 'link:%')",[])?;
                tx.execute(
                    "UPDATE connector_grants SET state='revoked',generation=generation+1",
                    [],
                )?;
                tx.execute("UPDATE source_files SET parse_state='revoked'", [])?;
                let mut q = tx.prepare(
                    "SELECT id FROM records WHERE json_extract(body,'$.sourceFile') IS NOT NULL",
                )?;
                let ids = q
                    .query_map([], |r| r.get::<_, String>(0))?
                    .collect::<Result<Vec<_>, _>>()?;
                drop(q);
                for rid in ids {
                    source_store::invalidate(&tx, &rid)?;
                    tx.execute(
                        "UPDATE records SET body=json_set(body,'$.status','revoked') WHERE id=?",
                        [rid],
                    )?;
                }
            }
            schedule = matches!(action, "resume" | "refresh");
            json!({"connectorId":"directory","grantGeneration":g,"jobId":format!("job:directory:{e}"),"status":state})
        }
        "authorize_source_target" => {
            target = Some(id(p, "linkId")?.to_string());
            crate::source_targets::grant(&tx, p)?
        }
        _ => unreachable!(),
    };
    tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1", [])?;
    tx.execute(
        "INSERT INTO source_api_requests VALUES(?1,?2,?3)",
        params![request, signature, result.to_string()],
    )?;
    tx.commit()?;
    if schedule {
        run(fixture)
    }
    if let Some(link) = target {
        if p["decision"] == "grant" {
            crate::source_targets::run(fixture, &link, result["grantGeneration"].as_i64().unwrap())
        }
    }
    Ok(result)
}

pub fn resume(fixture: &str) -> R<()> {
    if crate::runtime_root::is_real(){return Ok(())}
    let c = repository::open(fixture)?;
    source_store::init(&c)?;
    if !crate::runtime_root::is_real(){c.execute_batch("CREATE TABLE IF NOT EXISTS source_runtime_errors(connector_id TEXT PRIMARY KEY,code TEXT NOT NULL)")?;}else{c.prepare("SELECT connector_id,code FROM source_runtime_errors LIMIT 0")?;}
    if let Ok(l) = lease(&c, "directory") {
        if source_store::check(&c, &l).is_ok() {
            run(fixture)
        }
    }
    if crate::runtime_root::is_real() {
        return Ok(());
    }
    let mut q = c.prepare("SELECT sl.id,tc.grant_generation FROM source_links sl JOIN connectors tc ON tc.id=sl.grant_id WHERE sl.state='fetch_pending'")?;
    for row in q.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?)))? {
        let (link, g) = row?;
        crate::source_targets::run(fixture, &link, g)
    }
    Ok(())
}
