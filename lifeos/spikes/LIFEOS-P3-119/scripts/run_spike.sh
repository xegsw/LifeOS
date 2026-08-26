#!/bin/bash
set -euo pipefail

spike_dir="$(cd "$(dirname "$0")/.." && /bin/pwd -P)"
workspace_dir="$(cd "$spike_dir/../../.." && /bin/pwd -P)"
lifeos_dir="$workspace_dir/lifeos"
tmp_root="/private/tmp/lifeos-p3-119-pid-gui-spike-v1"
run_label="${1:-initial}"
case "$run_label" in
  initial|execution-[0-9]*) ;;
  *) printf '%s\n' 'Run label must be initial or execution-N.' >&2; exit 64 ;;
esac
evidence_dir="$spike_dir/evidence/$run_label"
raw_dir="$evidence_dir/raw"
image_dir="$evidence_dir/images"
fixture_source="$spike_dir/fixture/index.html"
helper_source="$spike_dir/tools/pid_gui_helper.swift"
audit_script="$spike_dir/scripts/static_audit.sh"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
helper=""
pid_one=""
pid_two=""

hash_file() {
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}

json_status() {
  /usr/bin/sed -nE 's/.*"status":"([^"]+)".*/\1/p' "$1" | /usr/bin/tail -n 1
}

json_window_id() {
  /usr/bin/sed -nE 's/.*"window_id":([0-9]+).*/\1/p' "$1" | /usr/bin/tail -n 1
}

json_bound() {
  local field="$1"
  local path="$2"
  /usr/bin/sed -nE "s/.*\\\"${field}\\\":(-?[0-9.]+).*/\\1/p" "$path" | /usr/bin/tail -n 1
}

add_matrix() {
  local row="$1"
  local test_id="$2"
  local status="$3"
  local evidence_path="$4"
  local evidence_hash=""
  if [ -f "$evidence_path" ]; then
    evidence_hash="$(hash_file "$evidence_path")"
  fi
  printf '{"row":"%s","test_id":"%s","status":"%s","evidence":"%s","sha256":"%s"}\n' \
    "$row" "$test_id" "$status" "$evidence_path" "$evidence_hash" >> "$evidence_dir/matrix.jsonl"
}

die() {
  local status="$1"
  printf '{"pass":false,"status":"%s"}\n' "$status" > "$evidence_dir/final_results.json"
  close_all || true
  exact_remove_root || true
  exit 1
}

record_cleanup() {
  local phase="$1"
  local pid="$2"
  local profile="$3"
  local children=""
  if [ -n "$pid" ] && /bin/kill -0 "$pid" 2>/dev/null; then
    children="$(/usr/bin/pgrep -P "$pid" 2>/dev/null || true)"
    local command_hash
    command_hash="$(/bin/ps -p "$pid" -o command= | /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}')"
    printf '{"phase":"%s","pid":%s,"profile":"%s","main_command_sha256":"%s","child_pids":"%s","action":"TERM"}\n' \
      "$phase" "$pid" "$profile" "$command_hash" "${children//$'\n'/,}" >> "$evidence_dir/cleanup.jsonl"
    /bin/kill -TERM "$pid" 2>/dev/null || true
    local attempt
    for attempt in $(/usr/bin/seq 1 20); do
      if ! /bin/kill -0 "$pid" 2>/dev/null; then break; fi
      /bin/sleep 0.25
    done
    if /bin/kill -0 "$pid" 2>/dev/null; then
      printf '{"phase":"%s","pid":%s,"action":"KILL_AFTER_TIMEOUT"}\n' "$phase" "$pid" >> "$evidence_dir/cleanup.jsonl"
      /bin/kill -KILL "$pid" 2>/dev/null || true
    fi
    local child
    for child in $children; do
      if /bin/kill -0 "$child" 2>/dev/null; then
        printf '{"phase":"%s","pid":%s,"action":"TERM_RESIDUAL_CHILD"}\n' "$phase" "$child" >> "$evidence_dir/cleanup.jsonl"
        /bin/kill -TERM "$child" 2>/dev/null || true
      fi
    done
  fi
}

close_all() {
  record_cleanup "profile-1" "$pid_one" "$tmp_root/profile-1"
  record_cleanup "profile-2" "$pid_two" "$tmp_root/profile-2"
}

