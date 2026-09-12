//! Controlled SQLite repository adapter. No model, network or credentials linkage.
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::os::unix::fs::PermissionsExt;
use std::{
    fs,
    path::PathBuf,
    time::{SystemTime, UNIX_EPOCH},
};
pub(crate) const TABLES: &[&str] = &[
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
#[derive(Deserialize)]
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
    if crate::runtime_root::is_real() && fixture != "conversation" {
        return reject("source_activation_required");
    }
    if fixture.is_empty()
        || fixture.len() > 60
        || !fixture
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || c == b'-')
    {
        return reject("fixture_rejected");
    }
    let root = crate::runtime_root::verify()?;
    let path = crate::runtime_root::store_path(fixture)?;
    let anchored = if crate::runtime_root::is_real() {
        let d = crate::artifact_io::Dir::root()?;
        Some(if d.exists("sources.sqlite")? {
            d.open("sources.sqlite")?
        } else {
            d.create("sources.sqlite")?
        })
    } else {
        None
    };
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
    let c = Connection::open_with_flags(
        &path,
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE
            | rusqlite::OpenFlags::SQLITE_OPEN_CREATE
            | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX
            | rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW,
    )?;
    if let Some(f) = &anchored {
        f.validate()?;
    } else {
        fs::set_permissions(&path, fs::Permissions::from_mode(0o600))
            .map_err(|_| Error::new("permissions_failed"))?;
    }
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