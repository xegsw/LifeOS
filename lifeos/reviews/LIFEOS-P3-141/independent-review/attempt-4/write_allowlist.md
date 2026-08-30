# Attempt 4 write allowlist

Allowed writes are limited to:

1. `lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-4/**` for
   review-owned design, source, fixtures, structured evidence, screenshots,
   hashes, manifest, and final report.
2. `/private/tmp/lifeos-p3-141-controlled-pilot-v1/**` only after creation of
   the review marker, only for fictional disposable source copies, builds,
   synthetic SQLite databases, runtime logs, and screenshots, and only until
   marker-gated literal cleanup.

Explicitly disallowed writes include the candidate, all engineering evidence,
all PM/governance ledgers, any historic review, any external service, every
real/Pilot asset, and every path not listed above.  No cleanup may use a glob,
parent directory, unresolved variable, or inferred target.
