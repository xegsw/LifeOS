# LIFEOS-P3-144 Phase-C profile delta: review-owned test design

## Purpose and decision boundary

This is a fresh, isolated, incremental independent review of Closure-3's Phase-C Pilot-7 build/profile authority.  It does not repeat Phase-B product, UI, native-window, or full GUI validation.  A pass can only support PM deciding whether the configuration delta may enter the already-authorized user-operated Phase C.  It cannot establish Pilot-7 access, a successful real Provider call, risk closure, product freeze, or Stage 4 readiness.

The fixed candidate selector supplied by the PM is `777af31e`; its complete immutable commit ID must be resolved and recorded only after this document, the allowlist, prohibited-path declaration, and precontact seal are complete.

## Isolation and controls

- Review output root: `lifeos/reviews/LIFEOS-P3-144/phase-c-profile-delta-review/`.
- Sole review temporary root: `/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1`.
- Candidate, Closure-1/2/3, existing engineering Evidence, and previous independent-review history are read-only.
- The actual Pilot-7 root and its database are forbidden objects: no filesystem, process, compile-run, cleanup, or diagnostic action may address them.
- No real network, DeepSeek, credential, or real-text action is permitted.
- All Cargo targets, Cargo cache, and temporary files will be placed under the review temporary root; `HOME` remains unchanged for synthetic Keychain tests.

## Test matrix

| ID | Review-owned procedure | Passing observation |
| --- | --- | --- |
| I-01 | Resolve and hash the full immutable candidate commit; create a read-only candidate snapshot and recompute Closure-3 Manifest/source hashes. | Selector, commit, manifest, source, and pre/post snapshot hashes agree. |
| I-02 | Run the complete serial Rust regression for the `engineering` profile and separately for the `independent-review` profile. | Each is exactly 22/22. |
| I-03 | Run the offline contract suite serially. | Exactly 23/23. |
| I-04 | Compile the `pilot-7` profile only (`cargo check` or `cargo test --no-run`) without starting an App/runtime. | Compile-only command passes and logs no Pilot-7 access. |
| M-01 | Review-owned static checks and disposable source mutations for exact Pilot parent/root/basename, marker schema/owner/run-id, and compiled `real_gate`. | Each altered invariant is rejected before unsafe use. |
| M-02 | Mutate synthetic/real authority inputs, profile/mode combinations, and build-time selectors. | Environment cannot promote synthetic to real; profile/mode mismatch fails before root/DB/network; unknown profile and pilot plus review-run-id are build-time rejected. |
| C-01 | Check the exact 20 IPC, UI, DeepSeek authority, schema, data/Health, credential, and disclosure contracts against the Closure-3 baseline. | No unapproved drift. |
| P-01 | Verify candidate/old-history zero write and forbidden-path/network/credential/text non-contact through bounded command logs and before/after hashes. | No prohibited contact and no candidate/history mutation. |
| CL-01 | Attempt cleanup with a wrong marker, then clean only the exact review temporary root with the matching marker. | Wrong marker is refused; correct-marker cleanup removes only the authorized temporary root. |
| V-01 | Generate a non-self-referential Final Manifest and execute an independent verifier from separate review-owned logic. | All claimed entries verify; failures are reported rather than suppressed. |

## Stop conditions

Stop as `Invalidated Attempt` on any candidate/history write, precontact-order violation, Pilot-7 access, real network/Provider/credential/text contact, or result that cannot be separated from such contact.  Stop as `Paused — Resumable` for a transient runner/tool failure after writing a checkpoint.  Report any P0/P1/P2/Unknown/Not Implemented truthfully; do not repair candidate code in this review.
