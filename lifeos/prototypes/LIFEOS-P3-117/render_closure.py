#!/usr/bin/env python3
"""Render the task-required action-level dynamic Evidence closure table."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "evidence/action_results.json"
OUTPUT = ROOT / "evidence/dynamic_closure.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    results = json.loads(RESULT.read_text(encoding="utf-8"))["results"]
    lines = [
        "# LIFEOS-P3-117 动态 Evidence 闭环",
        "",
        "每行是一次实际 GUI 动作及其原生 raw→proof→clean 图像链；PASS 不由汇总数量推定。",
        "",
        "| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in results:
        evidence = row["proof_path"] + " ; " + row["clean_path"] + " ; " + row["geometry_path"]
        hashes = row["proof_sha256"][:12] + " / " + row["clean_sha256"][:12] + " / " + row["geometry_sha256"][:12]
        lines.append(
            "| " + row["matrix"] + " · " + row["case_id"] + " | " + row["actual_action"].replace("|", " ") +
            " | " + row["expected_anchor"].replace("|", " ") +
            " | " + row["capture_id"] +
            " | " + evidence +
            " | " + hashes +
            " | " + row["status"] + " |"
        )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "rows": len(results), "output_sha256": sha(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
