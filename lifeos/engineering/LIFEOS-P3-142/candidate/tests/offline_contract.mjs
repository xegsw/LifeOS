import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const read = (file) => readFile(resolve(root, file), "utf8");
const [runtime, app, css, html, rootTool] = await Promise.all([
  read("src/runtime.rs"), read("ui/app.js"), read("ui/styles.css"), read("ui/index.html"), read("tools/task_root.mjs"),
]);
const failures = [];
const expect = (condition, name) => { if (!condition) failures.push(name); };

const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
expect(Boolean(ipcBlock), "exact_ipc_declaration_missing");
const commands = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((match) => match[1]) : [];
expect(commands.length === 20 && new Set(commands).size === 20, "exact_twenty_ipc_failed");
expect(commands.includes("save_ai_provider_settings") && commands.includes("save_ai_provider_credential"), "settings_ipc_missing");
expect(runtime.includes("deny_unknown_fields") && runtime.includes("dto_version_rejected"), "strict_dto_missing");
expect(runtime.includes("routing_authorization_required") && runtime.includes("cloud_supplement_not_authorized") && runtime.includes("automatic_failover_not_authorized"), "router_fail_closed_missing");
expect(runtime.includes("synthetic-credential-fixture-v1") && runtime.includes("credential-ref:synthetic:p3-142:v1"), "synthetic_credential_contract_missing");
expect(!/std::net|TcpStream|TcpListener|ToSocketAddrs|curl_easy|https?:\/\//.test(runtime), "network_surface_detected");
expect(!/fetch\(|XMLHttpRequest|WebSocket|https?:\/\//.test(app), "ui_network_surface_detected");
expect(!/providerRegistry[^\n]*DeepSeek|providerRegistry[^\n]*Kimi/.test(app), "provider_world_hardcoded_in_page");
expect(html.includes("app.js") && !html.includes("runtime-adapter.js"), "legacy_runtime_adapter_still_active");
expect(["Today", "Me", "Contexts", "Memory"].every((label) => app.includes(label)) && app.includes("Settings · 辅助入口"), "shell_navigation_contract_missing");
expect(app.includes("暂未开放") && app.includes("Global AI"), "settings_or_global_ai_contract_missing");
expect(css.includes(".global-ai") && css.includes("@media (max-width: 760px)") && css.includes(".rail"), "responsive_visual_contract_missing");
expect(html.includes('class="skip-link"') && css.includes(".skip-link {") && css.includes("top: -72px") && css.includes(".skip-link:focus") && css.includes("top: 12px"), "skip_link_focus_visibility_contract_missing");
expect(rootTool.includes("root_literal_rejected") && rootTool.includes("marker_payload_rejected") && rootTool.includes("symlink"), "marker_cleanup_contract_missing");

if (failures.length) {
  console.error(JSON.stringify({ status: "FAIL", failures }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: "PASS", checks: 15, ipc_count: commands.length, network: "absent", ui: "Chinese settings center" }));
