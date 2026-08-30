# P3-141 Provider Restoration Closure — Independent Test Design

## Scope and independence

This review is a new, isolated L3 review of the fixed candidate at main-repository
commit `48a26320`.  It will not reuse the engineering runner, fixture, PID,
screenshots, conclusion, or positive evidence.  All dynamic inputs are created by
this review under the single temporary root named in `write_allowlist.txt`.

The review will make no access of Pilot-6, `capture.sqlite`, any other Pilot,
real database or path, real text or Health value, credentials, real Provider,
network, cloud, third party, or product model.

## Acceptance tests

1. Recompute candidate identity from the current worktree HEAD and compare the
   candidate tree, source lineage, fixed inputs, engineering manifest, and
   retained historical assets with declared values before any dynamic run.
2. Independently inspect the P3-140 final candidate and the fixed P3-141
   candidate for exactly five profiles, five adapters, the expected mode mapping,
   and the DeepSeek/Kimi/OpenAI-compatible Settings labels.  Prove that DeepSeek
   and Kimi remain Custom configuration labels rather than enums or IPC.
3. Write review-owned loopback server and tests.  Exercise one Custom positive
   request plus negative wrong-model-envelope, malformed/wrong response,
   wrong-mode, untested-or-unenabled profile, post-lock switch, fallback, and
   second-provider attempts.  Each negative must demonstrate rejection before
   dispatch, receipt, audit, or SQLite change.
4. Independently enumerate IPC and prove exactly 20.  Run an independent
   regression suite for P3-141 non-Provider Memory, State, Context Resolver,
   Work/Health, Evidence, feedback, restart, and failure-code behavior.
5. Use disposable semantic mutations of a review-local copy to prove the review
   checker rejects: Custom removal, required-label removal, extra IPC, and
   broken first-send locking.  No mutation may modify the fixed candidate.
6. Start an app from a review-local, immutable candidate copy using a new
   synthetic database.  For desktop, compact, and narrow viewports capture
   synthetic-only Settings evidence and bind source hash -> binary hash -> PID ->
   one exact-title AXWindow -> AXWebView/WebArea -> screenshot hash.
7. Preserve raw evidence, line matrix, independently written verifier, and a
   non-self-referential FINAL_MANIFEST.  Its verifier must reject missing,
   extra, changed-hash, malformed-result, and cleanup-failure mutations.
8. Clean only the single authorized temporary root, only if its marker matches;
   preserve a cleanup receipt.  On any P0, stop positive testing and return
   Rework without modifying the candidate.

## Pass decision rule

Pass requires ABF2-M-001 through ABF2-M-009 to pass, with P0=0, P1=0,
Unknown=0, and Not Implemented=0.  A Pass is limited to the synthetic Provider
restoration Closure and does not authorize Phase C, real Provider use, risk
closure, product freeze, or Stage 4.
