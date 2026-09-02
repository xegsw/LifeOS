import { readFile, stat } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";

const engineering = resolve(import.meta.dirname, "../../../engineering/LIFEOS-P3-143");
const candidate = resolve(engineering, "candidate");
const manifestPath = resolve(engineering, "FINAL_MANIFEST.json");
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const result = [];
const check = (id, pass, detail) => result.push({ id, result: pass ? "PASS" : "FAIL", detail });

const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
check("IR-S-001", manifest.schema === "lifeos.p3-143.final-manifest.v1" && manifest.task === "LIFEOS-P3-143" && manifest.self_referential === false, "Manifest identity and self-exclusion are explicit.");
let manifestMismatch = 0;
for (const entry of manifest.files ?? []) {
  try {
    const path = resolve(engineering, entry.path);
    const bytes = await readFile(path);
    if (bytes.length !== entry.bytes || digest(bytes) !== entry.sha256) manifestMismatch += 1;
  } catch {
    manifestMismatch += 1;
  }
}
check("IR-S-002", manifestMismatch === 0, `Recomputed ${manifest.files?.length ?? 0} listed hashes; mismatches=${manifestMismatch}.`);

const runtime = await readFile(resolve(candidate, "src/runtime.rs"), "utf8");
const deepseek = await readFile(resolve(candidate, "src/deepseek.rs"), "utf8");
const credentials = await readFile(resolve(candidate, "src/secure_credentials.rs"), "utf8");
const app = await readFile(resolve(candidate, "ui/app.js"), "utf8");
const ipcBlock = runtime.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/);
const ipc = ipcBlock ? [...ipcBlock[1].matchAll(/^\s*"([a-z_]+)",$/gm)].map((match) => match[1]) : [];
check("IR-S-003", ipc.length === 20 && new Set(ipc).size === 20, `Exact IPC literals parsed=${ipc.length}, unique=${new Set(ipc).size}.`);
check("IR-S-004", /pub const AUTHORITY: &str = "https:\/\/api\.deepseek\.com";/.test(deepseek) && /\.env_clear\(\)/.test(deepseek) && /--max-redirs/.test(deepseek) && /--noproxy/.test(deepseek), "Adapter declares exact HTTPS authority, cleared environment, redirect limit, and proxy suppression.");
check("IR-S-005", /Aes256Gcm/.test(credentials) && /add_generic_password/.test(credentials) && /ciphertext: Vec<u8>/.test(credentials) && !/api_key TEXT/i.test(runtime), "Static credential design separates ciphertext record from Keychain material and does not declare a plaintext column.");
check("IR-S-006", /apply_tested_model_directory/.test(runtime) && /value\.selected_model = None;/.test(runtime) && /value\.enabled = false;/.test(runtime) && /operation != "send_fixed_canary"/.test(runtime), "Static state machine separates test, selection, enablement, and fixed-canary send.");
check("IR-S-007", !/fetch\s*\(/.test(app) && !/XMLHttpRequest/.test(app) && /window\.__TAURI__/.test(app), "UI static scan finds Tauri invoke boundary and no direct browser network primitive.");
const hardCodedRoot = /const TASK_ROOT: &str = "\/private\/tmp\/lifeos-p3-143-real-ai-secure-activation-v1";/.test(runtime);
const reviewOverride = /LIFEOS_P3_143_(?:REVIEW_)?ROOT/.test(runtime) || /std::env::var\([^)]*ROOT/.test(runtime);
check("IR-S-008", !hardCodedRoot || reviewOverride, "Fixed candidate must support a fresh review-owned root without touching the retained Phase-B root.");
const rootMarker = await stat("/private/tmp/lifeos-p3-143-independent-review-v1/.lifeos-p3-143-independent-review-owner.json");
check("IR-S-009", rootMarker.isFile() && (rootMarker.mode & 0o777) === 0o600, "Review-owned temporary-root marker is a 0600 regular file.");

const summary = {
  schema: "lifeos.p3-143.independent-review-static.v1",
  task: "LIFEOS-P3-143",
  runner_owner: "independent-review",
  candidate_test_or_verifier_imported: false,
  network_actions: 0,
  results: result,
  passed: result.filter((entry) => entry.result === "PASS").length,
  failed: result.filter((entry) => entry.result === "FAIL").length,
};
console.log(JSON.stringify(summary, null, 2));
if (summary.failed) process.exitCode = 1;
