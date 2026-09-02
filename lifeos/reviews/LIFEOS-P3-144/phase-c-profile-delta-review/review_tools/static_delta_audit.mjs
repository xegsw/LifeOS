import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const [snapshotRoot, outputPath] = process.argv.slice(2);
if (!snapshotRoot || !outputPath) throw new Error('usage: static_delta_audit.mjs SNAPSHOT_ROOT OUTPUT_JSON');

const candidate = path.join(snapshotRoot, 'lifeos/engineering/LIFEOS-P3-144/candidate');
const read = (relative) => fs.readFileSync(path.join(candidate, relative), 'utf8');
const build = read('build.rs');
const runtime = read('src/runtime.rs');
const deepseek = read('src/deepseek.rs');
const offlineContract = read('tests/offline_contract.mjs');
const main = read('src/main.rs');

const exactIpc = [
  'capture_record', 'get_today', 'runtime_status', 'confirm_capture_context',
  'get_context_recovery', 'get_context_next_action', 'decide_context_next_action',
  'record_action_result', 'assemble_global_ai_context', 'get_evidence_backed_understanding',
  'decide_understanding_feedback', 'get_ai_provider_settings', 'save_ai_provider_settings',
  'save_ai_provider_credential', 'test_ai_provider_connection', 'set_ai_provider_enabled',
  'upsert_durable_memory', 'update_current_state', 'resolve_request_context',
  'get_context_disclosure_receipt',
];

function requireMatch(source, pattern, name, errors) {
  if (!pattern.test(source)) errors.push(name);
}

