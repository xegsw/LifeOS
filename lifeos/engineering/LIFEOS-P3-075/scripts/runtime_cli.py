#!/usr/bin/env python3
"""Explicit operator CLI for the P3-075 task-local runtime drill."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from local_runtime import BOUNDARIES, CONTROLLED_PROJECT_ID, ControlledLocalRuntime, VisibleRuntimeError, receipt_json, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="P3-075 non-sensitive task-local runtime drill")
    parser.add_argument("--non-sensitive-test-only", action="store_true", help="required acknowledgement")
    parser.add_argument("--text", required=True, help="operator-provided non-sensitive test text")
    parser.add_argument("--idempotency-key", required=True, help="operator-provided key")
    parser.add_argument("--confirm-save", action="store_true", help="required explicit save confirmation")
    parser.add_argument("--next-step", required=True, help="operator-provided next step")
    parser.add_argument("--confirm-next-step", action="store_true", help="required explicit next-step confirmation")
    parser.add_argument("--run-id", default="operator-run", help="local runtime label")
    parser.add_argument("--inject-precommit-failure", action="store_true", help="controlled negative test only")
    args = parser.parse_args()
    if not args.non_sensitive_test_only:
        parser.error("--non-sensitive-test-only is required; do not enter personal or confidential data")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,64}", args.run_id):
        parser.error("--run-id accepts only letters, numbers, and hyphens")
    runtime = ROOT / "runtime"
    snapshot = runtime / f"{args.run_id}_snapshot.json"
    app = ControlledLocalRuntime(runtime / f"{args.run_id}.sqlite")
    try:
        receipt = app.save(text=args.text, idempotency_key=args.idempotency_key, confirmed=args.confirm_save,
                           now_ms=1786550400000, fail_before_commit=args.inject_precommit_failure)
        view = app.record_view(receipt.record_id)
        context = app.restore_context(CONTROLLED_PROJECT_ID)
        next_step = app.confirm_next_step(project_id=CONTROLLED_PROJECT_ID, next_step=args.next_step,
                                          confirmed=args.confirm_next_step, now_ms=1786550400001)
        write_json(snapshot, {"receipt": receipt_json(receipt), "record": view, "context": context,
                              "next_step": next_step, "boundaries": BOUNDARIES})
        print("已保存：事务已提交；原文、来源与内容身份可见；下一步已由操作者确认")
        return 0
    except VisibleRuntimeError as exc:
        write_json(snapshot, {"receipt": {"saved": False, "message": str(exc)},
                              "boundaries": {"network": "disabled", "external_action": "none"}})
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        app.close()


if __name__ == "__main__":
    raise SystemExit(main())
