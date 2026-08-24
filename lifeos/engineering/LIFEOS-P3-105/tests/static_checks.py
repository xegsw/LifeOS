#!/usr/bin/env python3
import hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT.parent / "LIFEOS-P3-104"
OUT = ROOT / "evidence" / "static_results.json"
results = []

def check(test_id, condition, detail, severity="P0"):
    results.append({"test_id": test_id, "execution_id": f"P3-105-STATIC-{len(results)+1:03d}", "severity": severity, "status": "PASS" if condition else "FAIL", "detail": detail})

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

fixed = {
    "Cargo.lock": "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1",
    "src/runtime.rs": "0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529",
    "src/main.rs": "4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c",
    "capabilities/main.json": "ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b"
}
for rel, expected in fixed.items():
    check(f"ST-FROZEN-{rel}", sha(ROOT / rel) == expected, f"{rel} hash={sha(ROOT / rel)}")
check("ST-DEPS-01", (ROOT / "Cargo.toml").read_bytes() == (BASE / "Cargo.toml").read_bytes(), "Cargo.toml and all direct dependency versions byte-identical")

config = json.loads((ROOT / "tauri.conf.json").read_text())
base_config = json.loads((BASE / "tauri.conf.json").read_text())
allowed = {"title", "width", "height", "minWidth", "minHeight"}
current_window = config["app"]["windows"][0]
base_window = base_config["app"]["windows"][0]
changed = {key for key in set(current_window) | set(base_window) if current_window.get(key) != base_window.get(key)}
clone = json.loads(json.dumps(config)); clone["app"]["windows"][0] = base_window
check("ST-CONFIG-01", changed <= allowed and clone == base_config, f"only allowed window fields changed: {sorted(changed)}")
check("ST-CONFIG-02", current_window["width"] == 1280 and current_window["height"] == 1024, "initial window is 1280x1024")

html_paths = sorted((ROOT / "ui").glob("*.html"))
all_html = "\n".join(path.read_text() for path in html_paths)
css = (ROOT / "ui/styles.css").read_text()
js = (ROOT / "ui/app.js").read_text()
check("ST-PAGES-01", len(html_paths) == 3, f"three HTML pages: {[p.name for p in html_paths]}", "P1")
for path in html_paths:
    text = path.read_text()
    check(f"ST-RAIL-{path.stem}", 'class="rail"' in text and text.count('class="rail-link"') >= 2, f"{path.name} left rail", "P1")
    check(f"ST-COMPOSER-{path.stem}", 'class="composer-wrap"' in text and 'data-action="capture"' in text, f"{path.name} composer", "P1")
    check(f"ST-A11Y-{path.stem}", 'class="skip-link"' in text and 'id="main-content"' in text and 'tabindex="-1"' in text, f"{path.name} skip link and focus target", "P1")
    check(f"ST-CLOSED-{path.stem}", 'aria-label="附件未启用"' in text and 'aria-label="语音未启用"' in text and text.count(" disabled") >= 2, f"{path.name} attachment and voice disabled")

for banned_id, pattern in {
    "ST-NO-IMG": r"<img\b", "ST-NO-CANVAS": r"<canvas\b", "ST-NO-BGIMG": r"background-image\s*:",
    "ST-NO-REMOTE": r"https?://|//[A-Za-z0-9.-]+/", "ST-NO-DATAIMG": r"data:image", "ST-NO-REFNAME": r"01_default_recovery_preview|02_no_reliable_suggestion_preview|03_permission_offline_preview"
}.items():
    check(banned_id, re.search(pattern, all_html + "\n" + css + "\n" + js, re.I) is None, f"pattern absent: {pattern}")

check("ST-IPC-01", js.count('safeInvoke("capture_record"') == 1 and js.count('safeInvoke("get_today"') >= 2 and js.count('safeInvoke("runtime_status"') == 1, "frontend references only three allowlisted IPC plus deliberate unknown probe")
check("ST-NETWORK-01", not re.search(r"fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon", js), "no frontend network API")
check("ST-CSP-01", config["app"]["security"]["csp"] == base_config["app"]["security"]["csp"] and config["app"]["security"]["capabilities"] == ["main"], "CSP and capability selection unchanged")
check("ST-MOTION-01", "prefers-reduced-motion: reduce" in css, "reduced motion override present", "P1")
check("ST-NARROW-01", "@media (max-width: 560px)" in css and "@media (max-width: 820px)" in css, "narrow layouts present", "P1")
check("ST-IDENTITY-01", "你的记录 · 原文" in all_html and "AI 未启用" in all_html and "固定" in all_html, "content identity and fixed-demo disclosure visible")
check("ST-STATE-D", "recovery-card" in (ROOT / "ui/default-recovery.html").read_text() and "suggestion-card" in (ROOT / "ui/default-recovery.html").read_text(), "default recovery anchors", "P1")
check("ST-STATE-N", "尚未选择 Project" in (ROOT / "ui/no-reliable-suggestion.html").read_text() and (ROOT / "ui/no-reliable-suggestion.html").read_text().count("trace-card") == 3, "no-suggestion anchors", "P1")
restricted = (ROOT / "ui/restricted-offline.html").read_text()
check("ST-STATE-R", all(token in restricted for token in ["网络离线", "来源权限受限", "permission-panel", "schedule"]), "restricted/offline anchors", "P1")

failures = [r for r in results if r["status"] != "PASS"]
payload = {"suite": "P3-105 static and visual contract preflight", "total": len(results), "pass": len(results)-len(failures), "fail": len(failures), "P0": sum(r["severity"]=="P0" for r in failures), "P1": sum(r["severity"]=="P1" for r in failures), "P2": 0, "Unknown": 0, "Not Implemented": 0, "results": results}
OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: payload[k] for k in ["total","pass","fail","P0","P1","P2","Unknown","Not Implemented"]}, ensure_ascii=False))
sys.exit(1 if failures else 0)
