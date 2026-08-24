#!/usr/bin/env python3
"""Run each frozen runtime counterexample as a separate process probe."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
CARGO = "/Users/xxe/.cargo/bin/cargo"
UNIT_RE = re.compile(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+")
TESTS = [
    ("RUNTIME-LIFECYCLE", "runtime::tests::lifecycle_saved_repeat_conflict_restart"),
    ("RUNTIME-ATOMIC-FAILURE", "runtime::tests::injected_failure_preserves_database_and_sentinel"),
    ("RUNTIME-PATH-ARGUMENTS", "runtime::tests::path_and_argument_boundaries_fail_closed"),
    ("RUNTIME-LINK-HARDLINK", "runtime::tests::symlink_and_hardlink_boundaries_fail_closed"),
    ("RUNTIME-DANGLING-4", "runtime::tests::dangling_database_and_sidecar_links_fail_closed"),
    ("RUNTIME-TAMPER-PROCESS", "runtime::tests::tampered_content_and_sidecar_fail_closed"),
    ("RUNTIME-CAPABILITIES", "runtime::tests::runtime_status_closes_direct_capabilities"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def residuals() -> list[str]:
    return sorted(str(path) for path in Path("/private/tmp").iterdir() if UNIT_RE.fullmatch(path.name))


def main() -> int:
    env = os.environ.copy()
    env["CARGO_NET_OFFLINE"] = "true"
    rows = []
    for row_id, test_name in TESTS:
        before = residuals()
        command = [CARGO, "test", "--locked", test_name, "--", "--exact", "--nocapture"]
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        after = residuals()
        log = OUT / f"{row_id.lower()}.log"
        log.write_text(completed.stdout, encoding="utf-8")
        ok = completed.returncode == 0 and not before and not after and "1 passed" in completed.stdout
        rows.append({
            "id": row_id,
            "test": test_name,
            "command": command,
            "returncode": completed.returncode,
            "unit_paths_before": before,
            "unit_paths_after": after,
            "log": str(log.relative_to(ROOT)),
            "sha256": digest(log),
            "status": "PASS" if ok else "FAIL",
        })
    payload = {"task": "LIFEOS-P3-106", "execution": "resume-1", "rows": rows}
    payload["summary"] = {"total": len(rows), "passed": sum(row["status"] == "PASS" for row in rows), "failed": sum(row["status"] != "PASS" for row in rows)}
    (OUT / "runtime_process_matrix.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
