import { chmod, lstat, readFile, rm } from "node:fs/promises";
import path from "node:path";

const root = "/private/tmp/lifeos-p3-144-independent-review-v1";
const marker = path.join(root, ".lifeos-p3-144-owner.json");
const expected = { schema: "lifeos.p3-144.independent-review-root.v1", task: "LIFEOS-P3-144", owner: "lifeos-p3-144-independent-review", runId: "v1" };
if (path.resolve(root) !== root || path.dirname(root) !== "/private/tmp") throw new Error("root_literal_rejected");
const rootStat = await lstat(root);
if (!rootStat.isDirectory() || rootStat.isSymbolicLink() || (rootStat.mode & 0o777) !== 0o700) throw new Error("root_type_rejected");
const markerStat = await lstat(marker);
if (!markerStat.isFile() || markerStat.isSymbolicLink() || (markerStat.mode & 0o777) !== 0o600) throw new Error("marker_type_rejected");
const actual = JSON.parse(await readFile(marker, "utf8"));
if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error("marker_payload_rejected");
await chmod(root, 0o700);
await rm(root, { recursive: true, force: false, maxRetries: 0 });
try { await lstat(root); throw new Error("cleanup_absence_failed"); } catch (error) { if (error.code !== "ENOENT") throw error; }
console.log(JSON.stringify({ root, marker, cleanup: "exact_marker_gated", absence: true }));
