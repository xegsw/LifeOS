#!/usr/bin/env python3
"""Append one actual GUI capture pair to the P3-117 structured closure ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
PLAN = TASK_ROOT / "test_plan.json"
RESULT = TASK_ROOT / "evidence/action_results.json"
GEOMETRY = TASK_ROOT / "evidence/captures/geometry"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--capture-id", required=True)
    parser.add_argument("--note", required=True)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    case = next((item for item in plan["cases"] if item["case_id"] == args.case), None)
    if case is None:
        raise RuntimeError(f"unknown frozen test case: {args.case}")
    geometry_path = GEOMETRY / f"{args.capture_id}.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    if set(geometry.get("phases", ())) != {"proof", "clean"}:
        raise RuntimeError(f"capture pair incomplete: {args.capture_id}")
    if geometry["signature"].split("|", 1)[0] != case["action"]:
        raise RuntimeError(f"probe action mismatch: expected {case['action']} got {geometry['signature']}")
    if case.get("viewport") and geometry["viewport_css"] != case["viewport"]:
        raise RuntimeError(f"viewport mismatch: expected {case['viewport']} got {geometry['viewport_css']}")

    existing = json.loads(RESULT.read_text(encoding="utf-8")) if RESULT.exists() else {"task": "LIFEOS-P3-117", "results": []}
    if any(row["case_id"] == args.case for row in existing["results"]):
        raise RuntimeError(f"case already recorded: {args.case}")
    record = {
        "case_id": args.case,
        "matrix": case["matrix"],
        "capture_id": args.capture_id,
        "actual_action": case["action"],
        "expected_anchor": case["anchor"],
        "expected_viewport": case.get("viewport", geometry["viewport_css"]),
        "probe_signature": geometry["signature"],
        "geometry_path": str(geometry_path.relative_to(TASK_ROOT)),
        "geometry_sha256": digest(geometry_path),
        "proof_path": geometry["phases"]["proof"]["crop_path"],
        "proof_sha256": geometry["phases"]["proof"]["crop_sha256"],
        "clean_path": geometry["phases"]["clean"]["crop_path"],
        "clean_sha256": geometry["phases"]["clean"]["crop_sha256"],
        "actual_observation": args.note,
        "status": "PASS",
        "allow_same_state": bool(case.get("allow_same_state", False)),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    existing["results"].append(record)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "case": args.case, "capture_id": args.capture_id}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
