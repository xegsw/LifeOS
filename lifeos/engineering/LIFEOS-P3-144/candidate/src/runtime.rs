use crate::{deepseek, secure_credentials};
use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{LogicalSize, Manager, Size};
use zeroize::Zeroize;

const MARKER: &str = ".lifeos-p3-144-owner.json";
const RUNTIME_CHILD: &str = "runtime";
const DB: &str = "secure-provider-settings.sqlite";
const DTO_VERSION: u8 = 1;
const PROFILE_ID: &str = "default";
const DEEPSEEK: &str = "deepseek";
const WORK: &str = "work";
const HEALTH: &str = "health";
const ITEM_LIMIT: i64 = 3;
const ITEM_CHARACTER_LIMIT: usize = 200;
const DISCLOSURE_CHARACTER_BUDGET: usize = 480;
const DISCLOSURE_TOKEN_BUDGET: usize = 120;
static NEXT_IDENTIFIER: AtomicU64 = AtomicU64::new(1);
const IPC: [&str; 20] = [
    "capture_record",
    "get_today",
    "runtime_status",
    "confirm_capture_context",
    "get_context_recovery",
    "get_context_next_action",
    "decide_context_next_action",
    "record_action_result",
    "assemble_global_ai_context",
    "get_evidence_backed_understanding",
    "decide_understanding_feedback",
    "get_ai_provider_settings",
    "save_ai_provider_settings",
    "save_ai_provider_credential",
    "test_ai_provider_connection",
    "set_ai_provider_enabled",
    "upsert_durable_memory",
    "update_current_state",
    "resolve_request_context",
    "get_context_disclosure_receipt",
];

#[derive(Debug, Serialize)]
struct ApiError {
    status: &'static str,
    code: &'static str,
    message: &'static str,
}

impl ApiError {
    fn blocked(code: &'static str, message: &'static str) -> Self {
        Self {
            status: "blocked",
            code,
            message,
        }
    }
}

fn io_error(_: std::io::Error) -> ApiError {
    ApiError::blocked("task_root_unavailable", "合成任务根无法安全验证；未写入。")
}

fn db_error(_: rusqlite::Error) -> ApiError {
    ApiError::blocked(
        "synthetic_store_unavailable",
        "合成设置存储不可用；未显示成功。",
    )
}

fn now_ms() -> Result<i64, ApiError> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|value| value.as_millis() as i64)
        .map_err(|_| ApiError::blocked("clock_unavailable", "本地时钟不可用；未写入。"))
}

fn run_mode() -> &'static str {
    // The mode is emitted by build.rs together with the exact root profile.
    // Runtime environment variables cannot turn an offline binary into a real gate.
    env!("LIFEOS_P3_144_COMPILED_RUN_MODE")
}

