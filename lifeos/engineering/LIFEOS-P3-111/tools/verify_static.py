#!/usr/bin/env python3
"""Fail-closed static contract check for the P3-111 isolated candidate."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
OUT = ROOT / "evidence" / "raw" / "static-results.json"
EXPECTED = {"capture_record", "get_today", "runtime_status"}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    frontend = (CANDIDATE / "ui/app.js").read_text(encoding="utf-8")
    cargo = (CANDIDATE / "Cargo.toml").read_text(encoding="utf-8")
    config = (CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8")
    capability = json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8"))
    commands = set(re.findall(r"fn (capture_record|get_today|runtime_status)\(", runtime))
    invokes = set(re.findall(r'safeInvoke\("([^"]+)"', frontend))
    forbidden = {
        "legacy_path": "LIFEOS_P3_104_DB_PATH" not in runtime,
        "private_tmp": "/private/tmp" not in runtime,
        "new_ipc": commands == EXPECTED and invokes == EXPECTED,
        "new_dependency": all(token not in cargo for token in ["tauri-plugin", "reqwest", "sqlx", "tokio::process"]),
        "permissions": capability.get("permissions") == [],
        "network_csp": "connect-src ipc:;" in config and "connect-src http" not in config and "connect-src https" not in config,
        "pilot_path": 'const PILOT_DB: &str = "/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2/capture.sqlite"' in runtime,
        "schema_unchanged": "PRAGMA user_version = 104" in runtime and "CREATE TABLE IF NOT EXISTS captures" in runtime,
        "no_clear_or_export": not re.search(r"\bfn\s+(clear|export|restore|set_permission)\b", runtime) and "data-action=\"export\"" not in frontend,
    }
    payload = {
        "check": "P3-111 static contract",
        "passed": all(forbidden.values()),
        "ipc_commands": sorted(commands),
        "frontend_invokes": sorted(invokes),
        "checks": forbidden,
        "candidate_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in sorted([CANDIDATE / "src/runtime.rs", CANDIDATE / "ui/app.js", CANDIDATE / "tauri.conf.json", CANDIDATE / "capabilities/main.json"])
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
