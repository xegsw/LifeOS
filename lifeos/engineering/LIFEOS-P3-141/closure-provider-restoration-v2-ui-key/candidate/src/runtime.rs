use rusqlite::{params, Connection, OpenFlags, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use std::ffi::{c_char, c_void, CString};
use std::fs;
use std::fs::OpenOptions;
use std::io::{Read, Write};
use std::net::{IpAddr, SocketAddr, TcpStream, ToSocketAddrs};
use std::os::unix::fs::{MetadataExt, PermissionsExt};
use std::os::unix::fs::OpenOptionsExt;
use std::path::{Component, Path, PathBuf};
use std::sync::{Mutex, OnceLock};
#[cfg(test)] use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::{LogicalSize, Manager, Size};

mod memory_context;
mod today_intelligence;

const DB: &str = "capture.sqlite";
const OWNERSHIP_MARKER: &str = ".lifeos-p3-141-owner.json";
const ROOT: Option<&str> = option_env!("LIFEOS_RUNTIME_ROOT");
const MODE: Option<&str> = option_env!("LIFEOS_INPUT_MODE");
// build.rs creates this only after it has verified a committed, review-owned
// Revision-2 independent Pass asset. Synthetic review builds get no binding at all; an
// arbitrary environment string can never enter the real-mode branch.
include!(concat!(env!("OUT_DIR"), "/phase_c_v2_receipt_binding.rs"));
const IPC: [&str; 20] = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings", "set_ai_provider_session_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"];
const CONTEXT: &str = "ctx:project:local-work-self-use";
const PROJECT: &str = "local-work-self-use";
const PERSON: &str = "person:local-owner";
const SYN_TEXT: &str = "整理 LifeOS Context Recovery 合成验收记录。";
const SYN_KEY: &str = "p3-141-synthetic-capture-001";
const SYN_SHORT: &str = "LifeOS Context Recovery 合成记录。";
const SYN_SHORT_KEY: &str = "p3-141-synthetic-insufficient-001";
const SYN_EDIT: &str = "整理并复核 LifeOS Context Recovery 合成验收记录。";
const SYN_RESULT: &str = "已完成合成验收记录整理与复核。";
const REAL_RESULT: &str = "用户在本地标记为已完成。";
const REAL_ACTION: &str = "确认此 Work Capture 的下一步。";

const SCHEMA: &str = r#"
PRAGMA journal_mode=DELETE; PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runtime_meta(mode TEXT PRIMARY KEY,contract TEXT NOT NULL,created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,person_id TEXT NOT NULL,source_id TEXT NOT NULL,artifact_version TEXT NOT NULL,source_available INTEGER NOT NULL,generation_current INTEGER NOT NULL,tombstoned INTEGER NOT NULL,authorized INTEGER NOT NULL,evidence_ready INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS captures(id TEXT PRIMARY KEY,content TEXT NOT NULL,created_at_ms INTEGER NOT NULL,source TEXT NOT NULL,source_id TEXT NOT NULL,artifact_version TEXT NOT NULL,idem_key TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS work_trial_days(day_key TEXT PRIMARY KEY,capture_id TEXT NOT NULL UNIQUE,created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS capture_project_links(capture_id TEXT PRIMARY KEY,context_id TEXT NOT NULL,link_status TEXT NOT NULL CHECK(link_status IN ('candidate','confirmed','rejected')));
CREATE TABLE IF NOT EXISTS candidate_actions(id TEXT PRIMARY KEY,capture_id TEXT NOT NULL,candidate_text TEXT NOT NULL,candidate_state TEXT NOT NULL CHECK(candidate_state IN ('active','accepted','rejected','deferred')),created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY,candidate_id TEXT NOT NULL UNIQUE,action_text TEXT NOT NULL,confirmation_kind TEXT NOT NULL,action_state TEXT NOT NULL CHECK(action_state IN ('open','completed')),created_at_ms INTEGER NOT NULL,confirmed_at_ms INTEGER GENERATED ALWAYS AS (created_at_ms) STORED);
CREATE TABLE IF NOT EXISTS action_results(id TEXT PRIMARY KEY,action_id TEXT NOT NULL UNIQUE,result_text TEXT NOT NULL,idem_key TEXT NOT NULL UNIQUE,created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT,target_kind TEXT NOT NULL,target_id TEXT NOT NULL,decision TEXT NOT NULL,idem_key TEXT NOT NULL UNIQUE,detail TEXT NOT NULL,created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT NOT NULL,target_id TEXT NOT NULL,detail TEXT NOT NULL,created_at_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS understandings(id TEXT PRIMARY KEY,request_id TEXT NOT NULL UNIQUE,kind TEXT NOT NULL CHECK(kind IN ('observation','suggestion')),summary TEXT NOT NULL,provider TEXT NOT NULL,model TEXT NOT NULL,evidence_refs_json TEXT NOT NULL,uncertainty TEXT NOT NULL,created_at_ms INTEGER NOT NULL);
PRAGMA user_version=141;
"#;

#[derive(Clone, Copy, Debug, PartialEq, Eq)] enum InputMode { Synthetic, Real }
impl InputMode {
    fn value(self) -> &'static str { if self == Self::Real { "real_self_use" } else { "synthetic" } }
    fn capture_prefix(self) -> &'static str { if self == Self::Real { "capture:p3-141:real:" } else { "capture:p3-141:synthetic:" } }
    fn candidate_prefix(self) -> &'static str { if self == Self::Real { "candidate:p3-141:real:" } else { "candidate:p3-141:synthetic:" } }
    fn action_prefix(self) -> &'static str { if self == Self::Real { "action:p3-141:real:" } else { "action:p3-141:synthetic:" } }
    fn source(self) -> &'static str { if self == Self::Real { "SRC-P3-141-WORK-LOCAL-001" } else { "SRC-P3-141-SYN-WORK-001" } }
    fn artifact(self) -> &'static str { if self == Self::Real { "ART-P3-141-WORK-SELF-USE-001@v1" } else { "ART-P3-141-SYN-WORK-001@v1" } }
    fn limit(self) -> i64 { if self == Self::Real { 14 } else { 2 } }
    fn idempotency_prefix(self) -> &'static str { if self == Self::Real { "p3-141-real-ui-" } else { "p3-141-" } }
}
fn mode() -> Result<InputMode, Error> { match (COMPILED_BUILD_MODE, MODE, VALIDATED_PHASE_C_V2_RECEIPT_SHA256) { ("synthetic_review", Some("synthetic"), None) => Ok(InputMode::Synthetic), ("phase_c_real", Some("real_self_use"), Some(binding)) if binding.len() == 64 => Ok(InputMode::Real), ("phase_c_real", Some("real_self_use"), _) => Err(Error::blocked("phase_c_v2_independent_pass_required", "真实模式需要已验证的独立 Revision-2 Pass receipt；没有探测真实根。")), _ => Err(Error::blocked("input_mode_rejected", "构建模式与输入模式必须明确且匹配。")) } }

#[derive(Debug, Serialize)] struct Error { status: &'static str, code: &'static str, message: &'static str }
impl Error { fn blocked(code: &'static str, message: &'static str) -> Self { eprintln!("ipc_result status=blocked code={code}"); Self { status: "blocked", code, message } } }
fn io(_: std::io::Error) -> Error { Error::blocked("path_boundary_unavailable", "本地路径边界无法验证；未显示成功。") }
fn sql(_: rusqlite::Error) -> Error { Error::blocked("database_unavailable", "本地数据库无法验证；未显示成功。") }
fn now() -> Result<i64, Error> { SystemTime::now().duration_since(UNIX_EPOCH).map(|v| v.as_millis() as i64).map_err(|_| Error::blocked("clock_unavailable", "本地时间不可用；未写入。")) }

// Evidence startup mode is off by default and has no IPC or product-state
// surface. It can write only a non-content receipt inside the authorized
// synthetic runtime after both explicit gates have been satisfied.
fn evidence_viewport() -> Result<Option<(&'static str, u32, u32)>, Error> {
    if std::env::var("LIFEOS_P3_141_EVIDENCE_MODE").ok().as_deref() != Some("1") { return Ok(None); }
    match std::env::var("LIFEOS_P3_141_VIEWPORT").ok().as_deref().unwrap_or("desktop") {
        "desktop" => Ok(Some(("desktop", 1280, 1024))),
        "compact" => Ok(Some(("compact", 700, 760))),
        "narrow" => Ok(Some(("narrow", 560, 640))),
        _ => Err(Error::blocked("evidence_viewport_rejected", "合成 Evidence 视口不受支持；未写入。")),
    }
}

fn controlled_fixture_evidence(paths: &Paths) -> bool {
    paths.mode == InputMode::Synthetic
        && std::env::var("LIFEOS_P3_141_SYNTHETIC_FIXTURE_EVIDENCE").ok().as_deref() == Some("1")
        && paths.root.starts_with("/private/tmp/lifeos-p3-141-provider-restoration-closure-v1/")
}

// The platform applies `set_size` asynchronously. Receipt values therefore
// come from three equal, non-zero observations after a post-settle delay, not
// from the event-loop's first (possibly previous-viewport) sample.
const VIEWPORT_SETTLE_DELAY_MS: u64 = 220;
const VIEWPORT_SETTLE_SAMPLE_GAP_MS: u64 = 80;
const VIEWPORT_SETTLE_SAMPLE_COUNT: usize = 3;

#[derive(Clone, Copy, Debug)]
struct ViewportGeometry { inner_width: u32, inner_height: u32, outer_width: u32, outer_height: u32, scale_factor: f64 }
impl ViewportGeometry {
    fn usable(self) -> bool { self.inner_width > 0 && self.inner_height > 0 && self.outer_width > 0 && self.outer_height > 0 && self.scale_factor.is_finite() && self.scale_factor > 0.0 }
    fn matches(self, other: Self) -> bool {
        self.inner_width == other.inner_width && self.inner_height == other.inner_height
            && self.outer_width == other.outer_width && self.outer_height == other.outer_height
            && self.scale_factor.to_bits() == other.scale_factor.to_bits()
    }
}

fn stable_viewport_geometry(samples: &[ViewportGeometry]) -> Result<ViewportGeometry, Error> {
    if samples.len() != VIEWPORT_SETTLE_SAMPLE_COUNT || samples.iter().any(|sample| !sample.usable()) {
        return Err(Error::blocked("evidence_viewport_unstable", "合成 Evidence 窗口尺寸未形成完整有效样本；未写入。"));
    }
    let observed = samples[samples.len() - 1];
    if samples.iter().all(|sample| sample.matches(observed)) { Ok(observed) }
    else { Err(Error::blocked("evidence_viewport_unstable", "合成 Evidence 窗口尺寸仍在变化；未写入。")) }
}

fn observe_viewport_geometry(window: &tauri::WebviewWindow) -> Result<ViewportGeometry, Error> {
    let inner=window.inner_size().map_err(|_| Error::blocked("evidence_viewport_unavailable", "合成 Evidence 内部窗口尺寸不可读取；未写入。"))?;
    let outer=window.outer_size().map_err(|_| Error::blocked("evidence_viewport_unavailable", "合成 Evidence 外部窗口尺寸不可读取；未写入。"))?;
    let scale=window.scale_factor().map_err(|_| Error::blocked("evidence_viewport_unavailable", "合成 Evidence 窗口缩放不可读取；未写入。"))?;
    Ok(ViewportGeometry { inner_width: inner.width, inner_height: inner.height, outer_width: outer.width, outer_height: outer.height, scale_factor: scale })
}

fn observe_stable_viewport_geometry(window: &tauri::WebviewWindow) -> Result<ViewportGeometry, Error> {
    std::thread::sleep(Duration::from_millis(VIEWPORT_SETTLE_DELAY_MS));
    let mut samples = Vec::with_capacity(VIEWPORT_SETTLE_SAMPLE_COUNT);
    for index in 0..VIEWPORT_SETTLE_SAMPLE_COUNT {
        samples.push(observe_viewport_geometry(window)?);
        if index + 1 < VIEWPORT_SETTLE_SAMPLE_COUNT { std::thread::sleep(Duration::from_millis(VIEWPORT_SETTLE_SAMPLE_GAP_MS)); }
    }
    stable_viewport_geometry(&samples)
}

fn write_controlled_viewport_receipt(paths: &Paths, viewport: &str, width: u32, height: u32, observed: ViewportGeometry) -> Result<(), Error> {
    let target=paths.root.parent().ok_or_else(||Error::blocked("evidence_viewport_unavailable","合成 Evidence 根缺少父目录。"))?.join(format!("p3-141-actual-viewport-{}.json",std::process::id()));
    if metadata(&target)?.is_some() { return Err(Error::blocked("startup_receipt_exists", "本次实际窗口收据已存在；未覆盖。")); }
    let value=serde_json::json!({"schema":"lifeos.p3-141.actual-tauri-viewport.v3","pid":std::process::id(),"identifier":"local.lifeos.p3-141","window_title":"LifeOS · P3-141 Controlled Pilot Candidate","viewport":viewport,"requested_inner_logical":{"width":width,"height":height},"observed_inner_physical":{"width":observed.inner_width,"height":observed.inner_height},"observed_inner_logical":{"width":observed.inner_width as f64/observed.scale_factor,"height":observed.inner_height as f64/observed.scale_factor},"observed_outer_physical":{"width":observed.outer_width,"height":observed.outer_height},"observed_outer_logical":{"width":observed.outer_width as f64/observed.scale_factor,"height":observed.outer_height as f64/observed.scale_factor},"observed_scale_factor":observed.scale_factor,"receipt_source":"post_set_size_stable_samples","settle_delay_ms":VIEWPORT_SETTLE_DELAY_MS,"settle_sample_gap_ms":VIEWPORT_SETTLE_SAMPLE_GAP_MS,"settle_sample_count":VIEWPORT_SETTLE_SAMPLE_COUNT,"synthetic_fixture":true,"content_recorded":false,"network_dispatch_count":0});
    let bytes=serde_json::to_vec_pretty(&value).map_err(|_|Error::blocked("startup_receipt_serialization_rejected","实际窗口收据无法安全序列化；未写入。"))?;
    let mut file=OpenOptions::new().write(true).create_new(true).mode(0o600).open(&target).map_err(io)?;
    if file.write_all(&bytes).is_err() || file.write_all(b"\n").is_err() || file.sync_all().is_err() { let _=fs::remove_file(&target); return Err(Error::blocked("startup_receipt_write_rejected","实际窗口收据未能原子写入。")); }
    Ok(())
}

fn write_startup_ready_receipt(paths: &Paths, window: &tauri::WebviewWindow) -> Result<(), Error> {
    let Some((viewport, width, height)) = evidence_viewport()? else { return Ok(()); };
    if paths.mode == InputMode::Synthetic {
        if !controlled_fixture_evidence(paths) { return Ok(()); }
        write(paths, |_| Ok(()))?;
        window.set_size(Size::Logical(LogicalSize::new(width as f64, height as f64))).map_err(|_| Error::blocked("evidence_viewport_unavailable", "合成 Evidence 窗口尺寸不可设置；未写入。"))?;
        let receipt_paths = paths.clone();
        let receipt_window = window.clone();
        let viewport = viewport.to_string();
        tauri::async_runtime::spawn_blocking(move || {
            let result = observe_stable_viewport_geometry(&receipt_window)
                .and_then(|observed| write_controlled_viewport_receipt(&receipt_paths, &viewport, width, height, observed));
            if let Err(error) = result { eprintln!("P3-141 startup Evidence rejected: {}", error.code); }
        });
        return Ok(());
    }
    window.set_size(Size::Logical(LogicalSize::new(width as f64, height as f64))).map_err(|_| Error::blocked("evidence_viewport_unavailable", "合成 Evidence 窗口尺寸不可设置；未写入。"))?;
    let timestamp = now()?;
    let pid = std::process::id();
    let target = paths.root.join(format!("p3-141-startup-ready-{pid}.json"));
    if metadata(&target)?.is_some() { return Err(Error::blocked("startup_receipt_exists", "本次启动收据已存在；未覆盖。")); }
    let value = serde_json::json!({
        "schema": "lifeos.p3-141.startup-ready.v1", "evidence_mode": true,
        "pid": pid, "identifier": "local.lifeos.p3-141",
        "window_title": "LifeOS · P3-141 Controlled Pilot Candidate", "viewport": viewport,
        "width": width, "height": height, "ready_at_ms": timestamp,
        "content_recorded": false, "model_dispatch_count": 0
    });
    let bytes = serde_json::to_vec_pretty(&value).map_err(|_| Error::blocked("startup_receipt_serialization_rejected", "启动收据无法安全序列化；未写入。"))?;
    let mut file = OpenOptions::new().write(true).create_new(true).mode(0o600).open(&target).map_err(io)?;
    if file.write_all(&bytes).is_err() || file.write_all(b"\n").is_err() || file.sync_all().is_err() {
        let _ = fs::remove_file(&target);
        return Err(Error::blocked("startup_receipt_write_rejected", "启动收据未能原子写入。"));
    }
    Ok(())
}

// Evidence identity must terminate at the native Wry WKWebView, not at an
// application-level HTML accessibility surrogate.  Tauri exposes the exact
// native view owned by this WebviewWindow; setting its AppKit accessibility
// role makes the OS AX tree report an AXWebArea for the same direct-PID
// window.  This runs before the delayed, post-set_size receipt is sampled, so
// a startup receipt cannot be emitted for a window whose native identity was
// not configured.
#[cfg(target_os = "macos")]
fn configure_native_webview_accessibility(window: &tauri::WebviewWindow) -> Result<(), Error> {
    use objc2_app_kit::{NSAccessibility, NSAccessibilityWebAreaRole};
    use objc2_foundation::NSString;
    use objc2_web_kit::WKWebView;

    window
        .with_webview(|webview| unsafe {
            let view: &WKWebView = &*webview.inner().cast();
            let label = NSString::from_str("LifeOS P3-141 native WebView content");
            view.setAccessibilityElement(true);
            view.setAccessibilityRole(Some(NSAccessibilityWebAreaRole));
            view.setAccessibilityLabel(Some(&label));
        })
        .map_err(|_| Error::blocked("native_webview_accessibility_rejected", "原生 WebView 无法建立可访问性绑定；未写入。"))
}

#[cfg(not(target_os = "macos"))]
fn configure_native_webview_accessibility(_: &tauri::WebviewWindow) -> Result<(), Error> {
    Ok(())
}

#[derive(Clone)] struct Paths { root: PathBuf, db: PathBuf, mode: InputMode }
struct State { paths: Paths, lock: Mutex<()>, provider: Mutex<ProviderState> }

const PROVIDER_SETTINGS: &str = "ai-provider-settings.json";

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum ProviderMode { Disabled, Local, Cloud }

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum ProviderProfile { Openai, Anthropic, Ollama, LmStudio, CustomOpenaiCompatible }

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
struct ProviderSettings {
    mode: ProviderMode,
    profile: ProviderProfile,
    base_url: String,
    model: String,
    temperature_bps: u16,
    max_output_tokens: u32,
    timeout_ms: u32,
}

#[derive(Clone)]
struct SessionCredential { value: Option<String>, environment_variable: Option<String> }

#[derive(Clone)]
struct ProviderState {
    settings: ProviderSettings,
    locked_profile: Option<ProviderProfile>,
    enabled: bool,
    credential: Option<SessionCredential>,
    connection_state: &'static str,
    last_test_fingerprint: Option<String>,
    last_tested_at_ms: Option<i64>,
    last_latency_ms: Option<u64>,
    model_request_count: u64,
    discovered_models: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct PersistedProviderSettings { settings: ProviderSettings, locked_profile: Option<ProviderProfile> }

#[derive(Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
struct OwnershipMarker { schema: String, contract: String, mode: String, database: String, owner: String }

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SaveProviderSettingsRequest { settings: ProviderSettings }

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SessionCredentialRequest { credential: Option<String>, environment_variable: Option<String> }

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct TestProviderConnectionRequest { cancel: Option<bool> }

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SetProviderEnabledRequest { enabled: bool }

#[derive(Debug, Serialize)]
struct CredentialStatus { present: bool, source: &'static str }

#[derive(Debug, Serialize)]
struct ProviderSettingsResponse {
    status: &'static str,
    settings: ProviderSettings,
    enabled: bool,
    connection_state: &'static str,
    last_tested_at_ms: Option<i64>,
    last_latency_ms: Option<u64>,
    model_request_count: u64,
    discovered_models: Vec<String>,
    credential: CredentialStatus,
    persistence: &'static str,
    network: &'static str,
    locked_provider: Option<&'static str>,
    selectable_profiles: Vec<&'static str>,
}

#[derive(Debug, Serialize)]
struct ProviderConnectionResponse {
    status: &'static str,
    connection_state: &'static str,
    tested_at_ms: i64,
    provider: &'static str,
    model: String,
    fixture_only: bool,
    network: &'static str,
    models: Vec<String>,
}

fn default_provider_settings() -> ProviderSettings { ProviderSettings { mode: ProviderMode::Disabled, profile: ProviderProfile::Openai, base_url: String::new(), model: String::new(), temperature_bps: 70, max_output_tokens: 2048, timeout_ms: 60_000 } }
fn default_provider_state() -> ProviderState { ProviderState { settings: default_provider_settings(), locked_profile: None, enabled: false, credential: None, connection_state: "not_configured", last_test_fingerprint: None, last_tested_at_ms: None, last_latency_ms: None, model_request_count: 0, discovered_models: Vec::new() } }
fn provider_settings_path(paths: &Paths) -> PathBuf { paths.root.join(PROVIDER_SETTINGS) }
fn provider_profiles() -> Vec<&'static str> { vec!["openai", "anthropic", "ollama", "lm_studio", "custom_openai_compatible"] }
fn credential_status(credential: &Option<SessionCredential>) -> CredentialStatus { match credential { Some(SessionCredential { value: Some(_), .. }) => CredentialStatus { present: true, source: "session_memory" }, Some(SessionCredential { environment_variable: Some(_), .. }) => CredentialStatus { present: true, source: "environment_variable_name" }, _ => CredentialStatus { present: false, source: "absent" } } }
fn provider_response(state: &ProviderState) -> ProviderSettingsResponse { ProviderSettingsResponse { status: "ready", settings: state.settings.clone(), enabled: state.enabled, connection_state: state.connection_state, last_tested_at_ms: state.last_tested_at_ms, last_latency_ms: state.last_latency_ms, model_request_count: state.model_request_count, discovered_models: state.discovered_models.clone(), credential: credential_status(&state.credential), persistence: "nonsecret_settings_and_provider_lock_0600", network: "synthetic_loopback_only", locked_provider: state.locked_profile.map(profile_name), selectable_profiles: provider_profiles() } }
fn profile_name(profile: ProviderProfile) -> &'static str { match profile { ProviderProfile::Openai => "openai", ProviderProfile::Anthropic => "anthropic", ProviderProfile::Ollama => "ollama", ProviderProfile::LmStudio => "lm_studio", ProviderProfile::CustomOpenaiCompatible => "custom_openai_compatible" } }
fn profile_matches_mode(profile: ProviderProfile, mode: ProviderMode) -> bool { match mode { ProviderMode::Disabled => true, ProviderMode::Local => matches!(profile, ProviderProfile::Ollama | ProviderProfile::LmStudio | ProviderProfile::CustomOpenaiCompatible), ProviderMode::Cloud => matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::CustomOpenaiCompatible) } }
fn settings_fingerprint(settings: &ProviderSettings) -> String { format!("{:?}|{:?}|{}|{}|{}|{}|{}", settings.mode, settings.profile, settings.base_url, settings.model, settings.temperature_bps, settings.max_output_tokens, settings.timeout_ms) }
fn valid_env_name(value: &str) -> bool { let mut chars = value.chars(); matches!(chars.next(), Some('A'..='Z')) && chars.all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_') && value.len() <= 128 }
fn private_ipv4(value: &str) -> bool { match value.parse::<std::net::Ipv4Addr>() { Ok(ip) => ip.is_loopback() || ip.is_private(), Err(_) => false } }
fn local_host(host: &str) -> bool { host == "localhost" || host == "::1" || private_ipv4(host) || (host.len() >= 3 && (host.starts_with("fc") || host.starts_with("fd")) && host.contains(':')) }
fn cloud_host(host: &str) -> bool { host.parse::<std::net::IpAddr>().is_err() && !host.is_empty() && host.len() <= 253 && host.contains('.') && host.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'.' || b == b'-') && !host.starts_with('.') && !host.ends_with('.') && !host.contains("..") }
fn endpoint_parts(value: &str) -> Result<(&str, &str, Option<u16>), Error> {
    if value.len() > 512 || value.is_empty() || value.bytes().any(|b| b.is_ascii_whitespace()) || value.contains('@') || value.contains('?') || value.contains('#') { return Err(Error::blocked("provider_endpoint_rejected", "Provider endpoint 不符合受控网络边界。")); }
    let (scheme, rest) = value.split_once("://").ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint 必须声明 HTTP(S) 协议。"))?;
    let authority = rest.split('/').next().unwrap_or_default();
    if authority.is_empty() || authority.contains(':') && !authority.starts_with('[') && authority.matches(':').count() != 1 { return Err(Error::blocked("provider_endpoint_rejected", "Provider endpoint 主机格式不受支持。")); }
    let (host, port) = if authority.starts_with('[') { let closing=authority.find(']').ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint IPv6 主机格式不受支持。"))?; let host=&authority[1..closing]; let remainder=&authority[closing+1..]; let port=if remainder.is_empty(){None}else{Some(remainder.strip_prefix(':').ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint IPv6 主机格式不受支持。"))?.parse::<u16>().map_err(|_|Error::blocked("provider_endpoint_rejected", "Provider endpoint 端口不受支持。"))?)}; (host,port) } else { let mut parts=authority.split(':');let host=parts.next().unwrap_or_default();let port=match parts.next(){Some(raw)=>Some(raw.parse::<u16>().map_err(|_|Error::blocked("provider_endpoint_rejected", "Provider endpoint 端口不受支持。"))?),None=>None};(host,port) };
    if host.is_empty() || port == Some(0) { return Err(Error::blocked("provider_endpoint_rejected", "Provider endpoint 缺少有效主机或端口。")); }
    Ok((scheme, host, port))
}
fn validate_provider_settings_for(settings: &ProviderSettings, input: InputMode) -> Result<(), Error> {
    if settings.temperature_bps > 200 || settings.max_output_tokens == 0 || settings.max_output_tokens > 8192 || settings.timeout_ms < 1_000 || settings.timeout_ms > 120_000 || settings.model.trim().len() > 128 || settings.model.bytes().any(|b| b.is_ascii_control()) { return Err(Error::blocked("provider_settings_rejected", "Provider 参数超出受控范围。")); }
    if !profile_matches_mode(settings.profile, settings.mode) { return Err(Error::blocked("provider_profile_mode_rejected", "Provider profile 与模式不匹配。")); }
    if settings.mode == ProviderMode::Disabled { if !settings.base_url.is_empty() || !settings.model.is_empty() { return Err(Error::blocked("disabled_provider_configuration_rejected", "Disabled 模式不保存 endpoint 或 model。")); } return Ok(()); }
    if settings.model.trim().is_empty() { return Err(Error::blocked("provider_settings_rejected", "启用 Provider 前必须选择 model。")); }
    let (scheme, host, port) = endpoint_parts(&settings.base_url)?;
    let synthetic_fixture_port = input == InputMode::Synthetic && host == "fixture.lifeos.test" && port.is_some();
    match settings.mode { ProviderMode::Local if scheme == "http" || scheme == "https" => if !local_host(host) { return Err(Error::blocked("provider_local_endpoint_rejected", "Local Provider 仅允许 loopback 或私有 LAN 字面地址。")); }, ProviderMode::Cloud if scheme == "https" && (matches!(port, None | Some(443)) || synthetic_fixture_port) => if !cloud_host(host) { return Err(Error::blocked("provider_cloud_endpoint_rejected", "Cloud Provider 仅允许受控 HTTPS 域名。")); }, ProviderMode::Local => return Err(Error::blocked("provider_local_endpoint_rejected", "Local Provider 仅允许 HTTP(S) loopback 或私有 LAN 服务。")), ProviderMode::Cloud => return Err(Error::blocked("provider_cloud_endpoint_rejected", "Cloud Provider 必须使用 HTTPS 标准端口。")), ProviderMode::Disabled => unreachable!() }
    Ok(())
}
#[cfg(test)]
fn validate_provider_settings(settings: &ProviderSettings) -> Result<(), Error> { validate_provider_settings_for(settings, InputMode::Real) }
fn valid_settings_file(metadata: &fs::Metadata) -> Result<(), Error> { if !metadata.file_type().is_file() || metadata.file_type().is_symlink() || metadata.nlink() != 1 || metadata.permissions().mode() & 0o777 != 0o600 { return Err(Error::blocked("provider_settings_file_rejected", "Provider 设置文件必须是 0600 的普通单链接文件。")); } Ok(()) }
fn load_provider_state(paths: &Paths) -> Result<ProviderState, Error> { let file = provider_settings_path(paths); match metadata(&file)? { None => Ok(default_provider_state()), Some(meta) => { valid_settings_file(&meta)?; let raw = fs::read_to_string(&file).map_err(io)?; let persisted: PersistedProviderSettings = serde_json::from_str(&raw).map_err(|_| Error::blocked("provider_settings_file_rejected", "Provider 设置文件无法按非敏感合同解析。"))?; validate_provider_settings_for(&persisted.settings, paths.mode)?; let connection_state = if persisted.settings.mode == ProviderMode::Disabled { "disabled" } else { "not_tested_after_restart" }; Ok(ProviderState { settings: persisted.settings, locked_profile: persisted.locked_profile, enabled: false, credential: None, connection_state, last_test_fingerprint: None, last_tested_at_ms: None, last_latency_ms: None, model_request_count: 0, discovered_models: Vec::new() }) } } }
fn write_provider_settings(paths: &Paths, settings: &ProviderSettings, locked_profile: Option<ProviderProfile>) -> Result<(), Error> { if paths.mode == InputMode::Real { write(paths, |_| Ok(()))?; } else { prepare_root(paths)?; } validate_provider_settings_for(settings, paths.mode)?; let target = provider_settings_path(paths); if let Some(meta) = metadata(&target)? { valid_settings_file(&meta)?; }
    let temporary = paths.root.join(".ai-provider-settings.tmp"); if metadata(&temporary)?.is_some() { return Err(Error::blocked("provider_settings_file_rejected", "Provider 设置临时文件异常存在。")); }
    let bytes = serde_json::to_vec_pretty(&PersistedProviderSettings { settings: settings.clone(), locked_profile }).map_err(|_| Error::blocked("provider_settings_serialization_rejected", "Provider 设置无法安全序列化。"))?;
    let mut file = OpenOptions::new().write(true).create_new(true).mode(0o600).open(&temporary).map_err(io)?;
    if file.write_all(&bytes).is_err() || file.write_all(b"\n").is_err() || file.sync_all().is_err() { let _ = fs::remove_file(&temporary); return Err(Error::blocked("provider_settings_write_rejected", "Provider 设置未能原子写入。")); }
    fs::rename(&temporary, &target).map_err(io)?; let meta = metadata(&target)?.ok_or_else(|| Error::blocked("provider_settings_write_rejected", "Provider 设置写入后不可见。"))?; valid_settings_file(&meta)
}
fn metadata(path: &Path) -> Result<Option<fs::Metadata>, Error> { match fs::symlink_metadata(path) { Ok(m) => Ok(Some(m)), Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None), Err(e) => Err(io(e)) } }
fn real_dir(path: &Path) -> Result<(), Error> { let m = fs::symlink_metadata(path).map_err(io)?; if !m.file_type().is_dir() || m.file_type().is_symlink() { return Err(Error::blocked("path_symlink_rejected", "Runtime 根祖先必须是无链接目录。")); } Ok(()) }
fn real_chain(path: &Path) -> Result<(), Error> { let mut current = PathBuf::new(); for part in path.components() { match part { Component::RootDir => current.push("/"), Component::Normal(value) => { current.push(value); real_dir(&current)?; }, _ => return Err(Error::blocked("runtime_root_noncanonical", "Runtime 根不规范。")), } } Ok(()) }
fn root_shape(root: &Path) -> Result<(), Error> { if !root.is_absolute() || root.components().any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_))) { return Err(Error::blocked("runtime_root_noncanonical", "Runtime 根必须是绝对规范路径。")); } let parent = root.parent().ok_or_else(|| Error::blocked("runtime_root_noncanonical", "Runtime 根缺少父目录。"))?; real_chain(parent) }
fn ownership_path(paths: &Paths) -> PathBuf { paths.root.join(OWNERSHIP_MARKER) }
fn valid_owned_file(meta: &fs::Metadata) -> Result<(), Error> { if !meta.file_type().is_file() || meta.file_type().is_symlink() || meta.nlink() != 1 || meta.permissions().mode() & 0o777 != 0o600 { return Err(Error::blocked("real_root_ownership_rejected", "本地 ownership marker 必须是 0600 的普通单链接文件。")); } Ok(()) }
fn expected_ownership() -> OwnershipMarker { OwnershipMarker { schema: "lifeos.p3-141.local-owner.v1".into(), contract: "LIFEOS-P3-141".into(), mode: "real_self_use".into(), database: DB.into(), owner: "candidate_initialized_local_root".into() } }
fn validate_ownership_marker(paths: &Paths) -> Result<(), Error> { let marker = ownership_path(paths); let meta = metadata(&marker)?.ok_or_else(|| Error::blocked("real_root_ownership_missing", "真实 Runtime 根缺少候选 ownership marker；未接管。"))?; valid_owned_file(&meta)?; let value: OwnershipMarker = serde_json::from_str(&fs::read_to_string(&marker).map_err(io)?).map_err(|_| Error::blocked("real_root_ownership_rejected", "本地 ownership marker 不可验证。"))?; if value != expected_ownership() { return Err(Error::blocked("real_root_ownership_rejected", "本地 ownership marker 不属于当前候选。")); } Ok(()) }
fn write_ownership_marker(paths: &Paths) -> Result<(), Error> { let marker = ownership_path(paths); if metadata(&marker)?.is_some() { return Err(Error::blocked("real_root_ownership_rejected", "ownership marker 已存在；未覆盖。")); } let bytes = serde_json::to_vec_pretty(&expected_ownership()).map_err(|_| Error::blocked("real_root_ownership_rejected", "ownership marker 无法序列化。"))?; let mut file = OpenOptions::new().write(true).create_new(true).mode(0o600).open(&marker).map_err(io)?; if file.write_all(&bytes).is_err() || file.write_all(b"\n").is_err() || file.sync_all().is_err() { return Err(Error::blocked("real_root_ownership_rejected", "ownership marker 未能原子写入。")); } let meta = metadata(&marker)?.ok_or_else(|| Error::blocked("real_root_ownership_rejected", "ownership marker 写入后不可见。"))?; valid_owned_file(&meta) }
fn reject_sidecars(paths: &Paths) -> Result<(), Error> { for suffix in ["-journal", "-wal", "-shm"] { if metadata(&PathBuf::from(format!("{}{}", paths.db.display(), suffix)))?.is_some() { return Err(Error::blocked("database_sidecar_rejected", "数据库 sidecar 不受支持。")); } } Ok(()) }
fn validate_existing_real_root(paths: &Paths) -> Result<(), Error> { let root_meta = metadata(&paths.root)?.ok_or_else(|| Error::blocked("real_root_ownership_missing", "真实 Runtime 根缺失。"))?; if !root_meta.file_type().is_dir() || root_meta.file_type().is_symlink() { return Err(Error::blocked("runtime_root_type_rejected", "真实 Runtime 根不是普通目录。")); } if fs::canonicalize(&paths.root).map_err(io)? != paths.root { return Err(Error::blocked("runtime_root_noncanonical", "真实 Runtime 根解析后发生变化。")); } let mut marker = false; let mut database = false; let mut provider = false; for item in fs::read_dir(&paths.root).map_err(io)? { let name = item.map_err(io)?.file_name(); match name.to_str() { Some(OWNERSHIP_MARKER) => marker = true, Some(DB) => database = true, Some(PROVIDER_SETTINGS) => provider = true, Some(value) if value == format!("{DB}-journal") || value == format!("{DB}-wal") || value == format!("{DB}-shm") => return Err(Error::blocked("database_sidecar_rejected", "数据库 sidecar 不受支持。")), _ => return Err(Error::blocked("real_root_not_empty", "真实 Runtime 根出现未知文件；未接管。")), } } if !marker || !database { return Err(Error::blocked("real_root_ownership_missing", "真实 Runtime 根必须由本候选以 marker 和 capture.sqlite 初始化。")); } validate_ownership_marker(paths)?; reject_sidecars(paths)?; let db_meta = metadata(&paths.db)?.ok_or_else(|| Error::blocked("database_type_rejected", "数据库缺失。"))?; if !db_meta.file_type().is_file() || db_meta.file_type().is_symlink() || db_meta.nlink() != 1 { return Err(Error::blocked("database_type_rejected", "数据库不是普通单链接文件。")); } if provider { let provider_meta = metadata(&provider_settings_path(paths))?.ok_or_else(|| Error::blocked("provider_settings_file_rejected", "Provider 设置不可见。"))?; valid_settings_file(&provider_meta)?; } let conn = Connection::open_with_flags(&paths.db, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sql)?; conn.pragma_update(None, "query_only", true).map_err(sql)?; valid_conn(&conn, InputMode::Real) }
fn paths() -> Result<Paths, Error> { let raw = ROOT.ok_or_else(|| Error::blocked("runtime_root_missing", "构建时 Runtime 根缺失。"))?; let root = PathBuf::from(raw); if raw.is_empty() { return Err(Error::blocked("runtime_root_noncanonical", "Runtime 根必须是绝对规范路径。")); } root_shape(&root)?; let current_mode = mode()?; let paths = Paths { db: root.join(DB), root, mode: current_mode }; if current_mode == InputMode::Synthetic { real_chain(&paths.root)?; if fs::canonicalize(&paths.root).map_err(io)? != paths.root { return Err(Error::blocked("runtime_root_noncanonical", "Runtime 根解析后发生变化。")); } } else if metadata(&paths.root)?.is_some() { validate_existing_real_root(&paths)?; } Ok(paths) }
fn prepare_root(paths: &Paths) -> Result<bool, Error> { if paths.mode == InputMode::Synthetic { real_chain(&paths.root)?; return Ok(false); } root_shape(&paths.root)?; match metadata(&paths.root)? { None => { fs::create_dir(&paths.root).map_err(io)?; fs::set_permissions(&paths.root, fs::Permissions::from_mode(0o700)).map_err(io)?; if fs::canonicalize(&paths.root).map_err(io)? != paths.root { return Err(Error::blocked("runtime_root_noncanonical", "真实 Runtime 根解析后发生变化。")); } Ok(true) }, Some(_) => { validate_existing_real_root(paths)?; Ok(false) } } }
fn db_present(paths: &Paths) -> Result<bool, Error> { if paths.mode == InputMode::Real { if metadata(&paths.root)?.is_none() { return Ok(false); } validate_existing_real_root(paths)?; return Ok(true); } prepare_root(paths)?; reject_sidecars(paths)?; match metadata(&paths.db)? { None => Ok(false), Some(m) if m.file_type().is_file() && !m.file_type().is_symlink() && m.nlink() == 1 => Ok(true), Some(_) => Err(Error::blocked("database_type_rejected", "数据库不是普通单链接文件。")), } }
fn init(conn: &Connection, m: InputMode) -> Result<(), Error> { conn.execute_batch(SCHEMA).map_err(sql)?; conn.execute("INSERT OR IGNORE INTO runtime_meta(mode,contract,created_at_ms) VALUES(?1,'LIFEOS-P3-141',?2)", params![m.value(), now()?]).map_err(sql)?; conn.execute("INSERT OR IGNORE INTO projects(id,person_id,source_id,artifact_version,source_available,generation_current,tombstoned,authorized,evidence_ready) VALUES(?1,?2,?3,?4,1,1,0,1,1)", params![PROJECT, PERSON, m.source(), m.artifact()]).map_err(sql)?; valid_conn(conn, m) }
fn valid_conn(conn: &Connection, m: InputMode) -> Result<(), Error> { let quick: String = conn.query_row("PRAGMA quick_check", [], |r| r.get(0)).map_err(sql)?; let version: i64 = conn.query_row("PRAGMA user_version", [], |r| r.get(0)).map_err(sql)?; let meta: Option<(String, String)> = conn.query_row("SELECT mode,contract FROM runtime_meta", [], |r| Ok((r.get(0)?, r.get(1)?))).optional().map_err(sql)?; if quick != "ok" || version != 141 || meta.as_ref().map(|x| (x.0.as_str(), x.1.as_str())) != Some((m.value(), "LIFEOS-P3-141")) { return Err(Error::blocked("database_contract_rejected", "数据库不符合 P3-141 合同。")); } Ok(()) }
fn read(paths: &Paths) -> Result<Connection, Error> { let conn = Connection::open_with_flags(&paths.db, OpenFlags::SQLITE_OPEN_READ_ONLY).map_err(sql)?; conn.pragma_update(None, "query_only", true).map_err(sql)?; valid_conn(&conn, paths.mode)?; Ok(conn) }
fn write<T>(paths: &Paths, f: impl FnOnce(&mut Connection) -> Result<T, Error>) -> Result<T, Error> { let fresh_real_root = prepare_root(paths)?; let present = if paths.mode == InputMode::Real { !fresh_real_root } else { db_present(paths)? }; let mut conn = Connection::open(&paths.db).map_err(sql)?; conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE;").map_err(sql)?; if present { valid_conn(&conn, paths.mode)?; } else { init(&conn, paths.mode)?; } let result = f(&mut conn)?; valid_conn(&conn, paths.mode)?; if fresh_real_root { write_ownership_marker(paths)?; } reject_sidecars(paths)?; Ok(result) }
fn read_or_memory(paths: &Paths) -> Result<Connection, Error> { if paths.mode == InputMode::Real && !db_present(paths)? { write(paths, |_| Ok(()))?; } if db_present(paths)? { read(paths) } else { let conn = Connection::open_in_memory().map_err(sql)?; init(&conn, paths.mode)?; Ok(conn) } }

// A request-local Bundle is current only while the selected Capture's
// authoritative Project/source/artifact authorization remains current.  This
// intentionally does not consult capture_project_links: a Persistent Link is
// not a prerequisite for a minimal request-local request.
fn ensure_selected_authorized(conn: &Connection, selection: &str) -> Result<(), Error> {
    let current: Option<i64> = conn.query_row(
        "SELECT 1 FROM captures c JOIN projects p ON p.source_id=c.source_id AND p.artifact_version=c.artifact_version WHERE c.id=?1 AND p.id=?2 AND p.person_id=?3 AND p.source_available=1 AND p.generation_current=1 AND p.tombstoned=0 AND p.authorized=1 AND p.evidence_ready=1",
        params![selection, PROJECT, PERSON],
        |row| row.get(0),
    ).optional().map_err(sql)?;
    if current.is_none() { return Err(Error::blocked("selection_authorization_stale", "选中的 Work 授权已撤销或来源已过期；没有组装、发送或写入。")); }
    Ok(())
}

#[cfg(test)] static TEST_REVOKE_AFTER_PROVIDER_DISPATCH: AtomicBool = AtomicBool::new(false);
#[cfg(test)] fn test_revoke_after_provider_dispatch(paths: &Paths) -> Result<(), Error> {
    if TEST_REVOKE_AFTER_PROVIDER_DISPATCH.swap(false, Ordering::SeqCst) {
        write(paths, |conn| { conn.execute("UPDATE projects SET authorized=0 WHERE id=?1", params![PROJECT]).map_err(sql)?; Ok(()) })?;
    }
    Ok(())
}

