//! Controlled SQLite repository adapter. No model, network or credentials linkage.
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::os::unix::fs::{MetadataExt, PermissionsExt};
use std::{
    fs,
    path::PathBuf,
    time::{SystemTime, UNIX_EPOCH},
};
const TABLES: &[&str] = &[
    "records",
    "memories",
    "states",
    "drafts",
    "questions",
    "packets",
    "derivations",
    "feedback",
    "sources",
];
#[derive(Debug, Serialize)]
pub struct Error {
    pub code: String,
}
impl Error {
    pub fn new(s: &str) -> Self {
        Self { code: s.into() }
    }
}
type R<T> = Result<T, Error>;
impl From<rusqlite::Error> for Error {
    fn from(_: rusqlite::Error) -> Self {
        Self::new("database_unavailable")
    }
}
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub version: u8,
    pub operation: String,
    #[serde(default)]
    pub payload: Value,
}
fn reject<T>(s: &str) -> R<T> {
    Err(Error::new(s))
}
fn time() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64
}
fn text<'a>(v: &'a Value, k: &str) -> R<&'a str> {
    v[k].as_str()
        .filter(|s| !s.is_empty() && s.len() < 8192)
        .ok_or_else(|| Error::new("dto_rejected"))
}
fn number(v: &Value, k: &str) -> R<i64> {
    v[k].as_i64()
        .filter(|n| *n >= 0)
        .ok_or_else(|| Error::new("dto_rejected"))
}
fn id(v: &Value, k: &str) -> R<String> {
    let s = text(v, k)?;
    if s.len() > 120
        || !s
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"-_:".contains(&b))
    {
        return reject("identity_rejected");
    }
    Ok(s.into())
}
fn fields(v: &Value, allowed: &[&str]) -> R<()> {
    if !v.is_object()
        || v.as_object()
            .unwrap()
            .keys()
            .any(|k| !allowed.contains(&k.as_str()))
    {
        return reject("unknown_field");
    }
    Ok(())
}
fn body(s: &str) -> R<()> {
    if s.trim().is_empty() || s.chars().count() > 200 {
        return reject("text_rejected");
    }
    Ok(())
}
pub fn open(fixture: &str) -> R<Connection> {
    if fixture.is_empty()
        || fixture.len() > 60
        || !fixture
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || c == b'-')
    {
        return reject("fixture_rejected");
    }
    let root = crate::runtime_root::verify()?;
    let path = root.join(format!("{fixture}.sqlite"));
    for suffix in ["", "-wal", "-shm", "-journal"] {
        let p = PathBuf::from(format!("{}{suffix}", path.display()));
        match fs::symlink_metadata(p) {
            Ok(m) if !m.is_file() || m.file_type().is_symlink() => {
                return reject("database_path_rejected")
            }
            Err(e) if e.kind() != std::io::ErrorKind::NotFound => {
                return reject("database_path_rejected")
            }
            _ => (),
        }
    }
    let c = Connection::open(&path)?;
    fs::set_permissions(&path, fs::Permissions::from_mode(0o600))
        .map_err(|_| Error::new("permissions_failed"))?;
    c.execute_batch("PRAGMA foreign_keys=ON; CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL); INSERT OR IGNORE INTO meta VALUES(1,0); CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,operation TEXT NOT NULL,payload TEXT NOT NULL,result TEXT NOT NULL); CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,event TEXT NOT NULL,ref TEXT NOT NULL,at INTEGER NOT NULL);")?;
    for t in TABLES {
        c.execute_batch(&format!("CREATE TABLE IF NOT EXISTS {t}(id TEXT PRIMARY KEY,body TEXT NOT NULL CHECK(json_valid(body)));"))?;
    }
    c.execute_batch("CREATE UNIQUE INDEX IF NOT EXISTS source_version ON records(json_extract(body,'$.sourceId'),json_extract(body,'$.externalId'),json_extract(body,'$.version')); CREATE UNIQUE INDEX IF NOT EXISTS turn_identity ON records(json_extract(body,'$.conversationId'),json_extract(body,'$.turnId')) WHERE json_extract(body,'$.conversationId') IS NOT NULL;")?;
    for (source, kind) in [
        ("conversation", "conversation"),
        ("obsidian-demo", "synthetic_markdown"),
        ("health-demo", "synthetic_health"),
    ] {
        c.execute(
            "INSERT OR IGNORE INTO sources VALUES(?1,?2)",
            params![
                source,
                json!({"id":source,"sourceType":kind,"authorized":true,"generation":1}).to_string()
            ],
        )?;
    }
    Ok(c)
}
fn get(c: &Connection, t: &str, key: &str) -> R<Option<Value>> {
    let raw: Option<String> = c
        .query_row(&format!("SELECT body FROM {t} WHERE id=?1"), [key], |r| {
            r.get(0)
        })
        .optional()?;
    raw.map(|s| serde_json::from_str(&s).map_err(|_| Error::new("corrupt_record")))
        .transpose()
}
fn list(c: &Connection, t: &str) -> R<Vec<Value>> {
    let mut q = c.prepare(&format!("SELECT body FROM {t} ORDER BY id"))?;
    let rows = q.query_map([], |r| r.get::<_, String>(0))?;
    rows.map(|s| serde_json::from_str(&s?).map_err(|_| Error::new("corrupt_record")))
        .collect()
}
fn put(c: &Connection, t: &str, key: &str, v: &Value) -> R<()> {
    c.execute(&format!("INSERT INTO {t}(id,body) VALUES(?1,?2) ON CONFLICT(id) DO UPDATE SET body=excluded.body"),params![key,v.to_string()])?;
    Ok(())
}
fn revision(c: &Connection) -> R<i64> {
    Ok(c.query_row("SELECT revision FROM meta WHERE id=1", [], |r| r.get(0))?)
}
fn snapshot(c: &Connection) -> R<Value> {
    let mut v = json!({"revision":revision(c)?,"now":time(),"boundary":{"network":0,"credentials":0,"provider":0},"profile":"synthetic"});
    for t in TABLES {
        if *t == "records" {
            let mut q = c.prepare(
                "SELECT body FROM records WHERE json_extract(body,'$.sourceFile') IS NULL",
            )?;
            let rows = q
                .query_map([], |r| r.get::<_, String>(0))?
                .collect::<Result<Vec<_>, _>>()?;
            v[*t] = json!(rows
                .iter()
                .map(|s| serde_json::from_str::<Value>(s).map_err(|_| Error::new("store_corrupt")))
                .collect::<R<Vec<_>>>()?);
        } else {
            v[*t] = json!(list(c, t)?)
        }
    }
    Ok(v)
}
fn active(c: &Connection, r: &Value, now: i64) -> R<bool> {
    let s = get(c, "sources", text(r, "sourceId")?)?.ok_or_else(|| Error::new("source_missing"))?;
    if r.get("sourceFile").is_some() {
        let l = crate::source_api::lease(c, text(r, "sourceId")?)?;
        if crate::source_store::check(c, &l).is_err() {
            return Ok(false);
        }
    }
    Ok(s["authorized"] == true
        && r["status"] == "active"
        && (r["validUntil"].is_null() || r["validUntil"].as_i64().is_some_and(|e| e > now)))
}
// Recompute feedback scope from stored targets and source authority, never packet claims.
fn relevant_feedback(c: &Connection, refs: &[Value], now: i64) -> R<Vec<Value>> {
    let mut result = vec![];
    for f in list(c, "feedback")? {
        let Some(d) = get(c, "derivations", text(&f, "targetId")?)? else {
            continue;
        };
        if d["status"] != f["decision"] && !(f["decision"] == "correct" && d["status"] == "stale") {
            continue;
        }
        let Some(basis) = d["inputRefs"].as_array().filter(|v| !v.is_empty()) else {
            continue;
        };
        let mut valid = true;
        for r in basis {
            let Some(raw) = get(c, "records", text(r, "id")?)? else {
                valid = false;
                break;
            };
            let source = get(c, "sources", text(&raw, "sourceId")?)?.unwrap();
            if !active(c, &raw, now)?
                || raw["version"] != r["version"]
                || source["generation"] != r["authorizationGeneration"]
                || !refs.iter().any(|v| {
                    v["id"] == r["id"]
                        && v["version"] == r["version"]
                        && v["authorizationGeneration"] == r["authorizationGeneration"]
                })
            {
                valid = false;
                break;
            }
        }
        if valid {
            result.push(json!({"targetId":f["targetId"],"decision":f["decision"]}));
        }
    }
    Ok(result)
}
// Bounded synthetic grammar, used to verify the existing correction DTO without adding fields.
fn quantity(
    s: &str,
    keys: &[&str],
    units: &[&str],
    max_digits: usize,
    decimal: bool,
) -> Option<f64> {
    let lower = s.to_lowercase();
    for key in keys {
        for (start, _) in lower.match_indices(key) {
            let rest = &lower[start + key.len()..];
            let mut skipped = 0;
            let mut offset = 0;
            for ch in rest.chars() {
                if ch.is_ascii_digit() {
                    break;
                }
                skipped += 1;
                offset += ch.len_utf8();
            }
            if skipped > 5 || offset == rest.len() {
                continue;
            }
            let tail = &rest[offset..];
            let integer_len = tail.bytes().take_while(|b| b.is_ascii_digit()).count();
            if integer_len == 0 || integer_len > max_digits {
                continue;
            }
            let mut end = integer_len;
            if decimal && tail[end..].starts_with('.') {
                let fraction = tail[end + 1..]
                    .bytes()
                    .take_while(|b| b.is_ascii_digit())
                    .count();
                if fraction == 0 {
                    continue;
                }
                end += fraction + 1;
            }
            if units
                .iter()
                .any(|u| tail[end..].trim_start().starts_with(u))
            {
                if let Ok(n) = tail[..end].parse::<f64>() {
                    return Some(n);
                }
            }
        }
    }
    None
}
fn correction_state(s: &str, domain: &str) -> Option<(&'static str, &'static str, Value)> {
    if let Some(n) = quantity(s, &["时间", "有空", "time"], &["分钟", "min"], 3, false) {
        return Some(("available_time", "work", json!(n as i64)));
    }
    if let Some(n) = quantity(s, &["睡眠", "睡了", "sleep"], &["小时", "h"], 2, true) {
        return Some(("sleep_hours", "health", json!(n)));
    }
    if domain == "work" {
        return Some(("work_load", "work", json!(s)));
    }
    None
}
fn invalidate(c: &Connection, rid: &str) -> R<()> {
    for t in ["memories", "states", "packets", "derivations"] {
        for mut v in list(c, t)? {
            if v["rawId"] == rid
                || v["inputRefs"]
                    .as_array()
                    .is_some_and(|a| a.iter().any(|x| x["id"] == rid || x.as_str() == Some(rid)))
            {
                v["status"] = json!("stale");
                put(c, t, &v["id"].as_str().unwrap().to_owned(), &v)?
            }
        }
    }
    Ok(())
}
fn txn(
    c: &mut Connection,
    op: &str,
    p: &Value,
    apply: impl FnOnce(&Connection) -> R<Value>,
) -> R<Value> {
    let key = id(p, "requestId")?;
    let payload = p.to_string();
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    let prior: Option<(String, String, String)> = tx
        .query_row(
            "SELECT operation,payload,result FROM requests WHERE id=?1",
            [&key],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .optional()?;
    if let Some((oldop, old, reply)) = prior {
        if oldop != op || old != payload {
            return reject("idempotency_conflict");
        }
        return serde_json::from_str(&reply).map_err(|_| Error::new("receipt_corrupt"));
    }
    let result = apply(&tx)?;
    tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1", [])?;
    tx.execute(
        "INSERT INTO audit(event,ref,at) VALUES(?1,?2,?3)",
        params![op, key, time()],
    )?;
    tx.execute(
        "INSERT INTO requests VALUES(?1,?2,?3,?4)",
        params![key, op, payload, result.to_string()],
    )?;
    tx.commit()?;
    Ok(result)
}
fn supersede_state(c: &Connection, key: &str, domain: &str, new_id: &str) -> R<()> {
    for state in list(c, "states")? {
        if state["stateKey"] == key && state["domain"] == domain && state["status"] == "active" {
            let rawid = text(&state, "rawId")?;
            if let Some(mut raw) = get(c, "records", rawid)? {
                raw["status"] = json!("superseded");
                raw["supersededBy"] = json!(new_id);
                put(c, "records", rawid, &raw)?;
            }
            invalidate(c, rawid)?;
        }
    }
    Ok(())
}
fn save(c: &Connection, p: &Value) -> R<Value> {
    fields(
        p,
        &[
            "requestId",
            "conversationId",
            "turnId",
            "text",
            "intent",
            "observedAt",
            "validUntil",
            "questionId",
            "statement",
            "scope",
            "confirmation",
            "draftId",
            "stateKey",
            "stateValue",
            "domain",
        ],
    )?;
    let rid = format!("raw:{}", id(p, "requestId")?);
    let s = text(p, "text")?;
    body(s)?;
    let intent = text(p, "intent")?;
    if !["record", "answer", "remember"].contains(&intent) {
        return reject("intent_rejected");
    }
    if intent != "remember" && (!p["confirmation"].is_null() || !p["statement"].is_null()) {
        return reject("confirmation_rejected");
    }
    let source = get(c, "sources", "conversation")?.unwrap();
    if source["authorized"] != true {
        return reject("authorization_rejected");
    }
    let observed = number(p, "observedAt")?;
    if observed > time() + 60000 {
        return reject("observation_time_rejected");
    }
    let domain = text(p, "domain")?;
    if !["work", "health", "person"].contains(&domain) {
        return reject("domain_rejected");
    }
    if intent == "remember"
        && (p["confirmation"] != "remember_this_statement"
            || text(p, "statement")? != s
            || p["scope"] != "person")
    {
        return reject("confirmation_rejected");
    }
    if intent == "remember"
        && list(c, "memories")?
            .iter()
            .any(|m| m["status"] == "active" && m["confirmed"] == true)
    {
        return reject("durable_memory_limit_rejected");
    }
    if intent != "remember"
        && p["stateKey"].is_string()
        && p["validUntil"].as_i64().is_none_or(|x| x <= observed)
    {
        return reject("validity_rejected");
    }
    if intent != "remember"
        && list(c, "records")?
            .iter()
            .filter(|r| {
                r["sourceId"] == "conversation"
                    && r["domain"] == domain
                    && r["status"] == "active"
                    && r["intent"] != "remember"
            })
            .count()
            >= 3
    {
        return reject("context_item_limit_rejected");
    };
    let raw = json!({"id":rid,"sourceId":"conversation","externalId":id(p,"turnId")?,"conversationId":id(p,"conversationId")?,"turnId":id(p,"turnId")?,"version":1,"text":s,"contentHash":format!("{:x}",Sha256::digest(s.as_bytes())),"observedAt":observed,"ingestedAt":time(),"validUntil":p["validUntil"],"authorizationGeneration":source["generation"],"status":"active","domain":domain,"intent":intent});
    put(c, "records", &rid, &raw)?;
    if intent == "remember" {
        put(
            c,
            "memories",
            &rid,
            &json!({"id":rid,"rawId":rid,"statement":s,"confirmed":true,"status":"active","generation":1,"scope":"person","domain":domain,"observedAt":observed}),
        )?;
    } else if p["stateKey"].is_string() {
        let key = text(p, "stateKey")?;
        if key == "available_time"
            && p["stateValue"]
                .as_i64()
                .is_none_or(|v| !(1..=1440).contains(&v))
        {
            return reject("state_value_rejected");
        };
        if key == "sleep_hours"
            && p["stateValue"]
                .as_f64()
                .is_none_or(|v| !(0.0..=24.0).contains(&v))
        {
            return reject("state_value_rejected");
        };
        if !["available_time", "sleep_hours", "work_load"].contains(&key) {
            return reject("state_key_rejected");
        }
        supersede_state(c, text(p, "stateKey")?, text(p, "domain")?, &rid)?;
        put(
            c,
            "states",
            &rid,
            &json!({"id":rid,"rawId":rid,"stateKey":key,"value":p["stateValue"],"domain":domain,"validUntil":p["validUntil"],"observedAt":observed,"generation":1,"status":"active"}),
        )?;
    }
    if intent == "answer" {
        let qid = id(p, "questionId")?;
        let mut q = get(c, "questions", &qid)?.ok_or_else(|| Error::new("question_missing"))?;
        if q["status"] != "pending" {
            return reject("question_stale");
        }
        q["status"] = json!("answered");
        q["answerRef"] = json!(rid);
        q["generation"] = json!(q["generation"].as_i64().unwrap() + 1);
        put(c, "questions", &qid, &q)?;
    }
    if let Some(d) = p["draftId"].as_str() {
        let mut draft = get(c, "drafts", d)?.ok_or_else(|| Error::new("draft_missing"))?;
        if draft["text"] != s {
            return reject("draft_conflict");
        }
        draft["status"] = json!("committed");
        draft["resultRef"] = json!(rid);
        put(c, "drafts", d, &draft)?;
    }
    Ok(json!({"status":"stored","id":rid}))
}
fn ingest(c: &Connection, p: &Value) -> R<Value> {
    fields(
        p,
        &[
            "requestId",
            "item",
            "authorizationRef",
            "observedAt",
            "validUntil",
            "noExpiryReason",
            "domain",
            "stateKey",
            "stateValue",
        ],
    )?;
    let item = &p["item"];
    fields(
        item,
        &[
            "sourceId",
            "externalId",
            "sourceType",
            "version",
            "content",
            "mimeType",
            "title",
            "createdAt",
            "updatedAt",
            "parentRef",
            "metadata",
        ],
    )?;
    let sid = id(item, "sourceId")?;
    if !["obsidian-demo", "health-demo"].contains(&sid.as_str())
        || p["authorizationRef"] != format!("local:{sid}")
    {
        return reject("authorization_rejected");
    }
    let src = get(c, "sources", &sid)?.unwrap();
    if src["authorized"] != true || item["sourceType"] != src["sourceType"] {
        return reject("authorization_rejected");
    }
    let ext = id(item, "externalId")?;
    let ver = number(item, "version")?;
    if ver < 1 {
        return reject("version_rejected");
    };
    let content = text(item, "content")?;
    body(content)?;
    let expected = if sid == "obsidian-demo" {
        "text/markdown"
    } else {
        "application/json"
    };
    if item["mimeType"] != expected {
        return reject("mime_rejected");
    }
    let observed = number(p, "observedAt")?;
    if observed > time() + 60000 {
        return reject("observation_time_rejected");
    }
    if sid == "health-demo" && p["validUntil"].as_i64().is_none_or(|v| v <= observed) {
        return reject("validity_rejected");
    }
    let rid = format!("source:{sid}:{ext}:{ver}");
    if list(c, "records")?.iter().any(|old| {
        old["sourceId"] == sid
            && old["externalId"] == ext
            && old["version"].as_i64().unwrap_or(0) > ver
    }) {
        return reject("source_version_stale");
    }
    if sid == "health-demo" {
        let h: Value =
            serde_json::from_str(content).map_err(|_| Error::new("health_payload_rejected"))?;
        fields(&h, &["sleepHours", "start", "end", "unit"])?;
        if h["unit"] != "hours"
            || h["sleepHours"]
                .as_f64()
                .is_none_or(|n| !(0.0..=24.0).contains(&n))
            || number(&h, "end")? <= number(&h, "start")?
            || h["end"] != observed
            || p["stateKey"] != "sleep_hours"
            || p["stateValue"] != h["sleepHours"]
            || p["domain"] != "health"
        {
            return reject("health_payload_rejected");
        }
    } else if p["domain"] != "work" {
        return reject("source_projection_rejected");
    } else if !p["stateKey"].is_null() {
        let n = content
            .split(|c: char| !c.is_ascii_digit())
            .find(|s| !s.is_empty())
            .and_then(|s| s.parse::<i64>().ok());
        if p["stateKey"] != "available_time"
            || !content.contains("时间")
            || !content.contains("分钟")
            || n.is_none()
            || p["stateValue"].as_i64() != n
            || p["validUntil"].as_i64().is_none_or(|v| v <= observed)
        {
            return reject("source_projection_rejected");
        }
    }

    for mut old in list(c, "records")? {
        if old["sourceId"] == sid && old["externalId"] == ext {
            let ov = old["version"].as_i64().unwrap();
            if ov == ver {
                if old["text"] == content && old["sourceMetadata"] == *item {
                    return Ok(json!({"status":"duplicate","id":old["id"]}));
                }
                return reject("source_version_conflict");
            };
            if ov > ver {
                return reject("source_version_stale");
            }
            if old["status"] == "active" {
                let oldid = text(&old, "id")?.to_owned();
                old["status"] = json!("superseded");
                old["supersededBy"] = json!(rid);
                put(c, "records", &oldid, &old)?;
                invalidate(c, &oldid)?
            }
        }
    }
    let raw = json!({"id":rid,"sourceId":sid,"externalId":ext,"version":ver,"text":content,"contentHash":format!("{:x}",Sha256::digest(content.as_bytes())),"sourceMetadata":item,"observedAt":observed,"ingestedAt":time(),"validUntil":p["validUntil"],"authorizationGeneration":src["generation"],"status":"active","domain":p["domain"],"intent":"source"});
    put(c, "records", &rid, &raw)?;
    if !p["stateKey"].is_null() {
        supersede_state(c, text(p, "stateKey")?, text(p, "domain")?, &rid)?;
        put(
            c,
            "states",
            &rid,
            &json!({"id":rid,"rawId":rid,"stateKey":p["stateKey"],"value":p["stateValue"],"domain":p["domain"],"validUntil":p["validUntil"],"observedAt":observed,"generation":ver,"status":"active"}),
        )?;
    }
    Ok(json!({"status":"imported","id":rid}))
}
pub fn dispatch(ipc: &str, req: Request, fixture: &str) -> R<Value> {
    // Hard-deny before opening any database or touching settings. No live implementation linked.
    if [
        "save_ai_provider_credential",
        "test_ai_provider_connection",
        "set_ai_provider_enabled",
    ]
    .contains(&ipc)
    {
        return reject("offline_capability_denied");
    }
    if req.operation == "confirm_send" || req.version != 2 {
        return reject("offline_contract_rejected");
    }
    let allowed = match ipc {
        "capture_record" => vec!["save", "ingest", "draft"],
        "update_current_state" | "upsert_durable_memory" => vec!["correct"],
        "get_today" | "get_evidence_backed_understanding" | "runtime_status" => vec!["snapshot"],
        "assemble_global_ai_context" => vec!["local_prepare", "surface_question"],
        "get_context_disclosure_receipt" => vec!["snapshot", "source_revoke"],
        "resolve_request_context" => vec!["offline_generate"],
        "decide_understanding_feedback" => vec!["question_decision", "feedback"],
        "get_ai_provider_settings" => vec!["snapshot"],
        "save_ai_provider_settings" => vec!["offline_settings"],
        _ => return reject("unavailable"),
    };
    if !allowed.contains(&req.operation.as_str()) {
        return reject("operation_rejected");
    }
    let mut c = open(fixture)?;
    let p = &req.payload;
    if req.operation == "snapshot" {
        fields(p, &[])?;
        return snapshot(&c);
    }
    if req.operation == "draft" {
        fields(
            p,
            &[
                "draftId",
                "conversationId",
                "turnId",
                "revision",
                "text",
                "requestId",
                "observedAt",
            ],
        )?;
        let did = id(p, "draftId")?;
        let s = p["text"]
            .as_str()
            .ok_or_else(|| Error::new("dto_rejected"))?;
        if s.chars().count() > 200 {
            return reject("text_rejected");
        };
        let rev = number(p, "revision")?;
        if let Some(old) = get(&c, "drafts", &did)? {
            if old["revision"].as_i64().unwrap() > rev {
                return reject("draft_stale");
            }
        }
        let mut v = p.clone();
        v["id"] = json!(did);
        v["status"] = json!("pending");
        put(&c, "drafts", &did, &v)?;
        return Ok(json!({"status":"draft_saved"}));
    }
    txn(&mut c, &req.operation, p, |tx| {
        match req.operation.as_str() {
            "save" => save(tx, p),
            "ingest" => ingest(tx, p),
            "correct" => {
                fields(
                    p,
                    &[
                        "requestId",
                        "id",
                        "text",
                        "expectedGeneration",
                        "observedAt",
                        "validUntil",
                        "confirmation",
                        "stateValue",
                        "draftId",
                    ],
                )?;
                let key = id(p, "id")?;
                let mut old =
                    get(tx, "records", &key)?.ok_or_else(|| Error::new("record_missing"))?;
                if !active(tx, &old, time())?
                    || number(p, "expectedGeneration")? != old["version"].as_i64().unwrap()
                {
                    return reject("stale_generation");
                };
                body(text(p, "text")?)?;
                if old["intent"] == "remember" && p["confirmation"] != "remember_this_statement" {
                    return reject("confirmation_rejected");
                };
                let observed = number(p, "observedAt")?;
                if observed > time() + 60000 {
                    return reject("observation_time_rejected");
                }
                if let Some(state) = get(tx, "states", &key)? {
                    let Some((new_key, domain, value)) =
                        correction_state(text(p, "text")?, text(&old, "domain")?)
                    else {
                        return reject("correction_type_rejected");
                    };
                    if state["stateKey"] != new_key || state["domain"] != domain {
                        return reject("correction_type_rejected");
                    }
                    let same_value = value == p["stateValue"]
                        || (value.is_number() && value.as_f64() == p["stateValue"].as_f64());
                    if !same_value
                        || (new_key == "available_time"
                            && value.as_i64().is_none_or(|v| !(1..=1440).contains(&v)))
                        || (new_key == "sleep_hours"
                            && value.as_f64().is_none_or(|v| !(0.0..=24.0).contains(&v)))
                    {
                        return reject("state_value_rejected");
                    }
                    if p["validUntil"].as_i64().is_none_or(|v| v <= observed) {
                        return reject("validity_rejected");
                    }
                } else if old["intent"] != "remember"
                    && (!p["stateValue"].is_null() || !p["validUntil"].is_null())
                {
                    return reject("correction_type_rejected");
                }
                let new_id = format!("raw:{}", id(p, "requestId")?);
                let mut new = old.clone();
                new["id"] = json!(new_id);
                new["text"] = p["text"].clone();
                new["contentHash"] =
                    json!(format!("{:x}", Sha256::digest(text(p, "text")?.as_bytes())));
                new["version"] = json!(old["version"].as_i64().unwrap() + 1);
                new["supersedes"] = json!(key);
                new["turnId"] = Value::Null;
                new["conversationId"] = Value::Null;
                new["observedAt"] = json!(number(p, "observedAt")?);
                new["validUntil"] = p["validUntil"].clone();
                old["status"] = json!("corrected");
                old["supersededBy"] = json!(new_id);
                put(tx, "records", &key, &old)?;
                put(tx, "records", &new_id, &new)?;
                for table in ["states", "memories"] {
                    if let Some(mut projection) = get(tx, table, &key)? {
                        projection["id"] = json!(new_id);
                        projection["rawId"] = json!(new_id);
                        projection["statement"] = p["text"].clone();
                        projection["value"] = p["stateValue"].clone();
                        projection["generation"] = new["version"].clone();
                        projection["validUntil"] = p["validUntil"].clone();
                        projection["observedAt"] = p["observedAt"].clone();
                        put(tx, table, &new_id, &projection)?
                    }
                }
                if let Some(did) = p["draftId"].as_str() {
                    let mut draft =
                        get(tx, "drafts", did)?.ok_or_else(|| Error::new("draft_missing"))?;
                    if draft["text"] != p["text"] {
                        return reject("draft_conflict");
                    };
                    draft["status"] = json!("committed");
                    draft["resultRef"] = json!(new_id);
                    put(tx, "drafts", did, &draft)?;
                }
                invalidate(tx, &key)?;
                Ok(json!({"status":"corrected","id":new_id,"supersedes":key}))
            }
            "source_revoke" => {
                fields(p, &["requestId", "sourceId", "expectedGeneration"])?;
                let sid = id(p, "sourceId")?;
                if sid == "conversation" {
                    return reject("source_rejected");
                };
                let mut src =
                    get(tx, "sources", &sid)?.ok_or_else(|| Error::new("source_missing"))?;
                if src["generation"] != p["expectedGeneration"] {
                    return reject("stale_generation");
                };
                src["authorized"] = json!(false);
                src["generation"] = json!(src["generation"].as_i64().unwrap() + 1);
                put(tx, "sources", &sid, &src)?;
                for raw in list(tx, "records")? {
                    if raw["sourceId"] == sid {
                        invalidate(tx, text(&raw, "id")?)?
                    }
                }
                Ok(json!({"status":"revoked"}))
            }
            "surface_question" => {
                fields(p, &["requestId", "question"])?;
                let q = &p["question"];
                fields(
                    q,
                    &[
                        "id",
                        "purpose",
                        "missingField",
                        "context",
                        "window",
                        "text",
                        "basisRefs",
                        "generation",
                        "status",
                    ],
                )?;
                let key = id(q, "id")?;
                if let Some(mut old) = get(tx, "questions", &key)? {
                    if old["status"] == "deferred"
                        && old["resumeAt"].as_i64().is_some_and(|t| t <= time())
                    {
                        old["status"] = json!("pending");
                        old["generation"] = json!(old["generation"].as_i64().unwrap() + 1);
                        put(tx, "questions", &key, &old)?;
                    }
                    return Ok(old);
                };
                if q["status"] != "pending" || q["generation"] != 1 {
                    return reject("question_rejected");
                };
                put(tx, "questions", &key, q)?;
                Ok(q.clone())
            }
            "question_decision" => {
                fields(
                    p,
                    &[
                        "requestId",
                        "questionId",
                        "expectedGeneration",
                        "decision",
                        "resumeAt",
                    ],
                )?;
                let key = id(p, "questionId")?;
                let mut q =
                    get(tx, "questions", &key)?.ok_or_else(|| Error::new("question_missing"))?;
                if q["generation"] != p["expectedGeneration"] || q["status"] != "pending" {
                    return reject("question_stale");
                };
                let d = text(p, "decision")?;
                if !["defer", "ignore", "refuse"].contains(&d) {
                    return reject("decision_rejected");
                };
                if d == "defer" && number(p, "resumeAt")? <= time() {
                    return reject("resume_time_rejected");
                };
                q["status"] = json!(match d {
                    "defer" => "deferred",
                    "ignore" => "ignored",
                    _ => "refused",
                });
                q["resumeAt"] = p["resumeAt"].clone();
                q["generation"] = json!(q["generation"].as_i64().unwrap() + 1);
                put(tx, "questions", &key, &q)?;
                Ok(q)
            }
            "local_prepare" => {
                fields(p, &["requestId", "expectedGeneration", "packet"])?;
                if number(p, "expectedGeneration")? != revision(tx)? {
                    return reject("stale_generation");
                };
                let packet = &p["packet"];
                fields(
                    packet,
                    &[
                        "id",
                        "purpose",
                        "budget",
                        "usedBudget",
                        "topK",
                        "inputRefs",
                        "included",
                        "excluded",
                        "states",
                        "feedback",
                        "createdAt",
                    ],
                )?;
                if !["person", "work", "health"].contains(&text(packet, "purpose")?)
                    || !(1..=8).contains(&number(packet, "topK")?)
                {
                    return reject("packet_rejected");
                }

                let refs = packet["inputRefs"]
                    .as_array()
                    .ok_or_else(|| Error::new("packet_rejected"))?;
                if packet["feedback"] != json!(relevant_feedback(tx, refs, time())?) {
                    return reject("feedback_scope_rejected");
                }
                let budget = number(packet, "budget")?;
                if !(32..=1200).contains(&budget) {
                    return reject("context_budget_rejected");
                };
                let included = packet["included"]
                    .as_array()
                    .ok_or_else(|| Error::new("packet_rejected"))?;
                if included.len() != refs.len() {
                    return reject("packet_rejected");
                }
                let states = packet["states"]
                    .as_array()
                    .ok_or_else(|| Error::new("packet_rejected"))?;
                for state in states {
                    let actual = get(tx, "states", text(state, "id")?)?
                        .ok_or_else(|| Error::new("packet_rejected"))?;
                    if actual != *state || !refs.iter().any(|r| r["id"] == state["rawId"]) {
                        return reject("packet_rejected");
                    }
                }
                let mut cost = 0;
                let mut seen = std::collections::BTreeSet::new();
                for r in refs {
                    let key = text(r, "id")?;
                    if !seen.insert(key) {
                        return reject("duplicate_context_ref");
                    };
                    let raw =
                        get(tx, "records", key)?.ok_or_else(|| Error::new("source_missing"))?;
                    let src = get(tx, "sources", text(&raw, "sourceId")?)?.unwrap();
                    if !active(tx, &raw, time())?
                        || raw["version"] != r["version"]
                        || src["generation"] != r["authorizationGeneration"]
                    {
                        return reject("context_stale");
                    };
                    let row = included
                        .iter()
                        .find(|v| v["id"] == key)
                        .ok_or_else(|| Error::new("packet_rejected"))?;
                    if row["text"] != raw["text"]
                        || row["version"] != raw["version"]
                        || row["domain"] != raw["domain"]
                    {
                        return reject("packet_rejected");
                    }
                    cost += 8 + (text(&raw, "text")?.chars().count() as i64 + 3) / 4;
                }
                if cost > budget || packet["usedBudget"] != cost {
                    return reject("context_budget_rejected");
                };
                let key = id(packet, "id")?;
                let mut v = packet.clone();
                v["status"] = json!("active");
                put(tx, "packets", &key, &v)?;
                Ok(v)
            }
            "offline_generate" => {
                fields(p, &["requestId", "modelId", "contextPacketId", "output"])?;
                if !["OfflineA", "OfflineB"].contains(&text(p, "modelId")?) {
                    return reject("offline_model_rejected");
                };
                let packet = get(tx, "packets", text(p, "contextPacketId")?)?
                    .ok_or_else(|| Error::new("packet_missing"))?;
                if packet["status"] != "active" {
                    return reject("context_stale");
                };
                if packet["feedback"]
                    != json!(relevant_feedback(
                        tx,
                        packet["inputRefs"].as_array().unwrap(),
                        time()
                    )?)
                {
                    return reject("context_stale");
                }
                for r in packet["inputRefs"].as_array().unwrap() {
                    let raw = get(tx, "records", text(r, "id")?)?.unwrap();
                    if !active(tx, &raw, time())? {
                        return reject("context_stale");
                    }
                }
                let key = format!("output:{}", id(p, "requestId")?);
                let v = json!({"id":key,"modelId":p["modelId"],"provider":"offline_fixture","inputRefs":packet["inputRefs"],"body":p["output"],"status":"candidate","createdAt":time(),"confirmed":false});
                put(tx, "derivations", &key, &v)?;
                Ok(v)
            }
            "feedback" => {
                fields(p, &["requestId", "id", "decision"])?;
                let key = id(p, "id")?;
                let mut d = get(tx, "derivations", &key)?
                    .ok_or_else(|| Error::new("derivation_missing"))?;
                let decision = text(p, "decision")?;
                if !["confirm", "reject", "ignore", "correct"].contains(&decision) {
                    return reject("feedback_rejected");
                };
                if d["status"] != "candidate" && decision != "correct" {
                    return reject("feedback_used");
                };
                d["status"] = json!(if decision == "correct" {
                    "stale"
                } else {
                    decision
                });
                put(tx, "derivations", &key, &d)?;
                let fid = id(p, "requestId")?;
                put(
                    tx,
                    "feedback",
                    &fid,
                    &json!({"id":fid,"targetId":key,"decision":decision,"createdAt":time()}),
                )?;
                Ok(d)
            }
            "offline_settings" => {
                fields(p, &["requestId", "modelId"])?;
                if !["OfflineA", "OfflineB"].contains(&text(p, "modelId")?) {
                    return reject("offline_model_rejected");
                };
                put(
                    tx,
                    "drafts",
                    "model-selection",
                    &json!({"id":"model-selection","modelId":p["modelId"],"status":"settings"}),
                )?;
                Ok(json!({"status":"saved"}))
            }
            _ => reject("operation_rejected"),
        }
    })
}
