#!/usr/bin/env python3
"""Materialize an explicit Not Pass matrix when frozen GUI binding cannot start."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    plan = json.loads((ROOT / "test_plan.json").read_text(encoding="utf-8"))
    blocker = {
        "id": "BLOCKED_COMPUTER_USE_PID_BINDING_UNAVAILABLE",
        "fact": "The installed Computer Use surface has app-scoped operations only; it exposes no PID or native window-ID targeting parameter.",
        "frozen_conflict": "Passing com.google.Chrome to Computer Use would invoke the app selector prohibited by ABF-P3-118-v1 and cannot prove the attested PID/window is the operated surface.",
        "actions_attempted": 0,
        "chrome_started": False,
        "computer_use_target_queried": False,
        "temporary_root_created": False,
        "conclusion": "Blocked before GUI, screenshot, or native-capture activity. No substitute path was used.",
    }
    closure = []
    for action in plan["actions"]:
        closure.append({
            "acceptance_item_id": action["id"],
            "precondition_and_action": action["action"],
            "expected_observable_result": action["expected"],
            "structured_result_id": f"R-{action['id']}",
            "evidence": None,
            "sha256": None,
            "status": "NOT_IMPLEMENTED",
            "reason": blocker["id"],
        })
    rows = []
    for index in range(1, 16):
        row_id = f"ABF-M-{index:03d}"
        if index == 1:
            rows.append({"row_id": row_id, "test_id": "P118-M001", "status": "UNKNOWN", "evidence": "evidence/preflight/fixed_inputs.json", "reason": "17 fixed inputs, task card, ABF, Chrome executable, and absent temporary root recomputed; the runtime does not expose an independently recordable actual model/reasoning label."})
        elif index == 15:
            rows.append({"row_id": row_id, "test_id": "P118-M015", "status": "PASS", "evidence": "evidence/preflight/cleanup_prelaunch.json", "reason": "No P3-118 process, candidate copy, profile, screenshot, or temporary root was ever created."})
        else:
            rows.append({"row_id": row_id, "test_id": f"P118-M{index:03d}", "status": "NOT_IMPLEMENTED", "evidence": None, "reason": blocker["id"]})
    results = {
        "schema_version": "1.0",
        "task": "LIFEOS-P3-118",
        "overall_status": "BLOCKED",
        "blocker": blocker,
        "matrix": rows,
        "counts": {"P0": 0, "P1": 0, "P2": 0, "Unknown": 1, "Not_Implemented": 13},
        "pass_formula_satisfied": False,
        "candidate_quality_assessed": False,
    }
    (output / "computer_use_pid_binding_assessment.json").write_text(json.dumps(blocker, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (output / "dynamic_closure.json").write_text(json.dumps({"schema_version": "1.0", "rows": closure, "all_required_rows_pass": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
