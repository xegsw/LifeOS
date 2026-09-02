import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve("lifeos/reviews/LIFEOS-P3-144/closure-4-independent-review");
const manifest = JSON.parse(await readFile(path.join(root, "FINAL_MANIFEST.json"), "utf8"));
const failures = [];
if (manifest.files.some((entry) => manifest.excluded_paths.includes(entry.path))) failures.push("excluded_path_included");
for (const entry of manifest.files) {
  const data = await readFile(path.join(root, entry.path));
  const digest = createHash("sha256").update(data).digest("hex");
  if (digest !== entry.sha256 || data.length !== entry.size) failures.push(entry.path);
}
const result = { schema: "lifeos.p3-144.closure-4-independent-review.manifest-verification.v1", status: failures.length ? "FAIL" : "PASS", checked: manifest.files.length, failures, self_exclusion: !manifest.files.some((entry) => entry.path === "FINAL_MANIFEST.json" || entry.path === "evidence/final_manifest_verification.json") };
await writeFile(path.join(root, "evidence/final_manifest_verification.json"), `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify(result));
if (failures.length) process.exit(1);