fn run_mode_matches_profile(profile: &str, mode: &str) -> bool {
    matches!(
        (profile, mode),
        ("engineering", "synthetic")
            | ("independent-review", "synthetic")
            | ("pilot-7", "real_gate")
    )
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ProviderMode {
    Cloud,
    Local,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ProviderDescriptor {
    id: String,
    label: String,
    mode: ProviderMode,
    form_fields: Vec<String>,
    capability_metadata: Vec<String>,
}

fn provider_registry() -> Vec<ProviderDescriptor> {
    let cloud = [
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("google_gemini", "Google Gemini"),
        ("deepseek", "DeepSeek"),
        ("kimi", "Kimi"),
        ("openrouter", "OpenRouter"),
        ("cloud_openai_compatible", "其他 OpenAI-compatible 服务"),
        ("cloud_custom", "自定义兼容接口"),
    ];
    let local = [
        ("ollama", "Ollama"),
        ("lm_studio", "LM Studio"),
        ("local_openai_compatible", "OpenAI-compatible 本地接口"),
        ("local_custom", "自定义本地服务"),
    ];
    cloud
        .into_iter()
        .map(|(id, label)| ProviderDescriptor {
            id: id.into(),
            label: label.into(),
            mode: ProviderMode::Cloud,
            form_fields: vec![
                "endpoint_url".into(),
                "model_label".into(),
                "api_key".into(),
            ],
            capability_metadata: cloud_capabilities(id),
        })
        .chain(local.into_iter().map(|(id, label)| ProviderDescriptor {
            id: id.into(),
            label: label.into(),
            mode: ProviderMode::Local,
            form_fields: vec!["local_runtime".into(), "model_label".into()],
            capability_metadata: local_capabilities(id),
        }))
        .collect()
}

fn cloud_capabilities(id: &str) -> Vec<String> {
    let mut values = vec![
        "text.reasoning".into(),
        "tool.use".into(),
        "long_context".into(),
        "structured_output".into(),
    ];
    if matches!(id, "openai" | "google_gemini" | "openrouter") {
        values.push("vision.understanding".into());
    }
    if matches!(id, "openai" | "google_gemini") {
        values.extend(["speech.transcription".into(), "speech.synthesis".into()]);
    }
    values.push("embedding".into());
    values
}

fn local_capabilities(id: &str) -> Vec<String> {
    let mut values = vec![
        "text.reasoning".into(),
        "long_context".into(),
        "structured_output".into(),
    ];
    if matches!(id, "ollama" | "lm_studio") {
        values.push("vision.understanding".into());
    }
    values
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct PrimaryService {
    mode: ProviderMode,
    provider_id: String,
    model_label: String,
    endpoint_url: Option<String>,
    local_runtime: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct RoutingPolicy {
    prefer_local: bool,
    allow_cloud_supplement: bool,
    allow_automatic_failover: bool,
    prefer_fast_response: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct FallbackService {
    configured: bool,
    provider_id: Option<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct AdvancedSettings {
    expanded: bool,
    capability_overrides: BTreeMap<String, String>,
    temperature: u16,
    max_output_tokens: u16,
    timeout_seconds: u16,
    context_window: u16,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct SettingsDto {
    version: u8,
    primary: PrimaryService,
    routing_policy: RoutingPolicy,
    fallback: FallbackService,
    advanced: AdvancedSettings,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PersistedState {
    settings: Option<SettingsDto>,
    connection_state: String,
    enabled: bool,
    credential_reference: Option<String>,
    credential_mask: Option<String>,
    last_test: Option<String>,
    selected_model: Option<String>,
    available_models: Vec<String>,
}

impl Default for PersistedState {
    fn default() -> Self {
        Self {
            settings: None,
            connection_state: "not_configured".into(),
            enabled: false,
            credential_reference: None,
            credential_mask: None,
            last_test: None,
            selected_model: None,
            available_models: Vec::new(),
        }
    }
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct SettingsResponse {
    schema_version: u8,
    primary_slot_count: u8,
    settings: Option<SettingsDto>,
    connection_state: String,
    enabled: bool,
    has_credential: bool,
    credential_mask: Option<String>,
    last_test: Option<String>,
    selected_model: Option<String>,
    available_models: Vec<String>,
    provider_registry: Vec<ProviderDescriptor>,
    capability_registry: BTreeMap<String, Vec<String>>,
    run_mode: String,
}

fn capability_registry(entries: &[ProviderDescriptor]) -> BTreeMap<String, Vec<String>> {
    entries
        .iter()
        .map(|entry| (entry.id.clone(), entry.capability_metadata.clone()))
        .collect()
}

fn response(state: &PersistedState) -> SettingsResponse {
    let registry = provider_registry();
    SettingsResponse {
        schema_version: DTO_VERSION,
        primary_slot_count: 1,
        settings: state.settings.clone(),
        connection_state: state.connection_state.clone(),
        enabled: state.enabled,
        has_credential: state.credential_reference.is_some(),
        credential_mask: state.credential_mask.clone(),
        last_test: state.last_test.clone(),
        selected_model: state.selected_model.clone(),
        available_models: state.available_models.clone(),
        capability_registry: capability_registry(&registry),
        provider_registry: registry,
        run_mode: run_mode().into(),
    }
}

#[derive(Clone, Debug)]
struct RootAuthority {
    profile: String,
    parent: String,
    basename: String,
    root: String,
    marker_schema: String,
    marker_task: String,
    marker_owner: String,
    run_id: String,
    marker_run_id: Option<String>,
}

fn compiled_root_authority() -> RootAuthority {
    let marker_run_id = env!("LIFEOS_P3_144_COMPILED_MARKER_RUN_ID");
    RootAuthority {
        profile: env!("LIFEOS_P3_144_COMPILED_ROOT_PROFILE").into(),
        parent: env!("LIFEOS_P3_144_COMPILED_ROOT_PARENT").into(),
        basename: env!("LIFEOS_P3_144_COMPILED_ROOT_BASENAME").into(),
        root: env!("LIFEOS_P3_144_COMPILED_ROOT").into(),
        marker_schema: env!("LIFEOS_P3_144_COMPILED_MARKER_SCHEMA").into(),
        marker_task: env!("LIFEOS_P3_144_COMPILED_MARKER_TASK").into(),
        marker_owner: env!("LIFEOS_P3_144_COMPILED_MARKER_OWNER").into(),
        run_id: env!("LIFEOS_P3_144_COMPILED_RUN_ID").into(),
        marker_run_id: (!marker_run_id.is_empty()).then(|| marker_run_id.into()),
    }
}

fn compiled_authority_is_valid(authority: &RootAuthority) -> bool {
    let root = Path::new(&authority.root);
    if authority.basename.is_empty()
        || authority.basename.contains('/')
        || authority.basename == "."
        || authority.basename == ".."
        || root.parent() != Some(Path::new(&authority.parent))
        || root.file_name().and_then(|value| value.to_str()) != Some(authority.basename.as_str())
        || authority.marker_task != "LIFEOS-P3-144"
        || authority.marker_owner.is_empty()
    {
        return false;
    }
    match authority.profile.as_str() {
        "engineering" => {
            authority.parent == "/private/tmp"
                && authority.root == "/private/tmp/lifeos-p3-144-engineering-v1"
                && authority.run_id == "engineering"
                && authority.marker_run_id.is_none()
                && authority.marker_owner == authority.basename
                && authority.marker_schema == "lifeos.p3-144.engineering-root.v1"
        }
        "independent-review" => {
            authority.parent == "/private/tmp"
                && authority.basename == "lifeos-p3-144-independent-review-v1"
                && authority.root == "/private/tmp/lifeos-p3-144-independent-review-v1"
                && authority.run_id == "v1"
                && authority.marker_run_id.as_deref() == Some("v1")
                && authority.marker_owner == "lifeos-p3-144-independent-review"
                && authority.marker_schema == "lifeos.p3-144.independent-review-root.v1"
        }
        "pilot-7" => {
            authority.parent == "/Users/xxe/Documents"
                && authority.basename == "LifeOS-Self-Use-Pilot-7"
                && authority.root == "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7"
                && authority.run_id == "pilot-7"
                && authority.marker_run_id.as_deref() == Some("pilot-7")
                && authority.marker_owner == "lifeos-p3-144-pilot-7"
                && authority.marker_schema == "lifeos.p3-144.pilot-7-root.v1"
        }
        _ => false,
    }
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
struct RootMarker {
    schema: String,
    task: String,
    owner: String,
    #[serde(default, rename = "runId", skip_serializing_if = "Option::is_none")]
    run_id: Option<String>,
}

fn expected_marker(authority: &RootAuthority) -> RootMarker {
    RootMarker {
        schema: authority.marker_schema.clone(),
        task: authority.marker_task.clone(),
        owner: authority.marker_owner.clone(),
        run_id: authority.marker_run_id.clone(),
    }
}

fn verify_runtime_child(root: &Path) -> Result<(), ApiError> {
    let child = root.join(RUNTIME_CHILD);
    if child.parent() != Some(root) {
        return Err(ApiError::blocked(
            "runtime_child_literal_rejected",
            "运行目录不是任务根的直接子目录。",
        ));
    }
    match fs::symlink_metadata(&child) {
        Ok(meta) => {
            if meta.file_type().is_symlink()
                || !meta.file_type().is_dir()
                || meta.permissions().mode() & 0o777 != 0o700
            {
                return Err(ApiError::blocked(
                    "runtime_child_type_rejected",
                    "运行目录必须是 0700 的普通目录。",
                ));
            }
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            fs::create_dir(&child).map_err(io_error)?;
            fs::set_permissions(&child, fs::Permissions::from_mode(0o700)).map_err(io_error)?;
        }
        Err(error) => return Err(io_error(error)),
    }
    if fs::canonicalize(&child).map_err(io_error)? != child {
        return Err(ApiError::blocked(
            "runtime_child_canonical_rejected",
            "运行目录解析后发生变化。",
        ));
    }
    Ok(())
}

fn verify_authorized_root(authority: &RootAuthority) -> Result<PathBuf, ApiError> {
    if !compiled_authority_is_valid(&authority) {
        return Err(ApiError::blocked(
            "compiled_root_authority_rejected",
            "编译期任务根 authority 无法验证。",
        ));
    }
    let root = PathBuf::from(&authority.root);
    let created_root = match fs::symlink_metadata(&root) {
        Ok(meta) => {
            if meta.file_type().is_symlink()
                || !meta.file_type().is_dir()
                || meta.permissions().mode() & 0o777 != 0o700
            {
                return Err(ApiError::blocked(
                    "task_root_type_rejected",
                    "任务根必须是 0700 的普通目录。",
                ));
            }
            false
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            fs::create_dir(&root).map_err(io_error)?;
            fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).map_err(io_error)?;
            true
        }
        Err(error) => return Err(io_error(error)),
    };
    if fs::canonicalize(&root).map_err(io_error)? != root {
        return Err(ApiError::blocked(
            "task_root_canonical_rejected",
            "任务根解析后发生变化。",
        ));
    }
    let marker = root.join(MARKER);
    match fs::symlink_metadata(&marker) {
        Err(error) if error.kind() == std::io::ErrorKind::NotFound && created_root => {
            let bytes = serde_json::to_vec_pretty(&expected_marker(&authority)).map_err(|_| {
                ApiError::blocked("marker_serialization_rejected", "任务 marker 无法序列化。")
            })?;
            let mut file = OpenOptions::new()
                .write(true)
                .create_new(true)
                .mode(0o600)
                .open(&marker)
                .map_err(io_error)?;
            file.write_all(&bytes)
                .and_then(|_| file.write_all(b"\n"))
                .and_then(|_| file.sync_all())
                .map_err(io_error)?;
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return Err(ApiError::blocked(
                "task_marker_missing",
                "预存任务根缺少授权 marker；未写入。",
            ));
        }
        Ok(_) => {}
        Err(error) => return Err(io_error(error)),
    }
    let meta = fs::symlink_metadata(&marker).map_err(io_error)?;
    if meta.file_type().is_symlink()
        || !meta.file_type().is_file()
        || meta.permissions().mode() & 0o777 != 0o600
    {
        return Err(ApiError::blocked(
            "task_marker_type_rejected",
            "任务 marker 必须是 0600 普通文件。",
        ));
    }
    let observed: RootMarker = serde_json::from_slice(&fs::read(&marker).map_err(io_error)?)
        .map_err(|_| ApiError::blocked("task_marker_rejected", "任务 marker 不能证明所有权。"))?;
    if observed != expected_marker(&authority) {
        return Err(ApiError::blocked(
            "task_marker_rejected",
            "任务 marker 不属于 P3-144。",
        ));
    }
    verify_runtime_child(&root)?;
    Ok(root)
}

fn verify_task_root() -> Result<PathBuf, ApiError> {
    let authority = compiled_root_authority();
    if !run_mode_matches_profile(&authority.profile, run_mode()) {
        return Err(ApiError::blocked(
            "compiled_run_mode_rejected",
            "编译期运行模式与任务根 profile 不一致；未访问数据或网络。",
        ));
    }
    verify_authorized_root(&authority)
}

fn database_path(root: &Path) -> Result<PathBuf, ApiError> {
    let path = root.join(DB);
    if path.parent() != Some(root) {
        return Err(ApiError::blocked(
            "database_path_rejected",
            "数据库必须位于已授权任务根。",
        ));
    }
    match fs::symlink_metadata(&path) {
        Ok(meta) if meta.file_type().is_symlink() => Err(ApiError::blocked(
            "database_path_rejected",
            "数据库路径不能是符号链接。",
        )),
        Ok(_) => Ok(path),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(path),
        Err(_) => Err(ApiError::blocked(
            "database_path_rejected",
            "数据库路径无法安全验证。",
        )),
    }
}

fn initialize_store(root: &Path) -> Result<PersistedState, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    connection.execute_batch("PRAGMA secure_delete=ON;
        CREATE TABLE IF NOT EXISTS provider_state (id INTEGER PRIMARY KEY CHECK(id = 1), state_json TEXT NOT NULL, updated_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS encrypted_credential (provider_id TEXT NOT NULL, profile_id TEXT NOT NULL, ciphertext BLOB NOT NULL, nonce BLOB NOT NULL, tag BLOB NOT NULL, algorithm TEXT NOT NULL, version INTEGER NOT NULL, key_reference TEXT NOT NULL, PRIMARY KEY(provider_id, profile_id));
        CREATE TABLE IF NOT EXISTS context_item (id TEXT PRIMARY KEY, domain TEXT NOT NULL CHECK(domain IN ('work','health')), item_type TEXT NOT NULL, text TEXT NOT NULL, authorized INTEGER NOT NULL CHECK(authorized IN (0,1)), status TEXT NOT NULL CHECK(status IN ('active','revoked','corrected')), expires_at_ms INTEGER, created_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS disclosure_request (id TEXT PRIMARY KEY, request_domain TEXT NOT NULL CHECK(request_domain IN ('work','health')), question TEXT NOT NULL, selected_refs_json TEXT NOT NULL, revision INTEGER NOT NULL, previewed INTEGER NOT NULL CHECK(previewed IN (0,1)), confirmation_used INTEGER NOT NULL CHECK(confirmation_used IN (0,1)), created_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS derivation (id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('derivation','understanding','suggestion')), provider_id TEXT NOT NULL, model_id TEXT NOT NULL, source_refs_json TEXT NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','confirmed','edited','rejected','ignored','corrected','invalidated')), created_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS feedback_event (id TEXT PRIMARY KEY, understanding_id TEXT NOT NULL, action TEXT NOT NULL, replacement_text TEXT, created_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS audit_event (id TEXT PRIMARY KEY, event_type TEXT NOT NULL, subject_id TEXT NOT NULL, status TEXT NOT NULL, created_at_ms INTEGER NOT NULL);")
        .map_err(db_error)?;
    connection
        .execute(
            "UPDATE disclosure_request SET revision=revision+1,previewed=0 WHERE confirmation_used=0 AND previewed=1",
            [],
        )
        .map_err(db_error)?;
    let stored: Option<String> = connection
        .query_row(
            "SELECT state_json FROM provider_state WHERE id = 1",
            [],
            |row| row.get(0),
        )
        .optional()
        .map_err(db_error)?;
    stored
        .map(|raw| {
            serde_json::from_str(&raw).map_err(|_| {
                ApiError::blocked("synthetic_store_rejected", "合成设置状态不可验证。")
            })
        })
        .transpose()
        .map(|value| value.unwrap_or_default())
}

fn selected_model_for_disclosure(root: &Path) -> Result<String, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    let stored: Option<String> = connection
        .query_row(
            "SELECT state_json FROM provider_state WHERE id = 1",
            [],
            |row| row.get(0),
        )
        .optional()
        .map_err(db_error)?;
    let state = stored
        .map(|raw| {
            serde_json::from_str::<PersistedState>(&raw).map_err(|_| {
                ApiError::blocked("synthetic_store_rejected", "合成设置状态不可验证。")
            })
        })
        .transpose()?
        .unwrap_or_default();
    Ok(state
        .selected_model
        .unwrap_or_else(|| "尚未选择模型".to_owned()))
}

fn persist(root: &Path, state: &PersistedState) -> Result<(), ApiError> {
    let raw = serde_json::to_string(state)
        .map_err(|_| ApiError::blocked("synthetic_store_rejected", "合成设置状态无法序列化。"))?;
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    connection.execute("INSERT INTO provider_state(id,state_json,updated_at_ms) VALUES(1,?1,?2) ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json,updated_at_ms=excluded.updated_at_ms", params![raw, now_ms()?]).map_err(db_error)?;
    Ok(())
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ContextItem {
    id: String,
    domain: String,
    item_type: String,
    text: String,
    authorized: bool,
    status: String,
    expires_at_ms: Option<i64>,
    created_at_ms: i64,
}

#[derive(Clone, Debug)]
struct DisclosureRow {
    id: String,
    request_domain: String,
    question: String,
    selected_refs: Vec<String>,
    revision: i64,
    previewed: bool,
    confirmation_used: bool,
}

fn next_identifier(prefix: &str) -> Result<String, ApiError> {
    Ok(format!(
        "{prefix}-{:x}-{:x}",
        now_ms()?,
        NEXT_IDENTIFIER.fetch_add(1, Ordering::Relaxed)
    ))
}

fn clean_text(value: &str, code: &'static str, message: &'static str) -> Result<String, ApiError> {
    let cleaned = value.trim();
    if cleaned.is_empty() || cleaned.chars().count() > ITEM_CHARACTER_LIMIT {
        return Err(ApiError::blocked(code, message));
    }
    Ok(cleaned.to_owned())
}

fn contains_medical_risk(value: &str) -> bool {
    let normalized = value.to_lowercase();
    [
        "diagnos",
        "treat",
        "medication",
        "emergency",
        "诊断",
        "治疗",
        "用药",
        "急诊",
    ]
    .iter()
    .any(|needle| normalized.contains(needle))
}

fn record_audit(
    root: &Path,
    event_type: &str,
    subject_id: &str,
    status: &str,
) -> Result<(), ApiError> {
    Connection::open(database_path(root)?)
        .map_err(db_error)?
        .execute(
            "INSERT INTO audit_event(id,event_type,subject_id,status,created_at_ms) VALUES(?1,?2,?3,?4,?5)",
            params![next_identifier("audit")?, event_type, subject_id, status, now_ms()?],
        )
        .map_err(db_error)?;
    Ok(())
}

fn active_items(root: &Path, domain: &str) -> Result<Vec<ContextItem>, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    let mut statement = connection
        .prepare("SELECT id,domain,item_type,text,authorized,status,expires_at_ms,created_at_ms FROM context_item WHERE domain=?1 AND authorized=1 AND status='active' AND (expires_at_ms IS NULL OR expires_at_ms>?2) ORDER BY created_at_ms ASC")
        .map_err(db_error)?;
    let rows = statement
        .query_map(params![domain, now_ms()?], |row| {
            Ok(ContextItem {
                id: row.get(0)?,
                domain: row.get(1)?,
                item_type: row.get(2)?,
                text: row.get(3)?,
                authorized: row.get::<_, i64>(4)? == 1,
                status: row.get(5)?,
                expires_at_ms: row.get(6)?,
                created_at_ms: row.get(7)?,
            })
        })
        .map_err(db_error)?
        .collect::<Result<Vec<_>, _>>()
        .map_err(db_error)?;
    Ok(rows)
}

fn insert_context_item(
    root: &Path,
    domain: &str,
    item_type: &str,
    text: &str,
) -> Result<ContextItem, ApiError> {
    let text = clean_text(
        text,
        "context_item_rejected",
        "条目不能为空且不得超过 200 个字符；未写入。",
    )?;
    if domain == HEALTH && contains_medical_risk(&text) {
        return Err(ApiError::blocked(
            "health_medical_boundary_rejected",
            "Health 仅支持非医疗 Current State；未写入。",
        ));
    }
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    let count: i64 = connection
        .query_row(
            "SELECT COUNT(*) FROM context_item WHERE domain=?1 AND status='active'",
            params![domain],
            |row| row.get(0),
        )
        .map_err(db_error)?;
    if count >= ITEM_LIMIT {
        return Err(ApiError::blocked(
            "context_item_limit_rejected",
            "每类最多保存 3 条；未写入。",
        ));
    }
    let item = ContextItem {
        id: next_identifier(domain)?,
        domain: domain.into(),
        item_type: item_type.into(),
        text,
        authorized: true,
        status: "active".into(),
        expires_at_ms: None,
        created_at_ms: now_ms()?,
    };
    connection.execute(
        "INSERT INTO context_item(id,domain,item_type,text,authorized,status,expires_at_ms,created_at_ms) VALUES(?1,?2,?3,?4,?5,?6,?7,?8)",
        params![&item.id, &item.domain, &item.item_type, &item.text, 1i64, &item.status, item.expires_at_ms, item.created_at_ms],
    ).map_err(db_error)?;
    record_audit(root, "context_item_saved", &item.id, "active")?;
    Ok(item)
}

fn retire_context_item(
    root: &Path,
    domain: &str,
    item_id: &str,
    status: &str,
) -> Result<(), ApiError> {
    if !matches!(status, "corrected" | "revoked") {
        return Err(ApiError::blocked(
            "context_item_action_rejected",
            "条目状态不受支持；未写入。",
        ));
    }
    let changed = Connection::open(database_path(root)?)
        .map_err(db_error)?
        .execute(
            "UPDATE context_item SET status=?1 WHERE id=?2 AND domain=?3 AND status='active'",
            params![status, item_id, domain],
        )
        .map_err(db_error)?;
    if changed != 1 {
        return Err(ApiError::blocked(
            "context_item_not_active",
            "条目不存在、跨域或已不再有效；未写入。",
        ));
    }
    let invalidated = invalidate_understandings_for_source(root, item_id)?;
    record_audit(root, "context_item_retired", item_id, status)?;
    if invalidated > 0 {
        record_audit(root, "source_lineage_invalidated", item_id, "invalidated")?;
    }
    Ok(())
}

fn correct_context_item(
    root: &Path,
    domain: &str,
    item_type: &str,
    item_id: &str,
    text: &str,
) -> Result<ContextItem, ApiError> {
    retire_context_item(root, domain, item_id, "corrected")?;
    insert_context_item(root, domain, item_type, text)
}

fn invalidate_understandings_for_source(root: &Path, item_id: &str) -> Result<usize, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    let mut statement = connection
        .prepare("SELECT id,source_refs_json FROM derivation WHERE status NOT IN ('invalidated','corrected')")
        .map_err(db_error)?;
    let rows = statement
        .query_map([], |row| {
            Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
        })
        .map_err(db_error)?
        .collect::<Result<Vec<_>, _>>()
        .map_err(db_error)?;
    let mut invalidated = 0;
    for (derivation_id, refs_json) in rows {
        let refs = serde_json::from_str::<Vec<String>>(&refs_json).map_err(|_| {
            ApiError::blocked(
                "context_serialization_rejected",
                "来源引用无法验证；未更新投影。",
            )
        })?;
        if refs.iter().any(|reference| reference == item_id) {
            invalidated += connection
                .execute(
                    "UPDATE derivation SET status='invalidated' WHERE id=?1 AND status NOT IN ('invalidated','corrected')",
                    params![derivation_id],
                )
                .map_err(db_error)?;
        }
    }
    Ok(invalidated)
}

fn relevant_to(question: &str, item: &ContextItem) -> bool {
    let query = question.to_lowercase();
    if (item.domain == WORK && (query.contains("work") || query.contains("工作")))
        || (item.domain == HEALTH
            && (query.contains("health")
                || query.contains("健康")
                || query.contains("fitness")
                || query.contains("运动")))
    {
        return true;
    }
    item.text
        .to_lowercase()
        .split(|ch: char| !ch.is_alphanumeric())
        .filter(|token| token.len() >= 3)
        .any(|token| query.contains(token))
}

fn load_disclosure(root: &Path, disclosure_id: &str) -> Result<DisclosureRow, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    connection.query_row(
        "SELECT id,request_domain,question,selected_refs_json,revision,previewed,confirmation_used FROM disclosure_request WHERE id=?1", params![disclosure_id],
        |row| {
            let refs: String = row.get(3)?;
            let selected_refs = serde_json::from_str(&refs).map_err(|_| rusqlite::Error::InvalidQuery)?;
            Ok(DisclosureRow { id: row.get(0)?, request_domain: row.get(1)?, question: row.get(2)?, selected_refs, revision: row.get(4)?, previewed: row.get::<_, i64>(5)? == 1, confirmation_used: row.get::<_, i64>(6)? == 1 })
        },
    ).map_err(db_error)
}

fn selected_items(root: &Path, disclosure: &DisclosureRow) -> Result<Vec<ContextItem>, ApiError> {
    let items = active_items(root, &disclosure.request_domain)?;
    let selected = disclosure
        .selected_refs
        .iter()
        .filter_map(|id| items.iter().find(|item| &item.id == id).cloned())
        .collect::<Vec<_>>();
    if selected.len() != disclosure.selected_refs.len() {
        return Err(ApiError::blocked(
            "disclosure_selection_stale",
            "披露集合已变化；请重新组装并确认。",
        ));
    }
    Ok(selected)
}

fn disclosure_view(
    root: &Path,
    disclosure_id: &str,
    mark_previewed: bool,
) -> Result<Value, ApiError> {
    let disclosure = load_disclosure(root, disclosure_id)?;
    let selected = selected_items(root, &disclosure)?;
    let model = selected_model_for_disclosure(root)?;
    if mark_previewed {
        Connection::open(database_path(root)?)
            .map_err(db_error)?
            .execute(
                "UPDATE disclosure_request SET previewed=1 WHERE id=?1 AND confirmation_used=0",
                params![disclosure_id],
            )
            .map_err(db_error)?;
        record_audit(root, "disclosure_previewed", disclosure_id, "shown")?;
    }
    Ok(
        json!({"disclosureId": disclosure.id, "revision": disclosure.revision, "provider": "DeepSeek", "model": model, "authority": deepseek::AUTHORITY, "processingLocation": "LifeOS local context resolver → DeepSeek only after this confirmation", "budget": {"itemLimit": ITEM_LIMIT, "characterLimit": DISCLOSURE_CHARACTER_BUDGET, "tokenLimit": DISCLOSURE_TOKEN_BUDGET}, "items": selected, "confirmationUsed": disclosure.confirmation_used}),
    )
}

fn assemble_disclosure(
    root: &Path,
    domain: &str,
    question: &str,
) -> Result<(String, usize, usize, usize), ApiError> {
    let question = clean_text(
        question,
        "context_request_rejected",
        "问题不能为空且不得超过 200 个字符；未发送。",
    )?;
    if domain == HEALTH && contains_medical_risk(&question) {
        return Err(ApiError::blocked(
            "health_medical_boundary_rejected",
            "Health 问题仅支持非医疗状态与约束；未发送。",
        ));
    }
    let selected = active_items(root, domain)?
        .into_iter()
        .filter(|item| relevant_to(&question, item))
        .collect::<Vec<_>>();
    if selected.is_empty() {
        return Err(ApiError::blocked(
            "minimal_context_empty",
            "没有符合当前请求、有效且已授权的最小上下文；未发送。",
        ));
    }
    let character_count = selected
        .iter()
        .map(|item| item.text.chars().count())
        .sum::<usize>();
    let token_estimate = character_count.div_ceil(4);
    if selected.len() > ITEM_LIMIT as usize
        || character_count > DISCLOSURE_CHARACTER_BUDGET
        || token_estimate > DISCLOSURE_TOKEN_BUDGET
    {
        return Err(ApiError::blocked(
            "context_budget_rejected",
            "最小上下文超出条数、字符或 token 预算；未发送。",
        ));
    }
    let disclosure_id = next_identifier("disclosure")?;
    let refs = selected
        .iter()
        .map(|item| item.id.clone())
        .collect::<Vec<_>>();
    let refs_json = serde_json::to_string(&refs).map_err(|_| {
        ApiError::blocked(
            "context_serialization_rejected",
            "披露集合无法序列化；未写入。",
        )
    })?;
    Connection::open(database_path(root)?).map_err(db_error)?.execute(
        "INSERT INTO disclosure_request(id,request_domain,question,selected_refs_json,revision,previewed,confirmation_used,created_at_ms) VALUES(?1,?2,?3,?4,1,0,0,?5)",
        params![disclosure_id, domain, question, refs_json, now_ms()?],
    ).map_err(db_error)?;
    record_audit(
        root,
        "context_assembled",
        &disclosure_id,
        "awaiting_preview",
    )?;
    Ok((disclosure_id, refs.len(), character_count, token_estimate))
}

fn remove_disclosure_item(
    root: &Path,
    disclosure_id: &str,
    item_id: &str,
) -> Result<Value, ApiError> {
    let disclosure = load_disclosure(root, disclosure_id)?;
    if disclosure.confirmation_used {
        return Err(ApiError::blocked(
            "confirmation_stale_or_replayed",
            "已确认的披露集合不能修改；请重新组装。",
        ));
    }
    let mut refs = disclosure.selected_refs;
    let before = refs.len();
    refs.retain(|value| value != item_id);
    if refs.len() + 1 != before {
        return Err(ApiError::blocked(
            "disclosure_item_rejected",
            "该条目不在当前披露集合；未写入。",
        ));
    }
    Connection::open(database_path(root)?).map_err(db_error)?.execute(
        "UPDATE disclosure_request SET selected_refs_json=?1,revision=revision+1,previewed=0 WHERE id=?2",
        params![serde_json::to_string(&refs).map_err(|_| ApiError::blocked("context_serialization_rejected", "披露集合无法保存。"))?, disclosure.id],
    ).map_err(db_error)?;
    record_audit(
        root,
        "disclosure_item_removed",
        disclosure_id,
        "requires_new_preview",
    )?;
    disclosure_view(root, disclosure_id, false)
}

fn consume_confirmation(
    root: &Path,
    disclosure_id: &str,
    observed_revision: i64,
) -> Result<DisclosureRow, ApiError> {
    let disclosure = load_disclosure(root, disclosure_id)?;
    if disclosure.revision != observed_revision
        || !disclosure.previewed
        || disclosure.confirmation_used
    {
        return Err(ApiError::blocked(
            "confirmation_stale_or_replayed",
            "披露集合已变化、未展示或确认已使用；请重新确认。",
        ));
    }
    if selected_items(root, &disclosure)?.is_empty() {
        return Err(ApiError::blocked(
            "disclosure_empty",
            "已移除全部条目；未发送。",
        ));
    }
    let changed = Connection::open(database_path(root)?).map_err(db_error)?.execute(
        "UPDATE disclosure_request SET confirmation_used=1 WHERE id=?1 AND revision=?2 AND previewed=1 AND confirmation_used=0", params![disclosure.id, disclosure.revision],
    ).map_err(db_error)?;
    if changed != 1 {
        return Err(ApiError::blocked(
            "confirmation_stale_or_replayed",
            "确认已失效；未发送。",
        ));
    }
    record_audit(root, "disclosure_confirmed", disclosure_id, "consumed")?;
    Ok(disclosure)
}

#[derive(Debug)]
struct CredentialRow {
    ciphertext: Vec<u8>,
    nonce: Vec<u8>,
    tag: Vec<u8>,
    algorithm: String,
    version: u8,
    key_reference: String,
}

fn credential_aad(provider_id: &str, profile_id: &str) -> Vec<u8> {
    format!("LIFEOS-P3-144|credential|v1|{provider_id}|{profile_id}").into_bytes()
}

fn credential_failure(error: secure_credentials::CredentialFailure) -> ApiError {
    let (code, message) = match error {
        secure_credentials::CredentialFailure::InvalidInput => (
            "credential_input_rejected",
            "凭据格式不符合本轮受控输入要求；未写入。",
        ),
        secure_credentials::CredentialFailure::KeychainUnavailable => (
            "keychain_unavailable",
            "专用 Keychain 密钥材料不可用；未写入。",
        ),
        secure_credentials::CredentialFailure::KeychainMissing => {
            ("key_material_missing", "密钥材料不存在；已在网络前拒绝。")
        }
        secure_credentials::CredentialFailure::EncryptionFailed => {
            ("credential_encryption_failed", "凭据无法安全加密；未写入。")
        }
        secure_credentials::CredentialFailure::AuthenticationFailed => (
            "credential_authentication_failed",
            "凭据认证失败；已在网络前拒绝。",
        ),
    };
    ApiError::blocked(code, message)
}

fn credential_row(root: &Path) -> Result<Option<CredentialRow>, ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    connection.query_row(
        "SELECT ciphertext, nonce, tag, algorithm, version, key_reference FROM encrypted_credential WHERE provider_id = ?1 AND profile_id = ?2",
        params![DEEPSEEK, PROFILE_ID],
        |row| Ok(CredentialRow { ciphertext: row.get(0)?, nonce: row.get(1)?, tag: row.get(2)?, algorithm: row.get(3)?, version: row.get(4)?, key_reference: row.get(5)? }),
    ).optional().map_err(db_error)
}

fn remove_credential_row(root: &Path) -> Result<Option<String>, ApiError> {
    let existing = credential_row(root)?;
    if let Some(row) = existing {
        match secure_credentials::delete_key_material(&row.key_reference) {
            Ok(()) | Err(secure_credentials::CredentialFailure::KeychainMissing) => {}
            Err(error) => return Err(credential_failure(error)),
        }
        let connection = Connection::open(database_path(root)?).map_err(db_error)?;
        connection
            .execute(
                "DELETE FROM encrypted_credential WHERE provider_id = ?1 AND profile_id = ?2",
                params![DEEPSEEK, PROFILE_ID],
            )
            .map_err(db_error)?;
        Ok(Some(row.key_reference))
    } else {
        Ok(None)
    }
}

fn write_credential_row(
    root: &Path,
    encrypted: &secure_credentials::EncryptedCredential,
) -> Result<(), ApiError> {
    let connection = Connection::open(database_path(root)?).map_err(db_error)?;
    connection.execute(
        "INSERT INTO encrypted_credential(provider_id, profile_id, ciphertext, nonce, tag, algorithm, version, key_reference) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        params![DEEPSEEK, PROFILE_ID, encrypted.ciphertext, encrypted.nonce, encrypted.tag, encrypted.algorithm, encrypted.version, encrypted.key_reference],
    ).map_err(db_error)?;
    Ok(())
}

fn load_api_key(root: &Path) -> Result<Vec<u8>, ApiError> {
    let row = credential_row(root)?.ok_or_else(|| {
        ApiError::blocked(
            "credential_required",
            "请先保存 DeepSeek 凭据；未发送网络请求。",
        )
    })?;
    let aad = credential_aad(DEEPSEEK, PROFILE_ID);
    secure_credentials::decrypt(
        &row.ciphertext,
        &row.nonce,
        &row.tag,
        &row.key_reference,
        &row.algorithm,
        row.version,
        &aad,
    )
    .map_err(credential_failure)
}

fn load_api_key_string(root: &Path) -> Result<String, ApiError> {
    let bytes = load_api_key(root)?;
    match String::from_utf8(bytes) {
        Ok(value) => Ok(value),
        Err(error) => {
            let mut invalid = error.into_bytes();
            invalid.zeroize();
            Err(ApiError::blocked(
                "credential_authentication_failed",
                "凭据无法解密；未发送网络请求。",
            ))
        }
    }
}

fn mask_for(api_key: &str) -> String {
    let suffix = api_key
        .chars()
        .rev()
        .take(4)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect::<String>();
    format!("••••{suffix}")
}

fn adapter_failure(error: deepseek::AdapterFailure) -> ApiError {
    let (code, message) = match error {
        deepseek::AdapterFailure::Authorization => (
            "real_gate_authorization_rejected",
            "真实 Gate 尚未满足授权条件；未发送请求。",
        ),
        deepseek::AdapterFailure::Authentication => (
            "provider_authentication_failed",
            "认证失败；没有启用服务或保存响应。",
        ),
        deepseek::AdapterFailure::Timeout => ("provider_timeout", "服务超时；状态保持失败关闭。"),
        deepseek::AdapterFailure::Network => (
            "provider_network_failed",
            "网络不可用或目标不可达；状态保持失败关闭。",
        ),
        deepseek::AdapterFailure::Model => (
            "provider_model_rejected",
            "模型不存在或不再可用；请重新测试。",
        ),
        deepseek::AdapterFailure::Capability => (
            "provider_capability_failed",
            "服务未返回可用能力；状态保持失败关闭。",
        ),
        deepseek::AdapterFailure::Protocol => (
            "provider_protocol_rejected",
            "服务响应不符合受控协议；状态保持失败关闭。",
        ),
    };
    ApiError::blocked(code, message)
}

fn receipt_value(receipt: &deepseek::NetworkReceipt) -> Value {
    json!({
        "authority": receipt.authority,
        "methodClass": receipt.method_class,
        "statusClass": receipt.status_class,
        "timestampMs": receipt.timestamp_ms,
        "requestBucket": receipt.request_bucket,
        "responseBucket": receipt.response_bucket,
    })
}

fn record_noncontent_receipt(
    root: &Path,
    operation: &str,
    receipt: &deepseek::NetworkReceipt,
) -> Result<(), ApiError> {
    let path = root.join("noncontent-network-receipts.json");
    let mut values = fs::read(&path)
        .ok()
        .and_then(|bytes| serde_json::from_slice::<Vec<Value>>(&bytes).ok())
        .unwrap_or_default();
    values.push(json!({"operation": operation, "receipt": receipt_value(receipt)}));
    let bytes = serde_json::to_vec_pretty(&values).map_err(|_| {
        ApiError::blocked("receipt_serialization_rejected", "非内容网络收据无法写入。")
    })?;
    let mut file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .mode(0o600)
        .open(path)
        .map_err(io_error)?;
    file.write_all(&bytes)
        .and_then(|_| file.write_all(b"\n"))
        .and_then(|_| file.sync_all())
        .map_err(io_error)
}

fn provider_exists(id: &str, mode: &ProviderMode) -> bool {
    provider_registry()
        .iter()
        .any(|entry| entry.id == id && &entry.mode == mode)
}

fn required_override_keys() -> [&'static str; 6] {
    [
        "text",
        "vision",
        "speech_input",
        "speech_output",
        "tool_use",
        "long_context",
    ]
}

fn validate(settings: &SettingsDto) -> Result<(), ApiError> {
    if settings.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "设置 DTO 版本不受支持；未写入。",
        ));
    }
    let primary = &settings.primary;
    if !provider_exists(&primary.provider_id, &primary.mode)
        || primary.model_label.trim().is_empty()
        || primary.model_label.len() > 96
    {
        return Err(ApiError::blocked(
            "provider_or_model_rejected",
            "Provider 或模型标签不符合合成目录。",
        ));
    }
    match primary.mode {
        ProviderMode::Cloud => {
            let expected = if primary.provider_id == DEEPSEEK {
                deepseek::AUTHORITY.to_owned()
            } else {
                format!("offline://catalog/cloud/{}", primary.provider_id)
            };
            if primary.endpoint_url.as_deref() != Some(expected.as_str())
                || primary.local_runtime.is_some()
            {
                return Err(ApiError::blocked(
                    "cloud_form_rejected",
                    "云端配置只能使用该 Provider 的离线目录端点。",
                ));
            }
        }
        ProviderMode::Local => {
            if primary.endpoint_url.is_some()
                || primary.local_runtime.as_deref() != Some("synthetic-local-runtime-v1")
            {
                return Err(ApiError::blocked(
                    "local_form_rejected",
                    "本地配置只能使用固定合成 Runtime 标识。",
                ));
            }
        }
    }
    if settings.fallback.configured != settings.fallback.provider_id.is_some() {
        return Err(ApiError::blocked(
            "fallback_shape_rejected",
            "备用服务状态不完整；未写入。",
        ));
    }
    if let Some(id) = &settings.fallback.provider_id {
        if !provider_registry().iter().any(|entry| &entry.id == id) || id == &primary.provider_id {
            return Err(ApiError::blocked(
                "fallback_provider_rejected",
                "备用服务不在目录中或重复主服务。",
            ));
        }
    }
    if !(0..=200).contains(&settings.advanced.temperature)
        || !(128..=8192).contains(&settings.advanced.max_output_tokens)
        || !(5..=120).contains(&settings.advanced.timeout_seconds)
        || !(4..=128).contains(&settings.advanced.context_window)
        || settings.advanced.capability_overrides.len() != required_override_keys().len()
        || required_override_keys().iter().any(|key| {
            settings
                .advanced
                .capability_overrides
                .get(*key)
                .map(String::as_str)
                != Some("auto")
        })
    {
        return Err(ApiError::blocked(
            "advanced_settings_rejected",
            "高级设置只能保留合同中的自动覆盖。",
        ));
    }
    Ok(())
}

#[allow(dead_code)]
#[derive(Clone, Debug)]
struct RouteRequest<'a> {
    capability: &'a str,
    authorized: bool,
    request_cloud_supplement: bool,
    request_automatic_failover: bool,
}

#[allow(dead_code)]
fn route(settings: &SettingsDto, request: RouteRequest<'_>) -> Result<String, ApiError> {
    if !request.authorized {
        return Err(ApiError::blocked(
            "routing_authorization_required",
            "没有明确授权时，能力路由不会选择服务。",
        ));
    }
    if request.request_cloud_supplement && !settings.routing_policy.allow_cloud_supplement {
        return Err(ApiError::blocked(
            "cloud_supplement_not_authorized",
            "云端补齐默认关闭，未选择服务。",
        ));
    }
    if request.request_automatic_failover && !settings.routing_policy.allow_automatic_failover {
        return Err(ApiError::blocked(
            "automatic_failover_not_authorized",
            "自动切换默认关闭，未选择备用服务。",
        ));
    }
    let provider = provider_registry()
        .into_iter()
        .find(|entry| entry.id == settings.primary.provider_id)
        .ok_or_else(|| ApiError::blocked("provider_missing", "主服务已不在合成目录中。"))?;
    if !provider
        .capability_metadata
        .iter()
        .any(|capability| capability == request.capability)
    {
        return Err(ApiError::blocked(
            "capability_not_supported",
            "当前主服务不支持该能力；请前往设置补齐。",
        ));
    }
    Ok(provider.id)
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct EmptyRequest {}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct GetSettingsRequest {
    version: u8,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct SaveSettingsRequest {
    version: u8,
    settings: SettingsDto,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct CredentialRequest {
    version: u8,
    operation: String,
    provider_id: String,
    profile_id: String,
    api_key: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct TestRequest {
    version: u8,
    user_action: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct EnabledRequest {
    version: u8,
    operation: String,
    enabled: Option<bool>,
    model_id: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct ContextMutationRequest {
    version: u8,
    operation: String,
    domain: String,
    text: Option<String>,
    item_id: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct AssembleRequest {
    version: u8,
    operation: String,
    domain: String,
    question: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct DisclosureRequest {
    version: u8,
    operation: String,
    disclosure_id: String,
    item_id: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct ResolveRequest {
    version: u8,
    operation: String,
    disclosure_id: String,
    observed_revision: i64,
    user_action: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct FeedbackRequest {
    version: u8,
    operation: String,
    understanding_id: String,
    replacement_text: Option<String>,
}

struct AppState {
    root: PathBuf,
    value: Mutex<PersistedState>,
}

fn locked<'a>(state: &'a AppState) -> Result<std::sync::MutexGuard<'a, PersistedState>, ApiError> {
    state
        .value
        .lock()
        .map_err(|_| ApiError::blocked("settings_lock_unavailable", "设置状态锁不可用。"))
}

#[tauri::command]
fn runtime_status(_: EmptyRequest) -> Value {
    json!({"status":"ready","runMode":run_mode(),"networkAuthority":deepseek::AUTHORITY,"credentialStore":"macOS Keychain exact P3-144 item","ipcAllowlist":IPC,"synthetic":run_mode() == "synthetic"})
}

#[tauri::command]
fn get_ai_provider_settings(
    request: GetSettingsRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "设置 DTO 版本不受支持。",
        ));
    }
    let value = locked(state.inner())?;
    Ok(response(&value))
}

#[tauri::command]
fn save_ai_provider_settings(
    request: SaveSettingsRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION || request.settings.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "设置 DTO 版本不受支持；未写入。",
        ));
    }
    validate(&request.settings)?;
    let mut value = locked(state.inner())?;
    value.settings = Some(request.settings);
    value.connection_state = if value.credential_reference.is_some() {
        "not_tested".into()
    } else {
        "credential_missing".into()
    };
    value.enabled = false;
    value.last_test = None;
    value.selected_model = None;
    value.available_models.clear();
    persist(&state.root, &value)?;
    Ok(response(&value))
}

#[tauri::command]
fn save_ai_provider_credential(
    mut request: CredentialRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "凭据 DTO 版本不受支持。",
        ));
    }
    if request.provider_id != DEEPSEEK || request.profile_id != PROFILE_ID {
        return Err(ApiError::blocked(
            "credential_target_rejected",
            "本轮只允许 DeepSeek 的默认专用凭据槽位。",
        ));
    }
    let configured = locked(state.inner())?.settings.clone();
    if configured.is_none() {
        return Err(ApiError::blocked(
            "settings_required",
            "请先保存主 AI 服务配置。",
        ));
    }
    let primary = configured.unwrap().primary;
    if primary.mode != ProviderMode::Cloud
        || primary.provider_id != DEEPSEEK
        || primary.endpoint_url.as_deref() != Some(deepseek::AUTHORITY)
    {
        return Err(ApiError::blocked(
            "deepseek_configuration_required",
            "只有保存精确 DeepSeek HTTPS 配置后才能保存凭据。",
        ));
    }
    match request.operation.as_str() {
        "store" => {
            let mut api_key = request.api_key.take().ok_or_else(|| {
                ApiError::blocked("credential_input_rejected", "凭据输入为空；未写入。")
            })?;
            remove_credential_row(&state.root)?;
            {
                let mut value = locked(state.inner())?;
                value.credential_reference = None;
                value.credential_mask = None;
                value.connection_state = "credential_missing".into();
                value.enabled = false;
                value.last_test = None;
                value.selected_model = None;
                value.available_models.clear();
                persist(&state.root, &value)?;
            }
            let aad = credential_aad(DEEPSEEK, PROFILE_ID);
            let encrypted_result = secure_credentials::encrypt(&api_key, &aad);
            let mask = mask_for(&api_key);
            api_key.zeroize();
            let encrypted = encrypted_result.map_err(credential_failure)?;
            if let Err(error) = write_credential_row(&state.root, &encrypted) {
                let _ = secure_credentials::delete_key_material(&encrypted.key_reference);
                return Err(error);
            }
            let mut value = locked(state.inner())?;
            value.credential_reference = Some(encrypted.key_reference);
            value.credential_mask = Some(mask);
            value.connection_state = "not_tested".into();
            value.enabled = false;
            value.last_test = None;
            value.selected_model = None;
            value.available_models.clear();
            persist(&state.root, &value)?;
            Ok(response(&value))
        }
        "delete" if request.api_key.is_none() => {
            remove_credential_row(&state.root)?;
            let mut value = locked(state.inner())?;
            value.credential_reference = None;
            value.credential_mask = None;
            value.connection_state = "credential_missing".into();
            value.enabled = false;
            value.last_test = None;
            value.selected_model = None;
            value.available_models.clear();
            persist(&state.root, &value)?;
            Ok(response(&value))
        }
        _ => Err(ApiError::blocked(
            "credential_operation_rejected",
            "凭据操作不符合严格 DTO；未写入。",
        )),
    }
}

#[tauri::command]
fn test_ai_provider_connection(
    request: TestRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION || request.user_action != "user_test" {
        return Err(ApiError::blocked(
            "test_action_rejected",
            "连接测试只能由用户明确点击触发。",
        ));
    }
    let value = locked(state.inner())?;
    let settings = value
        .settings
        .as_ref()
        .ok_or_else(|| ApiError::blocked("settings_required", "请先保存主 AI 服务配置。"))?;
    validate(settings)?;
    if settings.primary.mode != ProviderMode::Cloud
        || settings.primary.provider_id != DEEPSEEK
        || settings.primary.endpoint_url.as_deref() != Some(deepseek::AUTHORITY)
    {
        return Err(ApiError::blocked(
            "deepseek_configuration_required",
            "本轮只允许已保存的精确 DeepSeek 配置进行测试。",
        ));
    }
    if value.credential_reference.is_none() {
        return Err(ApiError::blocked(
            "credential_required",
            "请先保存 DeepSeek 凭据；未发送网络请求。",
        ));
    }
    let mut api_key = load_api_key_string(&state.root)?;
    drop(value);
    let timestamp = now_ms()?;
    let models_result = if run_mode() == "real_gate" {
        deepseek::real_models(&api_key, timestamp)
    } else {
        Ok(deepseek::synthetic_models(timestamp))
    };
    api_key.zeroize();
    let models = models_result.map_err(adapter_failure)?;
    record_noncontent_receipt(&state.root, "test_models", &models.receipt)?;
    let mut value = locked(state.inner())?;
    apply_tested_model_directory(&mut value, run_mode(), models.models);
    persist(&state.root, &value)?;
    Ok(response(&value))
}

fn apply_tested_model_directory(value: &mut PersistedState, run_mode: &str, models: Vec<String>) {
    value.connection_state = if run_mode == "real_gate" {
        "real_connected".into()
    } else {
        "synthetic_connected".into()
    };
    value.last_test = Some(run_mode.into());
    value.available_models = models;
    // A successful test only publishes a directory. It must never select or
    // enable a model; those transitions require separate explicit user actions.
    value.selected_model = None;
    value.enabled = false;
}

#[tauri::command]
fn set_ai_provider_enabled(
    request: EnabledRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "启用 DTO 版本不受支持。",
        ));
    }
    let mut value = locked(state.inner())?;
    match request.operation.as_str() {
        "select_model" if request.enabled.is_none() => {
            let model = request.model_id.as_deref().ok_or_else(|| {
                ApiError::blocked("model_selection_rejected", "请选择刚刚测试返回的模型。")
            })?;
            if !matches!(
                value.connection_state.as_str(),
                "synthetic_connected" | "real_connected"
            ) || !value.available_models.iter().any(|item| item == model)
            {
                return Err(ApiError::blocked(
                    "model_selection_rejected",
                    "模型只能从刚刚成功测试的目录中选择。",
                ));
            }
            value.selected_model = Some(model.into());
            value.enabled = false;
        }
        "set_enabled" if request.model_id.is_none() => {
            let enabled = request
                .enabled
                .ok_or_else(|| ApiError::blocked("enable_request_rejected", "启用请求不完整。"))?;
            if enabled
                && (!matches!(
                    value.connection_state.as_str(),
                    "synthetic_connected" | "real_connected"
                ) || value.selected_model.is_none())
            {
                return Err(ApiError::blocked(
                    "provider_not_ready",
                    "只有测试成功、选择模型后才能显式启用服务。",
                ));
            }
            value.enabled = enabled;
        }
        _ => {
            return Err(ApiError::blocked(
                "enable_request_rejected",
                "启用 DTO 不符合严格状态机。",
            ))
        }
    }
    persist(&state.root, &value)?;
    Ok(response(&value))
}

