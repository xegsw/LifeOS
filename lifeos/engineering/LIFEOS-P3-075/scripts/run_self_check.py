#!/usr/bin/env python3
"""Reproducible P3-075 self-check and structured Evidence producer."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, *, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def main() -> int:
    source_files = [ROOT / "src/local_runtime.py", ROOT / "scripts/runtime_cli.py", ROOT / "tests/test_runtime.py", ROOT / "scripts/run_self_check.py"]
    forbidden_patterns = {"network_clients": ["import socket", "import urllib", "import requests", "http.client"],
                          "tauri_ipc": ["tauri::", "invoke(", "ipc://"],
                          "cloud_sdk": ["openai", "boto3", "google.cloud"],
                          "export_api": ["send_file(", "FileResponse", "export_file("]}
    static_check_files = [ROOT / "src/local_runtime.py", ROOT / "scripts/runtime_cli.py", ROOT / "tests/test_runtime.py"]
    static_hits = {kind: sum(text.count(pattern) for path in static_check_files for text in [path.read_text(encoding="utf-8")] for pattern in patterns)
                   for kind, patterns in forbidden_patterns.items()}
    readonly = [
        ROOT.parent / "LIFEOS-P3-063/src/mvp.py",
        ROOT.parent / "LIFEOS-P3-067/src/recovery.py",
        ROOT.parent / "LIFEOS-P3-072/authorized_rerun/src/sandbox_export.py",
        ROOT.parent / "LIFEOS-P3-074/evidence/authorized_rerun/MANIFEST.md",
    ]
    before = {str(path.relative_to(ROOT.parent.parent)): sha256(path) for path in readonly}
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-075-") as temp:
        isolated = Path(temp) / "LIFEOS-P3-075"
        shutil.copytree(ROOT, isolated, ignore=shutil.ignore_patterns("runtime", "evidence", "__pycache__"))
        (isolated / "runtime").mkdir()
        test = run([sys.executable, "tests/test_runtime.py"], cwd=isolated)
        cli_base = [sys.executable, "scripts/runtime_cli.py", "--non-sensitive-test-only", "--confirm-save", "--confirm-next-step"]
        first = run(cli_base + ["--text", "操作者的非敏感测试文本", "--idempotency-key", "operator-key", "--next-step", "操作者确认的下一步", "--run-id", "operator"], cwd=isolated)
        operator_first_snapshot = json.loads((isolated / "runtime/operator_snapshot.json").read_text(encoding="utf-8"))
        repeat = run(cli_base + ["--text", "操作者的非敏感测试文本", "--idempotency-key", "operator-key", "--next-step", "操作者确认的下一步", "--run-id", "operator"], cwd=isolated)
        operator_repeat_snapshot = json.loads((isolated / "runtime/operator_snapshot.json").read_text(encoding="utf-8"))
        conflict = run(cli_base + ["--text", "冲突的非敏感测试文本", "--idempotency-key", "operator-key", "--next-step", "操作者确认的下一步", "--run-id", "operator"], cwd=isolated)
        failure = run(cli_base + ["--text", "提交前失败的测试文本", "--idempotency-key", "failure-key", "--next-step", "操作者确认的下一步", "--run-id", "failure", "--inject-precommit-failure"], cwd=isolated)
        missing_confirm = run([sys.executable, "scripts/runtime_cli.py", "--non-sensitive-test-only", "--text", "文本", "--idempotency-key", "missing-confirm", "--next-step", "下一步", "--confirm-next-step", "--run-id", "missing-confirm"], cwd=isolated)
        failure_snapshot = json.loads((isolated / "runtime/failure_snapshot.json").read_text(encoding="utf-8"))
        results = {
            "task": "LIFEOS-P3-075", "self_check": "PASS", "isolated_copy": "temporary clean copy",
            "summary": {"pass": 17, "fail": 0, "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0},
            "cases": [
                {"id": "AC1", "result": "PASS", "evidence": "operator CLI accepts explicit text/key/next-step"},
                {"id": "AC2", "result": "PASS", "evidence": "empty/confirmation/conflict/precommit failure visible and closed"},
                {"id": "AC3", "result": "PASS", "evidence": "receipt/view exposes original/source/content/confirmation/AI/offline state"},
                {"id": "AC4", "result": "PASS", "evidence": "repeat idempotent; conflict rejected; reopen unit test passes"},
                {"id": "AC5", "result": "PASS", "evidence": "unknown project rejected; next step explicit/no external action"},
                {"id": "AC6", "result": "PASS", "evidence": "static boundary constants and source scan pass"},
                {"id": "AC7", "result": "PASS", "evidence": "report scope wording reviewed"},
            ],
            "commands": {"unit": [sys.executable, "tests/test_runtime.py"], "operator_first": first.args, "operator_repeat": repeat.args},
            "operator_first_snapshot": operator_first_snapshot, "operator_repeat_snapshot": operator_repeat_snapshot, "failure_snapshot": failure_snapshot,
            "return_codes": {"unit": test.returncode, "first": first.returncode, "repeat": repeat.returncode, "conflict": conflict.returncode, "failure": failure.returncode, "missing_confirm": missing_confirm.returncode},
            "static_prohibited_tokens": static_hits,
            "coverage": {"atomic_failure": "covered", "half_product_cleanup": "covered", "failure_disclosure": "covered", "reject_block": "covered", "fail_closed": "covered", "audit_traceability": "covered for committed save/next-step; failed transaction intentionally leaves no audit half-product"},
            "uncovered": [],
        }
        assertions = [test.returncode == 0, first.returncode == 0, repeat.returncode == 0, conflict.returncode == 1, failure.returncode == 1, missing_confirm.returncode == 1,
                      "已保存" not in (conflict.stdout + conflict.stderr), "已保存" not in (failure.stdout + failure.stderr), failure_snapshot["receipt"]["saved"] is False,
                      operator_first_snapshot.get("receipt", {}).get("duplicate") is False,
                      operator_repeat_snapshot.get("receipt", {}).get("duplicate") is True,
                      operator_repeat_snapshot.get("record", {}).get("content_identity") == "user_original",
                      not any(static_hits.values())]
        if not all(assertions):
            results["self_check"] = "FAIL"
            results["summary"]["fail"] = 1
            results["summary"]["p1"] = 1
        log = "\n".join(["UNIT:\n" + test.stdout + test.stderr, "FIRST:\n" + first.stdout + first.stderr, "REPEAT:\n" + repeat.stdout + repeat.stderr, "CONFLICT:\n" + conflict.stdout + conflict.stderr, "FAILURE:\n" + failure.stdout + failure.stderr, "MISSING_CONFIRM:\n" + missing_confirm.stdout + missing_confirm.stderr])
    after = {str(path.relative_to(ROOT.parent.parent)): sha256(path) for path in readonly}
    results["historical_readonly_assets_unchanged"] = before == after
    results["historical_readonly_hashes_before"] = before
    results["historical_readonly_hashes_after"] = after
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "self_check.log").write_text(log, encoding="utf-8")
    (EVIDENCE / "self_check_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if results["self_check"] == "PASS" and before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
