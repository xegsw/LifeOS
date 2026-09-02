# LIFEOS-P3-143 Independent Re-review-3 — Review-owned Test Design

## Identity and independence

- Review ID: `LIFEOS-P3-143-independent-re-review-3`
- Candidate: immutable Git commit `a95a0beb` only. `dcbc3251` is the business-code delta; `6935abde` and `a95a0beb` add read-only review history only.
- Reviewer output root: `lifeos/reviews/LIFEOS-P3-143/independent-re-review-3/` (created new for this attempt).
- Runtime fixtures: only a newly created review-owned root beneath `/private/tmp`; no retained runtime, Pilot, personal data, real DB, Provider, credential, Keychain item, or network target may be read, probed, hashed, copied, or cleaned.
- Candidate, engineering Evidence, PM materials, and prior review assets are read-only inputs after this seal. This review will not invoke a candidate verifier as its proof and will preserve review-owned source, result rows, and a non-self-referential manifest/verifier.

## Ordered method

1. Verify the complete exact frozen-input set exists after the precontact seal. If an input is absent or the identity/contract cannot be recovered, record `Paused — Resumable` or `Blocked` without candidate contact or a candidate Rework claim.
2. Independently recompute the candidate, engineering Manifest, and required historical Review/Manifest hashes and lineage; detect unexpected candidate-tree changes from the stated commit structure.
3. Build review-owned offline tests and mutations in the review root. Tests must exercise the candidate through a disposable review-owned root and fresh synthetic SQLite only; all execution has network disabled and carries no credential.
4. Freeze the root-authority matrix before dynamic execution and record every action, assertion, sentinel/DB/filesystem before/after state, and network counter.
5. Check the exact 20 IPC list, Cloud 8/Local 4 registry, credential-action separation, and no-drift network-authority contract with static or synthetic-offline evidence only.
6. Run the full root-authority matrix, including legal creation; exact marker acceptance; missing, wrong, symlink, and wrong-permission marker rejection; root symlink/wrong-parent/traversal rejection; runtime absent/valid/symlink/wrong-permission checks; DB absent/valid direct-child/symlink/wrong-parent checks; two legal run IDs; malformed IDs (short, long, case, slash, dot-dot, absolute, unknown profile, mixed profiles); runtime-environment injection; and refuse-path sentinel, DB, and filesystem immutability.
7. Determine from the frozen contract whether this re-review must take new actual-Tauri evidence. If required and the desktop/AX/screenshot service is unavailable, checkpoint at that phase and report `Paused — Resumable`; do not rebuild, re-run prior phases, or call it a candidate Rework. If required and available, bind only a fresh direct launch PID to its exact-title AXWindow and AXWebView/Area before a target-window screenshot.
8. Stop writers, perform only marker-gated cleanup of the one literal review-owned root, and independently verify final absence. Missing, wrong, symlink, or non-0600 marker must make cleanup refuse.
9. Produce a row-by-row matrix; P0/P1/P2/Unknown/Not Implemented accounting; a report; review-owned tests and results; and a non-self-referential `FINAL_MANIFEST.json` with verifier.

## Required pass/fail discipline

- A candidate defect that violates the frozen contract is `Rework` only when reproduced by this review’s independent tests or static proof.
- Desktop, AX, screenshot, runner, or temporary-environment failures are `Paused — Resumable` with a checkpoint, never candidate Rework.
- No positive conclusion may rely on a candidate-owned test/verifier pass, a previous reviewer conclusion, or real Gate/Provider behavior.
- This review cannot claim PM acceptance, risk closure, product freeze, Phase C real validation, or Stage 4.
