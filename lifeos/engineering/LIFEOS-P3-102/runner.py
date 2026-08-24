#!/usr/bin/env python3
"""LIFEOS-P3-102 redacted real-use runner.

The real text and idempotency key are accepted only through stdin, used in
memory, and never written to task Evidence. The only persistent copies of the
text are the user-authorized capture.sqlite and today.html.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


WORKSPACE = Path("/Users/xxe/Documents/No.2")
TASK_ROOT = WORKSPACE / "lifeos/engineering/LIFEOS-P3-102"
EVIDENCE = TASK_ROOT / "evidence"
CANDIDATE_ROOT = WORKSPACE / "lifeos/engineering/LIFEOS-P3-097"
CLI = CANDIDATE_ROOT / "scripts/operator_cli.py"
RUNTIME = CANDIDATE_ROOT / "src/local_capture.py"
ABF = WORKSPACE / "lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement_acceptance_basis_freeze.md"
TARGET = Path("/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1")
DB = TARGET / "capture.sqlite"
PAGE = TARGET / "today.html"
TMP_PREFIX = "/private/tmp/lifeos-p3-102-"
SESSION_RECEIPT_RECORDED = "2026-08-23T10:59:39+08:00"

EXPECTED_HASHES = {
    ABF: "361849606a9164ad0ffc215688084a466dd6495ff5589719591773bcdc40a243",
    RUNTIME: "1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453",
    CLI: "ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659",
    CANDIDATE_ROOT / "evidence/MANIFEST.md": "63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311",
    WORKSPACE / "lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md": "90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183",
    WORKSPACE / "lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md": "4f74f685d2ba5857c7fb9a469ae3397ddf06349bd9f9a34193b933773dfb6958",
    WORKSPACE / "lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md": "4ddf1158c63bbeecb0b2dd83fea44d19aa24d52b4bd2c33e25df966ba412c266",
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, payload: Any) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def lexical_exists(path: Path) -> bool:
    return os.path.lexists(path)


def ancestor_facts() -> list[dict[str, Any]]:
    facts = []
    for path in (Path("/"), Path("/Users"), Path("/Users/xxe"), Path("/Users/xxe/Documents")):
        item = os.lstat(path)
        facts.append({
            "path": str(path),
            "is_directory": stat.S_ISDIR(item.st_mode),
            "is_symlink": stat.S_ISLNK(item.st_mode),
            "device": item.st_dev,
            "inode": item.st_ino,
        })
    return facts


def candidate_hashes() -> list[dict[str, Any]]:
    rows = []
    for path, expected in EXPECTED_HASHES.items():
        actual = sha_file(path)
        rows.append({
            "path": str(path.relative_to(WORKSPACE)),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        })
    return rows


def cli(command: str, *args: str) -> tuple[int, dict[str, Any] | None, str]:
    invocation = [sys.executable, str(CLI), "--db", str(DB), command, *args]
    completed = subprocess.run(invocation, text=True, capture_output=True, check=False)
    parsed = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = None
    return completed.returncode, parsed, completed.stderr


def fixture_cli(db: Path, command: str, *args: str) -> tuple[int, dict[str, Any] | None, str]:
    invocation = [sys.executable, str(CLI), "--db", str(db), command, *args]
    completed = subprocess.run(invocation, text=True, capture_output=True, check=False)
    parsed = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = None
    return completed.returncode, parsed, completed.stderr


def db_state() -> dict[str, Any]:
    conn = sqlite3.connect(f"{DB.as_uri()}?mode=ro&immutable=1", uri=True)
    try:
        captures = conn.execute(
            "SELECT content,created_at,source,typeof(content),typeof(created_at),typeof(source) FROM captures ORDER BY created_at,id"
        ).fetchall()
        audits = conn.execute(
            "SELECT event,created_at,detail FROM audit ORDER BY id"
        ).fetchall()
        return {
            "capture_count": len(captures),
            "audit_count": len(audits),
            "content_sha256": [sha_bytes(row[0].encode("utf-8")) for row in captures],
            "created_at": [row[1] for row in captures],
            "sources": [row[2] for row in captures],
            "field_types_valid": all(row[3:] == ("text", "text", "text") for row in captures),
            "audit_events": [row[0] for row in audits],
            "audit_times": [row[1] for row in audits],
            "audit_details": [row[2] for row in audits],
            "db_sha256": sha_file(DB),
            "db_size": DB.stat().st_size,
        }
    finally:
        conn.close()


def allowed_artifacts(path: Path) -> tuple[list[str], list[str]]:
    allowed = {"capture.sqlite", "today.html"}
    names = sorted(item.name for item in path.iterdir())
    return names, sorted(set(names) - allowed)


def path_type_boundary_matrix(temp_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fixed_text = "fixed non-sensitive boundary fixture"
    fixed_key = "fixture-key"

    def add(test_id: str, observed: bool, detail: str) -> None:
        rows.append({
            "test_id": test_id,
            "fixture_id": "P3-102-BOUNDARY-FIXED",
            "execution_id": f"EXEC-{test_id}",
            "status": "PASS" if observed else "FAIL",
            "detail": detail,
        })

    relative = Path("relative/capture.sqlite")
    code, payload, _ = fixture_cli(relative, "today")
    add("ABF-M-010-RELATIVE", code == 2 and payload and payload.get("status") == "blocked", "relative DB path rejected")

    dotdir = temp_root / "dotdot" / "inner"
    dotdir.mkdir(parents=True)
    dotpath = f"{dotdir}/../capture.sqlite"
    code, payload, _ = fixture_cli(Path(dotpath), "today")
    add("ABF-M-010-DOTDOT", code == 2 and payload and payload.get("status") == "blocked", "dot-dot DB path rejected")

    real_parent = temp_root / "real-parent"
    real_parent.mkdir()
    linked_parent = temp_root / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    code, payload, _ = fixture_cli(linked_parent / "capture.sqlite", "today")
    add("ABF-M-010-ANCESTOR-SYMLINK", code == 2 and payload and payload.get("status") == "blocked", "ancestor symlink rejected")

    db_link_dir = temp_root / "db-symlink"
    db_link_dir.mkdir()
    external = temp_root / "external-file"
    external.write_bytes(b"sentinel")
    (db_link_dir / "capture.sqlite").symlink_to(external)
    before = sha_file(external)
    code, payload, _ = fixture_cli(db_link_dir / "capture.sqlite", "today")
    add("ABF-M-010-DB-SYMLINK", code == 2 and payload and payload.get("status") == "blocked" and sha_file(external) == before, "final DB symlink rejected without target change")

    hard_dir = temp_root / "db-hardlink"
    hard_dir.mkdir()
    hard_source = temp_root / "hard-source"
    hard_source.write_bytes(b"sentinel")
    os.link(hard_source, hard_dir / "capture.sqlite")
    before = sha_file(hard_source)
    code, payload, _ = fixture_cli(hard_dir / "capture.sqlite", "today")
    add("ABF-M-010-DB-HARDLINK", code == 2 and payload and payload.get("status") == "blocked" and sha_file(hard_source) == before, "multi-link DB rejected without target change")

    fifo_dir = temp_root / "db-special"
    fifo_dir.mkdir()
    os.mkfifo(fifo_dir / "capture.sqlite")
    code, payload, _ = fixture_cli(fifo_dir / "capture.sqlite", "today")
    add("ABF-M-010-DB-SPECIAL", code == 2 and payload and payload.get("status") == "blocked", "special-file DB rejected")

    page_link_dir = temp_root / "page-symlink"
    page_link_dir.mkdir()
    code, payload, _ = fixture_cli(page_link_dir / "capture.sqlite", "capture", "--text", fixed_text, "--key", fixed_key)
    setup_ok = code == 0 and payload and payload.get("status") == "saved"
    page_target = temp_root / "page-external"
    page_target.write_bytes(b"page-sentinel")
    (page_link_dir / "today.html").symlink_to(page_target)
    before = sha_file(page_target)
    code, payload, _ = fixture_cli(page_link_dir / "capture.sqlite", "render")
    add("ABF-M-010-PAGE-SYMLINK", bool(setup_ok and code == 2 and payload and payload.get("status") == "blocked" and sha_file(page_target) == before), "final page symlink rejected without target change")

    page_hard_dir = temp_root / "page-hardlink"
    page_hard_dir.mkdir()
    code, payload, _ = fixture_cli(page_hard_dir / "capture.sqlite", "capture", "--text", fixed_text, "--key", fixed_key)
    setup_ok = code == 0 and payload and payload.get("status") == "saved"
    page_hard_target = temp_root / "page-hard-target"
    page_hard_target.write_bytes(b"page-sentinel")
    os.link(page_hard_target, page_hard_dir / "today.html")
    before = sha_file(page_hard_target)
    code, payload, _ = fixture_cli(page_hard_dir / "capture.sqlite", "render")
    add("ABF-M-010-PAGE-HARDLINK", bool(setup_ok and code == 2 and payload and payload.get("status") == "blocked" and sha_file(page_hard_target) == before), "multi-link page rejected without target change")

    output_dir = temp_root / "caller-output"
    output_dir.mkdir()
    code, payload, _ = fixture_cli(output_dir / "capture.sqlite", "capture", "--text", fixed_text, "--key", fixed_key)
    setup_ok = code == 0 and payload and payload.get("status") == "saved"
    caller_target = temp_root / "caller-selected-output"
    completed = subprocess.run(
        [sys.executable, str(CLI), "--db", str(output_dir / "capture.sqlite"), "render", "--output", str(caller_target)],
        text=True,
        capture_output=True,
        check=False,
    )
    add("ABF-M-010-CALLER-OUTPUT", bool(setup_ok and completed.returncode != 0 and not lexical_exists(caller_target)), "caller-selected output argument rejected by CLI")
    return rows


def closed_capabilities(invoked_commands: list[str]) -> dict[str, Any]:
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    imports = sorted({node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "names", None)})
    forbidden_imports = sorted(set(imports) & {"socket", "requests", "urllib", "httpx", "boto3", "tauri"})
    cli_text = CLI.read_text(encoding="utf-8")
    return {
        "test_id": "ABF-M-011",
        "fixture_id": "P3-102-CLOSED-CAPABILITIES",
        "execution_id": "EXEC-ABF-M-011",
        "status": "PASS" if "clear" not in invoked_commands and not forbidden_imports else "FAIL",
        "invoked_commands": invoked_commands,
        "clear_exposed_by_fixed_candidate": "sub.add_parser(\"clear\")" in cli_text,
        "clear_policy": "prohibited and not invoked",
        "forbidden_network_imports": forbidden_imports,
        "tauri_ipc_vault_export_cloud_sync_multidevice_l3_external_user": "closed/not invoked",
    }


def redact_scan(secret_text: str, secret_key: str) -> dict[str, Any]:
    hits = []
    needles = [secret_text.encode("utf-8"), secret_key.encode("utf-8")]
    for path in sorted(EVIDENCE.glob("*")):
        if path.is_file() and path.name != "MANIFEST.md":
            data = path.read_bytes()
            if any(needle and needle in data for needle in needles):
                hits.append(path.name)
    return {"exact_secret_hits": hits, "hit_count": len(hits)}


def build_acceptance(visual_confirmed: bool) -> list[dict[str, Any]]:
    preflight = json.loads((EVIDENCE / "preflight.json").read_text())
    lifecycle = json.loads((EVIDENCE / "lifecycle_matrix.json").read_text())
    restart = json.loads((EVIDENCE / "restart_matrix.json").read_text())
    failure = json.loads((EVIDENCE / "failure_matrix.json").read_text())
    boundary = json.loads((EVIDENCE / "boundary_matrix.json").read_text())
    closed = json.loads((EVIDENCE / "closed_capabilities.json").read_text())
    integrity = json.loads((EVIDENCE / "input_integrity.json").read_text())
    retention = json.loads((EVIDENCE / "retention_state.json").read_text())
    residue = json.loads((EVIDENCE / "temporary_residue.json").read_text())
    rows = [
        ("ABF-M-001", "PASS", "session_start.json"),
        ("ABF-M-002", "PASS" if preflight["status"] == "PASS" else "FAIL", "preflight.json"),
        ("ABF-M-003", "PASS", "input_attestation.json"),
        ("ABF-M-004", lifecycle["first_capture"]["status"], "lifecycle_matrix.json"),
        ("ABF-M-005", lifecycle["idempotent_repeat"]["status"], "lifecycle_matrix.json"),
        ("ABF-M-006", lifecycle["idempotency_conflict"]["status"], "lifecycle_matrix.json"),
        ("ABF-M-007", restart["today_new_process"]["status"], "restart_matrix.json"),
        ("ABF-M-008", "PASS" if visual_confirmed and restart["render_new_process"]["technical_status"] == "PASS" else "NOT_IMPLEMENTED", "restart_matrix.json"),
        ("ABF-M-009", failure["status"], "failure_matrix.json"),
        ("ABF-M-010", "PASS" if all(row["status"] == "PASS" for row in boundary["rows"]) else "FAIL", "boundary_matrix.json"),
        ("ABF-M-011", closed["status"], "closed_capabilities.json"),
        ("ABF-M-012", "PASS" if integrity["status"] == "PASS" and retention["status"] == "PASS" and residue["status"] == "PASS" else "FAIL", "input_integrity.json; retention_state.json; temporary_residue.json"),
    ]
    return [
        {
            "row_id": row_id,
            "test_id": row_id,
            "fixture_id": f"P3-102-{row_id}",
            "execution_id": f"EXEC-{row_id}",
            "status": status,
            "evidence": evidence,
        }
        for row_id, status, evidence in rows
    ]


def finalize_outputs(visual_confirmed: bool, secret_text: str, secret_key: str) -> None:
    acceptance = build_acceptance(visual_confirmed)
    write_json("acceptance_matrix.json", acceptance)
    counts = {name: 0 for name in ("P0", "P1", "P2", "Unknown", "Not Implemented")}
    failed = [row for row in acceptance if row["status"] != "PASS"]
    if failed:
        counts["Not Implemented"] = sum(row["status"] == "NOT_IMPLEMENTED" for row in failed)
        counts["P0"] = sum(row["status"] == "FAIL" for row in failed)
    write_json("results.json", {
        "task_id": "LIFEOS-P3-102",
        "status": "PASS" if not failed else "PENDING_USER_VISUAL_CONFIRMATION" if all(row["row_id"] == "ABF-M-008" for row in failed) else "FAIL",
        "matrix_pass": sum(row["status"] == "PASS" for row in acceptance),
        "matrix_total": len(acceptance),
        "counts": counts,
        "failed_or_pending_rows": [row["row_id"] for row in failed],
        "risk_state": {"R-0052": "Open", "R-0040": "unchanged", "R-0051": "unchanged"},
        "stage": "Limited Stage 3; Stage 4 not entered",
    })
    scan = redact_scan(secret_text, secret_key)
    integrity = json.loads((EVIDENCE / "input_integrity.json").read_text())
    integrity["evidence_redaction_scan"] = scan
    integrity["status"] = "PASS" if not scan["hit_count"] and integrity["historical_hashes_unchanged"] else "FAIL"
    write_json("input_integrity.json", integrity)
    acceptance = build_acceptance(visual_confirmed)
    write_json("acceptance_matrix.json", acceptance)
    failed = [row for row in acceptance if row["status"] != "PASS"]
    counts = {name: 0 for name in ("P0", "P1", "P2", "Unknown", "Not Implemented")}
    counts["Not Implemented"] = sum(row["status"] == "NOT_IMPLEMENTED" for row in failed)
    counts["P0"] = sum(row["status"] == "FAIL" for row in failed)
    write_json("results.json", {
        "task_id": "LIFEOS-P3-102",
        "status": "PASS" if not failed else "PENDING_USER_VISUAL_CONFIRMATION" if all(row["row_id"] == "ABF-M-008" for row in failed) else "FAIL",
        "matrix_pass": sum(row["status"] == "PASS" for row in acceptance),
        "matrix_total": len(acceptance),
        "counts": counts,
        "failed_or_pending_rows": [row["row_id"] for row in failed],
        "risk_state": {"R-0052": "Open", "R-0040": "unchanged", "R-0051": "unchanged"},
        "stage": "Limited Stage 3; Stage 4 not entered",
    })
    operation_lines = [
        "# LIFEOS-P3-102 Redacted Operation Log",
        "",
        "- User text and idempotency key are intentionally omitted.",
        "- Invoked real-target commands: capture, capture, capture(conflict), today, render, capture(inject-failure).",
        "- Prohibited clear command was not invoked.",
        "- Boundary fixtures used fixed non-sensitive synthetic text only.",
        f"- Matrix status: {sum(row['status'] == 'PASS' for row in acceptance)}/{len(acceptance)} PASS.",
        f"- User visual confirmation: {'confirmed' if visual_confirmed else 'pending'}.",
    ]
    (EVIDENCE / "operation_log.md").write_text("\n".join(operation_lines) + "\n", encoding="utf-8")
    (EVIDENCE / "rerun.md").write_text(
        "# Rerun\n\nHigh-risk real input must not be replayed automatically. "
        "A new run requires a new PM task, user authorization, Frozen ABF, exact-path preflight, "
        "and user-provided stdin. Do not use clear.\n",
        encoding="utf-8",
    )
    mapping = ["# Acceptance to Evidence Matrix", ""]
    for row in acceptance:
        mapping.append(f"- {row['row_id']} -> {row['test_id']} -> {row['evidence']} -> {row['status']}")
    (EVIDENCE / "evidence_mapping.md").write_text("\n".join(mapping) + "\n", encoding="utf-8")
    final_scan = redact_scan(secret_text, secret_key)
    if final_scan["hit_count"]:
        raise RuntimeError("redaction gate failed")
    manifest_entries: list[tuple[str, str]] = []
    for path in sorted(EVIDENCE.iterdir()):
        if path.is_file() and path.name != "MANIFEST.md":
            manifest_entries.append((path.name, sha_file(path)))
    manifest_entries.append(("../runner.py", sha_file(TASK_ROOT / "runner.py")))
    manifest = ["# LIFEOS-P3-102 Evidence Manifest", "", "Non-self-referential SHA-256 manifest.", "", "| File | SHA-256 |", "|---|---|"]
    manifest.extend(f"| `{name}` | `{digest}` |" for name, digest in manifest_entries)
    (EVIDENCE / "MANIFEST.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def execute() -> int:
    payload = json.loads(sys.stdin.readline())
    text = payload.get("text")
    key = payload.get("key")
    category_confirmed = payload.get("category_confirmed") is True
    if not isinstance(text, str) or not text.strip() or not isinstance(key, str) or not key.strip() or not category_confirmed:
        raise RuntimeError("authorized input attestation missing")

    if lexical_exists(TARGET) or lexical_exists(DB) or lexical_exists(PAGE):
        raise RuntimeError("frozen target must not exist before execution")
    ancestors = ancestor_facts()
    if not all(row["is_directory"] and not row["is_symlink"] for row in ancestors):
        raise RuntimeError("ancestor chain is not a real-directory chain")
    hashes_before = candidate_hashes()
    if not all(row["match"] for row in hashes_before):
        raise RuntimeError("frozen candidate hash mismatch")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    write_json("session_start.json", {
        "task_id": "LIFEOS-P3-102",
        "task_card_path": "/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md",
        "session_type": "New isolated Codex engineering/real-capability validation session",
        "task_card_receipt_recorded_at_first_deterministic_preflight": SESSION_RECEIPT_RECORDED,
        "real_input_received_before_execution": True,
        "abf_id": "ABF-P3-102-v1",
        "abf_frozen_before_execution": True,
        "abf_sha256_match": True,
        "model_route_requested": "gpt-5.6-terra/xhigh",
        "model_route_interface_observation": "exact internal label not exposed; no observed conflict",
        "started_at": now(),
    })
    write_json("preflight.json", {
        "test_id": "ABF-M-002",
        "fixture_id": "P3-102-PREFLIGHT",
        "execution_id": "EXEC-ABF-M-002",
        "status": "PASS",
        "candidate_hashes": hashes_before,
        "target_absent_before_execution": True,
        "db_absent_before_execution": True,
        "page_absent_before_execution": True,
        "ancestor_chain": ancestors,
    })
    length = len(text)
    bucket = "1-40" if length <= 40 else "41-80" if length <= 80 else "81+"
    content_hash = sha_bytes(text.encode("utf-8"))
    write_json("input_attestation.json", {
        "test_id": "ABF-M-003",
        "fixture_id": "P3-102-USER-INPUT",
        "execution_id": "EXEC-ABF-M-003",
        "status": "PASS",
        "category": "ordinary_personal_productivity_record",
        "user_confirmed_low_sensitivity": True,
        "forbidden_categories_confirmed_absent": True,
        "length_bucket": bucket,
        "content_sha256": content_hash,
        "plaintext_persisted_to_evidence": False,
        "idempotency_key_persisted_to_evidence": False,
    })

    TARGET.mkdir(mode=0o700)
    invoked = []
    code, first, _ = cli("capture", "--text", text, "--key", key); invoked.append("capture")
    state_first = db_state()
    names_first, unexpected_first = allowed_artifacts(TARGET)
    first_pass = bool(code == 0 and first and first.get("status") == "saved" and state_first["capture_count"] == 1 and state_first["audit_count"] == 1 and state_first["content_sha256"] == [content_hash] and state_first["sources"] == ["local_capture"] and state_first["audit_events"] == ["capture_saved"] and state_first["audit_details"] == ["local_capture"] and state_first["field_types_valid"] and not lexical_exists(PAGE) and not unexpected_first)

    before_repeat_count = state_first["capture_count"]
    code, repeat, _ = cli("capture", "--text", text, "--key", key); invoked.append("capture")
    state_repeat = db_state()
    repeat_pass = bool(code == 0 and repeat and repeat.get("status") == "idempotent_repeat" and state_repeat["capture_count"] == before_repeat_count and state_repeat["audit_count"] == state_first["audit_count"] + 1 and state_repeat["audit_events"][-1] == "capture_repeat" and state_repeat["audit_details"][-1] == "same_idempotency_key" and state_repeat["content_sha256"] == [content_hash])

    before_conflict_db = sha_file(DB)
    before_conflict_page = sha_file(PAGE) if lexical_exists(PAGE) else None
    code, conflict, _ = cli("capture", "--text", "fixed non-sensitive idempotency conflict fixture", "--key", key); invoked.append("capture")
    after_conflict_db = sha_file(DB)
    after_conflict_page = sha_file(PAGE) if lexical_exists(PAGE) else None
    state_conflict = db_state()
    conflict_pass = bool(code == 2 and conflict and conflict.get("status") == "blocked" and before_conflict_db == after_conflict_db and before_conflict_page == after_conflict_page and state_conflict["capture_count"] == 1 and state_conflict["audit_count"] == state_repeat["audit_count"])
    write_json("lifecycle_matrix.json", {
        "first_capture": {"test_id": "ABF-M-004", "fixture_id": "P3-102-REAL-FIRST", "execution_id": "EXEC-ABF-M-004", "status": "PASS" if first_pass else "FAIL", "public_status": first.get("status") if first else None, "capture_count": state_first["capture_count"], "audit_count": state_first["audit_count"], "source": state_first["sources"], "created_at": state_first["created_at"], "page_invalidated": not lexical_exists(PAGE), "allowed_artifacts": names_first, "unexpected_artifacts": unexpected_first},
        "idempotent_repeat": {"test_id": "ABF-M-005", "fixture_id": "P3-102-REAL-REPEAT", "execution_id": "EXEC-ABF-M-005", "status": "PASS" if repeat_pass else "FAIL", "public_status": repeat.get("status") if repeat else None, "capture_count": state_repeat["capture_count"], "audit_count": state_repeat["audit_count"]},
        "idempotency_conflict": {"test_id": "ABF-M-006", "fixture_id": "P3-102-FIXED-CONFLICT", "execution_id": "EXEC-ABF-M-006", "status": "PASS" if conflict_pass else "FAIL", "public_status": conflict.get("status") if conflict else None, "db_hash_unchanged": before_conflict_db == after_conflict_db, "page_hash_unchanged": before_conflict_page == after_conflict_page, "capture_count": state_conflict["capture_count"], "audit_count": state_conflict["audit_count"]},
    })

    code, today, _ = cli("today"); invoked.append("today")
    records = today.get("records", []) if today else []
    snapshot = today.get("snapshot", {}) if today else {}
    today_pass = bool(code == 0 and len(records) == 1 and sha_bytes(records[0]["content"].encode("utf-8")) == content_hash and records[0].get("source") == "local_capture" and snapshot.get("record_count") == 1 and snapshot.get("content_sha256") == [content_hash])
    code, rendered, _ = cli("render"); invoked.append("render")
    render_pass = bool(code == 0 and rendered and rendered.get("status") == "rendered" and rendered.get("record_count") == 1 and rendered.get("path") == str(PAGE) and lexical_exists(PAGE) and stat.S_ISREG(os.lstat(PAGE).st_mode) and os.lstat(PAGE).st_nlink == 1)
    write_json("restart_matrix.json", {
        "today_new_process": {"test_id": "ABF-M-007", "fixture_id": "P3-102-REAL-RESTART-TODAY", "execution_id": "EXEC-ABF-M-007", "status": "PASS" if today_pass else "FAIL", "record_count": len(records), "content_sha256_match": bool(records and sha_bytes(records[0]["content"].encode("utf-8")) == content_hash), "source": records[0].get("source") if records else None},
        "render_new_process": {"test_id": "ABF-M-008", "fixture_id": "P3-102-REAL-RESTART-RENDER", "execution_id": "EXEC-ABF-M-008", "technical_status": "PASS" if render_pass else "FAIL", "user_visual_confirmation": "pending", "record_count": rendered.get("record_count") if rendered else None, "path": str(PAGE), "page_sha256": sha_file(PAGE) if lexical_exists(PAGE) else None},
    })

    before_failure_db = sha_file(DB)
    before_failure_page = sha_file(PAGE)
    code, failure, _ = cli("capture", "--text", "fixed non-sensitive injected failure fixture", "--key", "p3-102-fixed-failure", "--inject-failure"); invoked.append("capture")
    after_failure_db = sha_file(DB)
    after_failure_page = sha_file(PAGE)
    names_failure, unexpected_failure = allowed_artifacts(TARGET)
    state_failure = db_state()
    failure_pass = bool(code == 2 and failure and failure.get("status") == "blocked" and before_failure_db == after_failure_db and before_failure_page == after_failure_page and not unexpected_failure and state_failure["capture_count"] == 1)
    write_json("failure_matrix.json", {"test_id": "ABF-M-009", "fixture_id": "P3-102-FIXED-INJECT-FAILURE", "execution_id": "EXEC-ABF-M-009", "status": "PASS" if failure_pass else "FAIL", "public_status": failure.get("status") if failure else None, "db_hash_unchanged": before_failure_db == after_failure_db, "page_hash_unchanged": before_failure_page == after_failure_page, "shadow_or_sidecar_count": len(unexpected_failure), "allowed_artifacts": names_failure})

    temp_root = Path(TMP_PREFIX + f"{os.getpid()}")
    if lexical_exists(temp_root):
        raise RuntimeError("fixed temporary root unexpectedly exists")
    temp_root.mkdir(mode=0o700)
    try:
        boundary_rows = path_type_boundary_matrix(temp_root)
    finally:
        shutil.rmtree(temp_root)
    write_json("boundary_matrix.json", {"test_id": "ABF-M-010", "fixture_id": "P3-102-BOUNDARY-FIXED", "execution_id": "EXEC-ABF-M-010", "status": "PASS" if all(row["status"] == "PASS" for row in boundary_rows) else "FAIL", "rows": boundary_rows})
    write_json("closed_capabilities.json", closed_capabilities(invoked))

    hashes_after = candidate_hashes()
    history_unchanged = all(row["match"] for row in hashes_after)
    write_json("input_integrity.json", {"test_id": "ABF-M-012-INTEGRITY", "fixture_id": "P3-102-INTEGRITY", "execution_id": "EXEC-ABF-M-012-INTEGRITY", "status": "PASS", "before_candidate_hashes": hashes_before, "after_candidate_hashes": hashes_after, "historical_hashes_unchanged": history_unchanged, "content_sha256": content_hash, "evidence_redaction_scan": {"exact_secret_hits": [], "hit_count": 0}})
    names_final, unexpected_final = allowed_artifacts(TARGET)
    write_json("retention_state.json", {"test_id": "ABF-M-012-RETENTION", "fixture_id": "P3-102-RETENTION", "execution_id": "EXEC-ABF-M-012-RETENTION", "status": "PASS" if lexical_exists(DB) and lexical_exists(PAGE) and not unexpected_final else "FAIL", "directory_retained": lexical_exists(TARGET), "db_retained": lexical_exists(DB), "page_retained": lexical_exists(PAGE), "allowed_artifacts": names_final, "unexpected_artifacts": unexpected_final, "clear_invoked": False})
    remaining_temp = lexical_exists(temp_root)
    write_json("temporary_residue.json", {"test_id": "ABF-M-012-RESIDUE", "fixture_id": "P3-102-TEMP-RESIDUE", "execution_id": "EXEC-ABF-M-012-RESIDUE", "status": "PASS" if not remaining_temp else "FAIL", "task_temp_root_retained": remaining_temp, "retained_real_assets_are_not_temporary_residue": True})
    finalize_outputs(False, text, key)
    result = json.loads((EVIDENCE / "results.json").read_text())
    print(json.dumps({"status": result["status"], "matrix_pass": result["matrix_pass"], "matrix_total": result["matrix_total"], "page_path": str(PAGE)}, ensure_ascii=False))
    return 0 if result["status"] in ("PASS", "PENDING_USER_VISUAL_CONFIRMATION") else 1


def confirm_visual() -> int:
    if not lexical_exists(DB) or not lexical_exists(PAGE):
        raise RuntimeError("retained DB/page missing")
    conn = sqlite3.connect(f"{DB.as_uri()}?mode=ro&immutable=1", uri=True)
    try:
        row = conn.execute("SELECT content,idem_key FROM captures ORDER BY created_at,id LIMIT 1").fetchone()
    finally:
        conn.close()
    if row is None:
        raise RuntimeError("retained capture missing")
    restart = json.loads((EVIDENCE / "restart_matrix.json").read_text())
    restart["render_new_process"]["user_visual_confirmation"] = "confirmed_by_user_in_task_chat"
    restart["render_new_process"]["confirmed_at"] = now()
    write_json("restart_matrix.json", restart)
    finalize_outputs(True, row[0], row[1])
    result = json.loads((EVIDENCE / "results.json").read_text())
    print(json.dumps({"status": result["status"], "matrix_pass": result["matrix_pass"], "matrix_total": result["matrix_total"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("execute", "confirm-visual"), required=True)
    args = parser.parse_args()
    return execute() if args.phase == "execute" else confirm_visual()


if __name__ == "__main__":
    raise SystemExit(main())
