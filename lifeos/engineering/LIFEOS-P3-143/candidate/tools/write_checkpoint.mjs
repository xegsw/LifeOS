import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { relative, resolve } from "node:path";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const task = resolve(candidate, "../../../tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md");
const baseline = resolve(candidate, "../../../tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation_acceptance_basis_freeze.md");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
async function walk(folder) {
  const entries = await readdir(folder, { withFileTypes: true });
  const result = [];
  for (const entry of entries) {
    const path = resolve(folder, entry.name);
    if (entry.name === "target") continue;
    if (entry.isDirectory()) result.push(...await walk(path));
    else if (entry.isFile()) { const bytes = await readFile(path); result.push({ path: relative(candidate, path), sha256: hash(bytes) }); }
  }
  return result;
}
const candidateFiles = (await walk(candidate)).sort((left, right) => left.path.localeCompare(right.path));
const checkpoint = {
  schema: "lifeos.execution-checkpoint.v1",
  task_id: "LIFEOS-P3-143",
  attempt_id: "engineering-phase-a-attempt-1",
  updated_at: new Date().toISOString(),
  task_contract_sha256: hash(await readFile(task)),
  candidate_sha256: hash(Buffer.from(JSON.stringify(candidateFiles))),
  baseline_sha256: hash(await readFile(baseline)),
  stage: "native_visual_capture",
  status: "paused_resumable",
  pause_class: "recoverable_environment",
  pause_reason_code: "compact_and_narrow_screenshot_thumbnail_only",
  completed_checks: ["preflight", "offline_contract", "credential_lifecycle_and_mutation", "desktop_direct_pid_ax_webview"],
  pending_checks: ["desktop_requested_geometry", "compact_readable_target_screenshot", "narrow_readable_target_screenshot", "phase_a_manifest", "user_operated_real_gate", "independent_review"],
  rerun_checks: ["native_visual_capture", "phase_a_manifest", "user_operated_real_gate", "independent_review"],
  excluded_artifacts: ["evidence/native-compact-settings.png: 127x134 unreadable thumbnail removed", "evidence/native-narrow-settings.png: 80x132 unreadable thumbnail removed"],
  prohibited_boundary_contact: false,
  candidate_or_history_mutated: false,
  positive_evidence_separable: true,
  runtime: { app_running: false, direct_pid: null, writers_stopped: true, database_closed: true, temporary_root_state: "present_marker_bound_for_resume" },
  resume_from: "native_visual_capture",
  safe_to_resume: true,
  notes: "No API Key, prompt, response, personal data or network request was used. The desktop AX/WebView chain is present; compact and narrow screenshot outputs were excluded because they are unreadable thumbnails."
};
await mkdir(evidence, { recursive: true });
await writeFile(resolve(evidence, "checkpoint.json"), `${JSON.stringify(checkpoint, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: "PAUSED_RESUMABLE", resume_from: checkpoint.resume_from, candidate_sha256: checkpoint.candidate_sha256 }));
