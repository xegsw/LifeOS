import { chmod, mkdir, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const cargo = "/Users/xxe/.cargo/bin/cargo";
const node = process.execPath;
const environment = {
  ...process.env,
  PATH: "/Users/xxe/.cargo/bin:" + (process.env.PATH || ""),
  LIFEOS_P3_145_ROOT_PROFILE: "engineering",
  CARGO_TARGET_DIR: resolve(candidate, ".cargo-target"),
  TMPDIR: resolve(candidate, ".tmp"),
};
const steps = [
  { id: "marker_init", file: node, args: ["tools/task_root.mjs", "init"] },
  { id: "rust_format", file: cargo, args: ["fmt", "--all", "--", "--check"] },
  { id: "locked_offline_check", file: cargo, args: ["check", "--locked", "--offline"] },
  { id: "locked_offline_tests", file: cargo, args: ["test", "--locked", "--offline", "--", "--test-threads=1"] },
  { id: "offline_contract", file: node, args: ["tests/offline_contract.mjs"] },
  { id: "static_contract", file: node, args: ["tools/collect_static_evidence.mjs"] },
  { id: "marker_negative_matrix", file: node, args: ["tools/task_root.mjs", "negative"] },
  { id: "marker_verify", file: node, args: ["tools/task_root.mjs", "verify"] },
];

await mkdir(environment.CARGO_TARGET_DIR, { recursive: true, mode: 0o700 });
await mkdir(environment.TMPDIR, { recursive: true, mode: 0o700 });
const report = {
  schema: "lifeos.p3-145.phase-a-automation.v1",
  task: "LIFEOS-P3-145",
  root_profile: "engineering",
  offline_only: true,
  started_at: new Date().toISOString(),
  steps: [],
};
for (const step of steps) {
  const result = spawnSync(step.file, step.args, {
    cwd: candidate,
    env: environment,
    encoding: "utf8",
    timeout: 180000,
  });
  report.steps.push({
    id: step.id,
    command: [step.file, ...step.args],
    status: result.status === 0 && !result.error ? "PASS" : "FAIL",
    exit_code: result.status,
    signal: result.signal || null,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    error: result.error?.message || null,
  });
  if (result.status !== 0 || result.error) break;
}
report.completed_at = new Date().toISOString();
report.result = report.steps.length === steps.length && report.steps.every((step) => step.status === "PASS") ? "PASS" : "FAIL";
await mkdir(evidence, { recursive: true, mode: 0o700 });
const reportPath = resolve(evidence, "phase_a_automation.json");
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
await chmod(reportPath, 0o600);
console.log(JSON.stringify({ task: report.task, result: report.result, steps: report.steps.map((step) => [step.id, step.status]) }));
if (report.result !== "PASS") process.exit(1);
