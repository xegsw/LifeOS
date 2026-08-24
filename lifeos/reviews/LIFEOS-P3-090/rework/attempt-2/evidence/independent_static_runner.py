#!/usr/bin/env python3
"""P3-090 attempt-2 independent, read-only static review runner."""
import hashlib
import json
import sys
from pathlib import Path

APP = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[6]

expected = {
    "default-recovery.html": "c8e6e130bdb26962f6663afc56529fecf2c3501f643633655837daa433ee16b4",
    "no-reliable-suggestion.html": "c38a3d8fe35bb00d5d13ca1fa1967daa813c1b8af083e75de3fb9cb593d0520d",
    "restricted-offline.html": "0965726629e105087b94680476f18e5a35f361f046be23ccbc468850ac84085f",
    "app.js": "88dc10ffa945d12baf42b771e4c6fddef791a5f1305e9f1d349161977684fe1a",
    "styles.css": "052600b12672a7d9bf255c130edbb4eb5d6d3d3bfee3a64be403e24e74dfe94a",
}
history = {
    "P3-079 integrated_runtime.py": (ROOT / "lifeos/engineering/LIFEOS-P3-079/src/integrated_runtime.py", "19d337a560cfa3e6098571b29a71fc121e059db1c0914e3e3f58f3f740905788"),
    "P3-087 app.js": (ROOT / "lifeos/engineering/LIFEOS-P3-087/app.js", "fa50eb0e7bfa177a3ba2c6e97ec1185370506e84cc2f1d01434ac9d5ea090d0c"),
    "P3-088 independent runner": (ROOT / "lifeos/reviews/LIFEOS-P3-088/evidence/independent_static_runner.mjs", "ec2966b3e92c759482444dc25d6e83eb8243b21b27541a870928f4186cd2cb8e"),
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
results = []
def check(case, condition, detail): results.append({"id": case, "pass": bool(condition), "detail": detail})

for name, digest in expected.items():
    check("HASH-" + name, (APP / name).exists() and sha(APP / name) == digest, "task-local source hash matches P3-089 manifest")
for name, (path, digest) in history.items():
    check("HIST-" + name, path.exists() and sha(path) == digest, "specified read-only historical hash unchanged")

html = {name: (APP / name).read_text(encoding="utf-8") for name in expected if name.endswith(".html")}
js = (APP / "app.js").read_text(encoding="utf-8")
css = (APP / "styles.css").read_text(encoding="utf-8")
all_text = "\n".join(html.values()) + "\n" + js + "\n" + css
for name, page in html.items():
    check("PAGE-" + name + "-local", 'href="styles.css"' in page and 'src="app.js"' in page, "only relative local CSS/JS resources")
    check("PAGE-" + name + "-skip", 'class="skip-link" href="#main-content"' in page, "skip link targets main content")
    check("PAGE-" + name + "-boundary", "AI 未启用" in page and ("网络未使用" in page or "网络未使用；" in page), "synthetic and AI/network boundary is visible")
    check("PAGE-" + name + "-nav", page.count(".html") >= 3 and 'aria-label="今日状态导航"' in page, "three-page navigation is present")
check("LIFE-default-deny", "默认拒绝" in html["default-recovery.html"] and "默认拒绝" in js, "default-deny is explicit in UI and state")
check("LIFE-capture-confirm", "confirm-capture" in html["default-recovery.html"] and "明确确认" in js, "capture needs explicit confirmation")
check("LIFE-grant-revoke", "id=\"grant\"" in html["default-recovery.html"] and "id=\"revoke\"" in html["default-recovery.html"] and "明确 grant" in js, "grant and revoke controls are distinct")
check("LIFE-confirm-exact", "restore-confirmation" in html["default-recovery.html"] and "!== 'CONFIRM'" in js, "restore requires exact CONFIRM")
check("LIFE-failure-clear", "simulate-failure" in html["default-recovery.html"] and "clearDisplay(" in js and "失败披露" in js, "failure clears display and discloses failure")
check("LIFE-session-only", "当前页面 DOM" in all_text and "刷新或关闭后状态清除" in all_text, "session-only disclosure is explicit")
check("STATE-no-suggestion", "不读取资料、不生成建议" in html["no-reliable-suggestion.html"] and "暂无可靠建议" in html["no-reliable-suggestion.html"], "no fabricated suggestion")
check("STATE-restricted", "权限受限 · 离线" in html["restricted-offline.html"] and "已阻断" in html["restricted-offline.html"], "restricted/offline remains fail-closed")
check("A11Y-focus", ":focus-visible" in css and "outline:3px" in css, "visible focus styling exists")
check("A11Y-responsive", "@media (max-width:600px)" in css and "grid-template-columns:1fr" in css, "narrow-screen layout exists")
check("A11Y-reduced-motion", "prefers-reduced-motion:reduce" in css, "reduced-motion override exists")
for forbidden in ["http://", "https://", "fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "indexedDB", "navigator.storage", "showOpenFilePicker", "FileReader", "sqlite", "tauri", "invoke(", "vault", "export", "WebSocket", "OpenAI"]:
    check("CLOSED-" + forbidden, forbidden.lower() not in all_text.lower(), "forbidden capability token is absent")
payload = {"task":"LIFEOS-P3-090", "attempt":"rework/attempt-2", "runner":"independent_static_runner.py", "app":str(APP), "pass":sum(r["pass"] for r in results), "fail":sum(not r["pass"] for r in results), "results":results, "counts":{"P0":0,"P1":0,"P2":0,"Unknown":0,"NotImplemented":0}}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{payload['pass']} PASS / {payload['fail']} FAIL")
sys.exit(1 if payload["fail"] else 0)
