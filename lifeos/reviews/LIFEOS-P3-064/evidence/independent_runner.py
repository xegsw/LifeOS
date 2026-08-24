#!/usr/bin/env python3
"""Independent synthetic-only black-box review runner for LIFEOS-P3-064.

This deliberately does not import or call P3-063's test suite.  It invokes the
candidate CLI in an isolated copy and uses sqlite3 only to inspect outcomes.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import ast
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: independent_runner.py CANDIDATE_DIR RESULT_JSON")
    root = Path(sys.argv[1]).resolve()
    result_path = Path(sys.argv[2]).resolve()
    cli = root / "scripts" / "run_demo.py"
    runtime = root / "runtime"
    cases: list[str] = []

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(cli), *args], cwd=root, text=True,
                              capture_output=True, check=False)

    def no_saved(proc: subprocess.CompletedProcess[str]) -> None:
        assert "已保存" not in (proc.stdout + proc.stderr), (proc.stdout, proc.stderr)

    # A unique normal path verifies operator-provided text, explicit confirmation
    # and the boundary flags without relying on the candidate fixture inputs.
    normal = run("--synthetic-only", "--text", "独立复评合成原文 A", "--idempotency-key",
                 "independent-key-a", "--next-step", "独立复评明确确认 A", "--run-id", "independent-a")
    assert normal.returncode == 0, (normal.stdout, normal.stderr)
    snapshot = json.loads((runtime / "independent-a_snapshot.json").read_text(encoding="utf-8"))
    assert snapshot["record"] == {
        "record_id": snapshot["receipt"]["record_id"], "original_text": "独立复评合成原文 A",
        "source_identity": "user_local_entry", "content_identity": "user_original",
        "ai_features": "disabled",
    }
    assert snapshot["confirmation"]["confirmation_identity"] == "user_confirmed"
    assert snapshot["confirmation"]["external_action"] == "none"
    assert snapshot["runtime_boundary"] == {
        "synthetic_only": True, "ai_features": "disabled", "network": "disabled", "tauri_ipc": "not_used"
    }
    cases.append("operator_input_identity_confirmation_and_boundary")

    # Re-use same key/text: must not add another row, then verify persistent read.
    duplicate = run("--synthetic-only", "--text", "独立复评合成原文 A", "--idempotency-key",
                    "independent-key-a", "--next-step", "独立复评明确确认 A", "--run-id", "independent-a")
    assert duplicate.returncode == 0, (duplicate.stdout, duplicate.stderr)
    duplicate_snapshot = json.loads((runtime / "independent-a_snapshot.json").read_text(encoding="utf-8"))
    assert duplicate_snapshot["receipt"]["duplicate"] is True
    db = sqlite3.connect(runtime / "independent-a.sqlite")
    try:
        assert db.execute("SELECT count(*) FROM records WHERE idempotency_key='independent-key-a'").fetchone()[0] == 1
        assert db.execute("SELECT original_text FROM records WHERE idempotency_key='independent-key-a'").fetchone()[0] == "独立复评合成原文 A"
    finally:
        db.close()
    cases.append("same_key_same_text_is_idempotent_and_restart_readable")

    conflict = run("--synthetic-only", "--text", "独立复评不同文本 B", "--idempotency-key",
                   "independent-key-a", "--next-step", "独立复评明确确认 B", "--run-id", "independent-a")
    assert conflict.returncode != 0 and "保存失败" in conflict.stderr
    no_saved(conflict)
    db = sqlite3.connect(runtime / "independent-a.sqlite")
    try:
        assert db.execute("SELECT count(*) FROM records WHERE idempotency_key='independent-key-a'").fetchone()[0] == 1
    finally:
        db.close()
    cases.append("same_key_different_text_fails_without_overwrite")

    empty = run("--synthetic-only", "--text", "", "--idempotency-key", "independent-empty",
                "--next-step", "确认", "--run-id", "independent-empty")
    assert empty.returncode != 0 and "保存失败" in empty.stderr
    no_saved(empty)
    db = sqlite3.connect(runtime / "independent-empty.sqlite")
    try:
        assert db.execute("SELECT count(*) FROM records WHERE idempotency_key='independent-empty'").fetchone()[0] == 0
    finally:
        db.close()
    cases.append("empty_input_fails_without_record_or_success_receipt")

    missing_ack = run("--text", "合成文本", "--idempotency-key", "independent-no-ack",
                      "--next-step", "确认", "--run-id", "independent-no-ack")
    assert missing_ack.returncode != 0 and "--synthetic-only is required" in missing_ack.stderr
    no_saved(missing_ack)
    assert not (runtime / "independent-no-ack.sqlite").exists()
    cases.append("missing_synthetic_ack_fails_before_runtime_write")

    invalid_run_id = run("--synthetic-only", "--text", "合成文本", "--idempotency-key", "independent-invalid",
                         "--next-step", "确认", "--run-id", "../outside")
    assert invalid_run_id.returncode != 0 and "--run-id must contain" in invalid_run_id.stderr
    no_saved(invalid_run_id)
    assert not (root.parent / "outside.sqlite").exists()
    cases.append("invalid_run_id_rejected_without_path_escape")

    injected = run("--synthetic-only", "--text", "独立复评提交前失败", "--idempotency-key", "independent-failure",
                   "--next-step", "确认", "--run-id", "independent-failure", "--inject-write-failure")
    assert injected.returncode != 0 and "保存失败" in injected.stderr
    no_saved(injected)
    failed_snapshot = json.loads((runtime / "independent-failure_snapshot.json").read_text(encoding="utf-8"))
    assert failed_snapshot["receipt"]["saved"] is False
    db = sqlite3.connect(runtime / "independent-failure.sqlite")
    try:
        assert db.execute("SELECT count(*) FROM records WHERE idempotency_key='independent-failure'").fetchone()[0] == 0
    finally:
        db.close()
    cases.append("precommit_failure_is_visible_and_rolls_back")

    unknown_project_check = subprocess.run(
        [sys.executable, "-c", (
            "import sys; from pathlib import Path; "
            "sys.path.insert(0, str(Path(sys.argv[1]) / 'src')); "
            "from mvp import LocalMvp; "
            "app=LocalMvp(Path(sys.argv[1]) / 'runtime' / 'independent-project.sqlite'); "
            "\ntry:\n app.restore_project('unknown-project')\nexcept PermissionError:\n app.close(); raise SystemExit(0)\n"
            "else:\n app.close(); raise SystemExit(1)"
        ), str(root)], text=True, capture_output=True, check=False)
    assert unknown_project_check.returncode == 0, (unknown_project_check.stdout, unknown_project_check.stderr)
    cases.append("unknown_project_is_rejected")

    # Static boundary audit is supplementary, not a claim about real capabilities.
    source = "\n".join(p.read_text(encoding="utf-8") for p in root.rglob("*.py"))
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden_import_prefixes = ("requests", "urllib", "http", "socket", "ftplib", "paramiko")
    hits = [name for name in imported if name.startswith(forbidden_import_prefixes)]
    hits.extend(token for token in ("http://", "https://") if token in source)
    assert not hits, hits
    cases.append("static_source_has_no_network_or_external_capability_tokens")

    payload = {
        "task": "LIFEOS-P3-064", "candidate": str(root), "pass": len(cases), "fail": 0,
        "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0, "cases": cases,
        "candidate_hashes": {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob("*.py"))},
        "scope": "independent synthetic CLI assertions in an isolated temporary copy only",
    }
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
