import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

const root = import.meta.dirname;
const manifest = JSON.parse(await readFile(resolve(root, "FINAL_MANIFEST.json"), "utf8"));
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const errors = [];
if (manifest.schema !== "lifeos.p3-143.independent-review-final-manifest.v1" || manifest.task !== "LIFEOS-P3-143" || manifest.self_referential !== false) errors.push({ path: "FINAL_MANIFEST.json", error: "identity_or_self_reference" });
for (const forbidden of ["FINAL_MANIFEST.json", "verify_final_manifest.mjs", "manifest_verification.json"]) {
  if (manifest.files?.some((entry) => entry.path === forbidden)) errors.push({ path: forbidden, error: "self_inclusion" });
}
for (const entry of manifest.files ?? []) {
  try {
    const bytes = await readFile(resolve(root, entry.path));
    if (bytes.length !== entry.bytes || hash(bytes) !== entry.sha256) errors.push({ path: entry.path, error: "hash_or_size_mismatch" });
  } catch {
    errors.push({ path: entry.path, error: "missing" });
  }
}
const result = { schema: "lifeos.p3-143.independent-review-manifest-verification.v1", task: "LIFEOS-P3-143", entries: manifest.files?.length ?? 0, errors, result: errors.length ? "FAIL" : "PASS" };
console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exitCode = 1;
