#!/bin/zsh
set -euo pipefail

repo='/Users/xxe/.codex/worktrees/74a3/No.2'
closure_root='/private/tmp/lifeos-p3-145-independent-review-closure-3'
candidate_root='/private/tmp/lifeos-p3-145-independent-review-closure-3/candidate'
runtime_root='/private/tmp/lifeos-p3-145-independent-review-v1'
closure_marker="$closure_root/.lifeos_p3_145_closure_3_marker"
runtime_marker="$runtime_root/.lifeos-p3-145-owner.json"

test -z "$(pgrep -x lifeos-p3-145 || true)"
test -d "$closure_root" && test ! -L "$closure_root"
test -f "$closure_marker" && test ! -L "$closure_marker"
test "$(stat -f '%Lp' "$closure_marker")" = '600'
test "$(shasum -a 256 "$closure_marker" | awk '{print $1}')" = '5c2d573969280b386631ede029cd795355997ce30b24d2eba710417dd4947a79'

test -d "$runtime_root" && test ! -L "$runtime_root"
test -f "$runtime_marker" && test ! -L "$runtime_marker"
test "$(stat -f '%Lp' "$runtime_marker")" = '600'
test "$(shasum -a 256 "$runtime_marker" | awk '{print $1}')" = 'bf3aef40c573413ad0d06611d869ee91e6335a805012223a5dc479b4492bcfbd'

test -d "$candidate_root" && test ! -L "$candidate_root"
chmod -R u+w "$candidate_root"
if git -C "$repo" worktree list --porcelain | /usr/bin/grep -Fx "worktree $candidate_root" >/dev/null; then
  git -C "$repo" worktree remove --force "$candidate_root"
else
  rm -rf -- "$candidate_root"
fi
test ! -e "$candidate_root"

rm -rf -- "$runtime_root"
test ! -e "$runtime_root"
rm -rf -- "$closure_root"
test ! -e "$closure_root"
printf 'closure-3 cleanup verified: candidate worktree and both exact temporary roots absent\n'
