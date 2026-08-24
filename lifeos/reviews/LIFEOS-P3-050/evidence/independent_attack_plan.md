# LIFEOS-P3-050 Independent Attack Plan

## 1. Seal context

- Task: `LIFEOS-P3-050`.
- Created at: `2026-08-21 08:33:32 CST`.
- Runtime selected by PM dispatch: `gpt-5.6-sol` + `xhigh`; no downgrade and no fallback.
- Session evidence: PM dispatch records a new Codex task `01a02001-a5f2-7681-a2b8-e42f44a08efd`; the first turn performed only the required isolation handshake, and the formal start arrived after dispatch evidence and ledger updates.
- Scope: synthetic memory/file SQLite only. No real database, real migration, real user data, Vault, Tauri/IPC, network, cloud/model, synchronization, multi-device, L3, or external user capability.
- Source assets are read-only. Test execution will use a fresh temporary copy; only this P3-050 review/evidence directory and the permitted local-precheck directory may be written.

## 2. Delayed-input attestation

At the time this plan was authored, the following delayed P3-049 assets had **not** been opened, searched, imported, executed, copied, or summarized:

- `lifeos/reviews/LIFEOS-P3-049/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-049/evidence/MANIFEST.md`
- P3-049 independent attack script(s)
- P3-049 structured attack result(s)
- P3-049 detailed attack log(s) and snapshots

The only P3-049 material read before this seal was `lifeos/reviews/LIFEOS-P3-049_pm_review.md`, explicitly permitted by the task card to understand the procedural Rework, published technical totals, and non-extrapolation boundary. Those published totals are not used as P3-050 evidence or as a scenario table.

The P3-050 attack implementation will be authored from this plan and the direct inputs below. It must not import, call, copy, or mechanically rewrite P3-048/P3-049 attack functions, scenario tables, or runner helpers. Historical runners may be used only for isolated equivalent regression reruns after the independent script is sealed.

## 3. Direct basis and current hashes

The attack plan is derived from the P3-050 task contract, P3-047 PM-CE-06, the P3-048 remediation description/evidence, and the current P3-031 candidate SQL/contract runner.

| Direct input | SHA-256 at planning time |
|---|---|
| P3-050 task card | `4c45f7380eb8dda34447d6d88a2a55c2f52ed7800b3c04c50f5d27156b17bbd8` |
| P3-047 PM-CE-06 script | `54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50` |
| P3-047 original PM-CE-06 result | `f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5` |
| Current P3-031 candidate SQL | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| Current P3-031 contract tests | `6729d48eeb9e523b5875165c053701602d6e10d5171fd27f235e680dcb34b3b5` |
| Current P3-031 validation shell | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |
| P3-048 engineering manifest | `780f473880f82249f50e99f41bc845377d58fbde4eccb5b96a2350a25bf492f4` |
| P3-048 PM manifest | `4e5d9a21794a4be027fe86183d582ae0885397920c7854c829596053f22e256e` |

## 4. Independently inferred invariants

The current candidate defines these relevant contracts:

1. A Tombstone begins at `accepted`; duplicate insert/REPLACE and every DELETE are rejected.
2. If either OLD or NEW `subject_type` is `authorization`, any change to `subject_type`, `subject_id`, `generation`, `command_id`, `reason_code`, or `blocked_at_ms` must abort.
3. `IS NOT` comparisons are intentionally NULL-safe; a NULL mutation cannot evade a comparison even though the table's NOT NULL constraint is also a defense.
4. Authorization cleanup status/time rules remain a separate state machine. An identity/control mutation combined with cleanup status/time mutation must fail as one statement, with no half-state.
5. A narrow fix must preserve generic Tombstone generation/control/status behavior and valid Authorization cleanup retry/cleaned paths.
6. SQLite `RAISE(ABORT)` rolls back the failing statement, not earlier successful statements in a caller-owned explicit transaction. The caller must rollback the transaction when its unit of work must be atomic.
7. Trigger firing order and the first visible error string are not contractual; final database state and rejection are contractual.

## 5. Configuration matrix

Every attack family and legal control will run in all eight combinations:

- backend: `memory`, `file`
- `PRAGMA foreign_keys`: `ON`, `OFF`
- `PRAGMA recursive_triggers`: `ON`, `OFF`

Each configuration uses a newly migrated synthetic database. File configurations additionally record `integrity_check`, `quick_check`, and `foreign_key_check`; all must be `ok`, `ok`, and empty respectively.

## 6. Attack families

### A. OLD/NEW namespace and identity directions

For each configuration, use independently built fixtures and verify statement rejection plus exact row preservation:

- `DIR-GA`: generic `artifact/placeholder` -> Authorization `authorization/auth-a`.
- `DIR-AG`: Authorization `authorization/auth-a` -> generic `artifact/escaped`.
- `DIR-AB`: Authorization `authorization/auth-a` -> another terminal Authorization `authorization/auth-b`.

### B. Six-field single and compound mutation by cleanup state

