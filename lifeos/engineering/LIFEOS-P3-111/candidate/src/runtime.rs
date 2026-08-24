use rusqlite::{params, Connection, OpenFlags, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs::{self, OpenOptions};
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

const DB_NAME: &str = "capture.sqlite";
const PILOT_ROOT: &str = "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2";
const PILOT_DB: &str = "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2/capture.sqlite";
const IPC_ALLOWLIST: [&str; 3] = ["capture_record", "get_today", "runtime_status"];
const MAX_RECORDS: usize = 3;
const MAX_TEXT_CHARS: usize = 280;

// P3-106 的冻结 schema 合同原样保留；P3-111 未更改 Schema/API。
const SCHEMA: &str = r#"
PRAGMA journal_mode = DELETE;
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS captures (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  source TEXT NOT NULL CHECK(source = 'local_capture'),
  idem_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event TEXT NOT NULL CHECK(event IN ('capture_saved', 'capture_repeat')),
  capture_id TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  detail TEXT NOT NULL,
  FOREIGN KEY(capture_id) REFERENCES captures(id)
);
PRAGMA user_version = 104;
"#;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CaptureRequest { text: String, key: String }

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EmptyRequest {}

#[derive(Debug, Serialize, Clone)]
struct RecordView { id: String, content: String, created_at_ms: u64, source: String, identity: &'static str }

#[derive(Debug, Serialize)]
struct CaptureResponse { status: &'static str, record: RecordView, record_count: usize, audit_event_count: usize }

#[derive(Debug, Serialize)]
struct AuditSummary { event_count: usize, saved_count: usize, repeat_count: usize, last_event: Option<String> }

#[derive(Debug, Serialize)]
struct TodayResponse { status: &'static str, records: Vec<RecordView>, source: &'static str, ai_status: &'static str, audit: AuditSummary }

#[derive(Debug, Serialize)]
struct RuntimeStatusResponse {
    status: &'static str, offline: bool, ai_enabled: bool, renderer_direct_capabilities: Vec<&'static str>, ipc_allowlist: Vec<&'static str>, unknown_ipc: &'static str,
    filesystem: bool, raw_database: bool, generic_path_api: bool, shell: bool, process_spawn: bool, network: bool, vault: bool, export: bool, sync: bool,
}

#[derive(Debug, Serialize)]
struct IpcError { status: &'static str, code: &'static str, message: &'static str }

impl IpcError {
    fn blocked(code: &'static str, message: &'static str) -> Self {
        eprintln!("ipc_result status=blocked code={code}");
        Self { status: "blocked", code, message }
    }
}

struct AppState { db_path: PathBuf, serial: Mutex<()> }

#[derive(Clone, Copy, PartialEq)]
enum Fault { None, BeforeCommit }

#[derive(Clone, Copy)]
enum StorageScope { Pilot, Fixture }

fn now_ms() -> Result<u64, IpcError> {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|value| value.as_millis() as u64)
        .map_err(|_| IpcError::blocked("clock_unavailable", "本地时间不可用；未保存记录。"))
}

fn new_id(now: u64, key: &str) -> String { format!("p3-111-{now:016x}-{key}") }

fn sqlite_error(_: rusqlite::Error) -> IpcError {
    IpcError::blocked("database_unavailable", "本地数据库无法验证；未显示成功，也未保留半成品。")
}

fn io_error(_: std::io::Error) -> IpcError {
    IpcError::blocked("path_boundary_unavailable", "本地路径边界无法验证；未显示成功，也未保留半成品。")
}

fn optional_metadata(path: &Path) -> Result<Option<fs::Metadata>, IpcError> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => Ok(Some(metadata)),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(error) => Err(io_error(error)),
    }
}

fn ensure_real_directory(path: &Path) -> Result<(), IpcError> {
    let metadata = fs::symlink_metadata(path).map_err(io_error)?;
    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() {
        return Err(IpcError::blocked("path_symlink_rejected", "数据库祖先目录不是无链接真实目录。"));
    }
    Ok(())
}

fn test_base() -> PathBuf { PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("evidence/test-fixtures") }

fn storage_scope(path: &Path) -> Result<StorageScope, IpcError> {
    if path == Path::new(PILOT_DB) { return Ok(StorageScope::Pilot); }
    let base = test_base();
    let parent = path.parent();
    if path.file_name().and_then(|value| value.to_str()) == Some(DB_NAME)
        && parent.and_then(Path::parent).is_some_and(|value| value == base)
    { return Ok(StorageScope::Fixture); }
    Err(IpcError::blocked("path_schema_rejected", "数据库不在唯一 Pilot-2 或受控包内测试夹具路径。"))
}

fn validate_database_object(path: &Path) -> Result<bool, IpcError> {
    let Some(metadata) = optional_metadata(path)? else { return Ok(false); };
    if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 {
        return Err(IpcError::blocked("database_type_rejected", "数据库不是普通单链接文件。"));
    }
    Ok(true)
}

fn validate_database_path(path: &Path, create_parent: bool) -> Result<bool, IpcError> {
    let scope = storage_scope(path)?;
    let parent = path.parent().ok_or_else(|| IpcError::blocked("path_schema_rejected", "数据库父目录不在允许边界内。"))?;
    match scope {
        StorageScope::Pilot => {
            for ancestor in [Path::new("/Users"), Path::new("/Users/xxe"), Path::new("/Users/xxe/Documents")] { ensure_real_directory(ancestor)?; }
            if parent != Path::new(PILOT_ROOT) { return Err(IpcError::blocked("path_schema_rejected", "数据库只能是唯一 Pilot-2/capture.sqlite。")); }
        }
        StorageScope::Fixture => ensure_real_directory(&test_base())?,
    }
    let parent_metadata = match optional_metadata(parent)? {
        Some(metadata) => metadata,
        None if create_parent => { fs::create_dir(parent).map_err(io_error)?; fs::symlink_metadata(parent).map_err(io_error)? }
        None => return Ok(false),
    };
    if !parent_metadata.file_type().is_dir() || parent_metadata.file_type().is_symlink() {
        return Err(IpcError::blocked("path_symlink_rejected", "数据库父对象不是无链接真实目录。"));
    }
    let database_present = validate_database_object(path)?;
    for suffix in ["-journal", "-wal", "-shm"] {
        let sidecar = PathBuf::from(format!("{}{}", path.display(), suffix));
        if optional_metadata(&sidecar)?.is_some() {
            return Err(IpcError::blocked("database_sidecar_rejected", "数据库存在未支持的 sidecar；运行时保持 fail-closed。"));
        }
    }
    for entry in fs::read_dir(parent).map_err(io_error)? {
        let name = entry.map_err(io_error)?.file_name().to_string_lossy().into_owned();
        if name.starts_with(".capture.sqlite.") && name.ends_with(".shadow") {
            return Err(IpcError::blocked("candidate_residue_rejected", "发现未完成候选工件；运行时保持 fail-closed。"));
        }
    }
    Ok(database_present)
}

fn valid_text(value: &str) -> bool { !value.trim().is_empty() && value.chars().count() <= MAX_TEXT_CHARS && !value.chars().any(|ch| ch == '\0') }
fn valid_key(value: &str) -> bool { value.starts_with("p3-111-") && value.len() <= 96 && value.chars().all(|ch| ch.is_ascii_alphanumeric() || ch == '-') }

fn validate_request(request: &CaptureRequest) -> Result<(), IpcError> {
    if !valid_text(&request.text) || !valid_key(&request.key) {
        return Err(IpcError::blocked("argument_schema_rejected", "输入不是允许的简短本地原文或受控幂等键。"));
    }
    Ok(())
}

fn open_read_only(path: &Path) -> Result<Connection, IpcError> {
    let conn = Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sqlite_error)?;
    conn.pragma_update(None, "query_only", true).map_err(sqlite_error)?;
    validate_connection(&conn)?;
    Ok(conn)
}

fn validate_connection(conn: &Connection) -> Result<(), IpcError> {
    let quick: String = conn.query_row("PRAGMA quick_check", [], |row| row.get(0)).map_err(sqlite_error)?;
    let version: i64 = conn.query_row("PRAGMA user_version", [], |row| row.get(0)).map_err(sqlite_error)?;
    if quick != "ok" || version != 104 { return Err(IpcError::blocked("database_contract_rejected", "数据库完整性或版本不符合冻结合同。")); }
    let table_count: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('captures','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    let unexpected: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT IN ('captures','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    if table_count != 3 || unexpected != 0 { return Err(IpcError::blocked("database_schema_rejected", "数据库表结构不符合冻结合同。")); }
    validated_today(conn).map(|_| ())
}

fn validated_today(conn: &Connection) -> Result<(Vec<RecordView>, AuditSummary), IpcError> {
    let mut statement = conn.prepare("SELECT id, content, created_at_ms, source, idem_key FROM captures ORDER BY created_at_ms, id").map_err(sqlite_error)?;
    let rows = statement.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?, row.get::<_, String>(3)?, row.get::<_, String>(4)?))).map_err(sqlite_error)?;
    let mut records = Vec::new();
    let mut ids = BTreeSet::new();
    for row in rows {
        let (id, content, created_at, source, key) = row.map_err(sqlite_error)?;
        if !id.starts_with("p3-111-") || !valid_text(&content) || created_at <= 0 || source != "local_capture" || !valid_key(&key) || !ids.insert(id.clone()) {
            return Err(IpcError::blocked("record_identity_rejected", "记录身份、来源或用户原文不可信。"));
        }
        records.push(RecordView { id, content, created_at_ms: created_at as u64, source, identity: "user_original" });
    }
    if records.len() > MAX_RECORDS { return Err(IpcError::blocked("record_limit_rejected", "本次受控使用最多允许三条本地记录。")); }
    let mut audit_statement = conn.prepare("SELECT event, capture_id, created_at_ms, detail FROM audit ORDER BY id").map_err(sqlite_error)?;
    let audit_rows = audit_statement.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?, row.get::<_, String>(3)?))).map_err(sqlite_error)?;
    let mut saved = BTreeSet::new(); let mut event_count = 0usize; let mut saved_count = 0usize; let mut repeat_count = 0usize; let mut last_event = None; let mut last_time = 0i64;
    for row in audit_rows {
        let (event, capture_id, created_at, detail) = row.map_err(sqlite_error)?;
        if created_at <= 0 || created_at < last_time || !ids.contains(&capture_id) { return Err(IpcError::blocked("audit_sequence_rejected", "审计顺序或记录绑定不可信。")); }
        match event.as_str() {
            "capture_saved" if detail == "local_capture" && saved.insert(capture_id.clone()) => saved_count += 1,
            "capture_repeat" if detail == "same_idempotency_key" && saved.contains(&capture_id) => repeat_count += 1,
            _ => return Err(IpcError::blocked("audit_contract_rejected", "审计事件不符合冻结合同。")),
        }
        event_count += 1; last_time = created_at; last_event = Some(event);
    }
    if saved.len() != records.len() || saved_count != records.len() { return Err(IpcError::blocked("audit_replay_rejected", "记录与审计重放状态不一致。")); }
    Ok((records, AuditSummary { event_count, saved_count, repeat_count, last_event }))
}

