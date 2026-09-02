# LIFEOS-P3-144 independent re-review-3 — precontact test design

## Identity and independence

- Review kind: fresh, isolated Phase B independent re-review after Closure-2.
- Review-owned root: `lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/`.
- Candidate identity to verify only after this seal: Git commit prefix `a38bcb19`, with the full SHA resolved from `HEAD`; product candidate content must be byte-identical to Closure-2 commit `461423b3` except for added invalidated-review history.
- This review must not reuse any seal, runner, fixture, DB, PID, screenshot, result, or conclusion from `independent-re-review-2` or another earlier review.
- The candidate, Closure-2, all prior reviews, Evidence, manifests, task/ABF, and PM ledgers are read-only once contact begins. The review does not repair the candidate or update a PM ledger.

## Non-negotiable containment

- `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7` is prohibited. This review will not access, test for existence, stat, enumerate, hash, read, create, write, or clean that path or anything below it.
- The review will not contact a real Provider, use real credentials, use real text, or use network access. All data, credentials, responses, and network observations are review-owned synthetic fixtures.
- The only runtime root is `/private/tmp/lifeos-p3-144-independent-review-v1`. It will be marker-gated, checked for invalid/missing/symlink-marker rejection, and cleaned only after writers/PIDs stop.
- Every Cargo invocation will use the absolute review-owned target directory `lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/work/cargo-target`; `HOME`, `TMPDIR`, and review cache locations will be under `work/`. Before and after Cargo, the review will obtain a candidate ignored-status snapshot and tracked/hash ledger, and will fail closed if candidate writes are observed.

## Independent test plan

1. After seal verification, resolve the exact commit, fixed inputs, candidate lineage, P3-143 baseline, Cloud 8/Local 4 profiles, exact 20 IPC registration, and Closure-2 equivalence from read-only sources.
2. Run the frozen `independent-review` Cargo profile in a review-owned environment: complete `cargo test --locked --offline -- --test-threads=1`, requiring 21/21; prove the fixed review root test is absent and verify CI lists complete suites for both profiles.
3. Create and retain review-owned test source, fixture DBs, mutation scripts, synthetic network harnesses, result logs, source/lineage ledgers, and replay entry points. No candidate test runner is sufficient proof.
4. Independently cover ABF-M-001 through ABF-M-024 and ABF-M-032. The concrete test groups include: Work and Health semantic persistence; fourth, over-200, empty, and unknown-field write-before rejection; relevance/validity/budget selection; remove/cancel/no-confirm/stale/replay/restart no-send behavior; DeepSeek-only/no-fallback/no-background/no-proxy/no-redirect guards; credential missing/tamper network-before failure; AI identity, all five feedback actions, correction/revocation invalidation; and Health non-medical failure closure.
5. For all negative network or DB cases, record counters and before/after state demonstrating the operation stopped before the prohibited write or request.
6. Direct-launch a fresh actual Tauri process from the verified candidate, bind the launch-returned PID to one exact-title AXWindow and its AXWebArea/WebView, then capture readable target-only desktop, compact, and narrow evidence. If the desktop, AX, or screenshot service is unavailable, record `Paused — Resumable` with a review-owned checkpoint and resume only at `visual_capture`.
7. Stop all writers/PIDs, perform marker-gated cleanup of the fixed runtime root, prove absence, build a non-self-referential FINAL_MANIFEST, and run a review-owned verifier plus missing-entry/hash-drift mutations.

## Pass rule and scope of conclusion

Pass requires each applicable ABF row, especially M-001–024 and M-032, to be independently supported, with P0=0, P1=0, Unknown=0, and Not Implemented=0; 21/21 profile tests, review-owned mutations, three native viewport proofs, lineage, cleanup, and final verifier must pass.

An Independent Pass would only permit PM consideration of Phase C. It does not mean PM Accepted, real capability enabled, risk closed, product frozen, or Stage 4 ready.
