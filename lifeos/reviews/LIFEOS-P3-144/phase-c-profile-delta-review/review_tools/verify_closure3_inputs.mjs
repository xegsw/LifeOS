import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const [snapshotRoot, historyRoot, outputPath] = process.argv.slice(2);
if (!snapshotRoot || !historyRoot || !outputPath) throw new Error('usage: verify_closure3_inputs.mjs SNAPSHOT HISTORY OUTPUT');

const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const snapshotPath = (relative) => path.join(snapshotRoot, relative);
const historyPath = (relative) => path.join(historyRoot, relative);
const closureManifestPath = snapshotPath('lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json');
const manifest = JSON.parse(fs.readFileSync(closureManifestPath, 'utf8'));
const groups = ['candidate', 'fixed_inputs', 'preserved_history', 'closure_evidence'];
const failures = [];
const entries = [];

for (const group of groups) {
  for (const item of manifest[group] ?? []) {
    const file = item.path.startsWith('lifeos/reviews/') ? historyPath(item.path) : snapshotPath(item.path);
    const exists = fs.existsSync(file);
    const actual = exists ? sha256(file) : null;
    const pass = exists && actual === item.sha256;
    if (!pass) failures.push({ group, path: item.path, expected: item.sha256, actual, exists });
    entries.push({ group, path: item.path, expected: item.sha256, actual, pass });
  }
}

function walk(dir, base = dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(full, base);
    if (entry.isFile()) return [path.relative(base, full).split(path.sep).join('/')];
    return [];
  });
}

const candidateRoot = snapshotPath('lifeos/engineering/LIFEOS-P3-144/candidate');
const declaredCandidate = new Set((manifest.candidate ?? []).map((item) => item.path.replace('lifeos/engineering/LIFEOS-P3-144/candidate/', '')));
const actualCandidate = new Set(walk(candidateRoot));
const unexpectedCandidateFiles = [...actualCandidate].filter((relative) => !declaredCandidate.has(relative));
const missingCandidateFiles = [...declaredCandidate].filter((relative) => !actualCandidate.has(relative));
if (manifest.self_exclusion !== true) failures.push({ group: 'manifest', error: 'self_exclusion_not_true' });
if (unexpectedCandidateFiles.length || missingCandidateFiles.length) failures.push({ group: 'candidate_tree', unexpectedCandidateFiles, missingCandidateFiles });

const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta.closure3-input-verifier.v1',
  closure_manifest_sha256: sha256(closureManifestPath),
  manifest_schema: manifest.schema,
  manifest_self_exclusion: manifest.self_exclusion,
  group_counts: Object.fromEntries(groups.map((group) => [group, (manifest[group] ?? []).length])),
  candidate_tree: { declared: declaredCandidate.size, actual: actualCandidate.size, unexpectedCandidateFiles, missingCandidateFiles },
  entries,
  failures,
  pass: failures.length === 0,
};
fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.pass) process.exitCode = 1;
