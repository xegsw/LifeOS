#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mvp import CONTROLLED_PROJECT_ID, LocalMvp, VisibleSaveError, write_json


def main() -> int:
    cases = []
    with tempfile.TemporaryDirectory(dir=ROOT / "runtime") as work:
        db = Path(work) / "synthetic.sqlite"
        app = LocalMvp(db)
        try:
            receipt = app.capture(original_text="合成原文", idempotency_key="k1", now_ms=1)
            assert receipt.saved and receipt.message == "已保存" and not receipt.duplicate
            visible = app.view_record(receipt.record_id)
            assert visible == {"record_id": receipt.record_id, "original_text": "合成原文", "source_identity": "user_local_entry", "content_identity": "user_original", "ai_features": "disabled"}
            cases.append("commit_then_saved_and_identity_visible")
            duplicate = app.capture(original_text="合成原文", idempotency_key="k1", now_ms=2)
            assert duplicate.saved and duplicate.duplicate and duplicate.record_id == receipt.record_id
            cases.append("duplicate_submit_is_idempotent")
            try:
                app.capture(original_text="另一条合成原文", idempotency_key="k1", now_ms=3)
                raise AssertionError("idempotency conflict accepted")
            except VisibleSaveError as exc:
                assert "保存失败" in str(exc)
            cases.append("idempotency_conflict_is_visible")
            try:
                app.capture(original_text="不应持久化", idempotency_key="fail-k", now_ms=4, fail_before_commit=True)
                raise AssertionError("injected failure reported success")
            except VisibleSaveError as exc:
                assert "保存失败" in str(exc)
            assert app.conn.execute("SELECT count(*) FROM records WHERE idempotency_key='fail-k'").fetchone()[0] == 0
            cases.append("write_failure_never_reports_saved_or_persists")
        finally:
            app.close()
        reopened = LocalMvp(db)
        try:
            assert reopened.view_record(receipt.record_id)["original_text"] == "合成原文"
            assert reopened.restore_project(CONTROLLED_PROJECT_ID)["restore_identity"] == "controlled_local_project"
            try:
                reopened.restore_project("other-project")
                raise AssertionError("uncontrolled project restored")
            except PermissionError:
                pass
            confirmation = reopened.confirm_next_step(project_id=CONTROLLED_PROJECT_ID, next_step_text="人工确认的下一步", now_ms=5)
            assert confirmation["confirmation_identity"] == "user_confirmed" and confirmation["external_action"] == "none"
            cases.extend(["restart_preserves_committed_record", "controlled_restore_and_explicit_confirmation", "no_external_action_or_ai_enabled"])
        finally:
            reopened.close()
    runtime = ROOT / "runtime"
    def cli(*arguments):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "run_demo.py"), *arguments],
                              capture_output=True, text=True, check=False)
    for name in ("e2e-normal", "e2e-conflict", "e2e-failure"):
        for suffix in (".sqlite", "_snapshot.json"):
            (runtime / (name + suffix)).unlink(missing_ok=True)
    normal = cli("--synthetic-only", "--text", "操作者输入的合成原文", "--idempotency-key", "e2e-normal-key",
                 "--next-step", "操作者显式确认的下一步", "--run-id", "e2e-normal")
    assert normal.returncode == 0 and "PASS demo" in normal.stdout
    normal_snapshot = json.loads((runtime / "e2e-normal_snapshot.json").read_text(encoding="utf-8"))
    assert normal_snapshot["record"]["original_text"] == "操作者输入的合成原文"
    assert normal_snapshot["confirmation"]["confirmation_identity"] == "user_confirmed"
    assert normal_snapshot["confirmation"]["external_action"] == "none"
    cases.append("e2e_operator_input_and_explicit_confirmation")
    empty = cli("--synthetic-only", "--text", "", "--idempotency-key", "empty-key", "--next-step", "确认", "--run-id", "e2e-failure")
    assert empty.returncode == 1 and "已保存" not in (empty.stdout + empty.stderr) and "保存失败" in empty.stderr
    cases.append("e2e_empty_input_is_visible_and_never_saved")
    first = cli("--synthetic-only", "--text", "第一条合成文本", "--idempotency-key", "conflict-key", "--next-step", "确认", "--run-id", "e2e-conflict")
    conflict = cli("--synthetic-only", "--text", "不同合成文本", "--idempotency-key", "conflict-key", "--next-step", "确认", "--run-id", "e2e-conflict")
    assert first.returncode == 0 and conflict.returncode == 1 and "保存失败" in conflict.stderr and "已保存" not in (conflict.stdout + conflict.stderr)
    cases.append("e2e_idempotency_conflict_is_visible_and_never_saved")
    failure = cli("--synthetic-only", "--text", "提交前失败的合成文本", "--idempotency-key", "failure-key", "--next-step", "确认", "--run-id", "e2e-failure", "--inject-write-failure")
    assert failure.returncode == 1 and "保存失败" in failure.stderr and "已保存" not in (failure.stdout + failure.stderr)
    failed_snapshot = json.loads((runtime / "e2e-failure_snapshot.json").read_text(encoding="utf-8"))
    assert failed_snapshot["receipt"]["saved"] is False
    cases.append("e2e_precommit_failure_is_visible_and_never_saved")
    result = {"task": "LIFEOS-P3-063", "pass": len(cases), "fail": 0, "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0, "cases": cases, "scope": "synthetic SQLite only; no network/Tauri/IPC/Vault/real paths"}
    write_json(ROOT / "evidence" / "test_results.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
