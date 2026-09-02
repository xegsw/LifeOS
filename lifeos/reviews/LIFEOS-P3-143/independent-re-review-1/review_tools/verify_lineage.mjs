import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";

const workspace = process.cwd();
const candidateCommit = "767301fb051d11a6bf11488413f8b03aabfc2d99";
const manifestPath = resolve(workspace, "lifeos/engineering/LIFEOS-P3-143/FINAL_MANIFEST.json");
const closurePath = resolve(workspace, "lifeos/engineering/LIFEOS-P3-143/evidence/root_authority_closure.json");
const outputPath = resolve(workspace, "lifeos/reviews/LIFEOS-P3-143/independent-re-review-1/evidence/lineage_verification.json");

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
const results = [];
for (const entry of manifest.files) {
  const absolute = resolve(dirname(manifestPath), entry.path);
  const relativePath = relative(workspace, absolute);
  const bytes = await readFile(absolute);
  const actual = sha256(bytes);
  results.push({
    category: entry.category,
    role: entry.role ?? null,
    path: relativePath,
    bytes_expected: entry.bytes,
    bytes_actual: bytes.length,
    sha256_expected: entry.sha256,
    sha256_actual: actual,
    pass: bytes.length === entry.bytes && actual === entry.sha256,
  });
}
const closureBytes = await readFile(closurePath);
const closure = JSON.parse(closureBytes);
const categories = Object.fromEntries(manifest.categories.map((category) => [category, 0]));
for (const item of results) categories[item.category] = (categories[item.category] ?? 0) + 1;
const errors = results.filter((item) => !item.pass).length;
const output = {
  schema: "lifeos.p3-143.independent-lineage-verification.v1",
  reviewer_owned: true,
  candidate_commit: candidateCommit,
  manifest_self_referential: manifest.self_referential,
  manifest_entry_count: results.length,
  category_counts: categories,
  hash_error_count: errors,
  root_authority_closure: {
    sha256: sha256(closureBytes),
    candidate_files: closure.candidate_identity?.candidate_files ?? null,
    closure_candidate_sha256: closure.candidate_identity?.after_root_authority_closure_sha256 ?? null,
    decision: closure.decision ?? null,
  },
  status: !manifest.self_referential && errors === 0 ? "PASS" : "FAIL",
  files: results,
};
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, { mode: 0o600 });
if (output.status !== "PASS") process.exitCode = 1;