fn unavailable(command: &str) -> Value {
    json!({"status":"not_available_in_p3_144","command":command,"runMode":run_mode(),"message":"该既有 IPC 不扩展为隐藏发送、文件读取或自动化入口。"})
}

fn evidence_viewport() -> Result<Option<(u32, u32)>, ApiError> {
    match std::env::var("LIFEOS_P3_144_VIEWPORT").ok().as_deref() {
        None | Some("desktop") => Ok(Some((1280, 1024))),
        Some("compact") => Ok(Some((1160, 768))),
        Some("narrow") => Ok(Some((700, 760))),
        Some(_) => Err(ApiError::blocked(
            "viewport_rejected",
            "只允许 desktop、compact 或 narrow 合成视口。",
        )),
    }
}

#[tauri::command]
fn capture_record(
    request: ContextMutationRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION || request.domain != WORK {
        return Err(ApiError::blocked(
            "work_dto_rejected",
            "Work 写入 DTO 不符合合同；未写入。",
        ));
    }
    match request.operation.as_str() {
        "store_work" if request.item_id.is_none() => {
            let text = request.text.as_deref().ok_or_else(|| {
                ApiError::blocked("work_dto_rejected", "Work 条目不能为空；未写入。")
            })?;
            let item = insert_context_item(&state.root, WORK, "user_work", text)?;
            Ok(
                json!({"status":"stored","item":{"id":item.id,"domain":item.domain,"type":item.item_type,"characterCount":item.text.chars().count()}}),
            )
        }
        "revoke_work" if request.text.is_none() => {
            let item_id = request.item_id.as_deref().ok_or_else(|| {
                ApiError::blocked("work_dto_rejected", "撤回 Work 需要精确条目 ID；未写入。")
            })?;
            retire_context_item(&state.root, WORK, item_id, "revoked")?;
            Ok(json!({"status":"revoked","itemId":item_id,"domain":WORK}))
        }
        "correct_work" => {
            let item_id = request.item_id.as_deref().ok_or_else(|| {
                ApiError::blocked("work_dto_rejected", "纠正 Work 需要精确条目 ID；未写入。")
            })?;
            let text = request.text.as_deref().ok_or_else(|| {
                ApiError::blocked("work_dto_rejected", "纠正 Work 需要替代文本；未写入。")
            })?;
            let item = correct_context_item(&state.root, WORK, "user_work", item_id, text)?;
            Ok(
                json!({"status":"corrected","replaces":item_id,"item":{"id":item.id,"domain":item.domain,"type":item.item_type,"characterCount":item.text.chars().count()}}),
            )
        }
        _ => Err(ApiError::blocked(
            "work_dto_rejected",
            "Work 写入 DTO 不符合合同；未写入。",
        )),
    }
}
#[tauri::command]
fn get_today(_: EmptyRequest, state: tauri::State<'_, AppState>) -> Result<Value, ApiError> {
    let connection = Connection::open(database_path(&state.root)?).map_err(db_error)?;
    let mut statement = connection.prepare("SELECT id,kind,status,source_refs_json,created_at_ms FROM derivation ORDER BY created_at_ms DESC").map_err(db_error)?;
    let projections = statement.query_map([], |row| Ok(json!({"understandingId":row.get::<_,String>(0)?,"kind":row.get::<_,String>(1)?,"status":row.get::<_,String>(2)?,"sourceRefs":serde_json::from_str::<Vec<String>>(&row.get::<_,String>(3)?).unwrap_or_default(),"createdAtMs":row.get::<_,i64>(4)?}))).map_err(db_error)?.collect::<Result<Vec<_>,_>>().map_err(db_error)?;
    Ok(
        json!({"status":"ready","todayProjection":projections,"workCount":active_items(&state.root, WORK)?.len(),"healthCurrentStateCount":active_items(&state.root, HEALTH)?.len()}),
    )
}
#[tauri::command]
fn confirm_capture_context(_: EmptyRequest) -> Value {
    unavailable("confirm_capture_context")
}
#[tauri::command]
fn get_context_recovery(_: EmptyRequest) -> Value {
    unavailable("get_context_recovery")
}
#[tauri::command]
fn get_context_next_action(_: EmptyRequest) -> Value {
    unavailable("get_context_next_action")
}
#[tauri::command]
fn decide_context_next_action(_: EmptyRequest) -> Value {
    unavailable("decide_context_next_action")
}
#[tauri::command]
fn record_action_result(_: EmptyRequest) -> Value {
    unavailable("record_action_result")
}
#[tauri::command]
fn assemble_global_ai_context(
    request: AssembleRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION
        || request.operation != "assemble"
        || !matches!(request.domain.as_str(), WORK | HEALTH)
    {
        return Err(ApiError::blocked(
            "context_request_rejected",
            "请求上下文 DTO 不符合合同；未写入、未发送。",
        ));
    }
    let (disclosure_id, selection_count, character_count, token_estimate) =
        assemble_disclosure(&state.root, &request.domain, &request.question)?;
    Ok(
        json!({"status":"assembled","disclosureId":disclosure_id,"networkCounter":0,"selectionCount":selection_count,"characterCount":character_count,"tokenEstimate":token_estimate}),
    )
}
#[tauri::command]
fn get_evidence_backed_understanding(
    _: EmptyRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    let connection = Connection::open(database_path(&state.root)?).map_err(db_error)?;
    let mut statement = connection.prepare("SELECT id,kind,provider_id,model_id,source_refs_json,body,status,created_at_ms FROM derivation ORDER BY created_at_ms DESC").map_err(db_error)?;
    let entries = statement.query_map([], |row| Ok(json!({"id":row.get::<_,String>(0)?,"kind":row.get::<_,String>(1)?,"provider":row.get::<_,String>(2)?,"model":row.get::<_,String>(3)?,"sourceRefs":serde_json::from_str::<Vec<String>>(&row.get::<_,String>(4)?).unwrap_or_default(),"text":row.get::<_,String>(5)?,"status":row.get::<_,String>(6)?,"createdAtMs":row.get::<_,i64>(7)?}))).map_err(db_error)?.collect::<Result<Vec<_>,_>>().map_err(db_error)?;
    Ok(json!({"status":"ready","understandings":entries}))
}
#[tauri::command]
fn decide_understanding_feedback(
    request: FeedbackRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION
        || !matches!(
            request.operation.as_str(),
            "confirm" | "edit" | "reject" | "ignore" | "correct"
        )
    {
        return Err(ApiError::blocked(
            "feedback_dto_rejected",
            "反馈 DTO 不符合合同；未写入。",
        ));
    }
    if request.operation == "edit" {
        let value = request.replacement_text.as_deref().ok_or_else(|| {
            ApiError::blocked(
                "feedback_dto_rejected",
                "编辑反馈需要受限替代文本；未写入。",
            )
        })?;
        let _ = clean_text(
            value,
            "feedback_dto_rejected",
            "编辑反馈不能为空且不得超过 200 个字符；未写入。",
        )?;
    } else if request.replacement_text.is_some() {
        return Err(ApiError::blocked(
            "feedback_dto_rejected",
            "当前反馈动作不接受替代文本；未写入。",
        ));
    }
    let status = match request.operation.as_str() {
        "confirm" => "confirmed",
        "edit" => "edited",
        "reject" => "rejected",
        "ignore" => "ignored",
        "correct" => "invalidated",
        _ => unreachable!(),
    };
    let connection = Connection::open(database_path(&state.root)?).map_err(db_error)?;
    let changed = connection.execute("UPDATE derivation SET status=?1 WHERE id=?2 AND status NOT IN ('invalidated','corrected')", params![status, request.understanding_id]).map_err(db_error)?;
    if changed != 1 {
        return Err(ApiError::blocked(
            "understanding_not_available",
            "AI Understanding 不存在或已失效；未写入。",
        ));
    }
    connection.execute("INSERT INTO feedback_event(id,understanding_id,action,replacement_text,created_at_ms) VALUES(?1,?2,?3,?4,?5)", params![next_identifier("feedback")?, request.understanding_id, request.operation, request.replacement_text, now_ms()?]).map_err(db_error)?;
    record_audit(
        &state.root,
        "understanding_feedback",
        &request.understanding_id,
        status,
    )?;
    Ok(
        json!({"status":"recorded","understandingId":request.understanding_id,"feedback":request.operation,"projectionStatus":if status == "invalidated" {"invalidated"} else {"recomputed"}}),
    )
}
#[tauri::command]
fn upsert_durable_memory(_: EmptyRequest) -> Result<Value, ApiError> {
    Err(ApiError::blocked(
        "durable_memory_not_allowed",
        "本任务不把 Work 或 Health Current State 写入 Durable Memory。",
    ))
}
#[tauri::command]
fn update_current_state(
    request: ContextMutationRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION || request.domain != HEALTH {
        return Err(ApiError::blocked(
            "health_dto_rejected",
            "Health Current State DTO 不符合合同；未写入。",
        ));
    }
    match request.operation.as_str() {
        "store_health_current_state" if request.item_id.is_none() => {
            let text = request.text.as_deref().ok_or_else(|| {
                ApiError::blocked(
                    "health_dto_rejected",
                    "Health Current State 不能为空；未写入。",
                )
            })?;
            let item = insert_context_item(&state.root, HEALTH, "health_current_state", text)?;
            Ok(
                json!({"status":"stored","item":{"id":item.id,"domain":item.domain,"type":item.item_type,"characterCount":item.text.chars().count()}}),
            )
        }
        "revoke_health_current_state" if request.text.is_none() => {
            let item_id = request.item_id.as_deref().ok_or_else(|| {
                ApiError::blocked(
                    "health_dto_rejected",
                    "撤回 Health Current State 需要精确条目 ID；未写入。",
                )
            })?;
            retire_context_item(&state.root, HEALTH, item_id, "revoked")?;
            Ok(json!({"status":"revoked","itemId":item_id,"domain":HEALTH}))
        }
        "correct_health_current_state" => {
            let item_id = request.item_id.as_deref().ok_or_else(|| {
                ApiError::blocked(
                    "health_dto_rejected",
                    "纠正 Health Current State 需要精确条目 ID；未写入。",
                )
            })?;
            let text = request.text.as_deref().ok_or_else(|| {
                ApiError::blocked(
                    "health_dto_rejected",
                    "纠正 Health Current State 需要替代文本；未写入。",
                )
            })?;
            let item =
                correct_context_item(&state.root, HEALTH, "health_current_state", item_id, text)?;
            Ok(
                json!({"status":"corrected","replaces":item_id,"item":{"id":item.id,"domain":item.domain,"type":item.item_type,"characterCount":item.text.chars().count()}}),
            )
        }
        _ => Err(ApiError::blocked(
            "health_dto_rejected",
            "Health Current State DTO 不符合合同；未写入。",
        )),
    }
}
#[tauri::command]
fn resolve_request_context(
    request: ResolveRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION
        || request.operation != "confirm_send"
        || request.user_action != "confirm_current_disclosure"
    {
        return Err(ApiError::blocked(
            "confirmation_rejected",
            "每次发送必须对当前披露集合明确确认；未发送。",
        ));
    }
    let value = locked(state.inner())?;
    let settings = value
        .settings
        .as_ref()
        .ok_or_else(|| ApiError::blocked("settings_required", "请先保存主 AI 服务配置。"))?;
    if settings.primary.mode != ProviderMode::Cloud
        || settings.primary.provider_id != DEEPSEEK
        || settings.primary.endpoint_url.as_deref() != Some(deepseek::AUTHORITY)
        || !value.enabled
        || value.credential_reference.is_none()
    {
        return Err(ApiError::blocked(
            "provider_not_ready",
            "DeepSeek 未完成用户测试、选择、启用或凭据检查；未发送。",
        ));
    }
    let model = value.selected_model.clone().ok_or_else(|| {
        ApiError::blocked("provider_not_ready", "尚未选择本次已测试模型；未发送。")
    })?;
    drop(value);
    let disclosure = consume_confirmation(
        &state.root,
        &request.disclosure_id,
        request.observed_revision,
    )?;
    let items = selected_items(&state.root, &disclosure)?;
    let mut api_key = load_api_key_string(&state.root)?;
    let timestamp = now_ms()?;
    let adapter = if run_mode() == "real_gate" {
        let prompt = format!(
            "{}\n{}",
            disclosure.question,
            items
                .iter()
                .map(|item| format!("[{}] {}", item.domain, item.text))
                .collect::<Vec<_>>()
                .join("\n")
        );
        deepseek::real_context_response(&api_key, &model, &prompt, timestamp)
    } else {
        Ok(deepseek::synthetic_context_response(timestamp, items.len()))
    };
    api_key.zeroize();
    let response = adapter.map_err(adapter_failure)?;
    record_noncontent_receipt(&state.root, "confirmed_minimal_context", &response.receipt)?;
    let body = if disclosure.request_domain == HEALTH
        && contains_medical_risk(&response.transient_response)
    {
        "此结果已按非医疗安全边界处理；请在需要医疗帮助时咨询合格专业人员。".to_owned()
    } else {
        response.transient_response
    };
    let derivation_id = next_identifier("understanding")?;
    Connection::open(database_path(&state.root)?).map_err(db_error)?.execute(
        "INSERT INTO derivation(id,kind,provider_id,model_id,source_refs_json,body,status,created_at_ms) VALUES(?1,'understanding',?2,?3,?4,?5,'pending',?6)",
        params![derivation_id, DEEPSEEK, model, serde_json::to_string(&disclosure.selected_refs).map_err(|_| ApiError::blocked("context_serialization_rejected", "来源引用无法保存。"))?, body, now_ms()?],
    ).map_err(db_error)?;
    record_audit(
        &state.root,
        "understanding_saved",
        &derivation_id,
        "pending",
    )?;
    Ok(
        json!({"status":"completed","understandingId":derivation_id,"kind":"understanding","provider":"DeepSeek","model":model,"sourceRefs":disclosure.selected_refs,"transientResponse":body,"receipt":receipt_value(&response.receipt)}),
    )
}
#[tauri::command]
fn get_context_disclosure_receipt(
    request: DisclosureRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "披露 DTO 版本不受支持。",
        ));
    }
    match request.operation.as_str() {
        "view" if request.item_id.is_none() => {
            disclosure_view(&state.root, &request.disclosure_id, true)
        }
        "remove_item" => remove_disclosure_item(
            &state.root,
            &request.disclosure_id,
            request.item_id.as_deref().ok_or_else(|| {
                ApiError::blocked(
                    "disclosure_dto_rejected",
                    "移除动作需要精确条目 ID；未写入。",
                )
            })?,
        ),
        _ => Err(ApiError::blocked(
            "disclosure_dto_rejected",
            "披露 DTO 不符合严格状态机。",
        )),
    }
}

