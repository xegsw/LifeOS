# LIFEOS-P3-143 Independent Re-review 1 — Precontact Test Design

## Identity and ordering

- Review identity: `LIFEOS-P3-143 / independent-re-review-1`.
- Reviewer: fresh isolated review session; review only, no candidate or PM-ledger modifications.
- Declared target: commit `767301fb051d11a6bf11488413f8b03aabfc2d99` on `codex/l3-p3-143-real-ai-activation`.
- This document is authored before any candidate-tree enumeration, candidate-file read/hash/stat, engineering-Evidence contact, candidate test execution, or runtime-root creation.

## Scope and safety boundary

The review uses only synthetic, non-secret fixtures and a fresh review-owned `/private/tmp` direct-child root that must first be accepted by the candidate's closed build-time profile and strict independent-review run-id grammar. No API key, Keychain credential, real Provider, network target, Pilot, personal DB/path/text, Health, Context, Memory, historical runtime root, or real user material may be probed, read, hashed, copied, tested, or cleaned.

## Planned independent evidence

1. Recompute the supplied commit lineage and declared fixed-input / engineering-artifact hashes using read-only commit-object access; record every exact path and result.
2. Build review-owned source-level and runtime tests. Do not import, call, copy, or treat the candidate verifier/tests as independent proof.
3. Verify root authority for at least two distinct legal independent-review run IDs. For each, assert a canonical non-symlink `/private/tmp` direct child, exact marker binding, permission restrictions, exact runtime direct-child binding, and a fresh direct-child SQLite DB.
4. Attack closed build-time profile/runtime binding before any DB, Keychain, network, or other durable state write: short/long/case/slash/dot-dot/absolute-path IDs; unknown profile; engineering/review mixing; environment root injection; wrong parent; root symlink; missing/wrong/permission-invalid marker; non-direct-child DB; and DB symlink. Each must fail closed with zero prohibited side effect.
5. Run synthetic credential-lifecycle and leak / tamper / delete / state-machine checks as review-owned tests. All tests use a review-specific canary that is neither a Provider key nor an external request payload.
6. If Phase-A contract requires GUI proof, launch the candidate directly under the review-owned profile and bind the launch-returned fresh PID to the exact title, one AXWindow and AXWebView/AXWebArea before capturing only the target window at each contract viewport. A locked desktop or unavailable AX/screenshot service is Paused — Resumable, recorded in a checkpoint, not candidate Rework.
7. Stop writers, validate the exact literal root plus ordinary non-symlink, identity-bound marker and required permissions, then perform only marker-gated cleanup. Wrong, missing, linked, or misbound markers must refuse deletion.

## Pass / stop criteria

- Pass requires independent, reproducible evidence for every applicable ABF row and no P0/P1/Unknown/Not Implemented; P2 may only be a disclosed non-security, non-reproducibility issue.
- A precontact-order violation, forbidden-boundary contact, candidate/history mutation, or non-separable sensitive evidence is a procedural P0 and ends this review attempt.
- A candidate security or authority failure is Rework; a missing frozen input is Blocked; a temporary desktop/AX/screenshot condition is Paused — Resumable with checkpoint.
