import { createHash } from "node:crypto";
import { lstat, readdir, readFile, writeFile } from "node:fs/promises";
import { relative, resolve } from "node:path";

const root = resolve(process.cwd(), "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3");
const manifestPath = resolve(root, "FINAL_MANIFEST.json");
const excludedDirectories = new Set(["work"]);
const excludedFiles = new Set(["FINAL_MANIFEST.json"]);
const files = [];
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = resolve(directory, entry.name);
    const rel = relative(root, absolute).replaceAll("\\\\", "/");
    if (entry.isDirectory()) {
      if (!excludedDirectories.has(rel)) await walk(absolute);
      continue;
    }
    const stat = await lstat(absolute);
    if (!stat.isFile()) throw new Error(`non-regular review artifact rejected: ${rel}`);
    if (!excludedFiles.has(rel)) {
      const content = await readFile(absolute);
      files.push({ path: rel, type: "regular", bytes: content.length, sha256: createHash("sha256").update(content).digest("hex") });
    }
  }
}
await walk(root);
files.sort((a, b) => a.path.localeCompare(b.path));
const result = {
  schema: "lifeos.p3-144.independent-review-final-manifest.v1",
  task_id: "LIFEOS-P3-144",
  review_id: "independent-re-review-3",
  evaluation_status: "INDEPENDENT_PASS_SYNTHETIC_OFFLINE",
  conclusion: "Independent Pass is established only for the sealed Phase B synthetic/offline review scope; no Phase C, real Provider, Pilot or real credential conclusion is made.",
  excluded_from_manifest: ["FINAL_MANIFEST.json", "work/"],
  entry_count: files.length,
  entries: files
};
await writeFile(manifestPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ status: "PASS", entry_count: files.length, self_reference: false, evaluation_status: result.evaluation_status }));
