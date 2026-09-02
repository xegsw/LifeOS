import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { createHash } from "node:crypto";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const files = ["build.rs", "src/runtime.rs", "src/deepseek.rs", "src/secure_credentials.rs", "ui/app.js", "ui/styles.css", "ui/index.html", "tauri.conf.json", "tests/offline_contract.mjs"];
const hash = (value) => createHash("sha256").update(value).digest("hex");
const source = Object.fromEntries(await Promise.all(files.map(async (file) => [file, hash(await readFile(resolve(candidate, file)))])));
const [build, runtime, adapter, credentials, app, config] = await Promise.all([
  readFile(resolve(candidate, "build.rs"), "utf8"), readFile(resolve(candidate, "src/runtime.rs"), "utf8"), readFile(resolve(candidate, "src/deepseek.rs"), "utf8"),
  readFile(resolve(candidate, "src/secure_credentials.rs"), "utf8"), readFile(resolve(candidate, "ui/app.js"), "utf8"), readFile(resolve(candidate, "tauri.conf.json"), "utf8"),
]);
const expectedIpc = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings", "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"];
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const commands = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((item) => item[1]) : [];
const exactIpc = commands.length === expectedIpc.length && commands.every((name, index) => name === expectedIpc[index]);
const phaseAHardPinned = runtime.includes("fn run_mode() -> &'static str {") && runtime.includes('    "synthetic"') && runtime.includes('if run_mode() == "real_gate"');
const report = {
  schema: "lifeos.p3-144.static-evidence.v1",
  task: "LIFEOS-P3-144",
  source_sha256: source,
  provider_registry: { cloud: 8, local: 4, permitted_future_real_gate_provider: "DeepSeek" },
  ipc: { expected: expectedIpc, observed: commands, exact: exactIpc },
  phase_a: {
    hard_pinned_synthetic_mode: phaseAHardPinned,
    no_renderer_network_api: !/fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|EventSource/.test(app),
    no_background_scheduler: !/setInterval|setTimeout\(|tokio::spawn|thread::spawn/.test(runtime + adapter),
    deepseek_authority_declared: adapter.includes('pub const AUTHORITY: &str = "https://api.deepseek.com"'),
  },
  minimal_context: {
    one_domain_only: runtime.includes("matches!(request.domain.as_str(), WORK | HEALTH)") && runtime.includes("request_domain"),
    item_limit: runtime.includes("const ITEM_LIMIT: i64 = 3"),
    character_and_token_budgets: runtime.includes("DISCLOSURE_CHARACTER_BUDGET") && runtime.includes("DISCLOSURE_TOKEN_BUDGET"),
    active_authorized_filter: runtime.includes("authorized=1 AND status='active'"),
    disclosure_preview_then_one_time_confirmation: runtime.includes("previewed=1") && runtime.includes("confirmation_used=1") && runtime.includes("confirmation_stale_or_replayed"),
    preview_displays_provider_model_location_and_budget: runtime.includes('"model": model') && app.includes("模型：") && app.includes("预算：") && app.includes("processingLocation"),
    removal_invalidates_confirmation: runtime.includes("revision=revision+1") && runtime.includes("previewed=0"),
    health_non_medical_boundary: runtime.includes("contains_medical_risk") && runtime.includes("health_medical_boundary_rejected"),
    durable_memory_refusal: runtime.includes("durable_memory_not_allowed"),
    audit_and_derivation_records: runtime.includes("CREATE TABLE IF NOT EXISTS audit_event") && runtime.includes("CREATE TABLE IF NOT EXISTS derivation"),
  },
  credential_boundary: {
    aead: credentials.includes("AES-256-GCM"),
    exact_keychain_service: credentials.includes("com.lifeos.p3-144.aead-key.v1"),
    plaintext_persistence_field_absent: !runtime.includes("api_key: String") && !runtime.includes("api_key: Vec"),
  },
  root_authority: {
    engineering_profile_only: build.includes("LIFEOS_P3_144_ROOT_PROFILE") && build.includes("engineering") && build.includes("independent-review"),
    no_real_root_profile: !build.includes("real-ai-secure-activation"),
    compiled_runtime_guard: runtime.includes("compiled_root_authority") && runtime.includes("verify_runtime_child") && runtime.includes("task_marker_missing"),
    exact_engineering_root: runtime.includes("lifeos-p3-144-engineering-v1"),
  },
};
const required = [exactIpc, phaseAHardPinned, report.phase_a.no_renderer_network_api, report.phase_a.no_background_scheduler, report.minimal_context.one_domain_only, report.minimal_context.item_limit, report.minimal_context.character_and_token_budgets, report.minimal_context.active_authorized_filter, report.minimal_context.disclosure_preview_then_one_time_confirmation, report.minimal_context.preview_displays_provider_model_location_and_budget, report.minimal_context.removal_invalidates_confirmation, report.minimal_context.health_non_medical_boundary, report.minimal_context.durable_memory_refusal, report.credential_boundary.aead, report.credential_boundary.exact_keychain_service, report.root_authority.engineering_profile_only, report.root_authority.no_real_root_profile, report.root_authority.compiled_runtime_guard, report.root_authority.exact_engineering_root];
report.result = required.every(Boolean) ? "PASS" : "FAIL";
await mkdir(evidence, { recursive: true });
await writeFile(resolve(evidence, "static_contract_report.json"), `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ task: report.task, result: report.result, ipc_count: commands.length, source_files: files.length }));
if (report.result !== "PASS") process.exit(1);
