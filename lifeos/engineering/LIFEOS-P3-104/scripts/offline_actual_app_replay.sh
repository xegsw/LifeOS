#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FIXTURE_BASE=/private/tmp/lifeos-p3-104-rework-replay
NORMAL_ROOT="$FIXTURE_BASE-normal"
DANGLING_ROOT="$FIXTURE_BASE-dangling"
BUNDLE="$PROJECT_ROOT/.tooling/target/debug/bundle/macos/LifeOS P3-104.app"
APP_EXECUTABLE="$BUNDLE/Contents/MacOS/lifeos-p3-104"

export RUSTUP_HOME=/Users/xxe/.rustup
export CARGO_HOME=/Users/xxe/.cargo
export CARGO_TARGET_DIR="$PROJECT_ROOT/.tooling/target"
export CARGO_NET_OFFLINE=true
export CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

cleanup_root() {
  target=$1
  case "$target" in
    /private/tmp/lifeos-p3-104-rework-replay-normal|/private/tmp/lifeos-p3-104-rework-replay-dangling) ;;
    *) echo "cleanup target rejected: $target" >&2; exit 2 ;;
  esac
  if [ -L "$target" ]; then
    echo "cleanup root symlink rejected: $target" >&2
    exit 2
  fi
  if [ -e "$target" ]; then
    rm -rf -- "$target"
  fi
}

app_pid() {
  pgrep -f "$APP_EXECUTABLE" | head -n 1 || true
}

wait_for_start() {
  attempts=0
  while [ "$attempts" -lt 40 ]; do
    pid=$(app_pid)
    if [ -n "$pid" ]; then
      printf '%s\n' "$pid"
      return 0
    fi
    attempts=$((attempts + 1))
    sleep 0.1
  done
  return 1
}

stop_app() {
  pid=$1
  case "$pid" in
    ''|*[!0-9]*) echo "invalid app pid" >&2; exit 2 ;;
  esac
  kill -TERM "$pid"
  attempts=0
  while kill -0 "$pid" 2>/dev/null; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 40 ]; then
      echo "app did not stop after TERM" >&2
      exit 2
    fi
    sleep 0.1
  done
}

launch_app() {
  db_path=$1
  stdout_path=$2
  stderr_path=$3
  open -n -g -F \
    --stdout "$stdout_path" \
    --stderr "$stderr_path" \
    --env "LIFEOS_P3_104_DB_PATH=$db_path" \
    --env "CARGO_NET_OFFLINE=true" \
    "$BUNDLE"
}

cd "$PROJECT_ROOT"
cleanup_root "$NORMAL_ROOT"
cleanup_root "$DANGLING_ROOT"

echo "REPLAY-00 clean task-local Cargo target"
"$CARGO_HOME/bin/cargo" clean

echo "REPLAY-01 build exact unsigned debug app bundle offline and locked"
"$CARGO_HOME/bin/cargo" tauri build \
  --debug \
  --bundles app \
  --no-sign \
  --config '{"bundle":{"active":true,"targets":["app"]}}' \
  -- --locked
test -x "$APP_EXECUTABLE"
shasum -a 256 Cargo.lock "$APP_EXECUTABLE"

echo "REPLAY-02 launch, stop, and reopen the exact bundle"
mkdir "$NORMAL_ROOT"
printf '%s\n' 'P3-104-REWORK-NORMAL-SENTINEL' > "$NORMAL_ROOT/sentinel.txt"
launch_app "$NORMAL_ROOT/capture.sqlite" "$NORMAL_ROOT/first.stdout.log" "$NORMAL_ROOT/first.stderr.log"
first_pid=$(wait_for_start)
echo "normal_first_start=PASS"
stop_app "$first_pid"
echo "normal_first_stop=PASS"
launch_app "$NORMAL_ROOT/capture.sqlite" "$NORMAL_ROOT/reopen.stdout.log" "$NORMAL_ROOT/reopen.stderr.log"
reopen_pid=$(wait_for_start)
echo "normal_reopen=PASS"
stop_app "$reopen_pid"
echo "normal_reopen_stop=PASS"
test ! -e "$NORMAL_ROOT/capture.sqlite"
test "$(cat "$NORMAL_ROOT/sentinel.txt")" = "P3-104-REWORK-NORMAL-SENTINEL"

echo "REPLAY-03 reject dangling final capture.sqlite in the actual app"
mkdir "$DANGLING_ROOT"
printf '%s\n' 'P3-104-REWORK-DANGLING-SENTINEL' > "$DANGLING_ROOT/sentinel.txt"
missing_target="$DANGLING_ROOT/missing.sqlite"
ln -s "$missing_target" "$DANGLING_ROOT/capture.sqlite"
sentinel_before=$(shasum -a 256 "$DANGLING_ROOT/sentinel.txt" | awk '{print $1}')
launch_app "$DANGLING_ROOT/capture.sqlite" "$DANGLING_ROOT/app.stdout.log" "$DANGLING_ROOT/app.stderr.log"
sleep 1
test -z "$(app_pid)"
echo "dangling_app_process=0"
echo "dangling_success_ui=not_rendered"
grep -F "controlled DB boundary rejected: database_type_rejected" "$DANGLING_ROOT/app.stderr.log"
test -L "$DANGLING_ROOT/capture.sqlite"
test "$(readlink "$DANGLING_ROOT/capture.sqlite")" = "$missing_target"
test ! -e "$missing_target"
sentinel_after=$(shasum -a 256 "$DANGLING_ROOT/sentinel.txt" | awk '{print $1}')
test "$sentinel_before" = "$sentinel_after"
test "$(find -P "$DANGLING_ROOT" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')" = "4"
test -z "$(find -P "$DANGLING_ROOT" -mindepth 1 -maxdepth 1 \( -name '*.shadow' -o -name 'capture.sqlite-journal' -o -name 'capture.sqlite-wal' -o -name 'capture.sqlite-shm' \) -print)"
echo "dangling_final_symlink_rejected=PASS"
echo "dangling_link_preserved=PASS"
echo "dangling_target_missing=PASS"
echo "dangling_sentinel_unchanged=PASS"
echo "dangling_residue_zero=PASS"

echo "REPLAY-04 exact cleanup"
cleanup_root "$NORMAL_ROOT"
cleanup_root "$DANGLING_ROOT"
test ! -e "$NORMAL_ROOT"
test ! -e "$DANGLING_ROOT"
echo "cleanup_residual=0"
echo "RESULT=PASS"
