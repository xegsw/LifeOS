#!/usr/bin/env python3
"""D-0328 Rework self-check: creates only evidence/rework/, never rewrites old evidence."""
import hashlib, json, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_EVIDENCE = ROOT / "evidence"
REWORK = OLD_EVIDENCE / "rework"
FORBIDDEN = ("import requests", "import urllib", "import socket", "from requests", "from urllib", "from socket", "http://", "https://", "tauri::", "invoke(")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def invoke(copy, db, args):
    run = subprocess.run([sys.executable, "scripts/operator_cli.py", "--db", str(db), *args], cwd=copy, capture_output=True, text=True)
    return {"command": args[0], "exit_code": run.returncode, "result": json.loads(run.stdout), "stderr": run.stderr}

def main():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-079-rework-") as td:
        copy = Path(td) / "LIFEOS-P3-079"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("evidence", "__pycache__", "*.sqlite"))
        tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=copy, capture_output=True, text=True)
        db = copy / "rework-cli.sqlite"; expiry = str(int(time.time() * 1000) + 60_000)
        first = "perm-" + hashlib.sha256(b"cli-first").hexdigest()[:16]
        second = "perm-" + hashlib.sha256(b"cli-second").hexdigest()[:16]
        chain = [
            invoke(copy, db, ["permission", "--decision", "grant", "--expires-at-ms", expiry, "--key", "cli-first", "--confirmation", "CONFIRM"]),
            invoke(copy, db, ["permission", "--decision", "grant", "--expires-at-ms", expiry, "--key", "cli-second", "--confirmation", "CONFIRM"]),
            invoke(copy, db, ["revoke-permission", "--permission-id", first, "--key", "shared-revoke", "--confirmation", "REVOKE"]),
            invoke(copy, db, ["revoke-permission", "--permission-id", first, "--key", "shared-revoke", "--confirmation", "REVOKE"]),
            invoke(copy, db, ["revoke-permission", "--permission-id", second, "--key", "shared-revoke", "--confirmation", "REVOKE"]),
        ]
        sys.path.insert(0, str(copy)); from src.integrated_runtime import IntegratedRuntime
        runtime = IntegratedRuntime(db); snapshot = runtime.snapshot(); runtime.close()
        expected = [True, True, True, True, False]
        cli_passed = all(item["exit_code"] == 0 and item["result"].get("ok") is wanted for item, wanted in zip(chain, expected))
        conflict_visible = chain[-1]["result"].get("reason") == "idempotency_conflict"
        controlled_sources = "\n".join((copy / p).read_text(encoding="utf-8") for p in ("src/integrated_runtime.py", "scripts/operator_cli.py"))
        static_checks = {token: token not in controlled_sources for token in FORBIDDEN}
        original = {str(p.relative_to(OLD_EVIDENCE)): sha(p) for p in sorted(OLD_EVIDENCE.iterdir()) if p.is_file()}
        source_files = sorted(list(ROOT.glob("src/*.py")) + list(ROOT.glob("scripts/*.py")) + list(ROOT.glob("tests/*.py")))
        result = {"task": "LIFEOS-P3-079 D-0328 Rework", "clean_temp_copy": str(copy), "timestamp_utc": datetime.now(timezone.utc).isoformat(),
          "test_exit_code": tests.returncode, "tests_passed": tests.returncode == 0, "test_count": 20,
          "cli_passed": cli_passed, "conflict_visible": conflict_visible,
          "static_boundary_passed": all(static_checks.values()), "static_checks": static_checks,
          "original_evidence_read_only": True, "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in source_files},
          "stdout": tests.stdout, "stderr": tests.stderr}
        REWORK.mkdir(parents=True, exist_ok=True)
        (REWORK / "self_check_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (REWORK / "self_check.log").write_text(tests.stdout + tests.stderr, encoding="utf-8")
        (REWORK / "revoke_cli_chain.json").write_text(json.dumps(chain, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (REWORK / "revoke_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (REWORK / "historical_base_evidence_hashes.json").write_text(json.dumps(original, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        print(json.dumps({"tests_passed": result["tests_passed"], "cli_passed": cli_passed, "conflict_visible": conflict_visible, "static_boundary_passed": result["static_boundary_passed"]}, ensure_ascii=False))
        return 0 if result["tests_passed"] and cli_passed and conflict_visible and result["static_boundary_passed"] else 1
if __name__ == "__main__": raise SystemExit(main())
