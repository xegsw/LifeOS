#!/usr/bin/env python3
"""Run review-owned semantic mutations in an isolated temporary clone.

The candidate remains read-only.  Each mutation changes one contract-bearing
expression in a temporary clone, then proves that its focused regression test
rejects the altered behaviour.  The clone and its build cache are removed
before this program reports success.
"""
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
WORK = TEMP / "review-semantic-mutations"
CLONE = WORK / "candidate"
TARGET = WORK / "cargo-target"
OUTPUT = REVIEW / "evidence" / "semantic_mutation.json"

CASES = [
    {
        "id": "provider_closed_set",
        "file": "src/runtime.rs",
        "before": 'vec!["openai", "anthropic", "ollama", "lm_studio"]',
        "after": 'vec!["openai", "anthropic", "ollama"]',
        "test": "runtime::tests::status_is_closed_to_the_p3_139_twenty_ipc",
    },
    {
        "id": "resolver_over_budget",
        "file": "src/runtime/memory_context.rs",
        "before": "fn token_for(reference: &str) -> usize { 8 + reference.len()/4 }",
        "after": "fn token_for(_reference: &str) -> usize { 1 }",
        "test": "runtime::memory_context::tests::format_budget_and_missing_receipt_fail_closed",
    },
    {
        "id": "health_stop_identity",
        "file": "src/runtime/today_intelligence.rs",
        "before": 'identity: "health_safety_stop".to_owned()',
        "after": 'identity: "system_suggestion".to_owned()',
        "test": "runtime::today_intelligence::tests::fixed_scenarios_are_evidence_linked_and_have_no_dispatch",
    },
    {
        "id": "feedback_stale_write",
        "file": "src/runtime/today_intelligence.rs",
        "before": "UPDATE p3140_results SET state='stale' WHERE result_id=?1",
        "after": "UPDATE p3140_results SET state='candidate' WHERE result_id=?1",
        "test": "runtime::today_intelligence::tests::repeated_request_is_stable_and_feedback_invalidates_only_target_slice",
    },
]


def within_temp(path: Path) -> bool:
    try:
        path.resolve().relative_to(TEMP)
        return True
    except ValueError:
        return False


def run(test: str) -> dict[str, object]:
    env = os.environ.copy()
    env.update(
        {
            "LIFEOS_RUNTIME_ROOT": str(WORK / "runtime"),
            "LIFEOS_INPUT_MODE": "synthetic",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TARGET),
        }
    )
    command = [
        "/Users/xxe/.cargo/bin/cargo",
        "test",
        "--manifest-path",
        str(CLONE / "Cargo.toml"),
        "--locked",
        "--offline",
        test,
        "--",
        "--exact",
        "--test-threads=1",
    ]
    completed = subprocess.run(command, env=env, text=True, capture_output=True, check=False)
    return {
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1600:],
        "stderr_tail": completed.stderr[-1600:],
    }


def main() -> int:
    if not CANDIDATE.is_dir() or not within_temp(WORK):
        raise SystemExit("candidate or isolated temporary root is invalid")
    if WORK.exists() or WORK.is_symlink():
        raise SystemExit("review semantic-mutation work root must be absent")

    TEMP.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.copytree(CANDIDATE, CLONE)
    (WORK / "runtime").mkdir(mode=0o700)
    cases: list[dict[str, object]] = []
    status = "PASS"
    try:
        for case in CASES:
            file_path = CLONE / str(case["file"])
            original = file_path.read_text(encoding="utf-8")
            before = str(case["before"])
            after = str(case["after"])
            if original.count(before) != 1:
                raise RuntimeError(f"mutation anchor is not unique for {case['id']}")
            baseline = run(str(case["test"]))
            mutated = original.replace(before, after, 1)
            file_path.write_text(mutated, encoding="utf-8")
            mutation = run(str(case["test"]))
            file_path.write_text(original, encoding="utf-8")
            detected = baseline["returncode"] == 0 and mutation["returncode"] != 0
            status = status if detected else "FAIL"
            cases.append(
                {
                    "id": case["id"],
                    "candidate_file": str(case["file"]),
                    "test": case["test"],
                    "baseline_returncode": baseline["returncode"],
                    "mutated_returncode": mutation["returncode"],
                    "mutation_detected": detected,
                    "baseline_output": baseline,
                    "mutation_output": mutation,
                }
            )
    finally:
        if WORK.exists() and within_temp(WORK):
            shutil.rmtree(WORK)

    payload = {
        "schema": "lifeos-p3-141-semantic-mutation-v1",
        "candidate_read_only": str(CANDIDATE),
        "clone_root": str(CLONE),
        "clone_removed": not WORK.exists(),
        "cases": cases,
        "status": status,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
