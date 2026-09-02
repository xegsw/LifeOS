#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const commit = 'f6c03b083efe4525005887dd1dd4dad423ca6d10';
const candidatePath = 'lifeos/engineering/LIFEOS-P3-144/candidate/build.rs';
const taskPath = 'lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md';

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function candidateBlob() {
  const result = spawnSync('git', ['show', `${commit}:${candidatePath}`], { encoding: 'utf8' });
  if (result.status !== 0) throw new Error('fixed candidate blob unavailable');
  return result.stdout;
}

function inspect(source, allowedRoot) {
  const runId = allowedRoot.match(/\/lifeos-p3-144-independent-review-([^/]+)$/)?.[1] ?? null;
  const min = source.match(/\((\d+)\.\.=48\)\.contains\(&value\.len\(\)\)/)?.[1];
  const profile = source.includes('"independent-review" =>');
  const dynamicRoot = source.includes('format!("{REVIEW_PREFIX}{run_id}")');
  const hasExactAllowedRoot = source.includes('lifeos-p3-144-independent-review-v1');
  const hasFixedV1RunId = source.includes('Some("v1".into())');
  const minimumRunIdLength = min ? Number(min) : null;
  const violations = [];
  if (!profile) violations.push('independent_review_profile_missing');
  if (minimumRunIdLength === null) violations.push('review_run_id_validation_missing');
  if (dynamicRoot && !hasExactAllowedRoot && !hasFixedV1RunId) violations.push('dynamic_unfrozen_review_root');
  if (minimumRunIdLength !== null && runId !== null && runId.length < minimumRunIdLength) {
    violations.push('frozen_v1_root_rejected_by_minimum_run_id');
  }
  return {
    allowedRoot,
    allowedRunId: runId,
    minimumRunIdLength,
    dynamicRoot,
    hasExactAllowedRoot,
    violations,
    verdict: violations.length ? 'P0_ROOT_AUTHORITY_CONFLICT' : 'NO_ROOT_CONFLICT'
  };
}

const task = readFileSync(taskPath, 'utf8');
const allowedRoot = task.match(/独立评审唯一临时根：`([^`]+)`/)?.[1];
if (!allowedRoot) throw new Error('frozen task root was not found');
const source = candidateBlob();
const cases = [
  { id: 'baseline_fixed_blob', result: inspect(source, allowedRoot), expected: 'P0_ROOT_AUTHORITY_CONFLICT' },
  {
    id: 'mutation_accepts_v1_length',
    result: inspect(
      source
        .replace('(8..=48).contains(&value.len())', '(2..=48).contains(&value.len())')
        .replace(
          'let review_run_id = env::var("LIFEOS_P3_144_REVIEW_RUN_ID").ok();',
          'let review_run_id = Some("v1".into());'
        ),
      allowedRoot
    ),
    expected: 'NO_ROOT_CONFLICT'
  },
  {
    id: 'mutation_removes_review_profile',
    result: inspect(source.replace('"independent-review" =>', '"removed-profile" =>'), allowedRoot),
    expected: 'P0_ROOT_AUTHORITY_CONFLICT'
  }
];
const passed = cases.every((entry) => entry.result.verdict === entry.expected);
console.log(JSON.stringify({
  schema: 'lifeos.p3-144.independent-review.root-contract.v1',
  candidateCommit: commit,
  candidatePath,
  candidateBlobSha256: sha256(source),
  taskPath,
  taskSha256: sha256(task),
  cases,
  passed
}, null, 2));
