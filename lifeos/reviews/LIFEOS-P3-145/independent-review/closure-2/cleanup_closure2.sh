#!/bin/zsh
set -euo pipefail

review_repo='/Users/xxe/.codex/worktrees/74a3/No.2'
closure_root='/private/tmp/lifeos-p3-145-independent-review-closure-2'
candidate_root='/private/tmp/lifeos-p3-145-independent-review-closure-2/candidate'
runtime_root='/private/tmp/lifeos-p3-145-independent-review-v1'
closure_marker="$closure_root/.lifeos_p3_145_closure_2_marker"
runtime_marker="$runtime_root/.lifeos-p3-145-owner.json"

test -d "$closure_root" && test ! -L "$closure_root"
test -f "$closure_marker" && test ! -L "$closure_marker"
test "$(stat -f '%Lp' "$closure_marker")" = '600'
test "$(shasum -a 256 "$closure_marker" | awk '{print $1}')" = '5e162e5c07fc226dac2a7ee4614a2392520536d2e73a18b9077efa031d9435d7'

test -d "$runtime_root" && test ! -L "$runtime_root"
test -f "$runtime_marker" && test ! -L "$runtime_marker"
test "$(stat -f '%Lp' "$runtime_marker")" = '600'
test "$(shasum -a 256 "$runtime_marker" | awk '{print $1}')" = 'bf3aef40c573413ad0d06611d869ee91e6335a805012223a5dc479b4492bcfbd'

test -d "$candidate_root" && test ! -L "$candidate_root"
chmod -R u+w "$candidate_root"
if git -C "$review_repo" worktree list --porcelain | rg -qx "worktree $candidate_root"; then
  test -z "$(git -C "$candidate_root" status --porcelain)"
  git -C "$review_repo" worktree remove --force "$candidate_root"
else
  # A prior failed Git removal can deregister the worktree before it removes
  # this exact, marker-guarded temporary directory. It is no longer a Git worktree.
  rm -rf -- "$candidate_root"
fi
test ! -e "$candidate_root"

rm -rf -- "$runtime_root"
test ! -e "$runtime_root"
rm -rf -- "$closure_root"
test ! -e "$closure_root"

printf 'closure-2 cleanup verified: runtime root, detached candidate, and build root removed\n'
