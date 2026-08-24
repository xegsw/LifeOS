#!/usr/bin/env python3
"""Synthetic-only operator interface for the P3-077 task-local runtime."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from permission_runtime import BOUNDARY, PermissionRuntime

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="P3-077 synthetic-only permission settings")
    p.add_argument("command", choices=("preview", "grant", "deny", "revoke", "consume"))
    p.add_argument("--run-id", default="operator-demo")
    p.add_argument("--expires-at-ms", type=int)
    p.add_argument("--permission-id")
    p.add_argument("--confirm")
    p.add_argument("--idempotency-key")
    return p

def main() -> int:
    args = parser().parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]+", args.run_id):
        print(json.dumps({"ok": False, "reason": "invalid_run_id", "external_action": "none"})); return 2
    runtime_dir = Path(__file__).resolve().parents[1] / "runtime"
    runtime_dir.mkdir(exist_ok=True)
    runtime = PermissionRuntime(runtime_dir / f"{args.run_id}.sqlite")
    try:
        if args.command == "preview": result = runtime.preview()
        elif args.command in {"grant", "deny"}: result = runtime.set_decision(args.command, {k: BOUNDARY[k] for k in ("project","category","purpose","location","processor")}, args.expires_at_ms or 0, args.confirm or "", args.idempotency_key or "")
        elif args.command == "revoke": result = runtime.revoke(args.permission_id or "", args.confirm or "", args.idempotency_key or "")
        else: result = runtime.consume({k: BOUNDARY[k] for k in ("project","category","purpose","location","processor")}, args.confirm or "")
        print(json.dumps(result, ensure_ascii=False))
        return 0 if args.command == "preview" or result.get("ok", result.get("allowed", False)) else 1
    finally: runtime.close()
if __name__ == "__main__": raise SystemExit(main())
