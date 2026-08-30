# Cleanup and replay plan

Before the receipt-gated Phase-C build, all generated assets are under the single authorized temporary root `/private/tmp/lifeos-p3-141-controlled-pilot-v1`; the only registered sub-worktree is its `candidate-peer`. No real Pilot root, database, text, Health value, credential, Provider target, or network target was contacted.

The replay sequence is fixed:

1. Commit the review-owned, non-self-referential evidence Manifest.
2. Create and commit the receipt that binds that exact Manifest.
3. From the clean detached candidate peer, run the one `phase_c_real` build gate using only a nonexistent synthetic runtime-root path and the committed peer receipt.
4. Remove the registered candidate peer with `git worktree remove`, then remove only the exact temporary root.

The executed cleanup receipt is deliberately produced after step 4 as a supplemental artifact, so it cannot create a circular dependency in the receipt-bound Manifest.
