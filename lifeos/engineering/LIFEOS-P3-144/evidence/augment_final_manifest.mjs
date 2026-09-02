import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { relative, resolve } from "node:path";

const evidence = resolve(import.meta.dirname);
const engineering = resolve(evidence, "..");
const lifeos = resolve(engineering, "..", "..");
const manifestPath = resolve(engineering, "FINAL_MANIFEST.json");
const freezePath = resolve(lifeos, "tasks", "LIFEOS-P3-144_acceptance_freeze_manifest.json");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");

const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
const freezeBytes = await readFile(freezePath);
const freeze = JSON.parse(freezeBytes.toString("utf8"));
if (freeze.task_id !== "LIFEOS-P3-144" || freeze.abf_id !== "ABF-P3-144-v1") throw new Error("freeze_identity_rejected");
const frozenEntries = [];
for (const entry of freeze.entries) {
  const absolute = resolve(lifeos, "..", entry.path);
  const bytes = await readFile(absolute);
  if (hash(bytes) !== entry.sha256) throw new Error(`frozen_input_hash_mismatch:${entry.path}`);
  frozenEntries.push({
    category: entry.role.startsWith("predecessor_") ? "history" : "fixed_input",
    role: entry.role,
    path: relative(engineering, absolute),
    bytes: bytes.length,
    sha256: hash(bytes)
  });
}
frozenEntries.push({
  category: "fixed_input",
  role: "acceptance_freeze_manifest",
  path: relative(engineering, freezePath),
  bytes: freezeBytes.length,
  sha256: hash(freezeBytes)
});
const observed = (manifest.files || []).map((entry) => ({ ...entry, category: entry.path.startsWith("candidate/") ? "candidate" : "evidence" }));
manifest.categories = ["candidate", "fixed_input", "history", "evidence"];
manifest.files = [...observed, ...frozenEntries].sort((left, right) => left.path.localeCompare(right.path));
manifest.fixed_input_freeze = { path: relative(engineering, freezePath), sha256: hash(freezeBytes), schema_version: freeze.schema_version, abf_id: freeze.abf_id, entry_count: frozenEntries.length, verified_before_manifest_write: true };
manifest.generated_at = "deterministic-from-current-files-and-frozen-inputs";
await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: "PASS", entries: manifest.files.length, frozen_entries: frozenEntries.length }));
