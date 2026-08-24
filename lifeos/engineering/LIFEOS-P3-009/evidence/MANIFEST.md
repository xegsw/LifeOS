# LIFEOS-P3-009 Evidence Manifest

- Fixture: `lifeos-p3-009-synthetic-v1` (synthetic-disposable)
- Runtime: Node `v24.19.0`, built-in `node:sqlite`
- Re-run: `cd lifeos/engineering/LIFEOS-P3-009 && node scripts/validate.mjs`
- Run at: `2026-08-13T04:44:06.081Z`
- Content snapshot SHA-256: `4d28b22d29c412fa335e30919d552c294405d313c1314a9d4837e88afe269159`
- Result: **37 PASS / 0 FAIL; TOTAL FAIL = 0; P0 FAIL = 0; P1 FAIL = 0; P2 FAIL = 0; existing 34-test regression = 34/34 PASS; P2 cleanup = 3/3 PASS; P1-3/P1-5 migration = 4/4 PASS; P3-015 regression = 1/1 PASS; P1-4 generation staling = 2/2 PASS; P1-8 suggestion ID binding = 4/4 PASS; P1-6 restore candidates = 5/5 PASS; P1-7 authorization expiry / feedback retraction = 4/4 PASS**
- Scope: synthetic, local, single-process TypeScript/SQLite skeleton; not real Tauri, Vault, filesystem export, cloud/model, vector, sync, L3, external user, production packaging or SLA.

## Evidence files

- `test_results.json`: machine-readable environment, result, snapshot and file hashes.
- `test_run.log`: raw Node test output.
- `invariant_migration_matrix.md`: H1-H9 / T-ARCH executable, mapped and unmigrated status.
- `default_off_matrix.md`: config and runtime-negative closure matrix.
- `architecture_conformance.md`: frozen-contract inheritance and remaining boundaries.

## P3-022 cleanup semantics

- Feedback IDs are insert-once: duplicate, conflicting and post-retraction writes fail closed without changing `user_text` or `status`.
- `fail` and `total_fail` count all failures; `p0_fail`, `p1_fail` and `p2_fail` count only failed test titles beginning with the matching severity prefix. Any failure still exits nonzero.
- `derivation.evidence_version_id` is retained only as a legacy compatibility/display pointer. `derivation_input` / exported `inputs` is the complete authoritative set for consumption, export inclusion and restore-candidate evaluation.

This manifest is engineering evidence, not PM Review, acceptance, freeze, capability enablement or stage advancement.
