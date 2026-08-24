use rusqlite::{params, Connection, OpenFlags, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashMap};
use std::env;
use std::fs::{self, OpenOptions};
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

const DB_NAME: &str = "capture.sqlite";
const FIXTURE_PREFIX: &str = "lifeos-p3-104-";
const PRIMARY_TEXT: &str = "P3-104 固定非敏感记录：核对今日页本地运行时。";
const CONFLICT_TEXT: &str = "P3-104 固定非敏感冲突文本：必须被阻断。";
const FAILURE_TEXT: &str = "P3-104 固定非敏感失败夹具：不得持久化。";
const PRIMARY_KEY: &str = "p3-104-ui-primary";
const FAILURE_KEY: &str = "p3-104-ui-failure";
const IPC_ALLOWLIST: [&str; 3] = ["capture_record", "get_today", "runtime_status"];

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
struct CaptureRequest {
    text: String,
    key: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EmptyRequest {}

#[derive(Debug, Serialize, Clone)]
struct RecordView {
    id: String,
    content: String,
    created_at_ms: u64,
    source: String,
    identity: &'static str,
}

#[derive(Debug, Serialize)]
struct CaptureResponse {
    status: &'static str,
    record: RecordView,
    record_count: usize,
    audit_event_count: usize,
}

#[derive(Debug, Serialize)]
struct AuditSummary {
    event_count: usize,
    saved_count: usize,
    repeat_count: usize,
    last_event: Option<String>,
}

#[derive(Debug, Serialize)]
struct TodayResponse {
    status: &'static str,
    records: Vec<RecordView>,
    source: &'static str,
    ai_status: &'static str,
    audit: AuditSummary,
}

#[derive(Debug, Serialize)]
struct RuntimeStatusResponse {
    status: &'static str,
    offline: bool,
    ai_enabled: bool,
    renderer_direct_capabilities: Vec<&'static str>,
    ipc_allowlist: Vec<&'static str>,
    unknown_ipc: &'static str,
    filesystem: bool,
    raw_database: bool,
    generic_path_api: bool,
    shell: bool,
    process_spawn: bool,
    network: bool,
    vault: bool,
    export: bool,
    sync: bool,
}

#[derive(Debug, Serialize)]
struct IpcError {
    status: &'static str,
    code: &'static str,
    message: &'static str,
}

impl IpcError {
    fn blocked(code: &'static str, message: &'static str) -> Self {
        eprintln!("ipc_result status=blocked code={code}");
        Self {
            status: "blocked",
            code,
            message,
        }
    }
}

struct AppState {
    db_path: PathBuf,
    serial: Mutex<()>,
}

fn now_ms() -> Result<u64, IpcError> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|value| value.as_millis() as u64)
        .map_err(|_| IpcError::blocked("clock_unavailable", "本地时间不可用；未保存记录。"))
}

fn new_id(now: u64) -> String {
    format!("p3-104-{now:016x}-{:08x}", std::process::id())
}

fn sqlite_error(_: rusqlite::Error) -> IpcError {
    IpcError::blocked(
        "database_unavailable",
        "本地数据库无法验证；未显示成功，也未保留半成品。",
    )
}

fn io_error(_: std::io::Error) -> IpcError {
    IpcError::blocked(
        "path_boundary_unavailable",
        "task-local 路径边界无法验证；未显示成功，也未保留半成品。",
    )
}

fn optional_metadata(path: &Path) -> Result<Option<fs::Metadata>, IpcError> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => Ok(Some(metadata)),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(error) => Err(io_error(error)),
    }
}

fn validate_database_object(path: &Path) -> Result<bool, IpcError> {
    let Some(metadata) = optional_metadata(path)? else {
        return Ok(false);
    };
    if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 {
        return Err(IpcError::blocked(
            "database_type_rejected",
            "数据库不是普通单链接文件。",
        ));
    }
    Ok(true)
}

