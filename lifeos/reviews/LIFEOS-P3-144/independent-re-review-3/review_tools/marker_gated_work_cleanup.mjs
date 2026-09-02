import { chmod, lstat, readFile, rm, symlink, unlink, writeFile } from "node:fs/promises";

const root = "/Users/xxe/.codex/worktrees/eb73/No.2/lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/work";
const expected = "lifeos-p3-144-independent-re-review-3-work-v1\n";
const markerName = ".review-work-marker";
const markerPath = `${root}/${markerName}`;
const mode = process.argv[2];
async function check(path) {
  const rootStat = await lstat(root);
  if (!rootStat.isDirectory() || rootStat.isSymbolicLink()) throw new Error("root_type_rejected");
  const markerStat = await lstat(path);
  if (!markerStat.isFile() || markerStat.isSymbolicLink()) throw new Error("marker_type_rejected");
  if ((markerStat.mode & 0o777) !== 0o600) throw new Error("marker_permission_rejected");
  if ((await readFile(path, "utf8")) !== expected) throw new Error("marker_payload_rejected");
}
if (mode === "probe-missing") {
  try { await check(`${root}/.missing-marker`); } catch (error) { console.log(JSON.stringify({ status: "PASS", probe: "missing_marker_rejected", code: error.code === "ENOENT" ? "marker_missing" : error.message })); process.exit(0); }
  throw new Error("missing_marker_was_not_rejected");
}
if (mode === "probe-symlink") {
  const link = `${root}/.symlink-marker`;
  await symlink(markerPath, link);
  try { await check(link); } catch (error) { console.log(JSON.stringify({ status: "PASS", probe: "symlink_marker_rejected", code: error.message })); await unlink(link); process.exit(0); }
  await unlink(link);
  throw new Error("symlink_marker_was_not_rejected");
}
if (mode === "probe-wrong") {
  const wrong = `${root}/.wrong-marker`;
  await writeFile(wrong, "wrong-owner\n", { mode: 0o600 });
  await chmod(wrong, 0o600);
  try { await check(wrong); } catch (error) { console.log(JSON.stringify({ status: "PASS", probe: "wrong_marker_rejected", code: error.message })); await unlink(wrong); process.exit(0); }
  await unlink(wrong);
  throw new Error("wrong_marker_was_not_rejected");
}
if (mode !== "cleanup") throw new Error("mode must be probe-missing, probe-wrong, probe-symlink, or cleanup");
await check(markerPath);
await rm(root, { recursive: true, force: false, maxRetries: 0 });
console.log(JSON.stringify({ status: "PASS", cleanup: "review_owned_work_removed", root }));
