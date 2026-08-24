# LIFEOS-P3-052 Independent Attack Plan

- Sealed at: 2026-08-21 CST, before reading P3-046/P3-047/P3-048/P3-049/P3-050 attack scripts, result sets, reviews, or manifests.
- Basis available at seal time: `AGENTS.md`, current status, operating rules, role/gate rules, P3-052 task card, review/session templates, and filenames only.
- Candidate under review: P3-048 candidate SQL, loaded directly by a new P3-052 runner.
- Independence rule: the new runner must not import, execute, or call any P3-047 runner or any historical attack helper. Historical assets may be compared only after this plan and its hash are sealed.
- Safety boundary: local candidate SQL plus synthetic SQLite data only; no real database, credentials, network target, or external system.

## Configuration matrix

Run every substantive case in all eight combinations:

1. memory / `foreign_keys=OFF` / `recursive_triggers=OFF`
2. memory / `foreign_keys=OFF` / `recursive_triggers=ON`
3. memory / `foreign_keys=ON` / `recursive_triggers=OFF`
4. memory / `foreign_keys=ON` / `recursive_triggers=ON`
5. file / `foreign_keys=OFF` / `recursive_triggers=OFF`
6. file / `foreign_keys=OFF` / `recursive_triggers=ON`
7. file / `foreign_keys=ON` / `recursive_triggers=OFF`
8. file / `foreign_keys=ON` / `recursive_triggers=ON`

For file cases, close and reopen before final assertions, then run `integrity_check`, `foreign_key_check`, and a residue check.

## Independent cases

### A. Submission, canonical hash, and idempotency binding

- A01: first valid lifecycle submission creates exactly one bound submission, one terminal transition, one lifecycle AuditEntry, and one lifecycle Outbox job.
- A02: exact replay is idempotent: no duplicate terminal mutation, AuditEntry, or Outbox job.
- A03: same idempotency key with a different command, target, expected generation, reason, terminal time, or canonical hash is rejected atomically.
- A04: same canonical request under a different idempotency key is rejected or deduplicated according to the schema contract, never double-applied.
- A05: preinserted/fabricated submission rows cannot authorize a lifecycle transition and cannot be rebound after creation.
- A06: malformed/noncanonical payload or hash mismatch cannot create partial state.

### B. AuditEntry evidence

- B01: AuditEntry is generated in the same transaction and binds correlation, command, authorization, generation, reason, and terminal time.
- B02: AuditEntry update/delete/replacement is rejected (append-only).
- B03: duplicate or preplaced correlation/evidence conflicts abort without lifecycle/outbox/submission residue.
- B04: trigger-time failure after an attempted lifecycle mutation leaves no durable audit or terminal partial state.
- B05: unrelated/generic audit rows cannot satisfy lifecycle evidence requirements.

### C. Outbox payload and state machine

- C01: lifecycle Outbox payload is immutable and correctly binds command/authorization/generation/reason/time/correlation.
- C02: not-before availability is enforced; a future job cannot be leased early.
- C03: lease acquisition establishes owner plus generation fencing; wrong owner/generation cannot mutate the job.
- C04: stale owner/generation cannot complete, cancel, dead-letter, or retry after a later lease generation.
- C05: retry increments retry state, clears/renews lease fields consistently, and respects next availability.
- C06: complete/cancel/dead-letter transitions are one-way and mutually exclusive; terminal jobs cannot be reactivated or payload-rebound.
- C07: duplicate/preplaced lifecycle outbox evidence conflicts cause an atomic abort.
- C08: retention cleanup removes only eligible terminal lifecycle jobs; pending/leased/retryable jobs remain.
- C09: generic-job cleanup cannot delete or rewrite lifecycle jobs, and lifecycle cleanup cannot overreach into generic jobs.

### D. Lifecycle generation/time and transaction boundaries

- D01: active-to-each-supported-terminal transition increments generation exactly once and pairs the same terminal time across Authorization, AuditEntry, Outbox payload, and submission.
- D02: direct partial field changes, backwards transition, terminal-to-terminal change, terminal deletion/replacement, or generation/time mismatch are rejected.
- D03: multirow mixed-validity statement is all-or-nothing.
- D04: explicit caller `BEGIN` + valid command + `ROLLBACK` removes all Authorization/Audit/Outbox/submission effects.
- D05: explicit caller transaction with a later statement failure, followed by caller rollback, leaves no durable effects.
- D06: autocommit statement failure rolls back all trigger side effects.
- D07: savepoint rollback restores all four evidence surfaces.

### E. Structural and persistence checks

- E01: required uniqueness/check/trigger contracts exist in the candidate SQL, without trusting runner assertions.
- E02: every file-mode case survives reopen with `integrity_check=ok`, empty `foreign_key_check`, and no temporary test residue.
- E03: behavior is invariant across FK and recursive-trigger PRAGMAs.

### F. Required regressions and preservation

- F01: rerun the current P3-031 contract entry independently/in an isolated copy and record exit/result counts.
- F02: independently reconstruct the semantic intent of PM-CE-01 through PM-CE-05; after the independent run, compare against historical definitions and fill any semantic gap.
- F03: after all independent cases are executed, hash-check the specified P3-046/P3-047 historical failure evidence and other read-only inputs before/after.
- F04: only after the plan and first independent results are sealed, compare P3-052 coverage/results with historical P3-047/P3-050 attack assets; historical results remain corroboration, not primary evidence.

## Verdict rules

- PASS requires every planned contract check to produce independent primary evidence with zero P0/P1, zero explicit P2 bypass, zero Not Implemented/Unknown, regression success, integrity success, hash preservation, and independence checks.
- Any P0/P1, explicit P2 contract bypass, evidence conflict, or preservation failure yields Rework.
- Missing critical assets, inability to create an independent runner, a non-fresh session, or sustained safeguards blocking critical work yields Blocked.
- A PASS is only an input to a later R-0048 decision. It does not close R-0048, affect closed R-0049, freeze assets, restore a baseline, enable real capability, or advance a stage.
