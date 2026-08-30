# P3-141 Phase B Attempt 3 — Write Allowlist

## Permitted writes

1. `lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-3/**` — review-owned source, fixtures, synthetic SQLite evidence, logs, redacted captures, matrices, manifests, and reports.
2. `/private/tmp/lifeos-p3-141-controlled-pilot-v1/**` — synthetic build/runtime state only after writing a unique review marker; exact marker-gated cleanup only.

## Explicitly prohibited writes

- Candidate source, candidate Evidence, P3-137/P3-139/P3-140 assets, historical P3-141 reviews, PM ledger/status/risk/freeze files, any non-allowlisted `/private/tmp` path, all Pilot roots and databases, credentials, network targets, and external systems.

## Cleanup rule

Cleanup may target only the literal temporary root above, only after verifying the review marker at its direct child path. No glob, parent directory, discovery scan, or cleanup attempt is permitted outside that exact root.
