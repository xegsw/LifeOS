#!/usr/bin/env python3
"""Operator CLI for a task-local synthetic recovery plan; accepts no filesystem path."""
import argparse, json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from recovery import RecoveryPlan, SyntheticRecovery

ROOT = Path(__file__).resolve().parents[1]
def local_db(run_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9-]{1,40}", run_id):
        raise ValueError("invalid_run_id")
    return str(ROOT / "runtime" / (run_id + ".sqlite"))

def main() -> int:
    p = argparse.ArgumentParser(description="synthetic-only recovery drill")
    p.add_argument("--run-id", required=True); p.add_argument("--record-id", required=True)
    p.add_argument("--source", required=True); p.add_argument("--version", required=True, type=int)
    p.add_argument("--confirm", default="")
    args = p.parse_args()
    if os.environ.get("LIFEOS_SYNTHETIC_ONLY") != "1":
        print(json.dumps({"status":"failed", "reason":"synthetic_only_acknowledgement_required"})); return 1
    drill = SyntheticRecovery(local_db(args.run_id))
    plan = RecoveryPlan(args.source, args.record_id, args.version, "saved")
    preview = drill.preview(plan)
    result = {"preview": preview, "execution": drill.recover(plan, args.confirm) if args.confirm else {"status":"not_executed", "reason":"preview_only"}, "snapshot": drill.snapshot()}
    print(json.dumps(result, sort_keys=True))
    drill.close()
    return 0 if result["execution"]["status"] in {"recovered", "not_executed", "blocked"} else 1
if __name__ == "__main__": raise SystemExit(main())
