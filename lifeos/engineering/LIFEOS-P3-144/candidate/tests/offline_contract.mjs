import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const read = (file) => readFile(resolve(root, file), "utf8");
const [runtime, adapter, credentials, app, css, html, rootTool, config, build] = await Promise.all([
  read("src/runtime.rs"), read("src/deepseek.rs"), read("src/secure_credentials.rs"), read("ui/app.js"),
  read("ui/styles.css"), read("ui/index.html"), read("tools/task_root.mjs"), read("tauri.conf.json"), read("build.rs"),
]);
const failures = [];
const expect = (condition, name) => { if (!condition) failures.push(name); };
const expected = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings", "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"];
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const commands = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((match) => match[1]) : [];

expect(commands.length === 20 && commands.every((name, index) => name === expected[index]), "exact_twenty_ipc_failed");
expect(runtime.includes("deny_unknown_fields") && runtime.includes("dto_version_rejected"), "strict_dto_missing");
expect(adapter.includes('pub const AUTHORITY: &str = "https://api.deepseek.com"'), "exact_deepseek_authority_missing");
expect(runtime.includes("fn run_mode() -> &'static str {") && runtime.includes('    "synthetic"'), "phase_a_not_hard_pinned_synthetic");
expect(runtime.includes("const ITEM_LIMIT: i64 = 3") && runtime.includes("DISCLOSURE_CHARACTER_BUDGET") && runtime.includes("DISCLOSURE_TOKEN_BUDGET"), "minimal_context_budget_missing");
expect(runtime.includes("authorized=1 AND status='active'") && runtime.includes("disclosure_selection_stale"), "invalid_context_exclusion_missing");
expect(runtime.includes("previewed=1") && runtime.includes("confirmation_used=1") && runtime.includes("confirmation_stale_or_replayed"), "preview_confirmation_contract_missing");
expect(runtime.includes('"model": model') && app.includes("模型：") && app.includes("预算：") && app.includes("processingLocation"), "preview_disclosure_fields_missing");
expect(runtime.includes("revision=revision+1") && runtime.includes("previewed=0"), "removal_invalidation_missing");
expect(runtime.includes("contains_medical_risk") && runtime.includes("health_medical_boundary_rejected") && runtime.includes("durable_memory_not_allowed"), "health_or_memory_boundary_missing");
expect(credentials.includes("AES-256-GCM") && credentials.includes("KEYCHAIN_SERVICE") && credentials.includes("delete_key_material"), "credential_port_missing");
expect(!/std::net|TcpStream|TcpListener|ToSocketAddrs|reqwest|ureq/.test(runtime + credentials), "unapproved_network_surface_detected");
expect(!/fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|EventSource/.test(app), "ui_network_surface_detected");
expect(app.includes("save-work") && app.includes("save-health") && app.includes('data-action="assemble"') && app.includes("confirm-disclosure") && app.includes('data-action="feedback:'), "work_health_ui_actions_missing");
expect(app.includes("DeepSeek") && app.includes("仅发送到"), "disclosure_provider_copy_missing");
expect(["Today", "Me", "Contexts", "Memory"].every((label) => app.includes(label)) && app.includes("Settings · 辅助入口"), "shell_navigation_contract_missing");
expect(css.includes(".global-ai") && css.includes("@media (max-width: 760px)") && css.includes(".rail") && css.includes(".context-page section"), "responsive_visual_contract_missing");
expect(html.includes("app.js") && !html.includes("runtime-adapter.js"), "legacy_runtime_adapter_still_active");
expect(config.includes("local.lifeos.p3-144") && config.includes("connect-src ipc:"), "tauri_identity_or_csp_missing");
expect(rootTool.includes("lifeos-p3-144-engineering-v1") && rootTool.includes("marker_payload_rejected") && rootTool.includes("symlink"), "marker_cleanup_contract_missing");
expect(build.includes("LIFEOS_P3_144_ROOT_PROFILE") && build.includes("engineering") && build.includes("independent-review") && build.includes("REVIEW_BASENAME") && build.includes("REVIEW_RUN_ID") && build.includes("rejects dynamic review run ids") && !build.includes("real-ai-secure-activation"), "build_time_root_profile_missing");
expect(runtime.includes("compiled_root_authority") && runtime.includes("verify_runtime_child") && runtime.includes("database_path") && runtime.includes("created_root") && runtime.includes("task_marker_missing"), "compiled_root_authority_runtime_guard_missing");

if (failures.length) {
  console.error(JSON.stringify({ status: "FAIL", failures }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: "PASS", checks: 21, ipc_count: commands.length, run_mode: "synthetic", ui: "Chinese Work Health disclosure center" }));
