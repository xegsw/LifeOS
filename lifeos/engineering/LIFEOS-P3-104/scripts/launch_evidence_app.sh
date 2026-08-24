#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FIXTURE_ROOT=/private/tmp/lifeos-p3-104-app-evidence
DB_PATH="$FIXTURE_ROOT/capture.sqlite"

if [ -e "$FIXTURE_ROOT" ]; then
  rm -rf "$FIXTURE_ROOT"
fi
mkdir "$FIXTURE_ROOT"
printf '%s\n' 'P3-104-SENTINEL' > "$FIXTURE_ROOT/sentinel.txt"

export RUSTUP_HOME=/Users/xxe/.rustup
export CARGO_HOME=/Users/xxe/.cargo
export CARGO_TARGET_DIR="$PROJECT_ROOT/.tooling/target"
export CARGO_NET_OFFLINE=true
export LIFEOS_P3_104_DB_PATH="$DB_PATH"

mkdir -p "$PROJECT_ROOT/evidence"
printf '%s\n' "$$" > "$PROJECT_ROOT/evidence/app.pid"
exec "$CARGO_TARGET_DIR/debug/bundle/macos/LifeOS P3-104.app/Contents/MacOS/lifeos-p3-104" \
  2> "$PROJECT_ROOT/evidence/ipc_trace.log"
