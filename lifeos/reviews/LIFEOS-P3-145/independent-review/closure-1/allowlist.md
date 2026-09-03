# Closure-1 allowlist

Permitted after the Closure-1 precontact seal only:

- Fixed Git object `579914d06923db65db8c3b421b2da663a1950354` and its detached, read-only snapshot at `/private/tmp/lifeos-p3-145-independent-review-closure-1/candidate`.
- The frozen task, ABF and Freeze Manifest named in `test_design.md`.
- This review directory and the exact synthetic temporary root `/private/tmp/lifeos-p3-145-independent-review-closure-1`.
- Offline Cargo build artifacts, synthetic `capture.sqlite`, a closure-local copied app wrapper, and fixed non-sensitive review canaries.
- Process, accessibility, screenshot and geometry metadata only after direct-PID binding proves the executable is inside the allowed closure root.

The reviewer may not modify the candidate, engineering deliverables, PM ledger, frozen inputs, or any path outside this list except creation of the required deliverable summary in `lifeos/deliverables/`.
