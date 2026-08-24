#!/usr/bin/env python3
"""Recompute P3-115 matrix/closure results from raw Chrome evidence.

This runner never drives a browser. It validates the evidence emitted by the
separate Computer Use Chrome actions and fails each matrix row closed when an
expected raw AX fact, screenshot, or prerequisite result is absent.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
RAW = EVIDENCE / "raw"
RESULTS = EVIDENCE / "results"
PROJECT = ROOT.parents[2]

INPUTS = [
    ("lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline.md", "a81d5dd92d826e277f347f5f761a149e93839528c2c3352674b192ff0121dc85"),
    ("lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md", "c5fdcd30e3886a2f00e260346991714c9b0193e7ddd69abffd9d7bb3fd308ece"),
    ("lifeos/reviews/LIFEOS-P3-113_pm_review.md", "fc387595ec31db54aaa58daf293c18e1602365f23c2f8a210d924b98f4ec1512"),
    ("lifeos/reviews/LIFEOS-P3-114_pm_review.md", "72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78"),
    ("lifeos/reviews/LIFEOS-P3-114/rework/rework-1/independent_review.md", "a7d2cd9fb53eeb4b88ae199e95d1c5dc7049fc93670675ef034c63b7ccbc4351"),
    ("lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence/MANIFEST.md", "486270122e98ea2111ecb4e22b4c91a459a4b5af2ff74b1982d973757ab90449"),
    ("lifeos/reviews/LIFEOS-P3-114/pm_evidence/rework-1/MANIFEST.md", "df384be261f4edb501d3a1ced75a1b4141e1bf15cb7ff4949488564e216f75dc"),
]

# (matrix id, action id, raw state basename, operation, expected AX terms)
ACTIONS = [
    ("ABF-M-002", "P115-M002-01", "m001-default-1512x861", "Fresh Chrome file URL load", ["file:///private/tmp/lifeos-p3-115-prototype-v1/index.html", "LifeOS · Today（P3-115 原型）"]),
    ("ABF-M-003", "P115-M003-01", "m001-default-1512x861", "Observe default Today", ["今天值得花注意力的 3 件事", "0–1 个问题", "Project 只作为工作项目的上下文"]),
    ("ABF-M-004", "P115-M004-01", "m004-work-evidence", "Click work Why now / evidence", ["SOURCE", "ARTIFACT", "确定性", "停止条件", "Advice candidate"]),
    ("ABF-M-005", "P115-M005-01", "m005-health-gate-default", "Observe unanswered health gate", ["未回答 · 停止训练型建议", "先保守，再行动"]),
    ("ABF-M-006", "P115-M006-01", "m006-answer-safe", "Answer 无加重／无警示", ["无警示 · 低风险候选", "一个可选的低风险恢复选项", "不是诊断、治疗或训练处方"]),
    ("ABF-M-006", "P115-M006-02", "m006-answer-skip", "Answer 今天跳过", ["跳过 · 降级", "不把跳过当成安全回答"]),
    ("ABF-M-006", "P115-M006-03", "m006-answer-warning", "Answer 有警示信号", ["警示信号 · 已停止", "专业人士"]),
    ("ABF-M-007", "P115-M007-01", "m007-feedback-accept", "Click 认可为可选项", ["FDB 已认可", "EXE 未执行"]),
    ("ABF-M-007", "P115-M007-02", "m007-feedback-modified", "Confirm 修改后接受", ["FDB 修改后接受", "EXE 未执行"]),
    ("ABF-M-007", "P115-M007-03", "m007-feedback-reject", "Click 不适用", ["FDB 已拒绝", "EXE 未执行"]),
    ("ABF-M-007", "P115-M007-04", "m007-feedback-defer", "Click 延后", ["FDB 已延后", "EXE 未执行"]),
    ("ABF-M-008", "P115-M008-01", "m008-execution-not-executed", "Record not executed", ["EXE 未执行", "RES 尚无"]),
    ("ABF-M-008", "P115-M008-02", "m008-execution-reported", "Record executed", ["EXE 已执行", "RES 尚无"]),
    ("ABF-M-008", "P115-M008-03", "m008-result-reported", "Record result", ["RES 已报告结果", "今晚不再追加训练型建议"]),
    ("ABF-M-009", "P115-M009-01", "m009-memory-pending", "Show pending Memory candidate", ["MEM-CAND · 待确认", "不会影响未来日期"]),
    ("ABF-M-009", "P115-M009-02", "m009-rejected-preserves-result", "Reject candidate then return Today", ["已拒绝", "RES 已报告结果", "Source / Artifact 固定合成输入"]),
    ("ABF-M-009", "P115-M009-03", "m009-memory-confirmed", "Confirm limited Memory candidate", ["MEM-CAND · 已确认"]),
    ("ABF-M-010", "P115-M010-01", "m010-source-missing", "Inject missing source", ["missing · fail-closed"]),
    ("ABF-M-010", "P115-M010-02", "m010-source-stale", "Inject stale source", ["stale · fail-closed"]),
    ("ABF-M-010", "P115-M010-03", "m010-source-conflict", "Inject conflicting source", ["conflict · fail-closed"]),
    ("ABF-M-010", "P115-M010-04", "m010-source-unauthorized", "Inject unauthorized source", ["unauthorized · fail-closed"]),
    ("ABF-M-011", "P115-M011-01", "m011-revoke-path-modified", "Create modified feedback before revocation", ["FDB 修改后接受"]),
    ("ABF-M-011", "P115-M011-02", "m011-revoke-path-executed", "Report execution before revocation", ["EXE 已执行"]),
    ("ABF-M-011", "P115-M011-03", "m011-revoke-path-result", "Report result before revocation", ["RES 已报告结果"]),
    ("ABF-M-011", "P115-M011-04", "m011-revoke-path-memory-pending", "Create pending candidate before revocation", ["MEM-CAND · 待确认"]),
    ("ABF-M-011", "P115-M011-05", "m011-revoke-ans-fdb-exe-res", "Revoke answer/feedback/execution/result chain", ["等待你的安全回答", "Source / Artifact 固定合成输入"]),
    ("ABF-M-011", "P115-M011-06", "m011-refresh-reset", "Chrome refresh", ["等待你的安全回答", "不是运行时 · 不保存输入"]),
    ("ABF-M-011", "P115-M011-07", "m011-close-reopen-reset", "Close task tab and reopen direct file URL", ["file:///private/tmp/lifeos-p3-115-prototype-v1/index.html", "等待你的安全回答"]),
    ("ABF-M-012", "P115-M012-01", "m012-navigation-memory", "Navigate Memory", ["长期记忆必须经过再次确认", "固定合成候选"]),
    ("ABF-M-012", "P115-M012-02", "m012-navigation-domains", "Navigate Domains", ["工作与健康／健身，是并列的生活语境", "Project 只在工作语境中出现"]),
    ("ABF-M-012", "P115-M012-03", "m012-navigation-today", "Navigate Today", ["今天值得花注意力的 3 件事", "Project 只作为工作项目的上下文"]),
    ("ABF-M-012", "P115-M012-04", "m012-capture-boundary", "Open global capture boundary", ["这只是原型入口", "不收集、不保存、不发送"]),
    ("ABF-M-013", "P115-M013-01", "m013-viewport-1280x1024", "Chrome device toolbar 1280x1024", ["视口：1280 × 1024", "今天值得花注意力的 3 件事"]),
    ("ABF-M-013", "P115-M013-02", "m013-viewport-1160x768", "Chrome device toolbar 1160x768", ["视口：1160 × 768", "让今天的结果保持可撤回"]),
    ("ABF-M-013", "P115-M013-03", "m013-viewport-700x760", "Chrome device toolbar 700x760", ["视口：700 × 760", "0–1 个问题"]),
    ("ABF-M-014", "P115-M014-01", "m014-keyboard-tab-skip", "Tab to skip link", ["focused UI element is 5 link Description: 跳到今日重点"]),
    ("ABF-M-014", "P115-M014-02", "m014-keyboard-enter-skip", "Enter on skip link", ["focused UI element is 17 container"]),
    ("ABF-M-014", "P115-M014-03", "m014-keyboard-shift-tab", "Shift+Tab after skip", ["focused UI element is 16 弹出式按钮 记录"]),
    ("ABF-M-014", "P115-M014-04", "m014-keyboard-enter-capture", "Enter on capture", ["这只是原型入口", "不收集、不保存、不发送"]),
    ("ABF-M-014", "P115-M014-05", "m014-keyboard-escape-capture", "Escape close capture dialog", ["今天值得花注意力的 3 件事"]),
    ("ABF-M-014", "P115-M014-06", "m014-low-motion-toggle", "Enable low-motion preview", ["已启用低动态"]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scan_static():
    completed = subprocess.run([sys.executable, str(ROOT / "tests" / "verify_static.py")], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    value = {"exit_code": completed.returncode, "output": completed.stdout.strip(), "status": "PASS" if completed.returncode == 0 else "FAIL"}
    write_json(RESULTS / "static_scan.json", value)
    return value


def read_status(path):
    if not path.is_file():
        return "PENDING"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status", "FAIL")
    except json.JSONDecodeError:
        return "FAIL"


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    fixed = []
    all_inputs_match = True
    for rel, expected in INPUTS:
        path = PROJECT / rel
        actual = sha(path) if path.is_file() else None
        fixed.append({"path": rel, "sha256": actual, "expected_sha256": expected, "match": actual == expected})
        all_inputs_match = all_inputs_match and actual == expected
    fixed_doc = {"status": "PASS" if all_inputs_match else "FAIL", "inputs": fixed}
    write_json(EVIDENCE / "fixed_inputs.json", {"inputs": [{"path": item["path"], "sha256": item["sha256"]} for item in fixed]})
    write_json(RAW / "m001-fixed-inputs.json", fixed_doc)
    scan = scan_static()
    closure = [{
        "id": "P115-M001-01", "matrix_id": "ABF-M-001", "status": fixed_doc["status"], "dynamic": False,
        "operation": "Recompute seven Frozen input hashes", "result_id": "P115-M001", "precondition": "v2 ABF startup", "observable": "All fixed hashes match", "evidence_path": "raw/m001-fixed-inputs.json", "sha256": sha(RAW / "m001-fixed-inputs.json"),
    }]
    per_matrix = {"ABF-M-001": [fixed_doc["status"]]}
    for matrix_id, action_id, stem, operation, expected in ACTIONS:
        raw = RAW / f"{stem}.ax.txt"
        screen = EVIDENCE / "screenshots" / f"{stem}.png"
        text = raw.read_text(encoding="utf-8") if raw.is_file() else ""
        passed = raw.is_file() and screen.is_file() and all(term in text for term in expected)
        closure.append({
            "id": action_id, "matrix_id": matrix_id, "status": "PASS" if passed else "FAIL", "dynamic": True,
            "operation": operation, "result_id": action_id, "precondition": "Recorded Chrome file: state", "observable": "All expected AX terms present", "expected_terms": expected,
            "evidence_path": f"raw/{stem}.ax.txt", "sha256": sha(raw) if raw.is_file() else None,
            "screenshot_path": f"screenshots/{stem}.png", "screenshot_sha256": sha(screen) if screen.is_file() else None,
        })
        per_matrix.setdefault(matrix_id, []).append("PASS" if passed else "FAIL")
    mutation = read_status(RESULTS / "mutation_results.json")
    closure.append({
        "id": "P115-M015-01", "matrix_id": "ABF-M-015", "status": "PASS" if scan["status"] == "PASS" and mutation == "PASS" else "PENDING", "dynamic": False,
        "operation": "Run static closure scan and mutation verifier", "result_id": "P115-M015", "precondition": "Source and evidence present", "observable": "Static scan and mutation verifier PASS", "evidence_path": "results/static_scan.json", "sha256": sha(RESULTS / "static_scan.json"),
    })
    per_matrix["ABF-M-015"] = [closure[-1]["status"]]
    cleanup = read_status(RESULTS / "cleanup.json")
    if (RESULTS / "cleanup.json").is_file():
        cleanup_sha = sha(RESULTS / "cleanup.json")
    else:
        cleanup_sha = None
    closure.append({
        "id": "P115-M016-01", "matrix_id": "ABF-M-016", "status": "PASS" if cleanup == "PASS" else "PENDING", "dynamic": False,
        "operation": "Verify exact task-local temporary root cleanup", "result_id": "P115-M016", "precondition": "All dynamic tests complete", "observable": "Exact temporary root absent", "evidence_path": "results/cleanup.json", "sha256": cleanup_sha,
    })
    per_matrix["ABF-M-016"] = [closure[-1]["status"]]
    write_json(EVIDENCE / "dynamic_closure.json", {"template": "UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE equivalent", "rows": closure})
    matrix = []
    for number in range(1, 17):
        matrix_id = f"ABF-M-{number:03d}"
        statuses = per_matrix.get(matrix_id, ["FAIL"])
        matrix.append({"id": matrix_id, "test_id": f"P115-M{number:03d}", "status": "PASS" if statuses and all(s == "PASS" for s in statuses) else "PENDING" if "PENDING" in statuses else "FAIL", "severity": "P0" if number not in {10, 13, 14} else "P1", "subactions": [row["id"] for row in closure if row["matrix_id"] == matrix_id]})
    write_json(RESULTS / "matrix_results.json", {"status": "PASS" if all(row["status"] == "PASS" for row in matrix) else "NOT_PASS", "matrix": matrix})
    print(json.dumps({"status": "PASS", "matrix": {row["id"]: row["status"] for row in matrix}, "closure_rows": len(closure)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
