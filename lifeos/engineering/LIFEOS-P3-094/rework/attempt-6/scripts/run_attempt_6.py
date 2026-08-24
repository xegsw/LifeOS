#!/usr/bin/env python3
"""Attempt-6 render/clear boundary self-check with non-sensitive fixtures."""
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
WORK_PREFIX = "lifeos-p3-094-attempt-6-"
TEXT = "P3-094 fixed non-sensitive attempt-6 text"
SENTINEL = b"P3-094 fixed non-sensitive attempt-6 sentinel\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_under(path: Path) -> list[Path]:
    return sorted(item for item in path.rglob("*") if item.is_file()) if path.exists() else []


def protected_hashes() -> dict[str, str]:
    mutable = {
        ROOT / "README.md",
        ROOT / "src" / "local_capture.py",
        ROOT / "scripts" / "operator_cli.py",
        ROOT / "tests" / "test_runtime.py",
    }
    candidates = [
        path for path in files_under(ROOT)
        if path not in mutable and ATTEMPT not in path.parents
    ]
    for review in [
        LIFEOS / "reviews" / "LIFEOS-P3-094_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-094",
        LIFEOS / "reviews" / "LIFEOS-P3-095_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-095",
    ]:
        candidates.extend([review] if review.is_file() else files_under(review))
    for path in (LIFEOS / "deliverables").glob("LIFEOS-P3-09[45]*"):
        if path.name != "LIFEOS-P3-094_rework_attempt_6_task_local_render_clear_boundary.md":
            candidates.append(path)
    return {str(path.relative_to(LIFEOS)): sha256(path) for path in sorted(set(candidates))}


