#!/usr/bin/env python3
"""Verify that the blocked result is complete, internally consistent, and non-passing."""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = json.loads((args.results_dir / "results.json").read_text(encoding="utf-8"))
    closure = json.loads((args.results_dir / "dynamic_closure.json").read_text(encoding="utf-8"))
    statuses = [row["status"] for row in closure["rows"]]
    checks = {
        "overall_status_is_blocked": results["overall_status"] == "BLOCKED",
        "blocked_before_actions": results["blocker"]["actions_attempted"] == 0,
        "no_chrome_started": results["blocker"]["chrome_started"] is False,
        "no_computer_use_target_query": results["blocker"]["computer_use_target_queried"] is False,
        "no_temporary_root": results["blocker"]["temporary_root_created"] is False,
        "matrix_has_15_rows": len(results["matrix"]) == 15,
        "closure_has_46_rows": len(closure["rows"]) == 46,
        "closure_all_not_implemented": all(status == "NOT_IMPLEMENTED" for status in statuses),
        "closure_not_pass": closure["all_required_rows_pass"] is False,
        "candidate_not_assessed": results["candidate_quality_assessed"] is False,
        "pass_formula_not_satisfied": results["pass_formula_satisfied"] is False,
        "honest_unknown_model_route": results["counts"] == {"P0": 0, "P1": 0, "P2": 0, "Unknown": 1, "Not_Implemented": 13},
    }
    output = {
        "schema_version": "1.0",
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if output["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
