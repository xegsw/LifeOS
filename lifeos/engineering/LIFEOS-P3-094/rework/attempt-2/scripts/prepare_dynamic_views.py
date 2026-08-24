#!/usr/bin/env python3
"""Prepare fixed-text success and fail-closed local pages for Chrome evidence."""
import shutil
import sys
from pathlib import Path

ENGINEERING = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ENGINEERING / "src"))
from local_capture import CaptureError, capture, render_today

ROOT = Path("/private/tmp/lifeos-p3-094-attempt-2-dynamic")
DB = ROOT / "capture.sqlite"
ROOT.mkdir(parents=True, exist_ok=True)
capture(DB, "P3-094 fixed non-sensitive verification text", "dynamic")
render_today(DB, ROOT / "today.html")
try:
    capture(DB, "", "empty")
except CaptureError:
    pass
(ROOT / "rejected.html").write_text("<!doctype html><meta charset='utf-8'><title>LifeOS 今日页（内部）</title><main><h1>今日</h1><p>捕获被拒绝：内容不能为空。</p><p>未显示成功或部分记录。</p><p>内部本地展示 · 不同步、不导出</p></main>", encoding="utf-8")
