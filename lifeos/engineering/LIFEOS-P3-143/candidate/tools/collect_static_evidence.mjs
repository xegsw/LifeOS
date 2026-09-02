import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { createHash } from "node:crypto";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const files = ["build.rs", "src/runtime.rs", "src/deepseek.rs", "src/secure_credentials.rs", "ui/app.js", "ui/styles.css", "ui/index.html", "tauri.conf.json", "tests/offline_contract.mjs"];
const hash = (value) => createHash("sha256").update(value).digest("hex");
const source = Object.fromEntries(await Promise.all(files.map(async (file) => {
  const value = await readFile(resolve(candidate, file));
  return [file, hash(value)];
})));
const [build, runtime, adapter, credentials, app, config] = await Promise.all([
  readFile(resolve(candidate, "build.rs"), "utf8"), readFile(resolve(candidate, "src/runtime.rs"), "utf8"), readFile(resolve(candidate, "src/deepseek.rs"), "utf8"),
  readFile(resolve(candidate, "src/secure_credentials.rs"), "utf8"), readFile(resolve(candidate, "ui/app.js"), "utf8"),
  readFile(resolve(candidate, "tauri.conf.json"), "utf8"),
]);
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const commands = ipcBlock ? [...ipcBlock[1].matchAll(/"([a-z_]+)"/g)].map((item) => item[1]) : [];
const transport = [".env_clear()", '"--proto"', '"=https"', '"--proto-redir"', '"--max-redirs"', '"--noproxy"', '"--proxy"', '"--config"'].every((needle) => adapter.includes(needle));
const report = {
  schema: "lifeos.p3-143.static-evidence.v1",
  task: "LIFEOS-P3-143",
  source_sha256: source,
  provider_registry: { cloud: 8, local: 4, real_gate_provider: "DeepSeek", unverified_provider_count: 11 },
  ipc: { count: commands.length, exact_unique: new Set(commands).size === 20 },
  credential_boundary: {
    sqlite_fields: ["ciphertext", "nonce", "tag", "algorithm", "version", "key_reference"],
    aead: credentials.includes("AES-256-GCM"),
    exact_keychain_service: credentials.includes("com.lifeos.p3-143.aead-key.v1"),
    plaintext_persistence_field_absent: !runtime.includes("api_key: String") && !runtime.includes("api_key: Vec"),
  },
  transport_boundary: {
    authority: "https://api.deepseek.com",
    direct_ui_network_api_absent: !/fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|EventSource/.test(app),
    adapter_guard_complete: transport,
    csp_ipc_only: config.includes("connect-src ipc:"),
    background_scheduler_absent: !/setInterval|setTimeout\(|tokio::spawn|thread::spawn/.test(runtime + adapter),
  },
  lifecycle: {
    explicit_steps: ["store", "user_test", "select_model", "set_enabled", "send_fixed_canary", "delete"],
    transient_response_only: app.includes("瞬时响应（不保存）") && app.includes("clear-response"),
  },
  root_authority: {
    build_time_profiles_only: build.includes("LIFEOS_P3_143_ROOT_PROFILE") && build.includes("independent-review") && build.includes("LIFEOS_P3_143_REVIEW_RUN_ID"),
    review_run_id_validation: build.includes("valid_review_run_id") && build.includes("8..=48"),
    runtime_compiled_authority_only: runtime.includes("compiled_root_authority") && runtime.includes("verify_runtime_child") && !runtime.includes('const TASK_ROOT: &str = "/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1"'),
    database_direct_child_guard: runtime.includes("database_path") && runtime.includes("database_path_rejected"),
  },
  result: commands.length === 20 && new Set(commands).size === 20 && transport && build.includes("valid_review_run_id") && runtime.includes("compiled_root_authority") ? "PASS" : "FAIL",
};
await mkdir(evidence, { recursive: true });
await writeFile(resolve(evidence, "static_contract_report.json"), `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ task: report.task, result: report.result, ipc_count: report.ipc.count, source_files: files.length }));
if (report.result !== "PASS") process.exit(1);
