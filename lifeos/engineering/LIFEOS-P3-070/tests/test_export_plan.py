import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from export_plan import BOUNDARIES, ExportPlan, SyntheticExportPlans


class ExportPlanTests(unittest.TestCase):
    def setUp(self):
        self.app = SyntheticExportPlans()
        self.app.register("synthetic-note-001", "synthetic_capture", 3)
        self.plan = ExportPlan("synthetic_capture", "synthetic-note-001", 3, "single_record", "portable_package_candidate")

    def tearDown(self):
        self.app.close()

    def test_ready_plan_discloses_all_required_semantics(self):
        preview = self.app.preview(self.plan)
        self.assertEqual("ready", preview["status"])
        for key in ("source", "content_identity", "scope", "target_category", "confirmation_required", "conflict_semantics", "failure_semantics"):
            self.assertIn(key, preview)
        self.assertEqual("none", preview["external_action"])

    def test_default_is_no_execution(self):
        before = len(self.app.snapshot()["audit"])
        self.assertEqual("ready", self.app.preview(self.plan)["status"])
        self.assertEqual(before, len(self.app.snapshot()["audit"]))
        self.assertFalse(any(row["event"] == "export_plan_confirmed" for row in self.app.snapshot()["audit"]))

    def test_confirm_returns_local_receipt_without_external_action(self):
        result = self.app.confirm(self.plan, "CONFIRM")
        self.assertEqual("confirmed_plan", result["status"])
        self.assertEqual("local_confirmed_plan_only", result["receipt"])
        self.assertEqual("none", result["external_action"])

    def test_missing_confirm_is_blocked_and_audited(self):
        self.assertEqual("explicit_confirmation_required", self.app.confirm(self.plan, "")["reason"])
        self.assertIn("export_plan_blocked", [row["event"] for row in self.app.snapshot()["audit"]])

    def test_source_and_identity_mismatches_fail_closed(self):
        self.assertEqual("source_mismatch", self.app.confirm(ExportPlan("other", "synthetic-note-001", 3, "single_record", "portable_package_candidate"), "CONFIRM")["reason"])
        self.assertEqual("identity_version_mismatch", self.app.confirm(ExportPlan("synthetic_capture", "synthetic-note-001", 2, "single_record", "portable_package_candidate"), "CONFIRM")["reason"])

    def test_conflict_revocation_tombstone_and_unknown_fail_closed(self):
        self.assertEqual("conflict_detected", self.app.confirm(self.plan, "CONFIRM", conflict=True)["reason"])
        self.app.revoke("synthetic-note-001", "revoked")
        self.assertEqual("revoked_or_tombstoned", self.app.confirm(self.plan, "CONFIRM")["reason"])
        unknown = ExportPlan("synthetic_capture", "unknown", 1, "single_record", "portable_package_candidate")
        self.assertEqual("unknown_content", self.app.confirm(unknown, "CONFIRM")["reason"])

    def test_static_boundary_contract_has_all_closed_capabilities(self):
        expected = {"network", "paths", "tauri_ipc", "vault", "real_export", "cloud", "sync", "multi_device", "l3", "external_user", "external_action"}
        self.assertTrue(expected.issubset(BOUNDARIES))
        self.assertEqual("disabled", BOUNDARIES["network"])
        self.assertTrue(all(value in {"disabled", "not_used", "none"} for value in BOUNDARIES.values()))

    def test_static_source_has_no_external_capability_imports(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "export_plan.py").read_text()
        for forbidden in ("import os", "import pathlib", "import socket", "import requests", "import urllib", "import subprocess"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
