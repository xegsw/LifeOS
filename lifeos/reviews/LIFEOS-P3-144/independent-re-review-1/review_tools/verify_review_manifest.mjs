import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";

const workspace = resolve(process.cwd());
const reviewBase = "lifeos/reviews/LIFEOS-P3-144/independent-re-review-1";
const manifestPath = join(workspace, reviewBase, "FINAL_MANIFEST.json");
const outputPath = join(workspace, reviewBase, "evidence/review_manifest_verification.json");
const sha256 = async (path) => createHash("sha256").update(await readFile(path)).digest("hex");
const failures = [];
const checks = [];
const check = (condition, id, detail = "") => {
  checks.push({ id, pass: Boolean(condition), detail });
  if (!condition) failures.push(id);
};
const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
check(manifest.schema === "lifeos.p3-144.independent-re-review-1.final-manifest.v1", "schema");
check(manifest.candidate_commit === "4115f2958d8fa08fa30fccc90217bdc404769363", "candidate_commit");
check(manifest.self_exclusion === true, "self_exclusion");
const all = Object.values(manifest.categories).flat();
const paths = all.map((entry) => entry.path);
check(new Set(paths).size === paths.length, "no_duplicate_paths");
check(!paths.includes(`${reviewBase}/FINAL_MANIFEST.json`), "manifest_not_listed");
check(!paths.includes(`${reviewBase}/evidence/review_manifest_verification.json`), "verification_output_not_listed");
for (const entry of all) {
  const absolute = join(workspace, entry.path);
  const actual = await sha256(absolute).catch(() => null);
  check(actual === entry.sha256, `hash:${entry.path}`, actual === entry.sha256 ? "" : (actual ? "hash mismatch" : "unreadable"));
}
const report = {
  schema: "lifeos.p3-144.independent-re-review-1.manifest-verification.v1",
  manifest: relative(workspace, manifestPath),
  result: failures.length === 0 ? "PASS" : "FAIL",
  category_counts: Object.fromEntries(Object.entries(manifest.categories).map(([key, values]) => [key, values.length])),
  checks,
  failures,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: report.result, failures: report.failures, category_counts: report.category_counts }));
if (failures.length) process.exitCode = 1;
