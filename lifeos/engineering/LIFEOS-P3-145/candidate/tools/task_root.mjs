import { chmod, lstat, mkdir, readFile, readdir, rm, symlink, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const ROOT = "/private/tmp/lifeos-p3-145-engineering-v1";
const MARKER = ".lifeos-p3-145-owner.json";
const EXPECTED = { schema: "lifeos.p3-145.engineering-root.v1", task: "LIFEOS-P3-145", owner: "lifeos-p3-145-engineering-v1" };

const fail = (code) => { throw new Error(code); };
const markerPath = (root = ROOT) => `${root}/${MARKER}`;
const exactRoot = (root) => root === ROOT && dirname(root) === "/private/tmp" && resolve(root) === ROOT;
const mode = (stats) => Number(stats.mode & 0o777);
const canonicalPayload = (value) => JSON.stringify(value, Object.keys(value).sort());

async function verifyAt(root, { exact = true } = {}) {
  if ((exact && !exactRoot(root)) || (!exact && !root.startsWith(`${ROOT}/negative-`))) fail("root_literal_rejected");
  const directory = await lstat(root);
  if (!directory.isDirectory() || directory.isSymbolicLink() || mode(directory) !== 0o700) fail("root_type_rejected");
  const marker = await lstat(markerPath(root));
  if (!marker.isFile() || marker.isSymbolicLink() || mode(marker) !== 0o600) fail("marker_type_rejected");
  const parsed = JSON.parse(await readFile(markerPath(root), "utf8"));
  if (canonicalPayload(parsed) !== canonicalPayload(EXPECTED)) fail("marker_payload_rejected");
  return { root, marker: markerPath(root), entries: (await readdir(root)).sort() };
}

async function init() {
  if (!exactRoot(ROOT)) fail("root_literal_rejected");
  await mkdir(ROOT, { mode: 0o700, recursive: true });
  await chmod(ROOT, 0o700);
  try {
    await writeFile(markerPath(), `${JSON.stringify(EXPECTED)}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
  } catch (error) {
    if (error?.code !== "EEXIST") throw error;
  }
  return verifyAt(ROOT);
}

async function negatives() {
  await init();
  const wrong = `${ROOT}/negative-wrong-marker`;
  const link = `${ROOT}/negative-symlink`;
  await rm(wrong, { recursive: true, force: true });
  await mkdir(wrong, { mode: 0o700 });
  await writeFile(markerPath(wrong), `${JSON.stringify({ ...EXPECTED, task: "wrong" })}\n`, { mode: 0o600 });
  let wrongRejected = false;
  try { await verifyAt(wrong, { exact: false }); } catch (error) { wrongRejected = error.message === "marker_payload_rejected"; }
  await rm(wrong, { recursive: true, force: true });
  await rm(link, { recursive: true, force: true });
  await symlink(ROOT, link);
  let linkRejected = false;
  try { await verifyAt(link, { exact: false }); } catch (error) { linkRejected = error.message === "root_type_rejected"; }
  await rm(link, { force: true });
  if (!wrongRejected || !linkRejected) fail("negative_matrix_failed");
  return { wrong_marker: "rejected", symlink: "rejected", traversal: "rejected_by_exact_literal" };
}

async function cleanup() {
  const receipt = await verifyAt(ROOT);
  await rm(ROOT, { recursive: true, force: false, maxRetries: 0 });
  try { await lstat(ROOT); fail("cleanup_absence_failed"); } catch (error) { if (error?.code !== "ENOENT") throw error; }
  return { cleaned_root: ROOT, marker: receipt.marker, absence: true };
}

const command = process.argv[2];
const output = command === "init" ? await init()
  : command === "verify" ? await verifyAt(ROOT)
  : command === "negative" ? await negatives()
  : command === "cleanup" ? await cleanup()
  : fail("usage_init_verify_negative_cleanup");
console.log(JSON.stringify(output));
