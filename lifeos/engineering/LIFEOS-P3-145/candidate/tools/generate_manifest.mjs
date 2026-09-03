import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { resolve, relative } from "node:path";
import { createHash } from "node:crypto";

const engineering = resolve(import.meta.dirname, "..", "..");
const candidate = resolve(engineering, "candidate");
const evidence = resolve(engineering, "evidence");
const output = resolve(engineering, "FINAL_MANIFEST.json");
const excluded = new Set([output, resolve(evidence, "manifest_verification.json")]);
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
async function walk(folder) {
  const entries = await readdir(folder, { withFileTypes: true });
  const values = [];
  for (const entry of entries) {
    const path = resolve(folder, entry.name);
    if (["target", ".cargo-target", ".tmp"].includes(entry.name)) continue;
    if (excluded.has(path)) continue;
    if (entry.isDirectory()) values.push(...await walk(path));
    else if (entry.isFile()) { const bytes = await readFile(path); values.push({ path: relative(engineering, path), bytes: bytes.length, sha256: hash(bytes) }); }
  }
  return values;
}
await mkdir(evidence, { recursive: true });
const files = [...await walk(candidate), ...await walk(evidence)].sort((a, b) => a.path.localeCompare(b.path));
const manifest = { schema: "lifeos.p3-145.final-manifest.v1", task: "LIFEOS-P3-145", self_referential: false, categories: ["candidate", "evidence"], files, generated_at: "deterministic-from-current-files" };
await writeFile(output, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: "PASS", entries: files.length, output }));
