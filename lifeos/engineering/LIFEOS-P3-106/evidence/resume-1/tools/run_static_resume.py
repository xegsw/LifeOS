#!/usr/bin/env python3
"""Read-only input/history verification for the P3-106 resume-1 namespace."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import sys


ROOT = Path(__file__).resolve().parents[3]
REPO = ROOT.parents[2]
OUT = ROOT / "evidence/resume-1"
INITIAL_EVIDENCE = ROOT / "evidence"
PM_ROOT = REPO / "lifeos/reviews/LIFEOS-P3-106"
ABF = REPO / "lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md"
LEGACY = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path: Path) -> dict[str, object]:
    try:
        value = path.lstat()
        return {
            "exists": True,
            "type": stat.filemode(value.st_mode)[0],
            "size": value.st_size,
            "mtime_ns": value.st_mtime_ns,
            "ctime_ns": value.st_ctime_ns,
        }
    except FileNotFoundError:
        return {"exists": False}


def result(test_id: str, ok: bool, detail: str) -> dict[str, str]:
    return {"id": test_id, "status": "PASS" if ok else "FAIL", "detail": detail}


def tree_snapshot(paths: list[Path]) -> list[dict[str, object]]:
    rows = []
    for base in paths:
        if base.is_file():
            rows.append({"path": str(base.relative_to(REPO)), "sha256": digest(base), "metadata": metadata(base)})
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or OUT in path.parents:
                continue
            rows.append({"path": str(path.relative_to(REPO)), "sha256": digest(path), "metadata": metadata(path)})
    return rows


def main() -> int:
    spec = importlib.util.spec_from_file_location("initial_preflight", ROOT / "tests/verify_preflight.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen preflight source")
    initial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(initial)

    rows = []
    fixed_rows = []
    for label, (path, expected) in initial.FIXED.items():
        actual = digest(path) if path.is_file() else "missing"
        ok = actual == expected
        rows.append(result(f"ABF-M-001-{label}", ok, f"{path.relative_to(REPO)} {actual}"))
        fixed_rows.append({"label": label, "path": str(path.relative_to(REPO)), "expected": expected, "actual": actual, "status": "PASS" if ok else "FAIL"})
    actual_abf = digest(ABF)
    rows.append(result("ABF-M-001-ABF-HASH", actual_abf == "1aa076a289173eb0dbd4e17ccfd3a1af89cbd9f815ad656d31d9318a5172a5c4", actual_abf))

    for rel in initial.IMMUTABLE:
        current = ROOT / rel
        authority = REPO / "lifeos/engineering/LIFEOS-P3-104" / rel
        rows.append(result(f"ABF-I-03-{rel}", current.read_bytes() == authority.read_bytes(), "P3-106 equals P3-104 byte-for-byte"))

    inventory = json.loads((OUT / "write_path_inventory.json").read_text(encoding="utf-8"))
    runtime = (ROOT / "src/runtime.rs").read_text(encoding="utf-8")
    expected_names = {"lifecycle", "failure", "arguments", "links", "dangling-final", "dangling-sidecars", "tamper", "sidecar"}
    actual_names = set(re.findall(r'fixture\("([a-z-]+)"\)', runtime))
    rows.append(result("ABF-M-002-UNIT-NAMES", actual_names == expected_names, str(sorted(actual_names))))
    rows.append(result("ABF-M-002-RESUME-INVENTORY", inventory.get("created_before_resume_copy_build_test_or_app_action") is True, "resume inventory precedes build/test/app actions"))

    config = json.loads((ROOT / "tauri.conf.json").read_text(encoding="utf-8"))
    window = config["app"]["windows"][0]
    rows.append(result("ABF-M-004-CONFIG-VIEWPORT", window["width"] == 1280 and window["height"] == 1024, f"{window['width']}x{window['height']}"))
    capability = json.loads((ROOT / "capabilities/main.json").read_text(encoding="utf-8"))
    rows.append(result("ABF-I-04-CAPABILITY", capability.get("permissions") == [], "renderer permissions empty"))
    rows.append(result("ABF-I-04-IPC", runtime.count("#[tauri::command]") == 3 and all(name in runtime for name in ["capture_record", "get_today", "runtime_status"]), "three command annotations"))

    html_paths = [ROOT / "ui/default-recovery.html", ROOT / "ui/no-reliable-suggestion.html", ROOT / "ui/restricted-offline.html"]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in html_paths)
    css = (ROOT / "ui/styles.css").read_text(encoding="utf-8")
    js = (ROOT / "ui/app.js").read_text(encoding="utf-8")
    rows.append(result("ABF-I-07-NO-SCREENSHOT", not re.search(r'<img|background(?:-image)?\s*:\s*url|base64,', combined + css, re.I), "no img/background-url/base64 page reuse"))
    rows.append(result("ABF-I-05-SHARED-SHELL", all(token in combined + css for token in ['class="rail"', "composer-wrap", "--canvas", "--blue", "recovery-card", "empty-card", "alert-stack"]), "shared shell tokens"))
    rows.append(result("ABF-I-08-IDENTITY", all(token in combined for token in ["你的记录 · 原文", "AI", "外部来源", "你已确认", "固定演示"]), "identity labels"))
    rows.append(result("ABF-M-011-UNIMPLEMENTED", "data-unimplemented" in combined and "未启用；没有调用 IPC" in js and combined.count("disabled aria-label") >= 6, "disclosed or disabled"))
    rows.append(result("ABF-M-012-NETWORK", "fetch(" not in js and "XMLHttpRequest" not in js and "WebSocket" not in js and "http://" not in combined + css + js and "https://" not in combined + css + js, "no frontend network"))
    rows.append(result("ABF-M-015-A11Y", all(token in combined + css for token in ["skip-link", ":focus-visible", "prefers-reduced-motion", 'aria-live="polite"']), "a11y hooks"))

    initial_snapshot = tree_snapshot([
        INITIAL_EVIDENCE,
        PM_ROOT / "pm_evidence/initial",
        REPO / "lifeos/reviews/LIFEOS-P3-106_pm_review.md",
        REPO / "lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md",
    ])
    unit_paths = sorted(str(path) for path in Path("/private/tmp").iterdir() if re.fullmatch(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+", path.name))
    run_paths = [Path(value) for value in inventory["actual_app_allowlist"]["exact_run_paths"]]
    preflight = {
        "initial_evidence_snapshot": initial_snapshot,
        "legacy_metadata": metadata(LEGACY),
        "unit_path_residuals": unit_paths,
        "authorized_run_path_pre_lstat": [{"path": str(path), "metadata": metadata(path)} for path in run_paths],
    }
    preflight_ok = not unit_paths and all(not row["metadata"]["exists"] for row in preflight["authorized_run_path_pre_lstat"])
    rows.append(result("ABF-M-002-PATH-PREFLIGHT", preflight_ok, "unit residuals zero; every exact resume path lstat missing"))

    summary = {
        "task": "LIFEOS-P3-106",
        "execution": "resume-1",
        "total": len(rows),
        "pass": sum(row["status"] == "PASS" for row in rows),
        "fail": sum(row["status"] != "PASS" for row in rows),
        "results": rows,
    }
    (OUT / "fixed_input_hashes.json").write_text(json.dumps(fixed_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "initial_read_only_baseline.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "static_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": summary["total"], "pass": summary["pass"], "fail": summary["fail"], "initial_files": len(initial_snapshot)}, ensure_ascii=False))
    return 0 if summary["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
