import ast
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sandbox_export import BOUNDARIES, ControlledSandboxExport, ExportPlan


def make():
    app = ControlledSandboxExport()
    app.register("synthetic-note-072", "synthetic://lifeos/p3-072", "Synthetic export body", 3)
    return app, ExportPlan("synthetic://lifeos/p3-072", "synthetic-note-072", 3, "single_record", "json")


def remove(result):
    if result.get("status") == "exported":
        shutil.rmtree(Path(tempfile.gettempdir()) / result["sandbox_id"])


def test_preview_is_default_no_write_with_required_disclosure():
    app, plan = make()
    try:
        before = len(app.audit_events()); preview = app.preview(plan)
        assert preview["status"] == "ready" and preview["confirmation_required"] == "CONFIRM"
        assert preview["target_semantics"] == "new_system_temporary_sandbox_only"
        assert preview["external_action"] == "none" and len(app.audit_events()) == before + 1
    finally: app.close()


def test_exact_confirmation_creates_one_new_temp_file_with_matching_receipt():
    app, plan = make()
    try:
        preview = app.preview(plan); result = app.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
        path = Path(tempfile.gettempdir()) / result["sandbox_id"] / result["filename"]
        assert result["status"] == "exported" and path.is_file() and result["content_matches_receipt"]
        assert json.loads(path.read_text())["source"] == plan.source
        again = app.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
        assert again["reason"] == "one_time_export_already_consumed"; remove(result)
    finally: app.close()


def test_confirmation_and_preview_token_must_be_exact():
    for confirmation, token in (("confirm", "valid"), ("CONFIRM", "wrong")):
        app, plan = make()
        try:
            preview = app.preview(plan); result = app.confirm_and_export(plan, confirmation, preview["preview_token"] if token == "valid" else token)
            assert result["status"] == "blocked" and result["external_action"] == "none"
        finally: app.close()


def test_source_version_unknown_conflict_revocation_and_tombstone_fail_closed():
    app, plan = make()
    try:
        results = [app.preview(ExportPlan("wrong", plan.content_id, 3, plan.scope, plan.target_category)), app.preview(ExportPlan(plan.source, plan.content_id, 4, plan.scope, plan.target_category)), app.preview(ExportPlan(plan.source, "unknown", 3, plan.scope, plan.target_category))]
        app.set_conflict(plan.content_id); results.append(app.preview(plan))
    finally: app.close()
    for state in ("revoked", "tombstoned"):
        other, candidate = make(); other.set_state(candidate.content_id, state); results.append(other.preview(candidate)); other.close()
    assert all(result["status"] == "blocked" and result["external_action"] == "none" for result in results)


def test_state_changed_after_preview_cannot_be_exported():
    app, plan = make()
    try:
        preview = app.preview(plan); app.set_state(plan.content_id, "revoked")
        assert app.confirm_and_export(plan, "CONFIRM", preview["preview_token"])["reason"] == "revoked_or_tombstoned"
    finally: app.close()


def test_write_failure_and_collision_leave_no_visible_output_and_are_audited():
    for kwargs in ({"fail_write": True}, {"collision": True}):
        app, plan = make()
        try:
            preview = app.preview(plan); result = app.confirm_and_export(plan, "CONFIRM", preview["preview_token"], **kwargs)
            assert result["reason"] == "write_failed" and result["visible_output_count"] == 0
            assert any(json.loads(row["detail_json"]).get("visible_output_count") == 0 for row in app.audit_events())
        finally: app.close()


def test_escape_and_existing_destination_are_rejected_without_overwrite():
    app, _ = make(); sandbox = app._new_sandbox()
    try:
        for name in ("../escape.json", "same.json"):
            if name == "same.json": (sandbox / name).write_bytes(b"old")
            try: app._write_new_atomically(sandbox, name, b"new")
            except RuntimeError: pass
            else: raise AssertionError("unsafe destination accepted")
        assert (sandbox / "same.json").read_bytes() == b"old"
    finally:
        ControlledSandboxExport._cleanup(sandbox); app.close()


def test_static_capability_boundary_is_closed():
    assert BOUNDARIES["non_temporary_path"] == "blocked"
    source = (ROOT / "src" / "sandbox_export.py").read_text()
    modules = {a.name.split(".")[0] for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Import) for a in node.names}
    assert not modules & {"socket", "urllib", "http", "requests", "subprocess"}
    assert "sqlite3.connect(\":memory:\")" in source and "mkdtemp" in source and "os.link" in source
