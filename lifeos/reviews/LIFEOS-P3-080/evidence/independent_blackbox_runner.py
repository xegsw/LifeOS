#!/usr/bin/env python3
"""P3-080 independent CLI-only counterexample runner.

This deliberately drives only the copied operator CLI; it neither imports nor
references P3-079 tests or self-check runners.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def call(root: Path, db: Path, *args: str) -> tuple[int, dict]:
    command = [sys.executable, str(root / "scripts/operator_cli.py"), "--db", str(db), *args]
    run = subprocess.run(command, text=True, capture_output=True, check=False)
    try:
        result = json.loads(run.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(f"non-JSON CLI output: {run.stdout!r}; stderr={run.stderr!r}") from error
    return run.returncode, result


def assert_that(condition: bool, name: str, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    target, evidence = args.target.resolve(), args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="p3-080-blackbox-"))
    cases: list[dict] = []

    def case(name: str, fn) -> None:
        try:
            fn()
            cases.append({"id": name, "status": "PASS"})
        except Exception as error:
            cases.append({"id": name, "status": "FAIL", "detail": str(error)})

    db = scratch / "drill.sqlite"
    future = "9999999999999"
    saved: dict[str, str] = {}

    def save(key: str, text: str, confirmation: str = "CONFIRM") -> dict:
        _, result = call(target, db, "save", "--text", text, "--key", key, "--confirmation", confirmation)
        return result

    def grant(key: str, decision: str = "grant") -> dict:
        _, result = call(target, db, "permission", "--decision", decision, "--expires-at-ms", future,
                         "--key", key, "--confirmation", "CONFIRM")
        return result

    case("IR-01-unconfirmed-save", lambda: assert_that(not save("save-no", "synthetic", "")["ok"], "IR-01"))

    def initial_save() -> None:
        result = save("save-one", "non-sensitive independent test text")
        assert_that(result["ok"] and result["saved"] and not result["duplicate"], "IR-02", str(result))
        saved["record"] = result["record_id"]
    case("IR-02-confirmed-save", initial_save)
    case("IR-03-save-same-key-replay", lambda: assert_that(save("save-one", "non-sensitive independent test text").get("duplicate") is True, "IR-03"))
    case("IR-04-save-key-conflict-is-atomic", lambda: assert_that(not save("save-one", "different synthetic text")["ok"], "IR-04"))

    def default_deny() -> None:
        _, result = call(target, db, "preview-restore", "--record-id", saved["record"], "--confirmation", "CONFIRM")
        assert_that(not result["ok"] and result["reason"] == "default_deny", "IR-05", str(result))
    case("IR-05-default-deny", default_deny)

    perms: dict[str, str] = {}
    def exact_grant() -> None:
        result = grant("grant-a")
        perms["a"] = result["permission_id"]
        _, preview = call(target, db, "preview-restore", "--record-id", saved["record"], "--confirmation", "CONFIRM")
        assert_that(preview.get("allowed") == "allowed_local_synthetic", "IR-06", str(preview))
    case("IR-06-exact-grant", exact_grant)

    def deny_wins() -> None:
        result = grant("deny-a", "deny")
        perms["deny"] = result["permission_id"]
        _, preview = call(target, db, "preview-restore", "--record-id", saved["record"], "--confirmation", "CONFIRM")
        assert_that(not preview["ok"] and preview["reason"] == "explicit_deny_current", "IR-07", str(preview))
    case("IR-07-deny-priority", deny_wins)

    def expiry_and_binding() -> None:
        other_db = scratch / "expiry.sqlite"
        _, record = call(target, other_db, "save", "--text", "expiry text", "--key", "e-save", "--confirmation", "CONFIRM")
        _, expired = call(target, other_db, "permission", "--decision", "grant", "--expires-at-ms", "1", "--key", "e-grant", "--confirmation", "CONFIRM")
        assert_that(not expired["ok"], "IR-08-expired", str(expired))
        _, bad_binding = call(target, other_db, "preview-restore", "--record-id", record["record_id"], "--source", "wrong", "--confirmation", "CONFIRM")
        assert_that(not bad_binding["ok"] and bad_binding["reason"] == "binding_mismatch", "IR-08-binding", str(bad_binding))
    case("IR-08-expiry-and-binding", expiry_and_binding)

    def revocation_idempotency() -> None:
        isolated = scratch / "revoke.sqlite"
        _, first = call(target, isolated, "permission", "--decision", "grant", "--expires-at-ms", future, "--key", "r-a", "--confirmation", "CONFIRM")
        _, second = call(target, isolated, "permission", "--decision", "grant", "--expires-at-ms", future, "--key", "r-b", "--confirmation", "CONFIRM")
        _, revoked = call(target, isolated, "revoke-permission", "--permission-id", first["permission_id"], "--key", "shared", "--confirmation", "REVOKE")
        _, replay = call(target, isolated, "revoke-permission", "--permission-id", first["permission_id"], "--key", "shared", "--confirmation", "REVOKE")
        _, conflict = call(target, isolated, "revoke-permission", "--permission-id", second["permission_id"], "--key", "shared", "--confirmation", "REVOKE")
        assert_that(revoked["reason"] == "revoked" and replay["reason"] == "idempotent_repeat" and not conflict["ok"] and conflict["reason"] == "idempotency_conflict", "IR-09", str([revoked, replay, conflict]))
        # New CLI process exercises persistent conflict/audit state after restart.
        _, restarted = call(target, isolated, "revoke-permission", "--permission-id", second["permission_id"], "--key", "shared", "--confirmation", "REVOKE")
        assert_that(not restarted["ok"] and restarted["reason"] == "idempotency_conflict", "IR-09-restart", str(restarted))
    case("IR-09-revoke-key-binding-and-restart", revocation_idempotency)

    def revoked_record_never_restores() -> None:
        isolated = scratch / "record-revoke.sqlite"
        _, record = call(target, isolated, "save", "--text", "revoke test", "--key", "rr-save", "--confirmation", "CONFIRM")
        call(target, isolated, "permission", "--decision", "grant", "--expires-at-ms", future, "--key", "rr-grant", "--confirmation", "CONFIRM")
        _, revoked = call(target, isolated, "revoke-record", "--record-id", record["record_id"])
        _, preview = call(target, isolated, "preview-restore", "--record-id", record["record_id"], "--confirmation", "CONFIRM")
        assert_that(revoked["ok"] and not preview["ok"] and preview["reason"] == "revoked_content", "IR-10", str([revoked, preview]))
    case("IR-10-revoked-content-no-restore", revoked_record_never_restores)

    def restore_confirm_idempotent() -> None:
        isolated = scratch / "restore.sqlite"
        _, record = call(target, isolated, "save", "--text", "restore test", "--key", "rs-save", "--confirmation", "CONFIRM")
        call(target, isolated, "permission", "--decision", "grant", "--expires-at-ms", future, "--key", "rs-grant", "--confirmation", "CONFIRM")
        _, ready = call(target, isolated, "preview-restore", "--record-id", record["record_id"], "--confirmation", "CONFIRM")
        _, first = call(target, isolated, "confirm-restore", "--record-id", record["record_id"], "--confirmation", "CONFIRM")
        _, second = call(target, isolated, "confirm-restore", "--record-id", record["record_id"], "--confirmation", "CONFIRM")
        assert_that(ready["status"] == "ready" and first["recovered"] and second["idempotent"], "IR-11", str([ready, first, second]))
    case("IR-11-preview-confirm-replay", restore_confirm_idempotent)

    def static_closed() -> None:
        # Inspect the runtime and its operator entrypoint only.  The excluded
        # execution-side test/runner files intentionally contain literal
        # forbidden tokens for their own assertions, not implementations.
        corpus = "\n".join(p.read_text(errors="ignore") for p in [
            target / "src/integrated_runtime.py", target / "scripts/operator_cli.py"
        ])
        banned = ["requests", "socket", "urllib", "http://", "https://", "invoke(", "tauri::"]
        assert_that(not any(token in corpus for token in banned), "IR-12", "forbidden integration token found")
    case("IR-12-prohibited-channels-static-closed", static_closed)

    failed = [item for item in cases if item["status"] == "FAIL"]
    result = {"task": "LIFEOS-P3-080", "runner": "CLI-only independent blackbox", "target": str(target), "cases": cases, "passed": len(cases) - len(failed), "failed": len(failed), "p0": 0, "p1": 0 if not failed else 1, "p2": 0, "unknown": 0, "not_implemented": 0}
    (evidence / "independent_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (evidence / "independent_snapshot.json").write_text(json.dumps({"scratch_removed": True, "target_hashes": {str(p.relative_to(target)): digest(p) for p in sorted(target.rglob("*.py"))}}, indent=2) + "\n")
    shutil.rmtree(scratch)
    summary = json.dumps({"passed": result["passed"], "failed": result["failed"]})
    (evidence / "independent_runner.log").write_text(summary + "\n")
    print(summary)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
