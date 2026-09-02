use crate::{deepseek, secure_credentials};
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
use zeroize::Zeroize;

const TASK_ROOT: &str = "/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1";
const MARKER: &str = ".lifeos-p3-143-owner.json";
const DB: &str = "secure-provider-settings.sqlite";
const DTO_VERSION: u8 = 1;
const PROFILE_ID: &str = "default";
const DEEPSEEK: &str = "deepseek";
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
    match std::env::var("LIFEOS_P3_143_REAL_GATE").ok().as_deref() {
        Some("enabled") => "real_gate",
        _ => "synthetic",
    }
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

#[derive(Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
struct RootMarker {
    schema: String,
    task: String,
    owner: String,
}

fn expected_marker() -> RootMarker {
    RootMarker {
        schema: "lifeos.p3-143.real-ai-secure-activation-root.v1".into(),
        task: "LIFEOS-P3-143".into(),
        owner: "lifeos-p3-143-real-ai-secure-activation-v1".into(),
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
            "任务 marker 不属于 P3-143。",
        ));
    }
    Ok(root)
}

fn initialize_store(root: &Path) -> Result<PersistedState, ApiError> {
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
    connection.execute_batch("PRAGMA secure_delete=ON; CREATE TABLE IF NOT EXISTS provider_state (id INTEGER PRIMARY KEY CHECK(id = 1), state_json TEXT NOT NULL, updated_at_ms INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS encrypted_credential (provider_id TEXT NOT NULL, profile_id TEXT NOT NULL, ciphertext BLOB NOT NULL, nonce BLOB NOT NULL, tag BLOB NOT NULL, algorithm TEXT NOT NULL, version INTEGER NOT NULL, key_reference TEXT NOT NULL, PRIMARY KEY(provider_id, profile_id));")
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

fn persist(root: &Path, state: &PersistedState) -> Result<(), ApiError> {
    let raw = serde_json::to_string(state)
        .map_err(|_| ApiError::blocked("synthetic_store_rejected", "合成设置状态无法序列化。"))?;
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
    connection.execute("INSERT INTO provider_state(id,state_json,updated_at_ms) VALUES(1,?1,?2) ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json,updated_at_ms=excluded.updated_at_ms", params![raw, now_ms()?]).map_err(db_error)?;
    Ok(())
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
    format!("LIFEOS-P3-143|credential|v1|{provider_id}|{profile_id}").into_bytes()
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
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
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
        let connection = Connection::open(root.join(DB)).map_err(db_error)?;
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
    let connection = Connection::open(root.join(DB)).map_err(db_error)?;
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
struct CanaryRequest {
    version: u8,
    operation: String,
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
    json!({"status":"ready","runMode":run_mode(),"networkAuthority":deepseek::AUTHORITY,"credentialStore":"macOS Keychain exact P3-143 item","ipcAllowlist":IPC,"synthetic":run_mode() == "synthetic"})
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
    json!({"status":"not_available_in_p3_143","command":command,"runMode":run_mode(),"message":"该既有 IPC 未在本任务扩展。"})
}

fn evidence_viewport() -> Result<Option<(u32, u32)>, ApiError> {
    match std::env::var("LIFEOS_P3_143_VIEWPORT").ok().as_deref() {
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
fn assemble_global_ai_context(
    request: CanaryRequest,
    state: tauri::State<'_, AppState>,
) -> Result<Value, ApiError> {
    if request.version != DTO_VERSION || request.operation != "send_fixed_canary" {
        return Err(ApiError::blocked(
            "canary_action_rejected",
            "只允许固定无个人含义的 canary 动作。",
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
    {
        return Err(ApiError::blocked(
            "canary_not_enabled",
            "只有明确启用的 DeepSeek 主服务才能发送固定 canary。",
        ));
    }
    let selected_model = value.selected_model.clone().ok_or_else(|| {
        ApiError::blocked(
            "model_selection_required",
            "请先从刚刚测试的目录中选择模型。",
        )
    })?;
    drop(value);
    let mut api_key = load_api_key_string(&state.root)?;
    let timestamp = now_ms()?;
    let send_result = if run_mode() == "real_gate" {
        deepseek::real_canary(&api_key, &selected_model, timestamp)
    } else {
        Ok(deepseek::synthetic_canary(timestamp))
    };
    api_key.zeroize();
    let response = send_result.map_err(adapter_failure)?;
    record_noncontent_receipt(&state.root, "send_fixed_canary", &response.receipt)?;
    Ok(json!({
        "status": "completed",
        "transientResponse": response.transient_response,
        "disclosure": {"provider": "DeepSeek", "authority": deepseek::AUTHORITY, "input": "fixed_nonpersonal_canary", "retained": false},
        "receipt": receipt_value(&response.receipt),
    }))
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
    json!({"provider":"DeepSeek","authority":deepseek::AUTHORITY,"input":"fixed_nonpersonal_canary_only","personalContext":false,"responseRetention":"transient_ui_only"})
}

pub fn run() {
    let root = verify_task_root()
        .unwrap_or_else(|error| panic!("P3-143 task root rejected: {}", error.code));
    let value = initialize_store(&root)
        .unwrap_or_else(|error| panic!("P3-143 store rejected: {}", error.code));
    let viewport = evidence_viewport()
        .unwrap_or_else(|error| panic!("P3-143 viewport rejected: {}", error.code));
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
        .expect("P3-143 Tauri builder failed")
        .run(move |app, event| {
            if let tauri::RunEvent::Ready = event {
                if let Some((width, height)) = viewport {
                    let window = app
                        .get_webview_window("main")
                        .expect("P3-143 main window missing");
                    window
                        .set_size(Size::Logical(LogicalSize::new(width as f64, height as f64)))
                        .expect("P3-143 viewport resize failed");
                }
            }
        });
}

#[cfg(test)]
mod tests {
    use super::*;

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
            credential_reference: Some("p3-143-key-nonsecret-reference".into()),
            credential_mask: Some("••••1234".into()),
            ..Default::default()
        };
        state.connection_state = "synthetic_connected".into();
        let json = serde_json::to_string(&state).unwrap();
        assert!(json.contains("p3-143-key-nonsecret-reference"));
        assert!(!json.contains("p3-143-key-canary-keep-private"));
        assert!(!json.contains("sk-"));
    }

    #[test]
    fn credential_keychain_material_and_aead_are_separate_and_fail_closed() {
        let source = "p3-143-key-canary-keep-private";
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
                "p3-143-key-missing-reference",
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
        let root = verify_task_root().unwrap();
        initialize_store(&root).unwrap();
        let _ = remove_credential_row(&root).unwrap();
        let mut cleanup = TestCredentialCleanup::root_bound(root.clone());
        let source = "p3-143-storage-canary-keep-private";
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
        let root = verify_task_root().unwrap();
        initialize_store(&root).unwrap();
        let _ = remove_credential_row(&root).unwrap();
        let mut cleanup = TestCredentialCleanup::root_bound(root.clone());
        let aad = credential_aad(DEEPSEEK, PROFILE_ID);
        let mut first =
            secure_credentials::encrypt("p3-143-first-canary-keep-private", &aad).unwrap();
        let first_reference = first.key_reference.clone();
        cleanup.track(first_reference.clone());
        write_credential_row(&root, &first).unwrap();
        first.ciphertext.zeroize();
        assert_eq!(
            remove_credential_row(&root).unwrap(),
            Some(first_reference.clone())
        );
        let mut second =
            secure_credentials::encrypt("p3-143-second-canary-keep-private", &aad).unwrap();
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
        assert_eq!(restored, b"p3-143-second-canary-keep-private");
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
}
