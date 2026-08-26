#!/usr/bin/env python3
"""Fail-closed verifier for the P3-120 Rework-1 manual packaged-app evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
P3_ROOT = SCRIPT.parents[3]
WORKSPACE = P3_ROOT.parents[2]
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
OUTPUT = REWORK / "rework-results.json"
ORDER = [
    "today-empty", "me", "contexts", "context-detail", "memory", "memory-detail",
    "global-ai", "ai-workspace", "settings", "capture-one", "repeat-one",
    "capture-two", "refresh", "closed", "reopen-today",
]
COUNTS = {
    "today-empty": (0, 0), "me": (0, 0), "contexts": (0, 0), "context-detail": (0, 0),
    "memory": (0, 0), "memory-detail": (0, 0), "global-ai": (0, 0), "ai-workspace": (0, 0),
    "settings": (0, 0), "capture-one": (1, 1), "repeat-one": (1, 2),
    "capture-two": (2, 3), "refresh": (2, 3), "closed": (2, 3), "reopen-today": (2, 3),
}
IMMUTABLE = {
    "initial_engineering_manifest": (P3_ROOT / "evidence/MANIFEST.md", "56f27d9e144f59b8e73cc24a398882fa6c7c6ec9750b84ff4572a5c3c99a70b0"),
    "initial_matrix": (P3_ROOT / "evidence/matrix-results.json", "68bf59499aae369520d4b001a3f1ae700a73406aa9618e5b7ff590e1eaf654e0"),
    "task_card": (WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md", "d61a1cd92924c70c5b83121d78911b90c289d0b27280e752182a19d72cb2902f"),
    "frozen_abf": (WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation_acceptance_basis_freeze.md", "e18c463ffb59f1bb80ba55d48a61009792cbd36190d998867d6f08a7aaebe219"),
}
AUTOMATION_EXCLUDED = {"Computer Use", "AppleScript", "AX", "CDP", "HTTP", "WebDriver", "browser control"}
LOG_LINES = {
    "today-empty": ["runtime_start status=restricted_offline db_scope=synthetic_task_local", "ipc_result command=runtime_status status=restricted_offline"],
    "capture-one": ["ipc_result command=capture_record status=saved record_count=1 audit_event_count=1 repeated=false", "ipc_result command=get_today status=loaded record_count=1 audit_event_count=1"],
    "repeat-one": ["ipc_result command=capture_record status=idempotent_repeat record_count=1 audit_event_count=2 repeated=true", "ipc_result command=get_today status=loaded record_count=1 audit_event_count=2"],
    "capture-two": ["ipc_result command=capture_record status=saved record_count=2 audit_event_count=3 repeated=false", "ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"],
    "refresh": ["ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"],
    "reopen-today": ["runtime_start status=restricted_offline db_scope=synthetic_task_local", "ipc_result command=runtime_status status=restricted_offline", "ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"],
}


def sha256(path: Path) -> str | None:
    if not path.is_file() or path.is_symlink():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path, errors: list[str], label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{label}: unreadable JSON: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}: expected JSON object")
        return {}
    return value


def add(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def verify_preflight(errors: list[str]) -> dict:
    preflight = load_json(REWORK / "preflight.json", errors, "preflight")
    add(preflight.get("result") == "PASS", errors, "preflight did not PASS")
    authority = preflight.get("authority", {})
    add(authority.get("actual_model") == "gpt-5.6-terra", errors, "model confirmation is not gpt-5.6-terra")
    add(authority.get("actual_reasoning_effort") == "xhigh", errors, "reasoning confirmation is not xhigh")
    for label, (path, expected) in IMMUTABLE.items():
        add(sha256(path) == expected, errors, f"immutable input changed: {label}")
    recorded = preflight.get("initial_readonly_files", {})
    delivery = recorded.get("initial_delivery", {}) if isinstance(recorded, dict) else {}
    add(delivery.get("actual_sha256") == "ef644706a21976053b81fe1019ff9294dce89099e4ab9d199b52df13fda5bdec", errors, "preflight lacks the original delivery hash")
    add(delivery.get("result") == "PASS", errors, "original delivery did not match during preflight")
    return preflight


def verify_step(step: str, errors: list[str]) -> dict:
    path = REWORK / "steps" / f"{step}.json"
    add(path.is_file() and not path.is_symlink(), errors, f"{step}: structured step is missing")
    payload = load_json(path, errors, step) if path.is_file() else {}
    add(payload.get("schema") == "lifeos-p3-120/rework-1-manual-step-v1", errors, f"{step}: wrong schema")
    add(payload.get("step") == step, errors, f"{step}: wrong step identity")
    add(payload.get("structured_result_id") == f"R1-{step}", errors, f"{step}: wrong structured result ID")
    add(payload.get("result") == "PASS", errors, f"{step}: did not PASS")
    expected_operator = "actual-app-start" if step == "today-empty" else "user-manual"
    add(payload.get("operator") == expected_operator, errors, f"{step}: operator is not {expected_operator}")
    add(bool(payload.get("attestation")), errors, f"{step}: no manual attestation")
    excluded = set(payload.get("automation_excluded", []))
    add(AUTOMATION_EXCLUDED <= excluded, errors, f"{step}: prohibited automation exclusions are incomplete")
    captures, audit = COUNTS[step]
    db = payload.get("db", {})
    if captures == 0 and audit == 0:
        empty_store_ok = db.get("exists") is False or (db.get("type") == "regular" and db.get("quick_check") == "ok")
        add(empty_store_ok, errors, f"{step}: empty state is neither an absent store nor a healthy empty SQLite store")
    else:
        add(db.get("exists") is True and db.get("type") == "regular", errors, f"{step}: synthetic DB is absent or non-regular")
        add(db.get("quick_check") == "ok", errors, f"{step}: SQLite quick_check failed")
    add(len(db.get("captures", [])) == captures, errors, f"{step}: capture count mismatch")
    add(len(db.get("audit", [])) == audit, errors, f"{step}: audit count mismatch")
    if captures == 2:
        add([item.get("content") for item in db.get("captures", [])] == ["P3-120 synthetic capture one", "P3-120 synthetic capture two"], errors, f"{step}: capture content/order mismatch")
    if audit == 3:
        add([item.get("event") for item in db.get("audit", [])] == ["capture_saved", "capture_repeat", "capture_saved"], errors, f"{step}: audit lifecycle mismatch")
    log = payload.get("log_snapshot", {})
    log_path = REWORK / str(log.get("path", ""))
    add(log_path.is_file() and not log_path.is_symlink(), errors, f"{step}: log snapshot is missing")
    add(sha256(log_path) == log.get("sha256"), errors, f"{step}: log snapshot hash mismatch")
    add(log.get("missing_expected_lines") == [], errors, f"{step}: recorder reported missing log lines")
    if log_path.is_file():
        log_text = log_path.read_text(encoding="utf-8")
        for line in LOG_LINES.get(step, []):
            add(line in log_text, errors, f"{step}: expected runtime log line is absent")
    screenshot = payload.get("screenshot")
    if step == "closed":
        add(screenshot is None, errors, "closed: screenshot must be absent")
    else:
        image_path = REWORK / str((screenshot or {}).get("path", ""))
        add(image_path.is_file() and not image_path.is_symlink(), errors, f"{step}: screenshot is missing")
        add(sha256(image_path) == (screenshot or {}).get("sha256"), errors, f"{step}: screenshot hash mismatch")
        add(image_path.stat().st_size > 10000 if image_path.is_file() else False, errors, f"{step}: screenshot is unexpectedly small")
        add(image_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") if image_path.is_file() else False, errors, f"{step}: screenshot is not PNG")
    return payload


def row(result: bool, evidence: list[str], details: str) -> dict:
    return {"result": "PASS" if result else "NOT PASS", "evidence": evidence, "details": details}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-cleanup", action="store_true", help="Require exact temp-root cleanup after the user manually closes the reopened app.")
    arguments = parser.parse_args()
    errors: list[str] = []
    preflight = verify_preflight(errors)
    steps = {step: verify_step(step, errors) for step in ORDER}
    session = load_json(REWORK / "session.json", errors, "session")
    add(session.get("manual_only") is True, errors, "session is not marked manual_only")
    launches = session.get("launches", [])
    add(len(launches) == 2 and launches[0].get("id") == "launch-1" and launches[1].get("id") == "launch-2", errors, "session does not record exactly two launches")
    add(len({entry.get("pid") for entry in launches}) == 2, errors, "launch PIDs are not distinct")
    actual_log = REWORK / "actual-app.log"
    log_text = actual_log.read_text(encoding="utf-8") if actual_log.is_file() else ""
    add(log_text.count("runtime_start status=restricted_offline db_scope=synthetic_task_local") == 2, errors, "actual app log does not prove two restricted starts")
    add(log_text.count("ipc_result command=runtime_status status=restricted_offline") == 2, errors, "actual app log does not prove runtime status on both starts")
    refresh_sha = steps.get("refresh", {}).get("db", {}).get("sha256")
    add(refresh_sha == steps.get("capture-two", {}).get("db", {}).get("sha256"), errors, "refresh changed the persisted DB")
    add(steps.get("closed", {}).get("app", {}).get("running") is False, errors, "closed step did not record process exit")
    add(steps.get("reopen-today", {}).get("app", {}).get("launch_count") == 2, errors, "reopen step does not use launch two")
    cleanup_ok = (not TEMP_ROOT.exists()) and (not TEMP_ROOT.is_symlink())
    if arguments.require_cleanup:
        add(cleanup_ok, errors, "exact temp root remains after requested cleanup")
    rows = {
        "M-001": row(not any("preflight" in error or "model confirmation" in error or "reasoning confirmation" in error or "immutable input" in error for error in errors), ["preflight.json"], "Initial assets were hashed before rework; model is recorded as gpt-5.6-terra + xhigh."),
        "M-004": row(all(step in steps for step in ["today-empty", "me", "contexts", "context-detail", "memory", "memory-detail", "global-ai", "ai-workspace", "settings"]), [f"steps/{step}.json" for step in ORDER[:9]], "Manual navigation screenshots and structured results cover the specified pages."),
        "M-005": row("runtime_start status=restricted_offline db_scope=synthetic_task_local" in log_text, ["actual-app.log", "steps/today-empty.json"], "Packaged runtime reported restricted offline status."),
        "M-006": row(not any(error.startswith("capture-one:") for error in errors), ["steps/capture-one.json"], "Manual first capture verifies saved then get_today at 1/1."),
        "M-007": row(not any(error.startswith("repeat-one:") for error in errors), ["steps/repeat-one.json"], "Manual repeat verifies deterministic idempotence at 1/2."),
        "M-008": row(not any(error.startswith("capture-two:") for error in errors), ["steps/capture-two.json"], "Manual second capture verifies ordered two-record lifecycle at 2/3."),
        "M-009": row(not any(error.startswith("refresh:") for error in errors) and refresh_sha == steps.get("capture-two", {}).get("db", {}).get("sha256"), ["steps/refresh.json"], "Manual refresh used get_today while DB hash remained identical."),
        "M-010": row(not any(error.startswith("closed:") or error.startswith("reopen-today:") for error in errors) and "actual app log does not prove two restricted starts" not in errors, ["steps/closed.json", "steps/reopen-today.json"], "User closed then reopened the same packaged runtime and data remained 2/3."),
        "M-015": row(cleanup_ok if arguments.require_cleanup else False, ["cleanup.json"], "Exact temporary root is absent after the final user close and cleanup." if arguments.require_cleanup else "Pending final close and cleanup."),
    }
    if not arguments.require_cleanup:
        rows["M-015"]["result"] = "PENDING"
    final_pass = not errors and (cleanup_ok if arguments.require_cleanup else True)
    payload = {
        "schema": "lifeos-p3-120/rework-1-verifier-v1",
        "verification_phase": "post-cleanup" if arguments.require_cleanup else "observed-before-cleanup",
        "automation": "manual packaged-app operation; verifier reads only recorded evidence",
        "preflight_model": {"model": preflight.get("authority", {}).get("actual_model"), "reasoning_effort": preflight.get("authority", {}).get("actual_reasoning_effort")},
        "rows": rows,
        "errors": errors,
        "result": "PASS" if final_pass else "NOT PASS",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "phase": payload["verification_phase"], "error_count": len(errors)}))
    return 0 if final_pass else 1


if __name__ == "__main__":
    sys.exit(main())
