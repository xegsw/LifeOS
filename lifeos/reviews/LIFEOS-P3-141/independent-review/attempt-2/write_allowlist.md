# LIFEOS-P3-141 Phase B Independent Review — Write Allowlist

## Permitted writes

1. `lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/**`
2. `/private/tmp/lifeos-p3-141-controlled-pilot-v1/**` during review-owned,
   synthetic execution only.

## Permitted read-only inputs after precontact seal

- PM frozen inputs and fixed-input inventory.
- P3-141 candidate root, read-only.
- P3-141 prior review attempts excluding this attempt, read-only.
- Explicitly listed P3-137/P3-139/P3-140 historical inputs, read-only.

## Explicitly prohibited actions

- Any write, create, copy, cleanup, metadata probe, hash, or inventory outside
  the two permitted write roots.
- Any interaction with retained Pilots, real data stores, real files, real
  health data, credentials, or external Provider/network targets.
- Any candidate or historical-asset modification, including generated caches,
  build output, test fixtures, screenshots, logs, or manifests.
- Any source of positive evidence other than a review-owned test, receipt,
  screenshot, or verifier result.
- Any Phase C action or claim.

## Cleanup rule

Cleanup may target only the literal task-local temporary root above and only
after its review-owned path is established.  Retained assets are never cleanup
targets.
