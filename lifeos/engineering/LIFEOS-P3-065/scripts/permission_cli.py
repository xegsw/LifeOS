#!/usr/bin/env python3
"""Operator CLI; all values are synthetic allow-list values, never paths."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from permissions import CONTROLLED_PROJECT_ID, PermissionErrorVisible, PermissionSettings

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="LIFEOS-P3-065 synthetic permission settings")
    p.add_argument("command", choices=["preview", "decide", "revoke", "consume", "snapshot"])
    p.add_argument("--synthetic-only", action="store_true", required=True)
    p.add_argument("--run-id", default="operator-session")
    p.add_argument("--project", default=CONTROLLED_PROJECT_ID); p.add_argument("--category"); p.add_argument("--purpose"); p.add_argument("--location"); p.add_argument("--processor")
    p.add_argument("--expires-at-ms", type=int); p.add_argument("--decision", choices=["grant", "deny"]); p.add_argument("--confirmation"); p.add_argument("--idempotency-key", default="")
    p.add_argument("--authorization-id"); p.add_argument("--now-ms", type=int, default=1000)
    return p

def main() -> int:
    a = parser().parse_args()
    if not a.run_id.replace("-", "").isalnum():
        print("拒绝：run-id 只能使用字母、数字和连字符", file=sys.stderr); return 2
    app = PermissionSettings(ROOT / "runtime" / (a.run_id + ".sqlite"))
    try:
        context = dict(project_id=a.project, category=a.category, purpose=a.purpose, location=a.location, processor=a.processor)
        if a.command == "preview": result = app.preview(**context, expires_at_ms=a.expires_at_ms)
        elif a.command == "decide": result = app.decide(**context, expires_at_ms=a.expires_at_ms, decision=a.decision, confirmation=a.confirmation, idempotency_key=a.idempotency_key, now_ms=a.now_ms)
        elif a.command == "revoke": result = app.revoke(authorization_id=a.authorization_id, confirmation=a.confirmation, idempotency_key=a.idempotency_key, now_ms=a.now_ms)
        elif a.command == "consume": result = app.consume(**context, now_ms=a.now_ms)
        else: result = app.snapshot()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0
    except (PermissionErrorVisible, TypeError) as exc:
        print(str(exc), file=sys.stderr); return 1
    finally: app.close()
if __name__ == "__main__": raise SystemExit(main())