For each of `accepted`, `active_blocked`, `cleanup_pending`, `cleanup_failed`, `vendor_limited`, and `cleaned`:

- independently mutate `subject_type`;
- independently mutate `subject_id`;
- independently mutate `generation`;
- independently mutate `command_id`;
- independently mutate `reason_code`;
- independently mutate `blocked_at_ms`;
- mutate all six fields in one statement.

Every mutation must be rejected and the complete row must equal its before snapshot. This is 42 state/field cases per configuration before other families.

### C. NULL and comparison edge cases

For all six cleanup states, attempt `NULL` independently in each of the six protected fields. Rejection may come from the control trigger or the NOT NULL table constraint; the acceptance criterion is fail-closed with an unchanged row and no database damage.

Also test:

- no-op assignment of all six protected fields to themselves;
- no-op cleanup status and timestamp;
- unchanged nullable values elsewhere do not make the protected comparison false or unknown.

The two no-op controls must succeed and leave the row byte-for-byte equivalent.

### D. Control mutation combined with cleanup status/time

For each starting cleanup state, combine a protected field mutation with a status and/or `updated_at_ms` change in one UPDATE. Include:

- a status edge that would otherwise be legal;
- a status edge that is illegal;
- same-status timestamp change;
- backward timestamp with status change;
- compound identity + status + timestamp change.

The statement must fail with no partial control, state, or time update. Which trigger supplies the first error is an observation only.

### E. Conflict algorithms and reconstruction neighbors

For each configuration:

- UPSERT (`ON CONFLICT DO UPDATE`) targeting an existing Tombstone;
- `INSERT OR REPLACE` targeting an existing generic or Authorization Tombstone;
- `UPDATE OR REPLACE` attempting generic -> Authorization, including a primary-key conflict;
- plain conflicting INSERT;
- DELETE followed by reinsert inside an explicit transaction.

All must fail closed and retain the original row(s). A rejection from the duplicate-insert or no-delete guard is acceptable when it prevents the same end state.

### F. Single-row, multi-row, statement atomicity, and caller transaction boundary

For each configuration:

- single-row protected mutation;
- one multi-row UPDATE that would legally advance a generic row and illegally rebind another row;
- one multi-row UPDATE across protected Authorization rows where one or more rows would mutate;
- one explicit transaction where a legal statement succeeds before a later protected statement fails;
- caller rollback after that failure.

Acceptance:

- the failed statement changes no row;
- a prior successful statement in the explicit transaction remains visible until caller rollback (SQLite `ABORT` semantics);
- caller rollback restores the full transaction snapshot;
- no commit containing a protected mutation is possible.

### G. Legal-path regression controls

For each configuration, prove the patch remains narrow:

- generic Tombstone generation/control update and forward status movement succeed;
- protected-row no-op succeeds;
- Authorization cleanup trace succeeds: `accepted -> active_blocked -> cleanup_pending`;
- `cleanup_failed -> cleanup_pending` retry succeeds;
- `vendor_limited -> cleanup_pending` retry succeeds;
- after controlled deletion of the three sensitive projections, a permitted transition to `cleaned` succeeds;
- a cleaned row remains terminal.

### H. Original PM-CE-06 and regression entrances

Outside the independent attack count, but before the delayed P3-049 comparison:

- run the original P3-047 PM-CE-06 script against the current candidate in a temporary copy and require `8 PASS / 0 BYPASS`, exit `0`;
- run the P3-048 total validation entrance in a separate temporary copy and require the published P3-048/P3-047-equivalent/P3-031 totals, exit `0`;
- record source before/after hashes so source Evidence is never overwritten.

## 7. Result classification and stop rules

Each independent case records: stable case ID, severity, family, configuration, expected outcome, status (`PASS`, `BYPASS`, `FAIL`, `NOT_IMPLEMENTED`, `UNKNOWN`), observed error, before/after snapshots, and relevant integrity checks.

- A protected operation that commits is a P2 contract bypass and forces `Rework`.
- Any active-Authorization revival, loss of terminal/audit history, or data corruption is P0/P1 and stops expansion after evidence capture.
- Any legal generic or cleanup control regression is at least P1/P2 depending on contract impact and forces `Rework`.
- Evidence/hash conflict, missing isolation proof, or unexecutable key input forces `Blocked`.
- Cross-trigger first-error variation and caller rollback responsibility are P3 observations only if final state and documented transaction semantics remain correct.
- `Pass` requires 0 P0, 0 P1, 0 P2 bypass, 0 new P2, 0 Not Implemented, 0 Unknown, exit `0`, all regression entrances passing, and all source hashes preserved.

## 8. Seal sequence

1. Save this plan.
2. Record its SHA-256 in `independent_attack_plan.sha256`.
3. Author and hash the independent P3-050 script without opening delayed P3-049 assets.
4. Execute the independent matrix and save structured results/log/snapshots/environment/commands.
5. Hash and seal the first-run assets.
6. Only then open P3-049 Review/Manifest/attack assets for coverage/statistical comparison.

