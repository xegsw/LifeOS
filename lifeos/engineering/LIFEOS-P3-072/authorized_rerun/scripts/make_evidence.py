#!/usr/bin/env python3
"""Create a redacted receipt evidence artifact; temp output is removed afterward."""
from __future__ import annotations
import json, shutil, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sandbox_export import ControlledSandboxExport, ExportPlan
app = ControlledSandboxExport()
try:
    app.register("synthetic-evidence-072", "synthetic://lifeos/p3-072", "Synthetic evidence payload", 1)
    plan = ExportPlan("synthetic://lifeos/p3-072", "synthetic-evidence-072", 1, "single_record", "json")
    preview = app.preview(plan); result = app.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
    assert result["status"] == "exported"
    receipt = {key: result[key] for key in ("status", "receipt", "source", "content_identity", "plan_hash", "export_hash", "filename", "content_matches_receipt", "external_action", "boundaries")}
    receipt["temporary_sandbox_removed_after_capture"] = True
    (ROOT / "evidence" / "export_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    shutil.rmtree(Path(tempfile.gettempdir()) / result["sandbox_id"])
finally: app.close()
