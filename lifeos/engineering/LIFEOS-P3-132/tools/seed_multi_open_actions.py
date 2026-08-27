#!/usr/bin/env python3
"""Create the one fixed, task-local CL-02 multi-open-Action fixture.

This is an Evidence fixture, not a product or IPC surface.  It writes one fresh
SQLite database only under the P3-132 task root and deliberately inserts the
rows in reverse deterministic order so the actual Tauri run can prove that
Today chooses by confirmed_at_ms, then action_id.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


TASK_TEMP_ROOT = Path("/private/tmp/lifeos-p3-132-global-ai-today-lite-v1")
DB_NAME = "capture.sqlite"
PERSON_ID = "person:synthetic-owner"
PROJECT_ID = "synthetic-lifeos-product"
CONTEXT_ID = "ctx:project:synthetic-lifeos-product"
SOURCE_ID = "SRC-SYN-WORK-001"
ARTIFACT_VERSION = "ART-SYN-CONTEXT-RECOVERY-001@v1"
SUFFICIENT_TEXT = "整理 LifeOS Context Recovery 合成验收记录。"
CAPTURE_ID = "capture:p3-131:fixture-multi-open"
DERIVATION_ID = "derivation:p3-131:fixture-multi-open"

SCHEMA = """
PRAGMA journal_mode = DELETE;
PRAGMA foreign_keys = ON;
CREATE TABLE captures (id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at_ms INTEGER NOT NULL, source TEXT NOT NULL CHECK(source='local_capture'), source_id TEXT NOT NULL, artifact_version TEXT NOT NULL, idem_key TEXT NOT NULL UNIQUE);
CREATE TABLE projects (id TEXT PRIMARY KEY, person_id TEXT NOT NULL, title TEXT NOT NULL, source_id TEXT NOT NULL, artifact_version TEXT NOT NULL, source_available INTEGER NOT NULL, generation_current INTEGER NOT NULL, tombstoned INTEGER NOT NULL, authorized INTEGER NOT NULL, evidence_ready INTEGER NOT NULL);
CREATE TABLE capture_project_links (capture_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, context_id TEXT NOT NULL, link_status TEXT NOT NULL CHECK(link_status IN ('candidate','confirmed','rejected')), source_id TEXT NOT NULL, artifact_version TEXT NOT NULL, FOREIGN KEY(capture_id) REFERENCES captures(id), FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE derivations (id TEXT PRIMARY KEY, context_id TEXT NOT NULL, capture_id TEXT NOT NULL, processor TEXT NOT NULL, processor_version TEXT NOT NULL, basis_refs TEXT NOT NULL, why_text TEXT NOT NULL, created_at_ms INTEGER NOT NULL, FOREIGN KEY(capture_id) REFERENCES captures(id));
CREATE TABLE candidate_actions (id TEXT PRIMARY KEY, context_id TEXT NOT NULL, capture_id TEXT NOT NULL, derivation_id TEXT NOT NULL, candidate_text TEXT NOT NULL, candidate_state TEXT NOT NULL CHECK(candidate_state IN ('active','accepted','rejected','deferred')), created_at_ms INTEGER NOT NULL, FOREIGN KEY(derivation_id) REFERENCES derivations(id));
CREATE TABLE feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, target_kind TEXT NOT NULL CHECK(target_kind IN ('capture_context','candidate_action','understanding')), target_id TEXT NOT NULL, context_id TEXT NOT NULL, decision TEXT NOT NULL, idem_key TEXT NOT NULL UNIQUE, detail TEXT NOT NULL, created_at_ms INTEGER NOT NULL);
CREATE TABLE actions (id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL UNIQUE, context_id TEXT NOT NULL, action_text TEXT NOT NULL, confirmation_kind TEXT NOT NULL CHECK(confirmation_kind IN ('accept','edit_accept')), action_state TEXT NOT NULL CHECK(action_state IN ('open','completed')), created_at_ms INTEGER NOT NULL, confirmed_at_ms INTEGER GENERATED ALWAYS AS (created_at_ms) STORED, FOREIGN KEY(candidate_id) REFERENCES candidate_actions(id));
CREATE TABLE action_results (id TEXT PRIMARY KEY, action_id TEXT NOT NULL UNIQUE, result_kind TEXT NOT NULL CHECK(result_kind='completed'), result_text TEXT NOT NULL, idem_key TEXT NOT NULL UNIQUE, created_at_ms INTEGER NOT NULL, FOREIGN KEY(action_id) REFERENCES actions(id));
CREATE TABLE audit (id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, target_id TEXT NOT NULL, created_at_ms INTEGER NOT NULL, detail TEXT NOT NULL);
CREATE TABLE understandings (id TEXT PRIMARY KEY, context_id TEXT NOT NULL, capture_id TEXT NOT NULL, request_id TEXT NOT NULL UNIQUE, page TEXT NOT NULL, selection_ref TEXT, removed_context_kinds TEXT NOT NULL, derivation_id TEXT NOT NULL UNIQUE, processor TEXT NOT NULL, processor_version TEXT NOT NULL, observation_text TEXT NOT NULL, suggestion_text TEXT NOT NULL, basis_refs TEXT NOT NULL, why_text TEXT NOT NULL, evidence_state TEXT NOT NULL CHECK(evidence_state='sufficient'), created_at_ms INTEGER NOT NULL, FOREIGN KEY(capture_id) REFERENCES captures(id));
PRAGMA user_version = 132;
"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runtime_root = args.runtime_root.resolve(strict=True)
    task_root = TASK_TEMP_ROOT.resolve(strict=True)
    if runtime_root.parent != task_root or not runtime_root.is_dir():
        raise SystemExit("runtime root must be one direct, real child of the P3-132 task temp root")
    database = runtime_root / DB_NAME
    if database.exists() or database.is_symlink():
        raise SystemExit("fixture database target must be absent and non-link")

    connection = sqlite3.connect(database)
    try:
        connection.executescript(SCHEMA)
        connection.execute(
            "INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?)",
            (PROJECT_ID, PERSON_ID, "LifeOS 产品开发", SOURCE_ID, ARTIFACT_VERSION, 1, 1, 0, 1, 1),
        )
        connection.execute(
            "INSERT INTO captures VALUES(?,?,?,?,?,?,?)",
            (CAPTURE_ID, SUFFICIENT_TEXT, 6000, "local_capture", SOURCE_ID, ARTIFACT_VERSION, "p3-131-fixture-multi-open"),
        )
        connection.execute(
            "INSERT INTO capture_project_links VALUES(?,?,?,?,?,?)",
            (CAPTURE_ID, PROJECT_ID, CONTEXT_ID, "confirmed", SOURCE_ID, ARTIFACT_VERSION),
        )
        connection.execute(
            "INSERT INTO derivations VALUES(?,?,?,?,?,?,?,?)",
            (DERIVATION_ID, CONTEXT_ID, CAPTURE_ID, "local_rule:p3-131-v1", "v1", f"capture:{CAPTURE_ID}", "fixed fixture provenance", 6001),
        )
        candidates = (
            ("candidate:p3-131:fixture-newer", "action:p3-131:fixture-newer", 7002),
            ("candidate:p3-131:fixture-tie-z", "action:p3-131:fixture-tie-z", 7000),
            ("candidate:p3-131:fixture-tie-a", "action:p3-131:fixture-tie-a", 7000),
        )
        for candidate_id, action_id, confirmed_at in candidates:
            connection.execute(
                "INSERT INTO candidate_actions VALUES(?,?,?,?,?,?,?)",
                (candidate_id, CONTEXT_ID, CAPTURE_ID, DERIVATION_ID, SUFFICIENT_TEXT, "accepted", confirmed_at),
            )
            connection.execute(
                "INSERT INTO feedback(target_kind,target_id,context_id,decision,idem_key,detail,created_at_ms) VALUES('candidate_action',?,?,?,?,?,?)",
                (candidate_id, CONTEXT_ID, "accept", f"p3-131-fixture-feedback-{action_id}", action_id, confirmed_at),
            )
            connection.execute(
                "INSERT INTO actions(id,candidate_id,context_id,action_text,confirmation_kind,action_state,created_at_ms) VALUES(?,?,?,?,?,'open',?)",
                (action_id, candidate_id, CONTEXT_ID, SUFFICIENT_TEXT, "accept", confirmed_at),
            )
            connection.execute(
                "INSERT INTO audit(event,target_id,created_at_ms,detail) VALUES('action_created',?,?,?)",
                (action_id, confirmed_at, "fixture_explicit_confirmed_action"),
            )
        connection.execute("INSERT INTO audit(event,target_id,created_at_ms,detail) VALUES('capture_saved',?,?,?)", (CAPTURE_ID, 6000, "fixture_capture"))
        connection.execute("INSERT INTO audit(event,target_id,created_at_ms,detail) VALUES('context_confirmed',?,?,?)", (CAPTURE_ID, 6001, CONTEXT_ID))
        quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
        connection.commit()
    finally:
        connection.close()

    expected_order = ["action:p3-131:fixture-tie-a", "action:p3-131:fixture-tie-z", "action:p3-131:fixture-newer"]
    descriptor = {
        "contract": "LIFEOS-P3-132",
        "fixture_kind": "task_local_multi_open_confirmed_actions",
        "runtime_root": str(runtime_root),
        "database_sha256": digest(database),
        "quick_check": quick_check,
        "insert_order": [item[1] for item in candidates],
        "ordering_rule": "confirmed_at_ms ASC, action_id ASC",
        "expected_open_order": expected_order,
        "expected_todays_focus": expected_order[0],
        "tie_break": "fixture-tie-a and fixture-tie-z have the same confirmed_at_ms=7000; fixture-tie-a wins by action_id",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
