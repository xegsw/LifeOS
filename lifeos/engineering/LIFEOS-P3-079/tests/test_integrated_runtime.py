import tempfile
import time
import unittest
from pathlib import Path

from src.integrated_runtime import BOUNDARIES, IntegratedRuntime


class IntegratedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "synthetic.sqlite"
        self.rt = IntegratedRuntime(self.db)
        self.until = int(time.time() * 1000) + 60_000

    def tearDown(self): self.rt.close(); self.temp.cleanup()
    def save(self, key="one"): return self.rt.save("非敏感测试文本：晨间复盘", key, "CONFIRM")
    def grant(self, key="grant"): return self.rt.set_permission("grant", self.until, "CONFIRM", key)

    def test_01_unconfirmed_never_saves(self):
        out = self.rt.save("x", "x", "NO"); self.assertFalse(out["ok"]); self.assertEqual(self.rt.snapshot()["records"], [])
    def test_02_save_and_view_source_status(self):
        r = self.save(); v = self.rt.view(r["record_id"]); self.assertEqual(v["source"], "operator_local_entry"); self.assertEqual(v["status"], "saved")
    def test_03_save_is_idempotent(self):
        a = self.save(); b = self.save(); self.assertTrue(b["duplicate"]); self.assertEqual(a["record_id"], b["record_id"])
    def test_04_save_conflict_visible(self):
        self.save(); out = self.rt.save("不同文本", "one", "CONFIRM"); self.assertFalse(out["ok"]); self.assertEqual(len(self.rt.snapshot()["records"]), 1)
    def test_05_atomic_failure_leaves_no_record(self):
        out = self.rt.save("x", "fault", "CONFIRM", inject_fault=True); self.assertFalse(out["ok"]); self.assertEqual(self.rt.snapshot()["records"], [])
    def test_06_default_deny(self):
        r = self.save(); out = self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM"); self.assertFalse(out["ok"]); self.assertEqual(out["reason"], "default_deny")
    def test_07_exact_grant_allows_local_only(self):
        r = self.save(); self.grant(); out = self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM"); self.assertEqual(out["allowed"], "allowed_local_synthetic")
    def test_08_wrong_confirmation_fail_closed(self):
        r = self.save(); self.grant(); out = self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "wrong"); self.assertFalse(out["ok"])
    def test_09_deny_wins(self):
        r = self.save(); self.grant(); self.rt.set_permission("deny", self.until, "CONFIRM", "deny"); self.assertEqual(self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM")["reason"], "explicit_deny_current")
    def test_10_expired_grant_denies(self):
        r = self.save(); out = self.rt.set_permission("grant", int(time.time()*1000)-1, "CONFIRM", "old"); self.assertFalse(out["ok"]); self.assertEqual(self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM")["reason"], "default_deny")
    def test_11_binding_mismatch_denies(self):
        r = self.save(); self.grant(); self.assertEqual(self.rt.restore_preview(r["record_id"], "wrong", 1, "CONFIRM")["reason"], "binding_mismatch")
    def test_12_restore_is_confirmed_and_idempotent(self):
        r = self.save(); self.grant(); a = self.rt.restore_confirm(r["record_id"], "operator_local_entry", 1, "CONFIRM"); b = self.rt.restore_confirm(r["record_id"], "operator_local_entry", 1, "CONFIRM"); self.assertFalse(a["idempotent"]); self.assertTrue(b["idempotent"])
    def test_13_revoked_record_never_restores(self):
        r = self.save(); self.grant(); self.rt.revoke_record(r["record_id"]); self.assertEqual(self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM")["reason"], "revoked_content")
    def test_14_permission_revoke_survives_restart(self):
        self.grant(); pid = self.rt.snapshot()["permissions"][0]["id"]; self.rt.revoke_permission(pid, "REVOKE", "rev"); self.rt.close(); self.rt = IntegratedRuntime(self.db); self.assertEqual(self.rt.snapshot()["permissions"][0]["status"], "revoked")
    def test_15_blocked_audit_survives_restart(self):
        r = self.save(); self.rt.restore_preview(r["record_id"], "operator_local_entry", 1, "CONFIRM"); self.rt.close(); self.rt = IntegratedRuntime(self.db); self.assertIn("restore_blocked", [x["event"] for x in self.rt.snapshot()["audits"]])
    def test_16_boundaries_closed(self):
        self.assertEqual(BOUNDARIES["network"], "disabled"); self.assertEqual(BOUNDARIES["external_action"], "none")

if __name__ == "__main__": unittest.main(verbosity=2)
