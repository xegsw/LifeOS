#!/usr/bin/env python3
"""Read-only P3-110 scan of the clean candidate copy for prohibited capability markers."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
WORK = Path("/private/tmp/lifeos-p3-110-review-work-v1")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
FILES = [
    WORK / "src/runtime.rs", WORK / "src/main.rs", WORK / "ui/app.js",
    WORK / "ui/default-recovery.html", WORK / "ui/no-reliable-suggestion.html",
    WORK / "ui/restricted-offline.html", WORK / "tauri.conf.json",
    WORK / "capabilities/main.json",
]
MARKERS = {
    "network": r"https?://|wss?://|fetch\s*\(|XMLHttpRequest|WebSocket|reqwest|hyper",
    "shell_or_process": r"Command::new|std::process|shell|process_spawn",
    "generic_file_db": r"fs::|OpenOptions|Connection::open|database_path|readFile|writeFile",
}
results: dict[str, object] = {"scanned_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "files": {}, "markers": {}}
combined = ""
for file in FILES:
    text = file.read_text(encoding="utf-8")
    combined += f"\\n// {file.name}\\n{text}"
    results["files"][str(file.relative_to(WORK))] = {"sha256": hashlib.sha256(file.read_bytes()).hexdigest(), "bytes": len(file.read_bytes())}
network_text = "\n".join(file.read_text(encoding="utf-8") for file in FILES if file.suffix in {".rs", ".js", ".html"})
for name, pattern in MARKERS.items():
    haystack = network_text if name == "network" else combined
    found = [{"offset": match.start(), "text": match.group(0)} for match in re.finditer(pattern, haystack, flags=re.IGNORECASE)]
    results["markers"][name] = found
commands = re.findall(r"#\[tauri::command\]\s*fn\s+([A-Za-z0-9_]+)", combined)
results["tauri_commands"] = commands
results["network_zero"] = not results["markers"]["network"]
results["only_expected_ipc"] = commands == ["capture_record", "get_today", "runtime_status"]
(EVIDENCE / "static-scan.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
