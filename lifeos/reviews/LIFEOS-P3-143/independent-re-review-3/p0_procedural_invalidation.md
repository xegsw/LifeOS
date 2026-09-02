# IR-RR3-P0-001 — Sealed single-root expansion

## Fact

The sealed `test_design.md` and post-seal `runtime_root_binding.md` limit this review to the one literal runtime root `/private/tmp/lifeos-p3-143-independent-review-rereview3-20260902`. During the later source-built `.app` evidence method, the review bundle was compiled with the separately valid candidate run ID `bundleui-20260902`. Its direct PID `99755` created `/private/tmp/lifeos-p3-143-independent-review-bundleui-20260902`.

## Impact

This is a procedural P0: the review used two runtime roots where its sealed design authorized one. The later native PID → exact-title AXWindow → AXWebArea → exact-PID target-only screenshot chain is technically observable but cannot be positive evidence for this independent re-review. The condition is not a candidate defect and is not a candidate Rework.

## Containment and boundary result

- PID `99755` was stopped before cleanup.
- The second root’s ordinary 0700 directory and exact ordinary 0600 marker were read and validated, then it was marker-gated cleaned; both known review roots are absent.
- Candidate, engineering Evidence and historical review inputs remain read-only; no Pilot, personal data, real DB, credential, Keychain item, Provider or network target was contacted.
- Later sealing or deletion cannot restore independence. A fresh isolated re-review must start with new precontact controls and one declared root before any candidate contact.
