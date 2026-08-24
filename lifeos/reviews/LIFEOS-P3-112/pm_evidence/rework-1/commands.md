# LIFEOS-P3-112 PM Rework 1 Review Commands

- Recomputed the submitted Rework Manifest bytes and SHA-256 for all 25 payload files.
- Built an isolated PM workspace at `/private/tmp/lifeos-p3-112-pm-rework1-v1/workspace` containing only the fixed P3-111 inputs and a copy of the submitted P3-112 runner.
- Executed the Manifest-bound runner copy without modifying it. Its task temporary root remained `/private/tmp/lifeos-p3-112-review-v1`; its output directory was inside the isolated PM workspace, so submitted Evidence was not overwritten.
- The runner used pre-existing `/Users/xxe/.cargo/bin/cargo` and `rustc`, `--locked --offline`, `CARGO_NET_OFFLINE=true`, and task-root-local `CARGO_TARGET_DIR` and `TMPDIR`.
- Compared ten deterministic generated JSON outputs with the submitted Rework Evidence by SHA-256.
- Inspected the unchanged control, six independent mutations, submitted-verifier cross-check, fixed inputs, history lineage and closure matrix.
- Precisely removed `/private/tmp/lifeos-p3-112-review-v1` and `/private/tmp/lifeos-p3-112-pm-rework1-v1`; no wildcard or historical-path cleanup was used.
