#!/usr/bin/env python3
"""Recompute the independent P3-130 review result from review-owned raw evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/tmp/lifeos-p3-130-context-recovery-v1")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ax_contains(name: str, *needles: str) -> dict:
    path = HERE / name
    value = path.read_text(encoding="utf-8") if path.is_file() else ""
    missing = [needle for needle in needles if needle not in value]
    return {"evidence": name, "status": "PASS" if not missing else "FAIL", "missing": missing, "sha256": sha(path) if path.is_file() else None}


def geometry(name: str, expected: str) -> dict:
    path = HERE / name
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []
    final = rows[-1] if rows else {}
    want_w, want_h = (float(item) for item in expected.split("x"))
    actual = final.get("content_bounds", {}).get("size_logical", {})
    ok = (final.get("source") == "actual-tauri-native-window" and final.get("requested_logical") == expected
          and actual.get("width") == want_w and actual.get("height") == want_h)
    return {"evidence": name, "status": "PASS" if ok else "FAIL", "expected_logical": expected,
            "observed_logical": actual, "row_count": len(rows), "sha256": sha(path) if path.is_file() else None}


def main() -> int:
    checks = []
    static = json.loads((HERE / "static_verification.json").read_text(encoding="utf-8"))
    checks.append({"check": "fresh_static_verification", "status": static.get("status"), "sha256": sha(HERE / "static_verification.json")})
    checks.extend([
        ax_contains("actual-confirm-initial.ax.txt", "records: 0", '"today": "empty"', '"context": "empty"', '"capture_record"', '"get_context_recovery"'),
        ax_contains("actual-confirm-captured.ax.txt", "capture_record: saved · candidate", "records: 1 · audit events: 2", "确认纳入此 Project Context"),
        ax_contains("actual-confirm-repeat.ax.txt", "capture_record: idempotent_repeat · candidate", "records: 1 · audit events: 3", "repeats: 1"),
        ax_contains("actual-confirm-selection-removed.ax.txt", "selection_included\": false", "未调用写入 IPC"),
        ax_contains("actual-confirm-confirmed.ax.txt", "confirm_capture_context: saved · confirm", "context\": \"confirmed\"", "audit events: 4"),
        ax_contains("actual-confirm-reopened.ax.txt", "context\": \"confirmed\"", "records: 1 · audit events: 4", "Feedback 结果：confirmed"),
        ax_contains("actual-confirm-context.ax.txt", "PROJECT-BACKED ONLY", "heading confirmed", "无 Person Profile、无 Domain ACL"),
        ax_contains("actual-confirm-memory.ax.txt", "SRC-SYN-WORK-001", "ART-SYN-CONTEXT-RECOVERY-001@v1", "feedback:1", "memory copy: false"),
        ax_contains("actual-reject-rejected.ax.txt", "confirm_capture_context: saved · reject", "context\": \"rejected\"", "Feedback 结果：rejected"),
        ax_contains("actual-mutation-source-fail.ax.txt", "context_evidence_gap", "source_unavailable", "audit events: 2"),
        ax_contains("actual-mutation-tombstone-fail.ax.txt", "context_evidence_gap", "project_tombstoned", "audit events: 2"),
        ax_contains("actual-mutation-authorization-fail.ax.txt", "context_evidence_gap", "authorization_missing", "audit events: 2"),
        geometry("native-geometry-1280x1024.jsonl", "1280x1024"),
        geometry("native-geometry-1160x768.jsonl", "1160x768"),
        geometry("native-geometry-700x760.jsonl", "700x760"),
    ])
    for name in ["mutation-source.json", "mutation-tombstone.json", "mutation-authorization.json"]:
        payload = json.loads((HERE / name).read_text(encoding="utf-8"))
        checks.append({"check": name, "status": "PASS" if payload.get("no_additional_write_after_mutation") else "FAIL",
                       "before_mutation_sha256": payload.get("before_mutation_sha256"),
                       "after_mutation_before_confirm_sha256": payload.get("after_mutation_before_confirm_sha256"),
                       "after_confirm_sha256": payload.get("after_confirm_sha256")})
    regression = json.loads((HERE / "candidate-regression.json").read_text(encoding="utf-8"))
    checks.append({"check": "candidate_regression_supplement", "status": "PASS" if regression.get("exit_code") == 0 and regression.get("five_passed") else "FAIL", "log_sha256": regression.get("log_sha256")})
    root_rejection = json.loads((HERE / "root-fail-closed.json").read_text(encoding="utf-8"))
    checks.append({"check": "runtime_root_fail_closed", "status": "PASS" if root_rejection.get("exit_code") != 0 and root_rejection.get("root_remained_absent") and root_rejection.get("rejected_before_build_output") else "FAIL", "log_sha256": root_rejection.get("log_sha256")})
    cleanup = json.loads((HERE / "cleanup.json").read_text(encoding="utf-8")) if (HERE / "cleanup.json").is_file() else {}
    cleanup_ok = cleanup.get("temporary_root_absent") is True and not TEMP_ROOT.exists()
    checks.append({"check": "exact_cleanup", "status": "PASS" if cleanup_ok else "FAIL", "temporary_root": str(TEMP_ROOT), "temporary_root_absent": not TEMP_ROOT.exists()})

    result = {"task": "LIFEOS-P3-130", "kind": "independent_review_verification", "checks": checks,
              "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"}
    (HERE / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "check_count": len(checks)}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
