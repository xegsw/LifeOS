import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from local_runtime import BOUNDARIES, CONTROLLED_PROJECT_ID, ControlledLocalRuntime, VisibleRuntimeError


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "controlled.sqlite"
        self.app = ControlledLocalRuntime(self.db)

    def tearDown(self):
        self.app.close()
        self.temp.cleanup()

    def test_first_save_only_after_explicit_confirmation(self):
        receipt = self.app.save(text="非敏感测试原文", idempotency_key="first", confirmed=True, now_ms=1)
        self.assertTrue(receipt.saved)
        self.assertFalse(receipt.duplicate)
        self.assertEqual(receipt.message, "已保存")

    def test_missing_save_confirmation_is_blocked_without_record(self):
        with self.assertRaisesRegex(VisibleRuntimeError, "明确确认"):
            self.app.save(text="非敏感测试原文", idempotency_key="unconfirmed", confirmed=False, now_ms=1)
        self.assertEqual(self.app.count_records("unconfirmed"), 0)

    def test_empty_text_is_visible_failure_without_record(self):
        with self.assertRaisesRegex(VisibleRuntimeError, "不能为空"):
            self.app.save(text=" ", idempotency_key="empty", confirmed=True, now_ms=1)
        self.assertEqual(self.app.count_records("empty"), 0)

    def test_precommit_failure_rolls_back_and_never_reports_saved(self):
        with self.assertRaisesRegex(VisibleRuntimeError, "未提交"):
            self.app.save(text="不应留下半成品", idempotency_key="fault", confirmed=True, now_ms=1,
                          fail_before_commit=True)
        self.assertEqual(self.app.count_records("fault"), 0)
        self.assertNotIn("save_pending", self.app.audit_events())

    def test_same_request_is_idempotent(self):
        first = self.app.save(text="相同文本", idempotency_key="repeat", confirmed=True, now_ms=1)
        second = self.app.save(text="相同文本", idempotency_key="repeat", confirmed=True, now_ms=2)
        self.assertEqual(first.record_id, second.record_id)
        self.assertTrue(second.duplicate)
        self.assertEqual(self.app.count_records("repeat"), 1)

    def test_conflicting_idempotency_key_is_rejected_without_overwrite(self):
        self.app.save(text="原始文本", idempotency_key="conflict", confirmed=True, now_ms=1)
        with self.assertRaisesRegex(VisibleRuntimeError, "不同测试文本"):
            self.app.save(text="冲突文本", idempotency_key="conflict", confirmed=True, now_ms=2)
        self.assertEqual(self.app.record_view("rec-" + __import__("hashlib").sha256(b"conflict").hexdigest()[:16])["original_text"], "原始文本")

    def test_identity_receipt_and_view_are_visible(self):
        receipt = self.app.save(text="可见身份", idempotency_key="identity", confirmed=True, now_ms=1)
        view = self.app.record_view(receipt.record_id)
        self.assertEqual(view["original_text"], "可见身份")
        self.assertEqual(view["source_identity"], "operator_local_entry")
        self.assertEqual(view["content_identity"], "user_original")
        self.assertEqual(receipt.operator_confirmation, "explicit")
        self.assertEqual(receipt.ai_status, "disabled")

    def test_committed_record_survives_reopen(self):
        receipt = self.app.save(text="重启可读", idempotency_key="reopen", confirmed=True, now_ms=1)
        self.app.close()
        self.app = ControlledLocalRuntime(self.db)
        self.assertEqual(self.app.record_view(receipt.record_id)["original_text"], "重启可读")

    def test_unknown_project_restore_is_rejected(self):
        with self.assertRaisesRegex(VisibleRuntimeError, "受控范围"):
            self.app.restore_context("unknown-project")

    def test_next_step_requires_explicit_confirmation(self):
        with self.assertRaisesRegex(VisibleRuntimeError, "明确确认"):
            self.app.confirm_next_step(project_id=CONTROLLED_PROJECT_ID, next_step="人工下一步", confirmed=False, now_ms=1)

    def test_confirmed_next_step_has_no_external_action(self):
        result = self.app.confirm_next_step(project_id=CONTROLLED_PROJECT_ID, next_step="人工下一步", confirmed=True, now_ms=1)
        self.assertEqual(result["confirmation_identity"], "operator_confirmed")
        self.assertEqual(result["external_action"], "none")

    def test_all_prohibited_channels_are_closed(self):
        expected = {"network", "cloud", "tauri_ipc", "vault", "export", "sync", "multi_device", "l3", "external_user", "ai_consumption", "real_paths"}
        self.assertTrue(expected.issubset(BOUNDARIES))
        self.assertEqual(BOUNDARIES["external_action"], "none")


if __name__ == "__main__":
    unittest.main(verbosity=2)
