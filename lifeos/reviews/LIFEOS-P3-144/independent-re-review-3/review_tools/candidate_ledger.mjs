import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const root = process.cwd();
const candidate = "lifeos/engineering/LIFEOS-P3-144/candidate";
const review = "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3";
const phase = process.argv.find((arg) => arg.startsWith("--phase="))?.slice(8);
const label = process.argv.find((arg) => arg.startsWith("--label="))?.slice(8) ?? phase;
if (!["before", "after"].includes(phase)) throw new Error("phase must be before or after");
const git = (...args) => execFileSync("git", args, { cwd: root, encoding: "utf8" }).trim();
const head = git("rev-parse", "HEAD");
const expectedHead = "a38bcb1911336d26ca7ee59214a3613ec3ab047a";
const closure2 = "461423b3489c18683167bb9c85775a79548836b1";
const tracked = git("ls-files", "-z", "--", candidate).split("\0").filter(Boolean).sort();
const entries = [];
for (const path of tracked) {
  const bytes = await readFile(resolve(root, path));
  entries.push({ path, bytes: bytes.length, sha256: createHash("sha256").update(bytes).digest("hex") });
}
const ignoredStatus = git("status", "--ignored", "--short", "--", candidate);
const candidateDiff = spawnSync("git", ["diff", "--quiet", closure2, expectedHead, "--", candidate], { cwd: root }).status;
const treeHash = createHash("sha256").update(JSON.stringify(entries)).digest("hex");
const result = {
  schema: "lifeos.p3-144.independent-review.candidate-ledger.v1",
  phase,
  candidate,
  head,
  expected_head: expectedHead,
  closure2_commit: closure2,
  head_matches: head === expectedHead,
  candidate_matches_closure2: candidateDiff === 0,
  ignored_status: ignoredStatus,
  ignored_status_empty: ignoredStatus === "",
  tracked_file_count: entries.length,
  source_tree_sha256: treeHash,
  entries,
  prohibited_pilot_contact: false
};
await mkdir(resolve(root, review, "evidence"), { recursive: true, mode: 0o700 });
const output = resolve(root, review, "evidence", `candidate_ledger_${label}.json`);
await writeFile(output, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.head_matches || !result.candidate_matches_closure2 || !result.ignored_status_empty || tracked.length !== 85) {
  throw new Error("candidate lineage or zero-write ledger check failed");
}
console.log(JSON.stringify({ status: "PASS", phase, label, tracked_file_count: tracked.length, source_tree_sha256: treeHash }));
