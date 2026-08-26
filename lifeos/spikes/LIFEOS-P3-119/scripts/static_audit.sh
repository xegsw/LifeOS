#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  printf '%s\n' '{"pass":false,"status":"STATIC_AUDIT_USAGE"}'
  exit 64
fi

source_path="$1"
fixture_path="$2"
rg_bin="$(command -v rg)"
if ! "$rg_bin" -q 'CGEventPostToPid' "$source_path"; then
  printf '%s\n' '{"pass":false,"status":"PID_EVENT_API_MISSING"}'
  exit 21
fi
if "$rg_bin" -q 'CGEventPost[(]' "$source_path"; then
  printf '%s\n' '{"pass":false,"status":"GLOBAL_EVENT_API_FORBIDDEN"}'
  exit 22
fi
if "$rg_bin" -q 'AppleScript|System Events|AXUIElement|kCGWindowName|kCGWindowOwnerName|CDP|DevTools|WebDriver|headless' "$source_path" "$fixture_path"; then
  printf '%s\n' '{"pass":false,"status":"FORBIDDEN_GUI_API_OR_METADATA"}'
  exit 23
fi
if "$rg_bin" -q 'http://|https://|localhost|fetch[(]|localStorage|sessionStorage|evaluateJavaScript|WKWebView' "$source_path" "$fixture_path"; then
  printf '%s\n' '{"pass":false,"status":"NETWORK_STORAGE_OR_DOM_BYPASS"}'
  exit 24
fi
printf '%s\n' '{"pass":true,"status":"STATIC_AUDIT_PASS"}'
