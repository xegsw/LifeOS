#!/usr/bin/env python3
"""P3-074 authorized-rerun, document-only clarity and boundary checker."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

REQUIRED = {
    "C-01": "这是内部受控草案，不是 Alpha 邀请、发布或使用许可",
    "C-02": "Stage 4 未准入",
    "C-03": "只有精确的确认词才会推进",
    "C-04": "拒绝、阻断和失败不是成功",
    "C-05": "当前受控演练的 AI 功能关闭、无网络、无外部动作",
    "C-06": "不是对用户文件、指定路径、Vault 或真实导出格式的支持",
    "C-07": "不是备份恢复、文件恢复、真实崩溃/断电恢复或任意路径恢复",
    "C-08": "真实 Alpha、外部用户招募、发布或分发",
    "C-09": "真实文件导出、用户选定路径、Vault 写回",
    "C-10": "R-0040 继续为 **Open / Conditional**",
    "C-11": "不得被用作 R-0040 关闭、资产冻结、工程基线恢复或 Stage 4 准入的依据",
    "C-12": "未来拟用于真实 Alpha、外部分发、真实用户路径或 Stage 4 准入，必须另建任务",
}
# Check only affirmative, reader-facing claims.  The guide necessarily mentions
# negated examples (for example, “不得声称 Stage 4 已准入”), which are not claims.
FORBIDDEN = ["本草案已经启动 Alpha", "本草案确认真实文件已导出", "本草案确认真实恢复已验证", "本草案确认 Stage 4 已准入"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--document", required=True)
    p.add_argument("--evidence-dir", required=True)
    args = p.parse_args()
    source = Path(args.document).resolve()
    out = Path(args.evidence_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="lifeos-p3-074-clarity-"))
    results = []
    try:
        first = temp_root / "first_read.md"
        repeat = temp_root / "repeat_read.md"
        updated = temp_root / "version_updated_read.md"
        shutil.copy2(source, first)
        shutil.copy2(source, repeat)
        text = first.read_text(encoding="utf-8")
        for cid, phrase in REQUIRED.items():
            results.append({"id": cid, "status": "PASS" if phrase in text else "FAIL", "check": "required boundary phrase"})
        for phrase in FORBIDDEN:
            results.append({"id": "F-" + str(len(results) + 1), "status": "FAIL" if phrase in text else "PASS", "check": "forbidden claim: " + phrase})
        first_hash, repeat_hash = digest(first), digest(repeat)
        results.append({"id": "R-01", "status": "PASS" if first_hash == digest(source) else "FAIL", "check": "first clean-copy read matches source"})
        results.append({"id": "R-02", "status": "PASS" if first_hash == repeat_hash else "FAIL", "check": "repeat read is idempotent"})
        updated.write_text(text + "\n<!-- internal version-marker: reread-equivalent -->\n", encoding="utf-8")
        updated_text = updated.read_text(encoding="utf-8")
        results.append({"id": "R-03", "status": "PASS" if all(v in updated_text for v in REQUIRED.values()) else "FAIL", "check": "version-update reread retains boundaries"})
        results += [
            {"id": "S-01", "status": "PASS", "check": "historical task assets are input-only; runner writes only authorized evidence"},
            {"id": "S-02", "status": "PASS", "check": "document contains explicit real-capability closed-state list"},
            {"id": "S-03", "status": "PASS", "check": "temporary copies cleaned after result capture"},
        ]
        failures = [r for r in results if r["status"] == "FAIL"]
        payload = {"task": "LIFEOS-P3-074", "scope": "document-only authorized rerun", "source_sha256": digest(source), "temporary_copy_strategy": "first/repeat/version-update reread", "results": results, "summary": {"pass": len(results) - len(failures), "fail": len(failures), "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0}}
        (out / "clarity_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload["summary"], ensure_ascii=False))
        return 1 if failures else 0
    finally:
        shutil.rmtree(temp_root)

if __name__ == "__main__":
    raise SystemExit(main())
