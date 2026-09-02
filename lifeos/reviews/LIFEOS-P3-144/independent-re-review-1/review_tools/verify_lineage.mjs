import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";

const execFileAsync = promisify(execFile);
const root = resolve(process.cwd());
const closureManifestPath = join(root, "lifeos/engineering/LIFEOS-P3-144/closure-1/FINAL_MANIFEST.json");
const outputPath = process.argv[2] ? resolve(process.argv[2]) : null;
if (!outputPath) throw new Error("usage: node verify_lineage.mjs OUTPUT_JSON");

const sha256 = async (path) => createHash("sha256").update(await readFile(path)).digest("hex");
const failures = [];
const checks = [];
const expect = (condition, id, detail = "") => {
  checks.push({ id, pass: Boolean(condition), detail });
  if (!condition) failures.push(id);
};
const manifest = JSON.parse(await readFile(closureManifestPath, "utf8"));
expect(manifest.schema === "lifeos.p3-144.closure-1.final-manifest.v1", "manifest_schema");
expect(manifest.self_exclusion === true, "manifest_self_exclusion");
const categories = [
  ["candidate", 85],
  ["fixed_inputs", 3],
  ["preserved_history", 3],
  ["closure_evidence", 12],
];
const allEntries = [];
for (const [category, expectedCount] of categories) {
  const entries = manifest[category];
  expect(Array.isArray(entries), `${category}_is_array`);
  expect(entries?.length === expectedCount, `${category}_count`, `expected=${expectedCount} actual=${entries?.length}`);
  for (const entry of entries || []) {
    const absolute = resolve(root, entry.path);
    const actual = await sha256(absolute).catch(() => null);
    expect(
      actual === entry.sha256,
      `hash:${entry.path}`,
      actual === entry.sha256 ? "" : (actual ? "hash mismatch" : "unreadable"),
    );
    allEntries.push(entry.path);
  }
}
expect(new Set(allEntries).size === allEntries.length, "manifest_no_duplicate_paths");

async function walk(dir) {
  const results = [];
  for (const item of await readdir(dir, { withFileTypes: true })) {
    const absolute = join(dir, item.name);
    if (item.isDirectory()) results.push(...await walk(absolute));
    else if (item.isFile()) results.push(relative(root, absolute));
    else results.push(`UNSUPPORTED:${relative(root, absolute)}`);
  }
  return results;
}

const candidateDirectory = join(root, "lifeos/engineering/LIFEOS-P3-144/candidate");
const actualCandidate = new Set((await walk(candidateDirectory)).sort());
const declaredCandidate = new Set(manifest.candidate.map((entry) => entry.path));
const missingCandidate = [...declaredCandidate].filter((path) => !actualCandidate.has(path));
const extraCandidate = [...actualCandidate].filter((path) => !declaredCandidate.has(path));
expect(missingCandidate.length === 0, "candidate_no_missing", JSON.stringify(missingCandidate));
expect(extraCandidate.length === 0, "candidate_no_extra", JSON.stringify(extraCandidate));

const { stdout: head } = await execFileAsync("git", ["rev-parse", "HEAD"], { cwd: root });
const { stdout: tree } = await execFileAsync("git", ["show", "-s", "--format=%T", head.trim()], { cwd: root });
expect(head.trim() === "4115f2958d8fa08fa30fccc90217bdc404769363", "fixed_candidate_commit", head.trim());
const report = {
  schema: "lifeos.p3-144.independent-review.lineage.v1",
  result: failures.length === 0 ? "PASS" : "FAIL",
  fixed_candidate_commit: head.trim(),
  git_tree: tree.trim(),
  checked_at: new Date().toISOString(),
  manifest: relative(root, closureManifestPath),
  categories: Object.fromEntries(categories.map(([name, count]) => [name, count])),
  candidate_tree: { declared: declaredCandidate.size, actual: actualCandidate.size, missing: missingCandidate, extra: extraCandidate },
  checks,
  failures,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
if (failures.length) process.exitCode = 1;
