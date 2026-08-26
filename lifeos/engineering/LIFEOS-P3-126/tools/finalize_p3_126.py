#!/usr/bin/env python3
"""Perform P3-126's exact temporary-root cleanup and write closure evidence."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


REPO = Path("/Users/xxe/Documents/No.2")
TASK = REPO / "lifeos/engineering/LIFEOS-P3-126"
EVIDENCE = TASK / "evidence"
TEMP = Path("/private/tmp/lifeos-p3-126-clean-closure-v1")
EXPECTED_TEMP = "/private/tmp/lifeos-p3-126-clean-closure-v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def result_item(path: str) -> dict[str, str]:
    item = REPO / path
    return {"path": path, "sha256": sha256(item)}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if TEMP.as_posix() != EXPECTED_TEMP or TEMP.resolve().as_posix() != EXPECTED_TEMP:
        raise RuntimeError("refusing cleanup outside the exact P3-126 temporary root")
    if not TEMP.is_dir():
        raise RuntimeError("expected P3-126 temporary root is absent before cleanup")

    # Inventory is evidence only. Deletion below names this one validated path;
    # no glob, prefix, or inherited P3-122 runtime root is ever targeted.
    before_files = sorted(
        p.relative_to(TEMP).as_posix() for p in TEMP.rglob("*") if p.is_file()
    )
    shutil.rmtree(TEMP)
    if TEMP.exists():
        raise RuntimeError("exact P3-126 temporary-root cleanup did not complete")

    cleanup = {
        "test_id": "P126-M012",
        "status": "PASS",
        "target": EXPECTED_TEMP,
        "target_exists_before": True,
        "file_count_before": len(before_files),
        "target_exists_after": False,
        "prohibited_old_runtime_root_touched": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    cleanup_path = EVIDENCE / "cleanup.json"
    write_json(cleanup_path, cleanup)

    rows = [
        ("ABF-M-001", "P126-M001", "Unknown", ["lifeos/engineering/LIFEOS-P3-126/evidence/preflight.json"],
         "User confirmed gpt-5.6-terra + xhigh; platform direct model/effort metadata was not exposed."),
        ("ABF-M-002", "P126-M002", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/source-lineage.json"], "P3-125 candidate 75/75 exact and fixed inputs unchanged."),
        ("ABF-M-003", "P126-M003", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/static-contract.json"], "Static closure contract passed."),
        ("ABF-M-004", "P126-M004", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/config-negatives.json", "lifeos/engineering/LIFEOS-P3-126/evidence/unit-tests.json", "lifeos/engineering/LIFEOS-P3-126/evidence/run-a-build.json"], "Configuration negatives, unit tests, and fresh bundle build passed."),
        ("ABF-M-005", "P126-M005", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/run-a-results.json", "lifeos/engineering/LIFEOS-P3-126/evidence/run-a-initial.jpeg", "lifeos/engineering/LIFEOS-P3-126/evidence/run-a-first.jpeg", "lifeos/engineering/LIFEOS-P3-126/evidence/run-a-repeat.jpeg", "lifeos/engineering/LIFEOS-P3-126/evidence/run-a-reopen.jpeg"], "Actual bundled app: 0/0 -> 1/1 -> 1/2 -> reopen 1/2."),
        ("ABF-M-006", "P126-M006", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/run-b-results.json", "lifeos/engineering/LIFEOS-P3-126/evidence/run-b-first.jpeg"], "Fresh Run-B created an independent 1/1 root."),
        ("ABF-M-007", "P126-M007", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/ipc-lifecycle.json"], "Observed allowed IPC lifecycle evidence."),
        ("ABF-M-008", "P126-M008", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/failure-closure.json"], "Failure and blocked-root closure evidence passed."),
        ("ABF-M-009", "P126-M009", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/boundary.json"], "No product source, network, model, or new IPC drift."),
        ("ABF-M-010", "P126-M010", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/history-integrity.json"], "P3-125 direct inputs remained byte-identical."),
        ("ABF-M-011", "P126-M011", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/mutation-results.json"], "All eight disposable negative mutations were rejected."),
        ("ABF-M-012", "P126-M012", "PASS", ["lifeos/engineering/LIFEOS-P3-126/evidence/cleanup.json"], "Exact task temporary root was removed after app closure."),
    ]
    closure_rows = [
        {
            "abf_row": abf_row,
            "test_id": test_id,
            "status": status,
            "evidence": [result_item(path) for path in paths],
            "observed": observed,
        }
        for abf_row, test_id, status, paths, observed in rows
    ]
    closure = {
        "task": "LIFEOS-P3-126",
        "abf": "ABF-P3-126-v1",
        "status": "NOT_PASS_MODEL_SOURCE_UNKNOWN",
        "counts": {"P0": 0, "P1": 0, "P2": 0, "Unknown": 1, "Not Implemented": 0, "pass_rows": 11},
        "frozen_formula_result": "NOT_PASS: ABF-M-001 requires platform-exposed actual model/effort; user confirmation is recorded but does not create platform evidence or amend the Frozen ABF.",
        "rows": closure_rows,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(EVIDENCE / "DYNAMIC_CLOSURE.json", closure)


if __name__ == "__main__":
    main()
