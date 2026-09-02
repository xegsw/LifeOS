import { lstat, readFile, rm } from "node:fs/promises";

const root = "/private/tmp/lifeos-p3-144-independent-review-v1";
const marker = `${root}/.lifeos-p3-144-owner.json`;
const expected = {
  schema: "lifeos.p3-144.independent-review-root.v1",
  task: "LIFEOS-P3-144",
  owner: "lifeos-p3-144-independent-review",
  runId: "v1",
};
const mode = (value) => value.mode & 0o777;
const rootMeta = await lstat(root);
const markerMeta = await lstat(marker);
if (!rootMeta.isDirectory() || rootMeta.isSymbolicLink() || mode(rootMeta) !== 0o700) throw new Error("root_contract_rejected");
if (!markerMeta.isFile() || markerMeta.isSymbolicLink() || mode(markerMeta) !== 0o600) throw new Error("marker_type_rejected");
const observed = JSON.parse(await readFile(marker, "utf8"));
if (JSON.stringify(observed) !== JSON.stringify(expected)) throw new Error("marker_payload_rejected");
await rm(root, { recursive: true, force: false, maxRetries: 0 });
console.log(JSON.stringify({ result: "PASS", root, cleanup: "marker_gated_exact_root" }));
