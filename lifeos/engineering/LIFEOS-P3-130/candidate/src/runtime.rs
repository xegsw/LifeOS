use rusqlite::{params, Connection, OpenFlags, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::fs::MetadataExt;
use std::path::{Component, Path, PathBuf};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{LogicalSize, Manager};

const DB_NAME: &str = "capture.sqlite";
const BUILD_RUNTIME_ROOT: Option<&str> = option_env!("LIFEOS_RUNTIME_ROOT");
const IPC_ALLOWLIST: [&str; 5] = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery"];
const CAPTURE_TEXT: &str = "整理 LifeOS Context Recovery 合成验收记录。";
const CAPTURE_KEY: &str = "p3-130-capture-001";
const CONFIRM_KEY: &str = "p3-130-confirm-001";
const PERSON_ID: &str = "person:synthetic-owner";
const PROJECT_ID: &str = "synthetic-lifeos-product";
const CONTEXT_ID: &str = "ctx:project:synthetic-lifeos-product";
const SOURCE_ID: &str = "SRC-SYN-WORK-001";
const ARTIFACT_VERSION: &str = "ART-SYN-CONTEXT-RECOVERY-001@v1";

// This is deliberately a Project-backed link model, not a generic Context or Memory table.
const SCHEMA: &str = r#"
PRAGMA journal_mode = DELETE;
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS captures (
  id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at_ms INTEGER NOT NULL,
  source TEXT NOT NULL CHECK(source = 'local_capture'), source_id TEXT NOT NULL,
  artifact_version TEXT NOT NULL, idem_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, person_id TEXT NOT NULL, title TEXT NOT NULL, source_id TEXT NOT NULL,
  artifact_version TEXT NOT NULL, source_available INTEGER NOT NULL, generation_current INTEGER NOT NULL,
  tombstoned INTEGER NOT NULL, authorized INTEGER NOT NULL, evidence_ready INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS capture_project_links (
  capture_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, context_id TEXT NOT NULL,
  link_status TEXT NOT NULL CHECK(link_status IN ('candidate','confirmed','rejected')),
  source_id TEXT NOT NULL, artifact_version TEXT NOT NULL,
  FOREIGN KEY(capture_id) REFERENCES captures(id), FOREIGN KEY(project_id) REFERENCES projects(id)
);
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT, capture_id TEXT NOT NULL, context_id TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('confirm','reject')), idem_key TEXT NOT NULL UNIQUE,
  created_at_ms INTEGER NOT NULL, FOREIGN KEY(capture_id) REFERENCES captures(id)
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
  capture_id TEXT NOT NULL, created_at_ms INTEGER NOT NULL, detail TEXT NOT NULL,
  FOREIGN KEY(capture_id) REFERENCES captures(id)
);
PRAGMA user_version = 130;
"#;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CaptureRequest { text: String, key: String }
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EmptyRequest {}
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct ConfirmRequest { capture_id: String, context_id: String, decision: Decision, idempotency_key: String }
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct ContextRequest { context_id: String }
#[derive(Debug, Deserialize, Serialize, Clone, Copy, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum Decision { Confirm, Reject }
impl Decision { fn as_str(self) -> &'static str { match self { Self::Confirm => "confirm", Self::Reject => "reject" } } }

#[derive(Debug, Serialize, Clone)]
struct RecordView { id: String, content: String, created_at_ms: u64, source: String, source_id: String, artifact_version: String, identity: &'static str }
#[derive(Debug, Serialize)]
struct AuditSummary { event_count: usize, saved_count: usize, repeat_count: usize, candidate_link_count: usize, confirmation_count: usize }
#[derive(Debug, Serialize, Clone)]
struct ContextRecovery {
    context_id: String, project_id: String, person_id: String, project_title: String, state: String,
    reliable_suggestion: bool, evidence_gap: Option<String>, source_ref: String, artifact_ref: String,
    typed_link_ref: Option<String>, feedback_ref: Option<String>, audit_ref: Option<String>, memory_copy_created: bool,
}
#[derive(Debug, Serialize)]
struct CaptureResponse { status: String, record: RecordView, record_count: usize, audit_event_count: usize, context_id: String, link_status: String }
#[derive(Debug, Serialize)]
struct ConfirmResponse { status: String, capture_id: String, context_id: String, decision: String, feedback_count: usize, audit_event_count: usize, recovery: ContextRecovery }
#[derive(Debug, Serialize)]
struct TodayResponse { status: &'static str, records: Vec<RecordView>, source: &'static str, ai_status: &'static str, audit: AuditSummary, context_recovery: ContextRecovery }
#[derive(Debug, Serialize)]
struct RuntimeStatusResponse {
    status: &'static str, offline: bool, ai_enabled: bool, renderer_direct_capabilities: Vec<&'static str>,
    ipc_allowlist: Vec<&'static str>, unknown_ipc: &'static str, filesystem: bool, raw_database: bool,
    generic_path_api: bool, shell: bool, process_spawn: bool, network: bool, vault: bool, export: bool, sync: bool,
    context_recovery: &'static str, memory_duplicate_original: bool,
}
#[derive(Debug, Serialize)]
struct IpcError { status: &'static str, code: &'static str, message: &'static str }
impl IpcError { fn blocked(code: &'static str, message: &'static str) -> Self { eprintln!("ipc_result status=blocked code={code}"); Self { status: "blocked", code, message } } }

#[derive(Clone)]
struct RuntimePaths { root: PathBuf, db_path: PathBuf, viewport_request: PathBuf }
struct AppState { runtime: RuntimePaths, serial: Mutex<()> }
#[derive(Clone, Copy, PartialEq)]
enum Fault { None, BeforeCommit }

fn now_ms() -> Result<u64, IpcError> { SystemTime::now().duration_since(UNIX_EPOCH).map(|value| value.as_millis() as u64).map_err(|_| IpcError::blocked("clock_unavailable", "本地时间不可用；未写入合成记录。")) }
fn sqlite_error(_: rusqlite::Error) -> IpcError { IpcError::blocked("database_unavailable", "本地合成数据库无法验证；未显示成功，也未保留半成品。") }
fn io_error(_: std::io::Error) -> IpcError { IpcError::blocked("path_boundary_unavailable", "本地路径边界无法验证；未显示成功，也未保留半成品。") }
fn optional_metadata(path: &Path) -> Result<Option<fs::Metadata>, IpcError> { match fs::symlink_metadata(path) { Ok(value) => Ok(Some(value)), Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None), Err(error) => Err(io_error(error)) } }
fn ensure_real_directory(path: &Path) -> Result<(), IpcError> { let metadata = fs::symlink_metadata(path).map_err(io_error)?; if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() { return Err(IpcError::blocked("path_symlink_rejected", "Runtime 根的祖先目录不是无链接真实目录。")); } Ok(()) }
fn ensure_real_directory_chain(path: &Path) -> Result<(), IpcError> {
    let mut current = PathBuf::new();
    for component in path.components() { match component { Component::RootDir => current.push(Path::new("/")), Component::Normal(name) => { current.push(name); ensure_real_directory(&current)?; }, Component::CurDir | Component::ParentDir | Component::Prefix(_) => return Err(IpcError::blocked("runtime_root_noncanonical", "Runtime 根包含未规范化组件。")), } }
    Ok(())
}
fn configured_runtime_paths() -> Result<RuntimePaths, IpcError> {
    let raw = BUILD_RUNTIME_ROOT.ok_or_else(|| IpcError::blocked("runtime_root_missing", "构建时 Runtime 根缺失；未创建文件或数据库。"))?;
    let root = PathBuf::from(raw);
    if raw.is_empty() || raw.as_bytes().contains(&0) || !root.is_absolute() || root.components().any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_))) { return Err(IpcError::blocked("runtime_root_noncanonical", "构建时 Runtime 根必须是绝对、规范化路径。")); }
    ensure_real_directory_chain(&root)?;
    if fs::canonicalize(&root).map_err(io_error)? != root { return Err(IpcError::blocked("runtime_root_noncanonical", "构建时 Runtime 根解析后发生变化。")); }
    Ok(RuntimePaths { root: root.clone(), db_path: root.join(DB_NAME), viewport_request: root.join("viewport-request.txt") })
}
fn validate_regular_or_absent(path: &Path, code: &'static str) -> Result<(), IpcError> { if let Some(metadata) = optional_metadata(path)? { if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 { return Err(IpcError::blocked(code, "运行时工件不是普通单链接文件。")); } } Ok(()) }
fn validate_database_object(path: &Path) -> Result<bool, IpcError> { let Some(metadata) = optional_metadata(path)? else { return Ok(false); }; if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 { return Err(IpcError::blocked("database_type_rejected", "数据库不是普通单链接文件。")); } Ok(true) }
fn geometry_path(paths: &RuntimePaths, requested: &str) -> Result<PathBuf, IpcError> { match requested { "1280x1024" | "1160x768" | "700x760" => Ok(paths.root.join(format!("native-geometry-{requested}.jsonl"))), _ => Err(IpcError::blocked("viewport_request_rejected", "逻辑视口请求不在冻结集合。")), } }
fn validate_database_path(paths: &RuntimePaths) -> Result<bool, IpcError> {
    ensure_real_directory_chain(&paths.root)?; validate_regular_or_absent(&paths.viewport_request, "viewport_type_rejected")?;
    for requested in ["1280x1024", "1160x768", "700x760"] { validate_regular_or_absent(&geometry_path(paths, requested)?, "geometry_type_rejected")?; }
    for suffix in ["-journal", "-wal", "-shm"] { if optional_metadata(&PathBuf::from(format!("{}{}", paths.db_path.display(), suffix)))?.is_some() { return Err(IpcError::blocked("database_sidecar_rejected", "数据库存在未支持的 sidecar；运行时保持 fail-closed。")); } }
    for entry in fs::read_dir(&paths.root).map_err(io_error)? { let name = entry.map_err(io_error)?.file_name().to_string_lossy().into_owned(); if name.starts_with(".capture.sqlite.") && name.ends_with(".shadow") { return Err(IpcError::blocked("candidate_residue_rejected", "发现未完成候选工件；运行时保持 fail-closed。")); } }
    validate_database_object(&paths.db_path)
}
fn open_read_only(path: &Path) -> Result<Connection, IpcError> { let conn = Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sqlite_error)?; conn.pragma_update(None, "query_only", true).map_err(sqlite_error)?; validate_connection(&conn)?; Ok(conn) }
fn initialise(conn: &Connection) -> Result<(), IpcError> {
    conn.execute_batch(SCHEMA).map_err(sqlite_error)?;
    conn.execute("INSERT OR IGNORE INTO projects(id,person_id,title,source_id,artifact_version,source_available,generation_current,tombstoned,authorized,evidence_ready) VALUES(?1,?2,'LifeOS 产品开发',?3,?4,1,1,0,1,1)", params![PROJECT_ID, PERSON_ID, SOURCE_ID, ARTIFACT_VERSION]).map_err(sqlite_error)?;
    validate_connection(conn)
}
fn validate_connection(conn: &Connection) -> Result<(), IpcError> {
    let quick: String = conn.query_row("PRAGMA quick_check", [], |row| row.get(0)).map_err(sqlite_error)?;
    let version: i64 = conn.query_row("PRAGMA user_version", [], |row| row.get(0)).map_err(sqlite_error)?;
    if quick != "ok" || version != 130 { return Err(IpcError::blocked("database_contract_rejected", "数据库完整性或版本不符合 P3-130 合同。")); }
    let known: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('captures','projects','capture_project_links','feedback','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    let unexpected: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT IN ('captures','projects','capture_project_links','feedback','audit','sqlite_sequence')", [], |row| row.get(0)).map_err(sqlite_error)?;
    if known != 6 || unexpected != 0 { return Err(IpcError::blocked("database_schema_rejected", "数据库表结构不符合 Project-backed 合同。")); }
    let project: Option<(String, String, String, String)> = conn.query_row("SELECT person_id,source_id,artifact_version,title FROM projects WHERE id=?1", params![PROJECT_ID], |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?))).optional().map_err(sqlite_error)?;
    match project { Some((person, source, artifact, title)) if person == PERSON_ID && source == SOURCE_ID && artifact == ARTIFACT_VERSION && title == "LifeOS 产品开发" => Ok(()), _ => Err(IpcError::blocked("project_contract_rejected", "Project 身份或来源版本不符合冻结合同。")), }
}
fn project_gap(conn: &Connection) -> Result<Option<String>, IpcError> {
    let flags: (i64, i64, i64, i64, i64) = conn.query_row("SELECT source_available,generation_current,tombstoned,authorized,evidence_ready FROM projects WHERE id=?1", params![PROJECT_ID], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?,row.get(3)?,row.get(4)?))).map_err(sqlite_error)?;
    let gap = if flags.0 != 1 { Some("source_unavailable") } else if flags.1 != 1 { Some("generation_stale") } else if flags.2 != 0 { Some("project_tombstoned") } else if flags.3 != 1 { Some("authorization_missing") } else if flags.4 != 1 { Some("evidence_incomplete") } else { None };
    Ok(gap.map(str::to_string))
}
fn audit_summary(conn: &Connection) -> Result<AuditSummary, IpcError> {
    let mut statement = conn.prepare("SELECT event, capture_id, detail FROM audit ORDER BY id").map_err(sqlite_error)?;
    let rows = statement.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, String>(2)?))).map_err(sqlite_error)?;
    let mut saved = 0usize; let mut repeat = 0usize; let mut candidate = 0usize; let mut confirmation = 0usize;
    for row in rows { let (event, capture_id, detail) = row.map_err(sqlite_error)?; if !capture_id.starts_with("capture:p3-130:") { return Err(IpcError::blocked("audit_contract_rejected", "审计记录没有受控 capture 身份。")); } match (event.as_str(), detail.as_str()) { ("capture_saved", "local_capture") => saved += 1, ("capture_repeat", "same_idempotency_key") => repeat += 1, ("context_link_candidate", CONTEXT_ID) => candidate += 1, ("context_confirmed", CONTEXT_ID) | ("context_rejected", CONTEXT_ID) => confirmation += 1, _ => return Err(IpcError::blocked("audit_contract_rejected", "审计事件不符合 P3-130 合同。")), } }
    Ok(AuditSummary { event_count: saved + repeat + candidate + confirmation, saved_count: saved, repeat_count: repeat, candidate_link_count: candidate, confirmation_count: confirmation })
}
fn records(conn: &Connection) -> Result<Vec<RecordView>, IpcError> {
    let mut statement = conn.prepare("SELECT id,content,created_at_ms,source,source_id,artifact_version,idem_key FROM captures ORDER BY created_at_ms,id").map_err(sqlite_error)?;
    let rows = statement.query_map([], |row| Ok((row.get::<_,String>(0)?,row.get::<_,String>(1)?,row.get::<_,i64>(2)?,row.get::<_,String>(3)?,row.get::<_,String>(4)?,row.get::<_,String>(5)?,row.get::<_,String>(6)?))).map_err(sqlite_error)?;
    let mut output = Vec::new();
    for row in rows { let (id, content, created, source, source_id, artifact, key) = row.map_err(sqlite_error)?; if !id.starts_with("capture:p3-130:") || content != CAPTURE_TEXT || source != "local_capture" || source_id != SOURCE_ID || artifact != ARTIFACT_VERSION || key != CAPTURE_KEY || created <= 0 { return Err(IpcError::blocked("record_identity_rejected", "记录身份、来源或冻结合成原文不可信。")); } output.push(RecordView { id, content, created_at_ms: created as u64, source, source_id, artifact_version: artifact, identity: "user_original" }); }
    if output.len() > 1 { return Err(IpcError::blocked("record_limit_rejected", "本次受控运行时只允许一条固定合成记录。")); }
    Ok(output)
}
fn recovery(conn: &Connection, context_id: &str) -> Result<ContextRecovery, IpcError> {
    if context_id != CONTEXT_ID { return Err(IpcError::blocked("context_schema_rejected", "只接受冻结的 Project-backed Context identity。")); }
    let gap = project_gap(conn)?;
    let link: Option<(String, String)> = conn.query_row("SELECT capture_id,link_status FROM capture_project_links WHERE context_id=?1", params![CONTEXT_ID], |row| Ok((row.get(0)?,row.get(1)?))).optional().map_err(sqlite_error)?;
    let feedback: Option<i64> = conn.query_row("SELECT id FROM feedback WHERE context_id=?1 ORDER BY id DESC LIMIT 1", params![CONTEXT_ID], |row| row.get(0)).optional().map_err(sqlite_error)?;
    let state = if let Some(reason) = &gap { format!("evidence_gap:{reason}") } else if let Some((_, status)) = &link { status.clone() } else { "empty".to_string() };
    let typed_link_ref = link.as_ref().map(|(capture_id, status)| format!("capture_project_links:{capture_id}:{status}"));
    Ok(ContextRecovery { context_id: CONTEXT_ID.to_string(), project_id: PROJECT_ID.to_string(), person_id: PERSON_ID.to_string(), project_title: "LifeOS 产品开发".to_string(), reliable_suggestion: false, state, evidence_gap: gap, source_ref: SOURCE_ID.to_string(), artifact_ref: ARTIFACT_VERSION.to_string(), typed_link_ref, feedback_ref: feedback.map(|id| format!("feedback:{id}")), audit_ref: link.map(|(capture_id, _)| format!("audit:capture:{capture_id}")), memory_copy_created: false })
}
fn remove_candidate(path: &Path) { for item in [path.to_path_buf(), PathBuf::from(format!("{}-journal", path.display())), PathBuf::from(format!("{}-wal", path.display())), PathBuf::from(format!("{}-shm", path.display()))] { let _ = fs::remove_file(item); } }
fn candidate_db(paths: &RuntimePaths) -> Result<(PathBuf, bool), IpcError> {
    let present = validate_database_path(paths)?; let now = now_ms()?; let candidate = paths.root.join(format!(".capture.sqlite.{now}.{}.shadow", std::process::id()));
    remove_candidate(&candidate); OpenOptions::new().write(true).create_new(true).open(&candidate).map_err(io_error)?;
    if present { if let Err(error) = fs::copy(&paths.db_path, &candidate) { remove_candidate(&candidate); return Err(io_error(error)); } }
    Ok((candidate, present))
}
fn open_candidate(path: &Path, present: bool) -> Result<Connection, IpcError> { let conn = Connection::open(path).map_err(sqlite_error)?; conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE;").map_err(sqlite_error)?; if present { validate_connection(&conn)?; } else { initialise(&conn)?; } Ok(conn) }
fn publish_candidate(paths: &RuntimePaths, candidate: &Path, original_present: bool) -> Result<(), IpcError> { if validate_database_object(&paths.db_path)? != original_present { remove_candidate(candidate); return Err(IpcError::blocked("database_object_changed", "数据库最终对象在发布前发生变化；候选未发布。")); } if let Err(error) = fs::rename(candidate, &paths.db_path) { remove_candidate(candidate); return Err(io_error(error)); } remove_candidate(candidate); Ok(()) }
fn capture_impl(paths: &RuntimePaths, request: &CaptureRequest, fault: Fault) -> Result<CaptureResponse, IpcError> {
    if request.text != CAPTURE_TEXT || request.key != CAPTURE_KEY { return Err(IpcError::blocked("argument_schema_rejected", "只接受冻结的合成用户原文及 capture 幂等键。")); }
    let (candidate, present) = candidate_db(paths)?;
    let outcome = (|| -> Result<CaptureResponse, IpcError> {
        let mut conn = open_candidate(&candidate, present)?; let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sqlite_error)?;
        let prior: Option<(String, String, i64)> = tx.query_row("SELECT id,content,created_at_ms FROM captures WHERE idem_key=?1", params![CAPTURE_KEY], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?))).optional().map_err(sqlite_error)?;
        let (status, record, link_status) = if let Some((id, content, created)) = prior {
            if content != CAPTURE_TEXT { return Err(IpcError::blocked("idempotency_conflict", "幂等键已绑定其他记录；冲突已阻断。")); }
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_repeat',?1,?2,'same_idempotency_key')", params![id, now_ms()? as i64]).map_err(sqlite_error)?;
            let status: String = tx.query_row("SELECT link_status FROM capture_project_links WHERE capture_id=?1", params![id], |row| row.get(0)).map_err(sqlite_error)?;
            ("idempotent_repeat".to_string(), RecordView { id, content, created_at_ms: created as u64, source: "local_capture".to_string(), source_id: SOURCE_ID.to_string(), artifact_version: ARTIFACT_VERSION.to_string(), identity: "user_original" }, status)
        } else {
            let now = now_ms()?; let id = format!("capture:p3-130:{now:016x}");
            tx.execute("INSERT INTO captures(id,content,created_at_ms,source,source_id,artifact_version,idem_key) VALUES(?1,?2,?3,'local_capture',?4,?5,?6)", params![id,CAPTURE_TEXT,now as i64,SOURCE_ID,ARTIFACT_VERSION,CAPTURE_KEY]).map_err(sqlite_error)?;
            tx.execute("INSERT INTO capture_project_links(capture_id,project_id,context_id,link_status,source_id,artifact_version) VALUES(?1,?2,?3,'candidate',?4,?5)", params![id,PROJECT_ID,CONTEXT_ID,SOURCE_ID,ARTIFACT_VERSION]).map_err(sqlite_error)?;
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES('capture_saved',?1,?2,'local_capture'),('context_link_candidate',?1,?2,?3)", params![id,now as i64,CONTEXT_ID]).map_err(sqlite_error)?;
            ("saved".to_string(), RecordView { id, content: CAPTURE_TEXT.to_string(), created_at_ms: now, source: "local_capture".to_string(), source_id: SOURCE_ID.to_string(), artifact_version: ARTIFACT_VERSION.to_string(), identity: "user_original" }, "candidate".to_string())
        };
        if fault == Fault::BeforeCommit { return Err(IpcError::blocked("injected_atomic_failure", "受控失败已注入；未显示成功，数据库与页面状态未更改。")); }
        tx.commit().map_err(sqlite_error)?; drop(conn);
        let verified = open_read_only(&candidate)?; let count = records(&verified)?.len(); let audit = audit_summary(&verified)?; drop(verified);
        Ok(CaptureResponse { status, record, record_count: count, audit_event_count: audit.event_count, context_id: CONTEXT_ID.to_string(), link_status })
    })();
    match outcome { Ok(response) => { publish_candidate(paths, &candidate, present)?; eprintln!("ipc_result command=capture_record status={} records={} audits={}", response.status, response.record_count, response.audit_event_count); Ok(response) }, Err(error) => { remove_candidate(&candidate); Err(error) } }
}
fn confirm_impl(paths: &RuntimePaths, request: &ConfirmRequest) -> Result<ConfirmResponse, IpcError> {
    if request.context_id != CONTEXT_ID || request.idempotency_key != CONFIRM_KEY || !request.capture_id.starts_with("capture:p3-130:") { return Err(IpcError::blocked("argument_schema_rejected", "确认请求不符合冻结的 capture、Context 或幂等键合同。")); }
    let (candidate, present) = candidate_db(paths)?;
    let outcome = (|| -> Result<ConfirmResponse, IpcError> {
        let mut conn = open_candidate(&candidate, present)?; if let Some(gap) = project_gap(&conn)? { return Err(IpcError::blocked("context_evidence_gap", Box::leak(format!("Project Context Evidence gap: {gap}").into_boxed_str()))); }
        let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sqlite_error)?;
        let existing: Option<(String, String, String)> = tx.query_row("SELECT capture_id,context_id,decision FROM feedback WHERE idem_key=?1", params![CONFIRM_KEY], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?))).optional().map_err(sqlite_error)?;
        let (status, decision) = if let Some((capture, context, decision)) = existing { if capture != request.capture_id || context != CONTEXT_ID || decision != request.decision.as_str() { return Err(IpcError::blocked("idempotency_conflict", "确认幂等键已绑定不同结果；冲突已阻断。")); } ("idempotent_repeat".to_string(), decision) } else {
            let link: Option<String> = tx.query_row("SELECT link_status FROM capture_project_links WHERE capture_id=?1 AND project_id=?2 AND context_id=?3", params![request.capture_id,PROJECT_ID,CONTEXT_ID], |row| row.get(0)).optional().map_err(sqlite_error)?;
            if link.as_deref() != Some("candidate") { return Err(IpcError::blocked("confirmation_state_rejected", "只能对存在的候选 Project-backed link 进行一次确认或拒绝。")); }
            let now = now_ms()?; tx.execute("INSERT INTO feedback(capture_id,context_id,decision,idem_key,created_at_ms) VALUES(?1,?2,?3,?4,?5)", params![request.capture_id,CONTEXT_ID,request.decision.as_str(),CONFIRM_KEY,now as i64]).map_err(sqlite_error)?;
            let link_status = if request.decision == Decision::Confirm { "confirmed" } else { "rejected" };
            tx.execute("UPDATE capture_project_links SET link_status=?1 WHERE capture_id=?2", params![link_status,request.capture_id]).map_err(sqlite_error)?;
            let event = if request.decision == Decision::Confirm { "context_confirmed" } else { "context_rejected" };
            tx.execute("INSERT INTO audit(event,capture_id,created_at_ms,detail) VALUES(?1,?2,?3,?4)", params![event,request.capture_id,now as i64,CONTEXT_ID]).map_err(sqlite_error)?;
            ("saved".to_string(), request.decision.as_str().to_string())
        };
        tx.commit().map_err(sqlite_error)?; drop(conn);
        let verified = open_read_only(&candidate)?; let feedback_count: i64 = verified.query_row("SELECT count(*) FROM feedback", [], |row| row.get(0)).map_err(sqlite_error)?; let audit = audit_summary(&verified)?; let recovery = recovery(&verified, CONTEXT_ID)?; drop(verified);
        Ok(ConfirmResponse { status, capture_id: request.capture_id.clone(), context_id: CONTEXT_ID.to_string(), decision, feedback_count: feedback_count as usize, audit_event_count: audit.event_count, recovery })
    })();
    match outcome { Ok(response) => { publish_candidate(paths, &candidate, present)?; eprintln!("ipc_result command=confirm_capture_context status={} decision={}", response.status, response.decision); Ok(response) }, Err(error) => { remove_candidate(&candidate); Err(error) } }
}
fn today_impl(paths: &RuntimePaths) -> Result<TodayResponse, IpcError> { if !validate_database_path(paths)? { let conn = Connection::open_in_memory().map_err(sqlite_error)?; initialise(&conn)?; return Ok(TodayResponse { status: "empty", records: Vec::new(), source: "local_capture", ai_status: "disabled", audit: AuditSummary { event_count: 0, saved_count: 0, repeat_count: 0, candidate_link_count: 0, confirmation_count: 0 }, context_recovery: recovery(&conn, CONTEXT_ID)? }); } let conn = open_read_only(&paths.db_path)?; let result = TodayResponse { status: "loaded", records: records(&conn)?, source: "local_capture", ai_status: "disabled", audit: audit_summary(&conn)?, context_recovery: recovery(&conn, CONTEXT_ID)? }; eprintln!("ipc_result command=get_today status={} records={}", result.status, result.records.len()); Ok(result) }
fn recovery_impl(paths: &RuntimePaths, request: &ContextRequest) -> Result<ContextRecovery, IpcError> { if request.context_id != CONTEXT_ID { return Err(IpcError::blocked("context_schema_rejected", "只接受冻结的 Project-backed Context identity。")); } if !validate_database_path(paths)? { let conn = Connection::open_in_memory().map_err(sqlite_error)?; initialise(&conn)?; return recovery(&conn, CONTEXT_ID); } let conn = open_read_only(&paths.db_path)?; let value = recovery(&conn, CONTEXT_ID)?; eprintln!("ipc_result command=get_context_recovery state={}", value.state); Ok(value) }
fn status_impl() -> RuntimeStatusResponse { RuntimeStatusResponse { status: "restricted_offline", offline: true, ai_enabled: false, renderer_direct_capabilities: Vec::new(), ipc_allowlist: IPC_ALLOWLIST.to_vec(), unknown_ipc: "deny", filesystem: false, raw_database: false, generic_path_api: false, shell: false, process_spawn: false, network: false, vault: false, export: false, sync: false, context_recovery: "project_backed_only", memory_duplicate_original: false } }
fn viewport_request(paths: &RuntimePaths) -> Result<String, IpcError> { let requested = match optional_metadata(&paths.viewport_request)? { Some(_) => fs::read_to_string(&paths.viewport_request).map_err(io_error)?.trim().to_string(), None => "1280x1024".to_string(), }; geometry_path(paths, &requested)?; Ok(requested) }
fn record_native_geometry(paths: &RuntimePaths, window: &tauri::Window, phase: &str, requested: &str) -> Result<(), IpcError> { let path = geometry_path(paths, requested)?; validate_regular_or_absent(&path, "geometry_type_rejected")?; let scale = window.scale_factor().map_err(|_| IpcError::blocked("native_geometry_unavailable", "无法读取实际原生窗口比例。"))?; let inner = window.inner_size().map_err(|_| IpcError::blocked("native_geometry_unavailable", "无法读取实际原生内容边界。"))?; let outer = window.outer_size().map_err(|_| IpcError::blocked("native_geometry_unavailable", "无法读取实际原生窗口边界。"))?; let inner_logical = inner.to_logical::<f64>(scale); let outer_logical = outer.to_logical::<f64>(scale); let record = serde_json::json!({"task":"LIFEOS-P3-130","source":"actual-tauri-native-window","phase":phase,"requested_logical":requested,"scale_factor":scale,"content_bounds":{"size_physical":{"width":inner.width,"height":inner.height},"size_logical":{"width":inner_logical.width,"height":inner_logical.height}},"outer_bounds":{"size_physical":{"width":outer.width,"height":outer.height},"size_logical":{"width":outer_logical.width,"height":outer_logical.height}}}); let mut file = OpenOptions::new().create(true).append(true).open(path).map_err(io_error)?; writeln!(file, "{record}").map_err(io_error)?; eprintln!("P3_130_NATIVE_GEOMETRY {record}"); Ok(()) }
#[tauri::command] fn capture_record(request: CaptureRequest, state: tauri::State<'_, AppState>) -> Result<CaptureResponse, IpcError> { let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用。"))?; capture_impl(&state.runtime, &request, Fault::None) }
#[tauri::command] fn get_today(request: EmptyRequest, state: tauri::State<'_, AppState>) -> Result<TodayResponse, IpcError> { let _ = request; let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用。"))?; today_impl(&state.runtime) }
#[tauri::command] fn runtime_status(request: EmptyRequest) -> RuntimeStatusResponse { let _ = request; eprintln!("ipc_result command=runtime_status status=restricted_offline"); status_impl() }
#[tauri::command] fn confirm_capture_context(request: ConfirmRequest, state: tauri::State<'_, AppState>) -> Result<ConfirmResponse, IpcError> { let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用。"))?; confirm_impl(&state.runtime, &request) }
#[tauri::command] fn get_context_recovery(request: ContextRequest, state: tauri::State<'_, AppState>) -> Result<ContextRecovery, IpcError> { let _guard = state.serial.lock().map_err(|_| IpcError::blocked("runtime_lock_unavailable", "本地运行时锁不可用。"))?; recovery_impl(&state.runtime, &request) }
pub fn run() {
    let runtime = configured_runtime_paths().unwrap_or_else(|error| panic!("P3-130 Runtime root rejected: {}", error.code)); validate_database_path(&runtime).unwrap_or_else(|error| panic!("P3-130 database boundary rejected: {}", error.code)); let requested = viewport_request(&runtime).unwrap_or_else(|error| panic!("P3-130 viewport rejected: {}", error.code)); eprintln!("runtime_start task=LIFEOS-P3-130 status=restricted_offline runtime_root={}", runtime.root.display());
    let setup_runtime = runtime.clone(); let event_runtime = runtime.clone();
    tauri::Builder::default().manage(AppState { runtime, serial: Mutex::new(()) }).setup(move |app| { let (width, height) = match requested.as_str() { "1280x1024" => (1280.0,1024.0), "1160x768" => (1160.0,768.0), "700x760" => (700.0,760.0), _ => panic!("unsupported configured viewport") }; let webview = app.get_webview_window("main").expect("main WebView window missing"); let window = webview.as_ref().window(); let scale = window.scale_factor().expect("scale unavailable"); let inner = window.inner_size().expect("inner unavailable").to_logical::<f64>(scale); let outer = window.outer_size().expect("outer unavailable").to_logical::<f64>(scale); window.set_size(LogicalSize::new(width + (outer.width-inner.width).max(0.0), height + (outer.height-inner.height).max(0.0))).expect("viewport resize failed"); record_native_geometry(&setup_runtime, &window, "setup", &requested).unwrap_or_else(|error| panic!("native geometry rejected: {}", error.code)); Ok(()) }).on_window_event(move |window,event| { if matches!(event, tauri::WindowEvent::Resized(_)) { let current = viewport_request(&event_runtime).unwrap_or_else(|error| panic!("native geometry viewport rejected: {}", error.code)); record_native_geometry(&event_runtime, window, "resized", &current).unwrap_or_else(|error| panic!("native geometry rejected: {}", error.code)); } }).invoke_handler(tauri::generate_handler![capture_record,get_today,runtime_status,confirm_capture_context,get_context_recovery]).run(tauri::generate_context!()).expect("P3-130 Tauri runtime failed");
}

