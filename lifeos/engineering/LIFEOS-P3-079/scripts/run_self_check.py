#!/usr/bin/env python3
"""Run P3-079 tests in a clean temporary copy and write structured evidence."""
import hashlib, json, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IMPORTS = ("import requests", "import urllib", "import socket", "import http", "from requests", "from urllib", "from socket")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-079-") as td:
        copy = Path(td) / "LIFEOS-P3-079"; shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("evidence", "__pycache__", "*.sqlite"))
        test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=copy, capture_output=True, text=True)
        db = copy / "operator-demo.sqlite"
        commands = [
          ["save", "--text", "非敏感测试文本：CLI 演练", "--key", "cli-save", "--confirmation", "CONFIRM"],
          ["permission", "--decision", "grant", "--expires-at-ms", str(int(time.time()*1000)+60_000), "--key", "cli-grant", "--confirmation", "CONFIRM"],
          ["preview-restore", "--record-id", "rec-" + hashlib.sha256(b"cli-save").hexdigest()[:16], "--confirmation", "CONFIRM"],
          ["confirm-restore", "--record-id", "rec-" + hashlib.sha256(b"cli-save").hexdigest()[:16], "--confirmation", "CONFIRM"],
        ]
        cli = []
        for command in commands:
            call = subprocess.run([sys.executable, "scripts/operator_cli.py", "--db", str(db), *command], cwd=copy, capture_output=True, text=True)
            cli.append({"command": command[0], "exit_code": call.returncode, "result": json.loads(call.stdout), "stderr": call.stderr})
        sys.path.insert(0, str(copy)); from src.integrated_runtime import IntegratedRuntime
        rt = IntegratedRuntime(db); snapshot = rt.snapshot(); rt.close()
        source = (copy / "src/integrated_runtime.py").read_text(encoding="utf-8")
        static = {name: (name not in source) for name in FORBIDDEN_IMPORTS}
        result = {"task": "LIFEOS-P3-079", "clean_temp_copy": str(copy), "test_exit_code": test.returncode,
          "tests_passed": test.returncode == 0, "cli_passed": all(x["exit_code"] == 0 and x["result"].get("ok") for x in cli), "static_boundary_passed": all(static.values()), "static_checks": static,
          "timestamp_utc": datetime.now(timezone.utc).isoformat(), "stdout": test.stdout, "stderr": test.stderr,
          "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in sorted(list(ROOT.glob("src/*.py")) + list(ROOT.glob("scripts/*.py")) + list(ROOT.glob("tests/*.py")))}}
        evidence = ROOT / "evidence"; evidence.mkdir(exist_ok=True)
        (evidence / "self_check_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (evidence / "self_check.log").write_text(test.stdout + test.stderr, encoding="utf-8")
        (evidence / "operator_cli_chain.json").write_text(json.dumps(cli, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (evidence / "operator_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("tests_passed", "cli_passed", "static_boundary_passed", "test_exit_code")}, ensure_ascii=False))
        return 0 if result["tests_passed"] and result["cli_passed"] and result["static_boundary_passed"] else 1
if __name__ == "__main__": raise SystemExit(main())