fn remove_candidate(path: &Path) {
    for candidate in [path.to_path_buf(), PathBuf::from(format!("{}-journal", path.display())), PathBuf::from(format!("{}-wal", path.display())), PathBuf::from(format!("{}-shm", path.display()))] { let _ = fs::remove_file(candidate); }
}

fn capture_impl(path: &Path, request: &CaptureRequest, fault: Fault) -> Result<CaptureResponse, IpcError> {
    validate_request(request)?;
    let database_present = validate_database_path(path, true)?;
    let now = now_ms()?; let parent = path.parent().expect("validated parent");
    let candidate = parent.join(format!(".capture.sqlite.{now}.{}.shadow", std::process::id()));
    remove_candidate(&candidate);
    OpenOptions::new().write(true).create_new(true).open(&candidate).map_err(io_error)?;
    if database_present { if let Err(error) = fs::copy(path, &candidate) { remove_candidate(&candidate); return Err(io_error(error)); } }
    let operation = (|| -> Result<(CaptureResponse, bool), IpcError> {
        let mut conn = Connection::open(&candidate).map_err(sqlite_error)?;
        conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE;").map_err(sqlite_error)?;
        if database_present { validate_connection(&conn)?; } else { conn.execute_batch(SCHEMA).map_err(sqlite_error)?; }
        let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sqlite_error)?;
        let prior = tx.query_row("SELECT id, content, created_at_ms FROM captures WHERE idem_key=?1", params![request.key], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?))).optional().map_err(sqlite_error)?;
        let (status, record, repeated) = if let Some((id, content, created_at)) = prior {
            if content != request.text { return Err(IpcError::blocked("idempotency_conflict", "幂等键已绑定其他记录；冲突已阻断，数据库未更改。")); }
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_repeat',?1,?2,'same_idempotency_key')", params![id, now as i64]).map_err(sqlite_error)?;
            ("idempotent_repeat", RecordView { id, content, created_at_ms: created_at as u64, source: "local_capture".to_string(), identity: "user_original" }, true)
        } else {
            let count: i64 = tx.query_row("SELECT count(*) FROM captures", [], |row| row.get(0)).map_err(sqlite_error)?;
            if count as usize >= MAX_RECORDS { return Err(IpcError::blocked("record_limit_rejected", "本次受控使用最多允许三条本地记录。")); }
            let id = new_id(now, &request.key);
            tx.execute("INSERT INTO captures(id,content,created_at_ms,source,idem_key) VALUES(?1,?2,?3,'local_capture',?4)", params![id, request.text, now as i64, request.key]).map_err(sqlite_error)?;
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_saved',?1,?2,'local_capture')", params![id, now as i64]).map_err(sqlite_error)?;
            ("saved", RecordView { id, content: request.text.clone(), created_at_ms: now, source: "local_capture".to_string(), identity: "user_original" }, false)
        };
        if fault == Fault::BeforeCommit { return Err(IpcError::blocked("injected_atomic_failure", "受控失败已注入；未显示成功，数据库与页面状态未更改。")); }
        tx.commit().map_err(sqlite_error)?; drop(conn);
        let verified = open_read_only(&candidate)?; let (records, audit) = validated_today(&verified)?; drop(verified);
        Ok((CaptureResponse { status, record, record_count: records.len(), audit_event_count: audit.event_count }, repeated))
    })();
    match operation {
        Ok((response, repeated)) => {
            if validate_database_object(path)? != database_present { remove_candidate(&candidate); return Err(IpcError::blocked("database_object_changed", "数据库最终对象在发布前发生变化；候选未发布。")); }
            if let Err(error) = fs::rename(&candidate, path) { remove_candidate(&candidate); return Err(io_error(error)); }
            remove_candidate(&candidate);
            eprintln!("ipc_result command=capture_record status={} record_count={} audit_event_count={} repeated={}", response.status, response.record_count, response.audit_event_count, repeated);
            Ok(response)
        }
        Err(error) => { remove_candidate(&candidate); Err(error) }
    }
}

