import fs from "node:fs";
import path from "node:path";

const candidate = path.resolve(process.argv[2]);
const receiptPath = path.resolve(process.argv[3]);
const reviewRoot = "/private/tmp/lifeos-p3-144-independent-review-v1";
const markerName = ".lifeos-p3-144-independent-review-owner.json";
const marker = {
  schema: "lifeos.p3-144.closure-4-review-owned-root.v1",
  task: "LIFEOS-P3-144",
  owner: "closure-4-independent-review",
};

const read = (relative) => fs.readFileSync(path.join(candidate, relative), "utf8");
const source = {
  deepseek: read("src/deepseek.rs"),
  runtime: read("src/runtime.rs"),
  ui: read("ui/app.js"),
  receipt: JSON.parse(fs.readFileSync(receiptPath, "utf8")),
};

const expectedIpc = [
  "capture_record", "get_today", "runtime_status", "confirm_capture_context",
  "get_context_recovery", "get_context_next_action", "decide_context_next_action",
  "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding",
  "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings",
  "save_ai_provider_credential", "test_ai_provider_connection", "set_ai_provider_enabled",
  "upsert_durable_memory", "update_current_state", "resolve_request_context",
  "get_context_disclosure_receipt",
];

function scalarPaths(value, prefix = [], output = []) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scalarPaths(item, [...prefix, String(index)], output));
  } else if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, item]) => scalarPaths(item, [...prefix, key], output));
  } else {
    output.push(prefix.join("."));
  }
  return output;
}

function registeredIpc(runtime) {
  const block = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\n\];/);
  return block ? [...block[1].matchAll(/"([a-z0-9_]+)"/g)].map((entry) => entry[1]) : [];
}

