#!/bin/sh
set -eu

ROOT='/private/tmp/lifeos-p3-145-independent-review-closure-1'
MARKER="$ROOT/.lifeos_p3_145_closure_1_marker"
EXPECTED_MARKER_SHA='d33381cdad80bda69887e7dd6335edd977dbc2d13c22c95e42d8575a2de13eb0'
PROJECT='/Users/xxe/.codex/worktrees/74a3/No.2'

test "$ROOT" = '/private/tmp/lifeos-p3-145-independent-review-closure-1'
test -d "$ROOT"
test -f "$MARKER"
test "$(stat -f '%HT' "$MARKER")" = 'Regular File'
test "$(stat -f '%Lp' "$MARKER")" = '600'
test "$(shasum -a 256 "$MARKER" | awk '{print $1}')" = "$EXPECTED_MARKER_SHA"

git -C "$PROJECT" worktree remove --force "$ROOT/candidate" || true
if test -e "$ROOT/candidate"; then
  chmod -R u+w "$ROOT/candidate"
fi
rm -rf -- "$ROOT"
test ! -e "$ROOT"
printf '%s\n' 'closure_root_cleanup=pass'
