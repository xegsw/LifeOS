import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = '/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1';
const REVIEW = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const EXPECTED_TOP_LEVEL = ['history', 'snapshot'];
const CONTROL_HASHES = {
  'test_design.md': '00b92b7e6ec5f36439737c8e0f6c94d180599187dbd97dfca42344e910b29c9a',
  'allowlist.md': '9be9d15be430e0cd93f04859ad911871f47ed006ff55e477859525e86c3552d8',
  'prohibited_paths.md': '74451ece56b785c4f246824643aa61c2417815ccde5108d8faf9c7a72c85eb4d',
  'PRECONTACT_SEAL.md': '0185fb8717d4e515254851c65efd7739732b80248bdab30f21043e3e77469e84'
};
const output = process.argv[2];
if (!output) throw new Error('usage: validate_recovery_root_v2.mjs OUTPUT_JSON');
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const failures = [];
const rootMetadata = fs.lstatSync(ROOT);
const realRoot = fs.realpathSync(ROOT);
if (path.dirname(ROOT) !== '/private/tmp' || realRoot !== ROOT || !rootMetadata.isDirectory() || rootMetadata.isSymbolicLink() || rootMetadata.uid !== process.getuid() || (rootMetadata.mode & 0o777) !== 0o700) failures.push('root_identity_or_permission_rejected');
const topLevel = fs.readdirSync(ROOT).sort();
if (JSON.stringify(topLevel) !== JSON.stringify(EXPECTED_TOP_LEVEL)) failures.push('residual_top_level_allowlist_rejected');
let nodesInspected = 0;
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const entry = path.join(dir, name);
    const metadata = fs.lstatSync(entry);
    nodesInspected += 1;
    if (metadata.isSymbolicLink()) failures.push(`symlink_rejected:${path.relative(ROOT, entry)}`);
    if (metadata.isDirectory() && !metadata.isSymbolicLink()) walk(entry);
  }
}
walk(ROOT);
const controls = Object.fromEntries(Object.entries(CONTROL_HASHES).map(([relative, expected]) => {
  const actual = sha256(path.join(REVIEW, relative));
  if (actual !== expected) failures.push(`control_hash_mismatch:${relative}`);
  return [relative, { expected, actual, pass: actual === expected }];
}));
const snapshot = path.join(ROOT, 'snapshot');
const history = path.join(ROOT, 'history');
const closure = JSON.parse(fs.readFileSync(path.join(snapshot, 'lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json'), 'utf8'));
let closureEntries = 0;
for (const group of ['candidate', 'fixed_inputs', 'preserved_history', 'closure_evidence']) {
  for (const item of closure[group] ?? []) {
    const source = path.join(item.path.startsWith('lifeos/reviews/') ? history : snapshot, item.path);
    closureEntries += 1;
    if (sha256(source) !== item.sha256) failures.push(`closure_input_hash_mismatch:${item.path}`);
  }
}
const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta.recovery-root-validation.v2',
  root: ROOT,
  real_root: realRoot,
  root_mode_octal: (rootMetadata.mode & 0o777).toString(8),
  root_uid: rootMetadata.uid,
  current_uid: process.getuid(),
  top_level: topLevel,
  expected_top_level: EXPECTED_TOP_LEVEL,
  nodes_inspected: nodesInspected,
  controls,
  closure_entries_verified: closureEntries,
  failures,
  pass: failures.length === 0
};
fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.pass) process.exitCode = 1;
