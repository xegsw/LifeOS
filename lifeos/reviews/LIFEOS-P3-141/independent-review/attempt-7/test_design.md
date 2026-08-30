# LIFEOS-P3-141 Phase B Independent Review — attempt-7 test design

## Identity and isolation

- Review role: mandatory independent Phase B review. This attempt has no shared test source, fixture, SQLite database, PID, AX window, screenshot, tool output, or conclusion from any earlier attempt.
- Candidate: commit `8eeaa0353c8f275d4a6321e3d3f66535b6e5f12b`, read-only after this design and precontact seal are immutable.
- Permitted writes: this attempt directory and `/private/tmp/lifeos-p3-141-controlled-pilot-v1` only. All build products, synthetic SQLite files, generated test source copies, app runtime data, Swift output, and cleanup targets stay in the latter root.
- No real-data root, existing Pilot, existing real DB, real text, Health value, credential, Provider endpoint, or network is accessed, probed, hashed, copied, created, or cleaned in Phase B.

## Fixed-input and candidate identity plan

1. Recompute the 12 frozen input byte counts and SHA-256 values from the PM fixed-input inventory, preserving the raw result.
2. Record the candidate Git `HEAD`, calculate a review-owned length-framed tree hash over the candidate source tree, and compare the 79-file result with `source_lineage.json` and the frozen P3-140 lineage value.
3. Recompute the exact IPC inventory from source and require exactly 20 commands. Inspect call topology for an external ModelPort, Provider, fallback, background dispatch, or a 21st IPC.
4. Independently parse the engineering Final Manifest; require exactly 149 listed entries, no self-reference, and matching byte/hash records. Recompute P3-140 ancestry as 79/79.
5. Hash the candidate source tree both before and after all review activity. Any difference is P0 and stops positive evidence.

## Review-owned synthetic verification

All scripts and test sources are authored in this attempt after sealing; no candidate test is adopted as positive evidence.

- Boundary mutations: missing root, pre-existing root, file target, directory target, symlink target, ancestor symlink, non-regular DB target, and root/DB mismatch. Each must fail before writing an authorized synthetic DB.
- Provider closure: enumerate only OpenAI, Anthropic, Ollama, and LM Studio; reject Custom, second provider, post-first-send change, fallback, background dispatch, and network dispatch. Validate explicit save, test, enable, and send separation.
- Resolver and disclosure: authorize only the request packet; cover insufficient authorization, minimum disclosure, L1/L2/L3 budget rejection, exact boundary, over-by-one, CrossDomain filtering, request-local Health removal, and no persistence of the removal.
- Person-level behavior: at most one Work item per synthetic day and at most 14 total; all five structured Health fields at bounds; reject free text; permit no more than three confirmed Memory items; reject automatic Memory promotion.
- Feedback and restart: correction/rejection makes dependent output stale, recomputation changes the output, restart neither sends nor writes again, and request IDs are never reused.
- Atomicity: authorization, stale, budget, malformed data, SQLite, Provider, and recomputation failures must happen before request, receipt, snapshot, audit, Memory, State, or dispatch writes. Review-owned sentinel plus non-content SQLite counts and receipts must remain identical.

## Actual-Tauri plan

For each of desktop `1280x1024`, compact `700x760`, and narrow `560x640`:

1. Build only into the allowed temporary root, bind source and executable hashes, and direct-launch the app to obtain its PID.
2. Require exactly one AXWindow with the exact title for that PID. The native AX subtree of that same window must contain AXWebArea or AXWebView; app-level HTML, AXHTMLContent, a screenshot, or a window-only record cannot substitute.
3. Call `set_size`, wait for stable repeated samples, and require the PID-specific AX frame to equal the receipt geometry. Capture a new screenshot and visually check the expected LifeOS state and no content leakage.
4. Exercise synthetic normal, request-local Health removal, feedback/recompute, Health safety stop, failure-close, and restart state as applicable to each viewport.

The review-owned strict AX helper includes negative controls for a window-only tree, an app-level-HTML-only tree, an AXHTMLContent-only tree, multiple exact-title windows, wrong PID, and unstable/mismatched geometry. Every such control must fail the helper.

## ABF line disposition

- M-001 through M-007: Phase B synthetic verification and lineage.
- M-008 and M-009: `PENDING_PHASE_C` only for real-day participation and real paired-day outcomes; synthetic quota/counterfactual checks remain Phase B evidence.
- M-010 through M-016: Phase B synthetic/offline checks, including non-content disclosure metadata and all three actual-Tauri viewports.
- M-017: `PENDING_PHASE_C` for the user-reviewed real-use receipt.
- M-018 through M-020: Phase B independent review, precise temporary-root cleanup, and non-self-referential final manifest.

`PENDING_PHASE_C` is a phased status, not a Phase B P0/P1/Unknown/Not Implemented defect and cannot be promoted to PASS in this attempt.

## Stop rules

Immediately stop positive conclusion upon a P0: prohibited target touch, candidate/source mutation, fixture or Evidence reuse, non-independent runner, bad fixed input, incomplete 20-IPC closure, external dispatch, privacy disclosure, non-atomic failure, invalid PID/window/WebView binding, missing required capture, failed AX control, or incomplete cleanup. No candidate repair is permitted.

## Expected retained artifacts

- Immutable precontact seal, write allowlist, test design hash, fixed-input verification, source lineage, runner source, raw test logs, raw AX/geometry records, screenshots, matrices, mutations, candidate before/after snapshots, cleanup receipt, independent review, final manifest, and a read-only rerun entrypoint.
