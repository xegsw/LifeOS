# Phase-C v2 Independent Pass Receipt Contract

Only a future, review-owned, committed independent-review worktree may create this receipt. This engineering closure defines the verifier and schema; it does not create an acceptable independent Pass asset.

## Exact location and names

The explicit environment variable is `LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH`. Its canonical, regular, non-linked file must be named `phase_c_v2_independent_pass_receipt.json` in:

`<review-git-worktree>/lifeos/reviews/LIFEOS-P3-141/independent-review/<safe-attempt-id>/`

The same directory must contain a canonical, regular, non-linked `FINAL_MANIFEST.json`. The review worktree and candidate worktree must be clean, declared peer worktrees with the same Git common directory and owner. Any Phase-B environment variable/path is an unconditional rejection.

## Receipt schema

Schema: `lifeos.p3-141.phase-c-independent-pass-receipt.v2`.

Exactly these fields are accepted (unknown or duplicate fields reject):

- `schema`, `task_id`, `task_sha256`, `fixed_input_inventory_sha256`
- `abf_id`, `abf_sha256`
- `candidate_commit`, `candidate_tree_sha256`, `verdict`
- `review_identity` with exactly `role`, `attempt_id`
- `review_manifest` with exactly `file`, `sha256`, `schema`
- `issued_at_utc`

Required frozen values are task `LIFEOS-P3-141`, Revision-2 task SHA `c97419a1818e0aa6fe6fc61c487e3ef97746e199b2c7d22435d8c05090374800`, Revision-2 inventory SHA `3651e046da8211f06bf5144a155a0505b7ddfbaab67a249e51d94aeae09861a5`, ABF `ABF-P3-141-v2`, and ABF SHA `096ad12beec63b78aaa3be92535b4a6ea632cdc4235c1d83f224db955d5dc9ea`.

`verdict` must be `PASS`; `candidate_commit` and `candidate_tree_sha256` must exactly match the clean candidate worktree's current `HEAD` and recomputed candidate tree at Phase-C build time.

## Independent Manifest schema

Schema: `lifeos.p3-141.independent-review-manifest.v2`. It must have no unknown/duplicate fields and must carry exactly the same Revision-2 task/inventory/ABF values, `review_identity`, `review_conclusion=PASS`, candidate commit/tree, a nonzero file count, a lowercase 64-character tree hash and an object-valued file inventory. Its SHA-256 must exactly equal the receipt's `review_manifest.sha256`.

No v1 ID/hash/schema/file name, attempt-8 receipt, old candidate/tree, old Manifest, Rework/Blocked verdict, fallback field, dirty worktree, path link, ancestor link, directory, malformed JSON, duplicate field or extra field can reach runtime-root resolution.
