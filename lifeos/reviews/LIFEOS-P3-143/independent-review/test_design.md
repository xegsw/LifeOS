# LIFEOS-P3-143 independent review — test design

## Review identity and precontact declaration

- Review: `LIFEOS-P3-143`, fresh isolated mandatory independent review.
- Design owner: this review session only; no candidate test, runner, verifier, fixture, result, screenshot, Keychain item, DB, temporary root or prior conclusion has been imported or used.
- Written before candidate, P3-143 engineering deliverable, engineering Evidence, P3-143 `FINAL_MANIFEST`, Phase A/B checkpoint, or any Phase-B receipt is read.
- Candidate and all historical P3-139 through P3-142 assets are read-only. This review will not modify engineering, candidates, deliverables, PM reviews, frozen inputs, or PM ledgers.

## Controlled review assets

- Review output root: `lifeos/reviews/LIFEOS-P3-143/independent-review/`.
- Disposable runtime root: `/private/tmp/lifeos-p3-143-independent-review-v1` only, with a unique regular 0600 marker and canonical non-symlink root/child checks before any later cleanup.
- Disposable SQLite databases and a review-owned synthetic credential canary are created only beneath that runtime root. The canary value will never be printed, placed in a command line/environment, hashed as plaintext, screen-captured, or written to Evidence.
- Any review-created Keychain material must use an exact P3-143-review-only item name, be metadata-checked without revealing value, and be deleted only through its exact identifier after the deletion matrix passes.
- No test starts a real Provider request. The only possible real-gate activity is after complete synthetic Phase-A review Pass, using the App, with the user manually entering a DeepSeek key out of Agent view. The reviewer neither asks for, types, pastes, observes, records, nor reuses that key.

## Independent method and ABF coverage

1. **Frozen lineage (ABF-M-001, M-020, M-022).** Independently recalculate the supplied acceptance-freeze hashes; then read exact allowlisted predecessor and P3-143 materials. Recompute fixed-input, candidate and non-self-referential Manifest hashes, and verify the P3-142 Cloud-8/Local-4 baseline and exact 20 IPC list from review-owned checks.
2. **Review-owned lifecycle (M-002 to M-010).** Write a new reviewer test runner and fixtures under this review root. Use only fresh SQLite DBs and a synthetic canary to test save/configuration, encrypted credential persistence, fresh-PID restart, DB-only/key-only separation, AAD/ciphertext/nonce/reference/profile/version tampering, update and delete invalidation, strict DTO rejection, and independent action counters.
3. **Leak and disclosure attack (M-003 to M-012, M-018 to M-019).** Scan review-owned DB/WAL/SHM, controlled logs, structured errors, screenshots, argv/env evidence and generated manifests for the canary. Assert UI masking never reveals prefix, length or reversible derivatives. Evidence records only redacted classifications, not test secrets, prompt, response, user Key, or model name.
4. **Authority and router attack (M-009 to M-015).** Independently exercise save/test/select/enable/send separation, explicit single-profile authorization, disabled/missing/untested/unselected-policy reject paths, Cloud-8/Local-4 visibility, all other Provider zero-request ledger, strict target authority, and no retry, redirect, proxy, fallback, background probe or parallel send. Synthetic harnesses must not bind a real DeepSeek endpoint or accidentally turn a negative connection test into a success.
5. **Native application evidence (M-014 to M-016).** Build/launch the fixed candidate only after static/lifecycle checks pass. For desktop, compact and narrow viewports: obtain a fresh direct-launch PID, bind its exact titled AXWindow, then AXWebView/AXArea, and capture only the target app with no Key, prompt or response. Deletion is followed by a fresh-PID denied-call check. Desktop/AX/screenshot unavailability creates a checkpoint and `Paused — Resumable`, not an engineering Rework.
6. **Phase evidence and cleanup (M-017 to M-021).** Read Phase A/B checkpoints and Phase-B non-content receipts only after sealing; independently check their non-content contract and chronology. Reproduce marker/wrong-marker/symlink rejection and exact cleanup against review-owned roots only. Verify final manifests with a review-owned verifier that excludes itself and records every covered row individually.

## Required independent assertions

- Candidate verifier PASS, static scans, candidate tests, prior screenshots and engineering receipts are never sole proof.
- No review test imports, invokes, copies or batch-maps candidate test code/results. Candidate tools may be read only as a subject of review.
- All mutation/failure assertions record a network counter and before/after database/reference state; a mutating failure must be rejected before network and must not silently repair the test input.
- A synthetic/offline Pass does not authorize the real gate. A later real gate, if reached, remains user-operated, DeepSeek-only, non-content, and separately evidenced.
- P0/P1/P2/Unknown/Not Implemented are reported individually. This review does not make PM acceptance, risk, freeze, baseline-recovery or Stage decisions.

## Stop conditions

- Stop and record a P0/Invalidated Attempt if prohibited data/path/provider/credential is contacted, a read-only asset is modified, or positive Evidence cannot be separated from a prohibited disclosure.
- Stop `Blocked` if a frozen input is missing or candidate identity cannot be established.
- Stop `Paused — Resumable` with a checkpoint for lock screen, unavailable AX/screenshot service, or temporary external availability after safe shutdown; resume only if the contract/candidate/baseline summaries remain identical.
