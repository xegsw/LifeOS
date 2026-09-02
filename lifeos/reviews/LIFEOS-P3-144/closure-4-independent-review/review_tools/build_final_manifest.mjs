import { createHash } from "node:crypto";
import { lstat, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve("lifeos/reviews/LIFEOS-P3-144/closure-4-independent-review");
const excluded = new Set(["FINAL_MANIFEST.json", "evidence/final_manifest_verification.json"]);
async function walk(directory, prefix = "") {
  const names = (await readdir(directory)).sort();
  const files = [];
  for (const name of names) {
    const absolute = path.join(directory, name);
    const relative = prefix ? `${prefix}/${name}` : name;
    const stat = await lstat(absolute);
    if (stat.isSymbolicLink()) throw new Error(`symlink_rejected:${relative}`);
    if (stat.isDirectory()) files.push(...await walk(absolute, relative));
    else if (stat.isFile() && !excluded.has(relative)) {
      const data = await readFile(absolute);
      files.push({ path: relative, size: data.length, sha256: createHash("sha256").update(data).digest("hex") });
    }
  }
  return files;
}
const files = await walk(root);
const manifest = {
  schema: "lifeos.p3-144.closure-4-independent-review.final-manifest.v1",
  candidate_commit: "86d764d91c4c6716254eef7d002dd47092c42826",
  predecessor_commit: "987dd42d",
  result: "PASS",
  non_self_referential: true,
  excluded_paths: [...excluded].sort(),
  file_count: files.length,
  files
};
await writeFile(path.join(root, "FINAL_MANIFEST.json"), `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: "PASS", file_count: files.length }));
