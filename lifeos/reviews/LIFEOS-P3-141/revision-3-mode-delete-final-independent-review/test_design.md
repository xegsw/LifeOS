# P3-141 Revision 3 Mode Delete — Independent Re-review Test Design

## Identity and independence

This is a new, review-owned, read-only L3 independent re-review.  The candidate is the input-branch `HEAD` declared by the task contract (declared identity: `f0c6cc6f`; the exact commit and candidate tree will be independently bound only after this seal).  No prior review test, fixture, database, PID, window, screenshot, temporary root, Evidence result, or conclusion will be reused as positive evidence.

## Write and execution boundary

Only this directory and `/private/tmp/lifeos-p3-141-revision-3-independent-review-mode-delete-v1` may receive review-created data.  The candidate, engineering Evidence, historical reviews, PM ledger, and all other project material are read-only.  No Pilot-6, real database/path/text, Health real data, real Provider, credential, network, or product model may be accessed.

## Independent test plan

1. Bind the exact current candidate commit, source tree, candidate file hashes, source/binary identities, and fixed inputs after sealing; reject drift before any positive conclusion.
2. Build review-owned synthetic fixtures and run a review-owned verifier covering the exact 20 IPC contract; Cloud five-provider and Local three-provider enumeration/segregation; distinct save/test/select/enable/send semantics; encrypted SQLite credential lifecycle; restart, update, and deletion behavior; no session/environment credential fallback.
3. Exercise the mode-delete lifecycle independently: save a synthetic Cloud credential, persist Local state, switch the UI to unsaved Cloud draft, require the save-first state with no usable deletion action, assert stale/programmatic deletion rejects before credential IPC or database mutation, then save and delete Cloud and confirm zero stored credentials and no restart mask/delete affordance.
4. Execute independent positive, negative, restart, repeat, stale-action, and failure-closure checks.  Database checks use only review-owned synthetic SQLite files under the sole temporary root and report non-secret counts/states, never key material.
5. Make and run disposable source mutations that respectively remove the draft-mode deletion guard/expose deletion, widen Provider sets, introduce session credential fallback, cross-use Cloud/Local state, widen an allowed root, and bypass marker cleanup.  Each must fail an independent test.
6. Direct-launch offline Tauri from the reviewed candidate and bind the launch-returned PID to one exact-title AXWindow and AXWebArea/WebView.  Capture review-owned desktop, compact, and narrow screenshots plus native geometry and source/binary hashes; prove each bound PID exits.  A missing direct AX chain is a stop condition.
7. Test exact cleanup: a wrong marker must refuse deletion; only a non-symlink mode-0600 correct marker may clean the literal review temporary root; prove the literal root is absent.  No old temporary root may be accessed.
8. Recompute candidate hashes before and after all review actions, generate a non-self-referential `FINAL_MANIFEST.json`, and run the review-owned verifier after finalization.

## Fail-closed criteria

Immediately stop positive validation and report `Blocked`/`Rework` if this session has a precontact-order breach, a frozen/direct input is missing or mismatched, the candidate changes, a prohibited boundary is contacted, an independent mutation is not caught, cleanup violates the contract, or fresh direct-PID native GUI evidence is incomplete.  A bounded Pass, if earned, is only for the synthetic/offline Revision-3 task contract; it is never PM acceptance, Phase C, Pilot-6, real Provider/credential authorization, risk closure, product freeze, or Stage 4.
