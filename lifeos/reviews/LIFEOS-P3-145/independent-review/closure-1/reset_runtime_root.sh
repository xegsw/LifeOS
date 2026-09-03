#!/bin/sh
set -eu

ROOT='/private/tmp/lifeos-p3-145-independent-review-v1'
MARKER="$ROOT/.lifeos-p3-145-owner.json"
EXPECTED_MARKER_SHA='bf3aef40c573413ad0d06611d869ee91e6335a805012223a5dc479b4492bcfbd'

test "$ROOT" = '/private/tmp/lifeos-p3-145-independent-review-v1'
test -d "$ROOT"
test -f "$MARKER"
test "$(stat -f '%HT' "$MARKER")" = 'Regular File'
test "$(stat -f '%Lp' "$MARKER")" = '600'
test "$(shasum -a 256 "$MARKER" | awk '{print $1}')" = "$EXPECTED_MARKER_SHA"
rm -rf -- "$ROOT"
test ! -e "$ROOT"
printf '%s\n' 'runtime_root_cleanup=pass'
