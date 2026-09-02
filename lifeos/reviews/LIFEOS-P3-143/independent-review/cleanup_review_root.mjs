import { lstat, readFile, rm } from "node:fs/promises";

const root = "/private/tmp/lifeos-p3-143-independent-review-v1";
const marker = `${root}/.lifeos-p3-143-independent-review-owner.json`;
const expected = {
  schema: "lifeos.p3-143.independent-review-root.v1",
  task: "LIFEOS-P3-143",
  owner: "lifeos-p3-143-independent-review-v1",
};
const same = (value) => JSON.stringify(value, Object.keys(value).sort());
const rootInfo = await lstat(root);
if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink() || (rootInfo.mode & 0o777) !== 0o700) throw new Error("review_root_type_rejected");
const markerInfo = await lstat(marker);
if (!markerInfo.isFile() || markerInfo.isSymbolicLink() || (markerInfo.mode & 0o777) !== 0o600) throw new Error("review_marker_type_rejected");
const payload = JSON.parse(await readFile(marker, "utf8"));
if (same(payload) !== same(expected)) throw new Error("review_marker_payload_rejected");
await rm(root, { recursive: true, force: false, maxRetries: 0 });
try { await lstat(root); throw new Error("review_root_still_present"); } catch (error) { if (error?.code !== "ENOENT") throw error; }
console.log(JSON.stringify({ root, marker, result: "cleaned_and_absent" }));
