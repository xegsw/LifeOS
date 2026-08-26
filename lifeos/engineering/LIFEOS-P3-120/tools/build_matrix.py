#!/usr/bin/env python3
"""Produce the non-self-referential, row-level ABF matrix from completed evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest()


def result_for(payload: dict, identifier: str) -> bool:
    return any(row.get("id") == identifier and row.get("result") == "PASS" for row in payload.get("checks", []))


def row(identifier: str, action: str, files: list[str], passed: bool) -> dict:
    return {
        "row_id": identifier,
        "action": action,
        "result": "PASS" if passed else "FAIL",
        "evidence": [{"path": f"evidence/{name}", "sha256": sha256(name)} for name in files],
    }


def main() -> int:
    fixed = load("fixed-inputs.json")
    build = load("build-results.json")
    static = load("static-results.json")
    ui = load("ui-state-contract-results.json")
    actual = load("actual-app-results.json")
    runtime = load("runtime-results.json")
    negative = load("negative-results.json")
    cleanup = load("cleanup.json")

    rows = [
        row("ABF-M-001", "复算 Frozen 输入、ABF 与 72/72 positive source allowlist。", ["fixed-inputs.json", "candidate-inventory.json"], fixed["result"] == "PASS"),
        row("ABF-M-002", "执行 locked/offline Cargo test、release build 与 macOS app bundle。", ["build-results.json", "build-test.log", "build-binary.log", "build-bundle.log"], build["result"] == "PASS"),
        row("ABF-M-003", "扫描 Rust IPC、capability、renderer 与 CSP 边界。", ["static-results.json"], static["result"] == "PASS"),
        row("ABF-M-004", "实际启动/停止/重开 `.app`；将核心页面可达性按无 GUI 注入的 source-state contract 单独核对。", ["actual-app-results.json", "actual-app-launch.log", "actual-app-reopen.log", "actual-app-process.trace", "support-images/actual-app-today.png", "ui-state-contract-results.json"], result_for(actual, "P120-M004") and ui["result"] == "PASS"),
        row("ABF-M-005", "核对 actual-app 的 runtime_status 日志与结构化 Runtime status。", ["actual-app-results.json", "runtime-results.json"], result_for(actual, "P120-M005-actual-app") and result_for(runtime, "P120-M005")),
        row("ABF-M-006", "从空合成 DB 显式提交 capture one，再从 Today 找回。", ["runtime-results.json", "runtime-test.log"], result_for(runtime, "P120-M006")),
        row("ABF-M-007", "重复提交 capture one，并核对幂等身份与回执。", ["runtime-results.json", "runtime-test.log"], result_for(runtime, "P120-M007")),
        row("ABF-M-008", "提交 capture two，并核对两条固定合成原文的顺序。", ["runtime-results.json", "runtime-test.log"], result_for(runtime, "P120-M008")),
        row("ABF-M-009", "刷新 Today，并核对 DB SHA、行数与身份不漂移。", ["runtime-results.json", "runtime-test.log"], result_for(runtime, "P120-M009")),
        row("ABF-M-010", "同一 synthetic DB 的关闭重开读取，核对两条记录。", ["runtime-results.json", "runtime-test.log", "actual-app-results.json"], result_for(runtime, "P120-M010") and result_for(actual, "P120-M004")),
        row("ABF-M-011", "验证路径逃逸、链接/硬链接/sidecar 与篡改 schema/content 的拒绝。", ["negative-results.json", "build-test.log"], all(result_for(negative, item) for item in ["P120-M011-A", "P120-M011-B", "P120-M011-C"])),
        row("ABF-M-012", "验证非法输入、额外 IPC 字段与注入 DB 失败均在变更前 fail-closed。", ["negative-results.json", "runtime-results.json", "runtime-test.log"], all(result_for(negative, item) for item in ["P120-M012-A", "P120-M012-B", "P120-M012-C"]) and result_for(runtime, "P120-M012")),
        row("ABF-M-013", "核对 Person-centered 页面/展开态与 runtime、fixture、AI candidate、confirmed identity。", ["static-results.json", "ui-state-contract-results.json", "support-images/actual-app-today.png"], static["result"] == "PASS" and ui["result"] == "PASS"),
        row("ABF-M-014", "核对 clear/export/permission/recovery/file/network/model/new IPC 关闭态。", ["static-results.json", "negative-results.json"], all(result_for(static, item) for item in ["S-001", "S-003", "S-004", "S-006"])),
        row("ABF-M-015", "复核不可变输入并精确清理唯一临时根。", ["fixed-inputs.json", "cleanup.json"], fixed["result"] == "PASS" and cleanup["result"] == "PASS" and cleanup.get("target_absent_after") is True),
    ]
    passed = all(entry["result"] == "PASS" for entry in rows)
    payload = {
        "schema": "lifeos-p3-120/abf-matrix-v1",
        "abf_id": "ABF-P3-120-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "rows": rows,
        "counts": {"P0": 0 if passed else 1, "P1": 0, "P2": 0, "Unknown": 0 if passed else 1, "Not Implemented": 0 if passed else 1},
        "result": "PASS" if passed else "FAIL",
    }
    (EVIDENCE / "matrix-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "rows": len(rows)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
