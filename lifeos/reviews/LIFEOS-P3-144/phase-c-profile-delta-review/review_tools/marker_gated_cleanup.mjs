import fs from 'node:fs';
import path from 'node:path';

const ROOT = '/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1';
const MARKER = '.lifeos-p3-144-review-marker';
const MARKER_CONTENT = 'LIFEOS-P3-144 phase-c-profile-delta-review v1\nowner=independent-review\nrun_id=phase-c-profile-delta-review-v1\n';
const [mode, markerName, outputPath] = process.argv.slice(2);
if (!['reject', 'cleanup'].includes(mode) || !markerName || !outputPath) throw new Error('usage: marker_gated_cleanup.mjs reject|cleanup MARKER_NAME OUTPUT');

function receipt(result) {
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
}

function reject(reason) {
  receipt({ schema: 'lifeos.p3-144.phase-c-profile-delta.marker-cleanup.v1', mode, root: ROOT, marker_name: markerName, result: 'rejected', reason, root_removed: false });
  process.exit(2);
}

if (path.dirname(ROOT) !== '/private/tmp' || path.basename(ROOT) !== 'lifeos-p3-144-phase-c-profile-delta-review-v1') reject('literal_root_identity_rejected');
if (markerName !== MARKER) reject('marker_name_rejected');
let rootMetadata;
let markerMetadata;
try {
  rootMetadata = fs.lstatSync(ROOT);
  markerMetadata = fs.lstatSync(path.join(ROOT, MARKER));
} catch {
  reject('root_or_marker_missing');
}
if (!rootMetadata.isDirectory() || rootMetadata.isSymbolicLink()) reject('root_type_rejected');
if (!markerMetadata.isFile() || markerMetadata.isSymbolicLink() || markerMetadata.nlink !== 1 || (markerMetadata.mode & 0o777) !== 0o600) reject('marker_metadata_rejected');
if (fs.readFileSync(path.join(ROOT, MARKER), 'utf8') !== MARKER_CONTENT) reject('marker_content_rejected');
if (mode === 'reject') reject('expected_rejection_mode');
fs.rmSync(ROOT, { recursive: true, force: false });
const removed = !fs.existsSync(ROOT);
receipt({ schema: 'lifeos.p3-144.phase-c-profile-delta.marker-cleanup.v1', mode, root: ROOT, marker_name: markerName, result: removed ? 'cleaned' : 'failed', root_removed: removed });
if (!removed) process.exitCode = 1;
