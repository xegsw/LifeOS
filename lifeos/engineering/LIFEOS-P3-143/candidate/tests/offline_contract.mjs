import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const read = (file) => readFile(resolve(root, file), "utf8");
const [runtime, adapter, credentials, app, css, html, rootTool, config] = await Promise.all([
  read("src/runtime.rs"), read("src/deepseek.rs"), read("src/secure_credentials.rs"), read("ui/app.js"),
  read("ui/styles.css"), read("ui/index.html"), read("tools/task_root.mjs"), read("tauri.conf.json"),
]);
const failures = [];
const expect = (condition, name) => { if (!condition) failures.push(name); };
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const commands = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((match) => match[1]) : [];

expect(Boolean(ipcBlock) && commands.length === 20 && new Set(commands).size === 20, "exact_twenty_ipc_failed");
expect(["save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "assemble_global_ai_context"].every((name) => commands.includes(name)), "credential_lifecycle_ipc_missing");
expect(runtime.includes("deny_unknown_fields") && runtime.includes("dto_version_rejected"), "strict_dto_missing");
expect(adapter.includes("https://api.deepseek.com") && runtime.includes("deepseek_configuration_required"), "exact_deepseek_configuration_missing");
expect(runtime.includes("credential_missing") && runtime.includes("selected_model") && runtime.includes("available_models"), "stepwise_state_machine_missing");
expect(runtime.includes("apply_tested_model_directory") && runtime.includes("value.selected_model = None") && runtime.includes("value.enabled = false"), "test_must_clear_selection_and_enablement");
expect(credentials.includes("AES-256-GCM") && credentials.includes("KEYCHAIN_SERVICE") && credentials.includes("delete_key_material"), "credential_port_missing");
expect(!/std::net|TcpStream|TcpListener|ToSocketAddrs|reqwest|ureq/.test(runtime + credentials), "unapproved_network_surface_detected");
expect(adapter.includes('pub const AUTHORITY: &str = "https://api.deepseek.com"') && adapter.includes(".env_clear()") && adapter.includes('"--proto"') && adapter.includes('"=https"') && adapter.includes('"--max-redirs"') && adapter.includes('"0"') && adapter.includes('"--noproxy"') && adapter.includes('"*"') && adapter.includes('"--proxy"'), "single_authority_transport_guard_missing");
expect(!/fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|EventSource/.test(app), "ui_network_surface_detected");
expect(app.includes('data-secret-field="apiKey"') && app.includes("input.value = \"\"") && app.includes("operation: \"store\""), "bounded_secret_input_contract_missing");
expect(app.includes("operation: \"select_model\"") && app.includes("operation: \"set_enabled\"") && app.includes("send_fixed_canary"), "explicit_lifecycle_controls_missing");
expect(app.includes('data-action="confirm-model"') && app.includes("state.pendingModel = node.value") && !app.includes('action("select-model", node.value)'), "model_selection_requires_explicit_confirmation");
expect(app.includes("瞬时响应（不保存）") && app.includes("clear-response"), "transient_response_cleanup_missing");
expect(html.includes("app.js") && !html.includes("runtime-adapter.js"), "legacy_runtime_adapter_still_active");
expect(["Today", "Me", "Contexts", "Memory"].every((label) => app.includes(label)) && app.includes("Settings · 辅助入口"), "shell_navigation_contract_missing");
expect(css.includes(".global-ai") && css.includes("@media (max-width: 760px)") && css.includes(".rail") && css.includes(".credential-area"), "responsive_visual_contract_missing");
expect(config.includes("local.lifeos.p3-143") && config.includes("connect-src ipc:"), "tauri_identity_or_csp_missing");
expect(rootTool.includes("root_literal_rejected") && rootTool.includes("marker_payload_rejected") && rootTool.includes("symlink"), "marker_cleanup_contract_missing");

if (failures.length) {
  console.error(JSON.stringify({ status: "FAIL", failures }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: "PASS", checks: 18, ipc_count: commands.length, network: "adapter_only_user_gate", ui: "Chinese settings center" }));