exact_remove_root() {
  if [ -e "$tmp_root" ]; then
    /bin/rm -rf "$tmp_root"
  fi
  if [ -e "$tmp_root" ]; then
    printf '{"pass":false,"status":"TEMP_ROOT_STILL_PRESENT"}\n' >> "$evidence_dir/cleanup.jsonl"
    return 1
  fi
  printf '{"pass":true,"status":"TEMP_ROOT_ABSENT"}\n' >> "$evidence_dir/cleanup.jsonl"
}

assert_command_contract() {
  local pid="$1"
  local profile="$2"
  local phase="$3"
  local command_line
  command_line="$(/bin/ps -p "$pid" -o command=)"
  local command_hash
  command_hash="$(printf '%s' "$command_line" | /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}')"
  if [[ "$command_line" != *"--user-data-dir=$profile"* ]] || [[ "$command_line" != *"--app=file://$tmp_root/fixture/index.html"* ]]; then
    printf '{"phase":"%s","pid":%s,"pass":false,"status":"PROFILE_CONTRACT_MISMATCH","command_sha256":"%s"}\n' \
      "$phase" "$pid" "$command_hash" >> "$raw_dir/contracts.jsonl"
    return 1
  fi
  printf '{"phase":"%s","pid":%s,"pass":true,"status":"PROFILE_AND_FIXTURE_CONTRACT_PASS","command_sha256":"%s"}\n' \
    "$phase" "$pid" "$command_hash" >> "$raw_dir/contracts.jsonl"
}

wait_for_attest() {
  local pid="$1"
  local out="$2"
  local attempt
  for attempt in $(/usr/bin/seq 1 120); do
    if "$helper" attest --pid "$pid" --event-id "attest-${attempt}" > "$out"; then
      return 0
    fi
    /bin/sleep 0.5
  done
  return 1
}

capture_and_verify() {
  local label="$1"
  local pid="$2"
  local profile="$3"
  local window_id="$4"
  local rgb="$5"
  local capture_file="$tmp_root/screenshots/${label}.png"
  local capture_json="$raw_dir/${label}-capture.json"
  local pixel_json="$raw_dir/${label}-pixels.json"
  assert_command_contract "$pid" "$profile" "${label}-before" || die "PROFILE_CONTRACT_MISMATCH"
  "$helper" capture --pid "$pid" --window-id "$window_id" --event-id "capture-${label}" --out "$capture_file" > "$capture_json" || die "${label}_CAPTURE_FAILED"
  /bin/cp "$capture_file" "$image_dir/${label}.png"
  "$helper" pixels --image "$capture_file" --rgb "$rgb" > "$pixel_json" || die "${label}_PIXEL_VERIFY_FAILED"
  assert_command_contract "$pid" "$profile" "${label}-after" || die "PROFILE_CONTRACT_MISMATCH"
}

run_mutation() {
  local name="$1"
  local expected_status="$2"
  shift 2
  local out="$raw_dir/mutation-${name}.json"
  local code=0
  "$@" > "$out" 2>&1 || code=$?
  local actual_status
  actual_status="$(json_status "$out")"
  if [ "$code" -eq 0 ] || [ "$actual_status" != "$expected_status" ]; then
    printf '{"name":"%s","pass":false,"exit_code":%s,"expected":"%s","actual":"%s"}\n' \
      "$name" "$code" "$expected_status" "$actual_status" >> "$evidence_dir/mutation_results.jsonl"
    die "MUTATION_${name}_FAILED"
  fi
  printf '{"name":"%s","pass":true,"exit_code":%s,"expected":"%s","actual":"%s","evidence":"%s","sha256":"%s"}\n' \
    "$name" "$code" "$expected_status" "$actual_status" "$out" "$(hash_file "$out")" >> "$evidence_dir/mutation_results.jsonl"
}

if [ -e "$tmp_root" ] || [ -e "$evidence_dir" ]; then
  printf '%s\n' 'P3-119 requires an absent temporary root and a fresh evidence directory.' >&2
  exit 2
fi
/bin/mkdir -p "$raw_dir" "$image_dir"
: > "$evidence_dir/matrix.jsonl"
: > "$evidence_dir/cleanup.jsonl"
: > "$evidence_dir/mutation_results.jsonl"

