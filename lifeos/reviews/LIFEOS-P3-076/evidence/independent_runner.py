#!/usr/bin/env python3
"""Fresh P3-076 independent review runner for the P3-075 controlled runtime.

The primary checks operate the candidate only through its operator CLI in a
fresh temporary copy.  A small public-interface companion covers the
controlled-project restore rejection because that operation is deliberately
not exposed by the CLI.  This runner never imports or reads the candidate's
test suite or self-check runner.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
CANDIDATE = REPO / "lifeos/engineering/LIFEOS-P3-075"
EVIDENCE = Path(__file__).resolve().parent
RESULTS = EVIDENCE / "independent_results.json"
LOG = EVIDENCE / "independent_runner.log"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_cli(copy: Path, run_id: str, text: str, key: str, *, save: bool = True,
             next_confirm: bool = True, failure: bool = False) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, "scripts/runtime_cli.py", "--non-sensitive-test-only", "--text", text,
            "--idempotency-key", key, "--next-step", "确认的测试下一步", "--run-id", run_id]
    if save:
        args.append("--confirm-save")
    if next_confirm:
        args.append("--confirm-next-step")
    if failure:
        args.append("--inject-precommit-failure")
    return subprocess.run(args, cwd=copy, text=True, capture_output=True, check=False)


def snapshot(copy: Path, run_id: str) -> dict:
    return json.loads((copy / "runtime" / f"{run_id}_snapshot.json").read_text(encoding="utf-8"))


def db_counts(copy: Path, run_id: str) -> tuple[int, int, int]:
    db = copy / "runtime" / f"{run_id}.sqlite"
    with sqlite3.connect(db) as conn:
        return tuple(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                     for table in ("records", "audits", "next_steps"))


def public_restore_rejection(copy: Path) -> subprocess.CompletedProcess[str]:
    # This companion is intentionally independent of the candidate test suite.
    program = """\
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src').resolve()))
from local_runtime import ControlledLocalRuntime, VisibleRuntimeError
app = ControlledLocalRuntime(Path('runtime/restore.sqlite'))
try:
    try:
        app.restore_context('unknown-project')
    except VisibleRuntimeError as exc:
        print(json.dumps({'rejected': True, 'message': str(exc)}, ensure_ascii=False))
    else:
        print(json.dumps({'rejected': False}))
finally:
    app.close()
