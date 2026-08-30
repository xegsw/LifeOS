# P3-141 Phase B Attempt 3 — Independent Test Design

## Scope and isolation

- Review only the fixed candidate commit `51be094af913b8850d57a32774c83f72cc254dce`.
- This design was authored before candidate source, candidate tests, current-worktree status, historical review contents, any generated binary, or any runtime root was contacted.
- Only synthetic, redacted fixture values may be used. No network, real Provider, credential, real text, Pilot root, or `capture.sqlite` is an input to this review.
- The only disposable runtime root is `/private/tmp/lifeos-p3-141-controlled-pilot-v1`; it is created only after the candidate is verified and only with the review marker.

## Fixed independent checks

1. Recalculate all 12 fixed-input byte/hash claims, P3-139 77-file and P3-140 79-file lineages, and the candidate tree before and after testing.
2. Parse source and invoke the candidate's public IPC surface independently: exactly 20 allowed commands; only OpenAI, Anthropic, Ollama, and LM Studio may be selected; Custom, fallback, parallel selection, background dispatch, and post-first-send changes must fail closed.
3. Build a review-owned test matrix of at least 43 individually named cases. It will include positive and negative cases for receipt gating, runtime-root ownership, canonical-path rejection, no-write atomic failure, new-root initialization, owned restart idempotence, Work, structured non-medical Health, three-Memory limit and confirmation, resolver budget, Today, feedback/stale/recompute, Health request-local removal, and Health safety stop.
4. Each negative case records pre/post synthetic SQLite object counts, dispatch count, sentinel digest, and relevant receipt/request identifiers; any persistence or dispatch on a rejected path fails the review.
5. Write review-owned semantic mutations for receipt gate, root ownership, Provider lock, Health safety stop/non-medical boundary, and feedback/budget failure closure. Every mutation must make the independently written verifier fail for the expected reason.
6. Run receipt-enabled actual Tauri only with synthetic redacted screen state at 1280×1024, 700×760, and 560×640. For each launch, bind the exact launch PID to exact bundle/binary hash, one AX window, and one AX web view before evidence capture.
7. Run a marker-gated cleanup that removes only the exact review temporary root. Recalculate a non-self-referential manifest after cleanup; no verification command may rewrite it.

## Pass and stop rules

- Pass requires every ABF-M-001 through ABF-M-020 item applicable to Phase B synthetic work to be proven with review-owned evidence, all 43+ cases passing, all required mutations detected, candidate unchanged, and the exact temporary root absent after cleanup.
- Stop and mark this attempt invalid/blocked on any prohibited-path access, real-content or credential exposure, network/Provider action, candidate mutation, unbound GUI capture, uncleanable temporary root, or a missing contract-critical test capability.
- Phase C, PM acceptance, risk closure, freezing, and Stage 4 are out of scope and will remain Pending / Not Implemented.