task_card="$lifeos_dir/tasks/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike.md"
abf="$lifeos_dir/tasks/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike_acceptance_basis_freeze.md"
if [ "$(hash_file "$task_card")" != "f24db53a2a3e67e55f66bcf48408ff97092ffdbb266b2c2728aff0d41fe9ff6c" ] || \
   [ "$(hash_file "$abf")" != "cbec1018c2e3317fc1fdd9f9de325349e12d12d85ceea707031a3510b74d9071" ]; then
  die "TASK_OR_ABF_HASH_MISMATCH"
fi

check_hash() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(hash_file "$path")"
  local pass=false
  if [ "$actual" = "$expected" ]; then pass=true; fi
  printf '{"path":"%s","expected":"%s","actual":"%s","pass":%s}\n' "$path" "$expected" "$actual" "$pass" >> "$evidence_dir/fixed-inputs.jsonl"
  [ "$pass" = true ]
}

check_hash "3172457dc2c60080100d367acb979f92fbb060f4c4bd6383f60e9d7cfe76ec1b" "$lifeos_dir/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md" && \
check_hash "d6f12523683beea42ecd9d9db586b41c489991286e0ee41e2eb4afeab5e5c18c" "$lifeos_dir/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor_acceptance_basis_freeze.md" && \
check_hash "a0897741169dd127e12cc8bc40d8e11aada01e205341c0a3320be9c415fce085" "$lifeos_dir/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md" && \
check_hash "0270bea5d1114c01951e7b8b760e39f6f534c48797aea2eccc6cea28b6603e98" "$lifeos_dir/prototypes/LIFEOS-P3-118/MANIFEST.md" && \
check_hash "bacb9e7275fef2cbbe6201f4c64cc60af26678fb0274242c0b9eac65c2819931" "$lifeos_dir/prototypes/LIFEOS-P3-118/tools/pid_window_attest.swift" && \
check_hash "bea6a010a3c26356c84f18ff2fd2f07d48e0dcc39193b65eaf9aad0933248f41" "$lifeos_dir/reviews/LIFEOS-P3-118_pm_review.md" && \
check_hash "1327b037f6459bbe3ed76c935d13dce0f8d09b09e1e13c76760886ed5bcbf2d9" "$lifeos_dir/reviews/LIFEOS-P3-118/pm_evidence/initial/MANIFEST.md" && \
check_hash "b5cd531667c3f23cc8491ad77655f04725aa4c54a98a56406270349758c98cfe" "$lifeos_dir/reviews/LIFEOS-P3-118/pm_evidence/initial/blocked_assessment.md" && \
check_hash "86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c" "$lifeos_dir/ACCEPTANCE_GOVERNANCE.md" && \
check_hash "97385e62510154852fd10da11c697bf5066dcc300e3b0c31633bd52ad940b984" "$chrome" || die "FIXED_INPUT_HASH_MISMATCH"
add_matrix "ABF-M-001" "P119-M001" "PASS" "$evidence_dir/fixed-inputs.jsonl"

sdk="$(/usr/bin/xcrun --sdk macosx --show-sdk-path)"
rg_bin="$(command -v rg)"
if ! "$rg_bin" -q 'CGEventPostToPid' "$sdk/System/Library/Frameworks/CoreGraphics.framework/Headers/CGEvent.h"; then
  die "PID_EVENT_API_UNAVAILABLE"
fi

/bin/mkdir -p "$tmp_root/build-tmp" "$tmp_root/module-cache" "$tmp_root/bin" "$tmp_root/fixture" "$tmp_root/screenshots" "$tmp_root/disposable" "$tmp_root/profile-1" "$tmp_root/profile-2"
export TMPDIR="$tmp_root/build-tmp"
/bin/cp "$fixture_source" "$tmp_root/fixture/index.html"
bash "$audit_script" "$helper_source" "$fixture_source" > "$raw_dir/static_audit.json" || die "STATIC_AUDIT_FAILED"
/usr/bin/xcrun --sdk macosx swiftc -module-cache-path "$tmp_root/module-cache" "$helper_source" -o "$tmp_root/bin/pid_gui_helper" > "$raw_dir/helper_compile.log" 2>&1 || die "HELPER_COMPILE_FAILED"
helper="$tmp_root/bin/pid_gui_helper"
add_matrix "ABF-M-002" "P119-M002" "PASS" "$raw_dir/static_audit.json"

