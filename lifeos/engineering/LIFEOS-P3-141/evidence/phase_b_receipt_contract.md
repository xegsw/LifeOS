# P3-141 Phase-B independent Pass receipt contract

This is a public verifier contract, not a receipt and not a Phase-B result. An engineering worktree cannot produce an accepting asset. Only a later independent reviewer, working in its own clean Git worktree after reviewing the fixed candidate commit/tree, may write and commit the two assets below.

## Compile modes

`LIFEOS_P3_141_BUILD_MODE=synthetic_review` must pair with `LIFEOS_INPUT_MODE=synthetic` and must not receive a receipt path. It is the only mode used by normal Phase-A synthetic replay.

`LIFEOS_P3_141_BUILD_MODE=phase_c_real` must pair with `LIFEOS_INPUT_MODE=real_self_use` and must receive `LIFEOS_P3_141_PHASE_B_RECEIPT_PATH`. The verifier runs before `LIFEOS_RUNTIME_ROOT` is read. The retired `LIFEOS_P3_141_PHASE_B_RECEIPT` token is always a rejection.

## Review-owned placement and filesystem rules

The receipt path must be exactly under a separately owned Git worktree:

```text
<review-worktree>/lifeos/reviews/LIFEOS-P3-141/independent-review/<attempt-id>/
  phase_b_pass_receipt.json
  FINAL_MANIFEST.json
```

Both files must be existing canonical, single-link, read-only regular files with bounded size. Every ancestor must be a real directory, with no symlink. The worktree must be a clean Git checkout, the two bytestrings must equal `HEAD:path`, and its canonical Git top-level must differ from the candidate worktree. It must also be a declared peer worktree of the same Git common directory and filesystem owner; an unrelated local repository is not an independent-review authority. A candidate-contained path, directory, symlink, linked ancestor, untracked change, or altered history fails closed.

## Exact schemas

`phase_b_pass_receipt.json` has schema `lifeos.p3-141.phase-b-independent-pass-receipt.v1`, with no unknown or duplicate field at any depth:

```json
{
  "schema": "lifeos.p3-141.phase-b-independent-pass-receipt.v1",
  "task_id": "LIFEOS-P3-141",
  "task_sha256": "88b0dbcafd525604b08ebb0dffc07dc360635666612c87a2cdc94e661e72ac5a",
  "abf_id": "ABF-P3-141-v1",
  "abf_sha256": "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2",
  "candidate_commit": "40-lowercase-hex",
  "candidate_tree_sha256": "64-lowercase-hex",
  "verdict": "PASS",
  "review_identity": {"role": "independent_review", "attempt_id": "directory-name"},
  "review_manifest": {
    "file": "FINAL_MANIFEST.json",
    "sha256": "64-lowercase-hex",
    "schema": "lifeos.p3-141.phase-b-independent-manifest.v1"
  },
  "issued_at_utc": "RFC3339-UTC"
}
```

`FINAL_MANIFEST.json` has schema `lifeos.p3-141.phase-b-independent-manifest.v1`, exact top-level fields `schema`, `task_id`, `review_identity`, `review_conclusion`, `candidate_commit`, `candidate_tree_sha256`, `file_count_excluding_manifest`, `tree_sha256_excluding_manifest`, and `files`. Its conclusion must be `PASS`; its role/attempt/candidate fields must equal the receipt, and its SHA-256 must equal `review_manifest.sha256`.

The verifier obtains the candidate commit from the candidate worktree `HEAD` and independently calculates the framed candidate tree SHA-256 (path-length, path, content-length, content). Any changed candidate is therefore stale and blocked. This contract intentionally does not define an engineering-generated marker, a signature substitute, or a self-issued receipt.
