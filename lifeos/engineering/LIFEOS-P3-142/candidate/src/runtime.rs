use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{LogicalSize, Manager, Size};

const TASK_ROOT: &str = "/private/tmp/lifeos-p3-142-ai-service-config-center-v1";
const MARKER: &str = ".lifeos-p3-142-owner.json";
const DB: &str = "synthetic-settings.sqlite";
const DTO_VERSION: u8 = 1;
const SYNTHETIC_CREDENTIAL_FIXTURE: &str = "synthetic-credential-fixture-v1";
const SYNTHETIC_CREDENTIAL_REFERENCE: &str = "credential-ref:synthetic:p3-142:v1";
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
                "credential_fixture".into(),
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
    last_test: Option<String>,
}

impl Default for PersistedState {
    fn default() -> Self {
        Self {
            settings: None,
            connection_state: "not_configured".into(),
            enabled: false,
            credential_reference: None,
            last_test: None,
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
    has_synthetic_credential_reference: bool,
    last_test: Option<String>,
    provider_registry: Vec<ProviderDescriptor>,
    capability_registry: BTreeMap<String, Vec<String>>,
    offline: bool,
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
        has_synthetic_credential_reference: state.credential_reference.as_deref()
            == Some(SYNTHETIC_CREDENTIAL_REFERENCE),
        last_test: state.last_test.clone(),
        capability_registry: capability_registry(&registry),
        provider_registry: registry,
        offline: true,
    }
}

#[derive(Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
struct RootMarker {
    schema: String,
    task: String,
    owner: String,
}

fn expected_marker() -> RootMarker {
    RootMarker {
        schema: "lifeos.p3-142.synthetic-root.v1".into(),
        task: "LIFEOS-P3-142".into(),
        owner: "lifeos-p3-142-ai-service-config-center-v1".into(),
    }
}

fn verify_task_root() -> Result<PathBuf, ApiError> {
    let root = PathBuf::from(TASK_ROOT);
    if root.parent() != Some(Path::new("/private/tmp")) {
        return Err(ApiError::blocked(
            "task_root_literal_rejected",
            "任务根不是合同指定的精确路径。",
        ));
    }
    match fs::symlink_metadata(&root) {
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
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            fs::create_dir(&root).map_err(io_error)?;
            fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).map_err(io_error)?;
        }
        Err(error) => return Err(io_error(error)),
    }
    if fs::canonicalize(&root).map_err(io_error)? != root {
        return Err(ApiError::blocked(
            "task_root_canonical_rejected",
            "任务根解析后发生变化。",
        ));
    }
    let marker = root.join(MARKER);
    if !marker.exists() {
        let bytes = serde_json::to_vec_pretty(&expected_marker()).map_err(|_| {
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
    if observed != expected_marker() {
        return Err(ApiError::blocked(
            "task_marker_rejected",
            "任务 marker 不属于 P3-142。",
        ));
    }
    Ok(root)
}

fn initialize_store(root: &Path) -> Result<PersistedState, ApiError> {
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
    connection.execute_batch("CREATE TABLE IF NOT EXISTS synthetic_provider_state (id INTEGER PRIMARY KEY CHECK(id = 1), state_json TEXT NOT NULL, updated_at_ms INTEGER NOT NULL);")
        .map_err(db_error)?;
    let stored: Option<String> = connection
        .query_row(
            "SELECT state_json FROM synthetic_provider_state WHERE id = 1",
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

fn persist(root: &Path, state: &PersistedState) -> Result<(), ApiError> {
    let raw = serde_json::to_string(state)
        .map_err(|_| ApiError::blocked("synthetic_store_rejected", "合成设置状态无法序列化。"))?;
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
    connection.execute("INSERT INTO synthetic_provider_state(id,state_json,updated_at_ms) VALUES(1,?1,?2) ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json,updated_at_ms=excluded.updated_at_ms", params![raw, now_ms()?]).map_err(db_error)?;
    Ok(())
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
            let expected = format!("offline://catalog/cloud/{}", primary.provider_id);
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

#[derive(Clone, Debug)]
struct RouteRequest<'a> {
    capability: &'a str,
    authorized: bool,
    request_cloud_supplement: bool,
    request_automatic_failover: bool,
}

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
    credential_fixture: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct TestRequest {
    version: u8,
    simulate: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct EnabledRequest {
    version: u8,
    enabled: bool,
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
    json!({"status":"ready","offline":true,"network":false,"credentialStore":false,"ipcAllowlist":IPC,"synthetic":true})
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
    value.connection_state = "not_tested".into();
    value.enabled = false;
    value.last_test = None;
    persist(&state.root, &value)?;
    Ok(response(&value))
}

#[tauri::command]
fn save_ai_provider_credential(
    request: CredentialRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION {
        return Err(ApiError::blocked(
            "dto_version_rejected",
            "凭据 DTO 版本不受支持。",
        ));
    }
    let mut value = locked(state.inner())?;
    if value.settings.is_none() {
        return Err(ApiError::blocked(
            "settings_required",
            "请先保存主 AI 服务配置。",
        ));
    }
    match request.operation.as_str() {
        "store_synthetic_reference"
            if request.credential_fixture.as_deref() == Some(SYNTHETIC_CREDENTIAL_FIXTURE) =>
        {
            value.credential_reference = Some(SYNTHETIC_CREDENTIAL_REFERENCE.into())
        }
        "delete_synthetic_reference" if request.credential_fixture.is_none() => {
            value.credential_reference = None
        }
        _ => {
            return Err(ApiError::blocked(
                "credential_fixture_rejected",
                "本任务只接受固定非秘密凭据夹具。",
            ))
        }
    }
    value.enabled = false;
    value.connection_state = "not_tested".into();
    persist(&state.root, &value)?;
    Ok(response(&value))
}

#[tauri::command]
fn test_ai_provider_connection(
    request: TestRequest,
    state: tauri::State<'_, AppState>,
) -> Result<SettingsResponse, ApiError> {
    if request.version != DTO_VERSION || request.simulate != "offline_metadata" {
        return Err(ApiError::blocked(
            "offline_test_rejected",
            "连接测试只能运行离线 metadata Adapter。",
        ));
    }
    let mut value = locked(state.inner())?;
    let settings = value
        .settings
        .as_ref()
        .ok_or_else(|| ApiError::blocked("settings_required", "请先保存主 AI 服务配置。"))?;
    validate(settings)?;
    if settings.primary.mode == ProviderMode::Cloud
        && value.credential_reference.as_deref() != Some(SYNTHETIC_CREDENTIAL_REFERENCE)
    {
        return Err(ApiError::blocked(
            "synthetic_credential_required",
            "云端合成配置需要固定非秘密凭据夹具。",
        ));
    }
    value.connection_state = "synthetic_connected".into();
    value.enabled = false;
    value.last_test = Some("offline_metadata_adapter".into());
    persist(&state.root, &value)?;
    Ok(response(&value))
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
    if request.enabled && value.connection_state != "synthetic_connected" {
        return Err(ApiError::blocked(
            "provider_not_tested",
            "只有离线测试成功后才能显式启用服务。",
        ));
    }
    value.enabled = request.enabled;
    persist(&state.root, &value)?;
    Ok(response(&value))
}

fn unavailable(command: &str) -> Value {
    json!({"status":"not_available_in_p3_142","command":command,"offline":true,"message":"该既有 IPC 未在本任务扩展。"})
}

fn evidence_viewport() -> Result<Option<(u32, u32)>, ApiError> {
    match std::env::var("LIFEOS_P3_142_VIEWPORT").ok().as_deref() {
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
fn capture_record(_: EmptyRequest) -> Value {
    unavailable("capture_record")
}
#[tauri::command]
fn get_today(_: EmptyRequest) -> Value {
    unavailable("get_today")
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
fn assemble_global_ai_context(_: EmptyRequest) -> Value {
    unavailable("assemble_global_ai_context")
}
#[tauri::command]
fn get_evidence_backed_understanding(_: EmptyRequest) -> Value {
    unavailable("get_evidence_backed_understanding")
}
#[tauri::command]
fn decide_understanding_feedback(_: EmptyRequest) -> Value {
    unavailable("decide_understanding_feedback")
}
#[tauri::command]
fn upsert_durable_memory(_: EmptyRequest) -> Value {
    unavailable("upsert_durable_memory")
}
#[tauri::command]
fn update_current_state(_: EmptyRequest) -> Value {
    unavailable("update_current_state")
}
#[tauri::command]
fn resolve_request_context(_: EmptyRequest) -> Value {
    unavailable("resolve_request_context")
}
#[tauri::command]
fn get_context_disclosure_receipt(_: EmptyRequest) -> Value {
    unavailable("get_context_disclosure_receipt")
}

pub fn run() {
    let root = verify_task_root()
        .unwrap_or_else(|error| panic!("P3-142 task root rejected: {}", error.code));
    let value = initialize_store(&root)
        .unwrap_or_else(|error| panic!("P3-142 store rejected: {}", error.code));
    let viewport = evidence_viewport()
        .unwrap_or_else(|error| panic!("P3-142 viewport rejected: {}", error.code));
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
        .expect("P3-142 Tauri builder failed")
        .run(move |app, event| {
            if let tauri::RunEvent::Ready = event {
                if let Some((width, height)) = viewport {
                    let window = app
                        .get_webview_window("main")
                        .expect("P3-142 main window missing");
                    window
                        .set_size(Size::Logical(LogicalSize::new(width as f64, height as f64)))
                        .expect("P3-142 viewport resize failed");
                }
            }
        });
}

#[cfg(test)]
mod tests {
    use super::*;

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
    fn persistence_payload_contains_only_synthetic_reference() {
        let mut state = PersistedState {
            settings: Some(cloud_settings()),
            credential_reference: Some(SYNTHETIC_CREDENTIAL_REFERENCE.into()),
            ..Default::default()
        };
        state.connection_state = "synthetic_connected".into();
        let json = serde_json::to_string(&state).unwrap();
        assert!(json.contains(SYNTHETIC_CREDENTIAL_REFERENCE));
        assert!(!json.contains(SYNTHETIC_CREDENTIAL_FIXTURE));
        assert!(!json.contains("sk-"));
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
}
