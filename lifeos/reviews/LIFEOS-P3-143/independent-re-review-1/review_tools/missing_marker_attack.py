#!/usr/bin/env python3
"""Independent dynamic attack: an existing authorised-shaped root without marker must not initialise state."""

import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

TASK = "LIFEOS-P3-143"
RUN_ID = "rereviewb20260902"
ROOT = Path(f"/private/tmp/lifeos-p3-143-independent-review-{RUN_ID}")
MARKER = ROOT / ".lifeos-p3-143-owner.json"
RUNTIME = ROOT / "runtime"
DATABASE = ROOT / "secure-provider-settings.sqlite"
INJECTED_ROOT = Path("/private/tmp/lifeos-p3-143-independent-review-injected20260902")
OUTPUT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-1/evidence/missing_marker_attack.json")


def mode(path: Path) -> int:
    return stat.S_IMODE(path.lstat().st_mode)


def ensure_absent(path: Path) -> None:
    try:
        path.lstat()
    except FileNotFoundError:
        return
    raise RuntimeError(f"preexisting_review_owned_path:{path}")


def exact_marker() -> dict:
    return {
        "schema": "lifeos.p3-143.independent-review-root.v1",
        "task": TASK,
        "owner": "lifeos-p3-143-independent-review",
        "runId": RUN_ID,
    }


def marker_gated_cleanup() -> str:
    if ROOT.parent != Path("/private/tmp") or ROOT.name != f"lifeos-p3-143-independent-review-{RUN_ID}":
        return "REFUSED:root:exact_literal_mismatch"
    root_stat = ROOT.lstat()
    if not ROOT.is_dir() or ROOT.is_symlink() or stat.S_IMODE(root_stat.st_mode) != 0o700:
        return "REFUSED:root:type_or_mode_mismatch"
    marker_stat = MARKER.lstat()
    if MARKER.is_symlink() or not MARKER.is_file() or stat.S_IMODE(marker_stat.st_mode) != 0o600:
        return "REFUSED:marker:type_or_mode_mismatch"
    observed = json.loads(MARKER.read_text())
    if observed != exact_marker():
        return "REFUSED:marker:exact_binding_mismatch"
    shutil.rmtree(ROOT)
    return "CLEANED" if not ROOT.exists() else "REFUSED:cleanup_absence_failed"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: missing_marker_attack.py CANDIDATE_BINARY")
    binary = Path(sys.argv[1]).resolve()
    ensure_absent(ROOT)
    ensure_absent(INJECTED_ROOT)
    os.mkdir(ROOT, 0o700)
    os.chmod(ROOT, 0o700)
    if MARKER.exists() or RUNTIME.exists() or DATABASE.exists():
        raise RuntimeError("fixture_not_empty")
    env = os.environ.copy()
    for key in list(env):
        if key.lower().endswith("_proxy"):
            env.pop(key)
    env["LIFEOS_P3_143_RUNTIME_ROOT"] = str(INJECTED_ROOT)
    env["LIFEOS_P3_143_REAL_GATE"] = "disabled"
    proc = subprocess.Popen([str(binary)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline and proc.poll() is None:
        if MARKER.exists() or RUNTIME.exists() or DATABASE.exists():
            break
        time.sleep(0.05)
    observed = {
        "marker_created": MARKER.exists(),
        "runtime_child_created": RUNTIME.exists(),
        "database_created": DATABASE.exists(),
        "injected_runtime_root_created": INJECTED_ROOT.exists(),
        "root_mode": mode(ROOT),
        "marker_mode": mode(MARKER) if MARKER.exists() else None,
    }
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    cleanup = marker_gated_cleanup() if MARKER.exists() else "REFUSED:marker:missing"
    result = {
        "schema": "lifeos.p3-143.independent-missing-marker-attack.v1",
        "reviewer_owned": True,
        "profile": "independent-review",
        "run_id": RUN_ID,
        "fixture": "fresh, pre-existing 0700 direct-child root with no marker, runtime child, or database",
        "expected": "reject before marker creation, database, Keychain, network, or other durable state write",
        "observed": observed,
        "candidate_exit_code": proc.returncode,
        "cleanup": cleanup,
        "verdict": "FAIL_OPEN" if any(observed[key] for key in ("marker_created", "runtime_child_created", "database_created")) else "PASS",
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 1 if result["verdict"] != "PASS" else 0


if __name__ == "__main__":
    sys.exit(main())
