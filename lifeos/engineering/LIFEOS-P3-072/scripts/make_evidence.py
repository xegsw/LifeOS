#!/usr/bin/env python3
"""Create task-local receipt evidence from one synthetic temporary export run."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sandbox_export import ControlledSandboxExport, ExportPlan  # noqa: E402


def main() -> None:
    engine = ControlledSandboxExport()
    try:
        engine.register("synthetic-evidence-072", "synthetic://lifeos/p3-072/evidence", "Synthetic evidence body", version=1)
        plan = ExportPlan("synthetic://lifeos/p3-072/evidence", "synthetic-evidence-072", 1, "single_record", "json")
        preview = engine.preview(plan)
        receipt = engine.confirm_and_export(plan, "CONFIRM", preview["preview_token"])
        assert receipt["status"] == "exported" and receipt["content_matches_receipt"]
        evidence_receipt = {
            "task": "LIFEOS-P3-072",
            "run": "synthetic temporary sandbox export",
            "status": receipt["status"],
            "receipt": receipt["receipt"],
            "source": receipt["source"],
            "content_identity": receipt["content_identity"],
            "plan_hash": receipt["plan_hash"],
            "export_hash": receipt["export_hash"],
            "filename": receipt["filename"],
            "content_matches_receipt": receipt["content_matches_receipt"],
            "sandbox_created_per_run": True,
            "sandbox_removed_after_evidence_capture": True,
        }
        (ROOT / "evidence" / "export_receipt.json").write_text(json.dumps(evidence_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        shutil.rmtree(Path(tempfile.gettempdir()) / receipt["sandbox_id"])
    finally:
        engine.close()


if __name__ == "__main__":
    main()
