#!/usr/bin/env python3
"""Launch one Tauri process, attest only that returned PID, capture its window."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"


def digest(path: Path) -> str:
    hash_value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hash_value.update(block)
    return hash_value.hexdigest()


def main() -> int:
    if len(sys.argv) != 7:
        raise SystemExit("usage: run_pid_viewport.py BINARY AX_HELPER TEMP_ROOT VIEWPORT EVIDENCE_DIR OUT_JSON")
    binary = Path(sys.argv[1])
    helper = Path(sys.argv[2])
    temp_root = Path(sys.argv[3])
    viewport = sys.argv[4]
    evidence_dir = Path(sys.argv[5])
    output = Path(sys.argv[6])
    binary = binary.resolve(strict=True)
    helper = helper.resolve(strict=True)
    temp_root = temp_root.resolve(strict=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    app_log = temp_root / f"{viewport}-app.log"
    attestation = temp_root / f"{viewport}-attestation.json"
    screenshot = evidence_dir / f"{viewport}_pid_bound.png"
    env = os.environ.copy()
    env["LIFEOS_P3_141_EVIDENCE_MODE"] = "1"
    env["LIFEOS_P3_141_VIEWPORT"] = viewport
    launched = subprocess.Popen([str(binary)], stdout=app_log.open("wb"), stderr=subprocess.STDOUT, env=env)
    result: dict[str, object] = {
        "schema_version": "lifeos.p3_141.phase_b.pid_viewport_run.v1",
        "viewport": viewport,
        "launch_pid": launched.pid,
        "binary": str(binary),
        "expected_title": TITLE,
        "global_process_or_window_enumeration": False,
    }
    try:
        for _ in range(30):
            if launched.poll() is not None:
                result["launch_exit_before_attestation"] = launched.returncode
                break
            call = subprocess.run([str(helper), str(launched.pid), TITLE, str(attestation)], capture_output=True, text=True)
            if call.returncode == 0:
                payload = json.loads(attestation.read_text(encoding="utf-8"))
                window_number = payload.get("window_number")
                if isinstance(window_number, int):
                    capture_command = ["/usr/sbin/screencapture", "-x", f"-l{window_number}", str(screenshot)]
                    result["capture_binding"] = "pid_bound_ax_window_number"
                else:
                    position = payload.get("position")
                    size = payload.get("size")
                    if not (isinstance(position, dict) and isinstance(size, dict)):
                        result["attestation_error"] = "window_number_and_geometry_unavailable"
                        result["attestation"] = payload
                        break
                    rectangle = "{},{},{},{}".format(
                        round(float(position["x"])), round(float(position["y"])),
                        round(float(size["width"])), round(float(size["height"])),
                    )
                    capture_command = ["/usr/sbin/screencapture", "-x", f"-R{rectangle}", str(screenshot)]
                    result["capture_binding"] = "pid_bound_ax_geometry"
                capture = subprocess.run(capture_command, capture_output=True, text=True)
                result["attestation"] = payload
                result["screencapture_exit"] = capture.returncode
                if capture.returncode == 0 and screenshot.is_file():
                    result["screenshot"] = str(screenshot)
                    result["screenshot_sha256"] = digest(screenshot)
                    result["pass"] = bool(payload.get("pass"))
                else:
                    result["screencapture_stderr"] = capture.stderr[-1000:]
                    result["pass"] = False
                break
            time.sleep(0.25)
        else:
            result["attestation_error"] = "pid_bound_window_not_available"
            result["pass"] = False
        result.setdefault("pass", False)
    finally:
        if launched.poll() is None:
            launched.terminate()
            try:
                launched.wait(timeout=5)
            except subprocess.TimeoutExpired:
                launched.kill()
                launched.wait(timeout=5)
        result["verified_pid_exit"] = launched.returncode
        result["app_log_sha256"] = digest(app_log) if app_log.exists() else None
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
