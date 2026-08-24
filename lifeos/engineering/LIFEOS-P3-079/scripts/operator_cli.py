#!/usr/bin/env python3
"""Local CLI for the P3-079 synthetic drill; all values are operator supplied."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.integrated_runtime import IntegratedRuntime

p = argparse.ArgumentParser()
p.add_argument("--db", required=True)
sub = p.add_subparsers(dest="command", required=True)
for name in ("save", "preview-restore", "confirm-restore", "revoke-record"):
    q = sub.add_parser(name); q.add_argument("--record-id"); q.add_argument("--confirmation", default="")
    q.add_argument("--text", default=""); q.add_argument("--key", default=""); q.add_argument("--source", default="operator_local_entry"); q.add_argument("--version", type=int, default=1)
perm = sub.add_parser("permission"); perm.add_argument("--decision", required=True); perm.add_argument("--expires-at-ms", type=int, required=True); perm.add_argument("--confirmation", default=""); perm.add_argument("--key", required=True)
revoke = sub.add_parser("revoke-permission"); revoke.add_argument("--permission-id", required=True); revoke.add_argument("--confirmation", default=""); revoke.add_argument("--key", required=True)
args = p.parse_args(); runtime = IntegratedRuntime(Path(args.db))
try:
    if args.command == "save": out = runtime.save(args.text, args.key, args.confirmation)
    elif args.command == "permission": out = runtime.set_permission(args.decision, args.expires_at_ms, args.confirmation, args.key)
    elif args.command == "preview-restore": out = runtime.restore_preview(args.record_id, args.source, args.version, args.confirmation)
    elif args.command == "confirm-restore": out = runtime.restore_confirm(args.record_id, args.source, args.version, args.confirmation)
    elif args.command == "revoke-record": out = runtime.revoke_record(args.record_id)
    else: out = runtime.revoke_permission(args.permission_id, args.confirmation, args.key)
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
finally: runtime.close()