fn validate_database_path(path: &Path) -> Result<bool, IpcError> {
    let raw = path.to_str().ok_or_else(|| {
        IpcError::blocked("path_schema_rejected", "数据库路径不是允许的 UTF-8 task-local 路径。")
    })?;
    if !raw.starts_with("/private/tmp/")
        || raw.contains("//")
        || raw.contains("/./")
        || raw.contains("/../")
        || path.file_name().and_then(|value| value.to_str()) != Some(DB_NAME)
    {
        return Err(IpcError::blocked(
            "path_schema_rejected",
            "数据库只允许固定 /private/tmp task-local capture.sqlite。",
        ));
    }
    let parent = path.parent().ok_or_else(|| {
        IpcError::blocked("path_schema_rejected", "数据库父目录不在允许边界内。")
    })?;
    if parent.parent() != Some(Path::new("/private/tmp"))
        || !parent
            .file_name()
            .and_then(|value| value.to_str())
            .is_some_and(|name| name.starts_with(FIXTURE_PREFIX) && name.len() > FIXTURE_PREFIX.len())
    {
        return Err(IpcError::blocked(
            "path_schema_rejected",
            "数据库父目录不是 P3-104 固定 task-local 夹具。",
        ));
    }
    for component in [Path::new("/private"), Path::new("/private/tmp")] {
        let metadata = fs::symlink_metadata(component).map_err(io_error)?;
        if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() {
            return Err(IpcError::blocked(
                "path_symlink_rejected",
                "数据库祖先目录不是无链接真实目录。",
            ));
        }
    }
    let parent_metadata = match optional_metadata(parent)? {
        Some(metadata) => metadata,
        None => {
            fs::create_dir(parent).map_err(io_error)?;
            fs::symlink_metadata(parent).map_err(io_error)?
        }
    };
    if !parent_metadata.file_type().is_dir() || parent_metadata.file_type().is_symlink() {
        return Err(IpcError::blocked(
            "path_symlink_rejected",
            "数据库父对象不是无链接真实目录。",
        ));
    }
    let database_present = validate_database_object(path)?;
    for suffix in ["-journal", "-wal", "-shm"] {
        let sidecar = PathBuf::from(format!("{}{}", path.display(), suffix));
        if optional_metadata(&sidecar)?.is_some() {
            return Err(IpcError::blocked(
                "database_sidecar_rejected",
                "数据库存在未支持的 sidecar；运行时保持 fail-closed。",
            ));
        }
    }
    for entry in fs::read_dir(parent).map_err(io_error)? {
        let name = entry
            .map_err(io_error)?
            .file_name()
            .to_string_lossy()
            .into_owned();
        if name.starts_with(".capture.sqlite.") && name.ends_with(".shadow") {
            return Err(IpcError::blocked(
                "candidate_residue_rejected",
                "发现未完成候选工件；运行时保持 fail-closed。",
            ));
        }
    }
    Ok(database_present)
}

fn open_read_only(path: &Path) -> Result<Connection, IpcError> {
    let conn = Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sqlite_error)?;
    conn.pragma_update(None, "query_only", true).map_err(sqlite_error)?;
    validate_connection(&conn)?;
    Ok(conn)
}

fn validate_connection(conn: &Connection) -> Result<(), IpcError> {
    let quick: String = conn
        .query_row("PRAGMA quick_check", [], |row| row.get(0))
        .map_err(sqlite_error)?;
    let version: i64 = conn
        .query_row("PRAGMA user_version", [], |row| row.get(0))
        .map_err(sqlite_error)?;
    if quick != "ok" || version != 104 {
        return Err(IpcError::blocked(
            "database_contract_rejected",
            "数据库完整性或版本不符合冻结合同。",
        ));
    }
    let table_count: i64 = conn
        .query_row(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('captures','audit','sqlite_sequence')",
            [],
            |row| row.get(0),
        )
        .map_err(sqlite_error)?;
    let unexpected: i64 = conn
        .query_row(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT IN ('captures','audit','sqlite_sequence')",
            [],
            |row| row.get(0),
        )
        .map_err(sqlite_error)?;
    if table_count != 3 || unexpected != 0 {
        return Err(IpcError::blocked(
            "database_schema_rejected",
            "数据库表结构不符合冻结合同。",
        ));
    }
    validated_today(conn).map(|_| ())
}