fn today_impl(path: &Path) -> Result<TodayResponse, IpcError> {
    let database_present = validate_database_path(path, false)?;
    if !database_present { return Ok(TodayResponse { status: "empty", records: Vec::new(), source: "local_capture", ai_status: "disabled", audit: AuditSummary { event_count: 0, saved_count: 0, repeat_count: 0, last_event: None } }); }
    let conn = open_read_only(path)?; let (records, audit) = validated_today(&conn)?;
    eprintln!("ipc_result command=get_today status=loaded record_count={} audit_event_count={}", records.len(), audit.event_count);
    Ok(TodayResponse { status: "loaded", records, source: "local_capture", ai_status: "disabled", audit })
}

fn status_impl() -> RuntimeStatusResponse {
    RuntimeStatusResponse { status: "restricted_offline", offline: true, ai_enabled: false, renderer_direct_capabilities: Vec::new(), ipc_allowlist: IPC_ALLOWLIST.to_vec(), unknown_ipc: "deny", filesystem: false, raw_database: false, generic_path_api: false, shell: false, process_spawn: false, network: false, vault: false, export: false, sync: false }
}

#[tauri::command]
fn capture_record(request: CaptureRequest, state: tauri::State<'_, AppState>) -> Result<CaptureResponse, IpcError> {
    let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未保存记录。"))?;
    capture_impl(&state.db_path, &request, Fault::None)
}