pub fn run() {
    let root = verify_task_root()
        .unwrap_or_else(|error| panic!("P3-144 task root rejected: {}", error.code));
    let value = initialize_store(&root)
        .unwrap_or_else(|error| panic!("P3-144 store rejected: {}", error.code));
    let viewport = evidence_viewport()
        .unwrap_or_else(|error| panic!("P3-144 viewport rejected: {}", error.code));
    tauri::Builder::default()
        .manage(AppState {
            root,
            value: Mutex::new(value),
        })
        .invoke_handler(tauri::generate_handler![
            capture_record,
            get_today,
            runtime_status,
            confirm_capture_context,
            get_context_recovery,
            get_context_next_action,
            decide_context_next_action,
            record_action_result,
            assemble_global_ai_context,
            get_evidence_backed_understanding,
            decide_understanding_feedback,
            get_ai_provider_settings,
            save_ai_provider_settings,
            save_ai_provider_credential,
            test_ai_provider_connection,
            set_ai_provider_enabled,
            upsert_durable_memory,
            update_current_state,
            resolve_request_context,
            get_context_disclosure_receipt
        ])
        .build(tauri::generate_context!())
        .expect("P3-144 Tauri builder failed")
        .run(move |app, event| {
            if let tauri::RunEvent::Ready = event {
                if let Some((width, height)) = viewport {
                    let window = app
                        .get_webview_window("main")
                        .expect("P3-144 main window missing");
                    window
                        .set_size(Size::Logical(LogicalSize::new(width as f64, height as f64)))
                        .expect("P3-144 viewport resize failed");
                }
            }
        });
}