#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct CaptureRequest { text: String, key: String }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct EmptyRequest {}
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct ContextRequest { context_id: String }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct ConfirmRequest { capture_id: String, context_id: String, decision: LinkDecision, idempotency_key: String }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct NextRequest { candidate_id: String, decision: NextDecision, edited_text: Option<String>, idempotency_key: String }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct ResultRequest { action_id: String, result: ActionResult, result_text: String, idempotency_key: String }
// These optional fields extend only the DTOs of existing commands.  They do
// not add an IPC, make a previously required argument optional, or change the
// SQLite schema.  They represent a request-local disclosure decision and are
// deliberately never persisted as a Context/Product relationship.
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct GlobalRequest { page: Page, selection_ref: Option<String>, removed_context_kinds: Option<Vec<Removed>>, include_related_personal_content: Option<bool> }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct UnderstandingRequest { context_id: String, page: Page, selection_ref: Option<String>, removed_context_kinds: Option<Vec<Removed>>, request_id: String, include_related_personal_content: Option<bool>, additional_context_confirmed: Option<bool> }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct FeedbackRequest { understanding_id: String, decision: FeedbackDecision, edited_text: Option<String>, idempotency_key: String }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)] #[serde(rename_all = "snake_case")] enum LinkDecision { Confirm, Reject }
impl LinkDecision { fn value(self) -> &'static str { if self == Self::Confirm { "confirm" } else { "reject" } } }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)] #[serde(rename_all = "snake_case")] enum NextDecision { Accept, EditAccept, Reject, Defer }
impl NextDecision { fn value(self) -> &'static str { match self { Self::Accept => "accept", Self::EditAccept => "edit_accept", Self::Reject => "reject", Self::Defer => "defer" } } }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)] #[serde(rename_all = "snake_case")] enum ActionResult { Completed }
impl ActionResult { fn value(self) -> &'static str { "completed" } }
#[derive(Clone, Copy, Debug, Deserialize, Serialize)] #[serde(rename_all = "snake_case")] enum Page { Today, ContextDetail }
impl Page { fn value(self) -> &'static str { if matches!(self, Self::Today) { "today" } else { "context_detail" } } }
#[derive(Clone, Copy, Debug, Deserialize, Serialize)] #[serde(rename_all = "snake_case")] enum Removed { PersonDetail, Page, Selection, Domain, Context, MemorySource }
impl Removed { fn value(self) -> &'static str { match self { Self::PersonDetail => "person_detail", Self::Page => "page", Self::Selection => "selection", Self::Domain => "domain", Self::Context => "context", Self::MemorySource => "memory_source" } } }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)] #[serde(rename_all = "snake_case")] enum FeedbackDecision { Confirm, EditConfirm, Reject, Correct, Ignore }
impl FeedbackDecision { fn value(self) -> &'static str { match self { Self::Confirm => "confirm", Self::EditConfirm => "edit_confirm", Self::Reject => "reject", Self::Correct => "correct", Self::Ignore => "ignore" } } }

#[derive(Debug, Serialize, Clone)] struct Record { id: String, content: String, created_at_ms: u64, source: String, source_id: String, artifact_version: String, identity: &'static str }
#[derive(Serialize, Clone)] struct Recovery { context_id: String, project_id: String, person_id: String, project_title: String, state: String, reliable_suggestion: bool, evidence_gap: Option<String>, source_ref: String, artifact_ref: String, typed_link_ref: Option<String>, feedback_ref: Option<String>, audit_ref: Option<String>, memory_copy_created: bool }
#[derive(Serialize, Clone)] struct Candidate { candidate_id: String, text: String, identity: &'static str, derivation_id: String, processor: String, processor_version: String, basis_refs: Vec<String>, evidence_state: &'static str, why: String }
#[derive(Serialize)] struct NextResponse { status: String, context_id: String, candidates: Vec<Candidate>, disclosure: Option<String>, evidence_gap: Option<String> }
#[derive(Serialize, Clone)] struct Action { action_id: String, text: String, state: String, confirmation_kind: String, candidate_ref: String, confirmed_at: u64 }
#[derive(Serialize)] struct Audit { event_count: usize, capture_saved: usize, capture_repeat: usize, context_feedback: usize, candidate_feedback: usize, action_created: usize, result_recorded: usize }
#[derive(Serialize)] struct Memory { derivation_refs: Vec<String>, candidate_refs: Vec<String>, feedback_refs: Vec<String>, action_refs: Vec<String>, result_refs: Vec<String>, original_copy_created: bool }
#[derive(Serialize)] struct Today { status: &'static str, records: Vec<Record>, source: &'static str, ai_status: &'static str, audit: Audit, context_recovery: Recovery, confirmed_actions: Vec<Action>, todays_focus: Option<String>, lifeos_noticed: Option<Notice>, memory_provenance: Memory, intelligence: Option<today_intelligence::TodayIntelligence> }
#[derive(Serialize)] struct Notice { identity: &'static str, state: String, text: String, understanding_ref: String, basis_refs: Vec<String>, processor: Option<String>, synthetic_adapter: bool }
#[derive(Debug, Serialize)] struct CaptureResponse { status: String, record: Record, record_count: usize, audit_event_count: usize, context_id: String, link_status: String }
#[derive(Serialize)] struct ConfirmResponse { status: String, capture_id: String, context_id: String, decision: String, feedback_count: usize, audit_event_count: usize, recovery: Recovery }
#[derive(Serialize)] struct DecisionResponse { status: String, candidate_id: String, decision: String, action: Option<Action>, feedback_ref: String, audit_event_count: usize }
#[derive(Serialize)] struct ResultResponse { status: String, action_id: String, result: String, result_ref: String, audit_event_count: usize }
#[derive(Serialize)] struct ContextItem { kind: String, reference: String, source: String, inclusion_reason: String, authorization: String, evidence_status: String, removable: bool, additional_personal_content: bool }
#[derive(Serialize)] struct Global { context_id: String, page: String, selection_ref: Option<String>, included: Vec<ContextItem>, removed_context_kinds: Vec<String>, authorization_summary: Vec<String>, permissions: Vec<String>, evidence_status: String, request_local: bool, additional_personal_count: usize, disclosure_required: bool }
#[derive(Debug, Serialize)] struct Understanding { understanding_id: String, observation: Option<String>, suggestion: Option<String>, identity: &'static str, processor: String, processor_version: String, basis_refs: Vec<String>, why: String, evidence_state: String, synthetic_adapter: bool, disclosure: Option<String> }
#[derive(Serialize)] struct Feedback { status: String, feedback_id: String, understanding_id: String, decision: String, feedback_text: Option<String>, audit_event_count: usize }
#[derive(Serialize)] struct Status { status: &'static str, input_mode: &'static str, controlled_synthetic_fixture: bool, offline: bool, ai_enabled: bool, renderer_direct_capabilities: Vec<&'static str>, ipc_allowlist: Vec<&'static str>, unknown_ipc: &'static str, filesystem: bool, raw_database: bool, generic_path_api: bool, shell: bool, process_spawn: bool, network: bool, vault: bool, export: bool, sync: bool, context_recovery: &'static str, candidate_rule: &'static str, memory_duplicate_original: bool, model_port: &'static str, model_adapter: &'static str }

fn valid_capture(paths: &Paths, request: &CaptureRequest) -> bool { if paths.mode == InputMode::Synthetic { (request.text == SYN_TEXT && request.key == SYN_KEY) || (request.text == SYN_SHORT && request.key == SYN_SHORT_KEY) } else { !request.text.trim().is_empty() && request.text.chars().count() <= 200 && request.key.starts_with(paths.mode.idempotency_prefix()) && request.key.len() <= 128 && request.key.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-') } }
fn record(paths: &Paths, id: String, content: String, created: i64, source: String, source_id: String, artifact: String) -> Result<Record, Error> { let valid_content = if paths.mode == InputMode::Real { !content.is_empty() && content.chars().count() <= 200 } else { content == SYN_TEXT || content == SYN_SHORT }; if !id.starts_with(paths.mode.capture_prefix()) || !valid_content || created <= 0 || source != "local_capture" || source_id != paths.mode.source() || artifact != paths.mode.artifact() { return Err(Error::blocked("record_identity_rejected", "Capture 身份、来源或额度不可信。")); } Ok(Record { id, content, created_at_ms: created as u64, source, source_id, artifact_version: artifact, identity: "user_original" }) }
fn audit(conn: &Connection) -> Result<Audit, Error> { let mut stmt = conn.prepare("SELECT event FROM audit").map_err(sql)?; let mut output = Audit { event_count: 0, capture_saved: 0, capture_repeat: 0, context_feedback: 0, candidate_feedback: 0, action_created: 0, result_recorded: 0 }; for event in stmt.query_map([], |r| r.get::<_, String>(0)).map_err(sql)? { output.event_count += 1; match event.map_err(sql)?.as_str() { "capture_saved" => output.capture_saved += 1, "capture_repeat" => output.capture_repeat += 1, "context_confirmed" | "context_rejected" => output.context_feedback += 1, "candidate_accepted" | "candidate_edit_accepted" | "candidate_rejected" | "candidate_deferred" | "understanding_created" | "understanding_confirmed" | "understanding_edited_confirmed" | "understanding_rejected" | "understanding_ignored" | "understanding_corrected" => output.candidate_feedback += 1, "action_created" | "understanding_action_created" => output.action_created += 1, "action_completed" => output.result_recorded += 1, _ => return Err(Error::blocked("audit_contract_rejected", "审计事件不在合同内。")), } } Ok(output) }
fn recovery(paths: &Paths, conn: &Connection) -> Result<Recovery, Error> { let link: Option<(String, String)> = conn.query_row("SELECT capture_id,link_status FROM capture_project_links ORDER BY capture_id DESC LIMIT 1", [], |r| Ok((r.get(0)?, r.get(1)?))).optional().map_err(sql)?; let state = link.as_ref().map(|x| x.1.clone()).unwrap_or_else(|| "empty".into()); Ok(Recovery { context_id: CONTEXT.into(), project_id: PROJECT.into(), person_id: PERSON.into(), project_title: "LifeOS Work".into(), state, reliable_suggestion: false, evidence_gap: None, source_ref: paths.mode.source().into(), artifact_ref: paths.mode.artifact().into(), typed_link_ref: link.as_ref().map(|x| format!("capture_project_links:{}:{}", x.0, x.1)), feedback_ref: None, audit_ref: link.map(|x| format!("audit:capture:{}", x.0)), memory_copy_created: false }) }
fn capture(paths: &Paths, request: &CaptureRequest) -> Result<CaptureResponse, Error> {
    if !valid_capture(paths, request) {
        return Err(Error::blocked(if paths.mode == InputMode::Real { "real_input_rejected" } else { "argument_schema_rejected" }, "输入必须符合当前模式的固定边界。"));
    }
    let request = request.clone();
    write(paths, move |conn| {
        let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?;
        let previous: Option<(String, String, i64)> = tx.query_row("SELECT id,content,created_at_ms FROM captures WHERE idem_key=?1", params![request.key], |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?))).optional().map_err(sql)?;
        let (status, item, link_status) = if let Some((id, text, time)) = previous {
            if text != request.text { return Err(Error::blocked("idempotency_conflict", "Capture key 已绑定不同原文。")); }
            tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('capture_repeat',?1,'same_idempotency_key',?2)", params![id, now()?]).map_err(sql)?;
            let link: Option<String> = tx.query_row("SELECT link_status FROM capture_project_links WHERE capture_id=?1", params![id], |row| row.get(0)).optional().map_err(sql)?;
            ("idempotent_repeat".into(), record(paths, id, text, time, "local_capture".into(), paths.mode.source().into(), paths.mode.artifact().into())?, link.unwrap_or_else(|| "unlinked".into()))
        } else {
            let count: i64 = tx.query_row("SELECT count(*) FROM captures", [], |row| row.get(0)).map_err(sql)?;
            if count >= paths.mode.limit() { return Err(Error::blocked("input_limit_rejected", "当前输入额度已满；写入前已拒绝。")); }
            let time = now()?;
            if paths.mode == InputMode::Real {
                let same_day: i64 = tx.query_row("SELECT count(*) FROM work_trial_days WHERE day_key=strftime('%Y-%m-%d',?1 / 1000,'unixepoch','localtime')", params![time], |row| row.get(0)).map_err(sql)?;
                if same_day >= 1 { return Err(Error::blocked("daily_work_limit_rejected", "当天已保存一条 Work；写入前已拒绝。")); }
            }
            let id = format!("{}{}", paths.mode.capture_prefix(), request.key);
            tx.execute("INSERT INTO captures(id,content,created_at_ms,source,source_id,artifact_version,idem_key) VALUES(?1,?2,?3,'local_capture',?4,?5,?6)", params![id, request.text, time, paths.mode.source(), paths.mode.artifact(), request.key]).map_err(sql)?;
            if paths.mode == InputMode::Real { tx.execute("INSERT INTO work_trial_days(day_key,capture_id,created_at_ms) VALUES(strftime('%Y-%m-%d',?1 / 1000,'unixepoch','localtime'),?2,?1)", params![time,id]).map_err(sql)?; }
            tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('capture_saved',?1,'local_capture',?2)", params![id, time]).map_err(sql)?;
            ("saved".into(), record(paths, id, request.text, time, "local_capture".into(), paths.mode.source().into(), paths.mode.artifact().into())?, "unlinked".into())
        };
        tx.commit().map_err(sql)?;
        let count: i64 = conn.query_row("SELECT count(*) FROM captures", [], |row| row.get(0)).map_err(sql)?;
        Ok(CaptureResponse { status, record: item, record_count: count as usize, audit_event_count: audit(conn)?.event_count, context_id: CONTEXT.into(), link_status })
    })
}
impl Clone for CaptureRequest { fn clone(&self) -> Self { Self { text: self.text.clone(), key: self.key.clone() } } }
fn confirm(paths: &Paths, request: &ConfirmRequest) -> Result<ConfirmResponse, Error> {
    if request.context_id != CONTEXT || !request.capture_id.starts_with(paths.mode.capture_prefix()) || !request.idempotency_key.starts_with(paths.mode.idempotency_prefix()) {
        return Err(Error::blocked("argument_schema_rejected", "Context 确认参数不符合合同。"));
    }
    let request = request.clone();
    write(paths, move |conn| {
        let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?;
        let exists: Option<i64> = tx.query_row("SELECT 1 FROM captures WHERE id=?1", params![request.capture_id], |row| row.get(0)).optional().map_err(sql)?;
        if exists.is_none() { return Err(Error::blocked("capture_missing", "待确认的 Capture 不存在。")); }
        let duplicate: Option<i64> = tx.query_row("SELECT 1 FROM feedback WHERE idem_key=?1", params![request.idempotency_key], |row| row.get(0)).optional().map_err(sql)?;
        if duplicate.is_none() {
            let existing: Option<String> = tx.query_row("SELECT link_status FROM capture_project_links WHERE capture_id=?1", params![request.capture_id], |row| row.get(0)).optional().map_err(sql)?;
            if existing.is_some() { return Err(Error::blocked("confirmation_state_rejected", "长期关联已经有明确状态。")); }
            if request.decision == LinkDecision::Confirm {
                tx.execute("INSERT INTO capture_project_links(capture_id,context_id,link_status) VALUES(?1,?2,'confirmed')", params![request.capture_id, CONTEXT]).map_err(sql)?;
            }
            let time = now()?;
            tx.execute("INSERT INTO feedback(target_kind,target_id,decision,idem_key,detail,created_at_ms) VALUES('capture_context',?1,?2,?3,'explicit_user_decision',?4)", params![request.capture_id, request.decision.value(), request.idempotency_key, time]).map_err(sql)?;
            tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES(?1,?2,?3,?4)", params![if request.decision == LinkDecision::Confirm { "context_confirmed" } else { "context_rejected" }, request.capture_id, CONTEXT, time]).map_err(sql)?;
        }
        tx.commit().map_err(sql)?;
        let feedback_count: i64 = conn.query_row("SELECT count(*) FROM feedback", [], |row| row.get(0)).map_err(sql)?;
        Ok(ConfirmResponse { status: if duplicate.is_some() { "idempotent_repeat".into() } else { "saved".into() }, capture_id: request.capture_id, context_id: CONTEXT.into(), decision: request.decision.value().into(), feedback_count: feedback_count as usize, audit_event_count: audit(conn)?.event_count, recovery: recovery(paths, conn)? })
    })
}
impl Clone for ConfirmRequest { fn clone(&self) -> Self { Self { capture_id: self.capture_id.clone(), context_id: self.context_id.clone(), decision: self.decision, idempotency_key: self.idempotency_key.clone() } } }
fn no_next(status: &str, disclosure: &str) -> NextResponse { NextResponse { status: status.into(), context_id: CONTEXT.into(), candidates: Vec::new(), disclosure: Some(disclosure.into()), evidence_gap: None } }
fn next(paths: &Paths, request: &ContextRequest) -> Result<NextResponse, Error> { if request.context_id != CONTEXT { return Err(Error::blocked("context_schema_rejected", "只接受固定 Project Context。")); } let conn = read_or_memory(paths)?; let capture: Option<(String, String)> = conn.query_row("SELECT id,content FROM captures ORDER BY created_at_ms DESC,id DESC LIMIT 1", [], |r| Ok((r.get(0)?, r.get(1)?))).optional().map_err(sql)?; let Some((capture_id, text)) = capture else { return Ok(no_next("empty", "暂时没有足够证据判断。")); }; if paths.mode == InputMode::Synthetic && text == SYN_SHORT { return Ok(no_next("insufficient_evidence", "暂时没有足够证据判断。")); } let link: Option<String> = conn.query_row("SELECT link_status FROM capture_project_links WHERE capture_id=?1", params![capture_id], |r| r.get(0)).optional().map_err(sql)?; if link.as_deref() != Some("confirmed") { return Ok(no_next("awaiting_context_confirmation", "请先确认此 capture 是否属于当前 Project Context。")); } let existing: Option<(String, String, String)> = conn.query_row("SELECT id,candidate_text,candidate_state FROM candidate_actions WHERE capture_id=?1 ORDER BY created_at_ms DESC LIMIT 1", params![capture_id], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?))).optional().map_err(sql)?; if let Some((id, content, state)) = existing { if state == "active" { return Ok(NextResponse { status: "available".into(), context_id: CONTEXT.into(), candidates: vec![Candidate { candidate_id: id, text: content, identity: "system_candidate_next_action", derivation_id: format!("derivation:{}", capture_id), processor: if paths.mode == InputMode::Real { "local_rule:p3-141-user-explicit-v1" } else { "local_rule:p3-141-synthetic-v1" }.into(), processor_version: "v1".into(), basis_refs: vec![format!("capture:{capture_id}"), format!("capture_project_links:{capture_id}:confirmed")], evidence_state: "sufficient", why: "候选需要用户显式接受、拒绝或暂缓。".into() }], disclosure: None, evidence_gap: None }); } return Ok(no_next("already_decided", "此候选已完成用户处置。")); }
    drop(conn); write(paths, move |conn| { let time = now()?; let id = format!("{}{}", paths.mode.candidate_prefix(), capture_id); let text = if paths.mode == InputMode::Real { REAL_ACTION } else { SYN_TEXT }; conn.execute("INSERT INTO candidate_actions(id,capture_id,candidate_text,candidate_state,created_at_ms) VALUES(?1,?2,?3,'active',?4)", params![id, capture_id, text, time]).map_err(sql)?; Ok(NextResponse { status: "available".into(), context_id: CONTEXT.into(), candidates: vec![Candidate { candidate_id: id, text: text.into(), identity: "system_candidate_next_action", derivation_id: format!("derivation:{}", capture_id), processor: if paths.mode == InputMode::Real { "local_rule:p3-141-user-explicit-v1" } else { "local_rule:p3-141-synthetic-v1" }.into(), processor_version: "v1".into(), basis_refs: vec![format!("capture:{capture_id}"), format!("capture_project_links:{capture_id}:confirmed")], evidence_state: "sufficient", why: "候选需要用户显式接受、拒绝或暂缓。".into() }], disclosure: None, evidence_gap: None }) }) }
fn next_request_local(paths: &Paths, request: &ContextRequest) -> Result<NextResponse, Error> {
    let _legacy_for_read_only_regression: fn(&Paths, &ContextRequest) -> Result<NextResponse, Error> = next;
    if !request_context_id(&request.context_id) { return Err(Error::blocked("context_schema_rejected", "请求 Context 标识不受支持。")); }
    let conn=read_or_memory(paths)?;
    let capture:Option<(String,String)>=conn.query_row("SELECT id,content FROM captures ORDER BY created_at_ms DESC,id DESC LIMIT 1",[],|row|Ok((row.get(0)?,row.get(1)?))).optional().map_err(sql)?;
    let Some((capture_id,text))=capture else{return Ok(no_next("empty","暂时没有足够证据判断。"));};
    if paths.mode==InputMode::Synthetic && text==SYN_SHORT{return Ok(no_next("insufficient_evidence","暂时没有足够证据判断。"));}
    let existing:Option<(String,String,String)>=conn.query_row("SELECT id,candidate_text,candidate_state FROM candidate_actions WHERE capture_id=?1 ORDER BY created_at_ms DESC LIMIT 1",params![capture_id],|row|Ok((row.get(0)?,row.get(1)?,row.get(2)?))).optional().map_err(sql)?;
    if let Some((id,text,state))=existing { if state=="active" { return Ok(NextResponse{status:"available".into(),context_id:"request-local".into(),candidates:vec![Candidate{candidate_id:id,text,identity:"system_candidate_next_action",derivation_id:format!("derivation:{capture_id}"),processor:"local_rule:request_local-v1".into(),processor_version:"v1".into(),basis_refs:vec![format!("capture:{capture_id}")],evidence_state:"sufficient",why:"持久关联不是本次最小请求的前置条件。".into()}],disclosure:None,evidence_gap:None}); } return Ok(no_next("already_decided","此候选已完成用户处置。")); }
    drop(conn);
    write(paths,move|conn|{let time=now()?;let id=format!("{}{}",paths.mode.candidate_prefix(),capture_id);let text=if paths.mode==InputMode::Real{REAL_ACTION}else{SYN_TEXT};conn.execute("INSERT INTO candidate_actions(id,capture_id,candidate_text,candidate_state,created_at_ms) VALUES(?1,?2,?3,'active',?4)",params![id,capture_id,text,time]).map_err(sql)?;Ok(NextResponse{status:"available".into(),context_id:"request-local".into(),candidates:vec![Candidate{candidate_id:id,text:text.into(),identity:"system_candidate_next_action",derivation_id:format!("derivation:{capture_id}"),processor:"local_rule:request_local-v1".into(),processor_version:"v1".into(),basis_refs:vec![format!("capture:{capture_id}")],evidence_state:"sufficient",why:"候选需要用户显式接受、拒绝或忽略。".into()}],disclosure:None,evidence_gap:None})})
}
fn action_view(conn: &Connection, id: &str) -> Result<Action, Error> { conn.query_row("SELECT id,action_text,action_state,confirmation_kind,candidate_id,confirmed_at_ms FROM actions WHERE id=?1", params![id], |r| Ok(Action { action_id: r.get(0)?, text: r.get(1)?, state: r.get(2)?, confirmation_kind: r.get(3)?, candidate_ref: r.get(4)?, confirmed_at: r.get::<_, i64>(5)? as u64 })).map_err(sql) }
fn decide(paths: &Paths, request: &NextRequest) -> Result<DecisionResponse, Error> { if !request.candidate_id.starts_with(paths.mode.candidate_prefix()) || !request.idempotency_key.starts_with(paths.mode.idempotency_prefix()) || (paths.mode == InputMode::Real && (request.decision == NextDecision::EditAccept || request.edited_text.is_some())) || (paths.mode == InputMode::Synthetic && request.decision == NextDecision::EditAccept && request.edited_text.as_deref() != Some(SYN_EDIT)) { return Err(Error::blocked("argument_schema_rejected", "Action 决定参数不符合合同。")); } let request = request.clone(); write(paths, move |conn| { let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?; let state: Option<String> = tx.query_row("SELECT candidate_state FROM candidate_actions WHERE id=?1", params![request.candidate_id], |r| r.get(0)).optional().map_err(sql)?; if state.as_deref() != Some("active") { return Err(Error::blocked("candidate_state_rejected", "只能处置开放的 Candidate。")); } let time = now()?; let mut action_id = String::new(); if matches!(request.decision, NextDecision::Accept | NextDecision::EditAccept) { action_id = format!("{}{}", paths.mode.action_prefix(), request.candidate_id); let text = if paths.mode == InputMode::Real { REAL_ACTION } else if request.decision == NextDecision::EditAccept { SYN_EDIT } else { SYN_TEXT }; tx.execute("INSERT INTO actions(id,candidate_id,action_text,confirmation_kind,action_state,created_at_ms) VALUES(?1,?2,?3,?4,'open',?5)", params![action_id, request.candidate_id, text, request.decision.value(), time]).map_err(sql)?; tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('action_created',?1,?2,?3)", params![action_id, request.decision.value(), time]).map_err(sql)?; } let state = match request.decision { NextDecision::Accept | NextDecision::EditAccept => "accepted", NextDecision::Reject => "rejected", NextDecision::Defer => "deferred" }; let event = match request.decision { NextDecision::Accept => "candidate_accepted", NextDecision::EditAccept => "candidate_edit_accepted", NextDecision::Reject => "candidate_rejected", NextDecision::Defer => "candidate_deferred" }; tx.execute("UPDATE candidate_actions SET candidate_state=?1 WHERE id=?2", params![state, request.candidate_id]).map_err(sql)?; tx.execute("INSERT INTO feedback(target_kind,target_id,decision,idem_key,detail,created_at_ms) VALUES('candidate_action',?1,?2,?3,?4,?5)", params![request.candidate_id, request.decision.value(), request.idempotency_key, action_id, time]).map_err(sql)?; tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES(?1,?2,?3,?4)", params![event, request.candidate_id, request.decision.value(), time]).map_err(sql)?; tx.commit().map_err(sql)?; Ok(DecisionResponse { status: "saved".into(), candidate_id: request.candidate_id, decision: request.decision.value().into(), action: if action_id.is_empty() { None } else { Some(action_view(conn, &action_id)?) }, feedback_ref: format!("feedback:{time}"), audit_event_count: audit(conn)?.event_count }) }) }
impl Clone for NextRequest { fn clone(&self) -> Self { Self { candidate_id: self.candidate_id.clone(), decision: self.decision, edited_text: self.edited_text.clone(), idempotency_key: self.idempotency_key.clone() } } }
fn result(paths: &Paths, request: &ResultRequest) -> Result<ResultResponse, Error> { let expected = if paths.mode == InputMode::Real { REAL_RESULT } else { SYN_RESULT }; if !request.action_id.starts_with(paths.mode.action_prefix()) || request.result != ActionResult::Completed || request.result_text != expected || !request.idempotency_key.starts_with(paths.mode.idempotency_prefix()) { return Err(Error::blocked("argument_schema_rejected", "Action Result 参数不符合合同。")); } let request = request.clone(); write(paths, move |conn| { let state: Option<String> = conn.query_row("SELECT action_state FROM actions WHERE id=?1", params![request.action_id], |r| r.get(0)).optional().map_err(sql)?; if state.as_deref() != Some("open") { return Err(Error::blocked("action_state_rejected", "只能记录开放 Action 的结果。")); } let time = now()?; let result_id = format!("action_result:p3-141:{time:016x}"); let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?; tx.execute("INSERT INTO action_results(id,action_id,result_text,idem_key,created_at_ms) VALUES(?1,?2,?3,?4,?5)", params![result_id, request.action_id, expected, request.idempotency_key, time]).map_err(sql)?; tx.execute("UPDATE actions SET action_state='completed' WHERE id=?1", params![request.action_id]).map_err(sql)?; tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('action_completed',?1,'completed',?2)", params![request.action_id, time]).map_err(sql)?; tx.commit().map_err(sql)?; Ok(ResultResponse { status: "saved".into(), action_id: request.action_id, result: request.result.value().into(), result_ref: result_id, audit_event_count: audit(conn)?.event_count }) }) }
impl Clone for ResultRequest { fn clone(&self) -> Self { Self { action_id: self.action_id.clone(), result: self.result, result_text: self.result_text.clone(), idempotency_key: self.idempotency_key.clone() } } }
fn today(paths: &Paths) -> Result<Today, Error> { let conn = read_or_memory(paths)?; let mut records = Vec::new(); let mut stmt = conn.prepare("SELECT id,content,created_at_ms,source,source_id,artifact_version FROM captures ORDER BY created_at_ms,id").map_err(sql)?; for row in stmt.query_map([], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?))).map_err(sql)? { let (id,content,time,source,source_id,artifact) = row.map_err(sql)?; records.push(record(paths,id,content,time,source,source_id,artifact)?); } let mut actions = Vec::new(); let mut stmt = conn.prepare("SELECT id,action_text,action_state,confirmation_kind,candidate_id,confirmed_at_ms FROM actions WHERE action_state='open' ORDER BY confirmed_at_ms,id").map_err(sql)?; for row in stmt.query_map([], |r| Ok(Action { action_id:r.get(0)?,text:r.get(1)?,state:r.get(2)?,confirmation_kind:r.get(3)?,candidate_ref:r.get(4)?,confirmed_at:r.get::<_,i64>(5)? as u64 })).map_err(sql)? { actions.push(row.map_err(sql)?); } let memory = Memory { derivation_refs: Vec::new(), candidate_refs: Vec::new(), feedback_refs: Vec::new(), action_refs: actions.iter().map(|x| x.action_id.clone()).collect(), result_refs: Vec::new(), original_copy_created: false }; Ok(Today { status: if records.is_empty() { "empty" } else { "ready" }, records, source:"local_capture", ai_status:"provider_requires_explicit_enablement", audit:audit(&conn)?, context_recovery:recovery(paths,&conn)?, todays_focus:actions.first().map(|x|x.action_id.clone()), confirmed_actions:actions, lifeos_noticed:None, memory_provenance:memory, intelligence:None }) }
fn request_context_id(value: &str) -> bool { value == CONTEXT || value == "request-local" || value.starts_with("request:") }
fn request_id(value: &str) -> bool { value.starts_with("p3-136-") || value.starts_with("p3-137-") }
fn context(paths: &Paths, request: &ContextRequest) -> Result<Recovery, Error> { if !request_context_id(&request.context_id) { return Err(Error::blocked("context_schema_rejected", "请求 Context 标识不受支持。")); } recovery(paths,&read_or_memory(paths)?) }
fn context_item(kind: &str, reference: &str, source: &str, why: &str, authorization: &str, evidence_status: &str, removable: bool, additional_personal_content: bool) -> ContextItem { ContextItem { kind:kind.into(),reference:reference.into(),source:source.into(),inclusion_reason:why.into(),authorization:authorization.into(),evidence_status:evidence_status.into(),removable,additional_personal_content } }
fn global(paths: &Paths, request: &GlobalRequest) -> Result<Global, Error> {
    let removed = request.removed_context_kinds.as_ref().map(|items|items.iter().map(|x|x.value().to_string()).collect::<Vec<_>>()).unwrap_or_default();
    let include_related = request.include_related_personal_content.unwrap_or(false) && !removed.iter().any(|kind| kind == "memory_source");
    let mut included=Vec::new();
    if let Some(selection)=request.selection_ref.as_ref() {
        if removed.iter().any(|kind| kind == "selection") { return Err(Error::blocked("selection_removed", "已移除当前记录；没有组装或发送请求。")); }
        let conn=read_or_memory(paths)?;
        let exists:Option<String>=conn.query_row("SELECT id FROM captures WHERE id=?1",params![selection],|row|row.get(0)).optional().map_err(sql)?;
        if exists.is_none() { return Err(Error::blocked("selection_stale", "选中的 Work 记录已失效；没有组装或发送请求。")); }
        ensure_selected_authorized(&conn,selection)?;
        included.push(context_item("selection",selection,"local_capture","用户在本次请求中显式选中的 Work 记录。","explicit_selection:granted","current",false,false));
    }
    for (kind,reference,source,why,removable) in [("page",request.page.value(),"renderer","当前可见页面状态。",true),("person_domain","work","domain_policy","最小 Work 身份与领域范围；不含额外原文。",true),("project",PROJECT,"project_identity","Project 仅作为对象身份，不是请求前置门槛。",true),("evidence_memory",paths.mode.source(),"source_identity","只携带当前选择的 Evidence／Memory 引用。",true)] {
        if !removed.iter().any(|item|item==kind) { included.push(context_item(kind,reference,source,why,"request_local:granted","current",removable,false)); }
    }
    if include_related { included.push(context_item("related_personal_content",CONTEXT,"context_candidate","当前记录之外的一项相关个人资料，必须在本次请求前明确确认。","request_local:pending_confirmation","current",true,true)); }
    let additional_personal_count=usize::from(include_related);
    Ok(Global { context_id:"request-local".into(),page:request.page.value().into(),selection_ref:request.selection_ref.clone(),included,removed_context_kinds:removed,authorization_summary:if include_related {vec!["selected_work:granted".into(),"related_personal_content:pending_confirmation".into()]}else{vec!["selected_work_and_minimal_refs:granted".into()]},permissions:vec!["model_port:explicit_user_action_only".into()],evidence_status:"current".into(),request_local:true,additional_personal_count,disclosure_required:include_related })
}
fn disabled_understanding() -> Understanding { Understanding { understanding_id:String::new(),observation:None,suggestion:None,identity:"no_reliable_understanding",processor:"provider_disabled".into(),processor_version:"p3-137-v1".into(),basis_refs:Vec::new(),why:"Provider 未经本次用户显式连接测试与启用；没有调用模型。".into(),evidence_state:"insufficient".into(),synthetic_adapter:false,disclosure:Some("Provider 未启用；尚未请求模型。".into()) } }
fn disclosure_understanding() -> Understanding { Understanding { understanding_id:String::new(),observation:None,suggestion:None,identity:"request_disclosure_required",processor:"context_engine".into(),processor_version:"p3-137-v1".into(),basis_refs:Vec::new(),why:"当前 Bundle 包含当前记录之外的个人资料；必须先由用户确认。".into(),evidence_state:"pending_authorization".into(),synthetic_adapter:false,disclosure:Some("将使用当前记录和 1 项相关资料。".into()) } }
#[allow(dead_code)]
fn understanding(_paths: &Paths, request: &UnderstandingRequest) -> Result<Understanding, Error> { if !request_context_id(&request.context_id) || !request_id(&request.request_id) { return Err(Error::blocked("request_id_rejected", "Understanding 请求不符合当前合同。")); } if request.include_related_personal_content.unwrap_or(false) && !request.additional_context_confirmed.unwrap_or(false) { return Ok(disclosure_understanding()); } Ok(disabled_understanding()) }
fn provider_understanding(paths: &Paths, state: &mut ProviderState, request: &UnderstandingRequest) -> Result<Understanding, Error> {
    if !request_context_id(&request.context_id) || !request_id(&request.request_id) { return Err(Error::blocked("request_id_rejected", "Understanding 请求不符合当前合同。")); }
    let selected = request.selection_ref.as_ref().ok_or_else(|| Error::blocked("selection_required", "发送前必须显式选择一条 Work Capture。"))?;
    let conn = read(paths)?;
    let content: String = conn.query_row("SELECT content FROM captures WHERE id=?1", params![selected], |row| row.get(0)).map_err(|_| Error::blocked("selection_stale", "选中的 Work Capture 已失效；没有调用模型。"))?;
    ensure_selected_authorized(&conn, selected)?;
    let existing: Option<(String, String, String, String, String, String)> = conn.query_row("SELECT id,kind,summary,provider,evidence_refs_json,uncertainty FROM understandings WHERE request_id=?1", params![request.request_id], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?,row.get(3)?,row.get(4)?,row.get(5)?))).optional().map_err(sql)?;
    if let Some((id, kind, summary, provider, evidence, uncertainty)) = existing { let refs=serde_json::from_str(&evidence).map_err(|_|Error::blocked("understanding_contract_rejected", "已存 Understanding 不可信。"))?; return Ok(Understanding { understanding_id:id, observation:if kind=="observation"{Some(summary.clone())}else{None}, suggestion:if kind=="suggestion"{Some(summary)}else{None}, identity:"ai_observation_and_suggestion", processor:format!("provider_adapter:{provider}"), processor_version:"p3-137-v1".into(), basis_refs:refs, why:"同一显式请求已持久化；关闭重开不会重发。".into(), evidence_state:uncertainty, synthetic_adapter:paths.mode==InputMode::Synthetic, disclosure:None }); }
    if request.include_related_personal_content.unwrap_or(false) && !request.additional_context_confirmed.unwrap_or(false) { return Ok(disclosure_understanding()); }
    if !state.enabled { return Ok(disabled_understanding()); }
    let fingerprint = settings_fingerprint(&state.settings);
    if state.connection_state != "connected" || state.last_test_fingerprint.as_deref() != Some(fingerprint.as_str()) { return Err(Error::blocked("provider_enablement_stale", "Provider 连接状态已过期；没有调用模型。")); }
    let removed = request.removed_context_kinds.as_ref().map(|items| items.iter().map(|item| item.value()).collect::<Vec<_>>()).unwrap_or_default();
    if removed.iter().any(|item| *item == "selection") { return Err(Error::blocked("selection_removed", "已移除 Selection 类别；没有调用模型。")); }
    let request_scope = if request.include_related_personal_content.unwrap_or(false) { format!("{}; related_personal_context=1", request.page.value()) } else { request.page.value().into() };
    let port = model_port(state.settings.profile);
    let wire = port.build_inference(&ProviderInferenceInput {
        model: &state.settings.model,
        temperature_bps: state.settings.temperature_bps,
        max_output_tokens: state.settings.max_output_tokens,
        page: &request_scope,
        selected_text: &content,
        evidence_ref: &format!("capture:{selected}"),
    })?;
    state.model_request_count += 1;
    let reply = match provider_http(paths, &state.settings, &state.credential, &wire) { Ok(reply) => reply, Err(error) => { state.enabled=false; state.connection_state="failed"; return Err(error); } };
    let output = match parse_provider_output(state.settings.profile, &reply.body) { Ok(output) => output, Err(error) => { state.enabled=false; state.connection_state="failed"; return Err(error); } };
    #[cfg(test)] test_revoke_after_provider_dispatch(paths)?;
    let expected_evidence_ref = format!("capture:{selected}");
    if output.evidence_refs != vec![expected_evidence_ref] { state.enabled=false; state.connection_state="failed"; return Err(Error::blocked("provider_evidence_ref_mismatch", "Provider 输出没有绑定本次显式选择的 Evidence ref；未写入派生对象。")); }
    if state.locked_profile.is_none() {
        state.locked_profile = Some(state.settings.profile);
        if let Err(error) = write_provider_settings(paths, &state.settings, state.locked_profile) {
            state.enabled = false;
            state.connection_state = "failed";
            return Err(error);
        }
    }
    let id = format!("understanding:p3-137:{}", request.request_id);
    let synthetic_adapter = paths.mode == InputMode::Synthetic;
    let provider = profile_name(state.settings.profile).to_string();
    let model = state.settings.model.clone();
    let request_id = request.request_id.clone();
    let evidence = serde_json::to_string(&output.evidence_refs).map_err(|_| Error::blocked("provider_response_invalid", "Evidence refs 无法持久化。"))?;
    let kind = output.kind.clone();
    let summary = output.summary.clone();
    let uncertainty = output.uncertainty.clone();
    let selection_for_commit = selected.clone();
    write(paths, move |conn| {
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?;
        ensure_selected_authorized(&tx, &selection_for_commit)?;
        let existing: Option<(String, String, String, String, String)> = tx.query_row("SELECT id,kind,summary,provider,evidence_refs_json FROM understandings WHERE request_id=?1", params![request_id], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?,row.get(3)?,row.get(4)?))).optional().map_err(sql)?;
        if let Some((id, kind, summary, provider, evidence)) = existing {
            let refs = serde_json::from_str(&evidence).map_err(|_| Error::blocked("understanding_contract_rejected", "已存 Understanding 不可信。"))?;
            return Ok(Understanding { understanding_id:id, observation:if kind=="observation"{Some(summary.clone())}else{None}, suggestion:if kind=="suggestion"{Some(summary)}else{None}, identity:"ai_observation_and_suggestion", processor:format!("provider_adapter:{provider}"), processor_version:"p3-137-v1".into(), basis_refs:refs, why:"同一显式请求的已验证派生对象。".into(), evidence_state:"sufficient".into(), synthetic_adapter, disclosure:None });
        }
        let time = now()?;
        tx.execute("INSERT INTO understandings(id,request_id,kind,summary,provider,model,evidence_refs_json,uncertainty,created_at_ms) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9)", params![id,request_id,kind,summary,provider,model,evidence,uncertainty.clone(),time]).map_err(sql)?;
        tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('understanding_created',?1,'provider_derived_noncontent_metadata',?2)", params![id,time]).map_err(sql)?;
        tx.commit().map_err(sql)?;
        Ok(Understanding { understanding_id:id, observation:if kind=="observation"{Some(summary.clone())}else{None}, suggestion:if kind=="suggestion"{Some(summary)}else{None}, identity:"ai_observation_and_suggestion", processor:format!("provider_adapter:{provider}"), processor_version:"p3-137-v1".into(), basis_refs:output.evidence_refs, why:"用户显式发送后的受控 Provider 派生对象；输出仅为候选。".into(), evidence_state:uncertainty, synthetic_adapter, disclosure:None })
    })
}
fn feedback(paths: &Paths, request: &FeedbackRequest) -> Result<Feedback, Error> {
    let valid_understanding=request.understanding_id.starts_with("understanding:p3-136:") || request.understanding_id.starts_with("understanding:p3-137:");
    let valid_key=request.idempotency_key.starts_with("p3-136-") || request.idempotency_key.starts_with("p3-137-");
    if !valid_understanding || !valid_key { return Err(Error::blocked("understanding_feedback_rejected", "Understanding Feedback 不符合当前合同。")); }
    if request.decision == FeedbackDecision::EditConfirm && request.edited_text.as_ref().map(|value|value.trim().is_empty() || value.len()>4096).unwrap_or(true) { return Err(Error::blocked("understanding_feedback_rejected", "编辑确认必须提供受控文本。")); }
    let request=FeedbackRequest{understanding_id:request.understanding_id.clone(),decision:request.decision,edited_text:request.edited_text.clone(),idempotency_key:request.idempotency_key.clone()};
    write(paths, move |conn| {
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?;
        let existing:Option<(String,String)>=tx.query_row("SELECT id,decision FROM feedback WHERE idem_key=?1",params![request.idempotency_key],|row|Ok((row.get(0)?,row.get(1)?))).optional().map_err(sql)?;
        if let Some((id,decision))=existing { drop(tx); return Ok(Feedback{status:"idempotent_repeat".into(),feedback_id:id,understanding_id:request.understanding_id,decision,feedback_text:None,audit_event_count:audit(conn)?.event_count}); }
        let source:Option<String>=tx.query_row("SELECT summary FROM understandings WHERE id=?1",params![request.understanding_id],|row|row.get(0)).optional().map_err(sql)?;
        let source=source.ok_or_else(||Error::blocked("understanding_not_found","Understanding 不存在；未写入反馈。"))?;
        let time=now()?; let decision=request.decision.value().to_string(); let feedback_id=format!("feedback:p3-137:{time:016x}");
        tx.execute("INSERT INTO feedback(target_kind,target_id,decision,idem_key,detail,created_at_ms) VALUES('understanding',?1,?2,?3,'user_explicit_noncontent_metadata',?4)",params![request.understanding_id,decision,request.idempotency_key,time]).map_err(sql)?;
        let event=match request.decision{FeedbackDecision::Confirm=>"understanding_confirmed",FeedbackDecision::EditConfirm=>"understanding_edited_confirmed",FeedbackDecision::Reject=>"understanding_rejected",FeedbackDecision::Ignore=>"understanding_ignored",FeedbackDecision::Correct=>"understanding_corrected"};
        if matches!(request.decision,FeedbackDecision::Confirm|FeedbackDecision::EditConfirm) { let action_id=format!("action:p3-137:{}",request.understanding_id); let action_text=request.edited_text.clone().unwrap_or(source); tx.execute("INSERT INTO actions(id,candidate_id,action_text,confirmation_kind,action_state,created_at_ms) VALUES(?1,?2,?3,?4,'open',?5)",params![action_id,request.understanding_id,action_text,decision,time]).map_err(sql)?; tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES('understanding_action_created',?1,'user_confirmed_only',?2)",params![action_id,time]).map_err(sql)?; }
        tx.execute("INSERT INTO audit(event,target_id,detail,created_at_ms) VALUES(?1,?2,'user_explicit_feedback',?3)",params![event,request.understanding_id,time]).map_err(sql)?;
        tx.commit().map_err(sql)?;
        Ok(Feedback{status:"saved".into(),feedback_id,understanding_id:request.understanding_id,decision,feedback_text:request.edited_text,audit_event_count:audit(conn)?.event_count})
    })
}
fn status(paths: &Paths) -> Status { Status { status:"ready",input_mode:paths.mode.value(),controlled_synthetic_fixture:controlled_fixture_evidence(paths),offline:true,ai_enabled:false,renderer_direct_capabilities:Vec::new(),ipc_allowlist:IPC.to_vec(),unknown_ipc:"rejected",filesystem:false,raw_database:false,generic_path_api:false,shell:false,process_spawn:false,network:false,vault:false,export:false,sync:false,context_recovery:"request_local_bundle_with_optional_persistent_links",candidate_rule:"explicit_user_decision_required",memory_duplicate_original:false,model_port:"replaceable_provider_explicit_only",model_adapter:"five_profile_explicit_user_enabled_synthetic_loopback_only" } }

fn get_provider_settings(state: &ProviderState) -> ProviderSettingsResponse { provider_response(state) }
fn save_provider_settings(paths: &Paths, state: &mut ProviderState, request: SaveProviderSettingsRequest) -> Result<ProviderSettingsResponse, Error> { validate_provider_settings_for(&request.settings, paths.mode)?; if let Some(locked) = state.locked_profile { if request.settings.profile != locked { return Err(Error::blocked("provider_locked_after_first_send", "首次发送后 Provider 已锁定；不能切换 Provider。")); } } write_provider_settings(paths, &request.settings, state.locked_profile)?; state.settings = request.settings; state.enabled = false; state.credential = None; state.connection_state = if state.settings.mode == ProviderMode::Disabled { "disabled" } else { "not_tested" }; state.last_test_fingerprint = None; state.last_tested_at_ms = None; state.last_latency_ms = None; state.discovered_models.clear(); Ok(provider_response(state)) }
fn set_provider_session_credential(state: &mut ProviderState, request: SessionCredentialRequest) -> Result<ProviderSettingsResponse, Error> { if state.settings.mode == ProviderMode::Disabled { return Err(Error::blocked("provider_disabled", "请先保存 Local 或 Cloud Provider 设置。")); } if request.credential.is_some() == request.environment_variable.is_some() { return Err(Error::blocked("credential_reference_rejected", "凭据必须仅使用 session 值或环境变量名之一。")); } if let Some(value) = request.credential.as_ref() { if value.is_empty() || value.len() > 4096 || value.bytes().any(|b| b.is_ascii_control()) { return Err(Error::blocked("credential_reference_rejected", "Session 凭据格式不受支持。")); } }
    if let Some(name) = request.environment_variable.as_ref() { if !valid_env_name(name) { return Err(Error::blocked("credential_reference_rejected", "环境变量名格式不受支持。")); } }
    state.credential = Some(SessionCredential { value: request.credential, environment_variable: request.environment_variable }); state.enabled = false; state.connection_state = "not_tested"; state.last_test_fingerprint = None; state.last_tested_at_ms = None; state.last_latency_ms = None; state.discovered_models.clear(); Ok(provider_response(state)) }

#[derive(Debug)] struct HttpReply { body: Vec<u8>, latency_ms: u64 }
#[derive(Debug, Deserialize)] #[serde(deny_unknown_fields)] struct ProviderOutput { kind: String, summary: String, uncertainty: String, evidence_refs: Vec<String> }

// The runtime never branches on a wire protocol. This narrow ModelPort seam
// owns each profile's probe, inference envelope and response envelope; the
// surrounding domain stays responsible only for authorization and persistence.
#[derive(Clone, Copy, Debug, PartialEq, Eq)] enum WireMethod { Get, Post }
#[derive(Debug)] struct ProviderWireRequest { method: WireMethod, path: &'static str, body: Option<String> }
impl ProviderWireRequest { fn get(path: &'static str) -> Self { Self { method: WireMethod::Get, path, body: None } } fn post(path: &'static str, body: String) -> Self { Self { method: WireMethod::Post, path, body: Some(body) } } }
struct ProviderInferenceInput<'a> { model: &'a str, temperature_bps: u16, max_output_tokens: u32, page: &'a str, selected_text: &'a str, evidence_ref: &'a str }
trait ModelPort {
    fn build_probe(&self) -> ProviderWireRequest;
    fn parse_models(&self, value: &serde_json::Value) -> Result<Vec<String>, Error>;
    fn build_inference(&self, input: &ProviderInferenceInput<'_>) -> Result<ProviderWireRequest, Error>;
    fn output_text<'a>(&self, value: &'a serde_json::Value) -> Option<&'a str>;
    fn credential_header(&self, value: &str) -> Option<String>;
}
struct OpenAiAdapter;
struct AnthropicAdapter;
struct OllamaAdapter;
struct LmStudioAdapter;
struct CustomOpenAiCompatibleAdapter;
fn protocol_rejected(message: &'static str) -> Error { Error::blocked("provider_protocol_rejected", message) }
fn valid_model_names(values: Vec<&str>) -> Result<Vec<String>, Error> { let models = values.into_iter().filter(|item| !item.is_empty() && item.len() <= 128 && !item.bytes().any(|byte| byte.is_ascii_control())).map(str::to_string).take(16).collect::<Vec<_>>(); if models.is_empty() { Err(protocol_rejected("Provider 探测没有可用模型。")) } else { Ok(models) } }
fn openai_models(value: &serde_json::Value) -> Result<Vec<String>, Error> { let data = value.get("data").and_then(|item| item.as_array()).ok_or_else(|| protocol_rejected("OpenAI-compatible 探测响应缺少 data。"))?; valid_model_names(data.iter().filter_map(|item| item.get("id").and_then(|id| id.as_str())).collect()) }
fn anthropic_models(value: &serde_json::Value) -> Result<Vec<String>, Error> { let data = value.get("data").and_then(|item| item.as_array()).ok_or_else(|| protocol_rejected("Anthropic 探测响应缺少 data。"))?; valid_model_names(data.iter().filter_map(|item| item.get("id").and_then(|id| id.as_str())).collect()) }
fn ollama_models(value: &serde_json::Value) -> Result<Vec<String>, Error> { let models = value.get("models").and_then(|item| item.as_array()).ok_or_else(|| protocol_rejected("Ollama 探测响应缺少 models。"))?; valid_model_names(models.iter().filter_map(|item| item.get("name").and_then(|name| name.as_str())).collect()) }
fn output_instruction() -> &'static str { "Return exactly one JSON object with keys kind, summary, uncertainty, evidence_refs. kind must be observation or suggestion. evidence_refs must contain only the supplied evidence reference. No markdown or extra keys." }
fn minimal_user_message(input: &ProviderInferenceInput<'_>) -> String { format!("Selected Work text:\n{}\nEvidence reference: {}\nPage: {}", input.selected_text, input.evidence_ref, input.page) }
fn temperature(input: &ProviderInferenceInput<'_>) -> f64 { f64::from(input.temperature_bps) / 100.0 }
fn openai_inference(input: &ProviderInferenceInput<'_>) -> ProviderWireRequest { ProviderWireRequest::post("/v1/chat/completions", serde_json::json!({"model":input.model,"temperature":temperature(input),"max_tokens":input.max_output_tokens,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":output_instruction()},{"role":"user","content":minimal_user_message(input)}]}).to_string()) }
fn openai_text(value: &serde_json::Value) -> Option<&str> { value.get("choices").and_then(|item| item.as_array()).and_then(|items| items.first()).and_then(|item| item.get("message")).and_then(|item| item.get("content")).and_then(|item| item.as_str()) }
impl ModelPort for OpenAiAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{openai_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(openai_inference(input))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{openai_text(value)} fn credential_header(&self,value:&str)->Option<String>{Some(format!("Authorization: Bearer {value}"))} }
impl ModelPort for AnthropicAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{anthropic_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(ProviderWireRequest::post("/v1/messages",serde_json::json!({"model":input.model,"max_tokens":input.max_output_tokens,"temperature":temperature(input),"system":output_instruction(),"messages":[{"role":"user","content":minimal_user_message(input)}]}).to_string()))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{value.get("content").and_then(|item|item.as_array()).and_then(|items|items.first()).and_then(|item|item.get("text")).and_then(|item|item.as_str())} fn credential_header(&self,value:&str)->Option<String>{Some(format!("x-api-key: {value}"))} }
impl ModelPort for OllamaAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/api/tags") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{ollama_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(ProviderWireRequest::post("/api/chat",serde_json::json!({"model":input.model,"stream":false,"options":{"temperature":temperature(input),"num_predict":input.max_output_tokens},"messages":[{"role":"system","content":output_instruction()},{"role":"user","content":minimal_user_message(input)}]}).to_string()))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{value.get("message").and_then(|item|item.get("content")).and_then(|item|item.as_str())} fn credential_header(&self,_:&str)->Option<String>{None} }
impl ModelPort for LmStudioAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{openai_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(openai_inference(input))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{openai_text(value)} fn credential_header(&self,value:&str)->Option<String>{Some(format!("Authorization: Bearer {value}"))} }
impl ModelPort for CustomOpenAiCompatibleAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{openai_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(openai_inference(input))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{openai_text(value)} fn credential_header(&self,value:&str)->Option<String>{Some(format!("Authorization: Bearer {value}"))} }
fn model_port(profile: ProviderProfile) -> Box<dyn ModelPort> { match profile { ProviderProfile::Openai => Box::new(OpenAiAdapter), ProviderProfile::Anthropic => Box::new(AnthropicAdapter), ProviderProfile::Ollama => Box::new(OllamaAdapter), ProviderProfile::LmStudio => Box::new(LmStudioAdapter), ProviderProfile::CustomOpenaiCompatible => Box::new(CustomOpenAiCompatibleAdapter) } }

fn endpoint_path(value: &str) -> Result<String, Error> { let (_, rest) = value.split_once("://").ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint 必须声明 HTTP(S) 协议。"))?; let path = rest.find('/').map(|index| &rest[index..]).unwrap_or(""); if path.contains('?') || path.contains('#') || path.contains("//") { return Err(Error::blocked("provider_endpoint_rejected", "Provider endpoint 路径不受支持。")); } Ok(if path.is_empty() { String::new() } else { path.trim_end_matches('/').into() }) }
fn local_socket(settings: &ProviderSettings) -> Result<(SocketAddr, String), Error> { let (_, host, port) = endpoint_parts(&settings.base_url)?; let port = port.ok_or_else(|| Error::blocked("provider_local_endpoint_rejected", "Local Provider 必须声明固定端口。"))?; let ip = if host == "localhost" { IpAddr::from([127, 0, 0, 1]) } else { host.parse::<IpAddr>().map_err(|_| Error::blocked("provider_local_endpoint_rejected", "Local Provider 必须为字面 IP 或 localhost。"))? }; if !local_host(host) { return Err(Error::blocked("provider_local_endpoint_rejected", "Local Provider 目标超出受控地址范围。")); } Ok((SocketAddr::new(ip, port), endpoint_path(&settings.base_url)?)) }
fn local_http(settings: &ProviderSettings, wire: &ProviderWireRequest) -> Result<HttpReply, Error> { let (address, prefix) = local_socket(settings)?; let started = Instant::now(); let timeout = Duration::from_millis(settings.timeout_ms as u64); let mut stream = TcpStream::connect_timeout(&address, timeout).map_err(|_| Error::blocked("provider_connection_failed", "Provider 连接失败；未写入派生对象。"))?; stream.set_read_timeout(Some(timeout)).map_err(io)?; stream.set_write_timeout(Some(timeout)).map_err(io)?; let path = format!("{}{}", prefix, wire.path); let request = match (wire.method, wire.body.as_deref()) { (WireMethod::Get, None) => format!("GET {path} HTTP/1.1\r\nHost: {}\r\nAccept: application/json\r\nConnection: close\r\n\r\n", address.ip()), (WireMethod::Post, Some(body)) => format!("POST {path} HTTP/1.1\r\nHost: {}\r\nAccept: application/json\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", address.ip(), body.len()), _ => return Err(Error::blocked("provider_protocol_rejected", "Provider 请求合同不一致；没有打开连接。")) }; stream.write_all(request.as_bytes()).map_err(|_| Error::blocked("provider_connection_failed", "Provider 请求未完成；未写入派生对象。"))?; let mut raw = Vec::new(); let mut chunk = [0u8; 4096]; let max = 131_072usize; loop { let count = stream.read(&mut chunk).map_err(|_| Error::blocked("provider_response_failed", "Provider 响应不可用；未写入派生对象。"))?; if count == 0 { break; } raw.extend_from_slice(&chunk[..count]); if raw.len() > max { return Err(Error::blocked("provider_response_too_large", "Provider 响应超出受控上限；未写入派生对象。")); } } let marker = raw.windows(4).position(|part| part == b"\r\n\r\n").ok_or_else(|| Error::blocked("provider_protocol_rejected", "Provider HTTP 响应格式不可信。"))?; let headers = std::str::from_utf8(&raw[..marker]).map_err(|_| Error::blocked("provider_protocol_rejected", "Provider HTTP 响应格式不可信。"))?; let status = headers.split_whitespace().nth(1).and_then(|value| value.parse::<u16>().ok()).ok_or_else(|| Error::blocked("provider_protocol_rejected", "Provider HTTP 状态不可信。"))?; if (300..400).contains(&status) { return Err(Error::blocked("provider_redirect_rejected", "Provider 重定向已拒绝。")); } if status != 200 { return Err(Error::blocked("provider_http_status_rejected", "Provider 返回非成功状态；未写入派生对象。")); } Ok(HttpReply { body: raw[marker + 4..].to_vec(), latency_ms: started.elapsed().as_millis() as u64 }) }

// HTTPS uses the platform TLS library directly, never a shell or a child process.
// Each explicit operation disables proxy discovery and redirect following. Cloud
// DNS is resolved twice and the checked address is pinned into the TLS request.
#[repr(C)] struct Curl { _private: [u8; 0] }
#[repr(C)] struct CurlList { _private: [u8; 0] }
#[link(name = "curl")]
unsafe extern "C" {
    fn curl_global_init(flags: u64) -> i32;
    fn curl_easy_init() -> *mut Curl;
    fn curl_easy_cleanup(handle: *mut Curl);
    fn curl_easy_setopt(handle: *mut Curl, option: i32, ...) -> i32;
    fn curl_easy_perform(handle: *mut Curl) -> i32;
    fn curl_easy_getinfo(handle: *mut Curl, info: i32, ...) -> i32;
    fn curl_slist_append(list: *mut CurlList, value: *const c_char) -> *mut CurlList;
    fn curl_slist_free_all(list: *mut CurlList);
}
const CURLOPT_WRITEDATA: i32 = 10001;
const CURLOPT_URL: i32 = 10002;
const CURLOPT_PROXY: i32 = 10004;
const CURLOPT_POSTFIELDS: i32 = 10015;
const CURLOPT_HTTPHEADER: i32 = 10023;
const CURLOPT_WRITEFUNCTION: i32 = 20011;
const CURLOPT_CUSTOMREQUEST: i32 = 10036;
const CURLOPT_FOLLOWLOCATION: i32 = 52;
const CURLOPT_SSL_VERIFYPEER: i32 = 64;
const CURLOPT_SSL_VERIFYHOST: i32 = 81;
const CURLOPT_NOSIGNAL: i32 = 99;
const CURLOPT_TIMEOUT_MS: i32 = 155;
const CURLOPT_CONNECTTIMEOUT_MS: i32 = 156;
const CURLOPT_POSTFIELDSIZE: i32 = 60;
const CURLOPT_RESOLVE: i32 = 10203;
const CURLINFO_RESPONSE_CODE: i32 = 0x200002;
static CURL_READY: OnceLock<bool> = OnceLock::new();
struct CurlBody { bytes: Vec<u8>, exceeded: bool }
unsafe extern "C" fn curl_write(ptr: *mut c_char, size: usize, count: usize, data: *mut c_void) -> usize { let total = match size.checked_mul(count) { Some(value) => value, None => return 0 }; let output = unsafe { &mut *(data as *mut CurlBody) }; if output.bytes.len().saturating_add(total) > 131_072 { output.exceeded = true; return 0; } output.bytes.extend_from_slice(unsafe { std::slice::from_raw_parts(ptr.cast::<u8>(), total) }); total }
fn curl_text(value: &str) -> Result<CString, Error> { CString::new(value).map_err(|_| Error::blocked("provider_transport_rejected", "Provider 请求包含不受支持的控制字符。")) }
fn append_curl_list(list: *mut CurlList, value: &str) -> Result<*mut CurlList, Error> { let value = curl_text(value)?; let next = unsafe { curl_slist_append(list, value.as_ptr()) }; if next.is_null() { Err(Error::blocked("provider_transport_rejected", "Provider 请求头无法安全构造。")) } else { Ok(next) } }
fn public_ip(value: IpAddr) -> bool { match value { IpAddr::V4(ip) => !ip.is_loopback() && !ip.is_private() && !ip.is_link_local() && !ip.is_broadcast() && !ip.is_unspecified() && !ip.is_multicast(), IpAddr::V6(ip) => !ip.is_loopback() && !ip.is_unique_local() && !ip.is_unicast_link_local() && !ip.is_unspecified() && !ip.is_multicast() } }
fn vetted_cloud_ips(host: &str, port: u16) -> Result<Vec<IpAddr>, Error> { let lookup = || -> Result<Vec<IpAddr>, Error> { let mut ips = (host, port).to_socket_addrs().map_err(|_| Error::blocked("provider_dns_rejected", "Cloud Provider 域名无法解析；没有打开连接。"))?.map(|address| address.ip()).collect::<Vec<_>>(); ips.sort(); ips.dedup(); if ips.is_empty() || ips.iter().any(|ip| !public_ip(*ip)) { return Err(Error::blocked("provider_dns_rejected", "Cloud Provider 解析到不受控地址；没有打开连接。")); } Ok(ips) }; let first = lookup()?; let second = lookup()?; if first != second { return Err(Error::blocked("provider_dns_recheck_rejected", "Cloud Provider DNS 结果在连接前变化；没有打开连接。")); } Ok(first) }
fn synthetic_target_allowed(paths: &Paths, host: &str) -> Result<(), Error> { if paths.mode != InputMode::Synthetic { return Ok(()); } if host == "127.0.0.1" || host == "localhost" || host == "::1" { Ok(()) } else { Err(Error::blocked("provider_synthetic_network_rejected", "合成模式只允许 task-local loopback fixture。")) } }
fn session_secret(credential: &Option<SessionCredential>) -> Result<String, Error> { match credential { Some(SessionCredential { value: Some(value), .. }) => Ok(value.clone()), Some(SessionCredential { environment_variable: Some(name), .. }) => std::env::var(name).map_err(|_| Error::blocked("credential_unavailable", "本次会话凭据引用不可用；没有打开连接。")), _ => Err(Error::blocked("credential_required", "Cloud Provider 测试需要本次会话凭据。")) } }
fn request_headers(settings: &ProviderSettings, credential: &Option<SessionCredential>, has_json_body: bool) -> Result<Vec<String>, Error> { let mut headers = vec!["Accept: application/json".into()]; if has_json_body { headers.push("Content-Type: application/json".into()); } if settings.mode == ProviderMode::Cloud { let secret = session_secret(credential)?; let port = model_port(settings.profile); let header = port.credential_header(&secret).ok_or_else(|| Error::blocked("credential_profile_rejected", "该 Provider profile 不接受 Cloud 凭据。"))?; headers.push(header); if settings.profile == ProviderProfile::Anthropic { headers.push("anthropic-version: 2023-06-01".into()); } } Ok(headers) }
fn curl_https(paths: &Paths, settings: &ProviderSettings, credential: &Option<SessionCredential>, wire: &ProviderWireRequest, host: &str, port: u16, address: IpAddr, allow_insecure_fixture: bool) -> Result<HttpReply, Error> { if !*CURL_READY.get_or_init(|| unsafe { curl_global_init(3) == 0 }) { return Err(Error::blocked("provider_tls_unavailable", "平台 TLS 运行时不可用；没有打开连接。")); } let prefix = endpoint_path(&settings.base_url)?; let (scheme, rest) = settings.base_url.split_once("://").ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint 必须声明 HTTP(S) 协议。"))?; let authority = rest.split('/').next().ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint 缺少主机。"))?; let url = curl_text(&format!("{scheme}://{authority}{prefix}{}", wire.path))?; let method = curl_text(match wire.method { WireMethod::Get => "GET", WireMethod::Post => "POST" })?; let proxy = curl_text("")?; let resolve = format!("{host}:{port}:{address}"); let resolve_list = append_curl_list(std::ptr::null_mut(), &resolve)?; let mut header_list: *mut CurlList = std::ptr::null_mut(); for header in request_headers(settings, credential, wire.body.is_some())? { header_list = append_curl_list(header_list, &header)?; } header_list = append_curl_list(header_list, &format!("Host: {host}"))?; let handle = unsafe { curl_easy_init() }; if handle.is_null() { unsafe { curl_slist_free_all(resolve_list); curl_slist_free_all(header_list); } return Err(Error::blocked("provider_tls_unavailable", "平台 TLS 客户端不可用；没有打开连接。")); } let started = Instant::now(); let mut output = CurlBody { bytes: Vec::new(), exceeded: false }; let allow_insecure_fixture = allow_insecure_fixture && paths.mode == InputMode::Synthetic && host == "fixture.lifeos.test";
    let body = wire.body.as_deref(); let method_contract_valid = matches!((wire.method, body), (WireMethod::Get, None) | (WireMethod::Post, Some(_))); let setup = unsafe { method_contract_valid && curl_easy_setopt(handle, CURLOPT_URL, url.as_ptr()) == 0 && curl_easy_setopt(handle, CURLOPT_CUSTOMREQUEST, method.as_ptr()) == 0 && curl_easy_setopt(handle, CURLOPT_PROXY, proxy.as_ptr()) == 0 && curl_easy_setopt(handle, CURLOPT_FOLLOWLOCATION, 0i64) == 0 && curl_easy_setopt(handle, CURLOPT_NOSIGNAL, 1i64) == 0 && curl_easy_setopt(handle, CURLOPT_TIMEOUT_MS, settings.timeout_ms as i64) == 0 && curl_easy_setopt(handle, CURLOPT_CONNECTTIMEOUT_MS, settings.timeout_ms as i64) == 0 && curl_easy_setopt(handle, CURLOPT_SSL_VERIFYPEER, if allow_insecure_fixture { 0i64 } else { 1i64 }) == 0 && curl_easy_setopt(handle, CURLOPT_SSL_VERIFYHOST, if allow_insecure_fixture { 0i64 } else { 2i64 }) == 0 && curl_easy_setopt(handle, CURLOPT_RESOLVE, resolve_list) == 0 && curl_easy_setopt(handle, CURLOPT_HTTPHEADER, header_list) == 0 && curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, curl_write as unsafe extern "C" fn(*mut c_char, usize, usize, *mut c_void) -> usize) == 0 && curl_easy_setopt(handle, CURLOPT_WRITEDATA, (&mut output as *mut CurlBody).cast::<c_void>()) == 0 && match body { Some(body) => curl_easy_setopt(handle, CURLOPT_POSTFIELDS, body.as_ptr()) == 0 && curl_easy_setopt(handle, CURLOPT_POSTFIELDSIZE, body.len() as i64) == 0, None => true } }; let code = if setup { unsafe { curl_easy_perform(handle) } } else { -1 }; let mut status: i64 = 0; if code == 0 { unsafe { curl_easy_getinfo(handle, CURLINFO_RESPONSE_CODE, &mut status) }; } unsafe { curl_easy_cleanup(handle); curl_slist_free_all(resolve_list); curl_slist_free_all(header_list); }
    if output.exceeded { return Err(Error::blocked("provider_response_too_large", "Provider 响应超出受控上限；未写入派生对象。")); } if code != 0 { return Err(Error::blocked("provider_connection_failed", "Provider TLS 请求失败；未写入派生对象。")); } if (300..400).contains(&status) { return Err(Error::blocked("provider_redirect_rejected", "Provider 重定向已拒绝。")); } if status != 200 { return Err(Error::blocked("provider_http_status_rejected", "Provider 返回非成功状态；未写入派生对象。")); } Ok(HttpReply { body: output.bytes, latency_ms: started.elapsed().as_millis() as u64 }) }
fn provider_http(paths: &Paths, settings: &ProviderSettings, credential: &Option<SessionCredential>, wire: &ProviderWireRequest) -> Result<HttpReply, Error> { validate_provider_settings_for(settings, paths.mode)?; let (scheme, host, endpoint_port) = endpoint_parts(&settings.base_url)?; synthetic_target_allowed(paths, host)?; if settings.mode == ProviderMode::Local && scheme == "http" { return local_http(settings, wire); } let (port, address, fixture_tls) = if settings.mode == ProviderMode::Cloud { if paths.mode == InputMode::Synthetic { if host != "fixture.lifeos.test" { return Err(Error::blocked("provider_synthetic_network_rejected", "合成 Cloud 验证只允许 task-local HTTPS fixture。")); } (endpoint_port.ok_or_else(|| Error::blocked("provider_endpoint_rejected", "合成 HTTPS fixture 缺少端口。"))?, IpAddr::from([127,0,0,1]), true) } else { if host == "fixture.lifeos.test" { return Err(Error::blocked("provider_endpoint_rejected", "保留的合成 fixture 域名不可用于用户 Provider。")); } let port = endpoint_port.unwrap_or(443); let address = *vetted_cloud_ips(host, port)?.first().ok_or_else(|| Error::blocked("provider_dns_rejected", "Cloud Provider 没有可用地址。"))?; (port, address, false) } } else { let (address, _) = local_socket(settings)?; (address.port(), address.ip(), false) }; if scheme != "https" { return Err(Error::blocked("provider_transport_rejected", "Provider 传输协议不受支持。")); } curl_https(paths, settings, credential, wire, host, port, address, fixture_tls) }
fn parse_provider_output(profile: ProviderProfile, body: &[u8]) -> Result<ProviderOutput, Error> { let value: serde_json::Value = serde_json::from_slice(body).map_err(|_| Error::blocked("provider_response_invalid", "Provider 响应不是可验证 JSON；未写入派生对象。"))?; let port = model_port(profile); let text = port.output_text(&value).ok_or_else(|| Error::blocked("provider_protocol_mismatch", "Provider 响应不符合该 profile 协议；未写入派生对象。"))?; if text.len() > 16_384 { return Err(Error::blocked("provider_response_too_large", "Provider 输出超出受控上限；未写入派生对象。")); } let output: ProviderOutput = serde_json::from_str(text).map_err(|_| Error::blocked("provider_response_invalid", "Provider 输出结构不可信；未写入派生对象。"))?; if !matches!(output.kind.as_str(), "observation" | "suggestion") || output.summary.trim().is_empty() || output.summary.len() > 4096 || output.uncertainty.trim().is_empty() || output.evidence_refs.len() > 8 || output.evidence_refs.iter().any(|item| item.len() > 128 || item.contains('/') || item.contains('\\')) { return Err(Error::blocked("provider_response_invalid", "Provider 输出超出最小派生合同；未写入派生对象。")); } Ok(output) }
fn test_provider_connection(paths: &Paths, state: &mut ProviderState, request: TestProviderConnectionRequest) -> Result<ProviderConnectionResponse, Error> { validate_provider_settings_for(&state.settings, paths.mode)?; if request.cancel.unwrap_or(false) { state.enabled=false; state.connection_state="not_tested"; return Err(Error::blocked("provider_test_cancelled", "用户取消了 Provider 测试；没有打开网络连接。")); } if state.settings.mode == ProviderMode::Disabled { return Err(Error::blocked("provider_disabled", "Disabled Provider 不执行连接测试。")); } if state.settings.mode == ProviderMode::Cloud && !credential_status(&state.credential).present { return Err(Error::blocked("credential_required", "Cloud Provider 测试需要本次会话的凭据引用。")); }
    state.enabled = false; state.connection_state = "testing"; let port = model_port(state.settings.profile); let probe = port.build_probe(); let reply = match provider_http(paths, &state.settings, &state.credential, &probe) { Ok(reply) => reply, Err(error) => { state.connection_state = "failed"; state.last_test_fingerprint = None; state.last_tested_at_ms = Some(now()?); state.last_latency_ms = None; state.discovered_models.clear(); return Err(error); } }; let parsed: serde_json::Value = serde_json::from_slice(&reply.body).map_err(|_| Error::blocked("provider_protocol_rejected", "Provider 探测响应不可验证。"))?; let models = port.parse_models(&parsed)?; let tested_at_ms = now()?; state.connection_state = "connected"; state.last_test_fingerprint = Some(settings_fingerprint(&state.settings)); state.last_tested_at_ms = Some(tested_at_ms); state.last_latency_ms = Some(reply.latency_ms); state.discovered_models = models.clone(); Ok(ProviderConnectionResponse { status:"connected", connection_state:state.connection_state, tested_at_ms, provider:profile_name(state.settings.profile), model:state.settings.model.clone(), fixture_only:paths.mode == InputMode::Synthetic, network:if paths.mode == InputMode::Synthetic{"task_local_loopback"}else{"explicit_user_checked_provider"}, models }) }
fn set_provider_enabled(state: &mut ProviderState, request: SetProviderEnabledRequest) -> Result<ProviderSettingsResponse, Error> { if !request.enabled { state.enabled = false; state.connection_state="disabled"; return Ok(provider_response(state)); } let fingerprint=settings_fingerprint(&state.settings); if state.settings.mode == ProviderMode::Disabled || state.connection_state != "connected" || state.last_test_fingerprint.as_deref() != Some(fingerprint.as_str()) { return Err(Error::blocked("provider_enablement_rejected", "仅可启用本次会话中配置未变且连接测试成功的 Provider。")); } state.enabled = true; Ok(provider_response(state)) }

#[tauri::command] fn capture_record(request:CaptureRequest,state:tauri::State<'_,State>)->Result<CaptureResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;capture(&state.paths,&request)}
#[tauri::command] fn get_today(request:today_intelligence::TodayRequest,state:tauri::State<'_,State>)->Result<Today,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;let intelligence=if request.is_p3140(){Some(today_intelligence::respond(&state.paths,&request)?)}else{None};let mut output=today(&state.paths)?;output.intelligence=intelligence;Ok(output)}
#[tauri::command] fn runtime_status(request:EmptyRequest,state:tauri::State<'_,State>)->Status{let _=request;status(&state.paths)}
#[tauri::command] fn confirm_capture_context(request:ConfirmRequest,state:tauri::State<'_,State>)->Result<ConfirmResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;confirm(&state.paths,&request)}
#[tauri::command] fn get_context_recovery(request:ContextRequest,state:tauri::State<'_,State>)->Result<Recovery,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;context(&state.paths,&request)}
#[tauri::command] fn get_context_next_action(request:ContextRequest,state:tauri::State<'_,State>)->Result<NextResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;next_request_local(&state.paths,&request)}
#[tauri::command] fn decide_context_next_action(request:NextRequest,state:tauri::State<'_,State>)->Result<DecisionResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;decide(&state.paths,&request)}
#[tauri::command] fn record_action_result(request:ResultRequest,state:tauri::State<'_,State>)->Result<ResultResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;result(&state.paths,&request)}
#[tauri::command] fn assemble_global_ai_context(request:GlobalRequest,state:tauri::State<'_,State>)->Result<Global,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;global(&state.paths,&request)}
#[tauri::command] fn get_evidence_backed_understanding(request:UnderstandingRequest,state:tauri::State<'_,State>)->Result<Understanding,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;let mut provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;provider_understanding(&state.paths,&mut provider,&request)}
#[tauri::command] fn decide_understanding_feedback(request:FeedbackRequest,state:tauri::State<'_,State>)->Result<Feedback,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;feedback(&state.paths,&request)}
#[tauri::command] fn get_ai_provider_settings(request:EmptyRequest,state:tauri::State<'_,State>)->Result<ProviderSettingsResponse,Error>{let _=request;let provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;Ok(get_provider_settings(&provider))}
#[tauri::command] fn save_ai_provider_settings(request:SaveProviderSettingsRequest,state:tauri::State<'_,State>)->Result<ProviderSettingsResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;let mut provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;save_provider_settings(&state.paths,&mut provider,request)}
#[tauri::command] fn set_ai_provider_session_credential(request:SessionCredentialRequest,state:tauri::State<'_,State>)->Result<ProviderSettingsResponse,Error>{let mut provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;set_provider_session_credential(&mut provider,request)}
#[tauri::command] fn test_ai_provider_connection(request:TestProviderConnectionRequest,state:tauri::State<'_,State>)->Result<ProviderConnectionResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;let mut provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;test_provider_connection(&state.paths,&mut provider,request)}
#[tauri::command] fn set_ai_provider_enabled(request:SetProviderEnabledRequest,state:tauri::State<'_,State>)->Result<ProviderSettingsResponse,Error>{let mut provider=state.provider.lock().map_err(|_|Error::blocked("provider_state_unavailable","Provider 状态不可用。"))?;set_provider_enabled(&mut provider,request)}
#[tauri::command] fn upsert_durable_memory(request:memory_context::DurableMemoryRequest,state:tauri::State<'_,State>)->Result<memory_context::MemoryMutationResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;memory_context::upsert(&state.paths,request)}
#[tauri::command] fn update_current_state(request:memory_context::CurrentStateRequest,state:tauri::State<'_,State>)->Result<memory_context::StateMutationResponse,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;memory_context::update_state(&state.paths,request)}
#[tauri::command] fn resolve_request_context(request:memory_context::ResolveRequest,state:tauri::State<'_,State>)->Result<memory_context::ResolvedContext,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;memory_context::resolve(&state.paths,request)}
#[tauri::command] fn get_context_disclosure_receipt(request:memory_context::ReceiptRequest,state:tauri::State<'_,State>)->Result<memory_context::DisclosureReceipt,Error>{let _guard=state.lock.lock().map_err(|_|Error::blocked("runtime_lock_unavailable","运行时锁不可用。"))?;memory_context::receipt(&state.paths,request)}
pub fn run() {
    let runtime = paths().unwrap_or_else(|e| panic!("P3-141 runtime root rejected: {}", e.code));
    if runtime.mode == InputMode::Synthetic {
        prepare_root(&runtime).unwrap_or_else(|e| panic!("P3-141 runtime root rejected: {}", e.code));
        let _ = db_present(&runtime).unwrap_or_else(|e| panic!("P3-141 database boundary rejected: {}", e.code));
    }
    let provider = load_provider_state(&runtime).unwrap_or_else(|e| panic!("P3-141 Provider state rejected: {}", e.code));
    let app = tauri::Builder::default()
        .manage(State { paths: runtime, lock: Mutex::new(()), provider: Mutex::new(provider) })
        .invoke_handler(tauri::generate_handler![capture_record,get_today,runtime_status,confirm_capture_context,get_context_recovery,get_context_next_action,decide_context_next_action,record_action_result,assemble_global_ai_context,get_evidence_backed_understanding,decide_understanding_feedback,get_ai_provider_settings,save_ai_provider_settings,set_ai_provider_session_credential,test_ai_provider_connection,set_ai_provider_enabled,upsert_durable_memory,update_current_state,resolve_request_context,get_context_disclosure_receipt])
        .build(tauri::generate_context!())
        .expect("P3-141 Tauri runtime failed");
    app.run(|app, event| {
        if let tauri::RunEvent::Ready = event {
            let window = app.get_webview_window("main").expect("main window missing");
            let state = app.state::<State>();
            configure_native_webview_accessibility(&window)
                .unwrap_or_else(|error| panic!("P3-141 native WebView accessibility rejected: {}", error.code));
            write_startup_ready_receipt(&state.paths, &window)
                .unwrap_or_else(|error| panic!("P3-141 startup Evidence rejected: {}", error.code));
        }
    });
}

#[cfg(test)] mod tests { use super::*; use sha2::{Digest,Sha256}; fn test_paths(name:&str)->Paths{let base=paths().unwrap().root;fs::create_dir_all(&base).unwrap();let root=base.join(format!("unit-{name}-{}",now().unwrap()));let _=fs::remove_dir_all(&root);let current=mode().unwrap();if current==InputMode::Synthetic{fs::create_dir(&root).unwrap();}Paths{db:root.join(DB),root,mode:current}} fn clean(p:&Paths){let _=fs::remove_dir_all(&p.root);} fn hash(p:&Path)->String{let mut h=Sha256::new();h.update(fs::read(p).unwrap());format!("{:x}",h.finalize())}
#[test] fn real_preexisting_database_is_rejected_before_write(){if mode().unwrap()!=InputMode::Real{return;}let p=test_paths("real-existing-db");fs::create_dir(&p.root).unwrap();fs::write(&p.db,b"not-a-sqlite-db").unwrap();let before=hash(&p.db);let error=capture(&p,&CaptureRequest{text:"安全测试".into(),key:"p3-141-real-ui-existing-db".into()}).unwrap_err();assert_eq!(error.code,"database_unavailable");assert_eq!(before,hash(&p.db));clean(&p);}
#[test] fn status_is_closed_to_the_p3_139_twenty_ipc(){let p=paths().unwrap();let s=status(&p);assert_eq!(s.ipc_allowlist,IPC);assert_eq!(IPC.len(),20);assert!(!s.ai_enabled&&!s.filesystem&&!s.raw_database&&!s.generic_path_api&&!s.shell&&!s.process_spawn&&!s.network&&!s.vault&&!s.export&&!s.sync);assert_eq!(s.model_port,"replaceable_provider_explicit_only");assert_eq!(s.model_adapter,"five_profile_explicit_user_enabled_synthetic_loopback_only");assert_eq!(provider_profiles(),vec!["openai","anthropic","ollama","lm_studio","custom_openai_compatible"]);}
#[test] fn receipt_geometry_requires_post_set_size_stability_and_never_reuses_another_viewport(){
    let desktop=ViewportGeometry{inner_width:1280,inner_height:949,outer_width:1280,outer_height:949,scale_factor:1.0};
    let compact=ViewportGeometry{inner_width:700,inner_height:760,outer_width:700,outer_height:760,scale_factor:1.0};
    let narrow=ViewportGeometry{inner_width:560,inner_height:640,outer_width:560,outer_height:640,scale_factor:1.0};
    let stale_then_compact=[desktop,compact,compact];
    assert_eq!(stable_viewport_geometry(&stale_then_compact).unwrap_err().code,"evidence_viewport_unstable");
    assert!(stable_viewport_geometry(&[compact,compact,compact]).unwrap().matches(compact));
    assert!(stable_viewport_geometry(&[narrow,narrow,narrow]).unwrap().matches(narrow));
    assert!(!compact.matches(narrow));
}
#[test] fn controlled_fixture_health_source_is_closed_and_today_uses_the_same_contract(){
    let fixture=Some(vec!["source:synthetic:controlled-fixture".into()]);
    let user=Some(vec!["source:local:user-confirmed".into()]);
    assert_eq!(memory_context::expected_source_ref(InputMode::Real,true),"source:synthetic:controlled-fixture");
    assert_eq!(memory_context::expected_source_ref(InputMode::Real,false),"source:local:user-confirmed");
    assert!(memory_context::validate_source_refs(InputMode::Real,true,&fixture).is_ok());
    assert_eq!(memory_context::validate_source_refs(InputMode::Real,true,&user).unwrap_err().code,"source_refs_rejected");
    assert_eq!(memory_context::validate_source_refs(InputMode::Real,true,&Some(vec!["source:synthetic:controlled-fixture".into(),"source:local:user-confirmed".into()])).unwrap_err().code,"source_refs_rejected");
    let today=include_str!("../ui/p3-140-today.js");
    let adapter=include_str!("../ui/runtime-adapter.js");
    let index=include_str!("../ui/index.html");
    assert!(today.contains("p3_141_runtime_status") && today.contains("source:synthetic:controlled-fixture"));
    assert!(adapter.contains("ui.p3_141_runtime_status = runtime.status"));
    assert!(index.find("runtime-adapter.js").unwrap() < index.find("p3-140-today.js").unwrap());
}
#[test] fn controlled_ui_health_dto_shape_is_a_valid_closed_five_field_request(){
    let request=memory_context::CurrentStateRequest{
        operation:memory_context::StateOperation::Set,state_id:"state:p3-141:real:health-ui-m8rl-abc".into(),replacement_id:None,
        state_key:Some("health_fitness_structured_v1".into()),value:None,domain:memory_context::Domain::Health,
        source_refs:Some(vec!["source:synthetic:controlled-fixture".into()]),expires_at_ms:Some(now().unwrap()+86_400_000),expected_generation:None,
        idempotency_key:"p3-141-real-ui-health-m8rl-abc".into(),structured_health:Some(memory_context::StructuredHealthState{
            sleep_duration_range:memory_context::SleepDurationRange::SevenToNineHours,energy:3,soreness_or_pain:false,training_load:memory_context::TrainingLoad::Medium,available_time:memory_context::AvailableTime::ThirtyToSixtyMinutes,
        }),
    };
    assert!(memory_context::validate_source_refs(InputMode::Real,true,&request.source_refs).is_ok());
    assert!(request.state_id.starts_with("state:p3-141:real:") && request.idempotency_key.starts_with("p3-141-real-ui-"));
    assert!(request.value.is_none() && request.structured_health.is_some() && request.expires_at_ms.unwrap()>0);
}
#[test] fn receipt_enabled_real_mode_requires_fresh_root_and_reopens_without_write(){if MODE != Some("real_self_use"){return;}assert_eq!(mode().unwrap(),InputMode::Real);let configured=paths().unwrap();assert!(metadata(&configured.root).unwrap().is_none());assert!(metadata(&configured.db).unwrap().is_none());let captured=capture(&configured,&CaptureRequest{text:"receipt-enabled synthetic fixture".into(),key:"p3-141-real-ui-receipt-enabled".into()}).unwrap();assert!(captured.record.id.starts_with(InputMode::Real.capture_prefix()));validate_existing_real_root(&configured).unwrap();let before=fs::read(&configured.db).unwrap();drop(read(&configured).unwrap());assert_eq!(before,fs::read(&configured.db).unwrap());fs::remove_dir_all(&configured.root).unwrap();}
#[test] fn provider_settings_are_nonsecret_atomic_and_session_only(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-settings");let mut state=default_provider_state();let settings=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://api.example.test/v1".into(),model:"fixture-model".into(),temperature_bps:70,max_output_tokens:512,timeout_ms:30_000};let saved=save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings.clone()}).unwrap();assert!(!saved.enabled&&!saved.credential.present);set_provider_session_credential(&mut state,SessionCredentialRequest{credential:Some("SESSION_SECRET_DO_NOT_PERSIST".into()),environment_variable:None}).unwrap();let file=provider_settings_path(&p);let raw=fs::read_to_string(&file).unwrap();assert!(!raw.contains("SESSION_SECRET_DO_NOT_PERSIST"));let meta=fs::symlink_metadata(&file).unwrap();assert_eq!(meta.permissions().mode()&0o777,0o600);let reloaded=load_provider_state(&p).unwrap();assert_eq!(reloaded.settings,settings);assert!(!credential_status(&reloaded.credential).present);clean(&p);}
#[test] fn provider_rejects_unsafe_endpoints_and_never_enables_stale_config(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-negative");let mut state=default_provider_state();for url in ["http://169.254.1.9/v1","http://224.0.0.1/v1","file:///tmp/not-allowed","https://user:pass@api.example.test/v1"]{let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:url.into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&settings).is_err());}let cloud_ip=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://127.0.0.1/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&cloud_ip).is_err());assert_eq!(serde_json::from_str::<ProviderProfile>("\"custom_openai_compatible\"").unwrap(),ProviderProfile::CustomOpenaiCompatible);let wrong_mode=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Ollama,base_url:"https://api.example.test/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert_eq!(validate_provider_settings(&wrong_mode).unwrap_err().code,"provider_profile_mode_rejected");let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:"http://127.0.0.1:11434/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings}).unwrap();assert_eq!(set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap_err().code,"provider_enablement_rejected");assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_connection_failed");assert!(!state.enabled);clean(&p);}
#[test] fn provider_understanding_requires_explicit_successful_enablement(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-understanding");let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();let mut state=default_provider_state();let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-test-explicit".into(),include_related_personal_content:None,additional_context_confirmed:None};assert!(provider_understanding(&p,&mut state,&request).unwrap().understanding_id.is_empty());assert_eq!(state.model_request_count,0);clean(&p);}
#[test] fn disabled_provider_is_a_persisted_non_network_state(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-disabled");let mut state=default_provider_state();let saved=save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:default_provider_settings()}).unwrap();assert_eq!(saved.connection_state,"disabled");assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_disabled");assert_eq!(load_provider_state(&p).unwrap().connection_state,"disabled");clean(&p);}
#[test] fn synthetic_lifecycle_and_no_write_rejection(){if mode().unwrap()==InputMode::Real{return;}let p=test_paths("synthetic");let c=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();assert_eq!(c.record_count,1);assert!(next(&p,&ContextRequest{context_id:CONTEXT.into()}).unwrap().candidates.is_empty());confirm(&p,&ConfirmRequest{capture_id:c.record.id,context_id:CONTEXT.into(),decision:LinkDecision::Confirm,idempotency_key:"p3-141-link-001".into()}).unwrap();let candidate=next(&p,&ContextRequest{context_id:CONTEXT.into()}).unwrap().candidates.remove(0);decide(&p,&NextRequest{candidate_id:candidate.candidate_id,decision:NextDecision::Accept,edited_text:None,idempotency_key:"p3-141-accept-001".into()}).unwrap();assert_eq!(today(&p).unwrap().confirmed_actions.len(),1);let before=hash(&p.db);assert_eq!(capture(&p,&CaptureRequest{text:"bad".into(),key:"bad".into()}).unwrap_err().code,"argument_schema_rejected");assert_eq!(before,hash(&p.db));clean(&p);}
#[test] fn synthetic_insufficient_evidence_never_creates_candidate_or_action(){if mode().unwrap()==InputMode::Real{return;}let p=test_paths("synthetic-insufficient");let c=capture(&p,&CaptureRequest{text:SYN_SHORT.into(),key:SYN_SHORT_KEY.into()}).unwrap();assert_eq!(c.link_status,"unlinked");let before=hash(&p.db);assert!(next(&p,&ContextRequest{context_id:CONTEXT.into()}).unwrap().candidates.is_empty());assert!(today(&p).unwrap().confirmed_actions.is_empty());assert_eq!(before,hash(&p.db));let reopened=read(&p).unwrap();let captures:i64=reopened.query_row("SELECT count(*) FROM captures",[],|r|r.get(0)).unwrap();let candidates:i64=reopened.query_row("SELECT count(*) FROM candidate_actions",[],|r|r.get(0)).unwrap();let actions:i64=reopened.query_row("SELECT count(*) FROM actions",[],|r|r.get(0)).unwrap();assert_eq!((captures,candidates,actions),(1,0,0));clean(&p);}
#[test] fn persistent_link_is_created_only_after_explicit_confirmation(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("explicit-link");let c=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();let conn=read(&p).unwrap();let before:i64=conn.query_row("SELECT count(*) FROM capture_project_links",[],|r|r.get(0)).unwrap();assert_eq!((c.link_status,before),("unlinked".into(),0));drop(conn);let rejected=confirm(&p,&ConfirmRequest{capture_id:c.record.id.clone(),context_id:CONTEXT.into(),decision:LinkDecision::Reject,idempotency_key:"p3-141-link-reject".into()}).unwrap();assert_eq!(rejected.recovery.state,"empty");let after_reject=read(&p).unwrap().query_row("SELECT count(*) FROM capture_project_links",[],|r|r.get::<_,i64>(0)).unwrap();assert_eq!(after_reject,0);let confirmed=confirm(&p,&ConfirmRequest{capture_id:c.record.id,context_id:CONTEXT.into(),decision:LinkDecision::Confirm,idempotency_key:"p3-141-link-confirm".into()}).unwrap();assert_eq!(confirmed.recovery.state,"confirmed");let after_confirm=read(&p).unwrap().query_row("SELECT count(*) FROM capture_project_links",[],|r|r.get::<_,i64>(0)).unwrap();assert_eq!(after_confirm,1);clean(&p);}
#[test] fn real_mode_model_port_is_explicit_and_not_implicit(){if mode().unwrap()!=InputMode::Real{return;}let p=test_paths("real-provider-gate");let mut state=default_provider_state();let settings=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://api.example.test".into(),model:"user-selected-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings}).unwrap();assert!(!state.enabled);let unavailable=provider_understanding(&p,&mut state,&UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:None,removed_context_kinds:None,request_id:"p3-137-real-explicit-only".into(),include_related_personal_content:None,additional_context_confirmed:None}).unwrap_err();assert_eq!(unavailable.code,"selection_required");assert_eq!(state.model_request_count,0);assert_eq!(status(&p).model_port,"replaceable_provider_explicit_only");clean(&p);}
#[test] fn request_local_bundle_is_minimal_and_does_not_require_persistent_link(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("request-local");let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();let before=hash(&p.db);let bundle=global(&p,&GlobalRequest{page:Page::Today,selection_ref:Some(capture.record.id.clone()),removed_context_kinds:None,include_related_personal_content:None}).unwrap();let kinds=bundle.included.iter().map(|item|item.kind.as_str()).collect::<Vec<_>>();assert_eq!(kinds,["selection","page","person_domain","project","evidence_memory"]);assert!(!bundle.disclosure_required&&bundle.request_local);assert_eq!(before,hash(&p.db));let pending=understanding(&p,&UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-unlinked-minimal".into(),include_related_personal_content:None,additional_context_confirmed:None}).unwrap();assert_eq!(pending.identity,"no_reliable_understanding");clean(&p);}
#[test] fn additional_personal_content_is_disclosed_before_any_request_or_write(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("disclosure");let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();let before=hash(&p.db);let bundle=global(&p,&GlobalRequest{page:Page::Today,selection_ref:Some(capture.record.id.clone()),removed_context_kinds:None,include_related_personal_content:Some(true)}).unwrap();assert!(bundle.disclosure_required);assert_eq!(bundle.additional_personal_count,1);assert!(bundle.included.iter().any(|item|item.additional_personal_content&&item.authorization=="request_local:pending_confirmation"));let mut state=default_provider_state();let pending=provider_understanding(&p,&mut state,&UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-extra-pending".into(),include_related_personal_content:Some(true),additional_context_confirmed:Some(false)}).unwrap();assert_eq!(pending.identity,"request_disclosure_required");assert_eq!(state.model_request_count,0);assert_eq!(before,hash(&p.db));clean(&p);}
}

