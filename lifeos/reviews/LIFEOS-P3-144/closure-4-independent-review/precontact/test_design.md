# LIFEOS-P3-144 Closure-4 Independent Review Test Design

- authored_at: 2026-09-03T00:00:00+08:00
- reviewer_role: independent AI trust / data-lifecycle reviewer
- fixed_candidate_commit: `86d764d9`
- predecessor_commit: `987dd42d`
- frozen_basis: `ABF-P3-144-v1`
- scope: Closure-4 delta only; candidate, history, engineering Evidence and prior reviews are read-only.

## Review objectives

1. Verify the fixed candidate is exactly commit `86d764d9`, and independently identify the delta from `987dd42d` without changing either tree.
2. Verify DeepSeek process timeout is classified as timeout and remains distinct from HTTP, authentication, network and provider failures.
3. Verify the answer and feedback UI state can be rendered after a confirmed request, including explicit user correction, without replaying a consumed disclosure confirmation.
4. Verify the runtime database basename is exactly `capture.sqlite`, the database is a regular non-symlink file with mode `0600`, and unsupported path/file types fail closed before mutation.
5. Verify feedback is single-consumption/idempotent as frozen, explicit correction preserves lineage, and restart restores the resulting state.
6. Verify synthetic close/reopen persists non-sensitive fixture state while the exact IPC registry remains 20 entries.
7. Verify the repository real-use receipt is non-content only, schema-bounded, and does not authorize reading any retained Pilot or real database.
8. Verify candidate/history hashes and the review-owned output manifest are independently reproducible and non-self-referential.

## Independent checks planned before candidate inspection

- `IR-C4-01 lineage`: commit identities, exact diff inventory, predecessor unchanged.
- `IR-C4-02 timeout`: review-owned process-exit classification assertions, including exit 28 and non-timeout failures.
- `IR-C4-03 UI state`: review-owned static/semantic assertions that confirmed response is assigned, disclosure is consumed, failure clears stale disclosure, and feedback/correction state is rendered.
- `IR-C4-04 DB authority`: review-owned clean-root lifecycle using only `/private/tmp/lifeos-p3-144-independent-review-v1`; assert basename, canonical containment, regular file, `0600`, restart persistence and negative symlink/type/mode cases.
- `IR-C4-05 feedback`: review-owned positive, replay, stale, correction and restart assertions; failed repeats must not create extra rows or audit success.
- `IR-C4-06 IPC`: independently derive and compare the registered command set to the frozen exact 20 list.
- `IR-C4-07 receipt privacy`: schema/key allowlist and prohibited-content-field scan of the repository receipt only; no real content/hash inspection.
- `IR-C4-08 actual Tauri`: only if needed after deterministic checks, launch against the synthetic review root and fresh synthetic DB; bind direct PID to target AXWindow/WebView. Environment failure is `Paused — Resumable`, not candidate failure.
- `IR-C4-09 mutations`: review-owned disposable copies or harness inputs for timeout misclassification, wrong DB basename, symlink/non-regular DB, mode drift, duplicate feedback and stale disclosure replay. Candidate remains read-only.
- `IR-C4-10 cleanup`: reject missing/wrong/symlink marker; stop writers; exact marker-gated cleanup of the single review root; prove literal root absent.

## Stop conditions

- Any access/stat/probe/hash/read/create/cleanup against the retained Pilot-7 path or descendants.
- Network access, real Provider/credential use, proxy inheritance or real model invocation.
- Candidate/history/fixed-input modification.
- Missing or mismatched frozen Task/ABF inputs, or candidate identity other than `86d764d9`.
- Positive Evidence cannot be separated from a prohibited or polluted artifact.

On an ordinary desktop/AX/screenshot environment issue, write a checkpoint and pause from the earliest affected stage. Do not invalidate deterministic work.
