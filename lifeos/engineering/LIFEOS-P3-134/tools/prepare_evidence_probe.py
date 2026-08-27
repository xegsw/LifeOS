#!/usr/bin/env python3
"""Create a disposable P3-134 actual-Tauri evidence probe outside the candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-134/candidate"
REFERENCE = ROOT / "lifeos/prototypes/LIFEOS-P3-116"
VISUAL = ["index.html", "app.js", "styles.css", "fixtures.js"]
IPC = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def probe_script(scenario: str) -> str:
    encoded = json.dumps(scenario)
    return f'''"use strict";
(() => {{
  const scenario = {encoded};
  const outputId = "p3-134-evidence-probe-output";
  const rect = (selector) => {{
    const node = document.querySelector(selector);
    if (!node) return null;
    const box = node.getBoundingClientRect();
    return {{ selector, x: Math.round(box.x * 100) / 100, y: Math.round(box.y * 100) / 100, width: Math.round(box.width * 100) / 100, height: Math.round(box.height * 100) / 100, visible: !!(box.width && box.height) }};
  }};
  const digest = (value) => {{ let h = 0x811c9dc5; for (let i = 0; i < value.length; i += 1) {{ h ^= value.charCodeAt(i); h = Math.imul(h, 0x01000193); }} return (h >>> 0).toString(16).padStart(8, "0"); }};
  const snapshot = (label) => {{
    const root = document.documentElement;
    const computed = getComputedStyle(root);
    const classes = [...new Set([...document.querySelectorAll("[class]")].flatMap((node) => [...node.classList]))].sort();
    const landmarks = [...document.querySelectorAll("main,nav,aside,header,section,form,[role]")].map((node) => `${{node.tagName.toLowerCase()}}|${{node.getAttribute("role") || ""}}|${{node.getAttribute("aria-label") || ""}}|${{[...node.classList].sort().join(".")}}`).sort();
    const keys = [["m", "#main-content"], ["r", ".icon-rail"], ["c", ".composer"], ["w", ".workspace-center"], ["i", ".workspace-inspector"], ["a", ".ai-panel"], ["d", ".modal-backdrop"]].map(([key, selector]) => {{ const value = rect(selector); return value ? [key, value.x, value.y, value.width, value.height] : [key, 0, 0, 0, 0]; }});
    const primary = document.querySelector(".workspace-send, [data-action='ai'], [data-action='runtime:accept'], [data-action='capture']");
    const global = document.querySelector(".ai-launch, .workspace-send");
    return {{
      label,
      scenario,
      viewport: {{ innerWidth: window.innerWidth, innerHeight: window.innerHeight, dpr: window.devicePixelRatio }},
      page: window.__P3_116_RUNTIME__?.state?.page || null,
      classes: {{ count: classes.length, digest: digest(classes.join("|")) }},
      landmarks: {{ count: landmarks.length, digest: digest(landmarks.join("|")) }},
      geometry: keys,
      computed_tokens: digest([computed.getPropertyValue("--blue").trim(), computed.getPropertyValue("--line").trim(), computed.getPropertyValue("--bg").trim(), computed.fontFamily].join("|")),
      active_element: (() => {{ const node = document.activeElement; const box = node?.getBoundingClientRect?.(); return {{ tag: node?.tagName?.toLowerCase() || null, class_count: node?.classList?.length || 0, visible: !!box && box.width > 0 && box.height > 0 }}; }})(),
      reduced_motion: document.body.classList.contains("reduced-motion"),
      health_context_removed: window.__P3_116_RUNTIME__?.state?.healthIncluded === false,
      horizontal_overflow: root.scrollWidth > root.clientWidth,
      primary_action_reachable: !!primary && (() => {{ const b = primary.getBoundingClientRect(); return b.width > 0 && b.height > 0; }})(),
      global_ai_reachable: !!global && (() => {{ const b = global.getBoundingClientRect(); return b.width > 0 && b.height > 0; }})(),
      content_recorded: false
    }};
  }};
  const emit = (value) => {{
    let output = document.getElementById(outputId);
    if (!output) {{
      output = document.createElement("div"); output.id = outputId; output.setAttribute("role", "status"); output.setAttribute("aria-label", "P3-134 non-content evidence probe");
      output.style.cssText = "position:fixed;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden"; document.body.appendChild(output);
    }}
    const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(value))));
    const unit = 320;
    const total = Math.ceil(encoded.length / unit);
    output.replaceChildren(...Array.from({{ length: total }}, (_, index) => {{
      const part = document.createElement("span");
      part.textContent = `P3-134-EVIDENCE:${{index + 1}}/${{total}}:${{encoded.slice(index * unit, (index + 1) * unit)}}`;
      return part;
    }}));
  }};
  const setState = (ui, name) => {{
    const state = ui.state;
    state.aiOpen = false; state.modal = null;
    if (name === "today-empty") {{ state.page = "today"; state.todayMode = "empty"; }}
    else if (name === "today-insufficient") {{ state.page = "today"; state.todayMode = "insufficient"; }}
    else if (name === "today-normal") {{ state.page = "today"; state.todayMode = "normal"; }}
    else if (name === "me") state.page = "me";
    else if (name === "contexts") state.page = "contexts";
    else if (name === "context-detail") {{ state.page = "detail"; state.selectedContext = "launch"; }}
    else if (name === "memory") state.page = "memory";
    else if (name === "memory-detail") {{ state.page = "memory-detail"; state.memoryDetail = "m6"; }}
    else if (name === "global-ai") {{ state.page = "today"; state.aiOpen = true; }}
    else if (name === "global-ai-health-removed") {{ state.page = "today"; state.aiOpen = true; state.healthIncluded = false; }}
    else if (name === "workspace") state.page = "workspace";
    else if (name === "quick-capture") {{ state.page = "today"; state.modal = "capture"; }}
    else if (name === "context-candidate") {{ state.page = "contexts"; state.modal = "suggest"; }}
    else if (name === "domain-gate") {{ state.page = "me"; state.modal = "activation"; }}
    else if (name === "settings-reduced") {{ state.page = "settings"; state.reducedMotion = true; }}
  }};
  const run = () => {{
    const ui = window.__P3_116_RUNTIME__;
    if (!ui) return setTimeout(run, 100);
    if (scenario === "interactive") {{
      const current = (label) => requestAnimationFrame(() => requestAnimationFrame(() => emit(snapshot(label))));
      document.addEventListener("click", () => setTimeout(() => current("interactive-click"), 250), true);
      document.addEventListener("keydown", (event) => setTimeout(() => current(`interactive-key-${{event.key}}`), 250), true);
      return current("interactive-startup");
    }}
    if (scenario !== "cycle") {{ setState(ui, scenario); ui.render(); return requestAnimationFrame(() => requestAnimationFrame(() => emit(snapshot(scenario)))); }}
    const names = ["today-empty", "today-insufficient", "today-normal", "me", "contexts", "context-detail", "memory", "memory-detail", "global-ai", "global-ai-health-removed", "workspace", "quick-capture", "context-candidate", "domain-gate", "settings-reduced"];
    const rows = [];
    for (const name of names) {{ setState(ui, name); ui.render(); rows.push(snapshot(name)); }}
    setState(ui, "today-empty"); ui.render(); requestAnimationFrame(() => requestAnimationFrame(() => emit({{ kind: "cycle", scenario, snapshots: rows, content_recorded: false }})));
  }};
  setTimeout(run, 900);
}})();
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp-root", type=Path, required=True)
    parser.add_argument("--variant", choices=("candidate", "reference"), required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--probe-name")
    parser.add_argument("--native-log", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--window-width", type=int)
    parser.add_argument("--window-height", type=int)
    parser.add_argument("--product-name")
    parser.add_argument("--identifier")
    args = parser.parse_args()
    temp = args.temp_root.resolve()
    expected = Path("/private/tmp/lifeos-p3-134-ui-restoration-v1")
    if temp != expected or not temp.is_dir() or temp.is_symlink():
        raise SystemExit("temporary root must be the authorized ordinary directory")
    destination = temp / "probes" / f"{args.variant}-{args.probe_name or args.scenario}"
    if destination.exists():
        raise SystemExit("probe destination already exists")
    shutil.copytree(CANDIDATE, destination, symlinks=False)
    if args.variant == "reference":
        for name in VISUAL:
            shutil.copy2(REFERENCE / name, destination / "ui" / name)
        app = destination / "ui" / "app.js"
        app_source = app.read_text(encoding="utf-8")
        anchor = "  render();\n})();"
        if anchor not in app_source:
            raise SystemExit("reference renderer exposure anchor missing")
        app.write_text(app_source.replace(anchor, "  window.__P3_116_RUNTIME__ = { state, render, app };\n  render();\n})();"), encoding="utf-8")
    (destination / "ui" / "evidence-probe.js").write_text(probe_script(args.scenario), encoding="utf-8")
    index = (destination / "ui" / "index.html").read_text(encoding="utf-8")
    index = index.replace("</body>", '    <script src="evidence-probe.js"></script>\n  </body>')
    (destination / "ui" / "index.html").write_text(index, encoding="utf-8")
    if any(value is not None for value in (args.window_width, args.window_height, args.product_name, args.identifier)):
        config_path = destination / "tauri.conf.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        window = config["app"]["windows"][0]
        if args.window_width is not None:
            window["width"] = args.window_width
        if args.window_height is not None:
            window["height"] = args.window_height
        if args.product_name is not None:
            config["productName"] = args.product_name
        if args.identifier is not None:
            config["identifier"] = args.identifier
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    runtime = destination / "src" / "runtime.rs"
    source = runtime.read_text(encoding="utf-8")
    needle = '.setup(|app|{let _=app.get_webview_window("main").expect("main window missing");Ok(())})'
    replacement = '.setup(|app|{let window=app.get_webview_window("main").expect("main window missing");if let Some(path)=option_env!("LIFEOS_EVIDENCE_NATIVE_LOG"){let inner=window.inner_size().expect("inner size");let outer=window.outer_size().expect("outer size");let scale=window.scale_factor().expect("scale factor");fs::write(path,format!("{{\\\"kind\\\":\\\"native_window_probe\\\",\\\"inner_size_px\\\":[{},{}],\\\"outer_size_px\\\":[{},{}],\\\"scale_factor\\\":{},\\\"content_recorded\\\":false}}",inner.width,inner.height,outer.width,outer.height,scale)).expect("evidence native log");}Ok(())})'
    if needle not in source:
        raise SystemExit("expected setup anchor missing")
    runtime.write_text(source.replace(needle, replacement), encoding="utf-8")
    original = inventory(CANDIDATE)
    probe = inventory(destination)
    changed = sorted(path for path in set(original) | set(probe) if original.get(path) != probe.get(path))
    runtime_text = (destination / "src" / "runtime.rs").read_text(encoding="utf-8")
    handler = re.search(r"tauri::generate_handler!\[(.*?)\]\)", runtime_text, re.S)
    commands = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    report = {
        "task": "LIFEOS-P3-134",
        "kind": "disposable evidence-only Tauri probe",
        "variant": args.variant,
        "scenario": args.scenario,
        "probe_name": args.probe_name or args.scenario,
        "probe_root": str(destination),
        "native_log": str(args.native_log),
        "candidate_source_delta": changed,
        "allowed_probe_delta": ["src/runtime.rs", "ui/evidence-probe.js", "ui/index.html"] + (["tauri.conf.json"] if any(value is not None for value in (args.window_width, args.window_height, args.product_name, args.identifier)) else []) + (VISUAL if args.variant == "reference" else []),
        "handler_commands": commands,
        "handler_exact_eleven": commands == IPC,
        "content_recorded": False,
        "probe_must_be_deleted_after_evidence": True,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