#[cfg(test)]
mod provider_fixture_tests {
    use super::*;
    use std::net::TcpListener;
    use std::thread;

    fn test_paths(name: &str) -> Paths { let base=paths().unwrap().root; let root=base.join(format!("p3-136-{name}-{}",now().unwrap())); let _=fs::remove_dir_all(&root); fs::create_dir(&root).unwrap(); Paths{db:root.join(DB),root,mode:InputMode::Synthetic} }
    fn fixture(replies: Vec<String>, delay_ms: u64) -> (u16, thread::JoinHandle<Vec<String>>) { let listener=TcpListener::bind("127.0.0.1:0").unwrap(); let port=listener.local_addr().unwrap().port(); let handle=thread::spawn(move || { let mut seen=Vec::new(); for reply in replies { let (mut stream,_)=listener.accept().unwrap(); stream.set_read_timeout(Some(Duration::from_secs(2))).unwrap(); let mut raw=vec![0u8;8192]; let count=stream.read(&mut raw).unwrap_or(0); seen.push(String::from_utf8_lossy(&raw[..count]).into_owned()); if delay_ms>0 { thread::sleep(Duration::from_millis(delay_ms)); } let _=stream.write_all(reply.as_bytes()); } seen }); (port,handle) }
    fn settings(port:u16, profile:ProviderProfile) -> ProviderSettings { ProviderSettings{mode:ProviderMode::Local,profile,base_url:format!("http://127.0.0.1:{port}/fixture"),model:"fixture-model".into(),temperature_bps:70,max_output_tokens:256,timeout_ms:1_000} }
    fn reply(status:&str, body:&str)->String { format!("HTTP/1.1 {status}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",body.len()) }
    fn output(profile:ProviderProfile, evidence_ref:&str)->String { let inner=serde_json::json!({"kind":"suggestion","summary":"合成 Provider 建议","uncertainty":"synthetic_fixture","evidence_refs":[evidence_ref]}).to_string().replace('"',"\\\""); match profile { ProviderProfile::Anthropic=>format!(r#"{{"content":[{{"text":"{inner}"}}]}}"#),ProviderProfile::Ollama=>format!(r#"{{"message":{{"content":"{inner}"}}}}"#),_=>format!(r#"{{"choices":[{{"message":{{"content":"{inner}"}}}}]}}"#) } }

    #[test]
    fn loopback_probe_send_feedback_restart_and_no_implicit_repeat() { let p=test_paths("lifecycle"); let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap(); let evidence_ref=format!("capture:{}",capture.record.id); let (port,handle)=fixture(vec![reply("200 OK",r#"{"models":[{"name":"fixture-model"}]}"#),reply("200 OK",&output(ProviderProfile::Ollama,&evidence_ref))],0); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::Ollama)}).unwrap(); let probe=test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap(); assert_eq!(probe.models,vec!["fixture-model"]); set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap(); let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-loopback-001".into(),include_related_personal_content:None,additional_context_confirmed:None}; let understanding=provider_understanding(&p,&mut state,&request).unwrap(); assert!(understanding.suggestion.is_some()); assert_eq!(state.model_request_count,1); assert_eq!(state.locked_profile,Some(ProviderProfile::Ollama)); let switch_request=SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::LmStudio)}; assert_eq!(save_provider_settings(&p,&mut state,switch_request).unwrap_err().code,"provider_locked_after_first_send"); let repeated=provider_understanding(&p,&mut state,&request).unwrap(); assert_eq!(repeated.understanding_id,understanding.understanding_id); assert_eq!(state.model_request_count,1); let feedback=feedback(&p,&FeedbackRequest{understanding_id:understanding.understanding_id.clone(),decision:FeedbackDecision::Confirm,edited_text:None,idempotency_key:"p3-137-feedback-001".into()}).unwrap(); assert_eq!(feedback.status,"saved"); assert_eq!(today(&p).unwrap().confirmed_actions.len(),1); let reopened=load_provider_state(&p).unwrap(); assert!(!reopened.enabled); assert_eq!(reopened.locked_profile,Some(ProviderProfile::Ollama)); assert_eq!(today(&p).unwrap().confirmed_actions.len(),1); let seen=handle.join().unwrap(); assert_eq!(seen.len(),2); assert!(seen[0].contains("GET /fixture/api/tags")); assert!(!seen[0].contains("Content-Length:")); assert!(seen[1].contains("POST /fixture/api/chat")); assert!(seen[1].contains("Evidence reference: capture:")); assert!(!seen[0].contains(SYN_TEXT)); let raw=fs::read_to_string(provider_settings_path(&p)).unwrap(); assert!(!raw.contains(SYN_TEXT)); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn authorized_unlinked_selection_still_sends_minimal_request() { let p=test_paths("authorized-unlinked"); let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap(); let evidence_ref=format!("capture:{}",capture.record.id); let (port,handle)=fixture(vec![reply("200 OK",r#"{"models":[{"name":"fixture-model"}]}"#),reply("200 OK",&output(ProviderProfile::Ollama,&evidence_ref))],0); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::Ollama)}).unwrap(); test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap(); set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap(); let links:i64=read(&p).unwrap().query_row("SELECT count(*) FROM capture_project_links",[],|row|row.get(0)).unwrap(); assert_eq!(links,0); let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-authorized-unlinked".into(),include_related_personal_content:None,additional_context_confirmed:None}; assert!(provider_understanding(&p,&mut state,&request).unwrap().understanding_id.starts_with("understanding:p3-137:")); assert_eq!(state.model_request_count,1); assert_eq!(read(&p).unwrap().query_row("SELECT count(*) FROM capture_project_links",[],|row|row.get::<_,i64>(0)).unwrap(),0); assert_eq!(handle.join().unwrap().len(),2); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn revoked_authorization_blocks_bundle_and_provider_before_dispatch() { let p=test_paths("authorization-revoked"); let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap(); write(&p,|conn|{conn.execute("UPDATE projects SET authorized=0 WHERE id=?1",params![PROJECT]).map_err(sql)?;Ok(())}).unwrap(); let before=fs::read(&p.db).unwrap(); let global_error=match global(&p,&GlobalRequest{page:Page::Today,selection_ref:Some(capture.record.id.clone()),removed_context_kinds:None,include_related_personal_content:None}) { Err(error)=>error, Ok(_)=>panic!("revoked selection unexpectedly assembled a Bundle") }; assert_eq!(global_error.code,"selection_authorization_stale"); let mut state=default_provider_state(); let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-revoked-before-dispatch".into(),include_related_personal_content:None,additional_context_confirmed:None}; let provider_error=provider_understanding(&p,&mut state,&request).unwrap_err(); assert_eq!(provider_error.code,"selection_authorization_stale"); assert_eq!(state.model_request_count,0); assert_eq!(before,fs::read(&p.db).unwrap()); assert!(today(&p).unwrap().confirmed_actions.is_empty()); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn authorization_race_recheck_blocks_derived_transaction_without_retry() { let p=test_paths("authorization-race"); let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap(); let evidence_ref=format!("capture:{}",capture.record.id); let (port,handle)=fixture(vec![reply("200 OK",r#"{"models":[{"name":"fixture-model"}]}"#),reply("200 OK",&output(ProviderProfile::Ollama,&evidence_ref))],0); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::Ollama)}).unwrap(); test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap(); set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap(); let before=(read(&p).unwrap().query_row("SELECT count(*) FROM understandings",[],|row|row.get::<_,i64>(0)).unwrap(),read(&p).unwrap().query_row("SELECT count(*) FROM audit",[],|row|row.get::<_,i64>(0)).unwrap(),today(&p).unwrap().confirmed_actions.len()); TEST_REVOKE_AFTER_PROVIDER_DISPATCH.store(true,Ordering::SeqCst); let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-revoked-race".into(),include_related_personal_content:None,additional_context_confirmed:None}; let error=provider_understanding(&p,&mut state,&request).unwrap_err(); assert_eq!(error.code,"selection_authorization_stale"); let after=(read(&p).unwrap().query_row("SELECT count(*) FROM understandings",[],|row|row.get::<_,i64>(0)).unwrap(),read(&p).unwrap().query_row("SELECT count(*) FROM audit",[],|row|row.get::<_,i64>(0)).unwrap(),today(&p).unwrap().confirmed_actions.len()); assert_eq!(before,after); assert_eq!(state.model_request_count,1); assert_eq!(read(&p).unwrap().query_row("SELECT authorized FROM projects WHERE id=?1",params![PROJECT],|row|row.get::<_,i64>(0)).unwrap(),0); assert_eq!(handle.join().unwrap().len(),2); fs::remove_dir_all(&p.root).unwrap(); }

    fn models(profile:ProviderProfile)->serde_json::Value { match profile { ProviderProfile::Anthropic=>serde_json::json!({"data":[{"id":"fixture-model","type":"model","display_name":"Synthetic"}],"has_more":false}), ProviderProfile::Ollama=>serde_json::json!({"models":[{"name":"fixture-model","size":1}]}), _=>serde_json::json!({"object":"list","data":[{"id":"fixture-model","object":"model"}]}) } }
    #[test]
    fn protocol_adapters_cover_the_closed_four_profiles_and_reject_mismatches() { for profile in [ProviderProfile::Openai,ProviderProfile::Anthropic,ProviderProfile::Ollama,ProviderProfile::LmStudio] { let port=model_port(profile); let probe=port.build_probe(); assert_eq!(probe.method,WireMethod::Get); assert!(probe.body.is_none()); assert_eq!(port.parse_models(&models(profile)).unwrap(),vec!["fixture-model"]); assert_eq!(port.parse_models(&serde_json::json!({"wrong_envelope":["fixture-model"]})).unwrap_err().code,"provider_protocol_rejected"); let wire=port.build_inference(&ProviderInferenceInput{model:"fixture-model",temperature_bps:70,max_output_tokens:256,page:"today",selected_text:SYN_TEXT,evidence_ref:"capture:synthetic"}).unwrap(); assert_eq!(wire.method,WireMethod::Post); let body:serde_json::Value=serde_json::from_str(wire.body.as_deref().unwrap()).unwrap(); match profile { ProviderProfile::Anthropic=>{assert_eq!(probe.path,"/v1/models");assert_eq!(wire.path,"/v1/messages");assert_eq!(body["model"],"fixture-model");assert_eq!(body["max_tokens"],256);assert_eq!(body["messages"][0]["role"],"user");assert!(body["system"].as_str().unwrap().contains("evidence_refs"));}, ProviderProfile::Ollama=>{assert_eq!(probe.path,"/api/tags");assert_eq!(wire.path,"/api/chat");assert_eq!(body["stream"],false);assert_eq!(body["options"]["num_predict"],256);assert_eq!(body["messages"][0]["role"],"system");}, _=>{assert_eq!(probe.path,"/v1/models");assert_eq!(wire.path,"/v1/chat/completions");assert_eq!(body["response_format"]["type"],"json_object");assert_eq!(body["max_tokens"],256);assert_eq!(body["messages"][1]["role"],"user");} } let parsed=parse_provider_output(profile,output(profile,"capture:synthetic").as_bytes()).unwrap(); assert_eq!(parsed.kind,"suggestion"); assert_eq!(parsed.uncertainty,"synthetic_fixture"); assert_eq!(parse_provider_output(profile,br#"{"wrong_response":true}"#).unwrap_err().code,"provider_protocol_mismatch"); } assert!(model_port(ProviderProfile::Openai).credential_header("synthetic").unwrap().starts_with("Authorization: Bearer ")); assert_eq!(model_port(ProviderProfile::Anthropic).credential_header("synthetic").unwrap(),"x-api-key: synthetic"); assert!(model_port(ProviderProfile::Ollama).credential_header("synthetic").is_none()); assert!(model_port(ProviderProfile::LmStudio).credential_header("synthetic").unwrap().starts_with("Authorization: Bearer ")); }

    #[test]
    fn provider_failures_do_not_persist_derived_objects_or_enable() { let p=test_paths("failures"); let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap(); let before=fs::read(&p.db).unwrap(); let (port,handle)=fixture(vec![reply("302 Found",r#"{"models":["fixture-model"]}"#)],0); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::LmStudio)}).unwrap(); assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_redirect_rejected"); assert!(!state.enabled); assert_eq!(before,fs::read(&p.db).unwrap()); assert_eq!(state.model_request_count,0); handle.join().unwrap(); let cancel=test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:Some(true)}).unwrap_err(); assert_eq!(cancel.code,"provider_test_cancelled"); let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-no-send".into(),include_related_personal_content:None,additional_context_confirmed:None}; assert!(provider_understanding(&p,&mut state,&request).unwrap().understanding_id.is_empty()); assert_eq!(state.model_request_count,0); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn loopback_timeout_http_malformed_oversize_disconnect_and_protocol_mismatch_fail_closed() { let p=test_paths("network-matrix"); for (name,wire,delay,expected) in [("http",reply("503 Service Unavailable",r#"{"error":"synthetic"}"#),0,"provider_http_status_rejected"),("malformed","not-http".into(),0,"provider_protocol_rejected"),("oversize",reply("200 OK",&format!(r#"{{"models":["{}"]}}"#,"x".repeat(140_000))),0,"provider_response_too_large"),("timeout",reply("200 OK",r#"{"models":["fixture-model"]}"#),1_200,"provider_response_failed")] { let (port,handle)=fixture(vec![wire],delay); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::Ollama)}).unwrap(); assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,expected,"{name}"); assert!(!state.enabled); handle.join().unwrap(); }
        let listener=TcpListener::bind("127.0.0.1:0").unwrap(); let port=listener.local_addr().unwrap().port(); let close=thread::spawn(move||{let (_stream,_)=listener.accept().unwrap();}); let mut state=default_provider_state(); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings(port,ProviderProfile::Ollama)}).unwrap(); let disconnected=test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code; assert!(matches!(disconnected,"provider_protocol_rejected"|"provider_response_failed")); close.join().unwrap(); assert_eq!(parse_provider_output(ProviderProfile::Anthropic,br#"{"choices":[]}"#).unwrap_err().code,"provider_protocol_mismatch"); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn feedback_all_decisions_are_audited_and_only_confirmation_affects_today() { let p=test_paths("feedback-matrix"); write(&p, |conn| { for number in 0..5 { conn.execute("INSERT INTO understandings(id,request_id,kind,summary,provider,model,evidence_refs_json,uncertainty,created_at_ms) VALUES(?1,?2,'suggestion','synthetic summary','ollama','fixture-model','[\"capture:synthetic\"]','synthetic',?3)",params![format!("understanding:p3-136:feedback-{number}"),format!("p3-136-feedback-request-{number}"),now()?]).map_err(sql)?; } Ok(()) }).unwrap(); for (number,decision,edited) in [(0,FeedbackDecision::Confirm,None),(1,FeedbackDecision::EditConfirm,Some("synthetic edited confirmation".into())),(2,FeedbackDecision::Reject,None),(3,FeedbackDecision::Ignore,None),(4,FeedbackDecision::Correct,None)] { let result=feedback(&p,&FeedbackRequest{understanding_id:format!("understanding:p3-136:feedback-{number}"),decision,edited_text:edited,idempotency_key:format!("p3-136-feedback-matrix-{number}")}).unwrap(); assert_eq!(result.status,"saved"); } let today_state=today(&p).unwrap(); assert_eq!(today_state.confirmed_actions.len(),2); let conn=read(&p).unwrap(); let feedback_count:i64=conn.query_row("SELECT count(*) FROM feedback WHERE target_kind='understanding'",[],|row|row.get(0)).unwrap(); let audit_events:i64=conn.query_row("SELECT count(*) FROM audit WHERE event IN ('understanding_confirmed','understanding_edited_confirmed','understanding_rejected','understanding_ignored','understanding_corrected')",[],|row|row.get(0)).unwrap(); assert_eq!(feedback_count,5); assert_eq!(audit_events,5); fs::remove_dir_all(&p.root).unwrap(); }

    #[test]
    fn settings_link_temp_and_failure_preserve_db_sentinel() { use std::os::unix::fs::symlink; let p=test_paths("settings-boundary"); let mut state=default_provider_state(); let setting=settings(19001,ProviderProfile::Ollama); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting.clone()}).unwrap(); let settings_file=provider_settings_path(&p); let original=fs::read(&settings_file).unwrap(); let sentinel=p.root.join("db-sentinel"); fs::write(&sentinel,b"p3-136 synthetic sentinel").unwrap(); let sentinel_before=fs::read(&sentinel).unwrap(); let temporary=p.root.join(".ai-provider-settings.tmp"); fs::write(&temporary,b"unexpected temp").unwrap(); assert_eq!(save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting.clone()}).unwrap_err().code,"provider_settings_file_rejected"); assert_eq!(original,fs::read(&settings_file).unwrap()); assert_eq!(sentinel_before,fs::read(&sentinel).unwrap()); fs::remove_file(&temporary).unwrap(); fs::remove_file(&settings_file).unwrap(); let target=p.root.join("not-a-settings-file"); fs::write(&target,b"synthetic").unwrap(); symlink(&target,&settings_file).unwrap(); assert_eq!(save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting}).unwrap_err().code,"provider_settings_file_rejected"); assert_eq!(sentinel_before,fs::read(&sentinel).unwrap()); fs::remove_dir_all(&p.root).unwrap(); }
}

#[cfg(test)]
mod provider_restoration_tests {
    use super::*;
    use std::net::TcpListener;
    use std::thread;

    fn fixture(replies: Vec<String>) -> (u16, thread::JoinHandle<Vec<String>>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let handle = thread::spawn(move || {
            let mut requests = Vec::new();
            for reply in replies {
                let (mut stream, _) = listener.accept().unwrap();
                let mut raw = vec![0_u8; 16_384];
                let count = stream.read(&mut raw).unwrap();
                requests.push(String::from_utf8_lossy(&raw[..count]).into_owned());
                stream.write_all(reply.as_bytes()).unwrap();
            }
            requests
        });
        (port, handle)
    }

    fn reply(body: &str) -> String {
        format!("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", body.len())
    }

    #[test]
    fn custom_openai_compatible_loopback_is_protocol_bound_and_first_send_locks() {
        if mode().unwrap() != InputMode::Synthetic { return; }
        let base = paths().unwrap().root;
        let root = base.join(format!("provider-restoration-custom-{}", now().unwrap()));
        fs::create_dir(&root).unwrap();
        let paths = Paths { db: root.join(DB), root, mode: InputMode::Synthetic };
        let capture = capture(&paths, &CaptureRequest { text: SYN_TEXT.into(), key: SYN_KEY.into() }).unwrap();
        let evidence_ref = format!("capture:{}", capture.record.id);
        let inner = serde_json::json!({"kind":"suggestion","summary":"synthetic custom provider result","uncertainty":"synthetic_fixture","evidence_refs":[evidence_ref]}).to_string().replace('"', "\\\"");
        let response = format!(r#"{{"choices":[{{"message":{{"content":"{inner}"}}}}]}}"#);
        let (port, handle) = fixture(vec![
            reply(r#"{"object":"list","data":[{"id":"fixture-model"}]}"#),
            reply(&response),
        ]);
        let custom = ProviderSettings { mode: ProviderMode::Local, profile: ProviderProfile::CustomOpenaiCompatible, base_url: format!("http://127.0.0.1:{port}/fixture"), model: "fixture-model".into(), temperature_bps: 70, max_output_tokens: 256, timeout_ms: 1_000 };
        let mut state = default_provider_state();
        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: custom.clone() }).unwrap();
        assert_eq!(test_provider_connection(&paths, &mut state, TestProviderConnectionRequest { cancel: None }).unwrap().provider, "custom_openai_compatible");
        set_provider_enabled(&mut state, SetProviderEnabledRequest { enabled: true }).unwrap();
        let request = UnderstandingRequest { context_id: "request-local".into(), page: Page::Today, selection_ref: Some(capture.record.id), removed_context_kinds: None, request_id: "p3-137-provider-restoration-custom".into(), include_related_personal_content: None, additional_context_confirmed: None };
        assert!(provider_understanding(&paths, &mut state, &request).unwrap().suggestion.is_some());
        assert_eq!(state.locked_profile, Some(ProviderProfile::CustomOpenaiCompatible));
        let switched = ProviderSettings { profile: ProviderProfile::LmStudio, ..custom };
        assert_eq!(save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: switched }).unwrap_err().code, "provider_locked_after_first_send");
        let requests = handle.join().unwrap();
        assert_eq!(requests.len(), 2);
        assert!(requests[0].contains("GET /fixture/v1/models"));
        assert!(requests[1].contains("POST /fixture/v1/chat/completions"));
        assert_eq!(state.model_request_count, 1);
        fs::remove_dir_all(&paths.root).unwrap();
    }

    #[test]
    fn custom_profile_rejects_wrong_envelope_response_mode_and_credential_order() {
        let custom = ProviderProfile::CustomOpenaiCompatible;
        let port = model_port(custom);
        assert_eq!(port.parse_models(&serde_json::json!({"models":["fixture-model"]})).unwrap_err().code, "provider_protocol_rejected");
        assert_eq!(parse_provider_output(custom, br#"{"message":{"content":"wrong"}}"#).unwrap_err().code, "provider_protocol_mismatch");
        let wrong_mode = ProviderSettings { mode: ProviderMode::Cloud, profile: ProviderProfile::Ollama, base_url: "https://fixture.lifeos.test:1/v1".into(), model: "fixture-model".into(), temperature_bps: 0, max_output_tokens: 1, timeout_ms: 1_000 };
        assert_eq!(validate_provider_settings_for(&wrong_mode, InputMode::Synthetic).unwrap_err().code, "provider_profile_mode_rejected");
        let mut state = default_provider_state();
        let disabled = set_provider_enabled(&mut state, SetProviderEnabledRequest { enabled: true }).unwrap_err();
        assert_eq!(disabled.code, "provider_enablement_rejected");
    }
}

#[cfg(test)]
mod closure_tests {
    use super::*;
    use sha2::{Digest, Sha256};

    #[derive(Clone, Debug, PartialEq, Eq)]
    struct Snapshot { db_hash: String, counts: [i64; 6] }

    fn taint() -> String { ["P3_141_", "SYNTHETIC_TAINT"].concat() }
    fn root_for(case: &str) -> Paths {
        let base = paths().unwrap().root.parent().unwrap().to_path_buf();
        fs::create_dir_all(&base).unwrap();
        let root = base.join(format!("closure-{case}-{}", now().unwrap()));
        if root.exists() { fs::remove_dir_all(&root).unwrap(); }
        Paths { db: root.join(DB), root, mode: InputMode::Real }
    }
    fn sentinel_for(paths: &Paths, case: &str) -> PathBuf {
        let sentinel = paths.root.parent().unwrap().join(format!("closure-sentinel-{case}-{}", now().unwrap()));
        fs::write(&sentinel, b"P3-141 sentinel").unwrap();
        sentinel
    }
    fn digest(path: &Path) -> String {
        let mut h = Sha256::new();
        h.update(fs::read(path).unwrap());
        format!("{:x}", h.finalize())
    }
    fn snapshot(paths: &Paths) -> Snapshot {
        if !paths.db.exists() { return Snapshot { db_hash: "absent".into(), counts: [0; 6] }; }
        if !fs::symlink_metadata(&paths.db).unwrap().file_type().is_file() { return Snapshot { db_hash: "non_regular".into(), counts: [-1; 6] }; }
        let db_hash = digest(&paths.db);
        let conn = match Connection::open_with_flags(&paths.db, OpenFlags::SQLITE_OPEN_READ_ONLY) {
            Ok(conn) => conn,
            Err(_) => return Snapshot { db_hash, counts: [-1; 6] },
        };
        let mut counts = [0; 6];
        for (index, table) in ["captures", "audit", "capture_project_links", "candidate_actions", "actions", "action_results"].iter().enumerate() {
            counts[index] = conn.query_row(&format!("SELECT count(*) FROM {table}"), [], |row| row.get(0)).unwrap_or(-1);
        }
        Snapshot { db_hash, counts }
    }
    fn receipt(case: &str, error: &Error, before: &Snapshot, after: &Snapshot, sentinel: &Path) {
        let sentinel_hash = digest(sentinel);
        println!(
            "P3-141-CLOSURE-RECEIPT|case={case}|code={}|db_before={}|db_after={}|counts_before={:?}|counts_after={:?}|sentinel_hash={sentinel_hash}",
            error.code, before.db_hash, after.db_hash, before.counts, after.counts
        );
        assert_eq!(before, after, "{case} mutated the database or audit");
    }
    fn cleanup(paths: &Paths, sentinel: &Path) {
        if paths.root.exists() { fs::remove_dir_all(&paths.root).unwrap(); }
        fs::remove_file(sentinel).unwrap();
    }
    fn capture_real(paths: &Paths, key: &str, suffix: &str) -> CaptureResponse {
        capture(paths, &CaptureRequest { text: format!("{}-{suffix}", taint()), key: key.into() }).unwrap()
    }
    fn real_memory(id: &str) -> memory_context::DurableMemoryRequest {
        memory_context::DurableMemoryRequest {
            operation: memory_context::MemoryOperation::Create, memory_id: id.into(), replacement_id: None,
            statement: Some(format!("Synthetic P3-141 controlled memory fixture {id}.")), memory_type: Some("preference".into()),
            source_refs: Some(vec!["source:local:user-confirmed".into()]), observed_at_ms: None,
            domain: memory_context::Domain::Person, scope: "person".into(), expected_generation: None,
            idempotency_key: format!("p3-141-real-ui-memory-{id}"),
        }
    }
    fn real_health(id: &str, energy: u8) -> memory_context::CurrentStateRequest {
        memory_context::CurrentStateRequest {
            operation: memory_context::StateOperation::Set, state_id: id.into(), replacement_id: None,
            state_key: Some("health_fitness_structured_v1".into()), value: None, domain: memory_context::Domain::Health,
            source_refs: Some(vec!["source:local:user-confirmed".into()]), expires_at_ms: Some(now().unwrap()+86_400_000), expected_generation: None,
            idempotency_key: format!("p3-141-real-ui-health-{id}"), structured_health: Some(memory_context::StructuredHealthState {
                sleep_duration_range: memory_context::SleepDurationRange::SevenToNineHours, energy, soreness_or_pain: false,
                training_load: memory_context::TrainingLoad::Medium, available_time: memory_context::AvailableTime::ThirtyToSixtyMinutes,
            }),
        }
    }
    fn seed_prior_work_days(paths: &Paths, count: i64) {
        write(paths, |conn| {
            let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(sql)?;
            let time=now()?;
            for number in 1..=count {
                let created=time-(count-number+1)*86_400_000;
                let key=format!("p3-141-real-ui-seeded-{number}");
                let id=format!("{}{}",InputMode::Real.capture_prefix(),key);
                tx.execute("INSERT INTO captures(id,content,created_at_ms,source,source_id,artifact_version,idem_key) VALUES(?1,?2,?3,'local_capture',?4,?5,?6)",params![id,format!("{}-seeded-{number}",taint()),created,InputMode::Real.source(),InputMode::Real.artifact(),key]).map_err(sql)?;
                tx.execute("INSERT INTO work_trial_days(day_key,capture_id,created_at_ms) VALUES(strftime('%Y-%m-%d',?1 / 1000,'unixepoch','localtime'),?2,?1)",params![created,id]).map_err(sql)?;
            }
            tx.commit().map_err(sql)
        }).unwrap();
    }
    fn confirm_real(paths: &Paths, capture_id: &str, key: &str) {
        confirm(paths, &ConfirmRequest {
            capture_id: capture_id.into(), context_id: CONTEXT.into(), decision: LinkDecision::Confirm, idempotency_key: key.into(),
        }).unwrap();
    }
    fn candidate_real(paths: &Paths) -> String {
        next(paths, &ContextRequest { context_id: CONTEXT.into() }).unwrap().candidates.remove(0).candidate_id
    }
    fn blocked<T>(value: Result<T, Error>) -> Error {
        match value { Err(error) => error, Ok(_) => panic!("expected a fail-closed result") }
    }

    #[test]
    fn closure_whitespace_real_capture_is_prewrite_rejected() {
        let paths = root_for("whitespace");
        for (case, text) in [("empty", ""), ("ascii", " \n\t "), ("unicode", "\u{3000}\u{00a0}\u{2003}")] {
            let sentinel = sentinel_for(&paths, case);
            let before = snapshot(&paths);
            let error = capture(&paths, &CaptureRequest { text: text.into(), key: format!("p3-141-real-ui-whitespace-{case}") }).unwrap_err();
            let after = snapshot(&paths);
            assert_eq!(error.code, "real_input_rejected");
            receipt(&format!("whitespace_{case}"), &error, &before, &after, &sentinel);
            fs::remove_file(&sentinel).unwrap();
        }
        assert!(!paths.root.exists());
    }

    #[test]
    fn closure_dto_idempotency_and_stale_paths_do_not_mutate() {
        let paths = root_for("dto-idempotency-stale");
        let sentinel = sentinel_for(&paths, "dto-idempotency-stale");
        let first = capture_real(&paths, "p3-141-real-ui-idempotency-first", "first");

        let before = snapshot(&paths);
        let error = capture(&paths, &CaptureRequest { text: format!("{}-different", taint()), key: "p3-141-real-ui-idempotency-first".into() }).unwrap_err();
        assert_eq!(error.code, "idempotency_conflict");
        receipt("idempotency_conflict", &error, &before, &snapshot(&paths), &sentinel);

        let before = snapshot(&paths);
        let error = blocked(confirm(&paths, &ConfirmRequest { capture_id: first.record.id.clone(), context_id: "ctx:wrong".into(), decision: LinkDecision::Confirm, idempotency_key: "p3-141-real-ui-bad-context".into() }));
        assert_eq!(error.code, "argument_schema_rejected");
        receipt("dto_confirm", &error, &before, &snapshot(&paths), &sentinel);

        confirm_real(&paths, &first.record.id, "p3-141-real-ui-confirm-first");
        let candidate = candidate_real(&paths);
        decide(&paths, &NextRequest { candidate_id: candidate.clone(), decision: NextDecision::Reject, edited_text: None, idempotency_key: "p3-141-real-ui-reject-first".into() }).unwrap();
        let before = snapshot(&paths);
        let error = blocked(decide(&paths, &NextRequest { candidate_id: candidate, decision: NextDecision::Reject, edited_text: None, idempotency_key: "p3-141-real-ui-reject-stale".into() }));
        assert_eq!(error.code, "candidate_state_rejected");
        receipt("stale_candidate", &error, &before, &snapshot(&paths), &sentinel);

        let before = snapshot(&paths);
        let error = blocked(decide(&paths, &NextRequest { candidate_id: "candidate:p3-141:bad".into(), decision: NextDecision::EditAccept, edited_text: Some("not-allowed".into()), idempotency_key: "p3-141-real-ui-bad-edit".into() }));
        assert_eq!(error.code, "argument_schema_rejected");
        receipt("dto_real_edit", &error, &before, &snapshot(&paths), &sentinel);
        cleanup(&paths, &sentinel);
    }

    #[test]
    fn closure_limit_file_type_and_database_boundary_fail_closed() {
        let daily = root_for("daily-limit");
        let sentinel = sentinel_for(&daily, "daily-limit");
        capture_real(&daily, "p3-141-real-ui-daily-first", "daily-first");
        drop(read(&daily).unwrap());
        let before = snapshot(&daily);
        let error = capture(&daily, &CaptureRequest { text: format!("{}-daily-second", taint()), key: "p3-141-real-ui-daily-second".into() }).unwrap_err();
        assert_eq!(error.code, "daily_work_limit_rejected");
        receipt("same_day_second_work", &error, &before, &snapshot(&daily), &sentinel);
        cleanup(&daily, &sentinel);

        let total = root_for("total-limit");
        let sentinel = sentinel_for(&total, "total-limit");
        seed_prior_work_days(&total, 14);
        let before = snapshot(&total);
        let error = capture(&total, &CaptureRequest { text: format!("{}-fifteenth", taint()), key: "p3-141-real-ui-fifteenth".into() }).unwrap_err();
        assert_eq!(error.code, "input_limit_rejected");
        receipt("total_fifteenth_work", &error, &before, &snapshot(&total), &sentinel);
        cleanup(&total, &sentinel);

        let file_root = root_for("root-file");
        let sentinel = sentinel_for(&file_root, "root-file");
        fs::write(&file_root.root, b"not-a-directory").unwrap();
        let before = snapshot(&file_root);
        let error = capture(&file_root, &CaptureRequest { text: taint(), key: "p3-141-real-ui-root-file".into() }).unwrap_err();
        assert_eq!(error.code, "runtime_root_type_rejected");
        receipt("root_file_type", &error, &before, &snapshot(&file_root), &sentinel);
        fs::remove_file(&file_root.root).unwrap(); fs::remove_file(&sentinel).unwrap();

        let db_dir = root_for("database-directory");
        let sentinel = sentinel_for(&db_dir, "database-directory");
        capture_real(&db_dir, "p3-141-real-ui-database-directory-init", "database-directory-init");
        fs::remove_file(&db_dir.db).unwrap(); fs::create_dir(&db_dir.db).unwrap();
        let before = snapshot(&db_dir);
        let error = capture(&db_dir, &CaptureRequest { text: taint(), key: "p3-141-real-ui-database-directory".into() }).unwrap_err();
        assert_eq!(error.code, "database_type_rejected");
        receipt("database_file_type", &error, &before, &snapshot(&db_dir), &sentinel);
        cleanup(&db_dir, &sentinel);

        let sidecar = root_for("sidecar");
        let sentinel = sentinel_for(&sidecar, "sidecar");
        capture_real(&sidecar, "p3-141-real-ui-sidecar-init", "sidecar-init");
        fs::write(sidecar.root.join("capture.sqlite-wal"), b"sidecar").unwrap();
        let before = snapshot(&sidecar);
        let error = capture(&sidecar, &CaptureRequest { text: taint(), key: "p3-141-real-ui-sidecar".into() }).unwrap_err();
        assert_eq!(error.code, "database_sidecar_rejected");
        receipt("sidecar_root_boundary", &error, &before, &snapshot(&sidecar), &sentinel);
        cleanup(&sidecar, &sentinel);
    }

    #[test]
    fn closure_real_memory_cap_is_restart_safe_and_fourth_is_prewrite_rejected() {
        let paths=root_for("memory-cap");
        for number in 1..=3 {
            let id=format!("memory:p3-141:real:fixture-{number}");
            let created=memory_context::upsert(&paths,real_memory(&id)).unwrap();
            let confirmed=memory_context::upsert(&paths,memory_context::DurableMemoryRequest { operation: memory_context::MemoryOperation::Confirm, memory_id:id, replacement_id:None, statement:None, memory_type:None, source_refs:None, observed_at_ms:None, domain:memory_context::Domain::Person, scope:"person".into(), expected_generation:Some(created.generation), idempotency_key:format!("p3-141-real-ui-memory-confirm-{number}") }).unwrap();
            assert_eq!(confirmed.validity,"active");
        }
        let reopened=read(&paths).unwrap();
        let confirmed:i64=reopened.query_row("SELECT count(*) FROM durable_memories WHERE confirmation='confirmed' AND validity='active'",[],|row|row.get(0)).unwrap();
        drop(reopened); assert_eq!(confirmed,3);
        let sentinel=sentinel_for(&paths,"memory-cap"); let before=snapshot(&paths);
        let error=memory_context::upsert(&paths,real_memory("memory:p3-141:real:fixture-4")).unwrap_err();
        assert_eq!(error.code,"durable_memory_limit_rejected"); receipt("durable_memory_fourth",&error,&before,&snapshot(&paths),&sentinel);
        cleanup(&paths,&sentinel);
    }

    #[test]
    fn closure_structured_health_has_five_fields_and_rejects_invalid_or_free_text_before_write() {
        let paths=root_for("structured-health");
        let saved=memory_context::update_state(&paths,real_health("state:p3-141:real:health-1",5)).unwrap();
        assert_eq!(saved.invalidated_slice,"state:health_fitness_structured_v1");
        let reopened=read(&paths).unwrap();
        let fields:(String,i64,i64,String,String)=reopened.query_row("SELECT sleep_duration_range,energy,soreness_or_pain,training_load,available_time FROM structured_health_states WHERE state_id=?1",params![saved.state_id],|row|Ok((row.get(0)?,row.get(1)?,row.get(2)?,row.get(3)?,row.get(4)?))).unwrap();
        drop(reopened); assert_eq!(fields,("seven_to_nine_hours".into(),5,0,"medium".into(),"thirty_to_sixty_minutes".into()));
        let sentinel=sentinel_for(&paths,"structured-health"); let before=snapshot(&paths);
        let error=memory_context::update_state(&paths,real_health("state:p3-141:real:health-invalid",0)).unwrap_err();
        assert_eq!(error.code,"health_schema_rejected"); receipt("health_energy_out_of_range",&error,&before,&snapshot(&paths),&sentinel);
        let raw=r#"{"operation":"set","state_id":"state:p3-141:real:health-free-text","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:local:user-confirmed"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"p3-141-real-ui-health-free-text","structured_health":{"sleep_duration_range":"seven_to_nine_hours","energy":3,"soreness_or_pain":false,"training_load":"low","available_time":"under_thirty_minutes","free_text":"forbidden"}}"#;
        assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(raw).is_err());
        assert_eq!(before,snapshot(&paths));
        cleanup(&paths,&sentinel);
    }

    #[test]
    fn closure_real_root_requires_fresh_absence_and_owned_restart() {
        use std::os::unix::fs::symlink;

        let fresh = root_for("fresh-owned-restart");
        assert!(metadata(&fresh.root).unwrap().is_none());
        assert!(metadata(&fresh.db).unwrap().is_none());
        let first = capture_real(&fresh, "p3-141-real-ui-fresh-owned", "fresh-owned");
        assert!(metadata(&fresh.root).unwrap().is_some());
        assert!(metadata(&fresh.db).unwrap().is_some());
        validate_existing_real_root(&fresh).unwrap();
        let before_restart = snapshot(&fresh);
        let reopened = read(&fresh).unwrap();
        let captures: i64 = reopened.query_row("SELECT count(*) FROM captures", [], |row| row.get(0)).unwrap();
        drop(reopened);
        assert_eq!(captures, 1);
        assert_eq!(before_restart, snapshot(&fresh));
        assert!(first.record.id.starts_with(InputMode::Real.capture_prefix()));
        cleanup(&fresh, &sentinel_for(&fresh, "fresh-owned-restart"));

        let empty = root_for("preexisting-empty");
        let sentinel = sentinel_for(&empty, "preexisting-empty");
        fs::create_dir(&empty.root).unwrap();
        let before = snapshot(&empty);
        let error = capture(&empty, &CaptureRequest { text: taint(), key: "p3-141-real-ui-preexisting-empty".into() }).unwrap_err();
        assert_eq!(error.code, "real_root_ownership_missing");
        receipt("preexisting_empty_root", &error, &before, &snapshot(&empty), &sentinel);
        cleanup(&empty, &sentinel);

        let expected_only = root_for("preexisting-expected-db");
        let sentinel = sentinel_for(&expected_only, "preexisting-expected-db");
        fs::create_dir(&expected_only.root).unwrap(); fs::write(&expected_only.db, b"not-owned").unwrap();
        let before = snapshot(&expected_only);
        let error = capture(&expected_only, &CaptureRequest { text: taint(), key: "p3-141-real-ui-preexisting-expected-db".into() }).unwrap_err();
        assert_eq!(error.code, "real_root_ownership_missing");
        receipt("preexisting_expected_db", &error, &before, &snapshot(&expected_only), &sentinel);
        cleanup(&expected_only, &sentinel);

        let unknown = root_for("preexisting-unknown");
        let sentinel = sentinel_for(&unknown, "preexisting-unknown");
        fs::create_dir(&unknown.root).unwrap(); fs::write(unknown.root.join("foreign.txt"), b"foreign").unwrap();
        let before = snapshot(&unknown);
        let error = capture(&unknown, &CaptureRequest { text: taint(), key: "p3-141-real-ui-preexisting-unknown".into() }).unwrap_err();
        assert_eq!(error.code, "real_root_not_empty");
        receipt("preexisting_unknown_file", &error, &before, &snapshot(&unknown), &sentinel);
        cleanup(&unknown, &sentinel);

        let link = root_for("preexisting-link");
        let sentinel = sentinel_for(&link, "preexisting-link");
        let target = link.root.parent().unwrap().join(format!("closure-link-target-{}", now().unwrap()));
        fs::create_dir(&target).unwrap(); symlink(&target, &link.root).unwrap();
        let before = snapshot(&link);
        let error = capture(&link, &CaptureRequest { text: taint(), key: "p3-141-real-ui-preexisting-link".into() }).unwrap_err();
        assert_eq!(error.code, "runtime_root_type_rejected");
        receipt("preexisting_root_link", &error, &before, &snapshot(&link), &sentinel);
        fs::remove_file(&link.root).unwrap(); fs::remove_dir(&target).unwrap(); fs::remove_file(&sentinel).unwrap();

        let base = paths().unwrap().root.parent().unwrap().to_path_buf();
        let actual_parent = base.join(format!("closure-ancestor-target-{}", now().unwrap()));
        let linked_parent = base.join(format!("closure-ancestor-link-{}", now().unwrap()));
        fs::create_dir(&actual_parent).unwrap(); symlink(&actual_parent, &linked_parent).unwrap();
        let ancestor = Paths { db: linked_parent.join(DB), root: linked_parent.join("child"), mode: InputMode::Real };
        let sentinel = actual_parent.join("ancestor-sentinel"); fs::write(&sentinel, b"P3-141 sentinel").unwrap();
        let before = snapshot(&ancestor);
        let error = capture(&ancestor, &CaptureRequest { text: taint(), key: "p3-141-real-ui-ancestor-link".into() }).unwrap_err();
        assert_eq!(error.code, "path_symlink_rejected");
        receipt("ancestor_link", &error, &before, &snapshot(&ancestor), &sentinel);
        fs::remove_file(&sentinel).unwrap(); fs::remove_file(&linked_parent).unwrap(); fs::remove_dir(&actual_parent).unwrap();
    }

    #[test]
    fn closure_invalid_database_unknown_ipc_and_focus_are_runtime_checked() {
        let bad_db = root_for("bad-database");
        let sentinel = sentinel_for(&bad_db, "bad-database");
        capture_real(&bad_db, "p3-141-real-ui-bad-database-init", "bad-database-init");
        fs::remove_file(&bad_db.db).unwrap(); fs::write(&bad_db.db, b"not-sqlite").unwrap();
        let before = snapshot(&bad_db);
        let error = capture(&bad_db, &CaptureRequest { text: taint(), key: "p3-141-real-ui-bad-database".into() }).unwrap_err();
        assert_eq!(error.code, "database_unavailable");
        receipt("invalid_database", &error, &before, &snapshot(&bad_db), &sentinel);
        cleanup(&bad_db, &sentinel);

        let paths = root_for("focus");
        let sentinel = sentinel_for(&paths, "focus");
        let zero = today(&paths).unwrap();
        assert!(zero.todays_focus.is_none() && zero.confirmed_actions.is_empty());
        let status_receipt = Error::blocked("unknown_ipc_rejected", "runtime status reports unknown IPC rejection");
        assert_eq!(status(&paths).unknown_ipc, "rejected");
        receipt("unknown_ipc_runtime_surface", &status_receipt, &snapshot(&paths), &snapshot(&paths), &sentinel);

        let captured = capture_real(&paths, "p3-141-real-ui-focus", "focus");
        confirm_real(&paths, &captured.record.id, "p3-141-real-ui-focus-confirm");
        let candidate = candidate_real(&paths);
        let action = decide(&paths, &NextRequest { candidate_id: candidate, decision: NextDecision::Accept, edited_text: None, idempotency_key: "p3-141-real-ui-focus-accept".into() }).unwrap().action.unwrap();
        let current = today(&paths).unwrap();
        assert_eq!(current.confirmed_actions.len(), 1);
        assert_eq!(current.todays_focus.as_deref(), Some(action.action_id.as_str()));
        assert_eq!(today(&paths).unwrap().todays_focus, current.todays_focus);
        result(&paths, &ResultRequest { action_id: action.action_id, result: ActionResult::Completed, result_text: REAL_RESULT.into(), idempotency_key: "p3-141-real-ui-focus-complete".into() }).unwrap();
        let completed = today(&paths).unwrap();
        assert!(completed.confirmed_actions.is_empty() && completed.todays_focus.is_none());
        cleanup(&paths, &sentinel);
    }

    #[test]
    fn closure_configured_runtime_root_fails_before_any_write() {
        let expected = match std::env::var("P3_141_EXPECT_PATH_ERROR") { Ok(value) => value, Err(_) => return };
        let sentinel = PathBuf::from(std::env::var("P3_141_SENTINEL_PATH").expect("closure sentinel path"));
        let before = Snapshot { db_hash: "absent".into(), counts: [0; 6] };
        let error = match paths() { Err(error) => error, Ok(_) => panic!("configured path unexpectedly accepted") };
        assert_eq!(error.code, expected);
        receipt(&format!("configured_path_{expected}"), &error, &before, &before, &sentinel);
    }
}