fn validated_today(conn: &Connection) -> Result<(Vec<RecordView>, AuditSummary), IpcError> {
    let mut record_statement = conn
        .prepare("SELECT id, content, created_at_ms, source, idem_key FROM captures ORDER BY created_at_ms, id")
        .map_err(sqlite_error)?;
    let rows = record_statement
        .query_map([], |row| {
            Ok((
                row.get::<_, String>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, i64>(2)?,
                row.get::<_, String>(3)?,
                row.get::<_, String>(4)?,
            ))
        })
        .map_err(sqlite_error)?;
    let mut records = Vec::new();
    let mut ids = BTreeSet::new();
    for row in rows {
        let (id, content, created_at, source, key) = row.map_err(sqlite_error)?;
        if id.is_empty()
            || content != PRIMARY_TEXT
            || created_at <= 0
            || source != "local_capture"
            || key != PRIMARY_KEY
            || !ids.insert(id.clone())
        {
            return Err(IpcError::blocked(
                "record_identity_rejected",
                "记录身份、来源或固定非敏感内容不可信。",
            ));
        }
        records.push(RecordView {
            id,
            content,
            created_at_ms: created_at as u64,
            source,
            identity: "user_original",
        });
    }

    let mut audit_statement = conn
        .prepare("SELECT event, capture_id, created_at_ms, detail FROM audit ORDER BY id")
        .map_err(sqlite_error)?;
    let audit_rows = audit_statement
        .query_map([], |row| {
            Ok((
                row.get::<_, String>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, i64>(2)?,
                row.get::<_, String>(3)?,
            ))
        })
        .map_err(sqlite_error)?;
    let mut saved = BTreeSet::new();
    let mut event_count = 0usize;
    let mut saved_count = 0usize;
    let mut repeat_count = 0usize;
    let mut last_event = None;
    let mut last_time = 0i64;
    let known: HashMap<&str, &str> = records
        .iter()
        .map(|record| (record.id.as_str(), record.source.as_str()))
        .collect();
    for row in audit_rows {
        let (event, capture_id, created_at, detail) = row.map_err(sqlite_error)?;
        if created_at <= 0 || created_at < last_time || !known.contains_key(capture_id.as_str()) {
            return Err(IpcError::blocked(
                "audit_sequence_rejected",
                "审计顺序或记录绑定不可信。",
            ));
        }
        match event.as_str() {
            "capture_saved" if detail == "local_capture" && saved.insert(capture_id.clone()) => {
                saved_count += 1
            }
            "capture_repeat" if detail == "same_idempotency_key" && saved.contains(&capture_id) => {
                repeat_count += 1
            }
            _ => {
                return Err(IpcError::blocked(
                    "audit_contract_rejected",
                    "审计事件不符合冻结合同。",
                ))
            }
        }
        event_count += 1;
        last_time = created_at;
        last_event = Some(event);
    }
    if saved.len() != records.len() || saved_count != records.len() {
        return Err(IpcError::blocked(
            "audit_replay_rejected",
            "记录与审计重放状态不一致。",
        ));
    }
    Ok((
        records,
        AuditSummary {
            event_count,
            saved_count,
            repeat_count,
            last_event,
        },
    ))
}

fn remove_candidate(path: &Path) {
    for candidate in [
        path.to_path_buf(),
        PathBuf::from(format!("{}-journal", path.display())),
        PathBuf::from(format!("{}-wal", path.display())),
        PathBuf::from(format!("{}-shm", path.display())),
    ] {
        let _ = fs::remove_file(candidate);
    }
}

