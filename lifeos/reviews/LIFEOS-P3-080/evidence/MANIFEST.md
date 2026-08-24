# LIFEOS-P3-080 Independent Evidence Manifest

Created 2026-08-21. All implementation inputs were read-only. The runner is
new for this review and invokes only the task-local copied CLI; it does not
import, call, or copy P3-079 `tests/`, `run_self_check.py`, or
`run_rework_self_check.py`.

## Reproduction

```bash
task_copy=$(mktemp -d /private/tmp/lifeos-p3-080.XXXXXX)
cp -R lifeos/engineering/LIFEOS-P3-079 "$task_copy/LIFEOS-P3-079"
python3 lifeos/reviews/LIFEOS-P3-080/evidence/independent_blackbox_runner.py \
  --target "$task_copy/LIFEOS-P3-079" \
  --evidence lifeos/reviews/LIFEOS-P3-080/evidence
```

Expected result: `{"passed": 12, "failed": 0}`. The runner makes and removes
its own synthetic SQLite scratch directory. The copied target may then be
removed; no project engineering asset is written.

## Artifacts and SHA-256

| Artifact | SHA-256 |
|---|---|
| `independent_blackbox_runner.py` | `340fc7d7a1f9e6cc2ecb16250406929129ba57c937ee6cd45dbbb28ba468a4f2` |
| `independent_results.json` | `c0bc3d6dc813f95a5a4df6a1862632491299fbabb5748a087dc9177c73bce6ed` |
| `independent_snapshot.json` | `ece8888807f21a84426f6d2c0da21825dcbefbe43150fddf624f83e6f2d52ae3` |
| `independent_runner.log` | `a3dafd6f7a8d86a9fc5f2c81486a9941db2287364c4fbe3d0351a180c7425c93` |
| P3-079 `src/integrated_runtime.py` | `19d337a560cfa3e6098571b29a71fc121e059db1c0914e3e3f58f3f740905788` |
| P3-079 `scripts/operator_cli.py` | `a2fda42bcabfb409fa28f05d383f8308cefae496de4a2465295e4284325ae45a` |
| P3-079 Rework Manifest | `358f668855608fdd72f0cd8fc14934fd92f7aeaf2d637912d632bea7dc9cd8dd` |

The two P3-079 source hashes agree with its Rework Manifest. The complete
Python-file hash snapshot is in `independent_snapshot.json`; no historical
input, parent Evidence, Review, or project ledger was modified.

## Acceptance matrix

| Acceptance criterion | Independent counterexample | Evidence |
|---|---|---|
| Explicit confirmation and idempotent save | IR-01–IR-04 | `independent_results.json` |
| Source/status restore and default deny | IR-05–IR-06 | `independent_results.json` |
| Deny priority, expiry and binding mismatch | IR-07–IR-08 | `independent_results.json` |
| Revoke key binding, visible conflict, restart audit | IR-09 | `independent_results.json` |
| Revoked content cannot restore; preview/confirm replay | IR-10–IR-11 | `independent_results.json` |
| Network/cloud/Tauri/IPC prohibited channels closed | IR-12 runtime/CLI static inspection | `independent_results.json`, runner source |
| Current hash and historical inputs not overwritten | copied-target hash snapshot and read-only review | `independent_snapshot.json` |

## Scope note

`IR-04` exercises a conflicting save request and verifies it fails without a
success result; it is the CLI-observable atomic-failure proxy. It does not
claim a real disk-fault, multi-process, or production durability test, all of
which are outside this task's synthetic single-process boundary.
