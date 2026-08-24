#!/usr/bin/env python3
"""Fresh, independent P3-071 review runner for the synthetic P3-070 plan package.

It never imports, invokes, or copies the P3-070 test suite.  The subject module is
copied into a per-run temporary directory so the reviewed tree stays read-only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUBJECT = ROOT / "lifeos/engineering/LIFEOS-P3-070"
OUT = Path(__file__).resolve().parent / "evidence/test_results.json"
REQUIRED_BOUNDARIES = {
    "network": "disabled", "paths": "not_used", "tauri_ipc": "not_used",
    "vault": "not_used", "real_export": "not_used", "cloud": "not_used",
    "sync": "not_used", "multi_device": "not_used", "l3": "not_used",
    "external_user": "not_used", "external_action": "none",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_has(snapshot: dict, reason: str) -> bool:
    for entry in snapshot["audit"]:
        if entry["event"] == "export_plan_blocked" and json.loads(entry["detail_json"]).get("reason") == reason:
            return True
    return False


def main() -> int:
    watched = [
        SUBJECT / "src/export_plan.py", SUBJECT / "evidence/MANIFEST.md",
        SUBJECT / "evidence/test_results.json", SUBJECT / "evidence/plan_snapshot.json",
        SUBJECT / "evidence/test_run.log",
    ]
    before = {str(p.relative_to(ROOT)): digest(p) for p in watched}
    cases: list[dict] = []

    def check(name: str, assertion: bool, detail: str) -> None:
        cases.append({"id": name, "result": "PASS" if assertion else "FAIL", "detail": detail})

    with tempfile.TemporaryDirectory(prefix="lifeos-p3-071-") as temp:
        copied = Path(temp) / "export_plan.py"
        shutil.copy2(SUBJECT / "src/export_plan.py", copied)
        spec = importlib.util.spec_from_file_location("p3070_subject_copy", copied)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        plans = module.SyntheticExportPlans()
        plan = module.ExportPlan("synthetic_capture", "review-note-001", 7, "single_record", "portable_package_candidate")
        plans.register("review-note-001", "synthetic_capture", 7)

        ready = plans.preview(plan)
        check("IR-01-default-plan-does-not-execute", ready["status"] == "ready" and ready["external_action"] == "none", "preview remains a plan")
        check("IR-02-required-disclosure-visible", all(k in ready for k in ("source", "content_identity", "scope", "target_category", "confirmation_required", "conflict_semantics", "failure_semantics")), "all required plan semantics are visible")
        receipt = plans.confirm(plan, "CONFIRM")
        check("IR-03-only-confirm-produces-local-receipt", receipt.get("receipt") == "local_confirmed_plan_only" and receipt["external_action"] == "none", "confirmation only returns local receipt")
        missing = plans.confirm(plan, "confirm")
        check("IR-04-missing-confirm-fails-closed-and-audits", missing.get("reason") == "explicit_confirmation_required" and audit_has(plans.snapshot(), "explicit_confirmation_required"), "case-sensitive confirmation is required")
        source_bad = plans.preview(module.ExportPlan("other", "review-note-001", 7, "single_record", "portable_package_candidate"))
        check("IR-05-source-mismatch-fails-closed-and-audits", source_bad.get("reason") == "source_mismatch" and audit_has(plans.snapshot(), "source_mismatch"), "source mismatch is blocked")
        version_bad = plans.preview(module.ExportPlan("synthetic_capture", "review-note-001", 8, "single_record", "portable_package_candidate"))
        check("IR-06-version-mismatch-fails-closed-and-audits", version_bad.get("reason") == "identity_version_mismatch" and audit_has(plans.snapshot(), "identity_version_mismatch"), "identity/version mismatch is blocked")
        conflict = plans.confirm(plan, "CONFIRM", conflict=True)
        check("IR-07-conflict-fails-closed-and-audits", conflict.get("reason") == "conflict_detected" and audit_has(plans.snapshot(), "conflict_detected"), "conflict is blocked")
        plans.revoke("review-note-001", "revoked")
        revoked = plans.preview(plan)
        check("IR-08-revocation-fails-closed-and-audits", revoked.get("reason") == "revoked_or_tombstoned" and audit_has(plans.snapshot(), "revoked_or_tombstoned"), "revoked record is blocked")
        plans.register("review-note-002", "synthetic_capture", 1)
        plans.revoke("review-note-002", "tombstoned")
        tomb = plans.preview(module.ExportPlan("synthetic_capture", "review-note-002", 1, "single_record", "portable_package_candidate"))
        check("IR-09-tombstone-fails-closed-and-audits", tomb.get("reason") == "revoked_or_tombstoned" and audit_has(plans.snapshot(), "revoked_or_tombstoned"), "tombstoned record is blocked")
        unknown = plans.preview(module.ExportPlan("synthetic_capture", "unknown", 1, "single_record", "portable_package_candidate"))
        check("IR-10-unknown-fails-closed-and-audits", unknown.get("reason") == "unknown_content" and audit_has(plans.snapshot(), "unknown_content"), "unknown record is blocked")
        invalid = plans.preview({"not": "a plan"})
        check("IR-11-invalid-input-fails-closed-and-audits", invalid.get("reason") == "invalid_or_unknown_plan" and audit_has(plans.snapshot(), "invalid_or_unknown_plan"), "untyped input is blocked")
        check("IR-12-all-boundaries-closed", ready["boundaries"] == REQUIRED_BOUNDARIES and receipt["boundaries"] == REQUIRED_BOUNDARIES, "all prohibited capabilities remain closed")
        source_text = copied.read_text()
        tree = ast.parse(source_text)
        imports = {
            (node.module or "").split(".")[0] for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name.split(".")[0] for node in ast.walk(tree)
            if isinstance(node, ast.Import) for alias in node.names
        }
        forbidden_imports = {"requests", "urllib", "http", "socket", "pathlib", "subprocess", "os", "shutil"}
        check("IR-13-static-source-has-no-external-capability-import", not (imports & forbidden_imports) and "open(" not in source_text, "AST import scan and file-write scan find no external capability")
        plans.close()

    after = {str(p.relative_to(ROOT)): digest(p) for p in watched}
    result = {
        "task": "LIFEOS-P3-071", "runner": "independent_runner.py", "subject": "LIFEOS-P3-070",
        "subject_tests_imported_called_or_copied": False, "temporary_subject_copy_only": True,
        "test_count": len(cases), "passed": sum(c["result"] == "PASS" for c in cases),
        "failed": sum(c["result"] == "FAIL" for c in cases), "cases": cases,
        "subject_hashes_before": before, "subject_hashes_after": after,
        "subject_hashes_unchanged": before == after, "external_action": "none",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0 if result["failed"] == 0 and result["subject_hashes_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
