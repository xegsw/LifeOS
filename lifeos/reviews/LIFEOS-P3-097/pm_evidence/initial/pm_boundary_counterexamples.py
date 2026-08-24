#!/usr/bin/env python3
"""PM-owned deterministic counterexamples for ABF-P3-097-v1."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
from pathlib import Path
from unittest.mock import patch


WORKSPACE = Path(__file__).resolve().parents[5]
SOURCE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py"
ROOT = Path("/private/tmp/lifeos-p3-097-pm-counterexample")
TEXT_ONE = "P3-097 PM fixed non-sensitive first"
TEXT_TWO = "P3-097 PM fixed non-sensitive second"
SENTINEL = b"P3-097 PM fixed non-sensitive sentinel\n"


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_097_pm_runtime", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load_runtime()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> dict:
    db = root / "capture.sqlite"
    page = root / "today.html"
    sentinel = root / "sentinel.txt"
    counts = None
    if db.is_file():
        with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
            counts = {
                "captures": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
                "audit": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0],
            }
    names = sorted(item.name for item in root.iterdir())
    residue = [
        name for name in names
        if name.startswith(".capture.sqlite.")
        or name.startswith(".today.html.")
        or name.endswith(("-journal", "-wal", "-shm"))
    ]
    return {
        "db_exists": db.is_file(),
        "db_sha256": digest(db.read_bytes()) if db.is_file() else None,
        "counts": counts,
        "page_exists": page.is_file(),
        "page_sha256": digest(page.read_bytes()) if page.is_file() else None,
        "sentinel_sha256": digest(sentinel.read_bytes()),
        "residue": residue,
    }


def new_fixture(name: str, *, seed: bool = True) -> tuple[Path, Path]:
    root = ROOT / name
    root.mkdir()
    (root / "sentinel.txt").write_bytes(SENTINEL)
    db = root / "capture.sqlite"
    if seed:
        runtime.capture(db, TEXT_ONE, "pm-key-one")
        runtime.render_today(db)
    return root, db


def replace_failure(root: Path, db: Path, *, repeat: bool) -> dict:
    before = snapshot(root)
    real_replace = runtime.os.replace
    observed = []

    def fail_live_publish(src, dst, *args, **kwargs):
        src_name = os.fspath(src)
        dst_name = os.fspath(dst)
        if dst_name == runtime.DB_NAME and Path(src_name).name.startswith(".capture.sqlite."):
            observed.append("live_replace_failed")
            raise OSError("fixed live os.replace failure")
        return real_replace(src, dst, *args, **kwargs)

    error = None
    with patch.object(runtime.os, "replace", side_effect=fail_live_publish):
        try:
            runtime.capture(db, TEXT_ONE if repeat else TEXT_TWO,
                            "pm-key-one" if repeat else "pm-key-two")
        except runtime.CaptureError as exc:
            error = type(exc).__name__
    after = snapshot(root)
    passed = error == "CaptureError" and observed == ["live_replace_failed"] and before == after
    return {"pass": passed, "error": error, "observed": observed, "before": before, "after": after}


def missing_db_replace_failure() -> dict:
    root, db = new_fixture("missing-db-replace", seed=False)
    before = snapshot(root)
    real_replace = runtime.os.replace
    observed = []

    def fail_live_publish(src, dst, *args, **kwargs):
        if os.fspath(dst) == runtime.DB_NAME:
            observed.append("live_replace_failed")
            raise OSError("fixed initial live os.replace failure")
        return real_replace(src, dst, *args, **kwargs)

    error = None
    with patch.object(runtime.os, "replace", side_effect=fail_live_publish):
        try:
            runtime.capture(db, TEXT_ONE, "pm-key-one")
        except runtime.CaptureError as exc:
            error = type(exc).__name__
    after = snapshot(root)
    passed = error == "CaptureError" and observed == ["live_replace_failed"] and before == after
    return {"pass": passed, "error": error, "observed": observed, "before": before, "after": after}


def post_publish_fd_close(*, repeat: bool) -> dict:
    root, db = new_fixture("repeat-fd-close" if repeat else "saved-fd-close")
    before = snapshot(root)
    observed = []

    def hook(point: str):
        if point == "post_publish_gate_fd_close":
            observed.append(point)
            raise OSError("fixed post-publish gate fd close error")

    with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
        result = runtime.capture(db, TEXT_ONE if repeat else TEXT_TWO,
                                 "pm-key-one" if repeat else "pm-key-two")
    after = snapshot(root)
    expected_status = "idempotent_repeat" if repeat else "saved"
    expected_counts = {"captures": 1 if repeat else 2, "audit": 2}
    page_ok = after["page_exists"] == before["page_exists"] if repeat else not after["page_exists"]
    passed = (
        result.get("status") == expected_status
        and observed == ["post_publish_gate_fd_close"]
        and after["counts"] == expected_counts
        and page_ok
        and after["sentinel_sha256"] == before["sentinel_sha256"]
        and not after["residue"]
    )
    return {"pass": passed, "result": result, "observed": observed, "before": before, "after": after}


def persistent_candidate_sidecar_failure() -> dict:
    root, db = new_fixture("persistent-sidecar")
    before = snapshot(root)

    def hook(point: str):
        if point == "candidate_close_sidecar":
            shadow = next(root.glob(".capture.sqlite.*.shadow"))
            (root / f"{shadow.name}-journal").write_bytes(b"P3-097 PM fixed sidecar\n")
        if point.startswith("sidecar_cleanup_attempt_"):
            raise PermissionError("fixed persistent pre-publish cleanup failure")

    error = None
    with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
        try:
            runtime.capture(db, TEXT_TWO, "pm-key-two")
        except runtime.CaptureError as exc:
            error = type(exc).__name__
    after = snapshot(root)
    passed = error == "CaptureError" and before == after
    return {"pass": passed, "error": error, "before": before, "after": after}


def external_render_clear_targets() -> dict:
    root, db = new_fixture("external-targets")
    outside = ROOT / "fixed-outside-target.html"
    outside.write_bytes(b"P3-097 PM fixed non-sensitive outside sentinel\n")
    outside_before = digest(outside.read_bytes())
    before = snapshot(root)
    errors = []
    for action in (
        lambda: runtime.render_today(db, outside),
        lambda: runtime.delete_all(db, "DELETE", outside),
    ):
        try:
            action()
        except runtime.CaptureError:
            errors.append("CaptureError")
    after = snapshot(root)
    passed = errors == ["CaptureError", "CaptureError"] and before == after and digest(outside.read_bytes()) == outside_before
    return {"pass": passed, "errors": errors, "before": before, "after": after, "outside_unchanged": digest(outside.read_bytes()) == outside_before}


def ancestor_directory_symlink() -> dict:
    real_root, real_db = new_fixture("real-parent")
    before = snapshot(real_root)
    linked_root = ROOT / "linked-parent"
    linked_root.symlink_to(real_root, target_is_directory=True)
    error = None
    try:
        runtime.capture(linked_root / "capture.sqlite", TEXT_TWO, "pm-key-two")
    except runtime.CaptureError as exc:
        error = type(exc).__name__
    after = snapshot(real_root)
    passed = error == "CaptureError" and before == after and linked_root.is_symlink()
    return {"pass": passed, "error": error, "before": before, "after": after}


def final_db_and_page_symlinks() -> dict:
    target_root, target_db = new_fixture("symlink-target")
    target_before = snapshot(target_root)

    db_link_root = ROOT / "db-link-root"
    db_link_root.mkdir()
    (db_link_root / "sentinel.txt").write_bytes(SENTINEL)
    (db_link_root / "capture.sqlite").symlink_to(target_db)
    db_error = None
    try:
        runtime.capture(db_link_root / "capture.sqlite", TEXT_TWO, "pm-key-two")
    except runtime.CaptureError as exc:
        db_error = type(exc).__name__

    page_link_root, page_db = new_fixture("page-link-root")
    outside_page = ROOT / "fixed-outside-page.html"
    outside_page.write_bytes(b"P3-097 PM fixed non-sensitive outside page\n")
    outside_before = digest(outside_page.read_bytes())
    (page_link_root / "today.html").unlink()
    (page_link_root / "today.html").symlink_to(outside_page)
    page_db_before = digest(page_db.read_bytes())
    page_error = None
    try:
        runtime.capture(page_db, TEXT_TWO, "pm-key-two")
    except runtime.CaptureError as exc:
        page_error = type(exc).__name__

    passed = (
        db_error == "CaptureError"
        and page_error == "CaptureError"
        and snapshot(target_root) == target_before
        and digest(page_db.read_bytes()) == page_db_before
        and digest(outside_page.read_bytes()) == outside_before
        and (page_link_root / "today.html").is_symlink()
    )
    return {"pass": passed, "db_error": db_error, "page_error": page_error, "outside_unchanged": digest(outside_page.read_bytes()) == outside_before}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if ROOT.exists():
        raise RuntimeError(f"refusing existing fixture root: {ROOT}")
    results = {}
    try:
        ROOT.mkdir()
        root, db = new_fixture("saved-replace")
        results["existing_saved_actual_replace_failure"] = replace_failure(root, db, repeat=False)
        root, db = new_fixture("repeat-replace")
        results["repeat_actual_replace_failure"] = replace_failure(root, db, repeat=True)
        results["missing_db_actual_replace_failure"] = missing_db_replace_failure()
        results["saved_post_publish_fd_close"] = post_publish_fd_close(repeat=False)
        results["repeat_post_publish_fd_close"] = post_publish_fd_close(repeat=True)
        results["persistent_candidate_sidecar_failure"] = persistent_candidate_sidecar_failure()
        results["external_render_clear_targets"] = external_render_clear_targets()
        results["ancestor_directory_symlink"] = ancestor_directory_symlink()
        results["final_db_and_page_symlinks"] = final_db_and_page_symlinks()
        payload = {
            "task_id": "LIFEOS-P3-097",
            "abf": "ABF-P3-097-v1",
            "fixed_non_sensitive_only": True,
            "cases": results,
            "pass_count": sum(1 for item in results.values() if item["pass"]),
            "fail_count": sum(1 for item in results.values() if not item["pass"]),
        }
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"pass_count": payload["pass_count"], "fail_count": payload["fail_count"]}, sort_keys=True))
        return 0 if payload["fail_count"] == 0 else 1
    finally:
        shutil.rmtree(ROOT, ignore_errors=False)


if __name__ == "__main__":
    raise SystemExit(main())
