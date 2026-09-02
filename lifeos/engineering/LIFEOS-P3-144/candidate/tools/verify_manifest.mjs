import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { createHash } from "node:crypto";

const engineering = resolve(import.meta.dirname, "..", "..");
const manifestPath = resolve(engineering, "FINAL_MANIFEST.json");
const evidencePath = resolve(engineering, "evidence", "manifest_verification.json");
const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const errors = [];
if (manifest.schema !== "lifeos.p3-144.final-manifest.v1" || manifest.task !== "LIFEOS-P3-144" || manifest.self_referential !== false) errors.push({ path: "FINAL_MANIFEST.json", error: "identity_or_self_reference" });
for (const entry of manifest.files || []) {
  try {
    const bytes = await readFile(resolve(engineering, entry.path));
    if (bytes.length !== entry.bytes || hash(bytes) !== entry.sha256) errors.push({ path: entry.path, error: "hash_mismatch" });
  } catch { errors.push({ path: entry.path, error: "missing" }); }
}
const result = { schema: "lifeos.p3-144.manifest-verification.v1", task: "LIFEOS-P3-144", entries: manifest.files?.length || 0, errors, result: errors.length ? "FAIL" : "PASS" };
await writeFile(evidencePath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify(result));
if (errors.length) process.exit(1);
