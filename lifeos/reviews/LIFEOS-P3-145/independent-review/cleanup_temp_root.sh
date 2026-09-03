#!/bin/sh
set -eu

ROOT='/private/tmp/lifeos-p3-145-independent-review-v1'
MARKER="$ROOT/.lifeos_p3_145_review_marker"
EXPECTED_MARKER_SHA='4b8b4cb1917051be1323a1f10be2fc0eb45c925d882554c001b8087dfda4450c'
PROJECT='/Users/xxe/.codex/worktrees/74a3/No.2'

test "$ROOT" = '/private/tmp/lifeos-p3-145-independent-review-v1'
test -d "$ROOT"
test -f "$MARKER"
test "$(shasum -a 256 "$MARKER" | awk '{print $1}')" = "$EXPECTED_MARKER_SHA"

git -C "$PROJECT" worktree remove --force "$ROOT/candidate" || true
if test -e "$ROOT/candidate"; then
  chmod -R u+w "$ROOT/candidate"
fi
rm -rf -- "$ROOT"
test ! -e "$ROOT"
printf '%s\n' 'marker_validated_cleanup=pass'
