#!/bin/zsh
# Actual-app launch/reopen verifier. It deliberately performs no GUI injection or scraper action.
set -euo pipefail

P3_120_TEMP_ROOT="${P3_120_TEMP_ROOT:-/private/tmp/lifeos-p3-120-runtime-mvp-v1}"
P3_120_APP_BINARY="$P3_120_TEMP_ROOT/cargo-target/release/bundle/macos/LifeOS P3-120 Synthetic Runtime MVP.app/Contents/MacOS/lifeos-p3-120"
P3_120_TRACE="$P3_120_TEMP_ROOT/actual-app-process.trace"

if [[ ! -x "$P3_120_APP_BINARY" ]]; then
  print -u2 "missing actual app: $P3_120_APP_BINARY"
  exit 1
fi

: > "$P3_120_TRACE"

replay_once() {
  local label="$1"
  local log_path="$P3_120_TEMP_ROOT/$label.stdout.log"
  "$P3_120_APP_BINARY" >"$log_path" 2>&1 &
  local app_pid=$!
  sleep 5
  if ! kill -0 "$app_pid" 2>/dev/null; then
    print -u2 "$label process exited before startup verification"
    exit 1
  fi
  local trace_line="$label pid=$app_pid alive_after_5s=true"
  print "$trace_line"
  print "$trace_line" >> "$P3_120_TRACE"
  kill -TERM "$app_pid" 2>/dev/null || true
  wait "$app_pid" 2>/dev/null || true
}

replay_once app-launch
replay_once app-reopen