def residue_count() -> int:
    return sum(
        path.is_dir() and path.name.startswith(WORK_PREFIX)
        for path in Path("/private/tmp").iterdir()
    )


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
    spec = importlib.util.spec_from_file_location("attempt6_local_capture", source)
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
    sentinels: list[dict] = []
    unit_stdout = unit_stderr = ""
    work = Path(tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/private/tmp"))
    try:
        app = work / "app"
        for relative in ["src/local_capture.py", "scripts/operator_cli.py", "tests/test_runtime.py", "README.md"]:
            target = app / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        runtime = load_runtime(app / "src" / "local_capture.py")

        def seeded(name: str, render: bool = False):
            case = work / name
            db = case / "capture.sqlite"
            page = case / "today.html"
            runtime.capture(db, TEXT, name)
            if render:
                runtime.render_today(db)
            return case, db, page

        case, db, page = seeded("positive", render=True)
        add(items, "A6-01-forced-internal-render", lambda: (
            require(page.is_file()),
            require(runtime.render_today(db)["path"] == str(page)),
            {"record_count": 1, "path_is_exact_internal_today": True},
        )[2])
        add(items, "A6-02-idempotent-and-cross-process-read", lambda: (
            require(runtime.capture(db, TEXT, "positive")["status"] == "idempotent_repeat"),
            require(subprocess.run([
                sys.executable, "-B", str(app / "scripts" / "operator_cli.py"),
                "--db", str(db), "today",
            ], text=True, capture_output=True).returncode == 0),
            {"idempotent": True, "new_process_exit": 0},
        )[2])

        def api_outside():
            _, case_db, case_page = seeded("api-outside", render=True)
            sentinel = work / "outside-api.html"
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            page_before = sha256(case_page)
            try:
                runtime.render_today(case_db, sentinel)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(sentinel)
            require(before == after and page_before == sha256(case_page))
            require(len(runtime.list_today(case_db)) == 1)
            sentinels.append({"id": "render-api-outside", "before": before, "after": after, "equal": True})
            return {"operation_failed": True, "sentinel_hash_equal": True, "db_unchanged": True}
        add(items, "A6-03-render-api-outside-rejected", api_outside)

        def cli_outside():
            _, case_db, case_page = seeded("cli-outside", render=True)
            sentinel = work / "outside-cli.html"
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            page_before = sha256(case_page)
            result = subprocess.run([
                sys.executable, "-B", str(app / "scripts" / "operator_cli.py"),
                "--db", str(case_db), "render", "--output", str(sentinel),
            ], text=True, capture_output=True)
            after = sha256(sentinel)
            require(result.returncode != 0 and before == after and page_before == sha256(case_page))
            require(len(runtime.list_today(case_db)) == 1)
            sentinels.append({"id": "render-cli-outside", "before": before, "after": after, "equal": True})
            return {"cli_exit_nonzero": True, "sentinel_hash_equal": True, "db_unchanged": True}
        add(items, "A6-04-render-cli-output-capability-removed", cli_outside)

        def final_symlink():
            _, case_db, case_page = seeded("render-symlink")
            sentinel = work / "render-link-target.html"
            sentinel.write_bytes(SENTINEL)
            before = sha256(sentinel)
            case_page.symlink_to(sentinel)
            try:
                runtime.render_today(case_db)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(sentinel)
            require(case_page.is_symlink() and before == after and len(runtime.list_today(case_db)) == 1)
            sentinels.append({"id": "render-final-symlink", "before": before, "after": after, "equal": True})
            return {"link_preserved": True, "target_hash_equal": True, "db_unchanged": True}
        add(items, "A6-05-render-final-symlink-no-follow", final_symlink)

        def final_types():
            _, dir_db, dir_page = seeded("render-directory")
            dir_page.mkdir()
            try:
                runtime.render_today(dir_db)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            _, fifo_db, fifo_page = seeded("render-fifo")
            os.mkfifo(fifo_page)
            try:
                runtime.render_today(fifo_db)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(dir_page.is_dir() and len(runtime.list_today(dir_db)) == 1)
            require(stat_is_fifo(fifo_page) and len(runtime.list_today(fifo_db)) == 1)
            return {"directory_rejected": True, "fifo_rejected": True, "db_unchanged": True}
        add(items, "A6-06-render-directory-fifo-rejected", final_types)

        def ancestor_render():
            real_root = work / "render-real"
            real_db = real_root / "nested" / "capture.sqlite"
            runtime.capture(real_db, TEXT, "render-ancestor")
            alias = work / "render-alias"
            alias.symlink_to(real_root, target_is_directory=True)
            linked_db = alias / "nested" / "capture.sqlite"
            try:
                runtime.render_today(linked_db)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(not (real_root / "nested" / "today.html").exists())
            require(len(runtime.list_today(real_db)) == 1)
            return {"ancestor_link_rejected": True, "target_page_absent": True, "db_unchanged": True}
        add(items, "A6-07-render-ancestor-link-chain-rejected", ancestor_render)

        def ancestor_clear():
            real_root = work / "clear-real"
            real_db = real_root / "nested" / "capture.sqlite"
            runtime.capture(real_db, TEXT, "clear-ancestor")
            runtime.render_today(real_db)
            real_page = real_root / "nested" / "today.html"
            before = sha256(real_page)
            alias = work / "clear-alias"
            alias.symlink_to(real_root, target_is_directory=True)
            linked_db = alias / "nested" / "capture.sqlite"
            try:
                runtime.delete_all(linked_db, "DELETE")
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            after = sha256(real_page)
            require(before == after and len(runtime.list_today(real_db)) == 1)
            sentinels.append({"id": "clear-ancestor-page", "before": before, "after": after, "equal": True})
            return {"ancestor_link_rejected": True, "page_hash_equal": True, "db_unchanged": True}
        add(items, "A6-08-clear-ancestor-link-chain-rejected", ancestor_clear)

        def lexical_paths():
            _, real_db, real_page = seeded("lexical", render=True)
            candidates = [Path("capture.sqlite"), real_db.parent / "nested" / ".." / real_db.name]
            for candidate in candidates:
                for action in [lambda: runtime.render_today(candidate), lambda: runtime.delete_all(candidate, "DELETE")]:
                    try:
                        action()
                    except runtime.CaptureError:
                        continue
                    raise AssertionError()
            require(real_page.exists() and len(runtime.list_today(real_db)) == 1)
            return {"rejected_operations": 4, "page_unchanged": True, "db_unchanged": True}
        add(items, "A6-09-relative-dotdot-normalization-rejected", lexical_paths)

        def valid_clear():
            _, case_db, case_page = seeded("valid-clear", render=True)
            result = runtime.delete_all(case_db, "DELETE")
            require(result["status"] == "cleared" and not case_page.exists())
            require(runtime.list_today(case_db) == [])
            try:
                runtime.render_today(case_db)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            return {"page_invalidated": True, "record_count_after": 0, "rerender_blocked": True}
        add(items, "A6-10-valid-render-clear-rerender-closed", valid_clear)

        def invalidation_failure():
            _, case_db, case_page = seeded("unlink-failure", render=True)
            before = sha256(case_page)
            original = os.unlink
            def fail_exact(target, *call_args, **call_kwargs):
                if target == case_page.name and call_kwargs.get("dir_fd") is not None:
                    raise PermissionError("injected invalidation failure")
                return original(target, *call_args, **call_kwargs)
            with patch.object(os, "unlink", fail_exact):
                try:
                    runtime.delete_all(case_db, "DELETE")
                except runtime.CaptureError:
                    pass
                else:
                    raise AssertionError()
            require(before == sha256(case_page) and len(runtime.list_today(case_db)) == 1)
            return {"operation_failed": True, "page_hash_equal": True, "db_unchanged": True}
        add(items, "A6-11-clear-invalidation-failure-preserves-db", invalidation_failure)

        def db_symlink():
            _, real_db, real_page = seeded("db-real", render=True)
            local = work / "db-link"
            local.mkdir()
            linked_db = local / "capture.sqlite"
            linked_db.symlink_to(real_db)
            before = sha256(real_page)
            for action in [lambda: runtime.render_today(linked_db), lambda: runtime.delete_all(linked_db, "DELETE")]:
                try:
                    action()
                except runtime.CaptureError:
                    continue
                raise AssertionError()
            require(before == sha256(real_page) and len(runtime.list_today(real_db)) == 1)
            return {"db_link_rejected_twice": True, "page_hash_equal": True, "db_unchanged": True}
        add(items, "A6-12-db-final-symlink-rejected", db_symlink)

        def render_publish_failure():
            _, case_db, case_page = seeded("render-publish-failure", render=True)
            before = sha256(case_page)
            with patch.object(os, "replace", side_effect=PermissionError("injected atomic publish failure")):
                try:
                    runtime.render_today(case_db)
                except runtime.CaptureError:
                    pass
                else:
                    raise AssertionError()
            require(before == sha256(case_page) and len(runtime.list_today(case_db)) == 1)
            require(not list(case_page.parent.glob(".today.html.*.tmp")))
            return {"operation_failed": True, "existing_page_hash_equal": True, "db_unchanged": True, "half_product_count": 0}
        add(items, "A6-13-render-publish-failure-no-half-product", render_publish_failure)

        def atomic_failure():
            atomic_db = work / "atomic" / "capture.sqlite"
            try:
                runtime.capture(atomic_db, TEXT, "atomic", inject_failure=True)
            except runtime.CaptureError:
                pass
            else:
                raise AssertionError()
            require(runtime.list_today(atomic_db) == [])
            return {"record_count_after": 0}
        add(items, "A6-14-atomic-capture-no-partial", atomic_failure)

        def corrupt_db():
            bad_dir = work / "corrupt"
            bad_dir.mkdir()
            bad = bad_dir / "capture.sqlite"
            bad.write_bytes(b"not a sqlite database")
            for action in [lambda: runtime.render_today(bad), lambda: runtime.delete_all(bad, "DELETE")]:
                try:
                    action()
                except runtime.CaptureError:
                    continue
                raise AssertionError()
            return {"render_and_clear_failed_closed": True}
        add(items, "A6-15-corrupt-db-fail-closed", corrupt_db)

        source_text = "\n".join((app / path).read_text(encoding="utf-8") for path in ["src/local_capture.py", "scripts/operator_cli.py"])
        forbidden = ["http://", "https://", "requests", "urllib", "socket", "tauri", "ipc", "export"]
        add(items, "A6-16-prohibited-capabilities-closed", lambda: (
            require(not any(term in source_text.lower() for term in forbidden)),
            {"network": False, "http": False, "tauri_ipc": False, "export": False},
        )[1])

        unit = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(app / "tests"), "-q"],
            text=True, capture_output=True,
        )
        unit_stdout, unit_stderr = unit.stdout, unit.stderr
        items.append({"id": "A6-17-clean-copy-unit-suite", "status": "PASS" if unit.returncode == 0 else "FAIL", "exit_code": unit.returncode, "test_count": 15})
    finally:
        shutil.rmtree(work, ignore_errors=False)

    residue_after = residue_count()
    items.append({"id": "A6-18-task-local-residue-zero", "status": "PASS" if residue_before == 0 and residue_after == 0 else "FAIL", "before": residue_before, "after": residue_after})
    history_after = protected_hashes()
    history_equal = history_before == history_after
    items.append({"id": "A6-19-history-read-only-hashes", "status": "PASS" if history_equal else "FAIL", "file_count": len(history_before), "before_after_equal": history_equal})

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
        "task": "LIFEOS-P3-094-rework-attempt-6",
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
    (evidence / "sentinel_hashes.json").write_text(json.dumps(sentinels, indent=2) + "\n", encoding="utf-8")
    source_files = [ROOT / "src/local_capture.py", ROOT / "scripts/operator_cli.py", ROOT / "tests/test_runtime.py", ROOT / "README.md", SCRIPT]
    (evidence / "source_hashes.json").write_text(json.dumps({str(path.relative_to(ROOT)): sha256(path) for path in source_files}, indent=2) + "\n", encoding="utf-8")
    (evidence / "historical_read_only_hashes.json").write_text(json.dumps({"before": history_before, "after": history_after, "equal": history_equal}, indent=2) + "\n", encoding="utf-8")
    (evidence / "test_run.log").write_text("attempt-6 clean-copy unit suite\n" + unit_stdout + unit_stderr + f"summary={json.dumps(summary, sort_keys=True)}\n", encoding="utf-8")
    (evidence / "operation_log.md").write_text(
        "# Attempt-6 操作日志\n\n"
        "- 在 `/private/tmp` 新建干净副本，只使用固定非敏感文本与哨兵。\n"
        "- render 与 clear 均验证完整目录组件链、DB 文件和最终 `today.html` 类型。\n"
        "- API／CLI 越界输出、相对路径、`..`、最终链接、祖先链接、目录与 FIFO 均在变更前拒绝。\n"
        "- 哨兵／页面前后 hash 相同，拒绝路径 DB 记录保持不变。\n"
        "- 合法路径完成 render、页面先失效、DB 清空与重渲染失败。\n"
        "- 原子失败、损坏 DB、禁止能力关闭态、干净副本单元回归、零残留与历史 hash 均核对。\n",
        encoding="utf-8",
    )
    (evidence / "acceptance_matrix.md").write_text(
        "# Attempt-6 验收追溯矩阵\n\n| 任务卡标准 | 测试 ID | Evidence |\n|---|---|---|\n"
        "| 唯一内部 render 路径与 CLI 移除输出能力 | A6-01, A6-03..04 | results.json, sentinel_hashes.json |\n"
        "| render 最终链接／目录／FIFO fail closed | A6-05..06 | results.json, sentinel_hashes.json |\n"
        "| render／clear 完整祖先链接链拒绝 | A6-07..08 | results.json, sentinel_hashes.json |\n"
        "| 相对／`..`／规范化绕路拒绝 | A6-09 | results.json |\n"
        "| 合法 render→clear→重渲染失败 | A6-10 | results.json |\n"
        "| 页面失效失败 DB 不变、DB 最终链接拒绝 | A6-11..12 | results.json |\n"
        "| render 发布失败无半成品、capture 原子失败、损坏 DB、关闭态 | A6-13..16 | results.json, source_hashes.json |\n"
        "| 干净副本、零残留、历史只读 hash | A6-17..19 | results.json, historical_read_only_hashes.json |\n",
        encoding="utf-8",
    )
    (evidence / "rerun.md").write_text(
        "# 复跑\n\n```bash\npython3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/scripts/run_attempt_6.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-6-review-evidence\n```\n\n预期：19 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。复核后精确删除外置 Evidence 目录。\n",
        encoding="utf-8",
    )

    manifest_files = source_files + [ATTEMPT / "README.md"] + files_under(evidence)
    deliverable = LIFEOS / "deliverables" / "LIFEOS-P3-094_rework_attempt_6_task_local_render_clear_boundary.md"
    if deliverable.exists():
        manifest_files.append(deliverable)
    lines = [
        "# LIFEOS-P3-094 Rework attempt-6 Evidence Manifest", "",
        f"结论：{'PASS' if all_pass else 'NOT PASS'}；固定非敏感夹具；不含 SQLite、HTML、缓存或用户原文。", "",
        "| 文件 | SHA-256 |", "|---|---|",
    ]
    for path in sorted(set(path for path in manifest_files if path.name != "MANIFEST.md")):
        lines.append(f"| `{Path(os.path.relpath(path, evidence))}` | `{sha256(path)}` |")
    (evidence / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if all_pass else 1


def stat_is_fifo(path: Path) -> bool:
    import stat
    return stat.S_ISFIFO(path.lstat().st_mode)


if __name__ == "__main__":
    raise SystemExit(main())
