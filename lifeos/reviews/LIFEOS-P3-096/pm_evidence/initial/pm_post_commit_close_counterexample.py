#!/usr/bin/env python3
"""PM fixed-fixture counterexample for ABF-I-01/I-02."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch


FIXED_FIRST = "P3-096 PM fixed non-sensitive first"
FIXED_SECOND = "P3-096 PM fixed non-sensitive second"
FIXED_SENTINEL = "P3-096 PM fixed non-sensitive sentinel\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runtime(source: Path):
    spec = importlib.util.spec_from_file_location("p3_096_pm_counterexample", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime load failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runtime = load_runtime(args.source.resolve())
    root = Path(tempfile.mkdtemp(prefix="pm-lifeos-p3-096-counterexample-", dir="/private/tmp"))
    try:
        db = root / "capture.sqlite"
        sentinel = root / "sentinel.txt"
        sentinel.write_text(FIXED_SENTINEL, encoding="utf-8")
        runtime.capture(db, FIXED_FIRST, "pm-first")
        runtime.render_today(db)

        def state() -> dict:
            with sqlite3.connect(db) as conn:
                return {
                    "db_sha256": digest(db),
                    "captures": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
                    "audit": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0],
                    "page_exists": (root / "today.html").exists(),
                    "sentinel_sha256": digest(sentinel),
                }

        before = state()
        original_connect = sqlite3.connect

        class CloseAfterCommitFailure:
            def __init__(self, connection):
                self._connection = connection

            def __getattr__(self, name):
                return getattr(self._connection, name)

            def close(self):
                self._connection.close()
                raise sqlite3.OperationalError("fixed post-commit close failure")

        def connect(target, *positional, **keywords):
            connection = original_connect(target, *positional, **keywords)
            if "mode=rw" in str(target):
                return CloseAfterCommitFailure(connection)
            return connection

        outcome = "accepted"
        error = ""
        try:
            with patch.object(runtime.sqlite3, "connect", connect):
                runtime.capture(db, FIXED_SECOND, "pm-second")
        except Exception as exc:  # fixed failure injection is the assertion target
            outcome = type(exc).__name__
            error = str(exc)

        after = state()
        payload = {
            "case_id": "PM-P3-096-CE-01",
            "mapped_to": ["L1-3", "L1-4", "ABF-I-01", "ABF-I-02"],
            "fixture": "fixed non-sensitive task-local SQLite and sentinel",
            "injected_failure": "connection close raises after the real commit and close complete",
            "outcome": outcome,
            "error": error,
            "failure_returned": outcome != "accepted",
            "protected_state_unchanged": before == after,
            "sentinel_unchanged": before["sentinel_sha256"] == after["sentinel_sha256"],
            "before": before,
            "after": after,
            "result": "FAIL" if outcome != "accepted" and before != after else "PASS",
            "severity": "P1",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 1 if payload["result"] == "FAIL" else 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
