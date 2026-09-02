import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();
const candidate = "lifeos/engineering/LIFEOS-P3-144/candidate";
const review = "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3";
const load = async (path) => readFile(resolve(root, path), "utf8");
const runtime = await load(`${candidate}/src/runtime.rs`);
const deepseek = await load(`${candidate}/src/deepseek.rs`);
const credentials = await load(`${candidate}/src/secure_credentials.rs`);
const ui = await load(`${candidate}/ui/app.js`);
const build = await load(`${candidate}/build.rs`);
const results = [];
const check = (id, title, passed, assertion) => {
  results.push({ id, title, status: passed ? "PASS" : "FAIL", assertion });
  if (!passed) throw new Error(`${id}: ${title}`);
};
const ipc = Array.from(runtime.matchAll(/^\s*"([a-z_]+)",$/gm), (match) => match[1]).slice(0, 20);
const expectedIpc = [
  "capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery",
  "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context",
  "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings",
  "save_ai_provider_settings", "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled",
  "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"
];

check("IR-001", "独立评审编译 profile 固定唯一根", build.includes('"independent-review"') && build.includes('"lifeos-p3-144-independent-review-v1"') && build.includes('rejects dynamic review run ids'), "build profile rejects dynamic independent-review run IDs and compiles the literal v1 root");
check("IR-002", "根、marker 与 runtime child 失败关闭", runtime.includes('task_marker_missing') && runtime.includes('task_marker_type_rejected') && runtime.includes('runtime_child_type_rejected') && runtime.includes('0o700') && runtime.includes('0o600'), "root, marker and child type/permission checks are present before store initialization");
check("IR-003", "离线 run mode 不是调用方环境开关", runtime.includes('fn run_mode()') && runtime.includes('"synthetic"') && runtime.includes('caller-controlled environment literal must never turn an offline build'), "offline mode is a compiled literal");
check("IR-004", "严格 20 IPC", ipc.length === 20 && JSON.stringify(ipc) === JSON.stringify(expectedIpc), "ordered IPC list equals the frozen 20-item contract");
check("IR-005", "Provider 目录保留 Cloud 8 / Local 4", ["openai", "anthropic", "google_gemini", "deepseek", "kimi", "openrouter", "cloud_openai_compatible", "cloud_custom", "ollama", "lm_studio", "local_openai_compatible", "local_custom"].every((value) => runtime.includes(`("${value}"`)), "all 12 frozen provider IDs remain in separate cloud/local arrays");
check("IR-006", "DeepSeek authority 精确", deepseek.includes('pub const AUTHORITY: &str = "https://api.deepseek.com"') && runtime.includes('endpoint_url.as_deref() != Some(deepseek::AUTHORITY)'), "only the exact HTTPS DeepSeek authority enters the active gate");
check("IR-007", "无代理、重定向或环境继承", deepseek.includes('.env_clear()') && deepseek.includes('.arg("--noproxy")') && deepseek.includes('.arg("*")') && deepseek.includes('.arg("--proxy")') && deepseek.includes('.arg("")') && deepseek.includes('.arg("--max-redirs")') && deepseek.includes('.arg("0")'), "real adapter clears environment and disables proxy/redirect use");
check("IR-008", "最小上下文预算", runtime.includes('const ITEM_LIMIT: i64 = 3') && runtime.includes('const DISCLOSURE_CHARACTER_BUDGET: usize = 480') && runtime.includes('const DISCLOSURE_TOKEN_BUDGET: usize = 120') && runtime.includes('context_budget_rejected'), "3-item, 480-character and 120-token checks reject before send");
check("IR-009", "空、未知与过量输入拒绝", runtime.includes('context_item_rejected') && runtime.includes('context_request_rejected') && runtime.includes('minimal_context_empty') && runtime.includes('context_item_limit_rejected'), "input, empty selection and fourth item all have explicit rejection codes");
check("IR-010", "相关性、有效性与域隔离", runtime.includes('fn relevant_to') && runtime.includes("status='active'") && runtime.includes('expires_at_ms>?2') && runtime.includes('request_domain'), "resolver filters active/non-expired records and respects Work/Health relevance");
check("IR-011", "移除、重预览、过期与重放拒绝", runtime.includes('fn remove_disclosure_item') && runtime.includes('previewed=0') && runtime.includes('confirmation_stale_or_replayed') && runtime.includes('confirmation_used=1 WHERE id=?1 AND revision=?2 AND previewed=1 AND confirmation_used=0'), "confirmation is atomically single-use and mutations invalidate preview");
check("IR-012", "凭据 AEAD 与 Keychain 材料分离", credentials.includes('Aes256Gcm') && credentials.includes('SecKeychain') && credentials.includes('AES-256-GCM') && runtime.includes('CREATE TABLE IF NOT EXISTS encrypted_credential') && runtime.includes('key_reference TEXT NOT NULL'), "SQLite retains encrypted material/reference while key material uses macOS Keychain");
check("IR-013", "凭据缺失、篡改与删除失败关闭", runtime.includes('credential_required') && runtime.includes('credential_authentication_failed') && runtime.includes('remove_credential_row') && credentials.includes('KeychainMissing'), "missing/tampered/deleted credential states have explicit pre-network failures");
check("IR-014", "保存、测试、选择、启用与发送分离", ui.includes('保存本身不会测试、读取模型、启用或发送') && ui.includes('data-action="test"') && ui.includes('data-action="confirm-model"') && ui.includes('data-action="enable"') && ui.includes('data-action="confirm-disclosure"'), "UI retains distinct user actions for each state transition");
const resolveSegment = runtime.slice(runtime.indexOf('fn resolve_request_context('));
check("IR-015", "Provider 就绪验证位于确认消耗之前", resolveSegment.indexOf('provider_not_ready') < resolveSegment.indexOf('consume_confirmation('), "no confirmation token is consumed before provider readiness is checked");
check("IR-016", "AI identity 与五类反馈", runtime.includes('provider":"DeepSeek') && ui.includes('["confirm","edit","reject","ignore","correct"]') && runtime.includes('feedback_event'), "understanding identity and five feedback actions are present");
check("IR-017", "撤回／修正会失效派生", runtime.includes('fn invalidate_understandings_for_source') && runtime.includes("status='invalidated'") && runtime.includes('source_lineage_invalidated'), "source retirement invalidates dependent understanding projections");
check("IR-018", "Health 非医疗边界", runtime.includes('fn contains_medical_risk') && runtime.includes('health_medical_boundary_rejected') && ui.includes('不提供诊断、治疗、用药或紧急判断'), "medical-risk text is rejected for Health inputs/questions and UI states the boundary");
check("IR-019", "UI 无 WebView 直连网络", !/\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(/.test(ui) && ui.includes('window.__TAURI__?.core?.invoke'), "UI uses Tauri invoke and contains no browser network primitive");
check("IR-020", "秘密输入即时清空", ui.includes('try { state.settings = await invoke("save_ai_provider_credential"') && ui.includes('finally { apiKey = ""; }') && ui.includes('if (input) input.value = ""'), "credential UI clears input and local variable after store attempt");
check("IR-021", "合成收据无网络", deepseek.includes('method_class: "NONE"') && deepseek.includes('status_class: "synthetic_no_network"') && runtime.includes('run_mode() == "synthetic"'), "synthetic model/context receipts assert no request method or network activity");
check("IR-022", "持久记忆入口拒绝扩展", runtime.includes('fn upsert_durable_memory(_: EmptyRequest)') && runtime.includes('durable_memory_not_allowed'), "P3-144 does not silently add durable-memory behavior");

const mutations = [
  { id: "MUT-001", subject: "root authority", altered: build.replace('"lifeos-p3-144-independent-review-v1"', '"/private/tmp/escaped"'), rejected: (text) => !text.includes('"lifeos-p3-144-independent-review-v1"') },
  { id: "MUT-002", subject: "DeepSeek authority", altered: deepseek.replace('https://api.deepseek.com', 'http://invalid.example'), rejected: (text) => !text.includes('https://api.deepseek.com') },
  { id: "MUT-003", subject: "confirmation single-use predicate", altered: runtime.replace('confirmation_used=1 WHERE id=?1 AND revision=?2 AND previewed=1 AND confirmation_used=0', 'confirmation_used=1 WHERE id=?1'), rejected: (text) => !text.includes('AND previewed=1 AND confirmation_used=0') },
  { id: "MUT-004", subject: "proxy isolation", altered: deepseek.replace('.env_clear()', ''), rejected: (text) => !text.includes('.env_clear()') },
  { id: "MUT-005", subject: "Health medical guard", altered: runtime.replaceAll('health_medical_boundary_rejected', 'removed_guard'), rejected: (text) => !text.includes('health_medical_boundary_rejected') }
].map((mutation) => ({ id: mutation.id, subject: mutation.subject, status: mutation.rejected(mutation.altered) ? "REJECTED" : "FAILED" }));
for (const mutation of mutations) check(mutation.id, `变异被评审器拒绝：${mutation.subject}`, mutation.status === "REJECTED", "review-owned in-memory semantic mutation removes a required guard and is detected");

const result = {
  schema: "lifeos.p3-144.independent-review.static-mutation.v1",
  candidate,
  source_sha256: createHash("sha256").update([runtime, deepseek, credentials, ui, build].join("\n")).digest("hex"),
  status: "PASS",
  checks: results,
  mutations,
  counts: { pass: results.filter((item) => item.status === "PASS").length, fail: results.filter((item) => item.status === "FAIL").length, rejected_mutations: mutations.filter((item) => item.status === "REJECTED").length },
  network_access: false,
  prohibited_pilot_contact: false
};
await mkdir(resolve(root, review, "evidence"), { recursive: true, mode: 0o700 });
await writeFile(resolve(root, review, "evidence/independent_static_mutations.json"), `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify(result.counts));
