#!/bin/sh
set -eu

review_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$review_dir"

check_file() {
  expected=$1
  file=$2
  actual=$(shasum -a 256 "$file" | awk '{print $1}')
  if [ "$actual" != "$expected" ]; then
    printf 'FAIL hash %s\n' "$file" >&2
    exit 1
  fi
}

# Expected values are patched after the review-owned documents are finalized.
check_file 'dfdf18146013476f9de73caada8587a92bfa8e3992cb0b5372c2c613781b9e4e' input_availability.json
check_file 'b634d29d0e581c810b8d1c1f66aa514e3e874dcafa7c6e9899c7b94fd8e4e97f' review_matrix.md
check_file 'ba1f89c476c89ba2107efd6ed7dc748a0d70789bff5d4cf7c4b4e5cb214fb938' checkpoint.json
check_file '7ded3a813283da290c9a01e0cb99782fca590eb0c784bacf90647d666feb6ed1' independent_review.md
check_file '71c36f4bea435abd98077c71b91402aeb011c8e291243ccbc290e13192c41c84' test_design.md
check_file '9e546ca1b51a6367494ea1bc68c09c30e6b352eb1bfaf189f7e1cae766ad37ee' allowlist.txt
check_file '3fe1c6d21882963a58ad74e0d0522e50990ff60b98fe144f005d00977d826075' prohibited_paths.md
check_file 'f26f865ea06852efdda220cb69c4c9e78f95d6faf3d7c43f0d76e2cf42e53ba5' precontact_seal.json

grep -F '"self_referential": false' FINAL_MANIFEST.json >/dev/null
grep -F '"entry_count": 10' FINAL_MANIFEST.json >/dev/null
grep -F '"path": "input_availability.json", "bytes": 1149, "sha256": "dfdf18146013476f9de73caada8587a92bfa8e3992cb0b5372c2c613781b9e4e"' FINAL_MANIFEST.json >/dev/null
grep -F '"path": "review_matrix.md", "bytes": 1451, "sha256": "b634d29d0e581c810b8d1c1f66aa514e3e874dcafa7c6e9899c7b94fd8e4e97f"' FINAL_MANIFEST.json >/dev/null
grep -F '"path": "checkpoint.json", "bytes": 669, "sha256": "ba1f89c476c89ba2107efd6ed7dc748a0d70789bff5d4cf7c4b4e5cb214fb938"' FINAL_MANIFEST.json >/dev/null
grep -F '"path": "independent_review.md", "bytes": 4158, "sha256": "7ded3a813283da290c9a01e0cb99782fca590eb0c784bacf90647d666feb6ed1"' FINAL_MANIFEST.json >/dev/null
grep -F '"path": "review_verifier.sh"' FINAL_MANIFEST.json >/dev/null
grep -F '"status": "BLOCKED_MISSING_EXACT_HISTORICAL_INPUTS"' input_availability.json >/dev/null
grep -F 'Result: **Blocked**' review_matrix.md >/dev/null
printf 'PASS review-owned blocked-package integrity\n'