fn capture_impl(path: &Path, request: &CaptureRequest) -> Result<CaptureResponse, IpcError> {
    let database_present = validate_database_path(path)?;
    let mode = match (request.text.as_str(), request.key.as_str()) {
        (PRIMARY_TEXT, PRIMARY_KEY) => "normal",
        (CONFLICT_TEXT, PRIMARY_KEY) => "conflict_probe",
        (FAILURE_TEXT, FAILURE_KEY) => "failure_probe",
        _ => {
            return Err(IpcError::blocked(
                "argument_schema_rejected",
                "仅允许冻结的非敏感文本与 task-local 幂等键。",
            ))
        }
    };

    if database_present {
        let conn = open_read_only(path)?;
        let prior = conn
            .query_row(
                "SELECT content FROM captures WHERE idem_key=?1",
                params![request.key],
                |row| row.get::<_, String>(0),
            )
            .optional()
            .map_err(sqlite_error)?;
        if mode == "conflict_probe" {
            return match prior {
                Some(content) if content != request.text => Err(IpcError::blocked(
                    "idempotency_conflict",
                    "幂等键已绑定其他记录；冲突已阻断，数据库未更改。",
                )),
                _ => Err(IpcError::blocked(
                    "conflict_probe_rejected",
                    "冲突夹具要求先存在冻结主记录。",
                )),
            };
        }
    } else if mode == "conflict_probe" {
        return Err(IpcError::blocked(
            "conflict_probe_rejected",
            "冲突夹具要求先存在冻结主记录。",
        ));
    }

    let now = now_ms()?;
    let parent = path.parent().expect("validated parent");
    let candidate = parent.join(format!(".capture.sqlite.{now}.{}.shadow", std::process::id()));
    remove_candidate(&candidate);
    OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&candidate)
        .map_err(io_error)?;
    if database_present {
        if let Err(error) = fs::copy(path, &candidate) {
            remove_candidate(&candidate);
            return Err(io_error(error));
        }
    }

    let operation = (|| -> Result<(CaptureResponse, bool), IpcError> {
        let mut conn = Connection::open(&candidate).map_err(sqlite_error)?;
        conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE;")
            .map_err(sqlite_error)?;
        if !database_present {
            conn.execute_batch(SCHEMA).map_err(sqlite_error)?;
        } else {
            validate_connection(&conn)?;
        }
        let tx = conn
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(sqlite_error)?;
        let prior = tx
            .query_row(
                "SELECT id, content, created_at_ms FROM captures WHERE idem_key=?1",
                params![request.key],
                |row| {
                    Ok((
                        row.get::<_, String>(0)?,
                        row.get::<_, String>(1)?,
                        row.get::<_, i64>(2)?,
                    ))
                },
            )
            .optional()
            .map_err(sqlite_error)?;
        let (status, record, repeated) = if let Some((id, content, created_at)) = prior {
            if content != request.text {
                return Err(IpcError::blocked(
                    "idempotency_conflict",
                    "幂等键已绑定其他记录；冲突已阻断，数据库未更改。",
                ));
            }
            tx.execute(
                "INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_repeat',?1,?2,'same_idempotency_key')",
                params![id, now as i64],
            )
            .map_err(sqlite_error)?;
            (
                "idempotent_repeat",
                RecordView {
                    id,
                    content,
                    created_at_ms: created_at as u64,
                    source: "local_capture".to_string(),
                    identity: "user_original",
                },
                true,
            )
        } else {
            let id = new_id(now);
            tx.execute(
                "INSERT INTO captures(id,content,created_at_ms,source,idem_key) VALUES(?1,?2,?3,'local_capture',?4)",
                params![id, request.text, now as i64, request.key],
            )
            .map_err(sqlite_error)?;
            tx.execute(
                "INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_saved',?1,?2,'local_capture')",
                params![id, now as i64],
            )
            .map_err(sqlite_error)?;
            if mode == "failure_probe" {
                return Err(IpcError::blocked(
                    "injected_atomic_failure",
                    "受控失败已注入；未显示成功，数据库与页面状态未更改。",
                ));
            }
            (
                "saved",
                RecordView {
                    id,
                    content: request.text.clone(),
                    created_at_ms: now,
                    source: "local_capture".to_string(),
                    identity: "user_original",
                },
                false,
            )
        };
        tx.commit().map_err(sqlite_error)?;
        drop(conn);
        let verified = open_read_only(&candidate)?;
        let (records, audit) = validated_today(&verified)?;
        drop(verified);
        Ok((
            CaptureResponse {
                status,
                record,
                record_count: records.len(),
                audit_event_count: audit.event_count,
            },
            repeated,
        ))
    })();

    match operation {
        Ok((response, repeated)) => {
            if validate_database_object(path)? != database_present {
                remove_candidate(&candidate);
                return Err(IpcError::blocked(
                    "database_object_changed",
                    "数据库最终对象在发布前发生变化；候选未发布。",
                ));
            }
            if let Err(error) = fs::rename(&candidate, path) {
                remove_candidate(&candidate);
                return Err(io_error(error));
            }
            remove_candidate(&candidate);
            eprintln!(
                "ipc_result command=capture_record status={} record_count={} repeated={}",
                response.status, response.record_count, repeated
            );
            Ok(response)
        }
        Err(error) => {
            remove_candidate(&candidate);
            Err(error)
        }
    }
}

