#!/bin/sh
set -eu

review_root="lifeos/reviews/LIFEOS-P3-141/independent-review"
temp_root="/private/tmp/lifeos-p3-141-controlled-pilot-v1"

test -f "$review_root/test_design.md"
test -f "$review_root/write_allowlist.md"
test -f "$review_root/precontact_seal.json"
test -f "$review_root/independent_review.md"
test -f "$review_root/phase_b_matrix.md"
test ! -e "$temp_root"
shasum -a 256 "$review_root/test_design.md" "$review_root/write_allowlist.md" "$review_root/precontact_seal.json" "$review_root/phase_b_matrix.md"
printf '%s\n' 'STARTUP_GATE_BLOCKED: missing frozen inputs and precontact-order violation; no candidate replay permitted.'
