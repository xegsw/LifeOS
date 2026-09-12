//! Synthetic SourcePort -> transactional application -> existing JSON repositories.
use crate::{
    artifact_io::{Dir, OwnedFile},
    health_ingestion::put,
    repository::{self, Error},
};
use rusqlite::{Connection, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    io::{BufRead, BufReader, Read},
    os::unix::fs::MetadataExt,
    process::{Command, Stdio},
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    time::{Duration, Instant},
};
type R<T> = Result<T, Error>;
const DAY: i64 = 86400000;
fn err(s: &str) -> Error {
    Error::new(s)
}
fn hash(s: &str) -> String {
    format!("{:x}", Sha256::digest(s.as_bytes()))
}
pub fn now() -> i64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as i64
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Row {
    event: String,
    source: String,
    metric: String,
    start_ms: i64,
    end_ms: i64,
    offset: i64,
    value: Option<f64>,
    unit: String,
    category: Option<String>,
    asleep: bool,
}
impl Row {
    fn check(&self) -> R<()> {
        if self.event != "row"
            || self.source.is_empty()
            || self.source.len() > 640
            || !matches!(self.metric.as_str(), "sleep" | "steps" | "exercise")
            || self.start_ms < 0
            || self.end_ms <= self.start_ms
            || self.end_ms - self.start_ms > 7 * DAY
            || self.end_ms > 4102444800000
            || self.offset.abs() > 840
            || self
                .value
                .is_some_and(|v| !v.is_finite() || v < 0.0 || v > 100000000.0)
        {
            return Err(err("health_row_rejected"));
        }
        if self.metric == "sleep" {
            if self.value.is_some() || self.unit != "minutes" {
                return Err(err("health_row_rejected"));
            }
        } else if self.value.is_none()
            || self.unit
                != if self.metric == "steps" {
                    "count"
                } else {
                    "minutes"
                }
        {
            return Err(err("health_row_rejected"));
        }
        Ok(())
    }
    fn days(&self) -> Vec<i64> {
        ((self.start_ms + self.offset * 60000).div_euclid(DAY)
            ..=(self.end_ms - 1 + self.offset * 60000).div_euclid(DAY))
            .collect()
    }
}
pub fn filename(s: &str) -> R<()> {
    if s.is_empty()
        || s.len() > 120
        || !s
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"-_.".contains(&c))
        || s.contains("..")
        || !(s.ends_with(".xml") || s.ends_with(".zip"))
    {
        return Err(err("health_filename_rejected"));
    }
    Ok(())
}
pub fn selected(name: &str) -> R<OwnedFile> {
    filename(name)?;
    if crate::runtime_root::is_real() {
        return Err(err("health_synthetic_only"));
    }
    let d = Dir::root()?.child("inputs", false)?;
    let mut f = d.open(name)?;
    if f.descriptor()?
        .metadata()
        .map_err(|_| err("health_file_rejected"))?
        .nlink()
        != 1
    {
        return Err(err("health_file_rejected"));
    }
    f.validate()?;
    Ok(f)
}
pub fn files() -> R<Vec<String>> {
    let d = Dir::root()?.child("inputs", false)?;
    let mut names = d.entries()?;
    if names.iter().filter(|n| !n.starts_with("test-")).count() > 64 {
        return Err(err("health_input_count_limit"));
    }
    names.retain(|n| !n.starts_with("test-") && filename(n).is_ok() && selected(n).is_ok());
    names.sort();
    Ok(names)
}
fn get(c: &Connection, t: &str, id: &str) -> R<Option<Value>> {
    let s: Option<String> = c
        .query_row(&format!("SELECT body FROM {t} WHERE id=?"), [id], |r| {
            r.get(0)
        })
        .optional()?;
    s.map(|s| serde_json::from_str(&s).map_err(|_| err("health_store_corrupt")))
        .transpose()
}
struct ChildGuard {
    child: std::process::Child,
    done: Arc<AtomicBool>,
}
impl Drop for ChildGuard {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
        self.done.store(true, Ordering::Release);
    }
}
/// Input is descriptor-bound and revalidated at transaction publication. No shell or arbitrary path.
pub fn import(
    c: &mut Connection,
    name: &str,
    at: i64,
    limits: &Value,
    mut progress: impl FnMut(u64),
    interrupt_after: Option<u64>,
) -> R<Value> {
    import_bound(c, name, at, limits, progress, interrupt_after, selected(name)?, false, || Ok(()))
}
pub trait Input {
    fn descriptor(&mut self) -> R<std::fs::File>;
    fn validate(&self) -> R<()>;
}
impl Input for OwnedFile {
    fn descriptor(&mut self) -> R<std::fs::File> { OwnedFile::descriptor(self) }
    fn validate(&self) -> R<()> { OwnedFile::validate(self) }
}
pub fn import_bound(c: &mut Connection, name: &str, at: i64, limits: &Value,
    mut progress: impl FnMut(u64), interrupt_after: Option<u64>, mut file: impl Input,
    private: bool, validate_target: impl Fn() -> R<()>) -> R<Value> {
    validate_target()?;
    let fd = file.descriptor()?;
    let before = fd.metadata().map_err(|_| err("health_file_rejected"))?;
    let identity = |m: &std::fs::Metadata| {
        (
            m.dev(),
            m.ino(),
            m.len(),
            m.mtime(),
            m.mtime_nsec(),
            m.ctime(),
            m.ctime_nsec(),
        )
    };
    let child = Command::new("/usr/bin/python3")
        .arg("-I")
        .arg("-B")
        .arg(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/tools/apple_health_source.py"
        ))
        .arg(limits.to_string())
        .env_clear()
        .stdin(Stdio::from(fd))
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|_| err("health_parser_unavailable"))?;
    let done = Arc::new(AtomicBool::new(false));
    let flag = done.clone();
    let pid = child.id();
    let parser_running = Arc::new(AtomicBool::new(true));
    let parser_flag = parser_running.clone();
    let interrupt = c.get_interrupt_handle();
    std::thread::spawn(move || {
        let start = Instant::now();
        while !flag.load(Ordering::Acquire) {
            if start.elapsed() > Duration::from_secs(300) {
                if parser_flag.load(Ordering::Acquire) {
                    unsafe {
                        libc::kill(pid as i32, libc::SIGKILL);
                    }
                }
                interrupt.interrupt();
                break;
            }
            std::thread::sleep(Duration::from_millis(50));
        }
    });
    let mut child = ChildGuard { child, done };
    let stdout = child.child.stdout.take().unwrap();
    let mut reader = BufReader::new(stdout);
    c.busy_timeout(Duration::from_secs(2))?;
    c.execute_batch("PRAGMA cache_size=-8192; PRAGMA max_page_count=262144;")?;
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    let legacy:i64=tx.query_row("SELECT count(*) FROM states WHERE json_extract(body,'$.kind')='health_current_state' AND COALESCE(json_extract(body,'$.protocol'),'legacy')<>'apple-file-v1'",[],|r|r.get(0))?;
    if legacy > 0 {
        return Err(err("health_protocol_overlap"));
    }
    let mut digest = String::new();
    let mut batch = String::new();
    let mut old = None;
    let mut inserted = 0u64;
    let mut duplicates = 0u64;
    let mut seen = 0u64;
    let mut end = None;
    let mut sources = std::collections::BTreeSet::new();
    loop {
        let mut line = String::new();
        let n = (&mut reader)
            .take(65537)
            .read_line(&mut line)
            .map_err(|_| err("health_parser_io_failed"))?;
        if n == 0 {
            break;
        }
        if n > 65536 || !line.ends_with('\n') {
            return Err(err("health_parser_line_limit"));
        }
        let v = crate::strict_json::parse(&line)?;
        match v["event"].as_str() {
            Some("begin") => {
                if !digest.is_empty() {
                    return Err(err("health_parser_protocol"));
                }
                digest = v["digest"]
                    .as_str()
                    .filter(|s| s.len() == 64 && s.bytes().all(|b| b.is_ascii_hexdigit()))
                    .ok_or_else(|| err("health_parser_protocol"))?
                    .into();
                batch = format!("health-apple-batch:{digest}");
                old = get(&tx, "records", &batch)?;
            }
            Some("row") => {
                if digest.is_empty() || end.is_some() {
                    return Err(err("health_parser_protocol"));
                }
                let row: Row = serde_json::from_value(v).map_err(|_| err("health_row_rejected"))?;
                row.check()?;
                seen += 1;
                if interrupt_after == Some(seen) {
                    return Err(err("health_test_interrupted"));
                }
                if seen % 100 == 0 {
                    progress(seen);
                }
                if old.is_some() {
                    continue;
                }
                let content = serde_json::to_string(&row).unwrap();
                let id = format!("health-apple-content:{}", hash(&content));
                let source_id = format!("health-apple-source:{}", hash(&row.source));
                sources.insert(source_id.clone());
                if sources.len() > 128 {
                    return Err(err("health_source_count_limit"));
                }
                if let Some(mut prior) = get(&tx, "records", &id)? {
                    duplicates += 1;
                    if prior["lastBatch"] == batch {
                        prior["ambiguousDuplicate"] = json!(true);
                    }
                    prior["lastBatch"] = json!(batch);
                    put(&tx, "records", &prior)?;
                } else {
                    inserted += 1;
                    put(
                        &tx,
                        "records",
                        &json!({"id":id,"kind":"health_apple_observation","protocol":"apple-file-v1","status":"observed","modelEligible":false,"sourceId":source_id,"observedAt":row.end_ms,"receivedAt":at,"firstBatch":batch,"lastBatch":batch,"contentFingerprintOnly":true,"ambiguousDuplicate":false,"days":row.days(),"row":row}),
                    )?;
                }
                // Membership is batch provenance, not sample revision. Unique within each batch.
                put(
                    &tx,
                    "records",
                    &json!({"id":format!("health-apple-member:{}:{}",digest,hash(&id)),"kind":"health_apple_membership","protocol":"apple-file-v1","modelEligible":false,"status":"observed","batch":batch,"observation":id}),
                )?;
                let mut source=get(&tx,"sources",&source_id)?.unwrap_or(json!({"id":source_id,"kind":"health_source","protocol":"apple-file-v1","name":row.source,"externalSourceId":source_id,"identityStrategy":"source-name-group","authorized":false,"ingestAuthorized":true,"modelEligible":false,"generation":1}));
                source["receivedAt"] = json!(at);
                source["observedAt"] =
                    json!(source["observedAt"].as_i64().unwrap_or(0).max(row.end_ms));
                put(&tx, "sources", &source)?;
            }
            Some("end") => {
                if digest.is_empty()
                    || end.is_some()
                    || v["digest"] != digest
                    || v["supported"].as_u64() != Some(seen)
                {
                    return Err(err("health_parser_protocol"));
                }
                end = Some(v);
            }
            Some("error") => return Err(err(v["code"].as_str().unwrap_or("health_parse_failed"))),
            _ => return Err(err("health_parser_protocol")),
        }
    }
    parser_running.store(false, Ordering::Release);
    let status = child
        .child
        .wait()
        .map_err(|_| err("health_parser_io_failed"))?;
    if !status.success() {
        return Err(err("health_parser_failed"));
    }
    let mut end = end.ok_or_else(|| err("health_parser_incomplete"))?;
    if private { end["types"] = json!({}); }
    validate_target()?;
    file.validate()?;
    let after = file
        .descriptor()?
        .metadata()
        .map_err(|_| err("health_file_rejected"))?;
    if identity(&before) != identity(&after) {
        return Err(err("health_file_changed"));
    }
    if let Some(old) = old {
        return Ok(
            json!({"status":"duplicate","file":name,"inserted":0,"duplicates":seen,"unsupported":old["unsupported"],"unsupportedTypes":old["unsupportedTypes"],"attachments":old["attachments"],"failed":0,"importedAt":old["receivedAt"],"originalImport":true}),
        );
    }
    let source_count: i64 = tx.query_row(
        "SELECT count(*) FROM sources WHERE json_extract(body,'$.protocol')='apple-file-v1'",
        [],
        |r| r.get(0),
    )?;
    if source_count > 128 {
        return Err(err("health_source_count_limit"));
    }
    let changed = project(&tx, at)?;
    let result = json!({"status":"completed","file":name,"inserted":inserted,"duplicates":duplicates,"unsupported":end["unsupported"],"unsupportedTypes":end["types"],"attachments":end["attachments"],"failed":0,"importedAt":at,"changedStates":changed});
    put(
        &tx,
        "records",
        &json!({"id":batch,"kind":"health_batch","protocol":"apple-file-v1","modelEligible":false,"status":"observed","file":name,"receivedAt":at,"inserted":inserted,"duplicates":duplicates,"unsupported":end["unsupported"],"unsupportedTypes":end["types"],"attachments":end["attachments"],"sources":sources,"result":result}),
    )?;
    tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1", [])?;
    validate_target()?;
    file.validate()?;
    tx.commit()?;
    Ok(result)
}
#[derive(Default)]
struct Group {
    key: String,
    source: String,
    metric: String,
    offset: i64,
    day: i64,
    end: i64,
    observed: i64,
    total: f64,
    uncertain: bool,
    estimated: bool,
    count: u64,
}
fn save(c: &Connection, g: &Group, at: i64) -> R<()> {
    if g.key.is_empty() {
        return Ok(());
    }
    let id = format!("health-apple-state:{}", hash(&g.key));
    let old = get(c, "states", &id)?;
    let value = if g.uncertain {
        Value::Null
    } else {
        json!(g.total)
    };
    let same = old.as_ref().is_some_and(|o| {
        o["value"] == value && o["observedAt"] == g.observed && o["observationCount"] == g.count
    });
    put(
        c,
        "states",
        &json!({"id":id,"kind":"health_current_state","protocol":"apple-file-v1","status":"observed","modelEligible":false,"domain":"Health","metric":g.metric,"unit":if g.metric=="steps"{"count"}else{"minutes"},"dayIndex":g.day,"offsetMinutes":g.offset,"value":value,"method":if g.uncertain{"file_observation_uncertain"}else{"file_observation_subset"},"estimated":g.estimated,"observedAt":g.observed,"receivedAt":if same{old.as_ref().unwrap()["receivedAt"].as_i64().unwrap_or(at)}else{at},"observationCount":g.count,"sources":[{"name":g.source,"value":value}],"refs":[],"coverage":"unknown"}),
    )
}
fn project(c: &Connection, at: i64) -> R<u64> {
    // SQLite performs a disk-capable ordered stream; never load all sample rows into a Vec.
    let mut q=c.prepare("SELECT r.body, CAST(d.value AS INTEGER) FROM records r,json_each(r.body,'$.days') d WHERE json_extract(r.body,'$.kind')='health_apple_observation' ORDER BY json_extract(r.body,'$.row.source'),json_extract(r.body,'$.row.metric'),json_extract(r.body,'$.row.offset'),CAST(d.value AS INTEGER),json_extract(r.body,'$.row.startMs'),r.id")?;
    let mut rows = q.query([])?;
    let mut g = Group::default();
    let mut groups = 0;
    while let Some(r) = rows.next()? {
        let raw: String = r.get(0)?;
        let day: i64 = r.get(1)?;
        let v: Value = serde_json::from_str(&raw).map_err(|_| err("health_store_corrupt"))?;
        let row: Row =
            serde_json::from_value(v["row"].clone()).map_err(|_| err("health_store_corrupt"))?;
        if row.metric == "sleep" && !row.asleep {
            continue;
        }
        let key = json!([row.source, row.metric, row.offset, day]).to_string();
        if key != g.key {
            save(c, &g, at)?;
            groups += 1;
            if groups > 10000 {
                return Err(err("health_projection_limit"));
            }
            g = Group {
                key,
                source: row.source.clone(),
                metric: row.metric.clone(),
                offset: row.offset,
                day,
                end: i64::MIN,
                ..Default::default()
            };
        }
        let from = day * DAY - row.offset * 60000;
        let start = row.start_ms.max(from);
        let end = row.end_ms.min(from + DAY);
        if row.metric == "sleep" {
            g.total += (end - start.max(g.end).min(end)) as f64 / 60000.0;
        } else {
            g.uncertain |= start < g.end || v["ambiguousDuplicate"] == true;
            g.total +=
                row.value.unwrap() * (end - start) as f64 / (row.end_ms - row.start_ms) as f64;
            g.estimated |= row.start_ms < from || row.end_ms > from + DAY;
        }
        g.end = g.end.max(end);
        g.observed = g.observed.max(row.end_ms);
        g.count += 1;
    }
    save(c, &g, at)?;
    Ok(groups)
}
#[cfg(test)]
mod tests;
