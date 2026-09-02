# Review-owned lineage verifier Closure 1

The first run at `evidence/lineage_verification.json` intentionally remains read-only history. It failed only because this review-owned verifier expected 75 candidate entries. The sealed Closure-1 manifest itself declares 85 candidate entries, and the actual candidate tree contains the same 85 paths.

This was a review-tool expectation defect, not a candidate mutation or a change to any frozen input. The verifier was corrected from 75 to 85 without changing its hash checks, extra/missing-path detection, fixed-commit binding, or any candidate file. The corrected run is recorded separately at `evidence/lineage_verification_closure_1.json`.
