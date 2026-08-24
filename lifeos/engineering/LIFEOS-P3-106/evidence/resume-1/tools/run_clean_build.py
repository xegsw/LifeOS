#!/usr/bin/env python3
"""Perform the authorized offline locked clean test/build/bundle replay."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
TARGET = ROOT / "target"
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
UNIT_RE = re.compile(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+")


def unit_paths() -> list[str]:
    return sorted(str(path) for path in Path("/private/tmp").iterdir() if UNIT_RE.fullmatch(path.name))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(name: str, command: list[str]) -> dict[str, object]:
    env = os.environ.copy()
    env["CARGO_NET_OFFLINE"] = "true"
    completed = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log = OUT / f"{name}.log"
    log.write_text(completed.stdout, encoding="utf-8")
    return {"id": name, "command": command, "returncode": completed.returncode, "log": str(log.relative_to(ROOT)), "sha256": digest(log), "status": "PASS" if completed.returncode == 0 else "FAIL"}


def main() -> int:
    if ROOT != Path("/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-106"):
        raise RuntimeError(f"unexpected project root: {ROOT}")
    if not CARGO.is_file():
        raise RuntimeError(f"cargo unavailable: {CARGO}")
    before_units = unit_paths()
    target_existed = TARGET.exists()
    if target_existed:
        shutil.rmtree(TARGET)
    target_absent_before = not TARGET.exists()

    results = [
        execute("cargo_test", [str(CARGO), "test", "--locked"]),
        execute("cargo_build", [str(CARGO), "build", "--locked"]),
        execute("cargo_tauri_bundle", [str(CARGO), "tauri", "build", "--debug", "--bundles", "app", "--no-sign", "--config", '{"bundle":{"active":true,"targets":["app"]}}', "--", "--locked"]),
    ]
    after_units = unit_paths()
    binary = ROOT / "target/debug/lifeos-p3-104"
    bundle_binary = ROOT / "target/debug/bundle/macos/LifeOS P3-104.app/Contents/MacOS/lifeos-p3-104"
    payload = {
        "task": "LIFEOS-P3-106",
        "execution": "resume-1",
        "network_mode": "CARGO_NET_OFFLINE=true",
        "target_existed_before_authorized_clean": target_existed,
        "target_absent_before_build": target_absent_before,
        "unit_paths_before": before_units,
        "unit_paths_after": after_units,
        "commands": results,
        "artifacts": {
            "source_main_sha256": digest(ROOT / "src/main.rs"),
            "source_runtime_sha256": digest(ROOT / "src/runtime.rs"),
            "cargo_lock_sha256": digest(ROOT / "Cargo.lock"),
            "binary": str(binary.relative_to(ROOT)),
            "binary_sha256": digest(binary) if binary.is_file() else "missing",
            "bundle_binary": str(bundle_binary.relative_to(ROOT)),
            "bundle_binary_sha256": digest(bundle_binary) if bundle_binary.is_file() else "missing",
        },
    }
    payload["status"] = "PASS" if target_absent_before and not before_units and not after_units and all(row["status"] == "PASS" for row in results) and binary.is_file() and bundle_binary.is_file() else "FAIL"
    (OUT / "clean_build_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "unit_before": len(before_units), "unit_after": len(after_units), "commands": [(row["id"], row["returncode"]) for row in results]}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
