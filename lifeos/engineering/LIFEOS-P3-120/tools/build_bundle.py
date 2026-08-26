#!/usr/bin/env python3
"""Perform the locked/offline Rust test, build, and macOS app bundle checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
BUNDLE = TEMP_ROOT / "cargo-target/release/bundle/macos/LifeOS P3-120 Synthetic Runtime MVP.app"


def execute(label: str, command: list[str], env: dict[str, str]) -> dict[str, object]:
    completed = subprocess.run(command, cwd=CANDIDATE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    (EVIDENCE / f"{label}.log").write_text(completed.stdout, encoding="utf-8")
    return {"label": label, "command": command, "exit_code": completed.returncode, "log": f"{label}.log", "result": "PASS" if completed.returncode == 0 else "FAIL"}


def main() -> int:
    if not CARGO.is_file():
        print(f"missing Cargo binary: {CARGO}", file=sys.stderr)
        return 1
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    (TEMP_ROOT / "tmp").mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"CARGO_NET_OFFLINE": "true", "CARGO_TARGET_DIR": str(TEMP_ROOT / "cargo-target"), "TMPDIR": str(TEMP_ROOT / "tmp")})
    commands = [
        execute("build-test", [str(CARGO), "test", "--locked", "--offline"], env),
        execute("build-binary", [str(CARGO), "build", "--locked", "--offline", "--release"], env),
        execute("build-bundle", [str(CARGO), "tauri", "build", "--bundles", "app", "--config", "tauri.conf.json", "--", "--locked", "--offline"], env),
    ]
    bundle_files = []
    if BUNDLE.is_dir():
        bundle_files = [path.relative_to(BUNDLE).as_posix() for path in sorted(BUNDLE.rglob("*")) if path.is_file()]
    bundle_ready = (BUNDLE / "Contents/MacOS/lifeos-p3-120").is_file() and (BUNDLE / "Contents/Info.plist").is_file()
    payload = {
        "schema": "lifeos-p3-120/build-results-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "commands": commands,
        "bundle": {"path": str(BUNDLE), "ready": bundle_ready, "files": bundle_files},
        "result": "PASS" if all(item["result"] == "PASS" for item in commands) and bundle_ready else "FAIL",
    }
    (EVIDENCE / "build-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "bundle_ready": bundle_ready, "commands": len(commands)}))
    return 0 if payload["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