fn today_impl(path: &Path) -> Result<TodayResponse, IpcError> {
    let database_present = validate_database_path(path)?;
    if !database_present {
        return Ok(TodayResponse {
            status: "empty",
            records: Vec::new(),
            source: "local_capture",
            ai_status: "disabled",
            audit: AuditSummary {
                event_count: 0,
                saved_count: 0,
                repeat_count: 0,
                last_event: None,
            },
        });
    }
    let conn = open_read_only(path)?;
    let (records, audit) = validated_today(&conn)?;
    eprintln!(
        "ipc_result command=get_today status=loaded record_count={} audit_event_count={}",
        records.len(), audit.event_count
    );
    Ok(TodayResponse {
        status: "loaded",
        records,
        source: "local_capture",
        ai_status: "disabled",
        audit,
    })
}

fn status_impl() -> RuntimeStatusResponse {
    RuntimeStatusResponse {
        status: "restricted_offline",
        offline: true,
        ai_enabled: false,
        renderer_direct_capabilities: Vec::new(),
        ipc_allowlist: IPC_ALLOWLIST.to_vec(),
        unknown_ipc: "deny",
        filesystem: false,
        raw_database: false,
        generic_path_api: false,
        shell: false,
        process_spawn: false,
        network: false,
        vault: false,
        export: false,
        sync: false,
    }
}

#[tauri::command]
fn capture_record(
    request: CaptureRequest,
    state: tauri::State<'_, AppState>,
) -> Result<CaptureResponse, IpcError> {
    let _guard = state.serial.lock().map_err(|_| {
        IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未保存记录。")
    })?;
    capture_impl(&state.db_path, &request)
}

#[tauri::command]
fn get_today(
    request: EmptyRequest,
    state: tauri::State<'_, AppState>,
) -> Result<TodayResponse, IpcError> {
    let _ = request;
    let _guard = state.serial.lock().map_err(|_| {
        IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未读取记录。")
    })?;
    today_impl(&state.db_path)
}

#[tauri::command]
fn runtime_status(request: EmptyRequest) -> RuntimeStatusResponse {
    let _ = request;
    eprintln!("ipc_result command=runtime_status status=restricted_offline");
    status_impl()
}

