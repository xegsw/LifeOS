# Runtime-root binding record

This is a post-seal execution binding, not a modification of the sealed test design, allowlist, prohibited declaration, or precontact seal.

- The sealed design authorizes exactly one fresh review-owned root beneath `/private/tmp`; it did not authorize a retained runtime root.
- The candidate’s read-only compile-time authority uses the `independent-review` profile and a validated run ID to form the only runtime root it will accept. The selected safe run ID is `rereview3-20260902`.
- Therefore the sole dynamic root for this review is `/private/tmp/lifeos-p3-143-independent-review-rereview3-20260902`. It was verified absent before any dynamic action. Its expected marker is a 0600 ordinary file with schema `lifeos.p3-143.independent-review-root.v1`, task `LIFEOS-P3-143`, owner `lifeos-p3-143-independent-review`, and `runId` `rereview3-20260902`.
- The provisional literal shown in `allowlist.md` is never created, used, or cleaned. This binding does not expand to any Pilot, retained root, personal data, credential, Keychain item, Provider, or network target; it only instantiates the one review-owned root class already sealed in the test design.

All later root operations must target the literal above, record pre/post state, and use marker-gated cleanup only.
