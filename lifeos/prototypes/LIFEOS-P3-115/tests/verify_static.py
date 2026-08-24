#!/usr/bin/env python3
"""Static, local-only checks for P3-115. No network or browser is used."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = ["index.html", "styles.css", "app.js", "fixtures.js", "fixtures.json", "interaction_contract.md", "state_machine.json", "visual_contract.json"]
FORBIDDEN = [r"https?://", r"fetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"localStorage", r"sessionStorage", r"indexedDB", r"document\.cookie", r"<img\b", r"background-image\s*:"]
MATRIX_TERMS = ["Person", "0–1", "Memory candidate", "Source", "Artifact", "Derivation", "Advice", "Feedback", "Escape", "prefers-reduced-motion", "file:"]

def fail(message):
    print(json.dumps({"status": "FAIL", "reason": message}, ensure_ascii=False))
    raise SystemExit(1)

for name in REQUIRED:
    if not (ROOT / name).is_file():
        fail(f"missing required file: {name}")

payload = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in REQUIRED)
for pattern in FORBIDDEN:
    if re.search(pattern, payload, re.I):
        fail(f"forbidden capability or remote asset pattern: {pattern}")
for term in MATRIX_TERMS:
    if term not in payload:
        fail(f"required product/accessibility term absent: {term}")

machine = json.loads((ROOT / "state_machine.json").read_text(encoding="utf-8"))
events = {item["event"] for item in machine["transitions"]}
for event in ["ANS_SAFE", "ANS_SKIP", "ANS_WARNING", "FDB_MODIFIED_ACCEPT", "EXE_REPORTED", "RES_REPORTED", "MEM_CANDIDATE", "SOURCE_FAILURE", "REVOKE_ANS_FDB_EXE_RES", "REFRESH_OR_CLOSE_REOPEN"]:
    if event not in events:
        fail(f"missing state transition: {event}")
print(json.dumps({"status": "PASS", "files": len(REQUIRED), "events": len(events), "network_or_storage": "closed"}, ensure_ascii=False))
