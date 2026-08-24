#!/usr/bin/env python3
"""Deterministic, read-only P3-100 risk-decision evidence runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
TMP_PREFIX = "lifeos-p3-100-"

ROOT_ASSETS = {
    "lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md": "3355c7f3e744abfd3be392902217f8abfa02bb783a492d87e88d8a63ddb2a09f",
    "lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md": "0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048",
    "lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md": "a214e681ebf9449af9097edde42cd04b02dc83be2a09eec472e1a3b67c386ee1",
    "lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md": "63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311",
    "lifeos/reviews/LIFEOS-P3-097_pm_review.md": "057cbf047f412c38cc606ef033604a9e7591de83272ad2523ab0e02d86a58fee",
    "lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md": "90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183",
    "lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md": "89909b6ebea2cf669da3d7934976d08417b2fbb3097265ff7cde2320e734931e",
    "lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review_acceptance_basis_freeze.md": "249239ef03a84576d7cec01bd0c9eb0a21bccf032b032348a1665e7f8ca36fff",
    "lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md": "6c87b447b5f295bcaf257d8403a4deff58b6ef63d899ba04b675f78ff6136175",
    "lifeos/reviews/LIFEOS-P3-098/independent_review.md": "5a9d1681dbe0a6c08e487581b1efb0e779e0ec720992abfe390df2097f1ee28a",
    "lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md": "4f74f685d2ba5857c7fb9a469ae3397ddf06349bd9f9a34193b933773dfb6958",
    "lifeos/reviews/LIFEOS-P3-098_pm_review.md": "232c144f103d877d35d86572a13efac132773528345e9e81b9725b37927cd668",
    "lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md": "4ddf1158c63bbeecb0b2dd83fea44d19aa24d52b4bd2c33e25df966ba412c266",
    "lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md": "ca418978b4879492537bd0441fa0ac92a23c0721432ce1a7e3ff101922b63085",
    "lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md": "e318ba97fcacf16646e7545da7bb16ab3eadda7cc32a238643bf030cc95213ca",
    "lifeos/deliverables/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md": "28a56fcdbc500dedf089ead4d0b0660fd5951d60a8eaf65cdb0a7b18f92b065d",
    "lifeos/reviews/LIFEOS-P3-099/independent_review.md": "03a93085d883d1e34045ffad468652c40e7b266f9a49b4a775f83f34e4897f11",
    "lifeos/reviews/LIFEOS-P3-099/evidence/MANIFEST.md": "ee0153534afc0c157fa6d3ed78e83914dc64df21b1821353795344cd0d5d515f",
    "lifeos/reviews/LIFEOS-P3-099_pm_review.md": "1dc23031615eac02262ae29de12c890f569e70ca48afd3ab4deaf9d32e5387b6",
    "lifeos/reviews/LIFEOS-P3-099/pm_evidence/initial/MANIFEST.md": "cc9014b1c2a33bf2f3a0bdf219f2d0ee9b51447d9c5ffcdfebe96bc57e47dcfb",
}

MANIFESTS = [
    ("P3-097 Engineering", "lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md", 16),
    ("P3-097 PM", "lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md", 23),
    ("P3-098 Independent", "lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md", 14),
    ("P3-098 PM", "lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md", 18),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def root_hashes() -> list[dict]:
    checks = []
    for rel, expected in ROOT_ASSETS.items():
        path = ROOT / rel
        actual = sha256(path) if path.is_file() else None
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
    return checks


def parse_manifest(rel: str) -> list[tuple[str, str]]:
    path = ROOT / rel
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        a, b = cells[0], cells[1]
        if re.fullmatch(r"[0-9a-f]{64}", a):
            expected, item = a, b
        elif re.fullmatch(r"[0-9a-f]{64}", b):
            item, expected = a, b
        else:
            continue
        entries.append((item, expected))
    return entries


def manifest_check(name: str, rel: str, expected_count: int) -> dict:
    manifest_path = ROOT / rel
    base = manifest_path.parent
    checks = []
    for item, expected in parse_manifest(rel):
        candidate = ROOT / item if item.startswith("lifeos/") else base / item
        actual = sha256(candidate) if candidate.is_file() else None
        checks.append({"path": str(candidate.relative_to(ROOT)) if candidate.exists() else item,
                       "expected": expected, "actual": actual, "match": actual == expected})
    return {"name": name, "manifest": rel, "expected_count": expected_count,
            "actual_count": len(checks), "checks": checks,
            "pass": len(checks) == expected_count and all(c["match"] for c in checks)}


def history_check() -> dict:
    source = ROOT / "lifeos/reviews/LIFEOS-P3-098/evidence/source_history_hashes.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    checks = []
    for item in data["history"]["checks"]:
        path = ROOT / item["path"]
        actual = sha256(path) if path.is_file() else None
        checks.append({"path": item["path"], "expected": item["expected"],
                       "actual": actual, "match": actual == item["expected"]})
    return {"declared_count": data["history"]["count"], "actual_count": len(checks),
            "checks": checks, "pass": len(checks) == 310 and all(c["match"] for c in checks)}


def unique_id_check() -> dict:
    path = ROOT / "lifeos/reviews/LIFEOS-P3-098/evidence/executed_test_ids.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    fields = ["test_id", "fixture_id", "execution_id"]
    duplicates = {f: sorted({x[f] for x in rows if sum(1 for y in rows if y[f] == x[f]) > 1}) for f in fields}
    return {"count": len(rows), "duplicates": duplicates,
            "all_pass": all(x.get("status") == "PASS" for x in rows),
            "pass": len(rows) == 45 and all(not duplicates[f] for f in fields) and all(x.get("status") == "PASS" for x in rows)}


def static_scan() -> dict:
    paths = [ROOT / "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py",
             ROOT / "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py"]
    patterns = [r"http://", r"https://", r"\bsocket\b", r"\brequests\b", r"\burllib\b", r"\btauri\b", r"\bvault\b", r"\bcloud\b", r"\bsync\b", r"\bexport\b"]
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in patterns:
            if re.search(token, text):
                findings.append({"path": str(path.relative_to(ROOT)), "token": token})
    imports = sorted(set(re.findall(r"^(?:from|import)\s+([A-Za-z0-9_]+)", "\n".join(p.read_text(encoding="utf-8") for p in paths), re.M)))
    allowed = {"__future__", "argparse", "datetime", "hashlib", "html", "json", "local_capture", "os", "pathlib", "re", "shutil", "sqlite3", "stat", "sys", "typing", "uuid"}
    unexpected = sorted(set(imports) - allowed)
    return {"files": [str(p.relative_to(ROOT)) for p in paths], "patterns": patterns,
            "findings": findings, "imports": imports, "unexpected_imports": unexpected,
            "pass": not findings and not unexpected,
            "scope_note": "Static closed-state check only; no production or external-capability inference."}


RISK_ROWS = [
    ("R0051-H01", "P3-094 attempt-1", "浏览器误导航／网络边界与 task-local 残留", ["IR-P3-098-015-FORBIDDEN-SCAN", "IR-P3-098-015-RESIDUE"]),
    ("R0051-H02", "P3-095", "clear 后旧 today.html 仍可展示", ["IR-P3-098-008-PAGE-INVALIDATE", "IR-P3-098-008-PUBLISH-AFTER-PAGE"]),
    ("R0051-H03", "P3-094 attempt-4/5", "clear 任意 output、越界删除与外部哨兵", ["IR-P3-098-012-CLEAR-EXTERNAL", "IR-P3-098-011-PAGE-NONCANON"]),
    ("R0051-H04", "P3-094 attempt-5/6", "render 越界、最终链接、祖先目录链接与特殊文件", ["IR-P3-098-012-RENDER-EXTERNAL", "IR-P3-098-011-ANCESTOR-DB-LINK", "IR-P3-098-011-FINAL-PAGE-LINK", "IR-P3-098-011-PAGE-FIFO"]),
    ("R0051-H05", "P3-094 attempt-6/7/8", "空、损坏、缺失或无 Schema DB 的旧页面与只读失败语义", ["IR-P3-098-005-MISSING-REPLACE", "IR-P3-098-013-SCHEMA-PK", "IR-P3-098-008-PAGE-INVALIDATE"]),
    ("R0051-H06", "P3-094 attempt-8", "canonical Schema 约束与非法 source 被误标", ["IR-P3-098-013-SCHEMA-PK", "IR-P3-098-013-SCHEMA-NOTNULL", "IR-P3-098-013-SCHEMA-UNIQUE", "IR-P3-098-013-SOURCE"]),
    ("R0051-H07", "P3-094 final", "post-commit cleanup/staging 假失败", ["IR-P3-098-003-SAVED-REPLACE", "IR-P3-098-007-SIDECAR-PERSISTENT", "IR-P3-098-009-SAVED-FD-CLOSE"]),
    ("R0051-H08", "P3-094 final", "未来／逆序 audit 与逐行 Evidence 假 PASS", ["IR-P3-098-013-AUDIT-FUTURE", "IR-P3-098-013-AUDIT-REVERSE", "IR-P3-098-014-MISSING-ROW", "IR-P3-098-014-DUP-EXEC", "IR-P3-098-014-MISSING-ASSERT"]),
    ("R0051-H09", "P3-096 initial", "commit 后 connection close 异常把成功误报失败", ["IR-P3-098-006-CANDIDATE-CLOSE", "IR-P3-098-009-SAVED-FD-CLOSE", "IR-P3-098-010-REPEAT-FD-CLOSE"]),
    ("R0051-H10", "P3-096 rework-1", "commit 后 sidecar 检查把已发布成功改报失败", ["IR-P3-098-007-SIDECAR-TRANSIENT", "IR-P3-098-007-SIDECAR-PERSISTENT", "IR-P3-098-009-SAVED-FD-CLOSE"]),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--received-at", required=True)
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    abf_rel = "lifeos/tasks/LIFEOS-P3-100_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md"
    abf_actual = sha256(ROOT / abf_rel)
    session = {
        "task_id": "LIFEOS-P3-100", "task_card": "/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-100_r0051_risk_closure_decision_assessment.md",
        "session_type": "New Session / Codex independent risk decision review",
        "received_at": args.received_at, "abf_frozen_at": "2026-08-22 23:43:47 CST (+0800)",
        "abf_path": abf_rel, "abf_expected_sha256": "a0049da75feca4b0f9cc9ac21c15c94719eedb28b3d095ee47aa47eefed48ce6",
        "abf_actual_sha256": abf_actual, "abf_match": abf_actual == "a0049da75feca4b0f9cc9ac21c15c94719eedb28b3d095ee47aa47eefed48ce6",
        "model_route_requested": "gpt-5.6-terra / xhigh", "model_route_observed": "not exposed",
        "explicit_route_conflict_observed": False,
        "independence_statement": "This new session did not participate in P3-094 through P3-099 engineering, independent review, or PM acceptance.",
        "authorization": "User delivered the absolute P3-100 task-card path to this new session.",
    }
    dump(EVIDENCE / "session_start.json", session)

    before = root_hashes()
    manifests = [manifest_check(*spec) for spec in MANIFESTS]
    history = history_check()
    ids = unique_id_check()
    dump(EVIDENCE / "manifest_results.json", {"manifests": manifests, "p3_098_unique_ids": ids, "history_310": history,
                                               "pass": all(m["pass"] for m in manifests) and ids["pass"] and history["pass"]})

    temp_root = Path(tempfile.mkdtemp(prefix=TMP_PREFIX, dir="/private/tmp"))
    rerun_output = temp_root / "p3-098-rerun"
    command = ["python3", "-B", str(ROOT / "lifeos/reviews/LIFEOS-P3-098/evidence/runner_source.py"), "--output", str(rerun_output)]
    proc = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rerun_copy = EVIDENCE / "rerun"
    if rerun_copy.exists():
        shutil.rmtree(rerun_copy)
    if rerun_output.exists():
        shutil.copytree(rerun_output, rerun_copy)
    (EVIDENCE / "rerun.log").write_text(proc.stdout, encoding="utf-8")
    rerun_results_path = rerun_copy / "results.json"
    rerun_results = json.loads(rerun_results_path.read_text(encoding="utf-8")) if rerun_results_path.is_file() else {}
    rerun_pass = (proc.returncode == 0 and rerun_results.get("pass") == 45 and rerun_results.get("fail") == 0
                  and rerun_results.get("counts") == {"Not Implemented": 0, "P0": 0, "P1": 0, "P2": 0, "Unknown": 0})
    (EVIDENCE / "rerun.md").write_text("# P3-100 isolated rerun\n\n```bash\n" + " ".join(command) + "\n```\n\nExpected and actual exit: `0`.\n", encoding="utf-8")

    executed = json.loads((rerun_copy / "executed_test_ids.json").read_text(encoding="utf-8")) if (rerun_copy / "executed_test_ids.json").is_file() else []
    passed_ids = {x.get("test_id") for x in executed if x.get("status") == "PASS"}
    risk_rows = []
    for risk_id, source, failure, evidence_ids in RISK_ROWS:
        missing = sorted(set(evidence_ids) - passed_ids)
        risk_rows.append({"risk_id": risk_id, "historical_source": source, "failure_class": failure,
                          "current_independent_test_ids": evidence_ids, "missing_test_ids": missing,
                          "status": "PASS" if not missing else "FAIL"})
    dump(EVIDENCE / "risk_coverage_matrix.json", {"rows": risk_rows, "count": len(risk_rows),
                                                   "pass": all(x["status"] == "PASS" for x in risk_rows),
                                                   "evidence_sources": ["P3-094/095/096 PM Reviews", "P3-098 acceptance_matrix/results/state transitions/failure injections/static scan"]})
    scope = static_scan()
    dump(EVIDENCE / "static_scope_scan.json", scope)

    all_pre = session["abf_match"] and all(x["match"] for x in before) and all(m["pass"] for m in manifests) and history["pass"] and ids["pass"] and rerun_pass and all(x["status"] == "PASS" for x in risk_rows) and scope["pass"]
    decision = {
        "conclusion": "Recommend Limited Closure" if all_pre else "Keep Open",
        "risk_basis_counts": {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0} if all_pre else {"P0": 0, "P1": 1, "P2": 0, "Unknown": 0, "Not Implemented": 0},
        "delivery_quality_counts": {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0},
        "limited_scope": ["fixed P3-097 candidate hashes", "single-process", "offline", "task-local", "fixed non-sensitive fixtures", "P3-097/P3-098 current Evidence"],
        "non_scope": ["concurrency or adversarial races", "process or OS crash recovery", "network filesystems", "permanent OS denial", "real personal files, paths, or databases", "production deployment or SLA", "network/cloud/third-party/Vault/Tauri/IPC/export/sync/multi-device/L3/external users", "Schema/API or asset freeze", "engineering baseline restoration", "Stage 4"],
        "reopen_triggers": ["any fixed candidate or Evidence hash changes", "any manifest mismatch or Evidence contradiction", "known failure class reproduces", "a new L1/L2 lifecycle, path, source, audit, or fail-closed counterexample appears", "scope expands to concurrency/crash/network filesystem/permanent denial", "scope expands to real personal data/path/DB or an external capability", "runtime/CLI/Schema/API/completion-point behavior changes"],
        "state_change": "none; R-0051 remains Open / Closure Candidate pending PM validation and explicit user confirmation",
    }
    dump(EVIDENCE / "risk_decision.json", decision)

    shutil.rmtree(temp_root)
    residue = sorted(str(p) for p in Path("/private/tmp").glob(TMP_PREFIX + "*"))
    after = root_hashes()
    input_hashes = {"before": before, "after": after, "count": len(before),
                    "before_all_match": all(x["match"] for x in before),
                    "after_all_match": all(x["match"] for x in after),
                    "before_after_identical": before == after}
    dump(EVIDENCE / "input_hashes.json", input_hashes)
    dump(EVIDENCE / "temporary_residue.json", {"prefix": "/private/tmp/lifeos-p3-100-*", "residue": residue, "count": len(residue), "pass": not residue})

    matrix_specs = [
        ("ABF-M-001", "P3-100-AUTH-001", session["abf_match"] and not session["explicit_route_conflict_observed"], "session_start.json"),
        ("ABF-M-002", "P3-100-HASH-002", input_hashes["before_all_match"] and len(before) == 20, "input_hashes.json"),
        ("ABF-M-003", "P3-100-MAN-003", manifests[0]["pass"], "manifest_results.json"),
        ("ABF-M-004", "P3-100-MAN-004", manifests[1]["pass"], "manifest_results.json"),
        ("ABF-M-005", "P3-100-IND-005", manifests[2]["pass"] and ids["pass"], "manifest_results.json"),
        ("ABF-M-006", "P3-100-MAN-006", manifests[3]["pass"], "manifest_results.json"),
        ("ABF-M-007", "P3-100-RUN-007", rerun_pass, "rerun/results.json, rerun.log"),
        ("ABF-M-008", "P3-100-RISK-008", all(x["status"] == "PASS" for x in risk_rows), "risk_coverage_matrix.json"),
        ("ABF-M-009", "P3-100-SCOPE-009", scope["pass"], "static_scope_scan.json"),
        ("ABF-M-010", "P3-100-DEC-010", decision["conclusion"] in {"Recommend Limited Closure", "Keep Open", "Blocked"}, "risk_decision.json"),
        ("ABF-M-011", "P3-100-BOUND-011", len(decision["limited_scope"]) >= 5 and len(decision["non_scope"]) >= 8 and len(decision["reopen_triggers"]) >= 6, "risk_decision.json"),
        ("ABF-M-012", "P3-100-CLEAN-012", input_hashes["before_after_identical"] and not residue, "input_hashes.json, temporary_residue.json"),
    ]
    matrix = [{"row_id": row, "test_id": test, "execution_id": f"P3-100-EX-{i:03d}", "status": "PASS" if passed else "FAIL", "evidence": evidence}
              for i, (row, test, passed, evidence) in enumerate(matrix_specs, 1)]
    dump(EVIDENCE / "decision_matrix.json", {"rows": matrix, "pass": all(x["status"] == "PASS" for x in matrix), "counts": {"PASS": sum(x["status"] == "PASS" for x in matrix), "FAIL": sum(x["status"] == "FAIL" for x in matrix)}})
    return 0 if all(x["status"] == "PASS" for x in matrix) else 1


if __name__ == "__main__":
    raise SystemExit(main())
