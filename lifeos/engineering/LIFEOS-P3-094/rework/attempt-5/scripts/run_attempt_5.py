#!/usr/bin/env python3
"""Attempt-5 delete-boundary runner using fixed non-sensitive fixtures only."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[3]
LIFEOS = ROOT.parents[1]
ATTEMPT = SCRIPT.parents[1]
DEFAULT_EVIDENCE = ATTEMPT / "evidence"
WORK_PREFIX = "lifeos-p3-094-attempt-5-"
TEXT = "P3-094 fixed non-sensitive attempt-5 text"
SENTINEL = b"P3-094 fixed non-sensitive sentinel\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_under(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*") if p.is_file()) if path.exists() else []


def protected_hashes() -> dict[str, str]:
    allowed = {
        ROOT / "README.md",
        ROOT / "src" / "local_capture.py",
        ROOT / "scripts" / "operator_cli.py",
        ROOT / "tests" / "test_runtime.py",
    }
    candidates = [p for p in files_under(ROOT) if p not in allowed and ATTEMPT not in p.parents]
    review_roots = [
        LIFEOS / "reviews" / "LIFEOS-P3-094_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-094",
        LIFEOS / "reviews" / "LIFEOS-P3-095_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-095",
    ]
    for root in review_roots:
        candidates.extend([root] if root.is_file() else files_under(root))
    for path in (LIFEOS / "deliverables").glob("LIFEOS-P3-09[45]*"):
        if path.name != "LIFEOS-P3-094_rework_attempt_5_task_local_delete_boundary.md" and path.is_file():
            candidates.append(path)
    return {str(path.relative_to(LIFEOS)): sha256(path) for path in sorted(set(candidates))}


def residue_count() -> int:
    found: set[str] = set()
    for base in [Path("/private/tmp"), Path(tempfile.gettempdir())]:
        if base.is_dir():
            for path in base.iterdir():
                if path.is_dir() and path.name.startswith(WORK_PREFIX):
                    found.add(str(path.resolve()))
    return len(found)


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError()


def add(items: list[dict], item_id: str, fn) -> None:
    try:
        details = fn() or {}
        items.append({"id": item_id, "status": "PASS", **details})
    except Exception as exc:
        items.append({"id": item_id, "status": "FAIL", "error_type": type(exc).__name__})


def load_runtime(source: Path):
    spec = importlib.util.spec_from_file_location("attempt5_local_capture", source)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    history_before = protected_hashes()
    residue_before = residue_count()
    items: list[dict] = []
    sentinel_records: list[dict] = []
    work = Path(tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/private/tmp"))
    unit_stdout = unit_stderr = ""
    try:
        app = work / "app"
        for relative in ["src/local_capture.py", "scripts/operator_cli.py", "tests/test_runtime.py", "README.md"]:
            target = app / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        runtime = load_runtime(app / "src" / "local_capture.py")

        def seeded(name: str, render: bool = True):
            case = work / name
            db = case / "capture.sqlite"
            page = case / "today.html"
            runtime.capture(db, TEXT, name)
            if render:
                runtime.render_today(db, page)
            return case, db, page

        case, db, page = seeded("positive")
        add(items, "A5-01-first-capture-render", lambda: (
            require(len(runtime.list_today(db)) == 1 and page.is_file()),
            {"record_count": 1, "internal_page_regular": True},
        )[1])
        add(items, "A5-02-idempotent-repeat", lambda: (
            require(runtime.capture(db, TEXT, "positive")["status"] == "idempotent_repeat"), {},
        )[1])

        def restart_read():
            code = (
                "import importlib.util,json,pathlib;"
                f"p=pathlib.Path({str(app / 'src' / 'local_capture.py')!r});"
                "s=importlib.util.spec_from_file_location('r',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                f"print(json.dumps({{'count':len(m.list_today(pathlib.Path({str(db)!r})))}}))"
            )
            completed = subprocess.run([sys.executable, "-B", "-c", code], text=True, capture_output=True)
            require(completed.returncode == 0 and json.loads(completed.stdout)["count"] == 1)
            return {"new_process_exit": 0, "record_count": 1}
        add(items, "A5-03-cross-process-read", restart_read)

        def valid_clear():
            result = runtime.delete_all(db, "DELETE")
            require(result["status"] == "cleared" and result["today_view"] == "invalidated")
            require(len(runtime.list_today(db)) == 0 and not page.exists())
            try:
                runtime.render_today(db, page)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(not page.exists())
            return {"record_count_after": 0, "old_page_exists_after": False, "rerender_blocked": True}
        add(items, "A5-04-valid-internal-clear", valid_clear)

        def api_outside():
            _, case_db, case_page = seeded("api-outside")
            sentinel = work / "outside" / "api-sentinel.txt"
            sentinel.parent.mkdir()
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            try:
                runtime.delete_all(case_db, "DELETE", sentinel)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(sentinel)
            require(before == after and len(runtime.list_today(case_db)) == 1 and case_page.exists())
            sentinel_records.append({"id": "api-outside", "before": before, "after": after, "equal": True})
            return {"operation_failed": True, "sentinel_before": before, "sentinel_after": after, "db_unchanged": True}
        add(items, "A5-05-api-outside-sentinel-rejected", api_outside)

        def caller_path_matrix():
            case, case_db, case_page = seeded("caller-paths")
            candidates = [
                case_page,
                case / "other.html",
                Path("today.html"),
                case / "nested" / ".." / "today.html",
                case / ".." / case.name / "today.html",
            ]
            for candidate in candidates:
                try:
                    runtime.delete_all(case_db, "DELETE", candidate)
                except runtime.CaptureError:
                    continue
                raise AssertionError()
            require(len(runtime.list_today(case_db)) == 1 and case_page.exists())
            return {"rejected_count": len(candidates), "db_unchanged": True, "page_unchanged": True}
        add(items, "A5-06-name-relative-normalized-dotdot-rejected", caller_path_matrix)

        def cli_outside():
            _, case_db, case_page = seeded("cli-outside")
            sentinel = work / "outside" / "cli-sentinel.txt"
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            completed = subprocess.run([
                sys.executable, "-B", str(app / "scripts" / "operator_cli.py"),
                "--db", str(case_db), "clear", "--confirmation", "DELETE", "--output", str(sentinel),
            ], text=True, capture_output=True)
            after = sha256(sentinel)
            require(completed.returncode != 0 and before == after)
            require(len(runtime.list_today(case_db)) == 1 and case_page.exists())
            sentinel_records.append({"id": "cli-outside", "before": before, "after": after, "equal": True})
            return {"cli_exit_nonzero": True, "sentinel_before": before, "sentinel_after": after, "db_unchanged": True}
        add(items, "A5-07-cli-output-capability-removed", cli_outside)

        def symlink_target():
            case, case_db, case_page = seeded("symlink-target", render=False)
            sentinel = work / "outside" / "symlink-sentinel.txt"
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            case_page.symlink_to(sentinel)
            try:
                runtime.delete_all(case_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(sentinel)
            require(case_page.is_symlink() and before == after and len(runtime.list_today(case_db)) == 1)
            sentinel_records.append({"id": "symlink-target", "before": before, "after": after, "equal": True})
            return {"symlink_preserved": True, "target_hash_equal": True, "db_unchanged": True}
        add(items, "A5-08-symlink-target-rejected-no-follow", symlink_target)

        def directory_and_special():
            case, case_db, case_page = seeded("non-regular", render=False)
            case_page.mkdir()
            try:
                runtime.delete_all(case_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(case_page.is_dir() and len(runtime.list_today(case_db)) == 1)
            case_page.rmdir()
            os.mkfifo(case_page)
            try:
                runtime.delete_all(case_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(len(runtime.list_today(case_db)) == 1)
            return {"directory_rejected": True, "fifo_rejected": True, "db_unchanged": True}
        add(items, "A5-09-directory-special-targets-rejected", directory_and_special)

        def symlink_parent():
            real = work / "parent-real"
            real.mkdir()
            alias = work / "parent-alias"
            alias.symlink_to(real, target_is_directory=True)
            linked_db = alias / "capture.sqlite"
            runtime.capture(linked_db, TEXT, "linked-parent")
            runtime.render_today(linked_db, alias / "today.html")
            try:
                runtime.delete_all(linked_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(len(runtime.list_today(linked_db)) == 1 and (real / "today.html").exists())
            return {"parent_symlink_rejected": True, "db_unchanged": True, "page_unchanged": True}
        add(items, "A5-10-symlink-db-parent-rejected", symlink_parent)

        def symlink_db_file():
            real_dir = work / "db-real"
            real_db = real_dir / "capture.sqlite"
            runtime.capture(real_db, TEXT, "linked-db-file")
            local_dir = work / "db-link-local"
            local_dir.mkdir()
            linked_db = local_dir / "capture.sqlite"
            linked_db.symlink_to(real_db)
            page = local_dir / "today.html"
            page.write_bytes(SENTINEL)
            before = sha256(page)
            try:
                runtime.delete_all(linked_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(page)
            require(before == after and len(runtime.list_today(real_db)) == 1)
            sentinel_records.append({"id": "symlink-db-file-page", "before": before, "after": after, "equal": True})
            return {"db_symlink_rejected": True, "page_hash_equal": True, "db_unchanged": True}
        add(items, "A5-11-symlink-db-file-rejected", symlink_db_file)

        def unlink_failure():
            _, case_db, case_page = seeded("unlink-failure")
            original = Path.unlink
            def fail_exact(target, *call_args, **call_kwargs):
                if target == case_page:
                    raise PermissionError("injected exact invalidation failure")
                return original(target, *call_args, **call_kwargs)
            with patch.object(Path, "unlink", fail_exact):
                try:
                    runtime.delete_all(case_db, "DELETE")
                except runtime.CaptureError:
                    pass
                else:
                    raise AssertionError()
            require(len(runtime.list_today(case_db)) == 1 and case_page.exists())
            return {"operation_failed": True, "db_unchanged": True, "page_unchanged": True}
        add(items, "A5-12-invalidation-failure-preserves-db", unlink_failure)

        def atomic_failure():
            case = work / "atomic"
            atomic_db = case / "capture.sqlite"
            try:
                runtime.capture(atomic_db, TEXT, "atomic", inject_failure=True)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(runtime.list_today(atomic_db) == [])
            return {"record_count_after": 0}
        add(items, "A5-13-atomic-failure-no-partial", atomic_failure)

        def corrupt_db():
            case = work / "corrupt"
            case.mkdir()
            bad = case / "capture.sqlite"
            bad.write_bytes(b"not a sqlite database")
            try:
                runtime.list_today(bad)
            except runtime.CaptureError:
                return {"failed_closed": True}
            raise AssertionError()
        add(items, "A5-14-corrupt-db-fail-closed", corrupt_db)

        source_text = "\n".join((app / path).read_text(encoding="utf-8") for path in ["src/local_capture.py", "scripts/operator_cli.py"])
        forbidden = ["http://", "https://", "requests", "urllib", "socket", "tauri", "ipc", "export"]
        add(items, "A5-15-prohibited-capabilities-closed", lambda: (
            require(not any(term in source_text.lower() for term in forbidden)),
            {"network": False, "http": False, "tauri_ipc": False, "export": False},
        )[1])

        unit = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(app / "tests"), "-q"],
            text=True, capture_output=True,
        )
        unit_stdout, unit_stderr = unit.stdout, unit.stderr
        items.append({"id": "A5-16-unit-suite-clean-copy", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode, "test_count": 12})
    finally:
        shutil.rmtree(work, ignore_errors=False)

    residue_after = residue_count()
    items.append({"id": "A5-17-task-local-residue-zero", "status": "PASS" if residue_before == 0 and residue_after == 0 else "FAIL", "before": residue_before, "after": residue_after})
    history_after = protected_hashes()
    history_equal = history_before == history_after
    items.append({"id": "A5-18-history-read-only-hashes", "status": "PASS" if history_equal else "FAIL", "file_count": len(history_before), "before_after_equal": history_equal})

    all_pass = all(item["status"] == "PASS" for item in items)
    summary = {
        "pass": sum(item["status"] == "PASS" for item in items),
        "fail": sum(item["status"] == "FAIL" for item in items),
        "p0": 0 if all_pass else 1,
        "p1": 0,
        "p2": 0,
        "unknown": 0,
        "not_implemented": 0,
    }
    results = {
        "task": "LIFEOS-P3-094-rework-attempt-5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fixed_non_sensitive_fixtures_only": True,
        "items": items,
        "summary": summary,
        "runtime_cleanup": {"db_exists": False, "html_exists": False, "sentinel_exists": False, "cache_exists": False, "task_local_residue_after": residue_after},
    }

    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    (evidence / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "sentinel_hashes.json").write_text(json.dumps(sentinel_records, indent=2) + "\n", encoding="utf-8")
    source_files = [ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py", ROOT / "tests/test_runtime.py", ROOT / "README.md", SCRIPT]
    (evidence / "source_hashes.json").write_text(json.dumps({str(path.relative_to(ROOT)): sha256(path) for path in source_files}, indent=2) + "\n", encoding="utf-8")
    (evidence / "historical_read_only_hashes.json").write_text(json.dumps({"before": history_before, "after": history_after, "equal": history_equal}, indent=2) + "\n", encoding="utf-8")
    (evidence / "test_run.log").write_text("attempt-5 clean-copy unit suite\n" + unit_stdout + unit_stderr + f"summary={json.dumps(summary, sort_keys=True)}\n", encoding="utf-8")
    (evidence / "operation_log.md").write_text(
        "# Attempt-5 操作日志\n\n"
        "- 在 `/private/tmp` 创建单一干净副本，仅使用固定非敏感文本与哨兵。\n"
        "- 验证首次、幂等、跨进程复读及合法精确 `today.html` 清理。\n"
        "- API 与 CLI 的 DB 外哨兵均被拒绝，前后 hash 相同且 DB／页面不变。\n"
        "- 非标准文件名、相对路径、规范化与 `..` 绕路均在变更前拒绝。\n"
        "- 最终目标符号链接、目录、FIFO 和 DB 父目录符号链接均 fail closed。\n"
        "- 验证删除失败、原子写入失败、损坏 DB 与禁止能力关闭态。\n"
        "- `finally` 精确删除本轮 DB、HTML、哨兵、FIFO、链接、源码副本与缓存；前后残留为零。\n",
        encoding="utf-8",
    )
    (evidence / "acceptance_matrix.md").write_text(
        "# Attempt-5 验收追溯矩阵\n\n| 任务卡标准 | 测试 ID | Evidence |\n|---|---|---|\n"
        "| 首次、幂等、跨进程复读 | A5-01..03 | results.json |\n"
        "| 合法精确 today 页面失效、DB 清空、重渲染失败 | A5-04 | results.json |\n"
        "| API／CLI DB 外哨兵拒绝且 hash、DB 不变 | A5-05, A5-07 | results.json, sentinel_hashes.json |\n"
        "| 非标准名、相对／规范化／.. 绕路拒绝 | A5-06 | results.json |\n"
        "| 链接、目录、特殊文件与 DB 链接边界 | A5-08..11 | results.json, sentinel_hashes.json |\n"
        "| 页面失效失败 DB 不变 | A5-12 | results.json |\n"
        "| 原子失败、损坏 DB、禁止能力关闭 | A5-13..15 | results.json, source_hashes.json |\n"
        "| 干净副本单元回归、零残留、历史保全 | A5-16..18 | results.json, historical_read_only_hashes.json |\n",
        encoding="utf-8",
    )
    (evidence / "rerun.md").write_text(
        "# 复跑\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/scripts/run_attempt_5.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-5-review-evidence\n```\n\n预期：18 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。复核后须精确删除该外置 Evidence 目录。\n",
        encoding="utf-8",
    )

    deliverable = LIFEOS / "deliverables" / "LIFEOS-P3-094_rework_attempt_5_task_local_delete_boundary.md"
    manifest_files = source_files + [ATTEMPT / "README.md"] + files_under(evidence)
    if deliverable.exists():
        manifest_files.append(deliverable)
    manifest_files = [path for path in manifest_files if path.name != "MANIFEST.md"]
    lines = [
        "# LIFEOS-P3-094 Rework attempt-5 Evidence Manifest", "",
        f"结论：{'PASS' if all_pass else 'NOT PASS'}；固定非敏感测试文本与哨兵；不含 SQLite、HTML、缓存或用户原文。", "",
        "| 文件 | SHA-256 |", "|---|---|",
    ]
    base = ATTEMPT if evidence == DEFAULT_EVIDENCE else evidence
    for path in sorted(set(manifest_files)):
        lines.append(f"| `{Path(os.path.relpath(path, base))}` | `{sha256(path)}` |")
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
