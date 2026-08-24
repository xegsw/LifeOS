from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from permission_runtime import BOUNDARY, PermissionRuntime

class PermissionRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.runtime = PermissionRuntime(Path(self.tmp.name) / "runtime.sqlite")
        self.context = {k: BOUNDARY[k] for k in ("project", "category", "purpose", "location", "processor")}
    def tearDown(self): self.runtime.close(); self.tmp.cleanup()
    def set(self, decision="grant", key="key-1", expiry=9999999999999): return self.runtime.set_decision(decision, self.context, expiry, "CONFIRM", key)
    def test_01_default_deny(self): self.assertEqual(self.runtime.consume(self.context, "CONFIRM")["reason"], "default_deny")
    def test_02_unique_grant_allows_synthetic_only(self): self.assertTrue(self.runtime.consume(self.context, "CONFIRM") ["allowed"] if self.set()["ok"] else False)
    def test_03_deny_precedes_grant(self): self.set("grant", "g"); self.set("deny", "d"); self.assertEqual(self.runtime.consume(self.context,"CONFIRM")["reason"], "explicit_deny_current")
    def test_04_grant_after_deny_still_denies(self): self.set("deny", "d"); self.set("grant", "g"); self.assertEqual(self.runtime.consume(self.context,"CONFIRM")["reason"], "explicit_deny_current")
    def test_05_multiple_grants_are_ambiguous(self): self.set("grant","g1"); self.set("grant","g2"); self.assertEqual(self.runtime.consume(self.context,"CONFIRM")["reason"], "ambiguous_multiple_current_grants")
    def test_06_revoke_fails_closed_and_is_idempotent(self): pid=self.set()["permission_id"]; self.assertTrue(self.runtime.revoke(pid,"REVOKE","r")["ok"]); self.assertFalse(self.runtime.consume(self.context,"CONFIRM")["allowed"]); self.assertEqual(self.runtime.revoke(pid,"REVOKE","r")["reason"], "idempotent_repeat")
    def test_07_expired_is_rejected(self): self.assertFalse(self.set(expiry=1)["ok"]); self.assertFalse(self.runtime.consume(self.context,"CONFIRM")["allowed"])
    def test_08_context_mismatch_denies(self): self.set(); bad=dict(self.context); bad["processor"]="other"; self.assertEqual(self.runtime.consume(bad,"CONFIRM")["reason"], "invalid_context")
    def test_09_confirm_required(self): self.set(); self.assertEqual(self.runtime.consume(self.context,"NO")["reason"], "confirmation_required")
    def test_10_repeated_decision_is_idempotent(self):
        expiry = 9999999999999
        first = self.set(expiry=expiry); again = self.set(expiry=expiry)
        self.assertTrue(again["ok"]); self.assertEqual(again["permission_id"], first["permission_id"])
    def test_11_key_conflict_is_visible(self): self.set("grant", "same"); self.assertEqual(self.set("deny", "same")["reason"], "idempotency_conflict")
    def test_12_audit_has_confirmations_and_rejections(self): self.runtime.consume(self.context,"NO"); self.set(); snap=self.runtime.snapshot(); self.assertTrue(any(a["event"] == "rejected" for a in snap["audits"])); self.assertTrue(any(a["confirmation"] == "CONFIRM" for a in snap["audits"]))
    def test_13_cli_preview_is_operator_visible(self):
        cli = Path(__file__).resolve().parents[1] / "scripts" / "permission_cli.py"
        result = subprocess.run([sys.executable, str(cli), "preview", "--run-id", "cli-test"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0); self.assertEqual(json.loads(result.stdout)["default_decision"], "deny")
    def test_14_atomic_failure_leaves_no_permission_row(self):
        self.runtime.conn.execute("CREATE TRIGGER inject_failure BEFORE INSERT ON permissions BEGIN SELECT RAISE(ABORT, 'injected'); END;")
        self.runtime.conn.commit(); self.assertEqual(self.set()["reason"], "atomic_write_failed")
        self.assertEqual(self.runtime.snapshot()["permissions"], [])
    def test_15_reopen_preserves_revoke_audit_and_fail_closed(self):
        db = self.runtime.db_path; pid = self.set()["permission_id"]; self.runtime.revoke(pid, "REVOKE", "reopen-r")
        self.runtime.close(); self.runtime = PermissionRuntime(db)
        self.assertFalse(self.runtime.consume(self.context, "CONFIRM")["allowed"])
        self.assertTrue(any(a["event"] == "revoked" for a in self.runtime.snapshot()["audits"]))

if __name__ == "__main__": unittest.main()
