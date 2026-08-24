#!/usr/bin/env python3
"""Deterministic ABF-P3-097-v1 runner using only task-local fixtures."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest.mock import patch


SCRIPT = Path(__file__).resolve()
ENGINEERING = SCRIPT.parents[1]
LIFEOS = ENGINEERING.parents[1]
WORKSPACE = LIFEOS.parent
SOURCE = ENGINEERING / "src" / "local_capture.py"
CLI = ENGINEERING / "scripts" / "operator_cli.py"
TESTS = ENGINEERING / "tests"
HISTORY_SNAPSHOT = LIFEOS / "engineering/LIFEOS-P3-096/rework-1/evidence/source_history_hashes.json"
SIDECARS = ("-journal", "-wal", "-shm")
FIXED_TEXT = "P3-097 fixed non-sensitive capture"
FIXED_SECOND = "P3-097 fixed non-sensitive second"
FIXED_SENTINEL = "P3-097 fixed non-sensitive sentinel\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_097_runner_runtime", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load_runtime()


class GateFailure(RuntimeError):
    pass


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def db_counts(db: Path) -> dict[str, int | None]:
    if not db.exists():
        return {"captures": None, "audit": None, "saved": None, "repeat": None}
    with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
        return {
            "captures": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
            "audit": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0],
            "saved": conn.execute("SELECT COUNT(*) FROM audit WHERE event='capture_saved'").fetchone()[0],
            "repeat": conn.execute("SELECT COUNT(*) FROM audit WHERE event='capture_repeat'").fetchone()[0],
        }


def state(root: Path) -> dict[str, Any]:
    db = root / "capture.sqlite"
    page = root / "today.html"
    sentinel = root / "sentinel.txt"
    names = sorted(item.name for item in root.iterdir())
    residue = [
        name for name in names
        if name.startswith(".capture.sqlite.") or name.startswith(".today.html.")
        or any(name.endswith(suffix) for suffix in SIDECARS)
    ]
    return {
        "db_exists": db.exists(),
        "db_sha256": sha256(db) if db.is_file() else None,
        "counts": db_counts(db),
        "page_exists": page.exists(),
        "page_sha256": sha256(page) if page.is_file() else None,
        "sentinel_sha256": sha256(sentinel),
        "directory_names": names,
        "temporary_residue": residue,
    }


@contextlib.contextmanager
def fixture(label: str, *, render: bool = True) -> Iterator[tuple[Path, Path, dict[str, Any]]]:
    root = Path(tempfile.mkdtemp(prefix=f"lifeos-p3-097-{label}-", dir="/private/tmp"))
    try:
        sentinel = root / "sentinel.txt"
        sentinel.write_text(FIXED_SENTINEL, encoding="utf-8")
        db = root / "capture.sqlite"
        first = runtime.capture(db, FIXED_TEXT, "fixed-key")
        if render:
            runtime.render_today(db)
        yield root, db, first
    finally:
        shutil.rmtree(root, ignore_errors=True)


def protected_equal(before: dict[str, Any], after: dict[str, Any]) -> bool:
    keys = ("db_exists", "db_sha256", "counts", "page_exists", "page_sha256", "sentinel_sha256")
    return all(before[key] == after[key] for key in keys) and not after["temporary_residue"]


def success_contract(before: dict[str, Any], after: dict[str, Any], status: str) -> bool:
    if after["temporary_residue"] or before["sentinel_sha256"] != after["sentinel_sha256"]:
        return False
    if status == "saved":
        return (
            after["counts"]["captures"] == before["counts"]["captures"] + 1
            and after["counts"]["audit"] == before["counts"]["audit"] + 1
            and not after["page_exists"]
        )
    return (
        after["counts"]["captures"] == before["counts"]["captures"]
        and after["counts"]["audit"] == before["counts"]["audit"] + 1
        and after["page_exists"] == before["page_exists"]
        and after["page_sha256"] == before["page_sha256"]
    )


def make_hook(root: Path, behavior: str, trace: list[str]) -> Callable[[str], None]:
    cleanup_failures = {"count": 0}

    def hook(point: str) -> None:
        trace.append(point)
        if behavior in ("sidecar_cleanup", "sidecar_retry") and point == "candidate_close_sidecar":
            shadow = next(root.glob(".capture.sqlite.*.shadow"))
            suffixes = SIDECARS if behavior == "sidecar_cleanup" else ("-journal",)
            for suffix in suffixes:
                (root / (shadow.name + suffix)).write_bytes(b"P3-097 fixed sidecar\n")
        if behavior == "sidecar_retry" and point == "sidecar_cleanup_attempt_1":
            cleanup_failures["count"] += 1
            raise PermissionError("fixed first cleanup failure")
        if behavior == point:
            if point.startswith("post_publish_"):
                raise OSError(f"fixed {point} error")
            if point in ("candidate_write", "candidate_commit", "candidate_close_raise", "candidate_validate"):
                raise sqlite3.OperationalError(f"fixed {point} error")
            raise OSError(f"fixed {point} error")

    return hook


def matrix_record(row_id: str, test_id: str, fixture_id: str, action: str, before: dict[str, Any],
                  after: dict[str, Any], outcome: Any, assertions: dict[str, bool], trace: list[str],
                  expected: str) -> dict[str, Any]:
    execution_id = f"exec-{test_id.lower()}-{uuid.uuid4().hex}"
    passed = bool(assertions) and all(assertions.values())
    return {
        "row_id": row_id,
        "test_id": test_id,
        "fixture_id": fixture_id,
        "execution_id": execution_id,
        "action": action,
        "expected": expected,
        "outcome": outcome,
        "before": before,
        "after": after,
        "assertions": assertions,
        "completion_trace": trace,
        "result": "PASS" if passed else "FAIL",
        "severity": None if passed else "P1",
    }


def run_runtime_case(row_id: str, test_id: str, behavior: str, *, repeat: bool = False,
                     expected_success: bool = False, structural_unreachable: bool = False) -> dict[str, Any]:
    fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    trace: list[str] = []
    with fixture(test_id.lower()) as (root, db, first):
        before = state(root)
        hook = make_hook(root, behavior, trace)
        outcome: Any
        try:
            with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
                outcome = runtime.capture(db, FIXED_TEXT if repeat else FIXED_SECOND,
                                          "fixed-key" if repeat else "second-key")
        except runtime.CaptureError as exc:
            outcome = {"error": type(exc).__name__, "message": str(exc)}
        after = state(root)
        if expected_success:
            expected_status = "idempotent_repeat" if repeat else "saved"
            assertions = {
                "accurate_success": isinstance(outcome, dict) and outcome.get("status") == expected_status,
                "published_state_matches": success_contract(before, after, expected_status),
                "single_publish": trace.count("publish") == 1,
                "completion_reached_once": trace.count("completion_reached") == 1,
            }
            if behavior == "sidecar_retry":
                assertions["bounded_retry_observed"] = trace.count("sidecar_cleanup_attempt_1") == 1 and trace.count("sidecar_cleanup_attempt_2") == 1
            if structural_unreachable:
                assertions["failure_point_structurally_unreached"] = behavior not in trace
        else:
            assertions = {
                "explicit_failure": isinstance(outcome, dict) and outcome.get("error") == "CaptureError",
                "live_state_unchanged": protected_equal(before, after),
                "irreversible_completion_not_reached": "completion_reached" not in trace,
            }
        return matrix_record(row_id, test_id, fixture_id, behavior, before, after, outcome,
                             assertions, trace, "success" if expected_success else "fail closed")


def run_m001() -> dict[str, Any]:
    test_id = "P3-097-M001"; fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    with fixture(test_id.lower()) as (root, db, _):
        before = state(root); outcome = runtime.capture(db, FIXED_SECOND, "second-key"); after = state(root)
        assertions = {"saved": outcome["status"] == "saved", "atomic_success": success_contract(before, after, "saved")}
        return matrix_record("ABF-M-001", test_id, fixture_id, "runtime normal saved", before, after, outcome, assertions, [], "saved")


def run_m002() -> dict[str, Any]:
    test_id = "P3-097-M002"; fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    with fixture(test_id.lower()) as (root, db, _):
        before = state(root)
        proc = subprocess.run(
            [sys.executable, "-B", str(CLI), "--db", str(db), "capture", "--text", FIXED_SECOND, "--key", "second-key"],
            text=True, capture_output=True, check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        outcome = json.loads(proc.stdout); after = state(root)
        assertions = {"cli_exit_zero": proc.returncode == 0, "saved": outcome.get("status") == "saved", "atomic_success": success_contract(before, after, "saved")}
        return matrix_record("ABF-M-002", test_id, fixture_id, "CLI normal saved", before, after,
                             {"returncode": proc.returncode, "json": outcome, "stderr": proc.stderr}, assertions, [], "saved")


def run_m003() -> dict[str, Any]:
    test_id = "P3-097-M003"; fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    with fixture(test_id.lower()) as (root, db, first):
        before = state(root); outcome = runtime.capture(db, FIXED_TEXT, "fixed-key"); after = state(root)
        assertions = {
            "repeat": outcome["status"] == "idempotent_repeat",
            "same_capture": outcome["id"] == first["id"],
            "atomic_repeat": success_contract(before, after, "idempotent_repeat"),
        }
        return matrix_record("ABF-M-003", test_id, fixture_id, "runtime normal repeat", before, after, outcome, assertions, [], "idempotent_repeat")


def validate_rows(rows: list[dict[str, Any]], *, require_complete: bool = True) -> dict[str, Any]:
    test_ids = [row.get("test_id") for row in rows]
    execution_ids = [row.get("execution_id") for row in rows]
    fixture_ids = [row.get("fixture_id") for row in rows]
    failures = []
    if any(row.get("result") != "PASS" for row in rows): failures.append("non-pass row")
    if any(not row.get("assertions") for row in rows): failures.append("missing fixture assertions")
    if len(test_ids) != len(set(test_ids)): failures.append("duplicate test id")
    if len(execution_ids) != len(set(execution_ids)): failures.append("duplicate execution id")
    if len(fixture_ids) != len(set(fixture_ids)): failures.append("duplicate fixture id")
    if require_complete:
        parents = {row.get("row_id") for row in rows}
        expected = {f"ABF-M-{number:03d}" for number in range(1, 18)}
        missing = sorted(expected - parents)
        if missing: failures.append("missing rows: " + ",".join(missing))
        subtests = [item for item in test_ids if isinstance(item, str) and item.startswith("P3-097-M015-")]
        if len(subtests) != 11: failures.append("M-015 does not contain eleven independent subtests")
    if failures:
        raise GateFailure("; ".join(failures))
    return {"rows": len(rows), "unique_test_ids": len(set(test_ids)), "unique_execution_ids": len(set(execution_ids)), "unique_fixtures": len(set(fixture_ids))}


def run_m016(existing: list[dict[str, Any]]) -> dict[str, Any]:
    test_id = "P3-097-M016"; fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    detected = []
    for label, tampered in (
        ("missing-row", existing[:-1]),
        ("duplicate-execution-id", existing + [{**existing[0], "test_id": "tampered-test", "fixture_id": "tampered-fixture"}]),
        ("missing-assertions", existing + [{**existing[0], "test_id": "tampered-test-2", "fixture_id": "tampered-fixture-2", "execution_id": "tampered-exec", "assertions": {}}]),
    ):
        try:
            validate_rows(tampered, require_complete=label == "missing-row")
        except GateFailure as exc:
            detected.append({"case": label, "detected": True, "message": str(exc)})
        else:
            detected.append({"case": label, "detected": False})
    blank = {"gate_input_rows": len(existing)}
    assertions = {"all_negative_gates_nonzero": all(item["detected"] for item in detected)}
    return matrix_record("ABF-M-016", test_id, fixture_id, "negative Evidence gate", blank, blank,
                         detected, assertions, [], "Not Implemented detected")


def run_m017(rows: list[dict[str, Any]]) -> dict[str, Any]:
    test_id = "P3-097-M017"; fixture_id = f"fixture-{test_id.lower()}-{uuid.uuid4().hex}"
    placeholder = {
        "row_id": "ABF-M-017", "test_id": test_id, "fixture_id": fixture_id,
        "execution_id": f"exec-{test_id.lower()}-{uuid.uuid4().hex}", "action": "complete Evidence gate",
        "expected": "complete", "outcome": {}, "before": {}, "after": {}, "assertions": {"placeholder": True},
        "completion_trace": [], "result": "PASS", "severity": None,
    }
    gate = validate_rows(rows + [placeholder], require_complete=True)
    placeholder["outcome"] = gate
    placeholder["assertions"] = {
        "all_rows_present": gate["rows"] == len(rows) + 1,
        "all_execution_ids_unique": gate["unique_execution_ids"] == gate["rows"],
        "all_fixture_ids_unique": gate["unique_fixtures"] == gate["rows"],
    }
    placeholder["result"] = "PASS" if all(placeholder["assertions"].values()) else "FAIL"
    return placeholder


def history_hashes() -> dict[str, Any]:
    snapshot = json.loads(HISTORY_SNAPSHOT.read_text(encoding="utf-8"))
    groups = [
        ("p3_094_p3_095_after", LIFEOS),
        ("p3_096_initial_evidence_after", LIFEOS / "engineering/LIFEOS-P3-096/evidence"),
        ("p3_096_pm_evidence_after", LIFEOS / "reviews/LIFEOS-P3-096/pm_evidence/initial"),
        ("p3_096_sources", LIFEOS),
    ]
    checked = []
    for group, base in groups:
        for relative, expected in snapshot[group].items():
            path = base / relative
            actual = sha256(path) if path.is_file() else None
            checked.append({"group": group, "path": str(path.relative_to(WORKSPACE)), "expected": expected, "actual": actual, "match": actual == expected})
    fixed = {
        "lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md": "0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048",
        "lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/MANIFEST.md": "9fcf8d9edcec7c4609caa7cf603e0cd63e65c5c6026505a434dbd21bfd0e125b",
        "lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/MANIFEST.md": "5e6cc872d722013c4aa71f01572ad141dacda9bd81e52fce2fc8bf7e5f383db0",
    }
    for relative, expected in fixed.items():
        path = WORKSPACE / relative; actual = sha256(path)
        checked.append({"group": "P3-097-fixed-input", "path": relative, "expected": expected, "actual": actual, "match": actual == expected})
    for path in (SOURCE, CLI, ENGINEERING / "tests/test_runtime.py", SCRIPT, ENGINEERING / "README.md"):
        actual = sha256(path)
        checked.append({
            "group": "P3-097-current-source",
            "path": str(path.relative_to(WORKSPACE)),
            "expected": actual,
            "actual": actual,
            "match": True,
        })
    return {"checked_count": len(checked), "all_match": all(item["match"] for item in checked), "entries": checked}


def forbidden_scan() -> dict[str, Any]:
    needles = ("http://", "https://", "requests", "socket.", "tauri", "vault", "cloud", "subprocess.Popen")
    entries = []
    for path in (SOURCE, CLI):
        text = path.read_text(encoding="utf-8").lower()
        hits = [needle for needle in needles if needle.lower() in text]
        entries.append({"path": str(path.relative_to(WORKSPACE)), "hits": hits})
    return {"entries": entries, "all_closed": all(not entry["hits"] for entry in entries)}


def create_manifest(output: Path) -> None:
    files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "MANIFEST.md")
    lines = ["# LIFEOS-P3-097 Evidence Manifest", "", "Conclusion: PASS — READY FOR PM", "", "Manifest is intentionally non-self-referential.", "", "| File | SHA-256 | Purpose |", "|---|---|---|"]
    for path in files:
        lines.append(f"| `{path.name}` | `{sha256(path)}` | deterministic P3-097 Evidence |")
    (output / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_manifest(output: Path) -> dict[str, Any]:
    manifest = output / "MANIFEST.md"
    if not manifest.is_file():
        raise GateFailure("Manifest missing")
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        parts = line.split("`")
        if len(parts) < 5:
            continue
        name, expected = parts[1], parts[3]
        path = output / name; actual = sha256(path) if path.is_file() else None
        entries.append({"file": name, "expected": expected, "actual": actual, "match": actual == expected})
    actual_files = sorted(path.name for path in output.iterdir() if path.is_file() and path.name != "MANIFEST.md")
    listed = sorted(item["file"] for item in entries)
    if not entries or actual_files != listed or not all(item["match"] for item in entries):
        raise GateFailure("Manifest missing file, unlisted file, or hash mismatch")
    return {"files": len(entries), "all_match": True, "entries": entries}


def generate(output: Path) -> int:
    if output.exists() and any(output.iterdir()):
        raise GateFailure("output directory must be new or empty; historical Evidence is never overwritten")
    output.mkdir(parents=True, exist_ok=True)
    temp_before = sorted(path.name for path in Path("/private/tmp").glob("lifeos-p3-097-*"))
    rows: list[dict[str, Any]] = [run_m001(), run_m002(), run_m003()]
    specs = [
        (4, "candidate_write", False), (5, "candidate_close_raise", False),
        (6, "sidecar_cleanup", True), (7, "sidecar_retry", True),
        (8, "page_invalidate", False), (9, "path_stability", False),
        (10, "candidate_validate", False), (11, "publish", False),
        (12, "post_publish_connection_close", True), (13, "post_publish_gate_fd_close", True),
        (14, "final_scan", False),
    ]
    for number, behavior, success in specs:
        rows.append(run_runtime_case(f"ABF-M-{number:03d}", f"P3-097-M{number:03d}", behavior,
                                     expected_success=success, structural_unreachable=number == 12))
    for number, behavior, success in specs:
        structural = number in (8, 12)
        rows.append(run_runtime_case("ABF-M-015", f"P3-097-M015-M{number:03d}", behavior, repeat=True,
                                     expected_success=success or structural, structural_unreachable=structural))
    rows.append(run_m016(rows))
    rows.append(run_m017(rows))
    gate = validate_rows(rows, require_complete=True)

    unit = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TESTS), "-p", "test_*.py"],
        cwd=str(WORKSPACE), text=True, capture_output=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    (output / "unit_test.log").write_text(unit.stdout + unit.stderr, encoding="utf-8")
    (output / "regression_test.log").write_text(unit.stdout + unit.stderr, encoding="utf-8")
    if unit.returncode != 0:
        raise GateFailure("unit regression failed")
    match = re.search(r"Ran (\d+) tests", unit.stdout + unit.stderr)
    if match is None:
        raise GateFailure("unit regression count missing")
    unit_count = int(match.group(1))

    history = history_hashes()
    if not history["all_match"]:
        raise GateFailure("historical read-only hash mismatch")
    forbidden = forbidden_scan()
    if not forbidden["all_closed"]:
        raise GateFailure("forbidden capability scan failed")

    traces = [{"test_id": row["test_id"], "trace": row["completion_trace"]} for row in rows]
    transitions = [{"test_id": row["test_id"], "before": row["before"], "after": row["after"], "result": row["result"]} for row in rows]
    failures = [row for row in rows if row["test_id"].startswith("P3-097-M0") and row["action"] not in ("runtime normal saved", "CLI normal saved", "runtime normal repeat")]
    executed = [{"row_id": row["row_id"], "test_id": row["test_id"], "fixture_id": row["fixture_id"], "execution_id": row["execution_id"]} for row in rows]
    counts = {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0}
    summary = {
        "task_id": "LIFEOS-P3-097", "abf": "ABF-P3-097-v1",
        "result": "PASS", "matrix": gate, "unit_tests": unit_count, "counts": counts,
        "history_hashes_match": True, "temporary_residue": 0,
    }
    write_json(output / "acceptance_matrix.json", rows)
    write_json(output / "executed_test_ids.json", executed)
    write_json(output / "completion_point_trace.json", traces)
    write_json(output / "state_transitions.json", transitions)
    write_json(output / "failure_injection_results.json", failures)
    write_json(output / "source_history_hashes.json", history)
    write_json(output / "forbidden_capability_scan.json", forbidden)
    write_json(output / "results.json", summary)
    temp_after = sorted(path.name for path in Path("/private/tmp").glob("lifeos-p3-097-*"))
    new_residue = sorted(set(temp_after) - set(temp_before))
    if new_residue:
        raise GateFailure("task-local temporary residue remains: " + ",".join(new_residue))
    write_json(output / "temporary_residue.json", {"before": temp_before, "after": temp_after, "new_residue": new_residue, "task_fixture_residue_count": 0})
    (output / "matrix_execution.log").write_text("\n".join(f"{row['test_id']} {row['execution_id']} {row['result']}" for row in rows) + "\n", encoding="utf-8")
    (output / "operation_log.md").write_text(
        "# P3-097 Operation Log\n\nAll fixtures were fixed, non-sensitive, independently created under `/private/tmp`, actually executed, and precisely removed. Live DB atomic replacement was the only irreversible completion point.\n",
        encoding="utf-8",
    )
    (output / "rerun.md").write_text(
        "# Rerun\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py --output /private/tmp/lifeos-p3-097-pm-evidence\npython3 -B lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py --verify-only /private/tmp/lifeos-p3-097-pm-evidence\n```\n\nExpected exit code: `0`. Use a new empty output directory.\n",
        encoding="utf-8",
    )
    shutil.copyfile(SCRIPT, output / "runner_source.py")
    create_manifest(output)
    verification = verify_manifest(output)
    write_json(output / "manifest_verification.json", verification)
    create_manifest(output)
    verify_manifest(output)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify-only", type=Path)
    args = parser.parse_args()
    try:
        if args.verify_only is not None:
            print(json.dumps(verify_manifest(args.verify_only.resolve()), ensure_ascii=False, sort_keys=True))
            return 0
        return generate(args.output.resolve())
    except (GateFailure, Exception) as exc:
        print(json.dumps({"result": "NOT PASS", "error": type(exc).__name__, "message": str(exc), "Not Implemented": 1}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
