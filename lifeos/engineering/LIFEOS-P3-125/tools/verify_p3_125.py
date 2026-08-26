#!/usr/bin/env python3
"""Machine-check the P3-125 task-local closure without touching historical assets."""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
RESULT = ROOT / "evidence" / "results" / "verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sqlite_summary(path: Path) -> dict:
    with sqlite3.connect(path) as connection:
        captures = connection.execute("SELECT count(*) FROM captures").fetchone()[0]
        audit_rows = connection.execute("SELECT event, detail FROM audit ORDER BY id").fetchall()
        row = connection.execute(
            "SELECT content, source, idem_key FROM captures ORDER BY created_at_ms"
        ).fetchone()
    return {
        "captures": captures,
        "audit": [{"event": event, "detail": detail} for event, detail in audit_rows],
        "record": None if row is None else {"content": row[0], "source": row[1], "idem_key": row[2]},
    }


def check(name: str, actual, expected=True) -> dict:
    return {"id": name, "pass": actual == expected, "actual": actual, "expected": expected}


def main() -> int:
    candidate = ROOT / "candidate"
    runtime = candidate / "src" / "runtime.rs"
    build_rs = candidate / "build.rs"
    source_text = runtime.read_text(encoding="utf-8")
    build_text = build_rs.read_text(encoding="utf-8")
    history = {
        REPO / "lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_acceptance_basis_freeze.md": "4ab5ed8a0c1349041d1d9b13452be5059abf510f4d2ecae386e23283c1956057",
        REPO / "lifeos/tasks/LIFEOS-P3-125_source_allowlist.md": "807ff8e1dd565eed4fec4c1b6bf5c6bca133861a9dffdbae1ca2bac60293dc4b",
        REPO / "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json": "b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c",
        REPO / "lifeos/reviews/LIFEOS-P3-122_pm_review.md": "1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe",
        REPO / "lifeos/reviews/LIFEOS-P3-124/rework-1/independent_review.md": "224b568e643ca7c3ba4f1468bfd01e4f3d3c0c529dd75d7d5c9ec8dc9d02221a",
    }
    checks = [check(f"hash:{path.name}", sha256(path), expected) for path, expected in history.items()]

    lineage = json.loads((ROOT / "evidence" / "results" / "source-lineage.json").read_text(encoding="utf-8"))
    checks.extend(
        [
            check("allowlist_rows", lineage["entry_count"], 75),
            check("allowlist_hash", lineage["allowlist_sha256"], "807ff8e1dd565eed4fec4c1b6bf5c6bca133861a9dffdbae1ca2bac60293dc4b"),
            check("build_time_root_embedded", "option_env!(\"LIFEOS_RUNTIME_ROOT\")" in source_text),
            check("build_time_root_required", "missing required build-time root" in build_text),
            check("single_root_db_derivation", "db_path: root.join(DB_NAME)" in source_text),
            check("single_root_viewport_derivation", "viewport_request: root.join(\"viewport-request.txt\")" in source_text),
            check("single_root_geometry_derivation", "paths.root.join(format!(\"native-geometry-{requested}.jsonl\"))" in source_text),
            check("no_legacy_runtime_root_literal", "/private/tmp/lifeos-p3-122-native-evidence-v1" not in source_text),
            check("no_independent_viewport_environment", "LIFEOS_P3_122_VIEWPORT" not in source_text),
            check("symlink_fail_closed", "no_linked_ancestor" in build_text and "ensure_real_directory_chain" in source_text),
            check("three_ipc_unchanged", "[\"capture_record\", \"get_today\", \"runtime_status\"]" in source_text),
        ]
    )
    failure_log_expectations = {
        "build-empty.log": "root is empty or contains a NUL byte",
        "build-relative.log": "root must be an absolute normalized path",
        "build-traversal.log": "root must be an absolute normalized path",
        "build-symlink.log": "root or an ancestor is not a real directory",
        "build-root-file.log": "root or an ancestor is not a real directory",
    }
    for filename, expected_message in failure_log_expectations.items():
        log = ROOT / "evidence" / "logs" / filename
        checks.append(check(f"fail_closed_log:{filename}", log.is_file() and expected_message in log.read_text(encoding="utf-8")))
    unit_log = ROOT / "evidence" / "logs" / "unit-test-final.log"
    checks.append(check("unit_test_final", unit_log.is_file() and "test result: ok. 4 passed" in unit_log.read_text(encoding="utf-8")))

    expected_record = {
        "content": "明天先把发布页的第一屏文字读一遍，再决定是否继续做视觉细节。",
        "source": "local_capture",
        "idem_key": "p3-122-synthetic-one",
    }
    expected_audit = [
        {"event": "capture_saved", "detail": "local_capture"},
        {"event": "capture_repeat", "detail": "same_idempotency_key"},
    ]
    final_snapshot = ROOT / "evidence" / "runtime-snapshots" / "final-capture.sqlite"
    reopen_snapshot = ROOT / "evidence" / "runtime-snapshots" / "final-reopened-capture.sqlite"
    final_summary = sqlite_summary(final_snapshot)
    reopened_summary = sqlite_summary(reopen_snapshot)
    checks.extend(
        [
            check("final_snapshot_capture_count", final_summary["captures"], 1),
            check("final_snapshot_audit", final_summary["audit"], expected_audit),
            check("final_snapshot_record", final_summary["record"], expected_record),
            check("reopened_snapshot_capture_count", reopened_summary["captures"], 1),
            check("reopened_snapshot_audit", reopened_summary["audit"], expected_audit),
            check("reopened_snapshot_record", reopened_summary["record"], expected_record),
        ]
    )
    geometry = ROOT / "evidence" / "runtime-snapshots" / "final-geometry.jsonl"
    geometry_rows = [json.loads(line) for line in geometry.read_text(encoding="utf-8").splitlines() if line]
    checks.extend(
        [
            check("native_geometry_has_actual_tauri_rows", all(row["source"] == "actual-tauri-native-window" for row in geometry_rows)),
            check("native_geometry_task", all(row["task"] == "LIFEOS-P3-125" for row in geometry_rows)),
        ]
    )
    evidence_files = [
        ROOT / "evidence" / "actual-app" / "run-b-initial.jpeg",
        ROOT / "evidence" / "actual-app" / "run-b-after-first.jpeg",
        ROOT / "evidence" / "actual-app" / "final-reopened.jpeg",
        ROOT / "evidence" / "actual-app" / "final-runtime-loaded.jpeg",
    ]
    checks.append(check("actual_app_screenshots_present", all(path.is_file() and path.stat().st_size > 0 for path in evidence_files)))

    output = {
        "task": "LIFEOS-P3-125",
        "result": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "checks": checks,
        "sha256": {
            "runtime_rs": sha256(runtime),
            "build_rs": sha256(build_rs),
            "final_capture_snapshot": sha256(final_snapshot),
            "final_reopened_capture_snapshot": sha256(reopen_snapshot),
            "final_geometry_snapshot": sha256(geometry),
        },
        "actual_app": {
            "run_a": "first capture plus idempotent repeat, then close/reopen",
            "run_b": "fresh compiled root begins empty then saves one fixed synthetic record",
            "final": "final source build captured once, repeated once, and retained the same database state after reopen",
        },
        "build_fail_closed_cases": {
            "empty": "root is empty or contains a NUL byte",
            "relative": "root must be an absolute normalized path",
            "traversal": "root must be an absolute normalized path",
            "symlink": "root or an ancestor is not a real directory",
        },
        "model_effort_attestation": "Unknown: task runtime did not expose an independent session model/effort attestation API.",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": output["result"], "checks": len(checks), "failed": [item["id"] for item in checks if not item["pass"]]}, ensure_ascii=False))
    return 0 if output["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
