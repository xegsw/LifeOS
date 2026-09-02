import childProcess from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [candidateRoot, reviewTmp, outputPath] = process.argv.slice(2);
if (!candidateRoot || !reviewTmp || !outputPath) throw new Error('usage: build_profile_mutations.mjs CANDIDATE_ROOT REVIEW_TMP OUTPUT');

const target = path.join(reviewTmp, 'cargo-target', 'build-profile-mutations');
const baseEnvironment = {
  ...process.env,
  CARGO_HOME: path.join(reviewTmp, 'cargo-home'),
  CARGO_TARGET_DIR: target,
  TMPDIR: path.join(reviewTmp, 'tmp'),
  CARGO_NET_OFFLINE: 'true',
  RUSTC: '/Users/xxe/.cargo/bin/rustc',
};

function invoke(name, profile, reviewRunId, extra = {}) {
  const env = { ...baseEnvironment, LIFEOS_P3_144_ROOT_PROFILE: profile, ...extra };
  if (reviewRunId === null) delete env.LIFEOS_P3_144_REVIEW_RUN_ID;
  else env.LIFEOS_P3_144_REVIEW_RUN_ID = reviewRunId;
  const result = childProcess.spawnSync('/Users/xxe/.cargo/bin/cargo', ['check', '--locked', '--offline'], {
    cwd: candidateRoot,
    env,
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });
  return {
    name,
    status: result.status,
    signal: result.signal,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

function locateBuildOutput(dir) {
  const build = path.join(dir, 'debug', 'build');
  for (const entry of fs.readdirSync(build, { withFileTypes: true })) {
    const output = path.join(build, entry.name, 'output');
    if (entry.isDirectory() && fs.existsSync(output) && fs.readFileSync(output, 'utf8').includes('LIFEOS_P3_144_COMPILED_RUN_MODE')) return output;
  }
  throw new Error('compiled build-script output not found');
}

const environmentOverride = invoke('synthetic_environment_cannot_promote_to_real', 'engineering', null, { LIFEOS_P3_144_RUN_MODE: 'real_gate' });
const buildOutput = fs.readFileSync(locateBuildOutput(target), 'utf8');
const unknownProfile = invoke('unknown_profile_build_time_rejected', 'unknown-profile', null);
const pilotReviewRunId = invoke('pilot_profile_with_review_run_id_build_time_rejected', 'pilot-7', 'delta-review-forbidden');

const assertions = {
  environment_override_exit_zero: environmentOverride.status === 0,
  compiled_profile_remains_engineering: buildOutput.includes('LIFEOS_P3_144_COMPILED_ROOT_PROFILE=engineering'),
  compiled_mode_remains_synthetic: buildOutput.includes('LIFEOS_P3_144_COMPILED_RUN_MODE=synthetic'),
  unknown_profile_exit_101: unknownProfile.status === 101,
  unknown_profile_message: /root profile must be engineering, independent-review, or pilot-7/.test(`${unknownProfile.stdout}${unknownProfile.stderr}`),
  pilot_review_run_id_exit_101: pilotReviewRunId.status === 101,
  pilot_review_run_id_message: /review run id is invalid for the pilot-7 root profile/.test(`${pilotReviewRunId.stdout}${pilotReviewRunId.stderr}`),
};
const logs = [environmentOverride, unknownProfile, pilotReviewRunId].map(({ name, status, signal, stdout, stderr }) => ({
  name,
  status,
  signal,
  output_tail: `${stdout}${stderr}`.split('\n').slice(-24).join('\n'),
}));
const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta.build-profile-mutations.v1',
  assertions,
  runs: logs,
  pass: Object.values(assertions).every(Boolean),
};
fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.pass) process.exitCode = 1;
