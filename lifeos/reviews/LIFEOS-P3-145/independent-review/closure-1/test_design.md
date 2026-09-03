# Closure-1 review-owned test design

## Scope and resumption basis

This is a D-0635 `Paused — Resumable` continuation of the single LIFEOS-P3-145 Phase-B independent review. Attempt-1 remains preserved under the parent review root. Its P0-145-IR-001 was an excluded, separable wrong-App evidence gap; it is not reused here.

Frozen inputs must remain exactly:

- Task SHA-256: `2cbaedabc1049d1e4e13d58c39b13095bd498a685cc5f8028ba0e9a17816f626`
- ABF SHA-256: `040c7166afac7e45bfcdf893c1cc23bfa28827e6e2d1d186ffd8cc4f049e66b1`
- Freeze Manifest SHA-256: `38755bb363a19c6e883fbe34e1d3c68fe58c291fc9c24f5304519e4f249681a9`
- Candidate commit: `579914d06923db65db8c3b421b2da663a1950354`

## Ordered test plan

1. Recheck frozen hashes, resolve the declared branch to the fixed commit, create one detached read-only candidate at the closure-specific temporary root, and compile only with the independent-review synthetic root profile.
2. Run a review-owned static contract runner. It must independently enumerate the exact 20 Tauri IPC commands and reject review mutations for a missing command, missing non-medical guard, missing confirmation gate, and wrong review-root marker.
3. Before any GUI action, assert no same-bundle competitor process exists. Build the immutable candidate into an external temporary output only; produce a closure-local bundle wrapper with a unique identity solely to prevent LaunchServices reuse, then record the direct returned PID, its executable path, hash, fixed candidate root relation, exact AXWindow title, and AXWebView/HTML content.
4. Against one new synthetic DB and fixed non-sensitive canaries, independently exercise AC01–AC18 and AC20: Person Work+Health state, confirmed durable memory, maximum-one/empty Today, explainable references, selected-context disclosure, synthetic provider response and feedback exactly once, credential save/restore/delete fail-closed, restart, and the non-medical rejection. AC19 remains Phase C only.
5. Capture target-only desktop/compact/narrow screenshots and geometry only after the PID chain passes. Perform negative mutations and DB metadata checks. Never use candidate-side tests or screenshots as proof.
6. Stop all closure-owned writers, validate the closure marker and exact temporary root, clean it, and produce a non-self-referential final manifest with an AC matrix.

## Stop conditions

Stop as `Paused — Resumable` for AX/screenshot/runner availability issues without prohibited contact. Stop as P0 only for candidate/frozen-input change, prohibited boundary contact, unsealable evidence mixing, or a renewed actual PID/executable mismatch. Do not repair candidate code.
