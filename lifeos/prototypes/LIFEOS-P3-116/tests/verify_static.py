#!/usr/bin/env python3
"""Fail-closed static and fixed-input checks for the P3-116 prototype."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
OUT = ROOT / "evidence" / "results" / "static_results.json"
FIXED = {
    "lifeos/architecture/LifeOS高保真原型IA-V1.0.md": "adcc9daf3b8f0fcf27a13176eabb1581c6079d47b48a26ee88cbaba209704243",
    "lifeos/architecture/LifeOS架构基线V1.0.md": "2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32",
    "lifeos/reviews/LIFEOS-P3-113_pm_review.md": "fc387595ec31db54aaa58daf293c18e1602365f23c2f8a210d924b98f4ec1512",
    "lifeos/reviews/LIFEOS-P3-114_pm_review.md": "72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78",
    "lifeos/deliverables/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract.md": "ccb518b073f5e791a84a18f2e91a37aa008f12ee323596a3357dd96d55242c07",
    "lifeos/reviews/LIFEOS-P3-115_pm_review.md": "f5c0cf27b35619b9450105809255be22aa825f7278dc75859036200e0a19c7f4",
    "lifeos/ACCEPTANCE_GOVERNANCE.md": "86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(test_id: str, label: str, condition: bool, detail: str) -> dict:
    return {"test_id": test_id, "label": label, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    source = {name: (ROOT / name).read_text(encoding="utf-8") for name in ("index.html", "styles.css", "fixtures.js", "app.js")}
    required = ["index.html", "styles.css", "fixtures.js", "app.js", "interaction_contract.md", "state_machine.json", "visual_contract.json", "ia_reconciliation.md"]
    results = [check("P116-S-001", "required prototype files", all((ROOT / item).is_file() for item in required), ", ".join(required))]
    joined = "\n".join(source.values())
    results.append(check("P116-S-002", "no remote/runtime/storage capability", not any(token in joined for token in ("fetch(", "XMLHttpRequest", "WebSocket", "localStorage", "sessionStorage", "navigator.serviceWorker", "https://", "http://")), "scanned HTML/CSS/JS entry sources"))
    results.append(check("P116-S-003", "primary IA is constrained", all(f'navButton("{item}"' in source["app.js"] for item in ("today", "me", "contexts", "memory")) and 'navButton("work"' not in source["app.js"] and 'navButton("health"' not in source["app.js"], "Today/Me/Contexts/Memory only"))
    results.append(check("P116-S-004", "person and context semantics are explicit", "Person 是一级主体" in (ROOT / "ia_reconciliation.md").read_text(encoding="utf-8") and "Project 只是其中一种 Context 类型" in source["app.js"], "reconciliation and UI copy"))
    results.append(check("P116-S-005", "semantic accessibility hooks", all(token in joined for token in ("skip-link", "main-content", ":focus-visible", "Escape", "prefers-reduced-motion")), "skip/focus/keyboard/motion hooks"))
    results.append(check("P116-S-006", "all required product views are coded", all(token in source["app.js"] for token in ("todayPage", "mePage", "contextsPage", "contextDetailPage", "memoryPage", "memoryDetailPage", "workspacePage", "aiPanel")), "nine required view states"))
    results.append(check("P116-S-007", "explicit synthetic and no-persistence disclosure", "固定合成演示" in joined and "不会保存" in joined and "非持久化" in joined, "visible product boundary copy"))
    results.append(check("P116-S-008", "no shell violations in implementation", "notification" not in source["app.js"].lower() and "bell" not in source["app.js"].lower() and "avatar" not in source["app.js"].lower(), "no prohibited shell feature is implemented"))
    try:
        state_machine = json.loads((ROOT / "state_machine.json").read_text(encoding="utf-8"))
        visual = json.loads((ROOT / "visual_contract.json").read_text(encoding="utf-8"))
        results.append(check("P116-S-009", "machine-readable contracts parse", len(state_machine["transitions"]) >= 10 and len(visual["responsive"]) == 3, "state machine and visual contract"))
    except (OSError, KeyError, json.JSONDecodeError) as err:
        results.append(check("P116-S-009", "machine-readable contracts parse", False, repr(err)))

    input_rows = []
    for rel, expected in FIXED.items():
        actual = sha256(WORKSPACE / rel)
        input_rows.append({"path": rel, "expected_sha256": expected, "actual_sha256": actual, "status": "PASS" if actual == expected else "FAIL"})
    (ROOT / "evidence" / "fixed_inputs.json").write_text(json.dumps({"abf_id": "ABF-P3-116-v1", "inputs": input_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(check("P116-S-010", "seven fixed inputs match ABF", all(row["status"] == "PASS" for row in input_rows), "fixed_inputs.json"))
    results.append(check("P116-S-011", "Global AI bar and side panel are one entry", all(token in source["app.js"] for token in ("data-ai-form", "ai-panel-composer", "state.aiOpen = true", "发送并展开 Global AI", "data-action=\"capture\"")), "bar opens contextual panel; Quick Capture remains a secondary action"))
    results.append(check("P116-S-012", "Me, Memory, and Workspace share the visual shell", all(token in source["app.js"] for token in ("shellChrome", "me-reference-stack", "memory-reference-grid", "workspace-reference", "workspace-shell", "workspace-future")), "three reference views use the same shell without changing primary IA or Future Agent disclosure"))
    payload = {"runner": "tests/verify_static.py", "overall": "PASS" if all(row["status"] == "PASS" for row in results) else "FAIL", "results": results}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
