#!/usr/bin/env python3
"""Offline operator entrypoint. No networking or user-directory output."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from local_capture import CaptureError, capture, delete_all, list_today, render_today, safe_snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    # Keep the caller's lexical spelling intact; the shared runtime gate rejects
    # dot/dot-dot, doubled separators, and other normalization aliases.
    parser.add_argument("--db", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("capture"); add.add_argument("--text", required=True); add.add_argument("--key", required=True); add.add_argument("--inject-failure", action="store_true")
    sub.add_parser("today")
    sub.add_parser("render")
    clear = sub.add_parser("clear"); clear.add_argument("--confirmation", required=True)
    args = parser.parse_args()
    try:
        if args.command == "capture": result = capture(args.db, args.text, args.key, inject_failure=args.inject_failure)
        elif args.command == "today": result = {"records": list_today(args.db), "snapshot": safe_snapshot(args.db)}
        elif args.command == "render": result = render_today(args.db)
        else: result = delete_all(args.db, args.confirmation)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except CaptureError as exc:
        print(json.dumps({"status": "blocked", "message": str(exc)}, ensure_ascii=False))
        return 2

if __name__ == "__main__": raise SystemExit(main())

