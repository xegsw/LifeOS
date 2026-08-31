import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const source = await readFile(new URL("../ui/runtime-adapter.js", import.meta.url), "utf8");
const listeners = new Map();
const fields = new Map([
  ["provider-mode", { value: "cloud" }],
  ["provider-profile", { value: "openai" }],
  ["provider-base-url", { value: "https://fixture.lifeos.test:443/v1" }],
  ["provider-model", { value: "" }],
  ["provider-temperature", { value: "0.70" }],
  ["provider-max-tokens", { value: "2048" }],
  ["provider-timeout", { value: "60" }],
]);
const root = {
  dataset: {},
  innerHTML: "",
  querySelector() { return null; },
  insertAdjacentHTML(_position, markup) { this.innerHTML = `${markup}${this.innerHTML}`; },
};
const document = {
  documentElement: { dataset: {} },
  addEventListener(type, listener) { listeners.set(type, listener); },
  querySelector(selector) {
    if (selector === "#main-content") return root;
    const field = selector.match(/^\[name='([^']+)'\]/)?.[1];
    return field ? fields.get(field) || null : null;
  },
  querySelectorAll() { return []; },
};
const settings = (mode, profile, credentialPresent) => ({
  status: "ready",
  settings: { mode, profile, base_url: mode === "cloud" ? "https://fixture.lifeos.test:443/v1" : "http://127.0.0.1:11434", model: "", temperature_bps: 70, max_output_tokens: 2048, timeout_ms: 60_000 },
  enabled: false,
  connection_state: "not_tested",
  last_tested_at_ms: null,
  last_latency_ms: null,
  model_request_count: 0,
  discovered_models: [],
  credential: { present: credentialPresent, masked: credentialPresent ? "••••9X4" : null },
});
let active = settings("local", "ollama", false);
const cloud = settings("cloud", "openai", true);
let credentialCalls = 0;
const invoke = async (command, { request = {} }) => {
  if (command === "runtime_status") return { input_mode: "synthetic" };
  if (command === "get_today") return { records: [], confirmed_actions: [] };
  if (command === "get_context_recovery") return {};
  if (command === "assemble_global_ai_context") return { disclosure_required: false, included: [], additional_personal_count: 0 };
  if (command === "get_ai_provider_settings") return request.mode === "cloud" ? cloud : active;
  if (command === "save_ai_provider_settings") {
    active = settings(request.settings.mode, request.settings.profile, request.settings.mode === "cloud");
    return active;
  }
  if (command === "save_ai_provider_credential") {
    credentialCalls += 1;
    if (request.operation === "delete") active.credential = { present: false, masked: null };
    return active;
  }
  throw new Error(`unexpected invoke: ${command}`);
};
const ui = { state: { page: "settings", todayMode: "empty" }, render() {} };
const sandbox = { window: { __P3_116_RUNTIME__: ui, __TAURI__: { core: { invoke } } }, document, Promise, Date, console, queueMicrotask, setTimeout };
vm.runInNewContext(source, sandbox, { filename: "runtime-adapter.js" });
const settle = async () => { await Promise.resolve(); await Promise.resolve(); await new Promise((resolve) => setTimeout(resolve, 0)); };
const eventFor = (action) => ({ preventDefault() {}, stopImmediatePropagation() {}, target: { dataset: { action }, closest() { return this; } } });

await settle();
listeners.get("change")({ target: { name: "provider-mode", value: "cloud" } });
await settle();
assert.match(root.innerHTML, /data-pending-mode="save-required"/);
assert.match(root.innerHTML, /先保存 Cloud 配置后管理 API Key/);
assert.doesNotMatch(root.innerHTML, /data-action="provider:clear-credential"/);
listeners.get("click")(eventFor("provider:clear-credential"));
await settle();
assert.equal(credentialCalls, 0, "a programmatic stale delete is rejected before the credential IPC");

listeners.get("click")(eventFor("provider:save"));
await settle();
assert.match(root.innerHTML, /data-action="provider:clear-credential"/);
listeners.get("click")(eventFor("provider:clear-credential"));
await settle();
assert.equal(credentialCalls, 1, "the persisted Cloud mode can delete its own saved credential");
assert.doesNotMatch(root.innerHTML, /data-action="provider:clear-credential"/);
console.log("mode-delete-ui-contract: PASS");