#[tauri::command]
fn get_today(request: EmptyRequest, state: tauri::State<'_, AppState>) -> Result<TodayResponse, IpcError> {
    let _ = request;
    let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未读取记录。"))?;
    today_impl(&state.db_path)
}

#[tauri::command]
fn runtime_status(request: EmptyRequest) -> RuntimeStatusResponse { let _ = request; eprintln!("ipc_result command=runtime_status status=restricted_offline"); status_impl() }

pub fn run() {
    let db_path = PathBuf::from(PILOT_DB);
    validate_database_path(&db_path, false).unwrap_or_else(|error| panic!("controlled DB boundary rejected: {}", error.code));
    eprintln!("runtime_start status=restricted_offline db_scope=pilot2");
    tauri::Builder::default().manage(AppState { db_path, serial: Mutex::new(()) })
        .invoke_handler(tauri::generate_handler![capture_record, get_today, runtime_status])
        .run(tauri::generate_context!()).expect("P3-111 Tauri runtime failed");
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture(name: &str) -> (PathBuf, PathBuf) {
        let root = test_base().join(format!("{name}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&root); fs::create_dir_all(&root).unwrap(); (root.join(DB_NAME), root)
    }
    fn request(text: &str, key: &str) -> CaptureRequest { CaptureRequest { text: text.to_string(), key: key.to_string() } }
    fn primary() -> CaptureRequest { request("P3-111 fixed non-sensitive lifecycle fixture.", "p3-111-test-primary") }

    #[test]
    fn lifecycle_saved_repeat_conflict_restart() {
        let (db, root) = fixture("lifecycle");
        let saved = capture_impl(&db, &primary(), Fault::None).unwrap(); assert_eq!(saved.status, "saved");
        let repeat = capture_impl(&db, &primary(), Fault::None).unwrap(); assert_eq!(repeat.status, "idempotent_repeat"); assert_eq!(repeat.record.id, saved.record.id);
        assert_eq!(capture_impl(&db, &request("P3-111 fixed non-sensitive conflict.", "p3-111-test-primary"), Fault::None).unwrap_err().code, "idempotency_conflict");
        let today = today_impl(&db).unwrap(); assert_eq!(today.records.len(), 1); assert_eq!(today.audit.event_count, 2); assert_eq!(today.records[0].identity, "user_original");
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn injected_failure_preserves_database_and_sentinel() {
        let (db, root) = fixture("failure"); capture_impl(&db, &primary(), Fault::None).unwrap();
        let sentinel = root.join("sentinel.txt"); fs::write(&sentinel, b"P3-111-SENTINEL").unwrap();
        let before_db = fs::read(&db).unwrap(); let before_sentinel = fs::read(&sentinel).unwrap();
        let error = capture_impl(&db, &request("P3-111 fixed non-sensitive failure fixture.", "p3-111-test-failure"), Fault::BeforeCommit).unwrap_err();
        assert_eq!(error.code, "injected_atomic_failure"); assert_eq!(fs::read(&db).unwrap(), before_db); assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel); assert_eq!(today_impl(&db).unwrap().records.len(), 1); assert_eq!(fs::read_dir(&root).unwrap().count(), 2);
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn path_and_argument_boundaries_fail_closed() {
        assert_eq!(validate_database_path(Path::new("/Users/xxe/Documents/not-pilot/capture.sqlite"), false).unwrap_err().code, "path_schema_rejected");
        let (db, root) = fixture("arguments"); assert_eq!(capture_impl(&db, &request("", "p3-111-test-primary"), Fault::None).unwrap_err().code, "argument_schema_rejected"); assert!(!db.exists()); fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn ipc_extra_fields_are_rejected_before_runtime_logic() {
        assert!(serde_json::from_str::<CaptureRequest>(r#"{"text":"fixed","key":"p3-111-test-primary","path":"/escape"}"#).is_err());
        assert!(serde_json::from_str::<EmptyRequest>(r#"{"sql":"SELECT 1"}"#).is_err());
    }

    #[test]
    fn symlink_and_hardlink_boundaries_fail_closed() {
        use std::os::unix::fs::symlink;
        let (db, root) = fixture("links"); let outside = root.join("outside.txt"); fs::write(&outside, b"P3-111-OUTSIDE-SENTINEL").unwrap(); symlink(&outside, &db).unwrap();
        assert_eq!(validate_database_path(&db, false).unwrap_err().code, "database_type_rejected"); fs::remove_file(&db).unwrap(); capture_impl(&db, &primary(), Fault::None).unwrap();
        let hardlink = root.join("hardlink.sqlite"); fs::hard_link(&db, &hardlink).unwrap(); assert_eq!(validate_database_path(&db, false).unwrap_err().code, "database_type_rejected"); fs::remove_file(hardlink).unwrap(); fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn dangling_database_and_sidecar_links_fail_closed() {
        use std::os::unix::fs::symlink;
        let (db, root) = fixture("dangling"); let missing = root.join("missing.sqlite"); symlink(&missing, &db).unwrap(); assert_eq!(capture_impl(&db, &primary(), Fault::None).unwrap_err().code, "database_type_rejected");
        fs::remove_file(&db).unwrap(); capture_impl(&db, &primary(), Fault::None).unwrap(); let sidecar = PathBuf::from(format!("{}-wal", db.display())); symlink(root.join("missing-wal"), &sidecar).unwrap(); assert_eq!(today_impl(&db).unwrap_err().code, "database_sidecar_rejected"); fs::remove_file(sidecar).unwrap(); fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn runtime_status_closes_direct_capabilities() {
        let status = status_impl(); assert!(status.offline && !status.ai_enabled && status.renderer_direct_capabilities.is_empty()); assert_eq!(status.ipc_allowlist, IPC_ALLOWLIST); assert_eq!(status.unknown_ipc, "deny"); assert!(!status.filesystem && !status.raw_database && !status.generic_path_api); assert!(!status.shell && !status.process_spawn && !status.network && !status.vault && !status.export && !status.sync);
    }

    #[test]
    fn tampered_content_and_schema_fail_closed() {
        let (db, root) = fixture("tamper"); capture_impl(&db, &primary(), Fault::None).unwrap(); let conn = Connection::open(&db).unwrap(); conn.execute("UPDATE captures SET content=''", []).unwrap(); drop(conn); assert_eq!(today_impl(&db).unwrap_err().code, "record_identity_rejected"); fs::remove_dir_all(root).unwrap();
    }
}
