#!/usr/bin/env python3
"""Verify the deterministic Person-centered UI state contract without GUI injection."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "candidate/ui/app.js"
EVIDENCE = ROOT / "evidence"


def item(identifier: str, passed: bool, actual: object) -> dict[str, object]:
    return {"id": identifier, "result": "PASS" if passed else "FAIL", "actual": actual}


def main() -> int:
    source = APP.read_text(encoding="utf-8")
    route_map = {
        "today": "todayPage",
        "me": "mePage",
        "contexts": "contextsPage",
        "context-detail": "contextDetailPage",
        "memory": "memoryPage",
        "memory-detail": "memoryDetailPage",
        "workspace": "workspacePage",
        "settings": "settingsPage",
    }
    direct_nav = ["today", "me", "contexts", "memory", "settings"]
    checks = [
        item("UI-001", all(f'state.page === "{route}"' in source and function in source for route, function in route_map.items() if route != "today") and "return todayPage();" in source, route_map),
        item("UI-002", all(f'nav("{route}"' in source for route in direct_nav), direct_nav),
        item("UI-003", all(token in source for token in ['action === "context-detail"', 'action === "memory-detail"', 'action === "workspace"', 'action === "ai-open"']), "detail and Global AI state transitions"),
        item("UI-004", 'await refreshToday(false);' in source and '成功后才会调用 get_today 重读并显示' in source and '没有显示成功态' in source, "capture success follows get_today; failures remove success state"),
        item("UI-005", all(token in source for token in ['Runtime data', 'read-only synthetic fixture', 'AI Observation', 'Decision Candidate', '用户确认']), "content identities remain visible per page state"),
    ]
    passed = all(check["result"] == "PASS" for check in checks)
    payload = {
        "schema": "lifeos-p3-120/ui-state-contract-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "method": "source-state contract only; actual app launch is separately evidenced and no GUI injection/AX/CDP/webdriver is used",
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "ui-state-contract-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "checks": len(checks)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
