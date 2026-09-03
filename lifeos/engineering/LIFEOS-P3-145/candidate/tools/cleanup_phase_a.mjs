import { lstat, readFile, rm, writeFile, chmod, mkdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const root = "/private/tmp/lifeos-p3-145-engineering-v1";
const marker = `${root}/.lifeos-p3-145-owner.json`;
const database = `${root}/capture.sqlite`;
const expectedMarker = {
  schema: "lifeos.p3-145.engineering-root.v1",
  task: "LIFEOS-P3-145",
  owner: "lifeos-p3-145-engineering-v1",
};
const mode = (metadata) => metadata.mode & 0o777;
const canonical = (value) => JSON.stringify(value, Object.keys(value).sort());
const fail = (code) => { throw new Error(code); };
const run = (file, args) => {
  const result = spawnSync(file, args, { encoding: "utf8" });
  if (result.error) throw result.error;
  return result;
};

const rootMetadata = await lstat(root);
const markerMetadata = await lstat(marker);
let databaseMetadata = null;
try {
  databaseMetadata = await lstat(database);
} catch (error) {
  if (error?.code !== "ENOENT") throw error;
}
if (!rootMetadata.isDirectory() || rootMetadata.isSymbolicLink() || mode(rootMetadata) !== 0o700) fail("cleanup_root_rejected");
if (!markerMetadata.isFile() || markerMetadata.isSymbolicLink() || mode(markerMetadata) !== 0o600) fail("cleanup_marker_rejected");
if (databaseMetadata && (!databaseMetadata.isFile() || databaseMetadata.isSymbolicLink() || mode(databaseMetadata) !== 0o600)) fail("cleanup_database_rejected");
const parsedMarker = JSON.parse(await readFile(marker, "utf8"));
if (canonical(parsedMarker) !== canonical(expectedMarker)) fail("cleanup_marker_payload_rejected");

const references = databaseMetadata
  ? (() => {
      const referenceQuery = run("/usr/bin/sqlite3", [database, "SELECT key_reference FROM encrypted_credential WHERE provider_id='deepseek' AND profile_id='default';"]);
      if (referenceQuery.status !== 0) fail("cleanup_reference_query_rejected");
      return referenceQuery.stdout.split("\n").map((value) => value.trim()).filter(Boolean);
    })()
  : [];
if (references.length > 1 || references.some((reference) => !/^p3-145-key-[a-f0-9]{32}$/.test(reference))) fail("cleanup_reference_rejected");
const reference = references[0] || null;
if (reference) {
  const deleted = run("/usr/bin/security", ["delete-generic-password", "-s", "com.lifeos.p3-145.aead-key.v1", "-a", reference]);
  if (deleted.status !== 0) fail("cleanup_keychain_delete_rejected");
  const absent = run("/usr/bin/security", ["find-generic-password", "-s", "com.lifeos.p3-145.aead-key.v1", "-a", reference]);
  if (absent.status === 0) fail("cleanup_keychain_still_present");
}

await rm(root, { recursive: true, force: false, maxRetries: 0 });
try {
  await lstat(root);
  fail("cleanup_root_still_present");
} catch (error) {
  if (error?.code !== "ENOENT") throw error;
}
const report = {
  schema: "lifeos.p3-145.phase-a-cleanup.v1",
  task: "LIFEOS-P3-145",
  root_marker_validated: true,
  database_mode_before_cleanup: databaseMetadata ? "600" : "absent_after_test_cleanup",
  synthetic_keychain_reference_sha256: reference ? createHash("sha256").update(reference).digest("hex") : null,
  synthetic_keychain_item_deleted: Boolean(reference),
  exact_engineering_root_removed: true,
  prohibited_boundary_contact: false,
};
await mkdir(evidence, { recursive: true, mode: 0o700 });
const reportPath = resolve(evidence, "cleanup.json");
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
await chmod(reportPath, 0o600);
console.log(JSON.stringify({ result: "PASS", root_removed: true, keychain_item_deleted: Boolean(reference) }));
