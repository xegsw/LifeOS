#!/usr/bin/env python3
"""Deterministic source/config checks for LIFEOS-P3-104.

This runner never opens the retained pilot and never connects to a network.
It checks only the P3-104 candidate and Frozen read-only hash inputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
RESULTS = Path(os.environ.get(
    "LIFEOS_P3_104_STATIC_RESULTS",
    str(ROOT / "evidence" / "static_results.json"),
))

EXPECTED_INPUTS = {
    "lifeos/engineering/LIFEOS-P3-091/default-recovery.html": "e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b",
    "lifeos/engineering/LIFEOS-P3-091/no-reliable-suggestion.html": "e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793",
    "lifeos/engineering/LIFEOS-P3-091/restricted-offline.html": "b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e",
    "lifeos/engineering/LIFEOS-P3-091/app.js": "a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac",
    "lifeos/engineering/LIFEOS-P3-091/styles.css": "35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91",
    "lifeos/engineering/LIFEOS-P3-091/evidence/rework/attempt-2/MANIFEST.md": "5dd7e82804dd9c60fcc2ad378d7fa80393a1d767586c6aff7673b09c4e6bef6e",
    "lifeos/reviews/LIFEOS-P3-092_pm_review.md": "bd2a6bf0dddc5b4b8b59208bc08dd8eb0307d2e77628b9eefdc6e3b175ce2831",
    "lifeos/deliverables/LIFEOS-P3-093_three_frozen_today_pages_controlled_ui_closure_and_next_capability_decision_package.md": "52496a8e37a3e865c2968f9f66de05fa092f2dabae15325d263e084e90124687",
    "lifeos/reviews/LIFEOS-P3-093_pm_review.md": "15d5e91e52a30e2c782bd61fe54779e3d5d98e73c166521b0b935c096467f9ae",
    "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py": "1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453",
    "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py": "ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659",
    "lifeos/spikes/P2-015-tauri-ipc-boundary/equivalent_capability_contract.json": "ce5d918fa5afc7cc016d1df7b2f5c863aade3b1d6eba2b5372bf6466763ff36b",
    "lifeos/reviews/LIFEOS-P3-103_pm_review.md": "ec649e224bcba7e3d4a5d92f98ed8b9d79f5d0ac0b41ecc05d1ca3311793f07e",
    "lifeos/reviews/LIFEOS-P3-103/pm_evidence/initial/MANIFEST.md": "cb099df64da3b87284e88e889bf7bd739d6118d6433a119dcad1972cf270d482",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


results: list[dict[str, object]] = []


def check(test_id: str, condition: bool, detail: str) -> None:
    results.append({"id": test_id, "status": "PASS" if condition else "FAIL", "detail": detail})


cargo = (ROOT / "Cargo.toml").read_text()
runtime = (ROOT / "src/runtime.rs").read_text()
config = json.loads((ROOT / "tauri.conf.json").read_text())
capability = json.loads((ROOT / "capabilities/main.json").read_text())
app_js = (ROOT / "ui/app.js").read_text()
styles = (ROOT / "ui/styles.css").read_text()
pages = {name: (ROOT / "ui" / name).read_text() for name in (
    "default-recovery.html", "no-reliable-suggestion.html", "restricted-offline.html"
)}

for index, (path, expected) in enumerate(EXPECTED_INPUTS.items(), start=1):
    actual = digest(PROJECT / path)
    check(f"STATIC-HISTORY-{index:02d}", actual == expected, f"{path}={actual}")

exact_dependencies = {
    'tauri-build = { version = "=2.6.3", features = [] }',
    'tauri = { version = "=2.11.5", features = [] }',
    'rusqlite = { version = "=0.40.2", features = ["bundled"] }',
    'serde = { version = "=1.0.229", features = ["derive"] }',
    'serde_json = "=1.0.151"',
}
check("STATIC-SUPPLY-01", all(item in cargo for item in exact_dependencies), "direct dependency versions frozen")
check("STATIC-SUPPLY-02", "git =" not in cargo and "path =" not in cargo, "no git/path dependency")
check("STATIC-IPC-01", re.search(r"generate_handler!\[\s*capture_record,\s*get_today,\s*runtime_status\s*\]", runtime, re.S) is not None, "exact invoke handler")
check("STATIC-IPC-02", "#[serde(deny_unknown_fields)]" in runtime, "strict request schemas")
check("STATIC-IPC-03", "renderer_direct_capabilities: Vec::new()" in runtime, "renderer direct capabilities empty")
check("STATIC-IPC-04", capability.get("permissions") == [], "Tauri capability permission list empty")
check("STATIC-IPC-05", config["app"]["security"]["capabilities"] == ["main"], "single capability selected")

csp = config["app"]["security"]["csp"]
check("STATIC-CSP-01", "default-src 'self'" in csp and "object-src 'none'" in csp and "frame-src 'none'" in csp, "CSP local and closed")
check("STATIC-CSP-02", "https:" not in csp and "wss:" not in csp, "CSP has no remote network source")
check("STATIC-CSP-03", "localhost" not in csp.lower(), "CSP has no localhost source")
check("STATIC-APP-01", config["app"]["withGlobalTauri"] is True and "devUrl" not in config["build"], "global Tauri API without dev server")
check("STATIC-APP-02", config["bundle"]["active"] is False, "no production bundle claim")
check("STATIC-APP-03", set(re.findall(r'safeInvoke\("([a-z0-9_]+)"', app_js)) == {"capture_record", "get_today", "runtime_status", "unknown_p3_104_command"}, "UI invokes allowlist plus explicit unknown negative probe")
check("STATIC-APP-04", "fetch(" not in app_js and "XMLHttpRequest" not in app_js and "WebSocket" not in app_js, "no renderer network API")
check("STATIC-APP-05", "innerHTML" not in app_js and ".textContent" in app_js, "user original rendered as text only")

for index, (name, html) in enumerate(pages.items(), start=1):
    check(f"STATIC-UI-{index:02d}-A", 'class="skip-link"' in html and 'tabindex="-1"' in html, f"{name} skip link and target")
    check(f"STATIC-UI-{index:02d}-B", "用户原文" in html and "AI 未启用" in html and "本地" in html, f"{name} identity boundary")
    check(f"STATIC-UI-{index:02d}-C", all(target in html for target in pages), f"{name} has three-page navigation")
check("STATIC-A11Y-01", ":focus-visible" in styles and ".skip-link:focus" in styles, "visible keyboard focus")
check("STATIC-A11Y-02", "prefers-reduced-motion:reduce" in styles, "reduced motion")
check("STATIC-A11Y-03", "@media (max-width:600px)" in styles, "narrow responsive layout")

banned_registration = ["clear", "delete", "export", "raw_sql", "shell", "process_spawn", "vault", "sync"]
handler_block = re.search(r"generate_handler!\[(.*?)\]", runtime, re.S).group(1)
check("STATIC-CLOSED-01", not any(word in handler_block.lower() for word in banned_registration), "banned commands not registered")
check("STATIC-CLOSED-02", "tauri-plugin" not in cargo and "plugin(" not in runtime, "no Tauri plugins")
check("STATIC-PRIVACY-01", "LifeOS-Self-Use-Pilot-1" not in "\n".join([cargo, runtime, app_js, *pages.values()]), "retained pilot path absent")

failed = [item for item in results if item["status"] != "PASS"]
payload = {
    "task": "LIFEOS-P3-104",
    "runner": "static_checks.py",
    "passed": len(results) - len(failed),
    "failed": len(failed),
    "p0": len(failed),
    "p1": 0,
    "p2": 0,
    "unknown": 0,
    "not_implemented": 0,
    "results": results,
}
RESULTS.parent.mkdir(parents=True, exist_ok=True)
RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: payload[key] for key in ("passed", "failed", "p0", "unknown", "not_implemented")}, ensure_ascii=False))
raise SystemExit(1 if failed else 0)