#[cfg(test)]
mod tests {
    use super::*;
    use sha2::{Digest, Sha256};
    fn paths(name: &str) -> RuntimePaths { let base = configured_runtime_paths().unwrap().root; let root = base.join(format!("unit-tests-{name}-{}", std::process::id())); let _ = fs::remove_dir_all(&root); fs::create_dir(&root).unwrap(); RuntimePaths { db_path: root.join(DB_NAME), viewport_request: root.join("viewport-request.txt"), root } }
    fn clean(paths: &RuntimePaths) { assert_eq!(paths.root.parent(), Some(configured_runtime_paths().unwrap().root.as_path())); fs::remove_dir_all(&paths.root).unwrap(); }
    fn hash(path: &Path) -> String { let mut digest = Sha256::new(); digest.update(fs::read(path).unwrap()); format!("{:x}",digest.finalize()) }
    fn capture() -> CaptureRequest { CaptureRequest { text: CAPTURE_TEXT.to_string(), key: CAPTURE_KEY.to_string() } }
    fn confirm(id: String, decision: Decision) -> ConfirmRequest { ConfirmRequest { capture_id:id, context_id:CONTEXT_ID.to_string(), decision, idempotency_key:CONFIRM_KEY.to_string() } }
    #[test] fn lifecycle_confirmation_reopen_and_provenance_are_consistent() { let runtime = paths("lifecycle"); assert_eq!(today_impl(&runtime).unwrap().status,"empty"); let first = capture_impl(&runtime,&capture(),Fault::None).unwrap(); let first_hash = hash(&runtime.db_path); let repeat = capture_impl(&runtime,&capture(),Fault::None).unwrap(); assert_eq!(first.status,"saved"); assert_eq!(repeat.status,"idempotent_repeat"); assert_eq!(first.record.id,repeat.record.id); let confirmed = confirm_impl(&runtime,&confirm(first.record.id.clone(),Decision::Confirm)).unwrap(); let confirm_repeat = confirm_impl(&runtime,&confirm(first.record.id.clone(),Decision::Confirm)).unwrap(); assert_eq!(confirmed.status,"saved"); assert_eq!(confirm_repeat.status,"idempotent_repeat"); assert_eq!(confirmed.recovery.state,"confirmed"); let reopened = today_impl(&runtime).unwrap(); assert_eq!(reopened.records.len(),1); assert_eq!(reopened.context_recovery.source_ref,SOURCE_ID); assert_eq!(reopened.context_recovery.artifact_ref,ARTIFACT_VERSION); assert!(!reopened.context_recovery.memory_copy_created); assert_ne!(first_hash,hash(&runtime.db_path)); clean(&runtime); }
    #[test] fn reject_is_idempotent_and_does_not_create_memory_copy() { let runtime = paths("reject"); let record = capture_impl(&runtime,&capture(),Fault::None).unwrap().record; let rejected = confirm_impl(&runtime,&confirm(record.id,Decision::Reject)).unwrap(); assert_eq!(rejected.recovery.state,"rejected"); assert!(!rejected.recovery.memory_copy_created); clean(&runtime); }
    #[test] fn bad_requests_and_atomic_failure_leave_no_success_state() { let runtime = paths("negative"); let bad = CaptureRequest { text:"bad".into(),key:CAPTURE_KEY.into() }; assert_eq!(capture_impl(&runtime,&bad,Fault::None).unwrap_err().code,"argument_schema_rejected"); assert!(!runtime.db_path.exists()); let saved = capture_impl(&runtime,&capture(),Fault::None).unwrap(); let before = hash(&runtime.db_path); assert_eq!(capture_impl(&runtime,&capture(),Fault::BeforeCommit).unwrap_err().code,"injected_atomic_failure"); assert_eq!(before,hash(&runtime.db_path)); let invalid = ConfirmRequest { capture_id:saved.record.id, context_id:"ctx:wrong".into(),decision:Decision::Confirm,idempotency_key:CONFIRM_KEY.into() }; assert_eq!(confirm_impl(&runtime,&invalid).unwrap_err().code,"argument_schema_rejected"); clean(&runtime); }
    #[test] fn three_independent_evidence_gaps_fail_closed_before_confirmation_write() { for (name, mutation) in [("source","source_available=0"),("generation","generation_current=0"),("tombstone","tombstoned=1"),("authorization","authorized=0"),("evidence","evidence_ready=0")] { let runtime = paths(name); let record = capture_impl(&runtime,&capture(),Fault::None).unwrap().record; let conn = Connection::open(&runtime.db_path).unwrap(); conn.execute(&format!("UPDATE projects SET {mutation} WHERE id=?1"),params![PROJECT_ID]).unwrap(); drop(conn); let before = hash(&runtime.db_path); assert_eq!(confirm_impl(&runtime,&confirm(record.id,Decision::Confirm)).unwrap_err().code,"context_evidence_gap"); assert_eq!(before,hash(&runtime.db_path)); clean(&runtime); } }
    #[test] fn conflicts_and_unknown_fields_fail_before_durable_change() { let runtime = paths("conflicts"); let record = capture_impl(&runtime,&capture(),Fault::None).unwrap().record; let before_missing = hash(&runtime.db_path); assert_eq!(confirm_impl(&runtime,&confirm("capture:p3-130:missing".to_string(),Decision::Confirm)).unwrap_err().code,"confirmation_state_rejected"); assert_eq!(before_missing,hash(&runtime.db_path)); assert_eq!(confirm_impl(&runtime,&confirm(record.id.clone(),Decision::Confirm)).unwrap().status,"saved"); let before_conflict = hash(&runtime.db_path); assert_eq!(confirm_impl(&runtime,&confirm("capture:p3-130:other".to_string(),Decision::Confirm)).unwrap_err().code,"idempotency_conflict"); assert_eq!(before_conflict,hash(&runtime.db_path)); assert!(serde_json::from_str::<CaptureRequest>(r#"{"text":"整理 LifeOS Context Recovery 合成验收记录。","key":"p3-130-capture-001","sql":"select 1"}"#).is_err()); assert!(serde_json::from_str::<ContextRequest>(r#"{"context_id":"ctx:project:synthetic-lifeos-product","path":"/escape"}"#).is_err()); assert!(serde_json::from_str::<ConfirmRequest>(r#"{"capture_id":"capture:p3-130:x","context_id":"ctx:project:synthetic-lifeos-product","decision":"confirm","idempotency_key":"p3-130-confirm-001","extra":true}"#).is_err()); assert_eq!(status_impl().ipc_allowlist,IPC_ALLOWLIST); clean(&runtime); }
}
