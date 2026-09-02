import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = '/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1';
const REVIEW = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const HISTORY_PREFIX = 'lifeos/reviews/';
const EXPECTED_TOP_LEVEL = ['cargo-home', 'cargo-target', 'history', 'mutations', 'snapshot', 'tmp'];
const CONTROL_HASHES = {
  'test_design.md': '00b92b7e6ec5f36439737c8e0f6c94d180599187dbd97dfca42344e910b29c9a',
  'allowlist.md': '9be9d15be430e0cd93f04859ad911871f47ed006ff55e477859525e86c3552d8',
  'prohibited_paths.md': '74451ece56b785c4f246824643aa61c2417815ccde5108d8faf9c7a72c85eb4d',
  'PRECONTACT_SEAL.md': '0185fb8717d4e515254851c65efd7739732b80248bdab30f21043e3e77469e84'
};
const output = process.argv[2];
if (!output) throw new Error('usage: validate_recovery_root.mjs OUTPUT_JSON');
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const failures = [];
const rootMeta = fs.lstatSync(ROOT);
const realRoot = fs.realpathSync(ROOT);
if (path.dirname(ROOT) !== '/private/tmp' || realRoot !== ROOT || !rootMeta.isDirectory() || rootMeta.isSymbolicLink()) failures.push('root_identity_rejected');
if (rootMeta.uid !== process.getuid()) failures.push('root_owner_rejected');
const topLevel = fs.readdirSync(ROOT).sort();
if (JSON.stringify(topLevel) !== JSON.stringify(EXPECTED_TOP_LEVEL)) failures.push('top_level_allowlist_rejected');
let nodes = 0;
function inspect(dir) {
  for (const name of fs.readdirSync(dir)) {
    const entry = path.join(dir, name);
    const metadata = fs.lstatSync(entry);
    nodes += 1;
    if (metadata.isSymbolicLink()) failures.push(`symlink_rejected:${path.relative(ROOT, entry)}`);
    if (metadata.isDirectory() && !metadata.isSymbolicLink()) inspect(entry);
  }
}
inspect(ROOT);
const controls = Object.fromEntries(Object.entries(CONTROL_HASHES).map(([relative, expected]) => {
  const actual = sha256(path.join(REVIEW, relative));
  if (actual !== expected) failures.push(`control_hash_mismatch:${relative}`);
  return [relative, { expected, actual, pass: actual === expected }];
}));
const snapshot = path.join(ROOT, 'snapshot');
const history = path.join(ROOT, 'history');
const closureManifest = JSON.parse(fs.readFileSync(path.join(snapshot, 'lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json'), 'utf8'));
let closureEntries = 0;
for (const group of ['candidate', 'fixed_inputs', 'preserved_history', 'closure_evidence']) {
  for (const item of closureManifest[group] ?? []) {
    const base = item.path.startsWith(HISTORY_PREFIX) ? history : snapshot;
    const actual = sha256(path.join(base, item.path));
    closureEntries += 1;
    if (actual !== item.sha256) failures.push(`closure_input_hash_mismatch:${item.path}`);
  }
}
const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta.recovery-root-validation.v1',
  root: ROOT,
  real_root: realRoot,
  root_mode_octal: (rootMeta.mode & 0o777).toString(8),
  root_uid: rootMeta.uid,
  current_uid: process.getuid(),
  top_level: topLevel,
  expected_top_level: EXPECTED_TOP_LEVEL,
  nodes_inspected: nodes,
  controls,
  closure_entries_verified: closureEntries,
  failures,
  pass: failures.length === 0
};
fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.pass) process.exitCode = 1;
