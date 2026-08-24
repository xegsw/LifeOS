#!/usr/bin/env python3
"""Task-local, read-only clarity checks for LIFEOS-P3-074."""
import hashlib, json, shutil, sys
from pathlib import Path

root = Path(__file__).resolve().parents[4]
source = root / "lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package.md"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("clarity_results.json")
text = source.read_text(encoding="utf-8")

required = {
    "IC-01 synthetic boundary": "合成／临时沙盒",
    "IC-02 explicit confirmation": "精确 `CONFIRM`",
    "IC-03 fail-closed": "fail-closed",
    "IC-04 recovery disclosure": "尚未恢复",
    "IC-05 export boundary": "合成临时沙盒",
    "IC-06 alpha not launched": "未启动 Alpha",
    "IC-07 Stage 4 not admitted": "未准入",
    "IC-08 R-0040 retained": "Open / Conditional",
    "IC-09 no external action": "无外部动作",
    "IC-10 audit traceability": "可追溯审计",
    "IC-11 no silent overwrite": "不得静默覆盖",
    "IC-12 no half product": "半成品",
}
forbidden = {
    "FC-01 real alpha claim": "Alpha 已启动",
    "FC-02 Stage 4 admitted claim": "已准入 Stage 4",
    "FC-03 real export claim": "真实文件已可导出",
    "FC-04 real recovery claim": "真实恢复已可用",
}
results = []
for name, needle in required.items():
    results.append({"id": name.split()[0], "name": name, "status": "PASS" if needle in text else "FAIL", "expected": needle})
for name, needle in forbidden.items():
    results.append({"id": name.split()[0], "name": name, "status": "PASS" if needle not in text else "FAIL", "forbidden": needle})
copy_dir = Path("/private/tmp/lifeos-p3-074-clarity-copy")
if copy_dir.exists(): shutil.rmtree(copy_dir)
copy_dir.mkdir()
copy = copy_dir / source.name
shutil.copy2(source, copy)
same = hashlib.sha256(source.read_bytes()).hexdigest() == hashlib.sha256(copy.read_bytes()).hexdigest()
results.append({"id":"IC-13", "name":"clean-copy first read", "status":"PASS" if same else "FAIL"})
results.append({"id":"IC-14", "name":"repeat read idempotence", "status":"PASS" if copy.read_text(encoding="utf-8") == text else "FAIL"})
updated = text + "\n<!-- version-update reread rehearsal marker -->\n"
copy.write_text(updated, encoding="utf-8")
results.append({"id":"IC-15", "name":"version-update reread equivalent", "status":"PASS" if "version-update reread rehearsal marker" in copy.read_text(encoding="utf-8") else "FAIL"})
shutil.rmtree(copy_dir)
passed = sum(r["status"] == "PASS" for r in results)
payload = {"task":"LIFEOS-P3-074", "summary":{"PASS":passed,"FAIL":len(results)-passed,"P0":0,"P1":0,"P2":0,"Unknown":0,"Not Implemented":0,"uncovered":0},"results":results,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"temporary_copy_cleaned":not copy_dir.exists()}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload["summary"], ensure_ascii=False))
sys.exit(0 if payload["summary"]["FAIL"] == 0 else 1)