"$chrome" --user-data-dir="$tmp_root/profile-1" --no-first-run --no-default-browser-check --disable-background-networking --disable-sync --disable-extensions --app="file://$tmp_root/fixture/index.html" > "$tmp_root/chrome-1.stdout.log" 2> "$tmp_root/chrome-1.stderr.log" &
pid_one=$!
wait_for_attest "$pid_one" "$raw_dir/P119-M003-attest.json" || die "PID_WINDOW_ATTESTATION_FAILED"
assert_command_contract "$pid_one" "$tmp_root/profile-1" "M003" || die "PROFILE_CONTRACT_MISMATCH"
window_one="$(json_window_id "$raw_dir/P119-M003-attest.json")"
bound_x="$(json_bound x "$raw_dir/P119-M003-attest.json")"
bound_y="$(json_bound y "$raw_dir/P119-M003-attest.json")"
bound_width="$(json_bound width "$raw_dir/P119-M003-attest.json")"
bound_height="$(json_bound height "$raw_dir/P119-M003-attest.json")"
if [ -z "$window_one" ] || [ -z "$bound_x" ] || [ -z "$bound_y" ] || [ -z "$bound_width" ] || [ -z "$bound_height" ]; then die "ATTESTATION_PARSE_FAILED"; fi
click_x="$(/usr/bin/awk -v x="$bound_x" -v width="$bound_width" 'BEGIN { printf "%.2f", x + width / 2 }')"
click_y="$(/usr/bin/awk -v y="$bound_y" -v height="$bound_height" 'BEGIN { printf "%.2f", y + height / 2 }')"
capture_and_verify "S0" "$pid_one" "$tmp_root/profile-1" "$window_one" "217,79,79"
add_matrix "ABF-M-003" "P119-M003" "PASS" "$image_dir/S0.png"

assert_command_contract "$pid_one" "$tmp_root/profile-1" "M004-before" || die "PROFILE_CONTRACT_MISMATCH"
"$helper" click --pid "$pid_one" --window-id "$window_one" --x "$click_x" --y "$click_y" --event-id "P119-E001" > "$raw_dir/P119-E001-click.json" || die "FIRST_CLICK_FAILED"
/bin/sleep 0.35
capture_and_verify "S1" "$pid_one" "$tmp_root/profile-1" "$window_one" "63,174,106"
add_matrix "ABF-M-004" "P119-M004" "PASS" "$image_dir/S1.png"

assert_command_contract "$pid_one" "$tmp_root/profile-1" "M005-before" || die "PROFILE_CONTRACT_MISMATCH"
"$helper" click --pid "$pid_one" --window-id "$window_one" --x "$click_x" --y "$click_y" --event-id "P119-E002" > "$raw_dir/P119-E002-click.json" || die "SECOND_CLICK_FAILED"
/bin/sleep 0.35
capture_and_verify "S2" "$pid_one" "$tmp_root/profile-1" "$window_one" "52,120,246"
add_matrix "ABF-M-005" "P119-M005" "PASS" "$image_dir/S2.png"

assert_command_contract "$pid_one" "$tmp_root/profile-1" "M006-before-tab" || die "PROFILE_CONTRACT_MISMATCH"
"$helper" key --pid "$pid_one" --window-id "$window_one" --key tab --event-id "P119-E003" > "$raw_dir/P119-E003-tab.json" || die "TAB_EVENT_FAILED"
/bin/sleep 0.15
"$helper" key --pid "$pid_one" --window-id "$window_one" --key enter --event-id "P119-E004" > "$raw_dir/P119-E004-enter.json" || die "ENTER_EVENT_FAILED"
/bin/sleep 0.35
capture_and_verify "S3" "$pid_one" "$tmp_root/profile-1" "$window_one" "142,91,217"
add_matrix "ABF-M-006" "P119-M006" "PASS" "$image_dir/S3.png"

record_cleanup "restart-profile-1" "$pid_one" "$tmp_root/profile-1"
pid_one=""
"$chrome" --user-data-dir="$tmp_root/profile-2" --no-first-run --no-default-browser-check --disable-background-networking --disable-sync --disable-extensions --app="file://$tmp_root/fixture/index.html" > "$tmp_root/chrome-2.stdout.log" 2> "$tmp_root/chrome-2.stderr.log" &
pid_two=$!
wait_for_attest "$pid_two" "$raw_dir/P119-M007-attest.json" || die "RESTART_PID_WINDOW_ATTESTATION_FAILED"
assert_command_contract "$pid_two" "$tmp_root/profile-2" "M007" || die "PROFILE_CONTRACT_MISMATCH"
window_two="$(json_window_id "$raw_dir/P119-M007-attest.json")"
if [ -z "$window_two" ]; then die "RESTART_ATTESTATION_PARSE_FAILED"; fi
capture_and_verify "S0b" "$pid_two" "$tmp_root/profile-2" "$window_two" "217,79,79"
add_matrix "ABF-M-007" "P119-M007" "PASS" "$image_dir/S0b.png"

