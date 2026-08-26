#!/usr/bin/env python3
"""Build machine-readable closure and a human-readable manifest from verified Rework-1 evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
ORDER = [
    "today-empty", "me", "contexts", "context-detail", "memory", "memory-detail",
    "global-ai", "ai-workspace", "settings", "capture-one", "repeat-one",
    "capture-two", "refresh", "closed", "reopen-today",
]
CLOSURE_ROWS = [
    ("M-001", "M-001", None, "Preflight preserved initial evidence and recorded model confirmation."),
    ("M-004-01", "M-004", "today-empty", "Actual packaged-app Today empty state."),
    ("M-004-02", "M-004", "me", "Actual manual navigation to Me."),
    ("M-004-03a", "M-004", "contexts", "Actual manual navigation to Contexts."),
    ("M-004-03b", "M-004", "context-detail", "Actual manual navigation to Context Detail."),
    ("M-004-04a", "M-004", "memory", "Actual manual navigation to Memory."),
    ("M-004-04b", "M-004", "memory-detail", "Actual manual navigation to Memory Detail."),
    ("M-004-05a", "M-004", "global-ai", "Actual manual opening of Global AI."),
    ("M-004-05b", "M-004", "ai-workspace", "Actual manual expansion of AI Workspace."),
    ("M-004-06", "M-004", "settings", "Actual manual navigation to Settings."),
    ("M-005", "M-005", "today-empty", "Restricted-offline packaged runtime status."),
    ("M-006", "M-006", "capture-one", "First fixed synthetic capture."),
    ("M-007", "M-007", "repeat-one", "Repeat of the first fixed synthetic capture."),
    ("M-008", "M-008", "capture-two", "Second fixed synthetic capture."),
    ("M-009", "M-009", "refresh", "Manual Today refresh."),
    ("M-010-01", "M-010", "closed", "Manual packaged-app close."),
    ("M-010-02", "M-010", "reopen-today", "Manual observation after same-bundle reopen."),
    ("M-015", "M-015", None, "Exact temporary-root cleanup after final user close."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REWORK).as_posix()


def main() -> int:
    result_path = REWORK / "rework-results.json"
    results = json.loads(result_path.read_text(encoding="utf-8"))
    if results.get("result") != "PASS" or any(row.get("result") != "PASS" for row in results.get("rows", {}).values()):
        print("verified results are not complete PASS", file=sys.stderr)
        return 1
    steps = {step: json.loads((REWORK / "steps" / f"{step}.json").read_text(encoding="utf-8")) for step in ORDER}
    closure = []
    for closure_id, acceptance_id, step, operation in CLOSURE_ROWS:
        if step is None:
            evidence_path = "preflight.json" if closure_id == "M-001" else "cleanup.json"
            evidence = REWORK / evidence_path
            closure.append({
                "closure_id": closure_id,
                "acceptance_id": acceptance_id,
                "operation": operation,
                "structured_result_id": "R1-PREFLIGHT" if closure_id == "M-001" else "R1-final",
                "visual": None,
                "log": {"path": evidence_path, "sha256": sha256(evidence)},
                "result": "PASS",
            })
            continue
        payload = steps[step]
        visual = payload.get("screenshot")
        closure.append({
            "closure_id": closure_id,
            "acceptance_id": acceptance_id,
            "operation": operation,
            "structured_result_id": payload["structured_result_id"],
            "manual_attestation": payload["attestation"],
            "visual": visual,
            "log": payload["log_snapshot"],
            "db_sha256": payload["db"].get("sha256"),
            "result": payload["result"],
        })
    generated_at = datetime.now(timezone.utc).isoformat()
    closure_payload = {
        "schema": "lifeos-p3-120/rework-1-dynamic-closure-v1",
        "generated_at_utc": generated_at,
        "actual_model": "gpt-5.6-terra",
        "actual_reasoning_effort": "xhigh",
        "operation_mode": "user-manual packaged-app interactions; capture/log/DB verification only",
        "rows": closure,
        "result": "PASS",
    }
    closure_path = REWORK / "DYNAMIC_CLOSURE.json"
    closure_path.write_text(json.dumps(closure_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifact_paths = [
        REWORK / "TEST_DESIGN.md", REWORK / "preflight.json", REWORK / "session.json",
        REWORK / "actual-app.log", REWORK / "build-bundle.log", REWORK / "cleanup.json",
        REWORK / "rework-results.json", closure_path,
    ]
    artifact_paths.extend(REWORK / "steps" / f"{step}.json" for step in ORDER)
    artifact_paths.extend(REWORK / "logs" / f"{step}.app.log" for step in ORDER)
    artifact_paths.extend(REWORK / "screenshots" / f"{step}.png" for step in ORDER if step != "closed")
    artifact_paths.extend(sorted((REWORK / "tools").glob("*.py")))
    manifest = [
        "# LIFEOS-P3-120 Rework-1 Evidence Manifest",
        "",
        "## Result",
        "",
        "`PASS` — post-cleanup verifier passed all M-001, M-004–M-010 and M-015 rows. This is an execution self-check, not PM acceptance.",
        "",
        "## Scope and provenance",
        "",
        "- Rework authority: PM Review `LIFEOS-P3-120_pm_review.md`, Rework 1/2 / User Adopted / Remediation Authorized.",
        "- Operation: user-manual packaged Tauri app; no Computer Use, AppleScript, AX, CDP, HTTP, WebDriver, browser control, P3-119 helper, source-state contract, or unit test substituted for dynamic action evidence.",
        "- Model confirmation: `gpt-5.6-terra` with `xhigh`, preserved in `preflight.json`.",
        "- Initial candidate Evidence remains read-only; its verified hashes are recorded in `preflight.json`.",
        "- Temporary root was exactly `/private/tmp/lifeos-p3-120-runtime-mvp-v1` and is absent after `cleanup.json`.",
        "",
        "## Acceptance mapping",
        "",
        "| Acceptance ID | Result | Primary Evidence |",
        "|---|---|---|",
    ]
    for acceptance_id, row in results["rows"].items():
        manifest.append(f"| {acceptance_id} | {row['result']} | {', '.join(row['evidence'])} |")
    manifest.extend(["", "## File hashes", "", "| Path | SHA-256 |", "|---|---|"])
    for artifact in sorted(set(artifact_paths)):
        if artifact.is_file() and not artifact.is_symlink():
            manifest.append(f"| `{relative(artifact)}` | `{sha256(artifact)}` |")
    manifest.append("")
    (REWORK / "MANIFEST.md").write_text("\n".join(manifest), encoding="utf-8")
    print(json.dumps({"result": "PASS", "closure_rows": len(closure), "artifact_count": len(artifact_paths)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