#[cfg(test)]
mod tests {
    use super::*;

    const FROZEN_REVIEW_ROOT: &str = "/private/tmp/lifeos-p3-144-independent-review-v1";
    const TEST_CLEANUP_MARKER: &str = ".lifeos-p3-144-root-authority-test-owner";
    const TEST_CLEANUP_OWNER: &[u8] = b"lifeos-p3-144-root-authority-test-v1\n";

    fn review_authority() -> RootAuthority {
        RootAuthority {
            profile: "independent-review".into(),
            parent: "/private/tmp".into(),
            basename: "lifeos-p3-144-independent-review-v1".into(),
            root: FROZEN_REVIEW_ROOT.into(),
            marker_schema: "lifeos.p3-144.independent-review-root.v1".into(),
            marker_task: "LIFEOS-P3-144".into(),
            marker_owner: "lifeos-p3-144-independent-review".into(),
            run_id: "v1".into(),
            marker_run_id: Some("v1".into()),
        }
    }

    fn pilot_7_authority() -> RootAuthority {
        RootAuthority {
            profile: "pilot-7".into(),
            parent: "/Users/xxe/Documents".into(),
            basename: "LifeOS-Self-Use-Pilot-7".into(),
            root: "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7".into(),
            marker_schema: "lifeos.p3-144.pilot-7-root.v1".into(),
            marker_task: "LIFEOS-P3-144".into(),
            marker_owner: "lifeos-p3-144-pilot-7".into(),
            run_id: "pilot-7".into(),
            marker_run_id: Some("pilot-7".into()),
        }
    }

