#!/usr/bin/env python3
"""Perform the locked offline unsigned macOS bundle and retain its exact result."""
from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
RAW = ROOT / "evidence" / "raw"
BUILD = Path("/private/tmp/lifeos-p3-111-build-output")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
command = [str(CARGO), "tauri", "build", "--bundles", "app", "--", "--offline", "--locked"]
env = os.environ | {"CARGO_TARGET_DIR": str(BUILD), "CARGO_BUILD_JOBS": "1", "RUSTFLAGS": "-Ccodegen-units=1"}
result = subprocess.run(command, cwd=CANDIDATE, text=True, capture_output=True, env=env)
RAW.mkdir(parents=True, exist_ok=True)
(RAW / "cargo-tauri-bundle.log").write_text(result.stdout + result.stderr, encoding="utf-8")
bundle = BUILD / "release/bundle/macos/LifeOS P3-111.app"
payload = {"command": "cargo tauri build --bundles app -- --offline --locked", "exit_code": result.returncode, "bundle_exists": bundle.is_dir(), "bundle_path": str(bundle), "network": "offline locked cargo inputs"}
(RAW / "bundle-result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(result.returncode)
