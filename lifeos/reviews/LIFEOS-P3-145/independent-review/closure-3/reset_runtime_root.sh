#!/bin/zsh
set -euo pipefail

runtime_root='/private/tmp/lifeos-p3-145-independent-review-v1'
marker="$runtime_root/.lifeos-p3-145-owner.json"
test -d "$runtime_root" && test ! -L "$runtime_root"
test -f "$marker" && test ! -L "$marker"
test "$(stat -f '%Lp' "$marker")" = '600'
test "$(shasum -a 256 "$marker" | awk '{print $1}')" = 'bf3aef40c573413ad0d06611d869ee91e6335a805012223a5dc479b4492bcfbd'
rm -rf -- "$runtime_root"
test ! -e "$runtime_root"
printf 'closure-3 synthetic runtime root removed after marker validation\n'
