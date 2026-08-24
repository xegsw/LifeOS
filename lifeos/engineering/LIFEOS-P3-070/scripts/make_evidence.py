"""Generate task-local snapshots and a checksum manifest, never an export."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from export_plan import ExportPlan, SyntheticExportPlans  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    evidence = ROOT / "evidence"
    app = SyntheticExportPlans()
    try:
        app.register("synthetic-note-001", "synthetic_capture", 3)
        plan = ExportPlan("synthetic_capture", "synthetic-note-001", 3, "single_record", "portable_package_candidate")
        ready = app.preview(plan)
        confirmed = app.confirm(plan, "CONFIRM")
        blocked = app.confirm(plan, "CONFIRM", conflict=True)
        snapshot = {"ready_plan": ready, "confirmed_receipt": confirmed, "conflict_result": blocked, "state": app.snapshot()}
    finally:
        app.close()
    (evidence / "plan_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    files = [ROOT / "src" / "export_plan.py", ROOT / "tests" / "test_export_plan.py", evidence / "test_results.json", evidence / "test_run.log", evidence / "plan_snapshot.json"]
    lines = ["# LIFEOS-P3-070 Evidence Manifest", "", "All evidence is task-local synthetic plan/receipt verification; no export was created.", ""]
    lines += [f"- `{path.relative_to(ROOT)}`: `{digest(path)}`" for path in files]
    lines += ["", "- Boundary: `external_action=none`; no network, paths, Tauri/IPC, Vault, real export, cloud, sync, multi-device, L3, or external user capability."]
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
