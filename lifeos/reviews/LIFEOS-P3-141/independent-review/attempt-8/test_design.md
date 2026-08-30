# LIFEOS-P3-141 Phase B Attempt-8 — Independent Test Design

## Independence commitment

This design was written before reading the candidate at commit `c7087586d89a52bc252765ec89fa63611f585d0e`. It is review-owned, will not import, invoke, copy, or treat engineering or historical review tests, fixtures, databases, PIDs, windows, screenshots, or conclusions as positive evidence. Attempt-7 is historical-only and may be consulted only after the seal.

## Scope and hard stops

- Phase B is synthetic/offline only. Pilot-6, every other Pilot, real DB/path/text/Health value, credential, Provider endpoint, and network target are excluded from every command and test.
- The only disposable runtime location is `/private/tmp/lifeos-p3-141-controlled-pilot-v1`; cleanup is a literal-path removal only after review evidence is captured.
- Any evidence of protected-path probing, content/credential taint, unintended dispatch, candidate mutation, non-binding native GUI identity, or a required failed invariant is P0: stop positive evidence and issue `Rework` or `Blocked` without repairing the candidate.

## Independent evidence plan

1. Recompute all 12 frozen inputs and ABF identity; record pre/post candidate commit, clean state, length-framed 79-file tree, 20 IPC inventory, and engineering Manifest 179/179 with a review-owned verifier.
2. Use review-authored Rust tests and a review-authored static/lineage verifier. Cover every ABF-M-001–020 Phase-B-applicable predicate and record Phase-C-only lines as `PENDING_PHASE_C`, never as a synthetic pass.
3. Exercise fresh synthetic SQLite fixtures for normal and negative paths. For root/DB/link/type and receipt/gate cases, assert reject-before-runtime-root-resolution and compare non-content sentinel plus relevant object/audit/request/receipt/memory/state counts before and after.
4. Test the closed Provider set, explicit saved/tested/enabled/sent state transitions, post-first-send lock, zero Custom/second/fallback/background dispatch, and explicit user-send only. No real endpoint is configured or called.
5. Verify resolver budget authorization and minimum disclosure: budget reject, exact boundary, over-by-one, domain exclusion, L1/L2 authorization, and no write on failure. Verify Work daily `<=1`, total `<=14`; structured Health exactly permits five fields and rejects free text; durable Memory `<=3` and never auto-promotes.
6. Verify feedback correction/rejection creates stale lineage and a changed recomputation; Health removal is request-local; safety signals select a conservative non-diagnostic stop; restart neither dispatches nor duplicates writes or request IDs.
7. Run review-owned semantic mutations for root validation, closed-provider/lock behavior, resolver budget, feedback/recompute, and pre-write atomicity. A mutation must be detected as a failure to count.
8. Launch the actual Tauri binary three times through a review-owned direct launcher. For each viewport, bind direct PID -> exact unique title AXWindow -> native AXWebArea/AXWebView; save the same-PID AX frame and a synthetic-only screenshot. Strict negative probes must reject window-only binding and `AXHTMLContent` substitutes.
9. Independently test Phase-B receipt validation: every old `LIFEOS_P3_141_PHASE_B_RECEIPT` string must be rejected, regardless of content. Before runtime-root resolution/write, reject missing, malformed, extra, duplicate, wrong ABF/candidate/tree/Manifest/verdict/owner, stale, dirty/uncommitted, unrelated Git root, file-link, ancestor-link, directory, and oversize values.
10. Only if all synthetic Phase-B tests produce a provisional Pass, produce a non-self-referential evidence manifest, fix its identity hash, and issue a Phase-B receipt bound to it. Commit only attempt-8, verify the tree is clean, then use that receipt for exactly one synthetic Phase-C gate positive control under the disposable root.

## Success rule

`Pass` requires all applicable ABF-M-001–020 checks and all negative controls to pass, P0/P1/Unknown/Not Implemented equal zero, evidence-manifest verification before receipt issuance, receipt binding to the committed review evidence identity, and exact temporary-root cleanup. The conclusion remains Phase-B synthetic/offline only; it does not create, probe, or validate a real Pilot.
