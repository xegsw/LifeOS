#!/usr/bin/env python3
"""Record and verify the programmatically frozen Cargo.lock inventory."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "Cargo.lock"
OUTPUT = ROOT / "evidence" / "cargo_lock_inventory.json"


def parse_value(line: str) -> str:
    return line.split("=", 1)[1].strip().strip('"')


packages = []
current = None
for line in LOCK.read_text().splitlines():
    if line == "[[package]]":
        if current:
            packages.append(current)
        current = {}
    elif current is not None and line.startswith("name = "):
        current["name"] = parse_value(line)
    elif current is not None and line.startswith("version = "):
        current["version"] = parse_value(line)
    elif current is not None and line.startswith("source = "):
        current["source"] = parse_value(line)
    elif current is not None and line.startswith("checksum = "):
        current["checksum"] = parse_value(line)
if current:
    packages.append(current)

direct = {
    "tauri": "2.11.5",
    "tauri-build": "2.6.3",
    "rusqlite": "0.40.2",
    "serde": "1.0.229",
    "serde_json": "1.0.151",
}
failures = []
for name, version in direct.items():
    matches = [item for item in packages if item.get("name") == name and item.get("version") == version]
    if not matches:
        failures.append(f"missing direct dependency {name}={version}")
for item in packages:
    source = item.get("source", "")
    if source and source != "registry+https://github.com/rust-lang/crates.io-index":
        failures.append(f"unexpected source {item.get('name')}={source}")
    if source and not item.get("checksum"):
        failures.append(f"missing checksum {item.get('name')}")

payload = {
    "task": "LIFEOS-P3-104",
    "cargo_lock_sha256": hashlib.sha256(LOCK.read_bytes()).hexdigest(),
    "package_count": len(packages),
    "direct_dependencies": direct,
    "failures": failures,
    "packages": packages,
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"package_count": len(packages), "failed": len(failures), "cargo_lock_sha256": payload["cargo_lock_sha256"]}))
raise SystemExit(1 if failures else 0)

