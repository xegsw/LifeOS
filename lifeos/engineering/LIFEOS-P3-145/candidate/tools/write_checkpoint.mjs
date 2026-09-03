import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { relative, resolve } from "node:path";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const task = resolve(candidate, "../../../tasks/LIFEOS-P3-145_work_health_cross_domain_today_personalization_and_feedback_adaptation_real_loop.md");
const baseline = resolve(candidate, "../../../tasks/LIFEOS-P3-145_work_health_cross_domain_today_personalization_and_feedback_adaptation_real_loop_acceptance_basis_freeze.md");
const freeze = resolve(candidate, "../../../tasks/LIFEOS-P3-145_acceptance_freeze_manifest.json");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
async function walk(folder) {
  const entries = await readdir(folder, { withFileTypes: true });
  const result = [];
  for (const entry of entries) {
    const path = resolve(folder, entry.name);
    if (["target", ".cargo-target", ".tmp"].includes(entry.name)) continue;
    if (entry.isDirectory()) result.push(...await walk(path));
    else if (entry.isFile()) result.push({ path: relative(candidate, path), sha256: hash(await readFile(path)) });
  }
  return result;
}
const candidateFiles = (await walk(candidate)).sort((left, right) => left.path.localeCompare(right.path));
const checkpoint = {
  schema: "lifeos.execution-checkpoint.v1",
  task_id: "LIFEOS-P3-145",
  attempt_id: "engineering-phase-a-attempt-1",
  updated_at: new Date().toISOString(),
  task_contract_sha256: hash(await readFile(task)),
  baseline_sha256: hash(await readFile(baseline)),
  acceptance_freeze_manifest_sha256: hash(await readFile(freeze)),
  candidate_sha256: hash(Buffer.from(JSON.stringify(candidateFiles))),
  stage: "phase_a_engineering_complete",
  status: "awaiting_independent_review",
  pause_class: "role_separation",
  pause_reason_code: "phase_a_complete_fresh_independent_review_required",
  completed_checks: [
    "preflight_allowlist_and_prohibited_path_declaration",
    "rust_format_and_targeted_locked_offline_test",
    "offline_contract_and_static_contract",
    "marker_negative_matrix",
    "locked_offline_tauri_bundle",
    "actual_tauri_synthetic_work_health_loop",
    "direct_launch_pid_to_exact_axwindow_to_axwebarea",
    "target_window_only_desktop_compact_narrow_screenshots"
  ],
  pending_checks: ["fresh_independent_review", "pm_acceptance", "phase_c_controlled_real_loop_after_independent_pass"],
  rerun_checks: ["independent_review_only_if_candidate_and_frozen_inputs_unchanged"],
  excluded_artifacts: [
    "Phase B review-root tests remain ignored in Phase A and are reserved for a fresh independent session",
    "All retained screenshots contain only fixed synthetic canaries"
  ],
  prohibited_boundary_contact: false,
  fixed_inputs_mutated: false,
  positive_evidence_separable: true,
  runtime: { app_running: false, direct_pid: null, writers_stopped: true, database_closed: true, temporary_root_state: "cleaned_marker_bound_after_phase_a" },
  resume_from: "fresh_independent_review",
  safe_to_resume: false,
  notes: "Phase A used only fixed synthetic fixtures and a hard-pinned synthetic mode. The actual-Tauri evidence records direct PID chains for desktop, compact, and narrow viewports; no network request or real personal content was used. This checkpoint is not an independent-review, PM acceptance, Phase C, risk-closure, product-freeze, or Stage-transition conclusion."
};
await mkdir(evidence, { recursive: true });
await writeFile(resolve(evidence, "checkpoint.json"), `${JSON.stringify(checkpoint, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: checkpoint.status, resume_from: checkpoint.resume_from, candidate_sha256: checkpoint.candidate_sha256 }));