function evaluate(input) {
  const checks = [];
  const check = (id, pass) => checks.push({ id, status: pass ? "PASS" : "FAIL" });

  check("IR-C4-TIMEOUT-01", input.deepseek.includes("process_exit == Some(28)") && input.deepseek.includes("return AdapterFailure::Timeout"));
  check("IR-C4-TIMEOUT-02", input.deepseek.includes('.arg("--max-time")\n        .arg("60")') && !input.deepseek.includes("--retry"));
  check("IR-C4-DB-01", input.runtime.includes('const DB: &str = "capture.sqlite";') && !input.runtime.includes('const DB: &str = "secure-provider-settings.sqlite";'));
  check("IR-C4-DB-02", input.runtime.includes("Ok(meta) if meta.file_type().is_file() => Ok(path)") && input.runtime.includes('"数据库路径必须是普通文件。"'));
  check("IR-C4-DB-03", input.runtime.includes("fs::set_permissions(&path, fs::Permissions::from_mode(0o600))"));
  check("IR-C4-FEEDBACK-01", input.runtime.includes('if current_status == "pending" {') && input.runtime.includes('"confirm" => Some("confirmed")') && input.runtime.includes('operation == "correct"'));
  check("IR-C4-FEEDBACK-02", input.runtime.includes("UPDATE derivation SET status=?1 WHERE id=?2 AND status=?3") && input.runtime.includes("understanding_feedback_consumed"));
  check("IR-C4-UI-01", input.ui.includes('invoke("get_evidence_backed_understanding"') && input.ui.includes("lifecycleStatus: latest.status"));
  check("IR-C4-UI-02", input.ui.includes('state.understanding = { ...result, lifecycleStatus: "pending" };') && input.ui.match(/catch \(error\) \{\s*state\.disclosure = null;\s*throw error;/));
  check("IR-C4-UI-03", input.ui.includes('const feedback = lifecycle === "pending"') && input.ui.includes('role="status"'));
  check("IR-C4-IPC-01", JSON.stringify(registeredIpc(input.runtime)) === JSON.stringify(expectedIpc));

  const receiptTop = Object.keys(input.receipt).sort();
  const allowedTop = ["authority", "background_request_count", "closure_network_request_count", "confirmed_minimal_context_request_count", "contains_real_text", "contains_real_text_hash", "contains_secret", "date", "lifecycle", "limits", "notes", "observed_noncontent_operations", "other_provider_request_count", "prohibited_actions", "provider", "schema", "task_id", "user_operated", "user_reported_complete"].sort();
  const forbiddenPath = scalarPaths(input.receipt).some((item) => /(^|\.)(text|body|content|content_hash|hash|api_key|secret|response)(\.|$)/i.test(item));
  check("IR-C4-RECEIPT-01", JSON.stringify(receiptTop) === JSON.stringify(allowedTop) && !forbiddenPath);
  check("IR-C4-RECEIPT-02", input.receipt.provider === "DeepSeek" && input.receipt.authority === "https://api.deepseek.com" && input.receipt.other_provider_request_count === 0 && input.receipt.background_request_count === 0 && input.receipt.closure_network_request_count === 0 && input.receipt.contains_real_text === false && input.receipt.contains_real_text_hash === false && input.receipt.contains_secret === false);
  check("IR-C4-RECEIPT-03", input.receipt.lifecycle?.database_basename === "capture.sqlite" && input.receipt.lifecycle?.database_mode === "0600" && input.receipt.lifecycle?.pilot_retained === true && input.receipt.lifecycle?.database_retained === true && input.receipt.lifecycle?.credential_retained === true);
  check("IR-C4-RECEIPT-04", Number.isInteger(input.receipt.limits?.active_work_items) && input.receipt.limits.active_work_items >= 0 && input.receipt.limits.active_work_items <= 3 && Number.isInteger(input.receipt.limits?.active_health_items) && input.receipt.limits.active_health_items >= 0 && input.receipt.limits.active_health_items <= 3 && input.receipt.limits.per_item_character_limit === 200);
  return checks;
}

function clone(value) {
  return { ...value, receipt: JSON.parse(JSON.stringify(value.receipt)) };
}

function exactMarkerValid(root) {
  const target = path.join(root, markerName);
  const rootStat = fs.lstatSync(root);
  const markerStat = fs.lstatSync(target);
  if (!rootStat.isDirectory() || rootStat.isSymbolicLink() || (rootStat.mode & 0o777) !== 0o700) return false;
  if (!markerStat.isFile() || markerStat.isSymbolicLink() || (markerStat.mode & 0o777) !== 0o600) return false;
  return JSON.stringify(JSON.parse(fs.readFileSync(target, "utf8"))) === JSON.stringify(marker);
}

function guardedCleanup(root) {
  if (!exactMarkerValid(root)) return false;
  fs.rmSync(root, { recursive: true });
  return true;
}

if (fs.existsSync(reviewRoot)) throw new Error("review_root_not_absent_before_review_owned_mutations");
fs.mkdirSync(reviewRoot, { mode: 0o700 });
fs.writeFileSync(path.join(reviewRoot, markerName), `${JSON.stringify(marker)}\n`, { mode: 0o600, flag: "wx" });
const baseChecks = evaluate(source);

const mutations = [
  ["timeout_as_network", (v) => { v.deepseek = v.deepseek.replace("return AdapterFailure::Timeout;", "return AdapterFailure::Network;"); }],
  ["timeout_30_seconds", (v) => { v.deepseek = v.deepseek.replace('.arg("60")', '.arg("30")'); }],
  ["wrong_database_basename", (v) => { v.runtime = v.runtime.replace('const DB: &str = "capture.sqlite";', 'const DB: &str = "other.sqlite";'); }],
  ["accept_non_regular_database", (v) => { v.runtime = v.runtime.replace("Ok(meta) if meta.file_type().is_file() => Ok(path)", "Ok(meta) => Ok(path)"); }],
  ["database_mode_0644", (v) => { v.runtime = v.runtime.replace("Permissions::from_mode(0o600)", "Permissions::from_mode(0o644)"); }],
  ["repeat_feedback_allowed", (v) => { v.runtime = v.runtime.replace('if current_status == "pending"', 'if current_status == "pending" || current_status == "confirmed"'); }],
  ["feedback_cas_removed", (v) => { v.runtime = v.runtime.replace("UPDATE derivation SET status=?1 WHERE id=?2 AND status=?3", "UPDATE derivation SET status=?1 WHERE id=?2"); }],
  ["stale_disclosure_retained", (v) => { v.ui = v.ui.replace("state.disclosure = null;\n          throw error;", "throw error;"); }],
  ["twenty_first_ipc", (v) => { v.runtime = v.runtime.replace('"get_context_disclosure_receipt",\n];', '"get_context_disclosure_receipt",\n    "hidden_send",\n];'); }],
  ["receipt_content_field", (v) => { v.receipt.content = "synthetic-forbidden-content"; }],
];

const mutationResults = mutations.map(([id, apply]) => {
  const value = clone(source);
  apply(value);
  const checks = evaluate(value);
  const caught = checks.some((item) => item.status === "FAIL");
  fs.writeFileSync(path.join(reviewRoot, `${id}.json`), `${JSON.stringify({ id, caught })}\n`, { mode: 0o600 });
  return { id, status: caught ? "PASS" : "FAIL" };
});

fs.writeFileSync(path.join(reviewRoot, markerName), '{"wrong":true}\n', { mode: 0o600 });
const wrongMarkerRefused = guardedCleanup(reviewRoot) === false && fs.existsSync(reviewRoot);
fs.writeFileSync(path.join(reviewRoot, markerName), `${JSON.stringify(marker)}\n`, { mode: 0o600 });
const cleanupSucceeded = guardedCleanup(reviewRoot) && !fs.existsSync(reviewRoot);

const result = {
  schema: "lifeos.p3-144.closure-4.review-tests.v1",
  candidate_commit: "86d764d91c4c6716254eef7d002dd47092c42826",
  base_checks: baseChecks,
  mutations: mutationResults,
  cleanup: {
    wrong_marker_refused: wrongMarkerRefused,
    exact_marker_cleanup: cleanupSucceeded,
    root_absent: !fs.existsSync(reviewRoot),
  },
};
const pass = baseChecks.every((item) => item.status === "PASS") && mutationResults.every((item) => item.status === "PASS") && wrongMarkerRefused && cleanupSucceeded;
process.stdout.write(`${JSON.stringify({ ...result, status: pass ? "PASS" : "FAIL" }, null, 2)}\n`);
process.exit(pass ? 0 : 1);
