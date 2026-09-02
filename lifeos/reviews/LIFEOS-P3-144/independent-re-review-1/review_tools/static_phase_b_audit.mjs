import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const root = resolve(process.cwd());
const candidate = resolve(root, "lifeos/engineering/LIFEOS-P3-144/candidate");
const outputPath = process.argv[2] ? resolve(process.argv[2]) : null;
if (!outputPath) throw new Error("usage: node static_phase_b_audit.mjs OUTPUT_JSON");
const read = (path) => readFile(resolve(candidate, path), "utf8");
const [runtime, adapter, credential, app, build] = await Promise.all([
  read("src/runtime.rs"), read("src/deepseek.rs"), read("src/secure_credentials.rs"), read("ui/app.js"), read("build.rs"),
]);
const expectedIpc = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings", "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"];
const checks = [];
const failures = [];
const expect = (condition, id, detail = "") => { checks.push({ id, pass: Boolean(condition), detail }); if (!condition) failures.push(id); };
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const actualIpc = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((match) => match[1]) : [];
expect(JSON.stringify(actualIpc) === JSON.stringify(expectedIpc), "exact_20_ipc", `actual=${actualIpc.length}`);
expect(runtime.includes('fn run_mode() -> &\'static str {') && runtime.includes('    "synthetic"'), "phase_b_synthetic_compiled_mode");
expect(build.includes('"independent-review"') && build.includes('REVIEW_BASENAME') && build.includes('rejects dynamic review run ids'), "frozen_review_root_profile");
expect(runtime.includes('ITEM_LIMIT: i64 = 3') && runtime.includes('ITEM_CHARACTER_LIMIT: usize = 200'), "per_domain_item_boundaries");
expect(runtime.includes('DISCLOSURE_CHARACTER_BUDGET') && runtime.includes('DISCLOSURE_TOKEN_BUDGET') && runtime.includes('context_budget_rejected'), "disclosure_budget_guard");
expect(runtime.includes("authorized=1 AND status='active'") && runtime.includes('disclosure_selection_stale'), "validity_and_selection_guard");
expect(runtime.includes('previewed') && runtime.includes('confirmation_used') && runtime.includes('confirmation_stale_or_replayed'), "fresh_confirmation_guard");
expect(runtime.includes('health_medical_boundary_rejected') && runtime.includes('contains_medical_risk') && runtime.includes('durable_memory_not_allowed'), "health_nonmedical_boundary");
expect(runtime.includes("kind:'understanding'") || runtime.includes("'understanding'"), "understanding_identity_persisted");
expect(runtime.includes('"confirm" | "edit" | "reject" | "ignore" | "correct"'), "five_feedback_actions");
expect(runtime.includes('invalidate_understandings_for_source') && runtime.includes("status='invalidated'"), "correction_invalidation");
expect(credential.includes('AES-256-GCM') && credential.includes('SecKeychain') && credential.includes('delete_key_material'), "credential_separation_and_cleanup");
expect(adapter.includes('pub const AUTHORITY: &str = "https://api.deepseek.com"'), "exact_deepseek_authority");
expect(adapter.includes('.env_clear()') && adapter.includes('--proto-redir') && adapter.includes('--max-redirs') && adapter.includes('--noproxy') && adapter.includes('--proxy'), "network_redirect_proxy_guard");
expect(!/TcpStream|TcpListener|reqwest|ureq/.test(`${runtime}\n${credential}`), "no_second_network_surface");
expect(app.includes('remove-disclosure') && app.includes('confirm-disclosure') && app.includes('仅发送到') && app.includes('processingLocation'), "visible_disclosure_and_removal");
expect(!/fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|EventSource/.test(app), "no_webview_network_surface");
const report = { schema: "lifeos.p3-144.independent-review.static-audit.v1", result: failures.length ? "FAIL" : "PASS", checked_at: new Date().toISOString(), checks, failures };
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
if (failures.length) process.exitCode = 1;
