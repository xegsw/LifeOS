import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { resolve, relative } from "node:path";
import { createHash } from "node:crypto";

const candidate = resolve(import.meta.dirname, "..");
const engineering = resolve(candidate, "..");
const evidence = resolve(engineering, "evidence");
const contract = resolve("/Users/xxe/.codex/worktrees/f987/No.2/lifeos/tasks/LIFEOS-P3-142_model_settings_ai_service_configuration_center_v1.md");
const baseline = resolve("/Users/xxe/.codex/worktrees/f987/No.2/lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
async function tree(folder) {
  const entries = await readdir(folder, { withFileTypes: true });
  const result = [];
  for (const entry of entries) {
    const path = resolve(folder, entry.name);
    if (entry.isDirectory()) result.push(...await tree(path));
    if (entry.isFile()) result.push({ path: relative(candidate, path), sha256: hash(await readFile(path)) });
  }
  return result;
}
const candidateFiles = (await tree(candidate)).sort((a, b) => a.path.localeCompare(b.path));
const candidateSha = hash(Buffer.from(JSON.stringify(candidateFiles)));
const contractSha = hash(await readFile(contract));
const baselineSha = hash(await readFile(baseline));
const title = "LifeOS · 模型设置（合成离线）";
const attempts = [
  { viewport: "desktop", requested: { width: 1280, height: 1024 }, pid: 46461, ax_file: "ax-desktop-final.txt", screenshot: "native-desktop-final.png", screenshot_pixels: { width: 138, height: 163 } },
  { viewport: "compact", requested: { width: 1160, height: 768 }, pid: 46481, ax_file: "ax-compact-final.txt", screenshot: "native-compact-final.png", screenshot_pixels: { width: 127, height: 134 } },
  { viewport: "narrow", requested: { width: 700, height: 760 }, pid: 46506, ax_file: "ax-narrow-final.txt", screenshot: "native-narrow-final.png", screenshot_pixels: { width: 80, height: 132 } },
].map((item) => ({ ...item, expected_window_title: title, ax_chain: "direct PID -> exact AXWindow title -> HTML content (Tauri WebView/Area)", screenshot_result: "excluded_thumbnail_not_readable" }));
const native = {
  schema: "lifeos.p3-142.native-window-evidence.v1",
  task: "LIFEOS-P3-142",
  status: "EVIDENCE_GAP",
  attempts,
  positive_native_binding: true,
  visual_acceptance: "NOT_PASS_PENDING_READABLE_TARGET_ONLY_SCREENSHOTS",
  environment_note: "Computer Use returned downscaled thumbnails; no external target or prohibited data was accessed.",
};
const checkpoint = {
  schema: "lifeos.execution-checkpoint.v1",
  task_id: "LIFEOS-P3-142",
  attempt_id: "engineering-attempt-1",
  updated_at: new Date().toISOString(),
  task_contract_sha256: contractSha,
  candidate_sha256: candidateSha,
  baseline_sha256: baselineSha,
  stage: "format_and_visual_capture",
  status: "paused_resumable",
  pause_class: "recoverable_environment",
  pause_reason_code: "rustfmt_unavailable_and_native_screenshot_thumbnail_only",
  completed_checks: ["preflight", "build_test", "data_lifecycle", "app_launch", "native_window_binding"],
  pending_checks: ["offline_cargo_fmt_check", "readable_target_only_desktop_screenshot", "readable_target_only_compact_screenshot", "readable_target_only_narrow_screenshot", "visual_checklist", "final_manifest", "exact_cleanup"],
  rerun_checks: ["offline_cargo_fmt_check", "visual_capture", "manifest", "cleanup"],
  excluded_artifacts: attempts.map((item) => `evidence/${item.screenshot}: ${item.screenshot_pixels.width}x${item.screenshot_pixels.height} thumbnail`),
  prohibited_boundary_contact: false,
  candidate_or_history_mutated: false,
  positive_evidence_separable: true,
  runtime: { app_running: false, direct_pid: null, writers_stopped: true, database_closed: true, temporary_root_state: "present_marker_bound_for_resume" },
  resume_from: "offline_cargo_fmt_check",
  safe_to_resume: true,
  notes: "Pre-marker build cache was not used as positive Evidence. It did not access prohibited targets; all listed completed checks use marker-bound reruns. The configured offline cargo fmt check is pending because this toolchain has no rustfmt binary. Do not include personal text, credentials, or database contents."
};
await mkdir(evidence, { recursive: true });
await writeFile(resolve(evidence, "native_window_evidence.json"), `${JSON.stringify(native, null, 2)}\n`);
await writeFile(resolve(evidence, "checkpoint.json"), `${JSON.stringify(checkpoint, null, 2)}\n`);
console.log(JSON.stringify({ native_status: native.status, checkpoint: checkpoint.status, candidate_sha256: candidateSha }));