pub fn run() {
    let raw_path = env::var_os("LIFEOS_P3_104_DB_PATH")
        .unwrap_or_else(|| panic!("LIFEOS_P3_104_DB_PATH is required for the controlled candidate"));
    let db_path = PathBuf::from(raw_path);
    validate_database_path(&db_path).unwrap_or_else(|error| {
        panic!("controlled DB boundary rejected: {}", error.code)
    });
    eprintln!("runtime_start status=restricted_offline db_scope=task_local");
    tauri::Builder::default()
        .manage(AppState {
            db_path,
            serial: Mutex::new(()),
        })
        .invoke_handler(tauri::generate_handler![
            capture_record,
            get_today,
            runtime_status
        ])
        .run(tauri::generate_context!())
        .expect("P3-104 Tauri runtime failed");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture(name: &str) -> (PathBuf, PathBuf) {
        let root = PathBuf::from(format!(
            "/private/tmp/lifeos-p3-104-unit-{name}-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir(&root).unwrap();
        (root.join(DB_NAME), root)
    }

    fn primary() -> CaptureRequest {
        CaptureRequest {
            text: PRIMARY_TEXT.to_string(),
            key: PRIMARY_KEY.to_string(),
        }
    }

    #[test]
    fn lifecycle_saved_repeat_conflict_restart() {
        let (db, root) = fixture("lifecycle");
        let saved = capture_impl(&db, &primary()).unwrap();
        assert_eq!(saved.status, "saved");
        let repeat = capture_impl(&db, &primary()).unwrap();
        assert_eq!(repeat.status, "idempotent_repeat");
        assert_eq!(repeat.record.id, saved.record.id);
        let conflict = capture_impl(
            &db,
            &CaptureRequest {
                text: CONFLICT_TEXT.to_string(),
                key: PRIMARY_KEY.to_string(),
            },
        )
        .unwrap_err();
        assert_eq!(conflict.code, "idempotency_conflict");
        let today = today_impl(&db).unwrap();
        assert_eq!(today.records.len(), 1);
        assert_eq!(today.audit.event_count, 2);
        assert_eq!(today.records[0].identity, "user_original");
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn injected_failure_preserves_database_and_sentinel() {
        let (db, root) = fixture("failure");
        capture_impl(&db, &primary()).unwrap();
        let sentinel = root.join("sentinel.txt");
        fs::write(&sentinel, b"P3-104-SENTINEL").unwrap();
        let before_db = fs::read(&db).unwrap();
        let before_sentinel = fs::read(&sentinel).unwrap();
        let error = capture_impl(
            &db,
            &CaptureRequest {
                text: FAILURE_TEXT.to_string(),
                key: FAILURE_KEY.to_string(),
            },
        )
        .unwrap_err();
        assert_eq!(error.code, "injected_atomic_failure");
        assert_eq!(fs::read(&db).unwrap(), before_db);
        assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel);
        assert_eq!(today_impl(&db).unwrap().records.len(), 1);
        assert_eq!(fs::read_dir(&root).unwrap().count(), 2);
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn path_and_argument_boundaries_fail_closed() {
        let bad = Path::new("/private/tmp/not-p3-104/capture.sqlite");
        assert_eq!(validate_database_path(bad).unwrap_err().code, "path_schema_rejected");
        let (db, root) = fixture("arguments");
        let error = capture_impl(
            &db,
            &CaptureRequest {
                text: "not allowlisted".to_string(),
                key: PRIMARY_KEY.to_string(),
            },
        )
        .unwrap_err();
        assert_eq!(error.code, "argument_schema_rejected");
        assert!(!db.exists());
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn symlink_and_hardlink_boundaries_fail_closed() {
        use std::os::unix::fs::symlink;

        let (db, root) = fixture("links");
        let outside = root.join("outside.txt");
        fs::write(&outside, b"P3-104-OUTSIDE-SENTINEL").unwrap();
        symlink(&outside, &db).unwrap();
        assert_eq!(validate_database_path(&db).unwrap_err().code, "database_type_rejected");
        fs::remove_file(&db).unwrap();
        capture_impl(&db, &primary()).unwrap();
        let hardlink = root.join("hardlink.sqlite");
        fs::hard_link(&db, &hardlink).unwrap();
        assert_eq!(validate_database_path(&db).unwrap_err().code, "database_type_rejected");
        fs::remove_file(hardlink).unwrap();
        fs::remove_dir_all(root).unwrap();

        let target = PathBuf::from(format!("/private/tmp/lifeos-p3-104-unit-link-target-{}", std::process::id()));
        let parent_link = PathBuf::from(format!("/private/tmp/lifeos-p3-104-unit-link-{}", std::process::id()));
        let _ = fs::remove_file(&parent_link);
        let _ = fs::remove_dir_all(&target);
        fs::create_dir(&target).unwrap();
        symlink(&target, &parent_link).unwrap();
        assert_eq!(
            validate_database_path(&parent_link.join(DB_NAME)).unwrap_err().code,
            "path_symlink_rejected"
        );
        fs::remove_file(parent_link).unwrap();
        fs::remove_dir_all(target).unwrap();
    }

    #[test]
    fn dangling_database_and_sidecar_links_fail_closed() {
        use std::os::unix::fs::symlink;

        let (db, root) = fixture("dangling-final");
        let missing_target = root.join("missing.sqlite");
        let sentinel = root.join("sentinel.txt");
        fs::write(&sentinel, b"P3-104-DANGLING-SENTINEL").unwrap();
        let before_sentinel = fs::read(&sentinel).unwrap();
        symlink(&missing_target, &db).unwrap();

        assert_eq!(validate_database_path(&db).unwrap_err().code, "database_type_rejected");
        assert_eq!(capture_impl(&db, &primary()).unwrap_err().code, "database_type_rejected");
        assert_eq!(today_impl(&db).unwrap_err().code, "database_type_rejected");
        assert!(fs::symlink_metadata(&db).unwrap().file_type().is_symlink());
        assert!(!missing_target.exists());
        assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel);
        assert_eq!(fs::read_dir(&root).unwrap().count(), 2);
        fs::remove_dir_all(root).unwrap();

        let (db, root) = fixture("dangling-sidecars");
        capture_impl(&db, &primary()).unwrap();
        let sentinel = root.join("sentinel.txt");
        fs::write(&sentinel, b"P3-104-SIDECAR-SENTINEL").unwrap();
        let before_db = fs::read(&db).unwrap();
        let before_sentinel = fs::read(&sentinel).unwrap();
        for suffix in ["-journal", "-wal", "-shm"] {
            let sidecar = PathBuf::from(format!("{}{}", db.display(), suffix));
            let missing = root.join(format!("missing{suffix}"));
            symlink(&missing, &sidecar).unwrap();
            assert_eq!(today_impl(&db).unwrap_err().code, "database_sidecar_rejected");
            assert_eq!(capture_impl(&db, &primary()).unwrap_err().code, "database_sidecar_rejected");
            assert!(fs::symlink_metadata(&sidecar).unwrap().file_type().is_symlink());
            assert!(!missing.exists());
            fs::remove_file(sidecar).unwrap();
        }
        assert_eq!(fs::read(&db).unwrap(), before_db);
        assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel);
        assert_eq!(today_impl(&db).unwrap().records.len(), 1);
        assert_eq!(fs::read_dir(&root).unwrap().count(), 2);
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn runtime_status_closes_direct_capabilities() {
        let status = status_impl();
        assert!(status.offline);
        assert!(!status.ai_enabled);
        assert!(status.renderer_direct_capabilities.is_empty());
        assert_eq!(status.ipc_allowlist, IPC_ALLOWLIST);
        assert_eq!(status.unknown_ipc, "deny");
        assert!(!status.filesystem && !status.raw_database && !status.generic_path_api);
        assert!(!status.shell && !status.process_spawn && !status.network);
        assert!(!status.vault && !status.export && !status.sync);
    }

    #[test]
    fn tampered_content_and_sidecar_fail_closed() {
        let (db, root) = fixture("tamper");
        capture_impl(&db, &primary()).unwrap();
        let conn = Connection::open(&db).unwrap();
        conn.execute("UPDATE captures SET content='tampered'", []).unwrap();
        drop(conn);
        assert_eq!(today_impl(&db).unwrap_err().code, "record_identity_rejected");
        fs::remove_dir_all(&root).unwrap();

        let (db, root) = fixture("sidecar");
        capture_impl(&db, &primary()).unwrap();
        fs::write(format!("{}-wal", db.display()), b"stale").unwrap();
        assert_eq!(today_impl(&db).unwrap_err().code, "database_sidecar_rejected");
        fs::remove_dir_all(root).unwrap();
    }
}
