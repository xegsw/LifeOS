#!/usr/bin/env python3
"""Machine-check the frozen P3-120 renderer, IPC, and capability boundary."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(identifier: str, passed: bool, actual: object, expectation: str) -> dict[str, object]:
    return {
        "id": identifier,
        "result": "PASS" if passed else "FAIL",
        "actual": actual,
        "expectation": expectation,
    }


def text_files() -> dict[str, str]:
    suffixes = {".rs", ".js", ".html", ".css", ".toml", ".json", ".md"}
    return {
        path.relative_to(CANDIDATE).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(CANDIDATE.rglob("*"))
        if path.is_file() and not path.is_symlink() and path.suffix in suffixes
    }


def main() -> int:
    files = text_files()
    runtime = files["src/runtime.rs"]
    main_rs = files["src/main.rs"]
    app_js = files["ui/app.js"]
    index_html = files["ui/index.html"]
    config = json.loads(files["tauri.conf.json"])
    capability = json.loads(files["capabilities/main.json"])
    executable_text = "\n".join(
        f"// {path}\n{text}"
        for path, text in files.items()
        if path.startswith(("src/", "ui/")) or path in {"tauri.conf.json", "capabilities/main.json"}
    )

    expected_commands = ["capture_record", "get_today", "runtime_status"]
    rust_commands = re.findall(r"#\[tauri::command\]\s*fn\s+([a-z_]+)", runtime)
    handler = re.search(r"tauri::generate_handler!\s*\[([^]]+)\]", runtime, re.S)
    handler_commands = re.findall(r"\b(capture_record|get_today|runtime_status)\b", handler.group(1) if handler else "")
    js_command_literals = re.findall(r'safeInvoke\("([a-z_]+)"', app_js)

    forbidden_patterns = {
        "renderer_fetch": r"\bfetch\s*\(",
        "renderer_xhr": r"XMLHttpRequest",
        "renderer_websocket": r"\bWebSocket\b",
        "renderer_storage": r"\b(?:localStorage|sessionStorage)\b",
        "renderer_file_shell": r"__TAURI__\s*\?*\.\s*(?:fs|shell|path|dialog|http|process|notification)",
        "rust_network": r"\b(?:reqwest|ureq|TcpStream|UdpSocket|WebSocket)\b",
        "rust_plugin": r"tauri_plugin_",
        "prohibited_entry": r"\b(?:clear|export|permission|recovery|file_import|file_picker)\s*\(",
    }
    forbidden_hits = {
        name: [path for path, text in files.items() if re.search(pattern, text, re.I)]
        for name, pattern in forbidden_patterns.items()
    }
    prohibited_api_literals = [
        literal
        for literal in re.findall(r'safeInvoke\("([^"]+)"', app_js)
        if literal not in expected_commands
    ]

    core_pages = [
        "todayPage",
        "mePage",
        "contextsPage",
        "contextDetailPage",
        "memoryPage",
        "memoryDetailPage",
        "workspacePage",
        "aiPanel",
        "settingsPage",
    ]
    identity_markers = [
        "Runtime data",
        "read-only synthetic fixture",
        "AI Observation",
        "Decision Candidate",
        "用户确认",
        "模型未启用",
    ]
    checks = [
        check("S-001", rust_commands == expected_commands, rust_commands, "exactly the three frozen Rust IPC commands"),
        check("S-002", handler_commands == expected_commands, handler_commands, "exactly the three frozen commands in generate_handler"),
        check("S-003", sorted(set(js_command_literals)) == expected_commands and not prohibited_api_literals, {"used": js_command_literals, "other": prohibited_api_literals}, "renderer invokes only the three frozen command names"),
        check("S-004", capability.get("permissions") == [], capability.get("permissions"), "capability grants no direct permissions"),
        check("S-005", config["app"]["windows"][0]["url"] == "index.html" and "connect-src ipc:" in config["app"]["security"]["csp"] and "http" not in config["app"]["security"]["csp"], config["app"]["security"], "local index.html and IPC-only connect CSP"),
        check("S-006", not any(forbidden_hits.values()), forbidden_hits, "no renderer direct storage/file/shell/network, Rust network/plugin, or prohibited entry"),
        check("S-007", all(page in app_js for page in core_pages), core_pages, "Today, Me, Contexts, both details, Memory, AI panel/workspace and weak Settings exist"),
        check("S-008", all(marker in app_js for marker in identity_markers), identity_markers, "runtime, fixture, AI candidate and confirmed identities are visibly distinct"),
        check("S-009", "P3-120 synthetic capture one" in app_js and "P3-120 synthetic capture two" in app_js and "<input" not in index_html and "contenteditable" not in app_js.lower(), "fixed two samples; no free-text input", "only the two frozen synthetic capture texts are offered"),
        check("S-010", "P3-111" not in executable_text and "Pilot-" not in executable_text and "LifeOS-Self-Use" not in executable_text, "legacy/Pilot markers absent from executable source", "candidate contains no legacy Pilot runtime target"),
        check("S-011", "RUNTIME_DB" in runtime and "/private/tmp/lifeos-p3-120-runtime-mvp-v1/capture.sqlite" in runtime and "PRAGMA user_version = 104" in runtime, "synthetic P3-120 path and inherited schema version", "exact task-local DB path and frozen SQLite schema"),
        check("S-012", "capture_record" in main_rs or "runtime::run" in main_rs, "Tauri executable entry point", "app entry point remains present"),
    ]
    passed = all(item["result"] == "PASS" for item in checks)
    payload = {
        "schema": "lifeos-p3-120/static-results-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "candidate_files": [{"path": path, "sha256": sha256(CANDIDATE / path)} for path in files],
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "static-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "checks": len(checks)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
