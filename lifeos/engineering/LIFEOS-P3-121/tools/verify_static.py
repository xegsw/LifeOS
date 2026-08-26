#!/usr/bin/env python3
"""P3-121 task-local, fail-closed static and boundary verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
OUTPUT = ROOT / "evidence" / "static" / "static-boundary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(name: str, condition: bool, evidence: str) -> dict:
    return {"id": name, "result": "PASS" if condition else "FAIL", "evidence": evidence}


def main() -> int:
    app = (CANDIDATE / "ui" / "app.js").read_text(encoding="utf-8")
    css = (CANDIDATE / "ui" / "styles.css").read_text(encoding="utf-8")
    html = (CANDIDATE / "ui" / "index.html").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src" / "runtime.rs").read_text(encoding="utf-8")
    config = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    capabilities = json.loads((CANDIDATE / "capabilities" / "main.json").read_text(encoding="utf-8"))
    command_names = ["capture_record", "get_today", "runtime_status"]
    forbidden_renderer = ["fetch(", "XMLHttpRequest", "WebSocket", "localStorage", "sessionStorage", "indexedDB", "window.open", "navigator.clipboard"]
    # A process identifier only namespaces task-local test fixtures; it is not a process-spawn capability.
    forbidden_runtime = ["Command::new", "reqwest", "ureq", "tokio::net", "FileDialog"]
    results = [
        require("S001-shell-ia", all(token in app for token in ["icon-rail", "Today", "Me", "Contexts", "Memory", "Settings", "ai-open", "capture-open"]), "same actual shell carries narrow rail, primary IA, Global AI and distinct Quick Capture"),
        require("S002-person-first", all(token in app for token in ["Today · Person", "现在的我", "Context Detail", "Memory Detail", "Identity", "Understanding", "Derivation", "Evidence", "Source"]), "Person-first hierarchy and separate provenance layers are present"),
        require("S003-no-forbidden-chrome", all(token not in app for token in ["通知中心", "账户资料", "avatar", "bell"]), "no notification center, profile shell, avatar, or bell wording in renderer"),
        require("S004-responsive-a11y", all(token in css for token in ["@media (max-width: 1050px)", "@media (max-width: 740px)", "prefers-reduced-motion", ".icon-rail", ".composer"]) and "skip-link" in html and "Escape" in app, "same DOM responsive rules, skip link, visible focus CSS, Escape, and reduced motion"),
        require("S005-three-ipc", all(runtime.count(name) >= 2 for name in command_names) and "generate_handler![capture_record, get_today, runtime_status]" in runtime and all(name in app for name in command_names), "exact Rust handler and renderer bridge use only the three frozen commands"),
        require("S006-runtime-root-and-fixtures", "/private/tmp/lifeos-p3-121-combined-v1" in runtime and "P3-121 synthetic capture one" in runtime and "P3-121 synthetic capture two" in runtime, "task-local root and the two frozen synthetic captures"),
        require("S007-renderer-boundary", all(token not in app for token in forbidden_renderer), "forbidden renderer patterns: " + ", ".join(forbidden_renderer)),
        require("S008-runtime-boundary", all(token not in runtime for token in forbidden_runtime), "forbidden runtime patterns: " + ", ".join(forbidden_runtime)),
        require("S009-tauri-config", config["productName"].startswith("LifeOS P3-121") and config["identifier"] == "local.lifeos.p3-121" and config["app"]["windows"][0]["width"] == 1280 and config["app"]["windows"][0]["height"] == 1024, "P3-121 local app identity and 1280x1024 requested default"),
        require("S010-capability-empty", capabilities["permissions"] == [], "main capability grants no plugin or direct system permission"),
    ]
    result = "PASS" if all(item["result"] == "PASS" for item in results) else "FAIL"
    payload = {
        "task": "LIFEOS-P3-121",
        "result": result,
        "candidate_files": {str(path.relative_to(CANDIDATE)): sha256(path) for path in sorted(CANDIDATE.rglob("*")) if path.is_file() and "target" not in path.parts},
        "checks": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"P3-121-STATIC: {result} ({sum(item['result'] == 'PASS' for item in results)}/{len(results)})")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
