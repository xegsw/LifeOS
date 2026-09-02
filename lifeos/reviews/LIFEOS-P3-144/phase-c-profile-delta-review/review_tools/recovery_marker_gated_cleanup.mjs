import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = '/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1';
const REVIEW = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const MARKER = 'recovery-cleanup-marker.json';
const EXPECTED_TOP_LEVEL = ['cargo-home', 'cargo-target', 'history', 'mutations', 'recovery-cleanup-marker.json', 'snapshot', 'tmp'];
const EXPECTED_MARKER = {
  allowlist_sha256: '9be9d15be430e0cd93f04859ad911871f47ed006ff55e477859525e86c3552d8',
  candidate_commit: '777af31ec88751661ada34aa13343aabf77b6609',
  checkpoint_sha256: '53d00fe07ad816dae4c604175a43785cb56978f8a7dc71ead73d84344dbb77b9',
  recovery_validation_sha256: '0cfd1bf2462612ac273a1862c599e82e96468193c0afabe13150cd5b63d0bb87',
  review: 'phase-c-profile-delta-review',
  root: ROOT,
  schema: 'lifeos.p3-144.phase-c-profile-delta.recovery-cleanup-marker.v1',
  task: 'LIFEOS-P3-144'
};
const CONTROL_HASHES = {
  'test_design.md': '00b92b7e6ec5f36439737c8e0f6c94d180599187dbd97dfca42344e910b29c9a',
  'allowlist.md': '9be9d15be430e0cd93f04859ad911871f47ed006ff55e477859525e86c3552d8',
  'prohibited_paths.md': '74451ece56b785c4f246824643aa61c2417815ccde5108d8faf9c7a72c85eb4d',
  'PRECONTACT_SEAL.md': '0185fb8717d4e515254851c65efd7739732b80248bdab30f21043e3e77469e84'
};
const output = process.argv[2];
if (!output) throw new Error('usage: recovery_marker_gated_cleanup.mjs OUTPUT_JSON');
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const failures = [];
function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return value;
}
const rootMetadata = fs.lstatSync(ROOT);
if (path.dirname(ROOT) !== '/private/tmp' || fs.realpathSync(ROOT) !== ROOT || !rootMetadata.isDirectory() || rootMetadata.isSymbolicLink() || rootMetadata.uid !== process.getuid() || (rootMetadata.mode & 0o777) !== 0o700) failures.push('root_identity_or_permission_rejected');
const topLevel = fs.readdirSync(ROOT).sort();
if (JSON.stringify(topLevel) !== JSON.stringify(EXPECTED_TOP_LEVEL)) failures.push('top_level_allowlist_rejected');
let nodesInspected = 0;
function noSymlinks(dir) {
  for (const name of fs.readdirSync(dir)) {
    const target = path.join(dir, name);
    const metadata = fs.lstatSync(target);
    nodesInspected += 1;
    if (metadata.isSymbolicLink()) failures.push(`symlink_rejected:${path.relative(ROOT, target)}`);
    if (metadata.isDirectory() && !metadata.isSymbolicLink()) noSymlinks(target);
  }
}
noSymlinks(ROOT);
const markerPath = path.join(ROOT, MARKER);
const markerMetadata = fs.lstatSync(markerPath);
if (!markerMetadata.isFile() || markerMetadata.isSymbolicLink() || markerMetadata.nlink !== 1 || (markerMetadata.mode & 0o777) !== 0o600) failures.push('recovery_marker_metadata_rejected');
const marker = JSON.parse(fs.readFileSync(markerPath, 'utf8'));
if (JSON.stringify(stable(marker)) !== JSON.stringify(stable(EXPECTED_MARKER))) failures.push('recovery_marker_content_rejected');
for (const [relative, expected] of Object.entries(CONTROL_HASHES)) {
  if (sha256(path.join(REVIEW, relative)) !== expected) failures.push(`control_hash_mismatch:${relative}`);
}
if (sha256(path.join(REVIEW, 'checkpoint.json')) !== EXPECTED_MARKER.checkpoint_sha256) failures.push('checkpoint_binding_rejected');
if (sha256(path.join(REVIEW, 'evidence_recovery_root_validation.json')) !== EXPECTED_MARKER.recovery_validation_sha256) failures.push('recovery_validation_binding_rejected');
const snapshot = path.join(ROOT, 'snapshot');
const history = path.join(ROOT, 'history');
const closure = JSON.parse(fs.readFileSync(path.join(snapshot, 'lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json'), 'utf8'));
let closureEntries = 0;
for (const group of ['candidate', 'fixed_inputs', 'preserved_history', 'closure_evidence']) {
  for (const entry of closure[group] ?? []) {
    const source = path.join(entry.path.startsWith('lifeos/reviews/') ? history : snapshot, entry.path);
    closureEntries += 1;
    if (sha256(source) !== entry.sha256) failures.push(`closure_input_hash_mismatch:${entry.path}`);
  }
}
const before = { root: ROOT, top_level: topLevel, nodes_inspected: nodesInspected, closure_entries_verified: closureEntries, failures };
if (failures.length) {
  fs.writeFileSync(output, `${JSON.stringify({ schema: 'lifeos.p3-144.phase-c-profile-delta.recovery-cleanup.v1', result: 'rejected', root_removed: false, before }, null, 2)}\n`, { mode: 0o600 });
  process.exitCode = 1;
} else {
  fs.rmSync(ROOT, { recursive: true, force: false });
  const removed = !fs.existsSync(ROOT);
  fs.writeFileSync(output, `${JSON.stringify({ schema: 'lifeos.p3-144.phase-c-profile-delta.recovery-cleanup.v1', result: removed ? 'cleaned' : 'failed', root_removed: removed, recovery_marker: EXPECTED_MARKER, before }, null, 2)}\n`, { mode: 0o600 });
  if (!removed) process.exitCode = 1;
}
