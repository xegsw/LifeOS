# LIFEOS-P3-127 PM Acceptance Evidence Manifest

- PM result: `PASS`
- Acceptance basis: `ABF-P3-127-v1`
- Scope: PM read-only verification of the submitted independent review and its preserved Evidence.

| Asset | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review.md` | `3504a3e2a6f642df8dbe32f65c7a880d18d6ed0670785f01caa0832fd764e988` |
| `lifeos/tasks/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md` | `f44199a28d023d94e9bd5a4150f9e83b67e4919ea1a7b349756f34f51c049666` |
| `lifeos/tasks/LIFEOS-P3-127_source_allowlist.md` | `5d45d86656cc60f7d13d8a5b9851dfeea969814f9f22eb571365d1ae712ef72e` |
| `lifeos/reviews/LIFEOS-P3-127/independent_review.md` | `0877d69b7205fdbadbce1d352b338d0a500c7bfd1f39cff87b18a3b3bc0d63f7` |
| `lifeos/deliverables/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review.md` | `d7f2695bd213d7e49565b731e6c7ed9e23faaeb99a271cd7cd08078c53f14b7c` |
| `lifeos/reviews/LIFEOS-P3-127/FINAL_MANIFEST.json` | `b6bac5396758cdb7b704a482ba620f996c5416643286fa6af8d0538fadc0a497` |
| `lifeos/reviews/LIFEOS-P3-127/pm_evidence/acceptance/verification.json` | `6b39129b9c1343692250e918986891f756d71141f75bf3aba73d4b68353f0d7c` |
| `lifeos/reviews/LIFEOS-P3-127_pm_review.md` | `f3d40a1c3d1341878e170d28c2dce9b9fa877122ab8e8277d7b18507dc511cd3` |

## Verification Summary

- Final Manifest: `59/59`, zero byte/hash errors, non-self-referential.
- Candidate lineage: `75/75`, zero failures.
- P3-126 historical assets: `123/123`, zero failures.
- Frozen matrix: `12/12 PASS`.
- Actual Tauri: two fresh synthetic runtime roots; only `capture_record`, `get_today`, `runtime_status`.
- Mutation controls: content, missing-file and symlink mutations all rejected.
- Cleanup: `/private/tmp/lifeos-p3-127-independent-review-v1` absent after exact cleanup.
- Final counts: `P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0`.

This Manifest intentionally excludes its own hash.