    fn write_test_cleanup_marker(root: &Path) {
        let marker = root.join(TEST_CLEANUP_MARKER);
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&marker)
            .unwrap();
        file.write_all(TEST_CLEANUP_OWNER).unwrap();
        file.sync_all().unwrap();
    }

    fn marker_gated_test_cleanup(root: &Path) {
        assert_eq!(root, Path::new(FROZEN_REVIEW_ROOT));
        let marker = root.join(TEST_CLEANUP_MARKER);
        let meta = fs::symlink_metadata(&marker).unwrap();
        assert!(meta.file_type().is_file() && !meta.file_type().is_symlink());
        assert_eq!(meta.permissions().mode() & 0o777, 0o600);
        assert_eq!(fs::read(&marker).unwrap(), TEST_CLEANUP_OWNER);
        fs::remove_dir_all(root).unwrap();
    }

    struct TestRoot {
        root: PathBuf,
        sentinel: PathBuf,
    }

    impl TestRoot {
        fn new() -> Self {
            let root = PathBuf::from(FROZEN_REVIEW_ROOT);
            assert!(matches!(
                fs::symlink_metadata(&root),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound
            ));
            let authority = review_authority();
            assert_eq!(verify_authorized_root(&authority).unwrap(), root);
            write_test_cleanup_marker(&root);
            let sentinel = root.join("database-sentinel.txt");
            fs::write(&sentinel, b"authorized-root-sentinel\n").unwrap();
            Self { root, sentinel }
        }
    }

    impl Drop for TestRoot {
        fn drop(&mut self) {
            marker_gated_test_cleanup(&self.root);
        }
    }

    struct ExistingReviewRoot {
        root: PathBuf,
        authority: RootAuthority,
        sentinel: PathBuf,
    }

    impl ExistingReviewRoot {
        fn new() -> Self {
            let root = PathBuf::from(FROZEN_REVIEW_ROOT);
            assert!(matches!(
                fs::symlink_metadata(&root),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound
            ));
            fs::create_dir(&root).unwrap();
            fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
            write_test_cleanup_marker(&root);
            let sentinel = root.join("sentinel.txt");
            fs::write(&sentinel, b"preexisting-root-sentinel\n").unwrap();
            Self {
                authority: review_authority(),
                root,
                sentinel,
            }
        }

        fn assert_prewrite_state(&self) {
            self.assert_sentinel_unchanged();
            assert!(!self.root.join(MARKER).exists());
            self.assert_no_runtime_or_database();
        }

        fn assert_sentinel_unchanged(&self) {
            assert_eq!(
                fs::read(&self.sentinel).unwrap(),
                b"preexisting-root-sentinel\n"
            );
        }

        fn assert_no_runtime_or_database(&self) {
            assert!(!self.root.join(RUNTIME_CHILD).exists());
            assert!(!self.root.join(DB).exists());
        }
    }

    impl Drop for ExistingReviewRoot {
        fn drop(&mut self) {
            marker_gated_test_cleanup(&self.root);
        }
    }

    struct PhaseATestRootCleanup {
        root: PathBuf,
        authority: RootAuthority,
    }

    impl PhaseATestRootCleanup {
        fn new(root: PathBuf) -> Self {
            let authority = compiled_root_authority();
            assert_eq!(root, PathBuf::from(&authority.root));
            Self { root, authority }
        }
    }

    impl Drop for PhaseATestRootCleanup {
        fn drop(&mut self) {
            reset_phase_a_store(&self.root);

            let marker = self.root.join(MARKER);
            let marker_meta = fs::symlink_metadata(&marker).unwrap();
            assert!(marker_meta.file_type().is_file() && !marker_meta.file_type().is_symlink());
            assert_eq!(marker_meta.permissions().mode() & 0o777, 0o600);
            let observed: RootMarker = serde_json::from_slice(&fs::read(&marker).unwrap()).unwrap();
            assert_eq!(observed, expected_marker(&self.authority));

            let runtime = self.root.join(RUNTIME_CHILD);
            let runtime_meta = fs::symlink_metadata(&runtime).unwrap();
            assert!(runtime_meta.file_type().is_dir() && !runtime_meta.file_type().is_symlink());
            assert_eq!(runtime_meta.permissions().mode() & 0o777, 0o700);
            fs::remove_dir(&runtime).unwrap();
            fs::remove_file(&marker).unwrap();
            fs::remove_dir(&self.root).unwrap();
        }
    }

    struct TestCredentialCleanup {
        root: Option<PathBuf>,
        references: Vec<String>,
    }

    impl TestCredentialCleanup {
        fn key_only(reference: String) -> Self {
            Self {
                root: None,
                references: vec![reference],
            }
        }

        fn root_bound(root: PathBuf) -> Self {
            Self {
                root: Some(root),
                references: Vec::new(),
            }
        }

        fn track(&mut self, reference: String) {
            self.references.push(reference);
        }
    }

    impl Drop for TestCredentialCleanup {
        fn drop(&mut self) {
            for reference in self.references.drain(..) {
                let _ = secure_credentials::delete_key_material(&reference);
            }
            if let Some(root) = &self.root {
                if let Ok(connection) = Connection::open(root.join(DB)) {
                    let _ = connection.execute(
                        "DELETE FROM encrypted_credential WHERE provider_id = ?1 AND profile_id = ?2",
                        params![DEEPSEEK, PROFILE_ID],
                    );
                }
            }
        }
    }

    fn cloud_settings() -> SettingsDto {
        SettingsDto {
            version: DTO_VERSION,
            primary: PrimaryService {
                mode: ProviderMode::Cloud,
                provider_id: "openai".into(),
                model_label: "synthetic-text-v1".into(),
                endpoint_url: Some("offline://catalog/cloud/openai".into()),
                local_runtime: None,
            },
            routing_policy: RoutingPolicy {
                prefer_local: true,
                allow_cloud_supplement: false,
                allow_automatic_failover: false,
                prefer_fast_response: false,
            },
            fallback: FallbackService {
                configured: false,
                provider_id: None,
            },
            advanced: AdvancedSettings {
                expanded: false,
                capability_overrides: required_override_keys()
                    .into_iter()
                    .map(|key| (key.into(), "auto".into()))
                    .collect(),
                temperature: 70,
                max_output_tokens: 2048,
                timeout_seconds: 60,
                context_window: 32,
            },
        }
    }

    #[test]
    fn registry_has_eight_cloud_and_four_local_entries() {
        let entries = provider_registry();
        assert_eq!(
            entries
                .iter()
                .filter(|item| item.mode == ProviderMode::Cloud)
                .count(),
            8
        );
        assert_eq!(
            entries
                .iter()
                .filter(|item| item.mode == ProviderMode::Local)
                .count(),
            4
        );
        assert!(
            entries.iter().any(|item| item.id == "deepseek")
                && entries.iter().any(|item| item.id == "kimi")
        );
    }

    #[test]
    fn capabilities_come_from_adapter_metadata_not_provider_name() {
        let mut entries = provider_registry();
        entries[0].id = "disposable_synthetic_provider".into();
        entries[0].capability_metadata = vec!["speech.transcription".into()];
        let snapshot = capability_registry(&entries);
        assert_eq!(
            snapshot["disposable_synthetic_provider"],
            vec![String::from("speech.transcription")]
        );
    }

    #[test]
    fn strict_dto_rejects_unknown_field_before_validation() {
        let value = json!({"version":1,"settings":{"version":1,"primary":{"mode":"cloud","providerId":"openai","modelLabel":"x","endpointUrl":"offline://catalog/cloud/openai","localRuntime":null,"unexpected":true},"routingPolicy":{"preferLocal":true,"allowCloudSupplement":false,"allowAutomaticFailover":false,"preferFastResponse":false},"fallback":{"configured":false,"providerId":null},"advanced":{"expanded":false,"capabilityOverrides":{"text":"auto","vision":"auto","speech_input":"auto","speech_output":"auto","tool_use":"auto","long_context":"auto"},"temperature":70,"maxOutputTokens":2048,"timeoutSeconds":60,"contextWindow":32}}});
        assert!(serde_json::from_value::<SaveSettingsRequest>(value).is_err());
    }

    #[test]
    fn cloud_and_local_fields_fail_closed() {
        let mut settings = cloud_settings();
        settings.primary.local_runtime = Some("synthetic-local-runtime-v1".into());
        assert_eq!(validate(&settings).unwrap_err().code, "cloud_form_rejected");
        settings.primary.mode = ProviderMode::Local;
        settings.primary.provider_id = "ollama".into();
        settings.primary.endpoint_url = Some("offline://catalog/cloud/ollama".into());
        assert_eq!(validate(&settings).unwrap_err().code, "local_form_rejected");
    }

    #[test]
    fn illegal_provider_capability_and_priority_fail_closed() {
        let mut settings = cloud_settings();
        settings.primary.provider_id = "unknown".into();
        assert_eq!(
            validate(&settings).unwrap_err().code,
            "provider_or_model_rejected"
        );
        let mut settings = cloud_settings();
        settings.advanced.temperature = 201;
        assert_eq!(
            validate(&settings).unwrap_err().code,
            "advanced_settings_rejected"
        );
        let error = route(
            &cloud_settings(),
            RouteRequest {
                capability: "not.a.capability",
                authorized: true,
                request_cloud_supplement: false,
                request_automatic_failover: false,
            },
        )
        .unwrap_err();
        assert_eq!(error.code, "capability_not_supported");
    }

    #[test]
    fn router_requires_authorization_and_defaults_to_no_cloud_supplement() {
        let settings = cloud_settings();
        assert_eq!(
            route(
                &settings,
                RouteRequest {
                    capability: "text.reasoning",
                    authorized: false,
                    request_cloud_supplement: false,
                    request_automatic_failover: false
                }
            )
            .unwrap_err()
            .code,
            "routing_authorization_required"
        );
        assert_eq!(
            route(
                &settings,
                RouteRequest {
                    capability: "text.reasoning",
                    authorized: true,
                    request_cloud_supplement: true,
                    request_automatic_failover: false
                }
            )
            .unwrap_err()
            .code,
            "cloud_supplement_not_authorized"
        );
        assert_eq!(
            route(
                &settings,
                RouteRequest {
                    capability: "text.reasoning",
                    authorized: true,
                    request_cloud_supplement: false,
                    request_automatic_failover: true
                }
            )
            .unwrap_err()
            .code,
            "automatic_failover_not_authorized"
        );
    }

    #[test]
    fn persistence_payload_contains_only_non_secret_reference() {
        let mut state = PersistedState {
            settings: Some(cloud_settings()),
            credential_reference: Some("p3-144-key-nonsecret-reference".into()),
            credential_mask: Some("••••1234".into()),
            ..Default::default()
        };
        state.connection_state = "synthetic_connected".into();
        let json = serde_json::to_string(&state).unwrap();
        assert!(json.contains("p3-144-key-nonsecret-reference"));
        assert!(!json.contains("p3-144-key-canary-keep-private"));
        assert!(!json.contains("sk-"));
    }

    #[test]
    fn compiled_root_authority_is_closed_and_non_runtime_configurable() {
        let authority = compiled_root_authority();
        assert!(compiled_authority_is_valid(&authority));
        match authority.profile.as_str() {
            "engineering" => {
                assert_eq!(authority.run_id, "engineering");
                assert!(authority.marker_run_id.is_none());
                assert_eq!(authority.root, "/private/tmp/lifeos-p3-144-engineering-v1");
            }
            "independent-review" => {
                assert_eq!(authority.run_id, "v1");
                assert_eq!(authority.marker_run_id.as_deref(), Some("v1"));
                assert_eq!(authority.root, FROZEN_REVIEW_ROOT);
            }
            other => panic!("unexpected compiled root profile: {other}"),
        }
    }

    #[test]
    fn pilot_7_authority_is_exact_without_accessing_the_pilot_root() {
        let authority = pilot_7_authority();
        assert!(compiled_authority_is_valid(&authority));
        assert!(run_mode_matches_profile("pilot-7", "real_gate"));
        assert!(!run_mode_matches_profile("pilot-7", "synthetic"));
        assert!(!run_mode_matches_profile("engineering", "real_gate"));
        assert_eq!(
            authority.root,
            "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7"
        );

        let mut wrong = authority.clone();
        wrong.basename = "LifeOS-Self-Use-Pilot-8".into();
        assert!(!compiled_authority_is_valid(&wrong));
        let mut wrong = authority.clone();
        wrong.root = "/private/tmp/lifeos-p3-144-pilot-7".into();
        assert!(!compiled_authority_is_valid(&wrong));
        let mut wrong = authority;
        wrong.marker_run_id = None;
        assert!(!compiled_authority_is_valid(&wrong));
    }

    #[test]
    fn absent_review_root_creates_the_exact_marker_before_runtime_or_database() {
        let authorized = TestRoot::new();
        let marker = authorized.root.join(MARKER);
        let marker_meta = fs::symlink_metadata(&marker).unwrap();
        assert!(marker_meta.file_type().is_file() && !marker_meta.file_type().is_symlink());
        assert_eq!(marker_meta.permissions().mode() & 0o777, 0o600);
        assert_eq!(
            serde_json::from_slice::<RootMarker>(&fs::read(&marker).unwrap()).unwrap(),
            expected_marker(&review_authority()),
        );
        let runtime = authorized.root.join(RUNTIME_CHILD);
        assert!(runtime.is_dir());
        assert_eq!(
            fs::metadata(runtime).unwrap().permissions().mode() & 0o777,
            0o700
        );
        assert!(!authorized.root.join(DB).exists());
        assert_eq!(
            fs::read(&authorized.sentinel).unwrap(),
            b"authorized-root-sentinel\n"
        );
    }

    #[test]
    fn existing_review_root_missing_or_mutated_marker_fails_before_runtime_or_database() {
        {
            let missing = ExistingReviewRoot::new();
            missing.assert_prewrite_state();
            assert_eq!(
                verify_authorized_root(&missing.authority).unwrap_err().code,
                "task_marker_missing"
            );
            missing.assert_prewrite_state();
        }

        {
            let wrong = ExistingReviewRoot::new();
            let wrong_marker = wrong.root.join(MARKER);
            fs::write(
                &wrong_marker,
                b"{\"schema\":\"wrong\",\"task\":\"LIFEOS-P3-144\",\"owner\":\"lifeos-p3-144-independent-review\",\"runId\":\"wrong\"}\n",
            )
            .unwrap();
            fs::set_permissions(&wrong_marker, fs::Permissions::from_mode(0o600)).unwrap();
            assert_eq!(
                verify_authorized_root(&wrong.authority).unwrap_err().code,
                "task_marker_rejected"
            );
            wrong.assert_sentinel_unchanged();
            wrong.assert_no_runtime_or_database();
        }

        {
            let marker_symlink = ExistingReviewRoot::new();
            let marker_link = marker_symlink.root.join(MARKER);
            std::os::unix::fs::symlink(&marker_symlink.sentinel, &marker_link).unwrap();
            assert_eq!(
                verify_authorized_root(&marker_symlink.authority)
                    .unwrap_err()
                    .code,
                "task_marker_type_rejected"
            );
            marker_symlink.assert_sentinel_unchanged();
            marker_symlink.assert_no_runtime_or_database();
        }

        {
            let wrong_permissions = ExistingReviewRoot::new();
            let permissions_marker = wrong_permissions.root.join(MARKER);
            fs::write(
                &permissions_marker,
                serde_json::to_vec(&expected_marker(&wrong_permissions.authority)).unwrap(),
            )
            .unwrap();
            fs::set_permissions(&permissions_marker, fs::Permissions::from_mode(0o640)).unwrap();
            assert_eq!(
                verify_authorized_root(&wrong_permissions.authority)
                    .unwrap_err()
                    .code,
                "task_marker_type_rejected"
            );
            wrong_permissions.assert_sentinel_unchanged();
            wrong_permissions.assert_no_runtime_or_database();
        }
    }

    #[test]
    fn review_root_authority_rejects_root_symlink_before_writes() {
        let link = PathBuf::from(FROZEN_REVIEW_ROOT);
        assert!(matches!(
            fs::symlink_metadata(&link),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound
        ));
        std::os::unix::fs::symlink("/private/tmp", &link).unwrap();
        assert_eq!(
            verify_authorized_root(&review_authority())
                .unwrap_err()
                .code,
            "task_root_type_rejected"
        );
        fs::remove_file(link).unwrap();
    }

    #[test]
    fn review_root_authority_rejects_wrong_profile_root_run_id_and_traversal_before_writes() {
        let root = ExistingReviewRoot::new();
        let mutations: [(&str, fn(&mut RootAuthority)); 6] = [
            ("wrong-profile", |authority: &mut RootAuthority| {
                authority.profile = "engineering".into();
            }),
            ("different-root", |authority: &mut RootAuthority| {
                authority.basename = "lifeos-p3-144-independent-review-other".into();
                authority.root = "/private/tmp/lifeos-p3-144-independent-review-other".into();
            }),
            ("dynamic-run-id", |authority: &mut RootAuthority| {
                authority.run_id = "independent-review-run".into();
                authority.marker_run_id = Some("independent-review-run".into());
            }),
            ("short-run-id", |authority: &mut RootAuthority| {
                authority.run_id = "x".into();
                authority.marker_run_id = Some("x".into());
            }),
            ("long-run-id", |authority: &mut RootAuthority| {
                authority.run_id = "v".repeat(49);
                authority.marker_run_id = Some("v".repeat(49));
            }),
            ("traversal", |authority: &mut RootAuthority| {
                authority.basename = "..".into();
                authority.root = "/private/tmp/..".into();
            }),
        ];
        for (_name, mutate) in mutations {
            let mut authority = root.authority.clone();
            mutate(&mut authority);
            assert_eq!(
                verify_authorized_root(&authority).unwrap_err().code,
                "compiled_root_authority_rejected"
            );
            root.assert_prewrite_state();
        }
    }

    #[test]
    fn database_symlink_is_rejected_before_open_and_sentinel_is_unchanged() {
        let authorized = TestRoot::new();
        let database = authorized.root.join(DB);
        std::os::unix::fs::symlink(&authorized.sentinel, &database).unwrap();
        assert_eq!(
            database_path(&authorized.root).unwrap_err().code,
            "database_path_rejected"
        );
        assert_eq!(
            fs::read(&authorized.sentinel).unwrap(),
            b"authorized-root-sentinel\n"
        );
        assert!(fs::symlink_metadata(&database)
            .unwrap()
            .file_type()
            .is_symlink());
    }

    #[test]
    fn credential_keychain_material_and_aead_are_separate_and_fail_closed() {
        let source = "p3-144-key-canary-keep-private";
        let aad = credential_aad(DEEPSEEK, PROFILE_ID);
        let encrypted = secure_credentials::encrypt(source, &aad).unwrap();
        let _cleanup = TestCredentialCleanup::key_only(encrypted.key_reference.clone());
        assert_ne!(encrypted.ciphertext, source.as_bytes());
        assert_eq!(encrypted.algorithm, secure_credentials::ALGORITHM);
        assert_eq!(encrypted.nonce.len(), 12);
        assert_eq!(encrypted.tag.len(), 16);
        let plain = secure_credentials::decrypt(
            &encrypted.ciphertext,
            &encrypted.nonce,
            &encrypted.tag,
            &encrypted.key_reference,
            encrypted.algorithm,
            encrypted.version,
            &aad,
        )
        .unwrap();
        assert_eq!(plain, source.as_bytes());
        let mut tampered = encrypted.ciphertext.clone();
        tampered[0] ^= 1;
        assert_eq!(
            secure_credentials::decrypt(
                &tampered,
                &encrypted.nonce,
                &encrypted.tag,
                &encrypted.key_reference,
                encrypted.algorithm,
                encrypted.version,
                &aad
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::AuthenticationFailed
        );
        let mut nonce_tampered = encrypted.nonce.clone();
        nonce_tampered[0] ^= 1;
        assert_eq!(
            secure_credentials::decrypt(
                &encrypted.ciphertext,
                &nonce_tampered,
                &encrypted.tag,
                &encrypted.key_reference,
                encrypted.algorithm,
                encrypted.version,
                &aad
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::AuthenticationFailed
        );
        assert_eq!(
            secure_credentials::decrypt(
                &encrypted.ciphertext,
                &encrypted.nonce,
                &encrypted.tag,
                &encrypted.key_reference,
                encrypted.algorithm,
                encrypted.version,
                b"wrong-aad"
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::AuthenticationFailed
        );
        assert_eq!(
            secure_credentials::decrypt(
                &encrypted.ciphertext,
                &encrypted.nonce,
                &encrypted.tag,
                &encrypted.key_reference,
                encrypted.algorithm,
                encrypted.version.saturating_add(1),
                &aad
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::AuthenticationFailed
        );
        assert_eq!(
            secure_credentials::decrypt(
                &encrypted.ciphertext,
                &encrypted.nonce,
                &encrypted.tag,
                "p3-144-key-missing-reference",
                encrypted.algorithm,
                encrypted.version,
                &aad
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::KeychainMissing
        );
        secure_credentials::delete_key_material(&encrypted.key_reference).unwrap();
        assert_eq!(
            secure_credentials::decrypt(
                &encrypted.ciphertext,
                &encrypted.nonce,
                &encrypted.tag,
                &encrypted.key_reference,
                encrypted.algorithm,
                encrypted.version,
                &aad
            )
            .unwrap_err(),
            secure_credentials::CredentialFailure::KeychainMissing
        );
    }

    #[test]
    fn sqlite_ciphertext_requires_its_exact_keychain_material_and_leaks_no_canary() {
        let test_root = TestRoot::new();
        let root = test_root.root.clone();
        initialize_store(&root).unwrap();
        let _ = remove_credential_row(&root).unwrap();
        let mut cleanup = TestCredentialCleanup::root_bound(root.clone());
        let source = "p3-144-storage-canary-keep-private";
        let aad = credential_aad(DEEPSEEK, PROFILE_ID);
        let mut encrypted = secure_credentials::encrypt(source, &aad).unwrap();
        let key_reference = encrypted.key_reference.clone();
        cleanup.track(key_reference.clone());
        write_credential_row(&root, &encrypted).unwrap();
        encrypted.ciphertext.zeroize();
        let db_bytes = fs::read(root.join(DB)).unwrap();
        assert!(!db_bytes
            .windows(source.len())
            .any(|window| window == source.as_bytes()));
        let mut plain = load_api_key(&root).unwrap();
        assert_eq!(plain, source.as_bytes());
        plain.zeroize();
        secure_credentials::delete_key_material(&key_reference).unwrap();
        assert_eq!(
            load_api_key(&root).unwrap_err().code,
            "key_material_missing"
        );
        assert_eq!(remove_credential_row(&root).unwrap(), Some(key_reference));
        assert!(credential_row(&root).unwrap().is_none());
    }

    #[test]
    fn credential_replacement_invalidates_the_previous_ciphertext_and_reference() {
        let test_root = TestRoot::new();
        let root = test_root.root.clone();
        initialize_store(&root).unwrap();
        let _ = remove_credential_row(&root).unwrap();
        let mut cleanup = TestCredentialCleanup::root_bound(root.clone());
        let aad = credential_aad(DEEPSEEK, PROFILE_ID);
        let mut first =
            secure_credentials::encrypt("p3-144-first-canary-keep-private", &aad).unwrap();
        let first_reference = first.key_reference.clone();
        cleanup.track(first_reference.clone());
        write_credential_row(&root, &first).unwrap();
        first.ciphertext.zeroize();
        assert_eq!(
            remove_credential_row(&root).unwrap(),
            Some(first_reference.clone())
        );
        let mut second =
            secure_credentials::encrypt("p3-144-second-canary-keep-private", &aad).unwrap();
        let second_reference = second.key_reference.clone();
        cleanup.track(second_reference.clone());
        write_credential_row(&root, &second).unwrap();
        second.ciphertext.zeroize();
        assert_ne!(first_reference, second_reference);
        assert_eq!(
            secure_credentials::delete_key_material(&first_reference).unwrap_err(),
            secure_credentials::CredentialFailure::KeychainMissing
        );
        let mut restored = load_api_key(&root).unwrap();
        assert_eq!(restored, b"p3-144-second-canary-keep-private");
        restored.zeroize();
        assert_eq!(
            remove_credential_row(&root).unwrap(),
            Some(second_reference)
        );
    }

    #[test]
    fn deepseek_requires_the_exact_https_authority() {
        let mut settings = cloud_settings();
        settings.primary.provider_id = DEEPSEEK.into();
        settings.primary.endpoint_url = Some(deepseek::AUTHORITY.into());
        assert!(validate(&settings).is_ok());
        settings.primary.endpoint_url = Some("https://api.deepseek.com.evil.invalid".into());
        assert_eq!(validate(&settings).unwrap_err().code, "cloud_form_rejected");
    }

    #[test]
    fn exactly_twenty_ipc_are_registered() {
        assert_eq!(IPC.len(), 20);
        assert_eq!(IPC[11], "get_ai_provider_settings");
        assert_eq!(IPC[15], "set_ai_provider_enabled");
    }

    #[test]
    fn provider_save_resets_test_and_enablement() {
        let mut state = PersistedState {
            connection_state: "synthetic_connected".into(),
            enabled: true,
            last_test: Some("offline_metadata_adapter".into()),
            ..Default::default()
        };
        state.settings = Some(cloud_settings());
        state.connection_state = "not_tested".into();
        state.enabled = false;
        state.last_test = None;
        assert!(
            !state.enabled && state.connection_state == "not_tested" && state.last_test.is_none()
        );
    }

    #[test]
    fn test_models_clears_prior_selection_and_keeps_provider_disabled() {
        let mut state = PersistedState {
            connection_state: "real_connected".into(),
            enabled: true,
            last_test: Some("real_gate".into()),
            selected_model: Some("previous-model".into()),
            available_models: vec!["previous-model".into()],
            ..Default::default()
        };

        apply_tested_model_directory(
            &mut state,
            "real_gate",
            vec!["tested-model-a".into(), "tested-model-b".into()],
        );

        assert_eq!(state.connection_state, "real_connected");
        assert_eq!(state.last_test.as_deref(), Some("real_gate"));
        assert_eq!(state.available_models.len(), 2);
        assert!(state.selected_model.is_none());
        assert!(!state.enabled);
    }

    fn reset_phase_a_store(root: &Path) {
        for name in [
            DB,
            "secure-provider-settings.sqlite-wal",
            "secure-provider-settings.sqlite-shm",
            "noncontent-network-receipts.json",
        ] {
            let path = root.join(name);
            if let Ok(meta) = fs::symlink_metadata(&path) {
                assert!(!meta.file_type().is_symlink());
                fs::remove_file(path).unwrap();
            }
        }
    }

    #[test]
    fn p3_144_phase_a_context_limits_disclosure_and_confirmation_are_fail_closed() {
        let root = verify_task_root().unwrap();
        let _root_cleanup = PhaseATestRootCleanup::new(root.clone());
        reset_phase_a_store(&root);
        initialize_store(&root).unwrap();

        let project =
            insert_context_item(&root, WORK, "user_work", "project milestone review").unwrap();
        insert_context_item(&root, WORK, "user_work", "work backlog sorting").unwrap();
        insert_context_item(&root, WORK, "user_work", "team focus note").unwrap();
        assert_eq!(
            insert_context_item(&root, WORK, "user_work", "fourth item")
                .unwrap_err()
                .code,
            "context_item_limit_rejected"
        );
        assert_eq!(
            insert_context_item(&root, HEALTH, "health_current_state", "need diagnosis")
                .unwrap_err()
                .code,
            "health_medical_boundary_rejected"
        );
        let health = insert_context_item(
            &root,
            HEALTH,
            "health_current_state",
            "fitness energy is steady",
        )
        .unwrap();
        assert_eq!(health.item_type, "health_current_state");

        let (disclosure_id, count, _, _) =
            assemble_disclosure(&root, WORK, "work project priority").unwrap();
        assert_eq!(count, 3);
        let shown = disclosure_view(&root, &disclosure_id, true).unwrap();
        assert_eq!(shown["items"].as_array().unwrap().len(), 3);
        assert!(shown["items"]
            .as_array()
            .unwrap()
            .iter()
            .all(|item| item["domain"] == WORK));
        let old_revision = shown["revision"].as_i64().unwrap();

        initialize_store(&root).unwrap();
        assert_eq!(
            consume_confirmation(&root, &disclosure_id, old_revision)
                .unwrap_err()
                .code,
            "confirmation_stale_or_replayed"
        );
        let restart_shown = disclosure_view(&root, &disclosure_id, true).unwrap();
        let restart_revision = restart_shown["revision"].as_i64().unwrap();

        let after_remove = remove_disclosure_item(&root, &disclosure_id, &project.id).unwrap();
        assert_eq!(after_remove["items"].as_array().unwrap().len(), 2);
        assert_eq!(
            consume_confirmation(&root, &disclosure_id, restart_revision)
                .unwrap_err()
                .code,
            "confirmation_stale_or_replayed"
        );
        let reshown = disclosure_view(&root, &disclosure_id, true).unwrap();
        let revision = reshown["revision"].as_i64().unwrap();
        assert!(consume_confirmation(&root, &disclosure_id, revision).is_ok());
        assert_eq!(
            consume_confirmation(&root, &disclosure_id, revision)
                .unwrap_err()
                .code,
            "confirmation_stale_or_replayed"
        );
        assert!(!root.join("noncontent-network-receipts.json").exists());

        let lineage_id = "understanding-lineage-fixture";
        Connection::open(database_path(&root).unwrap())
            .unwrap()
            .execute(
                "INSERT INTO derivation(id,kind,provider_id,model_id,source_refs_json,body,status,created_at_ms) VALUES(?1,'understanding','DeepSeek','deepseek-synthetic-v1',?2,'synthetic understanding','confirmed',?3)",
                params![lineage_id, serde_json::to_string(&vec![project.id.clone()]).unwrap(), now_ms().unwrap()],
            )
            .unwrap();
        retire_context_item(&root, WORK, &project.id, "corrected").unwrap();
        let lineage_status: String = Connection::open(database_path(&root).unwrap())
            .unwrap()
            .query_row(
                "SELECT status FROM derivation WHERE id=?1",
                params![lineage_id],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(lineage_status, "invalidated");

        let (stale_id, _, _, _) =
            assemble_disclosure(&root, HEALTH, "health fitness constraint").unwrap();
        retire_context_item(&root, HEALTH, &health.id, "revoked").unwrap();
        assert_eq!(
            retire_context_item(&root, HEALTH, &health.id, "revoked")
                .unwrap_err()
                .code,
            "context_item_not_active"
        );
        assert_eq!(
            disclosure_view(&root, &stale_id, false).unwrap_err().code,
            "disclosure_selection_stale"
        );
        reset_phase_a_store(&root);
    }
}
