import json
import tempfile
import time
import unittest
from pathlib import Path

from src.integrated_runtime import IntegratedRuntime


class RevokeIdempotencyReworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "synthetic.sqlite"
        self.rt = IntegratedRuntime(self.db)
        self.expires = int(time.time() * 1000) + 60_000

    def tearDown(self): self.rt.close(); self.temp.cleanup()
    def grant(self, key): return self.rt.set_permission("grant", self.expires, "CONFIRM", key)["permission_id"]

    def test_17_same_key_same_permission_is_idempotent(self):
        pid = self.grant("first")
        first = self.rt.revoke_permission(pid, "REVOKE", "revoke-key")
        repeat = self.rt.revoke_permission(pid, "REVOKE", "revoke-key")
        self.assertTrue(first["ok"]); self.assertTrue(repeat["ok"])
        self.assertEqual(repeat["reason"], "idempotent_repeat")

    def test_18_same_key_different_permission_is_visible_conflict(self):
        first, second = self.grant("first"), self.grant("second")
        self.assertTrue(self.rt.revoke_permission(first, "REVOKE", "shared-key")["ok"])
        conflict = self.rt.revoke_permission(second, "REVOKE", "shared-key")
        self.assertFalse(conflict["ok"]); self.assertEqual(conflict["reason"], "idempotency_conflict")
        states = {x["id"]: x["status"] for x in self.rt.snapshot()["permissions"]}
        self.assertEqual(states[first], "revoked"); self.assertEqual(states[second], "current")

    def test_19_restart_replay_keeps_same_receipt(self):
        pid = self.grant("first")
        self.rt.revoke_permission(pid, "REVOKE", "restart-key")
        self.rt.close(); self.rt = IntegratedRuntime(self.db)
        replay = self.rt.revoke_permission(pid, "REVOKE", "restart-key")
        self.assertTrue(replay["ok"]); self.assertEqual(replay["reason"], "idempotent_repeat")

    def test_20_audit_binds_permission_and_request_semantics(self):
        first, second = self.grant("first"), self.grant("second")
        self.rt.revoke_permission(first, "REVOKE", "audit-key")
        self.rt.revoke_permission(second, "REVOKE", "audit-key")
        audits = self.rt.snapshot()["audits"]
        revoked = [json.loads(x["detail_json"]) for x in audits if x["event"] == "permission_revoked"]
        blocked = [json.loads(x["detail_json"]) for x in audits if x["event"] == "revoke_blocked"]
        self.assertEqual(len(revoked), 1); self.assertEqual(revoked[0]["permission_id"], first)
        self.assertEqual(revoked[0]["operation"], "permission_revoke")
        self.assertEqual(blocked[-1]["reason"], "idempotency_conflict")
        self.assertEqual(blocked[-1]["permission_id"], second)

if __name__ == "__main__": unittest.main(verbosity=2)
