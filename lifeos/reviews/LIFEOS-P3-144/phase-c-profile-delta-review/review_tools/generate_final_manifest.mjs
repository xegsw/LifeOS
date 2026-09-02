import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const reviewRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const reviewFiles = [
  'PRECONTACT_HASHES.md',
  'PRECONTACT_SEAL.md',
  'allowlist.md',
  'checkpoint.json',
  'environment_incident.md',
  'evidence_build_profile_mutations.json',
  'evidence_closure3_input_verification.json',
  'evidence_closure3_posttest_verification.json',
  'evidence_missing_marker_cleanup_rejection.json',
  'evidence_recovery_cleanup_v2_receipt.json',
  'evidence_recovery_root_validation.json',
  'evidence_recovery_root_validation_v2.json',
  'evidence_static_delta_audit.json',
  'evidence_wrong_marker_rejection.json',
  'governance_guard.log',
  'offline_contract.log',
  'pilot_7_compile_only.log',
  'prohibited_paths.md',
  'review_matrix.json',
  'rust_engineering_serial.log',
  'rust_engineering_serial_resume.log',
  'rust_independent_review_serial.log',
  'test_design.md',
  'review_tools/build_profile_mutations.mjs',
  'review_tools/marker_gated_cleanup.mjs',
  'review_tools/recovery_marker_gated_cleanup.mjs',
  'review_tools/recovery_marker_gated_cleanup_v2.mjs',
  'review_tools/static_delta_audit.mjs',
  'review_tools/validate_recovery_root.mjs',
  'review_tools/validate_recovery_root_v2.mjs',
  'review_tools/verify_closure3_inputs.mjs'
];
const missing = reviewFiles.filter((relative) => !fs.existsSync(path.join(reviewRoot, relative)));
if (missing.length) throw new Error(`manifest inputs missing: ${missing.join(', ')}`);
const manifest = {
  schema: 'lifeos.p3-144.phase-c-profile-delta-review.final-manifest.v1',
  self_exclusion: true,
  excluded_paths: ['FINAL_MANIFEST.json', 'final_manifest_verification.json', 'independent_review.md', 'review_tools/generate_final_manifest.mjs', 'review_tools/verify_final_manifest.mjs'],
  candidate: {
    commit: '777af31ec88751661ada34aa13343aabf77b6609',
    closure_3_manifest_path: 'lifeos/engineering/LIFEOS-P3-144/closure-3/FINAL_MANIFEST.json',
    closure_3_manifest_sha256: '86040e7f57d810fd065a74180ac9be9c8ef212193b8b083762b13eae0f8b04f7',
    candidate_entry_count: 85,
    candidate_digest_sha256: '40ac45b249dd9df893dae9d3ed2e51c21c82c923d00b49b898517b8f2a9f9290',
    task_contract_path: 'lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md',
    task_contract_sha256: '77ffb9438807c37362608d2bca1c315a4ea8a222d4ec8a0c543fcc84158466ac'
  },
  review_evidence: reviewFiles.map((relative) => ({ path: relative, sha256: sha256(path.join(reviewRoot, relative)) })),
  review_outcome: {
    status: 'PASS',
    counts: { P0: 0, P1: 0, P2: 1, Unknown: 0, NotImplemented: 0 },
    blocking_row: null,
    candidate_finding: false
  }
};
fs.writeFileSync(path.join(reviewRoot, 'FINAL_MANIFEST.json'), `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
