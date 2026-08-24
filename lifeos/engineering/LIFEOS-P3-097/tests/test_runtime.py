import hashlib
import os
import sys
import shutil
import sqlite3
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import local_capture as runtime
from local_capture import CaptureError, capture, delete_all, list_today, render_today, safe_snapshot


class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="lifeos-p3-097-unit-", dir="/private/tmp")); self.db = self.root / "capture.sqlite"
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def capture_and_render(self):
        capture(self.db, "固定非敏感测试记录", "one")
        page = self.root / "today.html"
        render_today(self.db)
        return page
    def assert_db_unchanged(self):
        with sqlite3.connect(f"file:{self.db}?mode=ro", uri=True) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0], 1)
    def test_first_restart_and_render(self):
        self.assertEqual(capture(self.db, "固定非敏感测试记录", "one")["status"], "saved")
        self.assertEqual(len(list_today(self.db)), 1)
        out = self.root / "today.html"; self.assertEqual(render_today(self.db)["status"], "rendered")
        self.assertIn("固定非敏感测试记录", out.read_text())
    def test_repeat_and_conflict(self):
        capture(self.db, "固定非敏感测试记录", "one")
        self.assertEqual(capture(self.db, "固定非敏感测试记录", "one")["status"], "idempotent_repeat")
        with self.assertRaises(CaptureError): capture(self.db, "different", "one")
    def test_empty_and_atomic_failure(self):
        with self.assertRaises(CaptureError): capture(self.db, "", "one")
        with self.assertRaises(CaptureError): capture(self.db, "fixed", "fail", inject_failure=True)
        self.assertFalse(self.db.exists())
        self.assertEqual(list(self.root.iterdir()), [])
    def test_clear_confirmation_and_clean(self):
        page = self.capture_and_render()
        with self.assertRaises(CaptureError): delete_all(self.db, "no")
        self.assertTrue(page.exists())
        result = delete_all(self.db, "DELETE")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["today_view"], "invalidated")
        self.assertEqual(list_today(self.db), [])
        self.assertFalse(page.exists())
        with self.assertRaises(CaptureError): render_today(self.db)
        self.assertFalse(page.exists())
    def test_clear_page_invalidation_failure_preserves_db(self):
        page = self.capture_and_render()
        original = os.unlink
        def fail_exact(target, *args, **kwargs):
            if target == page.name and kwargs.get("dir_fd") is not None:
                raise PermissionError("injected page invalidation failure")
            return original(target, *args, **kwargs)
        with patch.object(os, "unlink", fail_exact):
            with self.assertRaises(CaptureError):
                delete_all(self.db, "DELETE")
        self.assert_db_unchanged()
        self.assertTrue(page.exists())
    def test_caller_output_paths_are_rejected_before_change(self):
        page = self.capture_and_render()
        outside = self.root.parent / (self.root.name + "-outside-sentinel.txt")
        outside.write_text("fixed non-sensitive sentinel", encoding="utf-8")
        outside_hash = hashlib.sha256(outside.read_bytes()).hexdigest()
        try:
            candidates = [
                page,
                self.root / "other.html",
                outside,
                Path("today.html"),
                self.root / "nested" / ".." / "today.html",
                self.root / ".." / self.root.name / "today.html",
            ]
            for candidate in candidates:
                with self.subTest(candidate=str(candidate)):
                    with self.assertRaises(CaptureError):
                        delete_all(self.db, "DELETE", candidate)
                    self.assert_db_unchanged()
                    self.assertTrue(page.exists())
            self.assertTrue(outside.exists())
            self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), outside_hash)
        finally:
            outside.unlink(missing_ok=True)
    def test_symlink_today_is_rejected_without_following(self):
        capture(self.db, "固定非敏感测试记录", "one")
        outside = self.root / "fixed-sentinel.txt"
        outside.write_text("fixed non-sensitive sentinel", encoding="utf-8")
        outside_hash = hashlib.sha256(outside.read_bytes()).hexdigest()
        page = self.root / "today.html"
        page.symlink_to(outside)
        with self.assertRaises(CaptureError):
            delete_all(self.db, "DELETE")
        self.assertTrue(page.is_symlink())
        self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), outside_hash)
        self.assert_db_unchanged()
    def test_directory_and_special_today_are_rejected(self):
        capture(self.db, "固定非敏感测试记录", "one")
        page = self.root / "today.html"
        page.mkdir()
        with self.assertRaises(CaptureError):
            delete_all(self.db, "DELETE")
        self.assert_db_unchanged()
        page.rmdir()
        os.mkfifo(page)
        with self.assertRaises(CaptureError):
            delete_all(self.db, "DELETE")
        self.assert_db_unchanged()
    def test_symlink_db_parent_is_rejected(self):
        real = self.root / "real"
        real.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        real_db = real / "capture.sqlite"
        capture(real_db, "固定非敏感测试记录", "linked")
        linked_db = alias / "capture.sqlite"
        with self.assertRaises(CaptureError):
            capture(linked_db, "固定非敏感测试记录二", "linked-two")
        with self.assertRaises(CaptureError):
            render_today(linked_db)
        (real / "today.html").write_text("fixed non-sensitive internal page", encoding="utf-8")
        with self.assertRaises(CaptureError):
            delete_all(linked_db, "DELETE")
        self.assertEqual(len(list_today(real_db)), 1)
        self.assertTrue((real / "today.html").exists())
    def test_symlink_db_file_is_rejected(self):
        real_dir = self.root / "real-db"
        real_dir.mkdir()
        real_db = real_dir / "capture.sqlite"
        capture(real_db, "固定非敏感测试记录", "linked-db")
        local_dir = self.root / "local"
        local_dir.mkdir()
        linked_db = local_dir / "capture.sqlite"
        linked_db.symlink_to(real_db)
        page = local_dir / "today.html"
        page.write_text("fixed non-sensitive internal page", encoding="utf-8")
        with self.assertRaises(CaptureError):
            delete_all(linked_db, "DELETE")
        self.assertEqual(len(list_today(real_db)), 1)
        self.assertTrue(page.exists())
    def test_cli_has_no_output_path_capability(self):
        page = self.capture_and_render()
        outside = self.root / "fixed-cli-sentinel.txt"
        outside.write_text("fixed non-sensitive sentinel", encoding="utf-8")
        before = hashlib.sha256(outside.read_bytes()).hexdigest()
        cli = Path(__file__).resolve().parents[1] / "scripts" / "operator_cli.py"
        completed = subprocess.run([
            sys.executable, "-B", str(cli), "--db", str(self.db), "clear",
            "--confirmation", "DELETE", "--output", str(outside),
        ], text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(outside.exists())
        self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), before)
        self.assert_db_unchanged()
        self.assertTrue(page.exists())
        completed = subprocess.run([
            sys.executable, "-B", str(cli), "--db", str(self.db), "render",
            "--output", str(outside),
        ], text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), before)
        self.assert_db_unchanged()

    def test_render_caller_path_and_final_types_are_rejected(self):
        capture(self.db, "固定非敏感测试记录", "one")
        outside = self.root / "fixed-render-sentinel.txt"
        outside.write_text("fixed non-sensitive sentinel", encoding="utf-8")
        before = hashlib.sha256(outside.read_bytes()).hexdigest()
        with self.assertRaises(CaptureError):
            render_today(self.db, outside)
        self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), before)
        self.assert_db_unchanged()

        page = self.root / "today.html"
        page.symlink_to(outside)
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assertTrue(page.is_symlink())
        self.assertEqual(hashlib.sha256(outside.read_bytes()).hexdigest(), before)
        page.unlink()
        page.mkdir()
        with self.assertRaises(CaptureError):
            render_today(self.db)
        page.rmdir()
        os.mkfifo(page)
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assert_db_unchanged()

    def test_render_and_clear_reject_ancestor_symlink_chain(self):
        real_root = self.root / "real-root"
        nested = real_root / "nested"
        nested.mkdir(parents=True)
        real_db = nested / "capture.sqlite"
        capture(real_db, "固定非敏感测试记录", "ancestor")
        render_today(real_db)
        real_page = nested / "today.html"
        before = hashlib.sha256(real_page.read_bytes()).hexdigest()
        alias = self.root / "alias-root"
        alias.symlink_to(real_root, target_is_directory=True)
        linked_db = alias / "nested" / "capture.sqlite"
        with self.assertRaises(CaptureError):
            render_today(linked_db)
        with self.assertRaises(CaptureError):
            delete_all(linked_db, "DELETE")
        self.assertTrue(real_page.exists())
        self.assertEqual(hashlib.sha256(real_page.read_bytes()).hexdigest(), before)
        self.assertEqual(len(list_today(real_db)), 1)

    def test_render_and_clear_reject_relative_and_dotdot_db_paths(self):
        capture(self.db, "固定非敏感测试记录", "one")
        dotdot_db = self.root / "nested" / ".." / self.db.name
        for candidate in (Path("capture.sqlite"), dotdot_db):
            with self.subTest(candidate=str(candidate)):
                with self.assertRaises(CaptureError):
                    render_today(candidate)
                with self.assertRaises(CaptureError):
                    delete_all(candidate, "DELETE")
        self.assert_db_unchanged()
    def test_empty_render_is_closed(self):
        capture(self.db, "temporary", "temporary")
        delete_all(self.db, "DELETE")
        with self.assertRaises(CaptureError): render_today(self.db)

    def test_empty_db_with_stale_page_is_invalidated_without_db_change(self):
        page = self.capture_and_render()
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM captures")
        before = self.db.read_bytes()
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assertFalse(page.exists())
        self.assertEqual(self.db.read_bytes(), before)
        with self.assertRaises(CaptureError):
            list_today(self.db)

    def test_corrupt_db_with_stale_page_is_invalidated_without_db_change(self):
        page = self.capture_and_render()
        self.db.write_bytes(b"fixed non-sensitive corrupt sqlite fixture")
        before = self.db.read_bytes()
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assertFalse(page.exists())
        self.assertEqual(self.db.read_bytes(), before)

    def test_query_failure_with_stale_page_is_invalidated_without_db_change(self):
        page = self.capture_and_render()
        before = self.db.read_bytes()
        with patch("local_capture._read_validated", side_effect=CaptureError("injected query failure")):
            with self.assertRaises(CaptureError):
                render_today(self.db)
        self.assertFalse(page.exists())
        self.assertEqual(self.db.read_bytes(), before)

    def test_stale_page_invalidation_failure_is_disclosed_and_db_unchanged(self):
        page = self.capture_and_render()
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM captures")
        db_before = self.db.read_bytes()
        page_before = page.read_bytes()
        original = os.unlink
        def fail_exact(target, *args, **kwargs):
            if target == page.name and kwargs.get("dir_fd") is not None:
                raise PermissionError("injected stale-page invalidation failure")
            return original(target, *args, **kwargs)
        with patch.object(os, "unlink", fail_exact):
            with self.assertRaisesRegex(CaptureError, "既有今日页无法失效"):
                render_today(self.db)
        self.assertEqual(page.read_bytes(), page_before)
        self.assertEqual(self.db.read_bytes(), db_before)
        with self.assertRaises(CaptureError):
            list_today(self.db)

    def test_missing_db_with_stale_page_is_invalidated_without_creation(self):
        self.root.mkdir(exist_ok=True)
        page = self.root / "today.html"
        page.write_bytes(b"fixed non-sensitive stale internal page")
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assertFalse(page.exists())
        self.assertFalse(self.db.exists())
        self.assertEqual(list(self.root.glob("capture.sqlite*")), [])

    def test_zero_byte_db_with_stale_page_is_invalidated_without_db_change(self):
        self.root.mkdir(exist_ok=True)
        self.db.write_bytes(b"")
        page = self.root / "today.html"
        page.write_bytes(b"fixed non-sensitive stale internal page")
        before = self.db.read_bytes()
        with self.assertRaises(CaptureError):
            render_today(self.db)
        self.assertFalse(page.exists())
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(list(self.root.glob("capture.sqlite-*")), [])

    def test_missing_and_partial_schema_are_not_initialized_by_render(self):
        for name, statements in {
            "no-required-schema": ["CREATE TABLE other(value TEXT)"],
            "partial-schema": [
                "CREATE TABLE captures(id TEXT, content TEXT, created_at TEXT, source TEXT, idem_key TEXT)"
            ],
            "both-tables-incomplete": [
                "CREATE TABLE captures(id TEXT, content TEXT, created_at TEXT, source TEXT)",
                "CREATE TABLE audit(id INTEGER, event TEXT)",
            ],
        }.items():
            with self.subTest(name=name):
                case = self.root / name
                case.mkdir()
                db = case / "capture.sqlite"
                with sqlite3.connect(db) as conn:
                    for statement in statements:
                        conn.execute(statement)
                page = case / "today.html"
                page.write_bytes(b"fixed non-sensitive stale internal page")
                before = db.read_bytes()
                with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                    objects_before = conn.execute(
                        "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
                    ).fetchall()
                with self.assertRaises(CaptureError):
                    render_today(db)
                with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                    objects_after = conn.execute(
                        "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
                    ).fetchall()
                self.assertFalse(page.exists())
                self.assertEqual(db.read_bytes(), before)
                self.assertEqual(objects_after, objects_before)
                self.assertEqual(list(case.glob("capture.sqlite-*")), [])

class InvariantClosureTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="lifeos-p3-097-invariant-", dir="/private/tmp"))
        self.db = self.root / "capture.sqlite"

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def seed(self, text="fixed <tag> & \"quote\" 中文\nline", key="fixed-key"):
        return capture(self.db, text, key)

    def db_hash(self):
        return hashlib.sha256(self.db.read_bytes()).hexdigest() if self.db.exists() else None

    def test_all_public_entries_share_exact_path_gate(self):
        self.seed()
        entries = [
            lambda p: capture(p, "fixed second", "second"),
            list_today,
            safe_snapshot,
            render_today,
            lambda p: delete_all(p, "DELETE"),
        ]
        for raw in ("capture.sqlite", str(self.root / "nested" / ".." / "capture.sqlite"),
                    str(self.root) + "//capture.sqlite", str(self.root / "other.sqlite")):
            for entry in entries:
                with self.subTest(raw=raw, entry=entry):
                    before = self.db_hash()
                    with self.assertRaises(CaptureError): entry(raw)
                    self.assertEqual(self.db_hash(), before)

    def test_parent_must_preexist_and_capture_leaves_nothing(self):
        db = self.root / "missing" / "capture.sqlite"
        with self.assertRaises(CaptureError): capture(db, "fixed", "key")
        self.assertFalse(db.parent.exists())

    def test_db_and_page_hardlinks_are_rejected(self):
        self.seed(); page = self.root / "today.html"; render_today(self.db)
        db_link = self.root / "db-hardlink"; os.link(self.db, db_link)
        with self.assertRaises(CaptureError): list_today(self.db)
        db_link.unlink()
        page_link = self.root / "page-hardlink"; os.link(page, page_link)
        with self.assertRaises(CaptureError): safe_snapshot(self.db)

    def test_db_and_page_socket_fifo_directory_objects_are_rejected(self):
        cases = ("directory", "fifo", "socket")
        for target_kind in ("db", "page"):
            for kind in cases:
                with self.subTest(target=target_kind, kind=kind):
                    case = self.root / f"{target_kind}-{kind}"; case.mkdir()
                    db = case / "capture.sqlite"; page = case / "today.html"
                    if target_kind == "page": capture(db, "fixed", "key"); target = page
                    else: target = db
                    if kind == "directory": target.mkdir()
                    elif kind == "fifo": os.mkfifo(target)
                    else:
                        target.write_bytes(b"fixed socket placeholder")
                    if kind != "socket":
                        with self.assertRaises(CaptureError): list_today(db)
                    else:
                        real_stat = os.stat
                        def socket_stat(name, *args, **kwargs):
                            if name == target.name and kwargs.get("dir_fd") is not None and kwargs.get("follow_symlinks") is False:
                                return os.stat_result((stat.S_IFSOCK | 0o600, 0, 0, 1, 0, 0, 0, 0, 0, 0))
                            return real_stat(name, *args, **kwargs)
                        with patch.object(os, "stat", socket_stat):
                            with self.assertRaises(CaptureError): list_today(db)

    def test_parent_permissions_and_temp_create_failure_fail_closed(self):
        locked = self.root / "locked"; locked.mkdir(); db = locked / "capture.sqlite"
        original_mode = locked.stat().st_mode & 0o777; locked.chmod(0)
        try:
            with self.assertRaises(CaptureError): capture(db, "fixed", "key")
        finally:
            locked.chmod(original_mode)
        self.assertFalse(db.exists())
        original_open = os.open
        def fail_temp(name, *args, **kwargs):
            if isinstance(name, str) and name.startswith(".capture.sqlite."):
                raise PermissionError("injected temp create failure")
            return original_open(name, *args, **kwargs)
        with patch.object(os, "open", fail_temp):
            with self.assertRaises(CaptureError): capture(self.db, "fixed", "key")
        self.assertFalse(self.db.exists()); self.assertEqual(list(self.root.glob(".capture.sqlite.*")), [])

    def test_sidecars_fail_closed_by_entry_semantics(self):
        self.seed(); render_today(self.db); page = self.root / "today.html"
        for suffix in ("-journal", "-wal", "-shm"):
            sidecar = Path(str(self.db) + suffix); sidecar.write_bytes(b"fixed sidecar")
            before = self.db_hash()
            with self.assertRaises(CaptureError): list_today(self.db)
            self.assertTrue(page.exists())
            with self.assertRaises(CaptureError): render_today(self.db)
            self.assertFalse(page.exists()); self.assertEqual(self.db_hash(), before)
            sidecar.unlink(); render_today(self.db)

    def test_existing_invalid_db_rejected_before_capture_write(self):
        self.db.write_bytes(b"fixed corrupt sqlite")
        page = self.root / "today.html"; page.write_bytes(b"fixed page")
        before_db = self.db.read_bytes(); before_page = page.read_bytes()
        with self.assertRaises(CaptureError): capture(self.db, "fixed", "key")
        self.assertEqual(self.db.read_bytes(), before_db); self.assertEqual(page.read_bytes(), before_page)

    def test_capture_success_invalidates_stale_page_and_failure_restores_it(self):
        self.seed(); render_today(self.db); page = self.root / "today.html"
        stale = page.read_bytes(); before = self.db_hash()
        with self.assertRaises(CaptureError): capture(self.db, "fixed second", "second", inject_failure=True)
        self.assertEqual(self.db_hash(), before); self.assertEqual(page.read_bytes(), stale)
        capture(self.db, "fixed second", "second")
        self.assertFalse(page.exists()); self.assertEqual(len(list_today(self.db)), 2)

    def test_repeat_only_appends_repeat_audit_and_conflict_changes_nothing(self):
        first = self.seed(); before = self.db_hash()
        repeat = capture(self.db, "fixed <tag> & \"quote\" 中文\nline", "fixed-key")
        self.assertEqual(repeat["id"], first["id"]); self.assertNotEqual(self.db_hash(), before)
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM audit WHERE event='capture_repeat'").fetchone()[0], 1)
        before = self.db_hash()
        with self.assertRaises(CaptureError): capture(self.db, "different", "fixed-key")
        self.assertEqual(self.db_hash(), before)

    def test_html_is_escaped_unicode_newline_and_long_text_is_complete(self):
        text = "<script>fixed</script> & \"quote\" 中文\n" + "x" * 20000
        self.seed(text); render_today(self.db)
        html = (self.root / "today.html").read_text()
        self.assertNotIn("<script>fixed</script>", html)
        self.assertIn("&lt;script&gt;fixed&lt;/script&gt;", html)
        self.assertIn("中文\n", html); self.assertGreaterEqual(html.count("x"), 20000)

    def test_source_and_row_type_mutations_fail_whole_result(self):
        self.seed("fixed one", "one"); capture(self.db, "fixed two", "two"); render_today(self.db)
        page = self.root / "today.html"
        mutations = [
            ("source", "UPDATE captures SET source='external' WHERE idem_key='two'", True),
            ("uuid", "UPDATE captures SET id='not-a-uuid' WHERE idem_key='two'", False),
            ("time", "UPDATE captures SET created_at='2026-08-22T12:00:00' WHERE idem_key='two'", False),
            ("content-empty", "UPDATE captures SET content='' WHERE idem_key='two'", False),
            ("content-blob", "UPDATE captures SET content=x'0102' WHERE idem_key='two'", False),
            ("key-empty", "UPDATE captures SET idem_key='' WHERE idem_key='two'", False),
        ]
        for name, sql, ignore_check in mutations:
            with self.subTest(name=name):
                backup = self.db.read_bytes(); render_today(self.db)
                with sqlite3.connect(self.db) as conn:
                    if ignore_check: conn.execute("PRAGMA ignore_check_constraints=ON")
                    conn.execute(sql)
                changed = self.db.read_bytes()
                with self.assertRaises(CaptureError): list_today(self.db)
                with self.assertRaises(CaptureError): safe_snapshot(self.db)
                with self.assertRaises(CaptureError): render_today(self.db)
                self.assertFalse(page.exists()); self.assertEqual(self.db.read_bytes(), changed)
                self.db.write_bytes(backup)

    def _assert_source_variant_rejected(self, value, *, ignore_check=False):
        self.seed(); page = self.root / "today.html"; page.write_bytes(b"fixed stale")
        with sqlite3.connect(self.db) as conn:
            if ignore_check: conn.execute("PRAGMA ignore_check_constraints=ON")
            conn.execute("UPDATE captures SET source=?", (value,))
        changed = self.db.read_bytes()
        with self.assertRaises(CaptureError): list_today(self.db)
        with self.assertRaises(CaptureError): render_today(self.db)
        self.assertFalse(page.exists()); self.assertEqual(self.db.read_bytes(), changed)

    def test_source_other_independent_fixture(self):
        """source-other"""
        self._assert_source_variant_rejected("external", ignore_check=True)

    def test_source_case_independent_fixture(self):
        """source-case"""
        self._assert_source_variant_rejected("LOCAL_CAPTURE", ignore_check=True)

    def test_source_empty_independent_fixture(self):
        """source-empty"""
        self._assert_source_variant_rejected("", ignore_check=True)

    def test_source_null_independent_fixture(self):
        """source-null"""
        capture_id = "12345678-1234-4234-8234-123456789abc"
        created_at = "2026-08-22T12:00:00+00:00"
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE captures(id TEXT PRIMARY KEY,content TEXT NOT NULL,created_at TEXT NOT NULL,source TEXT,idem_key TEXT NOT NULL UNIQUE)")
            conn.execute("CREATE TABLE audit(id INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT NOT NULL,capture_id TEXT,created_at TEXT NOT NULL,detail TEXT NOT NULL)")
            conn.execute("INSERT INTO captures VALUES(?,?,?,?,?)", (capture_id, "fixed", created_at, None, "key"))
            conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_saved',?,?, 'local_capture')", (capture_id, created_at))
        page = self.root / "today.html"; page.write_bytes(b"fixed stale")
        with self.assertRaises(CaptureError): render_today(self.db)
        self.assertFalse(page.exists())

    def test_source_blob_independent_fixture(self):
        """source-blob"""
        self._assert_source_variant_rejected(sqlite3.Binary(b"local_capture"), ignore_check=True)

    def test_duplicate_id_independent_fixture(self):
        """duplicate-id"""
        self.seed(); page = self.root / "today.html"; page.write_bytes(b"fixed stale")
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE extra_duplicate_id(id TEXT)")
        with self.assertRaises(CaptureError): render_today(self.db)
        self.assertFalse(page.exists())

    def test_duplicate_idem_independent_fixture(self):
        """duplicate-idem"""
        self.seed(); page = self.root / "today.html"; page.write_bytes(b"fixed stale")
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE INDEX duplicate_idem_probe ON captures(idem_key)")
        with self.assertRaises(CaptureError): render_today(self.db)
        self.assertFalse(page.exists())

    def test_capture_post_commit_cleanup_failure_injected(self):
        """Candidate sidecar cleanup is completed before live publication."""
        self.seed(); render_today(self.db); page = self.root / "today.html"
        before_db = self.db.read_bytes(); before_page = page.read_bytes()
        def hook(point):
            if point == "candidate_close_sidecar":
                shadow = next(self.root.glob(".capture.sqlite.*.shadow"))
                (self.root / (shadow.name + "-journal")).write_bytes(b"fixed sidecar")
            if point.startswith("sidecar_cleanup_attempt_"):
                raise PermissionError("injected persistent cleanup failure")
        with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
            with self.assertRaises(CaptureError): capture(self.db, "fixed two", "two")
        self.assertEqual(self.db.read_bytes(), before_db); self.assertEqual(page.read_bytes(), before_page)
        self.assertEqual(list(self.root.glob(".capture.sqlite.*")), [])

    def test_capture_commit_failure_injected(self):
        """capture-commit-failure"""
        self.seed(); render_today(self.db); page = self.root / "today.html"
        before_db = self.db.read_bytes(); before_page = page.read_bytes()
        def hook(point):
            if point == "candidate_commit":
                raise sqlite3.OperationalError("injected capture commit failure")
        with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
            with self.assertRaises(CaptureError): capture(self.db, "fixed two", "two")
        self.assertEqual(self.db.read_bytes(), before_db); self.assertEqual(page.read_bytes(), before_page)

    def test_existing_capture_has_no_post_publish_connection_close(self):
        """All database connections are released before live publication."""
        self.seed(); render_today(self.db)
        sentinel = self.root / "sentinel.txt"
        sentinel.write_text("P3-097 fixed non-sensitive sentinel\n", encoding="utf-8")
        sentinel_before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        close_calls = []
        def hook(point):
            if point == "post_publish_connection_close":
                close_calls.append("raised")
                raise sqlite3.OperationalError("fixed post-publish close failure")
        with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
            result = capture(self.db, "fixed two", "two")
        self.assertEqual(result["status"], "saved")
        self.assertEqual(close_calls, [])
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 2)
        self.assertFalse((self.root / "today.html").exists())
        self.assertEqual(hashlib.sha256(sentinel.read_bytes()).hexdigest(), sentinel_before)
        self.assertEqual(list(self.root.glob(".today.html.*")), [])
        self.assertEqual(list(self.root.glob("capture.sqlite-*")), [])

    def test_repeat_has_no_post_publish_connection_close(self):
        """Repeat also releases every connection before live publication."""
        first = self.seed(); render_today(self.db); page = self.root / "today.html"
        page_before = page.read_bytes()
        sentinel = self.root / "sentinel.txt"
        sentinel.write_text("P3-097 fixed non-sensitive sentinel\n", encoding="utf-8")
        sentinel_before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        close_calls = []
        def hook(point):
            if point == "post_publish_connection_close":
                close_calls.append("raised")
                raise sqlite3.OperationalError("fixed repeat post-publish close failure")
        with patch.object(runtime, "_TEST_FAILURE_HOOK", hook):
            result = capture(self.db, "fixed <tag> & \"quote\" 中文\nline", "fixed-key")
        self.assertEqual(result["status"], "idempotent_repeat")
        self.assertEqual(result["id"], first["id"])
        self.assertEqual(close_calls, [])
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM audit WHERE event='capture_repeat'").fetchone()[0], 1)
        self.assertEqual(page.read_bytes(), page_before)
        self.assertEqual(hashlib.sha256(sentinel.read_bytes()).hexdigest(), sentinel_before)
        self.assertEqual(list(self.root.glob(".today.html.*")), [])
        self.assertEqual(list(self.root.glob("capture.sqlite-*")), [])

    def test_clear_commit_failure_injected(self):
        """clear-commit-failure"""
        self.seed(); render_today(self.db); before = self.db.read_bytes(); real_connect = sqlite3.connect
        class Proxy:
            def __init__(self, conn): self._conn = conn
            def __getattr__(self, name): return getattr(self._conn, name)
            def commit(self): raise sqlite3.OperationalError("injected clear commit failure")
            def close(self): self._conn.close()
        def connect(target, *args, **kwargs):
            conn = real_connect(target, *args, **kwargs)
            return Proxy(conn) if "mode=rw" in str(target) else conn
        with patch.object(runtime.sqlite3, "connect", connect):
            with self.assertRaises(CaptureError): delete_all(self.db, "DELETE")
        self.assertEqual(self.db.read_bytes(), before); self.assertFalse((self.root / "today.html").exists())

    def test_audit_mutations_fail_closed(self):
        statements = [
            "DELETE FROM audit WHERE event='capture_saved'",
            "UPDATE audit SET event='forged'",
            "UPDATE audit SET capture_id='00000000-0000-4000-8000-000000000000'",
            "UPDATE audit SET detail='forged'",
            "UPDATE audit SET created_at='no-time'",
            "UPDATE audit SET detail=x'00'",
            "INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_saved','00000000-0000-4000-8000-000000000000','2026-08-22T12:00:00+00:00','local_capture')",
        ]
        for statement in statements:
            with self.subTest(statement=statement):
                if self.db.exists(): self.db.unlink()
                self.seed(); render_today(self.db); page = self.root / "today.html"
                with sqlite3.connect(self.db) as conn: conn.execute(statement)
                changed = self.db.read_bytes()
                with self.assertRaises(CaptureError): render_today(self.db)
                self.assertFalse(page.exists()); self.assertEqual(self.db.read_bytes(), changed)

    def test_extra_schema_objects_and_shape_changes_rejected(self):
        mutations = [
            "CREATE INDEX extra_idx ON captures(content)",
            "CREATE TRIGGER extra_trigger AFTER INSERT ON captures BEGIN SELECT 1; END",
            "CREATE TABLE shadow(value TEXT)",
        ]
        for statement in mutations:
            with self.subTest(statement=statement):
                if self.db.exists(): self.db.unlink()
                self.seed(); page = self.root / "today.html"; page.write_bytes(b"fixed stale")
                with sqlite3.connect(self.db) as conn: conn.execute(statement)
                before = self.db.read_bytes()
                with self.assertRaises(CaptureError): render_today(self.db)
                self.assertFalse(page.exists()); self.assertEqual(self.db.read_bytes(), before)

    def test_read_entries_never_create_missing_db_or_sidecar(self):
        for entry in (list_today, safe_snapshot, render_today):
            with self.subTest(entry=entry):
                page = self.root / "today.html"; page.write_bytes(b"fixed stale")
                with self.assertRaises(CaptureError): entry(self.db)
                self.assertFalse(self.db.exists()); self.assertEqual(list(self.root.glob("capture.sqlite*")), [])
                if entry is render_today: self.assertFalse(page.exists())
                else: self.assertTrue(page.exists()); page.unlink()

    def test_render_replace_failure_keeps_valid_page_and_cleans_temp(self):
        self.seed(); render_today(self.db); page = self.root / "today.html"; before = page.read_bytes()
        with patch.object(os, "replace", side_effect=OSError("injected replace")):
            with self.assertRaises(CaptureError): render_today(self.db)
        self.assertEqual(page.read_bytes(), before); self.assertEqual(list(self.root.glob(".today.html.*")), [])

    def test_render_fsync_failure_keeps_valid_page_and_cleans_temp(self):
        self.seed(); render_today(self.db); page = self.root / "today.html"; before = page.read_bytes()
        with patch.object(os, "fsync", side_effect=OSError("injected fsync")):
            with self.assertRaises(CaptureError): render_today(self.db)
        self.assertEqual(page.read_bytes(), before); self.assertEqual(list(self.root.glob(".today.html.*")), [])

    def test_clear_untrusted_db_invalidates_page_without_db_change(self):
        self.db.write_bytes(b"fixed corrupt"); page = self.root / "today.html"; page.write_bytes(b"fixed stale")
        before = self.db.read_bytes()
        with self.assertRaises(CaptureError): delete_all(self.db, "DELETE")
        self.assertFalse(page.exists()); self.assertEqual(self.db.read_bytes(), before)

    def test_clear_transaction_failure_rolls_back_and_page_stays_invalidated(self):
        self.seed(); render_today(self.db); before = self.db_hash()
        original = runtime._audit
        def fail_clear(conn, event, capture_id, detail):
            if event == "captures_cleared": raise sqlite3.OperationalError("injected clear audit")
            return original(conn, event, capture_id, detail)
        with patch("local_capture._audit", side_effect=fail_clear):
            with self.assertRaises(CaptureError): delete_all(self.db, "DELETE")
        self.assertEqual(self.db_hash(), before); self.assertFalse((self.root / "today.html").exists())
        self.assertEqual(len(list_today(self.db)), 1)

    def test_full_lifecycle_across_fresh_processes(self):
        cli = Path(__file__).resolve().parents[1] / "scripts" / "operator_cli.py"
        def call(*args):
            return subprocess.run([sys.executable, "-B", str(cli), "--db", str(self.db), *args],
                                  text=True, capture_output=True)
        self.assertEqual(call("capture", "--text", "fixed", "--key", "one").returncode, 0)
        self.assertEqual(call("capture", "--text", "fixed", "--key", "one").returncode, 0)
        self.assertEqual(call("today").returncode, 0)
        self.assertEqual(call("render").returncode, 0)
        self.assertEqual(call("capture", "--text", "fixed two", "--key", "two").returncode, 0)
        self.assertFalse((self.root / "today.html").exists())
        self.assertEqual(call("render").returncode, 0)
        self.assertEqual(call("clear", "--confirmation", "DELETE").returncode, 0)
        self.assertEqual(call("render").returncode, 2)
        self.assertFalse((self.root / "today.html").exists())


if __name__ == "__main__": unittest.main()
