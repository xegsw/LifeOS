#!/bin/zsh
set -eu

TASK_ROOT=/Users/xxe/Documents/No.2
TASK_ENGINEERING=$TASK_ROOT/lifeos/engineering/LIFEOS-P3-131
TEMP_ROOT=/private/tmp/lifeos-p3-131-next-action-v1
RUN_ROOT=$TEMP_ROOT/run-test

mkdir -p "$RUN_ROOT" "$TEMP_ROOT/cache/clang-test" "$TEMP_ROOT/cache/swift-test" "$TASK_ENGINEERING/evidence/build-cache/test"
LIFEOS_RUNTIME_ROOT="$RUN_ROOT" \
CARGO_TARGET_DIR="$TASK_ENGINEERING/evidence/build-cache/test" \
CLANG_MODULE_CACHE_PATH="$TEMP_ROOT/cache/clang-test" \
SWIFT_MODULECACHE_PATH="$TEMP_ROOT/cache/swift-test" \
/Users/xxe/.cargo/bin/cargo test --locked --offline \
  --manifest-path "$TASK_ENGINEERING/candidate/Cargo.toml"
python3 -B "$TASK_ENGINEERING/tools/verify_evidence.py" closure --out "$TASK_ENGINEERING/evidence/closure-check.json"
python3 -B "$TASK_ENGINEERING/tools/verify_evidence.py" lineage --out "$TASK_ENGINEERING/evidence/source-lineage.json"
python3 -B "$TASK_ENGINEERING/tools/verify_evidence.py" scan --out "$TASK_ENGINEERING/evidence/source-scan.json"
python3 -B "$TASK_ENGINEERING/tools/verify_evidence.py" manifest --out "$TASK_ENGINEERING/evidence/FINAL_MANIFEST.json"
rm -rf /private/tmp/lifeos-p3-131-next-action-v1
test ! -e /private/tmp/lifeos-p3-131-next-action-v1
