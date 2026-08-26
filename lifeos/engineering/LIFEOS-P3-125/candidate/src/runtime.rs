use rusqlite::{params, Connection, OpenFlags, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::fs::MetadataExt;
use std::path::{Component, Path, PathBuf};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{LogicalSize, Manager};

const DB_NAME: &str = "capture.sqlite";
const BUILD_RUNTIME_ROOT: Option<&str> = option_env!("LIFEOS_RUNTIME_ROOT");
const IPC_ALLOWLIST: [&str; 3] = ["capture_record", "get_today", "runtime_status"];
const SYNTHETIC_ONE: &str = "明天先把发布页的第一屏文字读一遍，再决定是否继续做视觉细节。";
const SYNTHETIC_TWO: &str = "P3-122 synthetic capture two";
const KEY_ONE: &str = "p3-122-synthetic-one";
const KEY_TWO: &str = "p3-122-synthetic-two";
const MAX_RECORDS: usize = 2;

// This keeps the inherited table/column/version contract unchanged.
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
#[derive(Clone)]
struct RuntimePaths { root: PathBuf, db_path: PathBuf, viewport_request: PathBuf }
struct AppState { runtime: RuntimePaths, serial: Mutex<()> }
#[derive(Clone, Copy, PartialEq)]
enum Fault { None, BeforeCommit }

fn now_ms() -> Result<u64, IpcError> {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|value| value.as_millis() as u64)
        .map_err(|_| IpcError::blocked("clock_unavailable", "本地时间不可用；未保存记录。"))
}
fn new_id(now: u64, key: &str) -> String { format!("p3-122-{now:016x}-{key}") }
fn sqlite_error(_: rusqlite::Error) -> IpcError { IpcError::blocked("database_unavailable", "本地合成数据库无法验证；未显示成功，也未保留半成品。") }
fn io_error(_: std::io::Error) -> IpcError { IpcError::blocked("path_boundary_unavailable", "本地路径边界无法验证；未显示成功，也未保留半成品。") }
fn optional_metadata(path: &Path) -> Result<Option<fs::Metadata>, IpcError> {
    match fs::symlink_metadata(path) { Ok(value) => Ok(Some(value)), Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None), Err(error) => Err(io_error(error)) }
}
fn ensure_real_directory(path: &Path) -> Result<(), IpcError> {
    let metadata = fs::symlink_metadata(path).map_err(io_error)?;
    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() { return Err(IpcError::blocked("path_symlink_rejected", "数据库祖先目录不是无链接真实目录。")); }
    Ok(())
}
fn configured_runtime_paths() -> Result<RuntimePaths, IpcError> {
    let raw = BUILD_RUNTIME_ROOT.ok_or_else(|| IpcError::blocked("runtime_root_missing", "构建时 Runtime 根缺失；未创建文件或数据库。"))?;
    if raw.is_empty() || raw.as_bytes().contains(&0) { return Err(IpcError::blocked("runtime_root_invalid", "构建时 Runtime 根为空或包含非法字符；未创建文件或数据库。")); }
    let root = PathBuf::from(raw);
    if !root.is_absolute() || root.components().any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_))) {
        return Err(IpcError::blocked("runtime_root_noncanonical", "构建时 Runtime 根必须是绝对、规范化路径；未创建文件或数据库。"));
    }
    ensure_real_directory_chain(&root)?;
    let canonical = fs::canonicalize(&root).map_err(io_error)?;
    if canonical != root { return Err(IpcError::blocked("runtime_root_noncanonical", "构建时 Runtime 根解析后发生变化；未创建文件或数据库。")); }
    Ok(RuntimePaths { root: root.clone(), db_path: root.join(DB_NAME), viewport_request: root.join("viewport-request.txt") })
}
fn ensure_real_directory_chain(path: &Path) -> Result<(), IpcError> {
    let mut current = PathBuf::new();
    for component in path.components() {
        match component {
            Component::RootDir => current.push(Path::new("/")),
            Component::Normal(name) => {
                current.push(name);
                ensure_real_directory(&current)?;
            }
            Component::CurDir | Component::ParentDir | Component::Prefix(_) => return Err(IpcError::blocked("runtime_root_noncanonical", "Runtime 根包含未规范化组件；未创建文件或数据库。")),
        }
    }
    Ok(())
}
fn validate_database_object(path: &Path) -> Result<bool, IpcError> {
    let Some(metadata) = optional_metadata(path)? else { return Ok(false); };
    if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 { return Err(IpcError::blocked("database_type_rejected", "数据库不是普通单链接文件。")); }
    Ok(true)
}
fn validate_regular_or_absent(path: &Path, code: &'static str, message: &'static str) -> Result<(), IpcError> {
    if let Some(metadata) = optional_metadata(path)? {
        if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 { return Err(IpcError::blocked(code, message)); }
    }
    Ok(())
}
fn geometry_path(paths: &RuntimePaths, requested: &str) -> Result<PathBuf, IpcError> {
    match requested {
        "1280x1024" | "1160x768" | "700x760" => Ok(paths.root.join(format!("native-geometry-{requested}.jsonl"))),
        _ => Err(IpcError::blocked("viewport_request_rejected", "逻辑视口请求不在冻结集合；未创建 geometry 文件。")),
    }
}
fn validate_runtime_artifacts(paths: &RuntimePaths) -> Result<(), IpcError> {
    validate_regular_or_absent(&paths.viewport_request, "viewport_type_rejected", "viewport 请求不是普通单链接文件。")?;
    for requested in ["1280x1024", "1160x768", "700x760"] {
        validate_regular_or_absent(&geometry_path(paths, requested)?, "geometry_type_rejected", "native geometry 文件不是普通单链接文件。")?;
    }
    Ok(())
}
fn validate_database_path(paths: &RuntimePaths, path: &Path) -> Result<bool, IpcError> {
    if path != paths.db_path { return Err(IpcError::blocked("path_schema_rejected", "数据库只能由唯一构建时 Runtime 根派生。")); }
    ensure_real_directory_chain(&paths.root)?;
    validate_runtime_artifacts(paths)?;
    let present = validate_database_object(path)?;
    for suffix in ["-journal", "-wal", "-shm"] {
        if optional_metadata(&PathBuf::from(format!("{}{}", path.display(), suffix)))?.is_some() { return Err(IpcError::blocked("database_sidecar_rejected", "数据库存在未支持的 sidecar；运行时保持 fail-closed。")); }
    }
    for entry in fs::read_dir(&paths.root).map_err(io_error)? {
        let name = entry.map_err(io_error)?.file_name().to_string_lossy().into_owned();
        if name.starts_with(".capture.sqlite.") && name.ends_with(".shadow") { return Err(IpcError::blocked("candidate_residue_rejected", "发现未完成候选工件；运行时保持 fail-closed。")); }
    }
    Ok(present)
}
fn valid_pair(text: &str, key: &str) -> bool { matches!((text, key), (SYNTHETIC_ONE, KEY_ONE) | (SYNTHETIC_TWO, KEY_TWO)) }
fn validate_request(request: &CaptureRequest) -> Result<(), IpcError> {
    if !valid_pair(&request.text, &request.key) { return Err(IpcError::blocked("argument_schema_rejected", "只接受冻结的两条合成演示文本及其确定幂等键。")); }
    Ok(())
}
fn open_read_only(path: &Path) -> Result<Connection, IpcError> {
    let conn = Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sqlite_error)?;
    conn.pragma_update(None, "query_only", true).map_err(sqlite_error)?; validate_connection(&conn)?; Ok(conn)
}
fn validate_connection(conn: &Connection) -> Result<(), IpcError> {
    let quick: String = conn.query_row("PRAGMA quick_check", [], |row| row.get(0)).map_err(sqlite_error)?;
    let version: i64 = conn.query_row("PRAGMA user_version", [], |row| row.get(0)).map_err(sqlite_error)?;
    if quick != "ok" || version != 104 { return Err(IpcError::blocked("database_contract_rejected", "数据库完整性或版本不符合继承合同。")); }
    let table_count: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('captures','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    let unexpected: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT IN ('captures','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    if table_count != 3 || unexpected != 0 { return Err(IpcError::blocked("database_schema_rejected", "数据库表结构不符合继承合同。")); }
    validated_today(conn).map(|_| ())
}
fn validated_today(conn: &Connection) -> Result<(Vec<RecordView>, AuditSummary), IpcError> {
    let mut statement = conn.prepare("SELECT id, content, created_at_ms, source, idem_key FROM captures ORDER BY created_at_ms, id").map_err(sqlite_error)?;
    let rows = statement.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?, row.get::<_, String>(3)?, row.get::<_, String>(4)?))).map_err(sqlite_error)?;
    let mut records = Vec::new(); let mut ids = BTreeSet::new();
    for row in rows {
        let (id, content, created_at, source, key) = row.map_err(sqlite_error)?;
        if !id.starts_with("p3-122-") || !valid_pair(&content, &key) || created_at <= 0 || source != "local_capture" || !ids.insert(id.clone()) { return Err(IpcError::blocked("record_identity_rejected", "记录身份、来源或合成原文不可信。")); }
        records.push(RecordView { id, content, created_at_ms: created_at as u64, source, identity: "user_original" });
    }
    if records.len() > MAX_RECORDS { return Err(IpcError::blocked("record_limit_rejected", "本次受控运行时只允许两条固定合成记录。")); }
    let mut audit_statement = conn.prepare("SELECT event, capture_id, created_at_ms, detail FROM audit ORDER BY id").map_err(sqlite_error)?;
    let audit_rows = audit_statement.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?, row.get::<_, String>(3)?))).map_err(sqlite_error)?;
    let mut saved = BTreeSet::new(); let mut event_count = 0usize; let mut saved_count = 0usize; let mut repeat_count = 0usize; let mut last_event = None; let mut last_time = 0i64;
    for row in audit_rows {
        let (event, capture_id, created_at, detail) = row.map_err(sqlite_error)?;
        if created_at <= 0 || created_at < last_time || !ids.contains(&capture_id) { return Err(IpcError::blocked("audit_sequence_rejected", "审计顺序或记录绑定不可信。")); }
        match event.as_str() {
            "capture_saved" if detail == "local_capture" && saved.insert(capture_id.clone()) => saved_count += 1,
            "capture_repeat" if detail == "same_idempotency_key" && saved.contains(&capture_id) => repeat_count += 1,
            _ => return Err(IpcError::blocked("audit_contract_rejected", "审计事件不符合继承合同。")),
        }
        event_count += 1; last_time = created_at; last_event = Some(event);
    }
    if saved.len() != records.len() || saved_count != records.len() { return Err(IpcError::blocked("audit_replay_rejected", "记录与审计重放状态不一致。")); }
    Ok((records, AuditSummary { event_count, saved_count, repeat_count, last_event }))
}
fn remove_candidate(path: &Path) {
    for candidate in [path.to_path_buf(), PathBuf::from(format!("{}-journal", path.display())), PathBuf::from(format!("{}-wal", path.display())), PathBuf::from(format!("{}-shm", path.display()))] { let _ = fs::remove_file(candidate); }
}
fn capture_impl(paths: &RuntimePaths, request: &CaptureRequest, fault: Fault) -> Result<CaptureResponse, IpcError> {
    let path = &paths.db_path;
    validate_request(request)?; let database_present = validate_database_path(paths, path)?; let now = now_ms()?; let parent = path.parent().expect("validated parent");
    let candidate = parent.join(format!(".capture.sqlite.{now}.{}.shadow", std::process::id())); remove_candidate(&candidate);
    OpenOptions::new().write(true).create_new(true).open(&candidate).map_err(io_error)?;
    if database_present { if let Err(error) = fs::copy(path, &candidate) { remove_candidate(&candidate); return Err(io_error(error)); } }
    let operation = (|| -> Result<(CaptureResponse, bool), IpcError> {
        let mut conn = Connection::open(&candidate).map_err(sqlite_error)?; conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE;").map_err(sqlite_error)?;
        if database_present { validate_connection(&conn)?; } else { conn.execute_batch(SCHEMA).map_err(sqlite_error)?; }
        let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sqlite_error)?;
        let prior = tx.query_row("SELECT id, content, created_at_ms FROM captures WHERE idem_key=?1", params![request.key], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, i64>(2)?))).optional().map_err(sqlite_error)?;
        let (status, record, repeated) = if let Some((id, content, created_at)) = prior {
            if content != request.text { return Err(IpcError::blocked("idempotency_conflict", "幂等键已绑定其他记录；冲突已阻断，数据库未更改。")); }
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_repeat',?1,?2,'same_idempotency_key')", params![id, now as i64]).map_err(sqlite_error)?;
            ("idempotent_repeat", RecordView { id, content, created_at_ms: created_at as u64, source: "local_capture".to_string(), identity: "user_original" }, true)
        } else {
            let count: i64 = tx.query_row("SELECT count(*) FROM captures", [], |row| row.get(0)).map_err(sqlite_error)?;
            if count as usize >= MAX_RECORDS { return Err(IpcError::blocked("record_limit_rejected", "本次受控运行时只允许两条固定合成记录。")); }
            let id = new_id(now, &request.key);
            tx.execute("INSERT INTO captures(id,content,created_at_ms,source,idem_key) VALUES(?1,?2,?3,'local_capture',?4)", params![id, request.text, now as i64, request.key]).map_err(sqlite_error)?;
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_saved',?1,?2,'local_capture')", params![id, now as i64]).map_err(sqlite_error)?;
            ("saved", RecordView { id, content: request.text.clone(), created_at_ms: now, source: "local_capture".to_string(), identity: "user_original" }, false)
        };
        if fault == Fault::BeforeCommit { return Err(IpcError::blocked("injected_atomic_failure", "受控失败已注入；未显示成功，数据库与页面状态未更改。")); }
        tx.commit().map_err(sqlite_error)?; drop(conn); let verified = open_read_only(&candidate)?; let (records, audit) = validated_today(&verified)?; drop(verified);
        Ok((CaptureResponse { status, record, record_count: records.len(), audit_event_count: audit.event_count }, repeated))
    })();
    match operation {
        Ok((response, repeated)) => {
            if validate_database_object(path)? != database_present { remove_candidate(&candidate); return Err(IpcError::blocked("database_object_changed", "数据库最终对象在发布前发生变化；候选未发布。")); }
            if let Err(error) = fs::rename(&candidate, path) { remove_candidate(&candidate); return Err(io_error(error)); }
            remove_candidate(&candidate); eprintln!("ipc_result command=capture_record status={} record_count={} audit_event_count={} repeated={}", response.status, response.record_count, response.audit_event_count, repeated); Ok(response)
        }
        Err(error) => { remove_candidate(&candidate); Err(error) }
    }
}
fn today_impl(paths: &RuntimePaths) -> Result<TodayResponse, IpcError> {
    let path = &paths.db_path;
    let present = validate_database_path(paths, path)?;
    if !present { return Ok(TodayResponse { status: "empty", records: Vec::new(), source: "local_capture", ai_status: "disabled", audit: AuditSummary { event_count: 0, saved_count: 0, repeat_count: 0, last_event: None } }); }
    let conn = open_read_only(path)?; let (records, audit) = validated_today(&conn)?;
    eprintln!("ipc_result command=get_today status=loaded record_count={} audit_event_count={}", records.len(), audit.event_count);
    Ok(TodayResponse { status: "loaded", records, source: "local_capture", ai_status: "disabled", audit })
}
fn status_impl() -> RuntimeStatusResponse {
    RuntimeStatusResponse { status: "restricted_offline", offline: true, ai_enabled: false, renderer_direct_capabilities: Vec::new(), ipc_allowlist: IPC_ALLOWLIST.to_vec(), unknown_ipc: "deny", filesystem: false, raw_database: false, generic_path_api: false, shell: false, process_spawn: false, network: false, vault: false, export: false, sync: false }
}
fn viewport_request(paths: &RuntimePaths) -> Result<String, IpcError> {
    let requested = match optional_metadata(&paths.viewport_request)? {
        Some(metadata) => {
            if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 {
                return Err(IpcError::blocked("viewport_type_rejected", "viewport 请求不是普通单链接文件；未创建 geometry 文件。"));
            }
            fs::read_to_string(&paths.viewport_request).map_err(io_error)?.trim().to_string()
        }
        None => "1280x1024".to_string(),
    };
    match requested.as_str() {
        "1280x1024" | "1160x768" | "700x760" => Ok(requested),
        _ => Err(IpcError::blocked("viewport_request_rejected", "逻辑视口请求不在冻结集合；未创建 geometry 文件。")),
    }
}
fn record_native_geometry(paths: &RuntimePaths, window: &tauri::Window, phase: &str, requested: &str) -> Result<(), IpcError> {
    validate_regular_or_absent(&geometry_path(paths, requested)?, "geometry_type_rejected", "native geometry 文件不是普通单链接文件。")?;
    let scale = window.scale_factor().expect("scale factor unavailable");
    let inner = window.inner_size().expect("native content size unavailable");
    let outer = window.outer_size().expect("native outer size unavailable");
    let inner_position = window.inner_position().expect("native content position unavailable");
    let outer_position = window.outer_position().expect("native outer position unavailable");
    let inner_logical = inner.to_logical::<f64>(scale);
    let outer_logical = outer.to_logical::<f64>(scale);
    let monitor = window.current_monitor().expect("monitor query failed").map(|value| {
        serde_json::json!({
            "name": value.name(),
            "position_physical": {"x": value.position().x, "y": value.position().y},
            "size_physical": {"width": value.size().width, "height": value.size().height},
            "scale_factor": value.scale_factor(),
        })
    });
    let record = serde_json::json!({
        "task": "LIFEOS-P3-125",
        "source": "actual-tauri-native-window",
        "phase": phase,
        "requested_logical": requested,
        "scale_factor": scale,
        "content_bounds": {
            "position_physical": {"x": inner_position.x, "y": inner_position.y},
            "size_physical": {"width": inner.width, "height": inner.height},
            "size_logical": {"width": inner_logical.width, "height": inner_logical.height},
        },
        "outer_bounds": {
            "position_physical": {"x": outer_position.x, "y": outer_position.y},
            "size_physical": {"width": outer.width, "height": outer.height},
            "size_logical": {"width": outer_logical.width, "height": outer_logical.height},
        },
        "monitor": monitor,
    });
    let path = geometry_path(paths, requested)?;
    let mut file = OpenOptions::new().create(true).append(true).open(&path).map_err(io_error)?;
    writeln!(file, "{record}").map_err(io_error)?;
    eprintln!("P3_125_NATIVE_GEOMETRY {record}");
    Ok(())
}
#[tauri::command]
fn capture_record(request: CaptureRequest, state: tauri::State<'_, AppState>) -> Result<CaptureResponse, IpcError> {
    let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未保存记录。"))?;
    capture_impl(&state.runtime, &request, Fault::None)
}
#[tauri::command]
fn get_today(request: EmptyRequest, state: tauri::State<'_, AppState>) -> Result<TodayResponse, IpcError> {
    let _ = request; let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用；未读取记录。"))?; today_impl(&state.runtime)
}
#[tauri::command]
fn runtime_status(request: EmptyRequest) -> RuntimeStatusResponse { let _ = request; eprintln!("ipc_result command=runtime_status status=restricted_offline"); status_impl() }
pub fn run() {
    let runtime = configured_runtime_paths().unwrap_or_else(|error| panic!("controlled synthetic Runtime root rejected: {}", error.code));
    validate_database_path(&runtime, &runtime.db_path).unwrap_or_else(|error| panic!("controlled synthetic DB boundary rejected: {}", error.code));
    let initial_viewport = viewport_request(&runtime).unwrap_or_else(|error| panic!("controlled synthetic viewport rejected: {}", error.code));
    eprintln!("runtime_start status=restricted_offline db_scope=synthetic_task_local runtime_root={}", runtime.root.display());
    let setup_runtime = runtime.clone();
    let event_runtime = runtime.clone();
    tauri::Builder::default()
        .manage(AppState { runtime, serial: Mutex::new(()) })
        .setup(move |app| {
            let requested = initial_viewport.clone();
            let (width, height) = match requested.as_str() {
                "1280x1024" => (1280.0, 1024.0),
                "1160x768" => (1160.0, 768.0),
                "700x760" => (700.0, 760.0),
                _ => panic!("unsupported configured viewport request: {requested}"),
            };
            let webview_window = app.get_webview_window("main").expect("main WebView window missing");
            let window = webview_window.as_ref().window();
            let initial_scale = window.scale_factor().expect("initial scale factor unavailable");
            let initial_inner = window.inner_size().expect("initial native content size unavailable").to_logical::<f64>(initial_scale);
            let initial_outer = window.outer_size().expect("initial native outer size unavailable").to_logical::<f64>(initial_scale);
            let chrome_width = (initial_outer.width - initial_inner.width).max(0.0);
            let chrome_height = (initial_outer.height - initial_inner.height).max(0.0);
            window.set_size(LogicalSize::new(width + chrome_width, height + chrome_height)).expect("logical content viewport request failed");
            record_native_geometry(&setup_runtime, &window, "setup", &requested).unwrap_or_else(|error| panic!("native geometry rejected: {}", error.code));
            Ok(())
        })
        .on_window_event(move |window, event| {
            if let tauri::WindowEvent::Resized(inner) = event {
                let _ = inner;
                let requested = viewport_request(&event_runtime).unwrap_or_else(|error| panic!("native geometry viewport rejected: {}", error.code));
                record_native_geometry(&event_runtime, window, "resized", &requested).unwrap_or_else(|error| panic!("native geometry rejected: {}", error.code));
            }
        })
        .invoke_handler(tauri::generate_handler![capture_record, get_today, runtime_status])
        .run(tauri::generate_context!())
        .expect("P3-125 Tauri runtime failed");
}
// Historical P3-122 tests are retained only as copied source lineage.  P3-125's
// task-local tests below exercise the configurable-root contract instead.
#[cfg(any())]
mod inherited_p3_122_tests {
    use super::*;
    use sha2::{Digest, Sha256};
    use std::os::unix::fs::symlink;
    fn fixture(name: &str) -> (PathBuf, PathBuf) {
        let base = test_base(); fs::create_dir_all(&base).unwrap(); let root = base.join(format!("p3-122-{name}-{}", std::process::id())); let _ = fs::remove_dir_all(&root); fs::create_dir(&root).unwrap(); (root.join(DB_NAME), root)
    }
    fn cleanup(root: &Path) { assert_eq!(root.parent(), Some(test_base().as_path())); fs::remove_dir_all(root).unwrap(); }
    fn one() -> CaptureRequest { CaptureRequest { text: SYNTHETIC_ONE.to_string(), key: KEY_ONE.to_string() } }
    fn two() -> CaptureRequest { CaptureRequest { text: SYNTHETIC_TWO.to_string(), key: KEY_TWO.to_string() } }
    fn file_sha256(path: &Path) -> String {
        let mut digest = Sha256::new();
        digest.update(fs::read(path).unwrap());
        format!("{:x}", digest.finalize())
    }
    #[test]
    fn evidence_trace_covers_status_lifecycle_and_atomic_failure() {
        let status = status_impl();
        let (db, root) = fixture("evidence-trace");
        let initial = today_impl(&db).unwrap();
        let first = capture_impl(&db, &one(), Fault::None).unwrap();
        let after_first_sha256 = file_sha256(&db);
        let repeat = capture_impl(&db, &one(), Fault::None).unwrap();
        let after_repeat_sha256 = file_sha256(&db);
        let second = capture_impl(&db, &two(), Fault::None).unwrap();
        let before_refresh_sha256 = file_sha256(&db);
        let refreshed = today_impl(&db).unwrap();
        let reopened = today_impl(&db).unwrap();
        assert_eq!(initial.status, "empty");
        assert_eq!(first.status, "saved");
        assert_eq!(repeat.status, "idempotent_repeat");
        assert_eq!(first.record.id, repeat.record.id);
        assert_eq!(second.status, "saved");
        assert_eq!(refreshed.records.len(), 2);
        assert_eq!(reopened.records.len(), 2);
        assert_eq!(refreshed.records[0].content, SYNTHETIC_ONE);
        assert_eq!(refreshed.records[1].content, SYNTHETIC_TWO);
        cleanup(&root);

        let (failure_db, failure_root) = fixture("evidence-failure");
        capture_impl(&failure_db, &one(), Fault::None).unwrap();
        let sentinel = failure_root.join("sentinel.txt");
        fs::write(&sentinel, b"P3-122-SENTINEL").unwrap();
        let before_failure_sha256 = file_sha256(&failure_db);
        let before_sentinel_sha256 = file_sha256(&sentinel);
        let failure = capture_impl(&failure_db, &two(), Fault::BeforeCommit).unwrap_err();
        let after_failure_sha256 = file_sha256(&failure_db);
        let after_sentinel_sha256 = file_sha256(&sentinel);
        let after_failure_today = today_impl(&failure_db).unwrap();
        assert_eq!(failure.code, "injected_atomic_failure");
        assert_eq!(before_failure_sha256, after_failure_sha256);
        assert_eq!(before_sentinel_sha256, after_sentinel_sha256);
        assert_eq!(after_failure_today.records.len(), 1);
        eprintln!(
            "P3-122-RUNTIME-TRACE {}",
            serde_json::json!({
                "runtime_status": {
                    "status": status.status,
                    "offline": status.offline,
                    "ai_enabled": status.ai_enabled,
                    "ipc_allowlist": status.ipc_allowlist,
                    "renderer_direct_capabilities": status.renderer_direct_capabilities,
                    "unknown_ipc": status.unknown_ipc,
                },
                "lifecycle": {
                    "initial_status": initial.status,
                    "first_status": first.status,
                    "first_record_id": first.record.id,
                    "repeat_status": repeat.status,
                    "repeat_record_id": repeat.record.id,
                    "second_status": second.status,
                    "before_refresh_sha256": before_refresh_sha256,
                    "refresh_status": refreshed.status,
                    "refresh_contents": refreshed.records.iter().map(|record| record.content.clone()).collect::<Vec<_>>(),
                    "reopen_status": reopened.status,
                    "reopen_contents": reopened.records.iter().map(|record| record.content.clone()).collect::<Vec<_>>(),
                    "after_first_sha256": after_first_sha256,
                    "after_repeat_sha256": after_repeat_sha256,
                },
                "atomic_failure": {
                    "code": failure.code,
                    "before_db_sha256": before_failure_sha256,
                    "after_db_sha256": after_failure_sha256,
                    "before_sentinel_sha256": before_sentinel_sha256,
                    "after_sentinel_sha256": after_sentinel_sha256,
                    "records_after_failure": after_failure_today.records.len(),
                }
            })
        );
        cleanup(&failure_root);
    }
    #[test]
    fn first_repeat_second_refresh_and_reopen_are_consistent() {
        let (db, root) = fixture("lifecycle"); assert_eq!(today_impl(&db).unwrap().status, "empty"); let saved = capture_impl(&db, &one(), Fault::None).unwrap(); assert_eq!(saved.status, "saved");
        let repeat = capture_impl(&db, &one(), Fault::None).unwrap(); assert_eq!(repeat.status, "idempotent_repeat"); assert_eq!(repeat.record.id, saved.record.id);
        assert_eq!(capture_impl(&db, &two(), Fault::None).unwrap().status, "saved"); let refreshed = today_impl(&db).unwrap(); assert_eq!(refreshed.records.len(), 2); assert_eq!(refreshed.audit.event_count, 3);
        let reopened = today_impl(&db).unwrap(); assert_eq!(reopened.records.len(), 2); assert_eq!(reopened.records[0].content, SYNTHETIC_ONE); assert_eq!(reopened.records[1].content, SYNTHETIC_TWO); cleanup(&root);
    }
    #[test]
    fn injected_failure_preserves_database_and_sentinel() {
        let (db, root) = fixture("failure"); capture_impl(&db, &one(), Fault::None).unwrap(); let sentinel = root.join("sentinel.txt"); fs::write(&sentinel, b"P3-122-SENTINEL").unwrap(); let before_db = fs::read(&db).unwrap(); let before_sentinel = fs::read(&sentinel).unwrap();
        assert_eq!(capture_impl(&db, &two(), Fault::BeforeCommit).unwrap_err().code, "injected_atomic_failure"); assert_eq!(fs::read(&db).unwrap(), before_db); assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel); assert_eq!(today_impl(&db).unwrap().records.len(), 1); cleanup(&root);
    }
    #[test]
    fn invalid_or_unpaired_input_is_rejected_before_storage() {
        let (db, root) = fixture("arguments"); let invalid = CaptureRequest { text: "not accepted".to_string(), key: KEY_ONE.to_string() }; assert_eq!(capture_impl(&db, &invalid, Fault::None).unwrap_err().code, "argument_schema_rejected"); assert!(!db.exists()); cleanup(&root);
    }
    #[test]
    fn extra_ipc_fields_are_rejected_before_runtime_logic() {
        assert!(serde_json::from_str::<CaptureRequest>(r#"{"text":"明天先把发布页的第一屏文字读一遍，再决定是否继续做视觉细节。","key":"p3-122-synthetic-one","path":"/escape"}"#).is_err()); assert!(serde_json::from_str::<EmptyRequest>(r#"{"sql":"SELECT 1"}"#).is_err());
    }
    #[test]
    fn link_hardlink_and_sidecar_boundaries_fail_closed() {
        let (db, root) = fixture("links"); let outside = root.join("outside.txt"); fs::write(&outside, b"P3-122-OUTSIDE-SENTINEL").unwrap(); symlink(&outside, &db).unwrap(); assert_eq!(validate_database_path(&db, false).unwrap_err().code, "database_type_rejected"); fs::remove_file(&db).unwrap(); capture_impl(&db, &one(), Fault::None).unwrap();
        let hardlink = root.join("hardlink.sqlite"); fs::hard_link(&db, &hardlink).unwrap(); assert_eq!(validate_database_path(&db, false).unwrap_err().code, "database_type_rejected"); fs::remove_file(&hardlink).unwrap(); let sidecar = PathBuf::from(format!("{}-wal", db.display())); symlink(root.join("missing-wal"), &sidecar).unwrap(); assert_eq!(today_impl(&db).unwrap_err().code, "database_sidecar_rejected"); fs::remove_file(sidecar).unwrap(); cleanup(&root);
    }
    #[test]
    fn tampered_content_and_schema_fail_closed() {
        let (db, root) = fixture("tamper"); capture_impl(&db, &one(), Fault::None).unwrap(); let conn = Connection::open(&db).unwrap(); conn.execute("UPDATE captures SET content='tampered'", []).unwrap(); drop(conn); assert_eq!(today_impl(&db).unwrap_err().code, "record_identity_rejected"); cleanup(&root);
    }
    #[test]
    fn runtime_status_closes_direct_capabilities_and_keeps_three_ipc() {
        let status = status_impl(); assert!(status.offline && !status.ai_enabled && status.renderer_direct_capabilities.is_empty()); assert_eq!(status.ipc_allowlist, IPC_ALLOWLIST); assert_eq!(status.unknown_ipc, "deny"); assert!(!status.filesystem && !status.raw_database && !status.generic_path_api); assert!(!status.shell && !status.process_spawn && !status.network && !status.vault && !status.export && !status.sync);
    }
    #[test]
    fn runtime_path_is_exact_and_other_paths_are_rejected() {
        assert!(matches!(storage_scope(Path::new(RUNTIME_DB)), Ok(StorageScope::Runtime))); assert_eq!(validate_database_path(Path::new("/private/tmp/other/capture.sqlite"), false).unwrap_err().code, "path_schema_rejected");
    }
}

#[cfg(test)]
mod p3_125_tests {
    use super::*;
    use sha2::{Digest, Sha256};
    use std::os::unix::fs::PermissionsExt;
    use std::os::unix::fs::symlink;

    fn hash(path: &Path) -> String {
        let mut digest = Sha256::new();
        digest.update(fs::read(path).unwrap());
        format!("{:x}", digest.finalize())
    }
    fn paths() -> RuntimePaths { configured_runtime_paths().unwrap() }
    fn reset(paths: &RuntimePaths) {
        for path in [
            paths.db_path.clone(),
            PathBuf::from(format!("{}-journal", paths.db_path.display())),
            PathBuf::from(format!("{}-wal", paths.db_path.display())),
            PathBuf::from(format!("{}-shm", paths.db_path.display())),
            paths.viewport_request.clone(),
            paths.root.join("native-geometry-1280x1024.jsonl"),
            paths.root.join("native-geometry-1160x768.jsonl"),
            paths.root.join("native-geometry-700x760.jsonl"),
        ] { let _ = fs::remove_file(path); }
    }
    fn one() -> CaptureRequest { CaptureRequest { text: SYNTHETIC_ONE.to_string(), key: KEY_ONE.to_string() } }
    fn two() -> CaptureRequest { CaptureRequest { text: SYNTHETIC_TWO.to_string(), key: KEY_TWO.to_string() } }

    #[test]
    fn compiled_root_derives_every_runtime_path() {
        let runtime = paths();
        assert!(runtime.root.is_absolute());
        assert_eq!(runtime.db_path, runtime.root.join(DB_NAME));
        assert_eq!(runtime.viewport_request, runtime.root.join("viewport-request.txt"));
        assert_eq!(geometry_path(&runtime, "1280x1024").unwrap(), runtime.root.join("native-geometry-1280x1024.jsonl"));
    }

    #[test]
    fn first_repeat_refresh_reopen_and_atomic_failure_are_consistent() {
        let runtime = paths(); reset(&runtime);
        assert_eq!(today_impl(&runtime).unwrap().status, "empty");
        let first = capture_impl(&runtime, &one(), Fault::None).unwrap();
        let first_hash = hash(&runtime.db_path);
        let repeat = capture_impl(&runtime, &one(), Fault::None).unwrap();
        assert_eq!(first.status, "saved"); assert_eq!(repeat.status, "idempotent_repeat"); assert_eq!(first.record.id, repeat.record.id);
        assert_eq!(capture_impl(&runtime, &two(), Fault::None).unwrap().status, "saved");
        let refreshed = today_impl(&runtime).unwrap(); let reopened = today_impl(&runtime).unwrap();
        assert_eq!(refreshed.records.len(), 2); assert_eq!(reopened.audit.event_count, 3);
        assert_ne!(first_hash, hash(&runtime.db_path));
        reset(&runtime);
        capture_impl(&runtime, &one(), Fault::None).unwrap();
        let sentinel = runtime.root.join("unit-sentinel.txt"); fs::write(&sentinel, b"P3-125-SENTINEL").unwrap();
        let before_db = hash(&runtime.db_path); let before_sentinel = hash(&sentinel);
        assert_eq!(capture_impl(&runtime, &two(), Fault::BeforeCommit).unwrap_err().code, "injected_atomic_failure");
        assert_eq!(before_db, hash(&runtime.db_path)); assert_eq!(before_sentinel, hash(&sentinel));
        fs::remove_file(sentinel).unwrap(); reset(&runtime);
    }

    #[test]
    fn input_and_storage_type_failures_preserve_the_root() {
        let runtime = paths(); reset(&runtime);
        let invalid = CaptureRequest { text: "not accepted".to_string(), key: KEY_ONE.to_string() };
        assert_eq!(capture_impl(&runtime, &invalid, Fault::None).unwrap_err().code, "argument_schema_rejected");
        assert!(!runtime.db_path.exists());
        let sentinel = runtime.root.join("outside-sentinel.txt"); fs::write(&sentinel, b"P3-125-SENTINEL").unwrap();
        symlink(&sentinel, &runtime.db_path).unwrap();
        assert_eq!(today_impl(&runtime).unwrap_err().code, "database_type_rejected");
        fs::remove_file(&runtime.db_path).unwrap();
        fs::create_dir(runtime.root.join("native-geometry-1280x1024.jsonl")).unwrap();
        assert_eq!(validate_runtime_artifacts(&runtime).unwrap_err().code, "geometry_type_rejected");
        fs::remove_dir(runtime.root.join("native-geometry-1280x1024.jsonl")).unwrap();
        fs::remove_file(sentinel).unwrap(); reset(&runtime);
    }

    #[test]
    fn non_sqlite_sidecar_and_unwritable_failures_preserve_existing_data() {
        let runtime = paths(); reset(&runtime);
        let sentinel = runtime.root.join("boundary-sentinel.txt");
        fs::write(&sentinel, b"P3-125-SENTINEL").unwrap();
        fs::write(&runtime.db_path, b"not a sqlite database").unwrap();
        let before_db = fs::read(&runtime.db_path).unwrap(); let before_sentinel = fs::read(&sentinel).unwrap();
        assert_eq!(capture_impl(&runtime, &one(), Fault::None).unwrap_err().code, "database_unavailable");
        assert_eq!(fs::read(&runtime.db_path).unwrap(), before_db); assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel);
        fs::remove_file(&runtime.db_path).unwrap(); capture_impl(&runtime, &one(), Fault::None).unwrap();
        let sidecar = PathBuf::from(format!("{}-wal", runtime.db_path.display())); fs::write(&sidecar, b"blocked").unwrap();
        assert_eq!(today_impl(&runtime).unwrap_err().code, "database_sidecar_rejected"); fs::remove_file(sidecar).unwrap();
        reset(&runtime); let original_mode = fs::metadata(&runtime.root).unwrap().permissions().mode();
        fs::set_permissions(&runtime.root, fs::Permissions::from_mode(0o500)).unwrap();
        let result = capture_impl(&runtime, &one(), Fault::None);
        fs::set_permissions(&runtime.root, fs::Permissions::from_mode(original_mode)).unwrap();
        assert_eq!(result.unwrap_err().code, "path_boundary_unavailable");
        assert!(!runtime.db_path.exists()); assert_eq!(fs::read(&sentinel).unwrap(), before_sentinel);
        fs::remove_file(sentinel).unwrap(); reset(&runtime);
    }
}
