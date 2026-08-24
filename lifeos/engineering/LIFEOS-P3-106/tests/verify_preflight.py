#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
EVIDENCE = ROOT / "evidence"
ABF = REPO / "lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md"

FIXED = {
    "visual/default": (REPO / "lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg", "7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1"),
    "visual/no-suggestion": (REPO / "lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg", "55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697"),
    "visual/restricted": (REPO / "lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg", "9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661"),
    "p3-104/Cargo.lock": (REPO / "lifeos/engineering/LIFEOS-P3-104/Cargo.lock", "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1"),
    "p3-104/Cargo.toml": (REPO / "lifeos/engineering/LIFEOS-P3-104/Cargo.toml", "9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e"),
    "p3-104/runtime": (REPO / "lifeos/engineering/LIFEOS-P3-104/src/runtime.rs", "0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529"),
    "p3-104/main": (REPO / "lifeos/engineering/LIFEOS-P3-104/src/main.rs", "4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c"),
    "p3-104/capability": (REPO / "lifeos/engineering/LIFEOS-P3-104/capabilities/main.json", "ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b"),
    "p3-104/config": (REPO / "lifeos/engineering/LIFEOS-P3-104/tauri.conf.json", "7c30529e69e5b30900156512f396a5d58fd8e20739786cc77abf5d0f7f6780ef"),
    "p3-104/replay": (REPO / "lifeos/engineering/LIFEOS-P3-104/scripts/offline_actual_app_replay.sh", "cf82f88faa7b80d5818f85d5f23e87dbae228ac0314b9b8642be8ef55157db73"),
    "p3-104/engineering-manifest": (REPO / "lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md", "8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1"),
    "p3-104/review": (REPO / "lifeos/reviews/LIFEOS-P3-104_pm_review.md", "8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795"),
    "p3-104/pm-manifest": (REPO / "lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md", "e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4"),
    "p3-105/default": (REPO / "lifeos/engineering/LIFEOS-P3-105/ui/default-recovery.html", "4a6464236b03ad5ffee1d50268169558320ca90484fe646933ff19c2497a5d56"),
    "p3-105/no-suggestion": (REPO / "lifeos/engineering/LIFEOS-P3-105/ui/no-reliable-suggestion.html", "1fdd0129ffa056fd64a08e0c6227cdf84b90cc8e964ff811dde2efabfaa85ce2"),
    "p3-105/restricted": (REPO / "lifeos/engineering/LIFEOS-P3-105/ui/restricted-offline.html", "fa918f044fa9cbb4f3eafcb117af97bc039c5bbeb075ada2e91f9da34eecd27d"),
    "p3-105/app": (REPO / "lifeos/engineering/LIFEOS-P3-105/ui/app.js", "62d6685c8911efb5ccaabadde350e267cb0ce58b829abbeca0580ff7025a6507"),
    "p3-105/styles": (REPO / "lifeos/engineering/LIFEOS-P3-105/ui/styles.css", "5b93977e863bd33a6f505e585080cdf85a547c08cee1bca9c7fa05008d26d50d"),
    "p3-105/config": (REPO / "lifeos/engineering/LIFEOS-P3-105/tauri.conf.json", "d44e1e03ade7ecc5dc75f5431295de78735ccf0596a421eae0f553411294e0f0"),
    "p3-105/engineering-manifest": (REPO / "lifeos/engineering/LIFEOS-P3-105/evidence/MANIFEST.md", "b3bb63eb3605499fe70885f3056c3a1fb177227f20cff0fa6e3ec2d95cdb9b92"),
    "p3-105/review": (REPO / "lifeos/reviews/LIFEOS-P3-105_pm_review.md", "8f7c1add69313082863012dc04576dc20beb3889eff0ad73f431a07710820cc6"),
    "p3-105/pm-manifest": (REPO / "lifeos/reviews/LIFEOS-P3-105/pm_evidence/initial/MANIFEST.md", "73212af186afb8aa4bb5dccf41f05a6836e20e4ec58824f459a0049ef4c3d73b"),
}
IMMUTABLE = ["Cargo.lock", "Cargo.toml", "src/runtime.rs", "src/main.rs", "capabilities/main.json"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def result(test_id: str, ok: bool, detail: str) -> dict:
    return {"id": test_id, "status": "PASS" if ok else "FAIL", "detail": detail}

def metadata(path: Path) -> dict:
    try:
        value = path.lstat()
        return {"exists": True, "type": stat.filemode(value.st_mode)[0], "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}
    except FileNotFoundError:
        return {"exists": False}

def main() -> int:
    rows, hash_rows = [], []
    for label, (path, expected) in FIXED.items():
        actual = digest(path) if path.is_file() else "missing"
        ok = actual == expected
        rows.append(result(f"ABF-M-001-{label}", ok, f"{path.relative_to(REPO)} {actual}"))
        hash_rows.append({"label": label, "path": str(path.relative_to(REPO)), "expected": expected, "actual": actual, "status": "PASS" if ok else "FAIL"})
    rows.append(result("ABF-M-001-ABF-HASH", digest(ABF) == "1aa076a289173eb0dbd4e17ccfd3a1af89cbd9f815ad656d31d9318a5172a5c4", digest(ABF)))
    for rel in IMMUTABLE:
        rows.append(result(f"ABF-I-03-{rel}", (ROOT / rel).read_bytes() == (REPO / "lifeos/engineering/LIFEOS-P3-104" / rel).read_bytes(), "P3-106 equals P3-104 byte-for-byte"))
    inventory = json.loads((ROOT / "write_path_inventory.json").read_text())
    runtime = (ROOT / "src/runtime.rs").read_text()
    expected_names = {"lifecycle", "failure", "arguments", "links", "dangling-final", "dangling-sidecars", "tamper", "sidecar"}
    actual_names = set(re.findall(r'fixture\("([a-z-]+)"\)', runtime))
    rows.append(result("ABF-M-002-UNIT-NAMES", actual_names == expected_names, f"{sorted(actual_names)}"))
    rows.append(result("ABF-M-002-INVENTORY", inventory.get("created_before_copy_build_or_test") is True and len(inventory.get("generators", [])) == 4, "four generator groups"))
    config = json.loads((ROOT / "tauri.conf.json").read_text())
    window = config["app"]["windows"][0]
    rows.append(result("ABF-M-004-VIEWPORT", window["width"] == 1280 and window["height"] == 1024, f"{window['width']}x{window['height']}"))
    capability = json.loads((ROOT / "capabilities/main.json").read_text())
    rows.append(result("ABF-I-04-CAPABILITY", capability.get("permissions") == [], "renderer permissions empty"))
    rows.append(result("ABF-I-04-IPC", runtime.count("#[tauri::command]") == 3 and all(name in runtime for name in ["capture_record", "get_today", "runtime_status"]), "three command annotations"))
    ui_files = [ROOT / "ui/default-recovery.html", ROOT / "ui/no-reliable-suggestion.html", ROOT / "ui/restricted-offline.html"]
    combined = "\n".join(path.read_text() for path in ui_files)
    css, js = (ROOT / "ui/styles.css").read_text(), (ROOT / "ui/app.js").read_text()
    rows.append(result("ABF-I-07-NO-SCREENSHOT", not re.search(r'<img|background(?:-image)?\s*:\s*url|base64,', combined + css, re.I), "no img/background-url/base64 page reuse"))
    rows.append(result("ABF-I-05-SHARED-SHELL", all(token in combined + css for token in ["class=\"rail\"", "composer-wrap", "--canvas", "--blue", "recovery-card", "empty-card", "alert-stack"]), "shared shell tokens"))
    rows.append(result("ABF-I-08-IDENTITY", all(token in combined for token in ["你的记录 · 原文", "AI", "外部来源", "你已确认", "固定演示"]), "identity labels"))
    rows.append(result("ABF-M-011-UNIMPLEMENTED", "data-unimplemented" in combined and "未启用；没有调用 IPC" in js and combined.count("disabled aria-label") >= 6, "disclosed or disabled"))
    rows.append(result("ABF-M-012-NETWORK", "fetch(" not in js and "XMLHttpRequest" not in js and "WebSocket" not in js and "http://" not in combined + css + js and "https://" not in combined + css + js, "no frontend network"))
    rows.append(result("ABF-M-015-A11Y", all(token in combined + css for token in ["skip-link", ":focus-visible", "prefers-reduced-motion", "aria-live=\"polite\""]), "a11y hooks"))
    legacy = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")
    (EVIDENCE / "legacy_metadata_before.json").write_text(json.dumps({"path": str(legacy), "metadata": metadata(legacy)}, ensure_ascii=False, indent=2) + "\n")
    (EVIDENCE / "fixed_input_hashes.json").write_text(json.dumps(hash_rows, ensure_ascii=False, indent=2) + "\n")
    summary = {"task_id": "LIFEOS-P3-106", "total": len(rows), "pass": sum(row["status"] == "PASS" for row in rows), "fail": sum(row["status"] != "PASS" for row in rows), "results": rows}
    (EVIDENCE / "static_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in ["total", "pass", "fail"]}, ensure_ascii=False))
    return 0 if summary["fail"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