function validate({ buildSource, runtimeSource, deepseekSource, contractSource, mainSource }) {
  const errors = [];
  requireMatch(buildSource, /const PILOT_PARENT: &str = "\/Users\/xxe\/Documents";/, 'pilot_parent_not_exact', errors);
  requireMatch(buildSource, /const PILOT_BASENAME: &str = "LifeOS-Self-Use-Pilot-7";/, 'pilot_basename_not_exact', errors);
  requireMatch(buildSource, /const PILOT_RUN_ID: &str = "pilot-7";/, 'pilot_run_id_not_exact', errors);
  requireMatch(buildSource, /"lifeos\.p3-144\.pilot-7-root\.v1"/, 'pilot_marker_schema_missing', errors);
  requireMatch(buildSource, /"lifeos-p3-144-pilot-7"/, 'pilot_marker_owner_missing', errors);
  requireMatch(buildSource, /"real_gate"\.to_owned\(\)/, 'pilot_real_gate_not_compiled', errors);
  requireMatch(buildSource, /"pilot-7"\s*=>\s*\{[\s\S]*?if review_run_id\.is_some\(\)\s*\{[\s\S]*?panic!\("review run id is invalid for the pilot-7 root profile"\)/, 'pilot_review_run_id_not_rejected_at_build', errors);
  requireMatch(buildSource, /_ => panic!\("root profile must be engineering, independent-review, or pilot-7"\)/, 'unknown_profile_not_rejected_at_build', errors);

  const runMode = runtimeSource.match(/fn run_mode\(\) -> &'static str \{([\s\S]*?)\n\}/)?.[1] ?? '';
  requireMatch(runMode, /env!\("LIFEOS_P3_144_COMPILED_RUN_MODE"\)/, 'run_mode_not_compile_time_bound', errors);
  if (/std::env::var|env::var/.test(runMode)) errors.push('run_mode_runtime_env_override_possible');
  const rootAuthority = runtimeSource.match(/fn compiled_root_authority\(\) -> RootAuthority \{([\s\S]*?)\n\}/)?.[1] ?? '';
  requireMatch(rootAuthority, /env!\("LIFEOS_P3_144_COMPILED_ROOT_PROFILE"\)/, 'root_profile_not_compile_time_bound', errors);
  requireMatch(rootAuthority, /env!\("LIFEOS_P3_144_COMPILED_ROOT"\)/, 'root_not_compile_time_bound', errors);
  const verifyRoot = runtimeSource.match(/fn verify_task_root\(\) -> Result<PathBuf, ApiError> \{([\s\S]*?)\n\}/)?.[1] ?? '';
  const modeIndex = verifyRoot.indexOf('run_mode_matches_profile');
  const rootIndex = verifyRoot.indexOf('verify_authorized_root');
  if (modeIndex < 0 || rootIndex < 0 || modeIndex > rootIndex) errors.push('profile_mode_not_rejected_before_root_access');
  const runFunction = runtimeSource.match(/pub fn run\(\) \{([\s\S]*?)\n\}/)?.[1] ?? '';
  const verifyIndex = runFunction.indexOf('verify_task_root');
  const initIndex = runFunction.indexOf('initialize_store');
  if (verifyIndex < 0 || initIndex < 0 || verifyIndex > initIndex) errors.push('root_not_verified_before_database_initialization');
  const resolveRequest = runtimeSource.match(/fn resolve_request_context\([\s\S]*?\n\}/)?.[0] ?? '';
  const confirmationIndex = resolveRequest.indexOf('consume_confirmation');
  const keyIndex = resolveRequest.indexOf('load_api_key_string');
  if (confirmationIndex < 0 || keyIndex < 0 || confirmationIndex > keyIndex) errors.push('confirmation_not_verified_before_provider_material');

  for (const ipc of exactIpc) {
    if (!runtimeSource.includes(`"${ipc}"`)) errors.push(`ipc_missing_${ipc}`);
  }
  const ipcBlock = runtimeSource.match(/const IPC: \[&str; 20\] = \[([\s\S]*?)\];/)?.[1] ?? '';
  const discoveredIpc = [...ipcBlock.matchAll(/"([a-z_]+)"/g)].map((match) => match[1]);
  if (discoveredIpc.length !== 20 || JSON.stringify(discoveredIpc) !== JSON.stringify(exactIpc)) errors.push('ipc_list_drift');
  requireMatch(deepseekSource, /pub const AUTHORITY: &str = "https:\/\/api\.deepseek\.com";/, 'deepseek_authority_drift', errors);
  if (!/--noproxy/.test(deepseekSource) || !/--proto-redir/.test(deepseekSource) || !/--max-redirs/.test(deepseekSource)) errors.push('authority_fail_closed_guards_missing');
  if (!/HealthFitness|health.*current.?state|current.?state.*health/is.test(runtimeSource)) errors.push('health_current_state_contract_missing');
  if (!/save_ai_provider_credential/.test(runtimeSource) || !/get_context_disclosure_receipt/.test(runtimeSource)) errors.push('credential_or_disclosure_registration_missing');
  if (!/pilot-7/.test(contractSource) || !/real_gate/.test(contractSource) || !/ipc_count/.test(contractSource)) errors.push('offline_contract_delta_guard_missing');
  return errors;
}

const pristineErrors = validate({ buildSource: build, runtimeSource: runtime, deepseekSource: deepseek, contractSource: offlineContract, mainSource: main });
const mutations = [
  ['pilot_parent', { buildSource: build.replace('/Users/xxe/Documents', '/private/tmp') }, 'pilot_parent_not_exact'],
  ['pilot_mode', { buildSource: build.replace('"real_gate".to_owned()', '"synthetic".to_owned()') }, 'pilot_real_gate_not_compiled'],
  ['runtime_mode_env', { runtimeSource: runtime.replace('env!("LIFEOS_P3_144_COMPILED_RUN_MODE")', 'std::env::var("LIFEOS_P3_144_RUN_MODE").unwrap().leak()') }, 'run_mode_not_compile_time_bound'],
  ['root_gate_order', { runtimeSource: runtime.replace('if !run_mode_matches_profile(&authority.profile, run_mode()) {', 'if false {') }, 'profile_mode_not_rejected_before_root_access'],
  ['pilot_run_id', { buildSource: build.replace('if review_run_id.is_some() {\n                    panic!("review run id is invalid for the pilot-7 root profile");\n                }', '') }, 'pilot_review_run_id_not_rejected_at_build'],
  ['ipc_removed', { runtimeSource: runtime.replace('"get_context_disclosure_receipt",', '') }, 'ipc_missing_get_context_disclosure_receipt'],
];

const mutationResults = mutations.map(([name, overrides, expectedError]) => {
  const errors = validate({
    buildSource: overrides.buildSource ?? build,
    runtimeSource: overrides.runtimeSource ?? runtime,
    deepseekSource: deepseek,
    contractSource: offlineContract,
    mainSource: main,
  });
  return { name, detected: errors.includes(expectedError), expected_error: expectedError, errors };
});

const result = {
  schema: 'lifeos.p3-144.phase-c-profile-delta.static-audit.v1',
  candidate_sha256: Object.fromEntries(['build.rs', 'src/runtime.rs', 'src/deepseek.rs', 'src/main.rs', 'tests/offline_contract.mjs'].map((relative) => [relative, crypto.createHash('sha256').update(read(relative)).digest('hex')])),
  pristine: { pass: pristineErrors.length === 0, errors: pristineErrors },
  mutations: mutationResults,
  pass: pristineErrors.length === 0 && mutationResults.every((entry) => entry.detected),
};
fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
if (!result.pass) process.exitCode = 1;
