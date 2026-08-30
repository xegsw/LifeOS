#!/usr/bin/env python3
"""Exercise build-time runtime-root boundaries using only temporary fixtures."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
CANDIDATE = Path(sys.argv[1]).resolve()
TEMP = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1").resolve()
WORK = TEMP / "review-path-boundaries"
OUTPUT = REVIEW / "evidence" / "path_boundary_cases.json"


def run(root: str) -> dict[str, object]:
    env = os.environ.copy()
    env.update(
        {
            "LIFEOS_RUNTIME_ROOT": root,
            "LIFEOS_INPUT_MODE": "synthetic",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TEMP / "review-path-boundary-target"),
        }
    )
    command = [
        "/Users/xxe/.cargo/bin/cargo", "build", "--manifest-path", str(CANDIDATE / "Cargo.toml"),
        "--locked", "--offline",
    ]
    result = subprocess.run(command, env=env, text=True, capture_output=True, check=False)
    return {"returncode": result.returncode, "stdout_tail": result.stdout[-1600:], "stderr_tail": result.stderr[-1600:]}


def main() -> int:
    if not CANDIDATE.is_dir() or WORK.exists():
        raise SystemExit("invalid candidate or existing path-boundary work root")
    TEMP.mkdir(mode=0o700, parents=True, exist_ok=True)
    WORK.mkdir(mode=0o700)
    valid = WORK / "valid-existing-directory"
    valid.mkdir(mode=0o700)
    linked = WORK / "linked-root"
    linked.symlink_to(valid, target_is_directory=True)
    regular = WORK / "regular-file"
    regular.write_text("synthetic boundary fixture\n", encoding="utf-8")
    missing = WORK / "missing-directory"
    cases = [
        ("existing_real_directory", str(valid), 0, None),
        ("symlink_root", str(linked), 1, "root or an ancestor is not a real directory"),
        ("regular_file_root", str(regular), 1, "root or an ancestor is not a real directory"),
        ("missing_root", str(missing), 1, "root or an ancestor is not a real directory"),
        ("lexically_noncanonical", str(valid.parent / "valid-existing-directory/../valid-existing-directory"), 1, "root must be an absolute normalized path"),
    ]
    results = []
    status = "PASS"
    for case_id, root, expected_class, expected_text in cases:
        result = run(root)
        text = str(result["stdout_tail"]) + str(result["stderr_tail"])
        passed = (result["returncode"] == 0) if expected_class == 0 else (result["returncode"] != 0 and expected_text in text)
        results.append({"case": case_id, "root": root, "result": result, "pass": passed})
        if not passed:
            status = "FAIL"
    shutil.rmtree(WORK)
    payload = {
        "schema": "lifeos-p3-141-review-path-boundaries-v1",
        "candidate_read_only": str(CANDIDATE),
        "temporary_fixture_root": str(WORK),
        "fixtures_removed": not WORK.exists(),
        "cases": results,
        "status": status,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