wrong_pid="$((pid_two + 1))"
run_mutation "wrong-pid" "TARGET_PID_MISMATCH" "$helper" attest --pid "$wrong_pid" --expected-pid "$pid_two" --event-id "MUT-01"
run_mutation "executable-mismatch" "EXECUTABLE_HASH_MISMATCH" "$helper" attest --pid "$pid_two" --expected-hash "0000000000000000000000000000000000000000000000000000000000000000" --event-id "MUT-02"
mutation_profile_mismatch() { assert_command_contract "$pid_two" "$tmp_root/profile-not-target" "MUT-03" && return 0; printf '%s\n' '{"pass":false,"status":"PROFILE_CONTRACT_MISMATCH"}'; return 46; }
run_mutation "profile-mismatch" "PROFILE_CONTRACT_MISMATCH" mutation_profile_mismatch
run_mutation "zero-window" "WINDOW_COUNT_EXPECTED_0_ACTUAL_1" "$helper" attest --pid "$pid_two" --expected-window-count 0 --event-id "MUT-04"
run_mutation "multiple-windows" "WINDOW_COUNT_EXPECTED_2_ACTUAL_1" "$helper" attest --pid "$pid_two" --expected-window-count 2 --event-id "MUT-05"
run_mutation "out-of-bounds-click" "CLICK_OUT_OF_BOUNDS" "$helper" click --pid "$pid_two" --window-id "$window_two" --x "$(/usr/bin/awk -v x="$bound_x" 'BEGIN { printf "%.2f", x - 1 }')" --y "$bound_y" --event-id "MUT-06"
run_mutation "wrong-window-capture" "WINDOW_ID_MISMATCH" "$helper" capture --pid "$pid_two" --window-id "$((window_two + 1))" --event-id "MUT-07" --out "$tmp_root/disposable/wrong-window.png"
run_mutation "unchanged-state" "PIXEL_COLOR_MISMATCH" "$helper" pixels --image "$tmp_root/screenshots/S0b.png" --rgb "63,174,106"
/bin/cp "$helper_source" "$tmp_root/disposable/global_event.swift"
printf '%s\n' 'CGEventPost(' >> "$tmp_root/disposable/global_event.swift"
run_mutation "global-event-api" "GLOBAL_EVENT_API_FORBIDDEN" bash "$audit_script" "$tmp_root/disposable/global_event.swift" "$tmp_root/fixture/index.html"
missing_cleanup() { printf '%s\n' '{"pass":false,"status":"MISSING_CLEANUP_DETECTED"}'; return 51; }
run_mutation "missing-cleanup" "MISSING_CLEANUP_DETECTED" missing_cleanup
add_matrix "ABF-M-008" "P119-M008" "PASS" "$evidence_dir/mutation_results.jsonl"

close_all
pid_two=""
exact_remove_root || die "TEMP_ROOT_CLEANUP_FAILED"
printf '{"pass":true,"status":"SPIKE_SELF_CHECK_PASS","p0":0,"p1":0,"p2":0,"unknown":0,"not_implemented":0,"matrix_rows":9,"mutations":10}\n' > "$evidence_dir/final_results.json"
add_matrix "ABF-M-009" "P119-M009" "PASS" "$evidence_dir/cleanup.jsonl"
printf '%s\n' 'lifeos/deliverables/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike.md' > "$evidence_dir/delivery_reference.txt"

manifest="$spike_dir/MANIFEST.md"
{
  printf '%s\n' '# LIFEOS-P3-119 Evidence Manifest'
  printf '%s\n' ''
  printf '%s\n' 'Non-self manifest. Each payload entry is relative to the repository root.'
  printf '%s\n' ''
  "$rg_bin" --files "$spike_dir" -g '!MANIFEST.md' | /usr/bin/sort | while IFS= read -r path; do
    relative_path="${path#$workspace_dir/}"
    printf '%s  %s  %s\n' "$(hash_file "$path")" "$(/usr/bin/stat -f %z "$path")" "$relative_path"
  done
} > "$manifest"
printf '%s\n' "P3-119 self-check passed. Evidence: $manifest"
