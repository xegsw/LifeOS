#!/usr/bin/env python3
"""Build the fixed P3-141 candidate without modifying its source tree."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


REVIEW = Path(__file__).resolve().parent
CANDIDATE = Path("/Users/xxe/.codex/worktrees/506c/No.2/lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate")
TEMP = Path("/private/tmp/lifeos-p3-141-revision-3-independent-review-final-v4")


def main() -> int:
    environment = os.environ.copy()
    environment.update({
        "LIFEOS_P3_141_BUILD_MODE": "revision_3_synthetic",
        "LIFEOS_INPUT_MODE": "synthetic",
        "LIFEOS_P3_141_AUTHORIZED_SYNTHETIC_ROOT": str(TEMP),
        "LIFEOS_RUNTIME_ROOT": str(TEMP / "runtime"),
        "CARGO_TARGET_DIR": str(TEMP / "target"),
        "CARGO_NET_OFFLINE": "true",
        "CARGO_BUILD_LOCKED": "true",
        "TMPDIR": str(TEMP / "tmp"),
    })
    (TEMP / "tmp").mkdir(mode=0o700, exist_ok=True)
    os.chmod(TEMP / "tmp", 0o700)
    command = ["/Users/xxe/.cargo/bin/cargo", "tauri", "build", "--no-sign"]
    completed = subprocess.run(command, cwd=CANDIDATE, env=environment, text=True, capture_output=True)
    payload = {
        "schema": "lifeos.p3-141.revision-3.review-owned-pristine-build.v1",
        "candidate": str(CANDIDATE),
        "command": command,
        "cwd": str(CANDIDATE),
        "authorized_root": str(TEMP),
        "runtime_root": str(TEMP / "runtime"),
        "target_dir": str(TEMP / "target"),
        "network": "offline",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    (REVIEW / "build_result.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"returncode={completed.returncode}")
    print(completed.stdout[-2000:])
    print(completed.stderr[-4000:])
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
