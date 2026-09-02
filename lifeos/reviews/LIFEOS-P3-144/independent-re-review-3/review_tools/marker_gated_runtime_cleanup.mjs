import { lstat, mkdir, readFile, rename, rm, symlink, writeFile, chmod, realpath } from "node:fs/promises";
import { resolve } from "node:path";

const root = "/private/tmp/lifeos-p3-144-independent-review-v1";
const marker = `${root}/.lifeos-p3-144-owner.json`;
const backup = `${root}/.lifeos-p3-144-owner.json.review-backup`;
const expected = {
  schema: "lifeos.p3-144.independent-review-root.v1",
  task: "LIFEOS-P3-144",
  owner: "lifeos-p3-144-independent-review",
  runId: "v1"
};
const review = resolve(process.cwd(), "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3");
const rejected = [];
const assertRejects = async (label) => {
  try {
    await verify();
    throw new Error(`${label}_accepted`);
  } catch (error) {
    if (error.message.endsWith("_accepted")) throw error;
    rejected.push({ label, code: error.message });
  }
};
async function verify() {
  const rootMeta = await lstat(root);
  if (!rootMeta.isDirectory() || rootMeta.isSymbolicLink() || (rootMeta.mode & 0o777) !== 0o700) throw new Error("root_type_rejected");
  if (await realpath(root) !== root) throw new Error("root_canonical_rejected");
  const markerMeta = await lstat(marker);
  if (!markerMeta.isFile() || markerMeta.isSymbolicLink() || (markerMeta.mode & 0o777) !== 0o600) throw new Error("marker_type_rejected");
  const observed = JSON.parse(await readFile(marker, "utf8"));
  if (JSON.stringify(observed) !== JSON.stringify(expected)) throw new Error("marker_payload_rejected");
  const runtime = `${root}/runtime`;
  const runtimeMeta = await lstat(runtime);
  if (!runtimeMeta.isDirectory() || runtimeMeta.isSymbolicLink() || (runtimeMeta.mode & 0o777) !== 0o700) throw new Error("runtime_child_rejected");
  if (await realpath(runtime) !== runtime) throw new Error("runtime_child_canonical_rejected");
}

try { await lstat(root); } catch { throw new Error("review_runtime_root_missing_before_cleanup"); }
await rename(marker, backup);
await assertRejects("missing_marker");
await rename(backup, marker);
await rename(marker, backup);
await writeFile(marker, `${JSON.stringify({ ...expected, runId: "wrong" })}\n`, { mode: 0o600 });
await chmod(marker, 0o600);
await assertRejects("wrong_marker");
await rm(marker);
await rename(backup, marker);
await rename(marker, backup);
await symlink(backup, marker);
await assertRejects("symlink_marker");
await rm(marker);
await rename(backup, marker);
await verify();
await rm(root, { recursive: true, force: false, maxRetries: 1 });
let absent = false;
try { await lstat(root); } catch (error) { absent = error.code === "ENOENT"; }
if (!absent) throw new Error("runtime_root_still_present_after_cleanup");
const receipt = {
  schema: "lifeos.p3-144.independent-review.marker-gated-runtime-cleanup.v1",
  exact_root: root,
  writer_pids_stopped_before_cleanup: [28009, 28564, 28598, 28801, 28823],
  expected_marker: expected,
  rejected,
  cleanup_performed: true,
  exact_root_absent_after_cleanup: true,
  prohibited_pilot_contact: false
};
await mkdir(resolve(review, "evidence"), { recursive: true, mode: 0o700 });
await writeFile(resolve(review, "evidence/runtime_cleanup_resume_2_receipt.json"), `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ status: "PASS", rejected: rejected.length, root_absent: absent }));
