# Precontact allowlist

This allowlist is effective only after the accompanying precontact seal is written and hashed.

## Allowed writes

1. `lifeos/reviews/LIFEOS-P3-144/phase-c-profile-delta-review/` only.
2. `/private/tmp/lifeos-p3-144-phase-c-profile-delta-review-v1` only, provided its review marker matches exactly.

## Allowed read-only candidate and history contact after seal

1. Git object `777af31e` and only the complete commit ID to which it resolves, via read-only `git rev-parse`, `git show`, `git ls-tree`, `git diff`, and `git archive` operations.
2. The candidate tree and the Closure-3 Manifest/source files selected from that immutable commit, copied only into the review-owned temporary snapshot.  The snapshot must be made read-only before build/test commands.
3. The named Closure-1/2/3 engineering artifacts and prior independent-review artifacts only when their exact path is first recorded in review-owned discovery output and their content is read without modification.
4. Project toolchain executables, local Cargo registry/cache inputs, and generated files under the sole review temporary root required for offline build/test execution.

## Allowed execution after seal

Offline `cargo test` and `cargo check`/`cargo test --no-run` against the read-only candidate snapshot only.  Cargo target, cache, and `TMPDIR` must be review-owned.  `HOME` must not be redirected.  Pilot-7 profile execution is compile-only; no App or runtime launch is allowed.

## Explicitly not allowed

Anything outside the two write roots; any write to candidate or historical inputs; any broad inventory before candidate paths are resolved; all real-network, Provider, credential, and real-text operations; and all forbidden-path actions in `prohibited_paths.md`.
