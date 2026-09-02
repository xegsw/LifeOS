import childProcess from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const reviewRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const workspace = path.resolve(reviewRoot, '../../../..');
const manifestPath = path.join(reviewRoot, 'FINAL_MANIFEST.json');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const sha256 = (content) => crypto.createHash('sha256').update(content).digest('hex');
const git = (args) => {
  const run = childProcess.spawnSync('/usr/bin/git', ['-C', workspace, ...args], { encoding: null, maxBuffer: 20 * 1024 * 1024 });
  if (run.status !== 0) throw new Error(`git command failed: ${args.join(' ')}`);
  return run.stdout;
};
const commit = manifest.candidate.commit;
const failures = [];
const evidence = [];

if (manifest.self_exclusion !== true) failures.push('self_exclusion_not_true');
for (const excluded of manifest.excluded_paths ?? []) {
  if ((manifest.review_evidence ?? []).some((entry) => entry.path === excluded)) failures.push(`excluded_path_included:${excluded}`);
}
for (const entry of manifest.review_evidence ?? []) {
  const target = path.join(reviewRoot, entry.path);
  const actual = fs.existsSync(target) ? sha256(fs.readFileSync(target)) : null;
  const pass = actual === entry.sha256;
  if (!pass) failures.push(`review_evidence_mismatch:${entry.path}`);
  evidence.push({ path: entry.path, expected: entry.sha256, actual, pass });
}

const resolvedCommit = git(['rev-parse', `${commit}^{commit}`]).toString('utf8').trim();
if (resolvedCommit !== commit) failures.push('candidate_commit_mismatch');
const closurePath = manifest.candidate.closure_3_manifest_path;
const closureBytes = git(['show', `${commit}:${closurePath}`]);
if (sha256(closureBytes) !== manifest.candidate.closure_3_manifest_sha256) failures.push('closure3_manifest_hash_mismatch');
const closure = JSON.parse(closureBytes.toString('utf8'));
const candidateEntries = closure.candidate ?? [];
const aggregate = candidateEntries.slice().sort((a, b) => a.path.localeCompare(b.path)).map((entry) => `${entry.path}\0${entry.sha256}\n`).join('');
if (candidateEntries.length !== manifest.candidate.candidate_entry_count) failures.push('candidate_entry_count_mismatch');
if (sha256(aggregate) !== manifest.candidate.candidate_digest_sha256) failures.push('candidate_digest_mismatch');
for (const group of ['candidate', 'fixed_inputs', 'preserved_history', 'closure_evidence']) {
  for (const entry of closure[group] ?? []) {
    const actual = sha256(git(['show', `${commit}:${entry.path}`]));
    if (actual !== entry.sha256) failures.push(`closure_input_mismatch:${entry.path}`);
  }
}
const taskActual = sha256(git(['show', `${commit}:${manifest.candidate.task_contract_path}`]));
if (taskActual !== manifest.candidate.task_contract_sha256) failures.push('task_contract_hash_mismatch');

const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta-review.final-manifest-verifier.v1',
  integrity_pass: failures.length === 0,
  review_outcome: manifest.review_outcome,
  candidate_commit: resolvedCommit,
  review_evidence_count: evidence.length,
  evidence,
  failures
};
fs.writeFileSync(path.join(reviewRoot, 'final_manifest_verification.json'), `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (failures.length) process.exitCode = 1;
