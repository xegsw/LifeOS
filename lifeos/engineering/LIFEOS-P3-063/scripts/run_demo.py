#!/usr/bin/env python3
"""Operator-facing, synthetic-only CLI for the controlled local MVP loop."""

import argparse
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mvp import CONTROLLED_PROJECT_ID, LocalMvp, asdict, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="LIFEOS-P3-063 local synthetic-only MVP loop")
    parser.add_argument("--synthetic-only", action="store_true", help="required acknowledgement: do not enter personal or real data")
    parser.add_argument("--text", required=True, help="operator-provided synthetic original text")
    parser.add_argument("--idempotency-key", required=True, help="operator-provided synthetic request key")
    parser.add_argument("--next-step", required=True, help="operator-provided text to explicitly confirm")
    parser.add_argument("--run-id", default="operator-session", help="local runtime label, letters/numbers/hyphen only")
    parser.add_argument("--inject-write-failure", action="store_true", help="controlled negative test: fail before commit")
    args = parser.parse_args()
    if not args.synthetic_only:
        parser.error("--synthetic-only is required; this tool accepts non-sensitive synthetic records only")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,64}", args.run_id):
        parser.error("--run-id must contain only letters, numbers, or hyphens")

    runtime = ROOT / "runtime"
    db = runtime / (args.run_id + ".sqlite")
    snapshot_path = runtime / (args.run_id + "_snapshot.json")
    app = LocalMvp(db)
    try:
        try:
            receipt = app.capture(original_text=args.text, idempotency_key=args.idempotency_key,
                                  now_ms=1786550400000, fail_before_commit=args.inject_write_failure)
            restored = app.restore_project(CONTROLLED_PROJECT_ID)
            confirmation = app.confirm_next_step(project_id=CONTROLLED_PROJECT_ID,
                                                 next_step_text=args.next_step, now_ms=1786550400001)
            write_json(snapshot_path, {"receipt": asdict(receipt), "record": app.view_record(receipt.record_id),
                                       "restored": restored, "confirmation": confirmation,
                                       "operator_input": {"synthetic_only_acknowledged": True, "run_id": args.run_id},
                                       "runtime_boundary": {"synthetic_only": True, "ai_features": "disabled",
                                                            "network": "disabled", "tauri_ipc": "not_used"}})
            print("PASS demo: capture committed, source visible, controlled project restored, next step explicitly confirmed")
            return 0
        except Exception as exc:
            write_json(snapshot_path, {"receipt": {"saved": False, "message": str(exc)},
                                       "operator_input": {"synthetic_only_acknowledged": True, "run_id": args.run_id},
                                       "runtime_boundary": {"synthetic_only": True, "ai_features": "disabled",
                                                            "network": "disabled", "tauri_ipc": "not_used"}})
            print(str(exc), file=sys.stderr)
            return 1
    finally:
        app.close()


if __name__ == "__main__":
    raise SystemExit(main())
