import { createHash } from "node:crypto";
import { lstat, readdir, readFile } from "node:fs/promises";
import { relative, resolve } from "node:path";

const root = resolve(process.cwd(), "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3");
const manifest = JSON.parse(await readFile(resolve(root, "FINAL_MANIFEST.json"), "utf8"));
const mutation = process.argv.find((arg) => arg.startsWith("--mutation="))?.slice(11);
if (mutation === "missing_entry") manifest.entries = manifest.entries.slice(1);
if (mutation === "hash_drift" && manifest.entries.length) manifest.entries[0].sha256 = "0".repeat(64);
if (mutation && !["missing_entry", "hash_drift"].includes(mutation)) throw new Error("unsupported mutation");
const errors = [];
if (manifest.evaluation_status !== "INDEPENDENT_PASS_SYNTHETIC_OFFLINE") errors.push("evaluation_status_must_be_independent_pass_synthetic_offline");
if (manifest.entries.some((entry) => entry.path === "FINAL_MANIFEST.json" || entry.path.startsWith("work/"))) errors.push("self_or_work_entry_rejected");
const expectedPaths = new Set();
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = resolve(directory, entry.name);
    const path = relative(root, absolute).replaceAll("\\\\", "/");
    if (entry.isDirectory()) {
      if (path !== "work") await walk(absolute);
      continue;
    }
    const stat = await lstat(absolute);
    if (!stat.isFile() || stat.isSymbolicLink()) errors.push(`unexpected_type:${path}`);
    else if (path !== "FINAL_MANIFEST.json") expectedPaths.add(path);
  }
}
await walk(root);
const declaredPaths = new Set(manifest.entries.map((entry) => entry.path));
for (const path of expectedPaths) if (!declaredPaths.has(path)) errors.push(`missing_entry:${path}`);
for (const path of declaredPaths) if (!expectedPaths.has(path)) errors.push(`extra_entry:${path}`);
for (const entry of manifest.entries) {
  const absolute = resolve(root, entry.path);
  if (!absolute.startsWith(`${root}/`)) {
    errors.push(`path_escape:${entry.path}`);
    continue;
  }
  let stat;
  try { stat = await lstat(absolute); } catch { errors.push(`missing:${entry.path}`); continue; }
  if (!stat.isFile() || stat.isSymbolicLink()) { errors.push(`type:${entry.path}`); continue; }
  const bytes = await readFile(absolute);
  const sha256 = createHash("sha256").update(bytes).digest("hex");
  if (bytes.length !== entry.bytes) errors.push(`bytes:${entry.path}`);
  if (sha256 !== entry.sha256) errors.push(`hash:${entry.path}`);
}
console.log(JSON.stringify({ status: errors.length ? "FAIL" : "PASS", entry_count: manifest.entry_count, mutation: mutation ?? null, errors }));
if (errors.length) process.exit(1);
