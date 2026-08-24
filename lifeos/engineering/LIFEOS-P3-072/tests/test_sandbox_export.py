import ast
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sandbox_export import BOUNDARIES, ControlledSandboxExport, ExportPlan  # noqa: E402


def engine_and_plan():
    engine = ControlledSandboxExport()
    engine.register("synthetic-note-072", "synthetic://lifeos/p3-072", "Synthetic export body", version=3)
    return engine, ExportPlan("synthetic://lifeos/p3-072", "synthetic-note-072", 3, "single_record", "json")


def close_engine(engine):
    engine.close()


def remove_test_sandbox(result):
    """Tests never leave their synthetic sandbox files behind."""
    if result.get("status") == "exported":
        shutil.rmtree(Path(tempfile.gettempdir()) / result["sandbox_id"])


def test_preview_discloses_confirmation_and_temporary_target():
    engine, plan = engine_and_plan()
    try:
        preview = engine.preview(plan)
        assert preview["status"] == "ready"
        assert preview["confirmation_required"] == "CONFIRM"
        assert preview["target_semantics"] == "new_system_temporary_sandbox_only"
        assert preview["content_identity"]["content_hash"]
        assert preview["external_action"] == "none"
    finally:
        close_engine(engine)


def test_exact_confirm_writes_once_to_new_temporary_sandbox_with_matching_receipt():
    engine, plan = engine_and_plan()
    try:
        preview = engine.preview(plan)
        result = engine.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
        assert result["status"] == "exported"
        assert result["content_matches_receipt"] is True
        assert result["export_hash"] in result["filename"]
        assert result["external_action"] == "temporary_sandbox_file_only"
        assert result["sandbox_id"].startswith("lifeos-p3-072-export-")
        exported = json.loads((Path(tempfile.gettempdir()) / result["sandbox_id"] / result["filename"]).read_text("utf-8"))
        assert exported["source"] == plan.source
        assert exported["content_identity"] == result["content_identity"]
        assert exported["plan_hash"] == result["plan_hash"]
        again = engine.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
        assert again["status"] == "blocked" and again["reason"] == "one_time_export_already_consumed"
        remove_test_sandbox(result)
    finally:
        close_engine(engine)


def test_missing_or_mismatched_confirmation_or_preview_token_fails_closed():
    for confirmation, token_modifier in (("confirm", False), ("CONFIRM", True)):
        engine, plan = engine_and_plan()
        try:
            preview = engine.preview(plan)
            token = "wrong" if token_modifier else preview["preview_token"]
            result = engine.confirm_and_export(plan, confirmation, token)
            assert result["status"] == "blocked" and result["external_action"] == "none"
        finally:
            close_engine(engine)


def test_source_version_unknown_conflict_revoked_and_tombstoned_fail_closed_and_audit():
    cases = []
    engine, plan = engine_and_plan()
    try:
        cases.append(engine.preview(ExportPlan("wrong-source", plan.content_id, 3, plan.scope, plan.target_category)))
        cases.append(engine.preview(ExportPlan(plan.source, plan.content_id, 4, plan.scope, plan.target_category)))
        cases.append(engine.preview(ExportPlan(plan.source, "unknown", 3, plan.scope, plan.target_category)))
        engine.set_conflict(plan.content_id)
        cases.append(engine.preview(plan))
    finally:
        close_engine(engine)
    for state in ("revoked", "tombstoned"):
        other, other_plan = engine_and_plan()
        other.set_state(other_plan.content_id, state)
        cases.append(other.preview(other_plan))
        close_engine(other)
    assert all(case["status"] == "blocked" and case["external_action"] == "none" for case in cases)


def test_write_failure_is_audited_and_leaves_no_visible_output():
    engine, plan = engine_and_plan()
    try:
        preview = engine.preview(plan)
        result = engine.confirm_and_export(plan, "CONFIRM", preview["preview_token"], inject_failure=True)
        assert result == {"status": "blocked", "reason": "write_failed", "visible_output_count": 0, "external_action": "none", "boundaries": BOUNDARIES}
        assert any(json.loads(event["detail_json"]).get("visible_output_count") == 0 for event in engine.audit_events())
    finally:
        close_engine(engine)


def test_collision_and_escaped_path_are_blocked_without_overwrite_or_visible_output():
    engine, plan = engine_and_plan()
    try:
        preview = engine.preview(plan)
        collision = engine.confirm_and_export(plan, "CONFIRM", preview["preview_token"], simulate_destination_collision=True)
        assert collision["status"] == "blocked" and collision["reason"] == "write_failed"
        assert collision["visible_output_count"] == 0 and collision["external_action"] == "none"
        sandbox = engine._new_sandbox()
        try:
            try:
                engine._atomic_new_file(sandbox, "../outside.json", b"synthetic")
                raise AssertionError("escaped path was accepted")
            except RuntimeError as error:
                assert str(error) == "destination_not_new_temporary_sandbox_file"
        finally:
            sandbox.rmdir()
    finally:
        close_engine(engine)


def test_static_boundary_contract_and_source_imports_are_closed():
    assert BOUNDARIES == {
        "network": "disabled", "tauri_ipc": "not_used", "vault": "not_used", "real_database": "not_used",
        "cloud": "not_used", "sync": "not_used", "multi_device": "not_used", "l3": "not_used",
        "external_user": "not_used", "non_temporary_path": "blocked",
    }
    source = (ROOT / "src" / "sandbox_export.py").read_text("utf-8")
    names = {node.names[0].name.split(".")[0] for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Import)}
    names |= {node.module.split(".")[0] for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ImportFrom) and node.module}
    assert not names & {"socket", "urllib", "http", "requests", "subprocess"}
    assert "mkdtemp" in source and "os.link" in source and "sqlite3.connect(\":memory:\")" in source