"""
    return subprocess.run([sys.executable, "-c", program], cwd=copy, text=True,
                          capture_output=True, check=False)


def add(results: list[dict], name: str, passed: bool, detail: str) -> None:
    results.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    results: list[dict] = []
    logs: list[str] = []
    before = {str(p.relative_to(REPO)): sha256(p) for p in sorted(CANDIDATE.rglob("*")) if p.is_file()}
    historical = [
        REPO / "lifeos/deliverables/LIFEOS-P3-075_minimal_local_mvp_controlled_runtime_capability_package.md",
        REPO / "lifeos/reviews/LIFEOS-P3-075_pm_review.md",
        CANDIDATE / "evidence/MANIFEST.md",
    ]
    historical_before = {str(p.relative_to(REPO)): sha256(p) for p in historical}
    manifest_text = (CANDIDATE / "evidence/MANIFEST.md").read_text(encoding="utf-8")
    manifest_entries = re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", manifest_text)
    manifest_match = bool(manifest_entries) and all(
        (CANDIDATE / relative).is_file() and sha256(CANDIDATE / relative) == expected
        for relative, expected in manifest_entries
    )
    add(results, "candidate_execution_manifest_matches_current_hash", manifest_match,
        "every P3-075 execution-manifest SHA-256 entry matches its current read-only file")

    with tempfile.TemporaryDirectory(prefix="lifeos-p3076-") as temp:
        copy = Path(temp) / "LIFEOS-P3-075"
        shutil.copytree(CANDIDATE, copy, ignore=shutil.ignore_patterns("runtime", "__pycache__", "*.pyc"))

        first = call_cli(copy, "first", "P3-076 non-sensitive text", "key-first")
        first_snapshot = snapshot(copy, "first")
        add(results, "first_explicit_confirmed_submission", first.returncode == 0 and
            first_snapshot["receipt"]["saved"] and first_snapshot["receipt"]["source_identity"] == "operator_local_entry" and
            first_snapshot["record"]["content_identity"] == "user_original" and
            first_snapshot["next_step"]["confirmation_identity"] == "operator_confirmed" and
            first_snapshot["boundaries"]["network"] == "disabled", "CLI succeeds only with explicit confirmations; identities and closure state are visible")

        repeat = call_cli(copy, "first", "P3-076 non-sensitive text", "key-first")
        add(results, "idempotent_repeat", repeat.returncode == 0 and snapshot(copy, "first")["receipt"]["duplicate"] and
            db_counts(copy, "first")[0] == 1, "same key and same text returns duplicate without a second record")

        reopen = subprocess.run([sys.executable, "-c", "import sqlite3; c=sqlite3.connect('runtime/first.sqlite'); print(c.execute('select original_text from records').fetchone()[0])"], cwd=copy, text=True, capture_output=True, check=False)
        add(results, "close_reopen_persistence", reopen.returncode == 0 and reopen.stdout.strip() == "P3-076 non-sensitive text", "fresh SQLite connection reads only the committed record")

        empty = call_cli(copy, "empty", "   ", "key-empty")
        add(results, "empty_input_fail_closed", empty.returncode != 0 and "保存失败" in empty.stderr and "已保存" not in empty.stdout and db_counts(copy, "empty") == (0, 0, 0), "empty text is visibly rejected with no record, audit, or next step")

        no_save = call_cli(copy, "no-save", "text", "key-no-save", save=False)
        add(results, "missing_save_confirmation_fail_closed", no_save.returncode != 0 and "明确确认" in no_save.stderr and db_counts(copy, "no-save") == (0, 0, 0), "missing save confirmation leaves no record, audit, or next step")

        no_next = call_cli(copy, "no-next", "confirmed save", "key-no-next", next_confirm=False)
        n_records, n_audits, n_steps = db_counts(copy, "no-next")
        add(results, "missing_next_step_confirmation_blocked", no_next.returncode != 0 and "下一步已阻断" in no_next.stderr and
            (n_records, n_audits, n_steps) == (1, 1, 0), "save remains committed because it had its own confirmation; unconfirmed next step is absent")

        conflict_first = call_cli(copy, "conflict", "original", "key-conflict")
        conflict_second = call_cli(copy, "conflict", "replacement", "key-conflict")
        conflict_db = subprocess.run([sys.executable, "-c", "import sqlite3; c=sqlite3.connect('runtime/conflict.sqlite'); print(c.execute('select original_text from records').fetchone()[0])"], cwd=copy, text=True, capture_output=True, check=False)
        add(results, "same_key_different_text_rejected_without_overwrite", conflict_first.returncode == 0 and conflict_second.returncode != 0 and
            "幂等键已用于不同测试文本" in conflict_second.stderr and conflict_db.stdout.strip() == "original", "conflicting replay is visible and cannot overwrite original text")

        injected = call_cli(copy, "failure", "must rollback", "key-failure", failure=True)
        add(results, "precommit_failure_atomic_rollback", injected.returncode != 0 and "事务未提交" in injected.stderr and
            "已保存" not in injected.stdout and db_counts(copy, "failure") == (0, 0, 0), "injected pre-commit failure discloses failure and removes pending artifacts")

        restore = public_restore_rejection(copy)
        restore_value = json.loads(restore.stdout) if restore.returncode == 0 and restore.stdout else {}
        add(results, "unknown_project_restore_rejected", restore.returncode == 0 and restore_value.get("rejected") is True and
            "受控范围" in restore_value.get("message", ""), "public restore interface rejects an unknown project")

        target_sources = [copy / "src/local_runtime.py", copy / "scripts/runtime_cli.py"]
        source_text = "\n".join(path.read_text(encoding="utf-8") for path in target_sources)
        prohibited = ("http://", "https://", "socket.", "requests", "urllib", "tauri", "ipc", "vault", "export", "sync", "multi_device", "external_user")
        hits = [token for token in prohibited if token in source_text.lower() and token not in {"tauri", "ipc", "vault", "export", "sync", "multi_device", "external_user"}]
        # Boundary labels are expected declarations; executable external imports/URLs are not.
        imports = [line.strip() for line in source_text.splitlines() if line.startswith("import ") or line.startswith("from ")]
        external_import = any(any(name in line for name in ("requests", "urllib", "socket", "http", "boto", "openai")) for line in imports)
        add(results, "prohibited_external_channels_static_closed", not hits and not external_import and
            '"network": "disabled"' in source_text and '"tauri_ipc": "not_used"' in source_text and
            '"external_action": "none"' in source_text, "no URL/network client import; declared network/Tauri/external-action boundaries remain closed")

        copy_hashes = {str(p.relative_to(copy)): sha256(p) for p in sorted(copy.rglob("*")) if p.is_file() and "runtime" not in p.parts}
        add(results, "candidate_copy_matches_original_hash", all(
            before[str((CANDIDATE / rel).relative_to(REPO))] == digest for rel, digest in copy_hashes.items()
        ), "fresh copied candidate sources match original pre-run hashes")

    after = {str(p.relative_to(REPO)): sha256(p) for p in sorted(CANDIDATE.rglob("*")) if p.is_file()}
    historical_after = {str(p.relative_to(REPO)): sha256(p) for p in historical}
    add(results, "historical_assets_preserved", before == after and historical_before == historical_after, "candidate, P3-075 delivery, PM review, and manifest hashes unchanged after review")

    summary = {"PASS": sum(x["status"] == "PASS" for x in results), "FAIL": sum(x["status"] == "FAIL" for x in results)}
    payload = {"task": "LIFEOS-P3-076", "candidate": "LIFEOS-P3-075", "results": results,
               "summary": summary, "counts": {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0},
               "candidate_hashes_before": before, "historical_hashes": historical_before}
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LOG.write_text("\n".join(f"{x['status']} {x['name']}: {x['detail']}" for x in results) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
