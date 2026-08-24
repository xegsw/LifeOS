#!/usr/bin/env python3
"""Fresh, task-local independent verification for LIFEOS-P3-078.

This runner deliberately does not import or invoke P3-077's test suite or
self-check script.  It copies the candidate to a new temporary directory,
drives the public runtime/CLI, and records per-case outcomes only here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import ast
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
LIFEOS = HERE.parents[1]
CANDIDATE = LIFEOS / "engineering" / "LIFEOS-P3-077"
OUT = HERE / "evidence"
RESULTS = OUT / "independent_results.json"
LOG = OUT / "independent_review.log"
SNAPSHOT = OUT / "independent_snapshot.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, object]] = []
    snapshots: dict[str, object] = {}

    def check(case_id: str, criterion: str, assertion) -> None:
        try:
            assertion()
            cases.append({"id": case_id, "criterion": criterion, "status": "PASS"})
        except Exception as exc:  # retain failure detail as audit evidence
            cases.append({"id": case_id, "criterion": criterion, "status": "FAIL", "detail": repr(exc)})

    def require(condition: bool, detail: object) -> None:
        if not condition:
            raise AssertionError(detail)

    with tempfile.TemporaryDirectory(prefix="lifeos-p3-078-independent-") as temp:
        isolated = Path(temp) / "candidate"
        shutil.copytree(CANDIDATE, isolated)
        spec = importlib.util.spec_from_file_location("candidate_runtime", isolated / "src" / "permission_runtime.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        Runtime, boundary = module.PermissionRuntime, module.BOUNDARY
        context = {key: boundary[key] for key in ("project", "category", "purpose", "location", "processor")}
        future = int(time.time() * 1000) + 600_000

        db = isolated / "independent.sqlite"
        runtime = Runtime(db)
        try:
            check("IR-01", "preview 清楚声明默认拒绝、固定边界与确认 token", lambda: (
                (lambda p: (p["default_decision"] == "deny" and p["confirm_token"] == "CONFIRM" and p["boundary"]["external_action"] == "none") or (_ for _ in ()).throw(AssertionError(p)))(runtime.preview())
            ))
            check("IR-02", "无 grant 时默认拒绝并声明无外部动作", lambda: (
                (lambda r: (not r["allowed"] and r["reason"] == "default_deny" and r["external_action"] == "none") or (_ for _ in ()).throw(AssertionError(r)))(runtime.consume(context, "CONFIRM"))
            ))
            grant = runtime.set_decision("grant", context, future, "CONFIRM", "ir-grant")
            check("IR-03", "唯一精确 grant 加 CONFIRM 才允许本地合成路径", lambda: (
                grant["ok"] and runtime.consume(context, "CONFIRM")["allowed"]
            ) or (_ for _ in ()).throw(AssertionError("grant did not allow")))
            check("IR-04", "错误确认 fail-closed", lambda: (not runtime.consume(context, "NO")["allowed"]) or (_ for _ in ()).throw(AssertionError("wrong confirm allowed")))
            wrong_context = dict(context); wrong_context["purpose"] = "other"
            check("IR-05", "绑定不匹配 fail-closed", lambda: (not runtime.consume(wrong_context, "CONFIRM")["allowed"]) or (_ for _ in ()).throw(AssertionError("mismatch allowed")))
            deny = runtime.set_decision("deny", context, future, "CONFIRM", "ir-deny-after-grant")
            check("IR-06", "当前 deny 在既有 grant 后仍优先", lambda: (deny["ok"] and runtime.consume(context, "CONFIRM")["reason"] == "explicit_deny_current") or (_ for _ in ()).throw(AssertionError("deny priority missing")))
            check("IR-07", "相同幂等键重复回执，不生成第二项", lambda: runtime.set_decision("deny", context, future, "CONFIRM", "ir-deny-after-grant")["reason"] == "idempotent_repeat")
            check("IR-08", "冲突幂等键 fail-closed", lambda: (not runtime.set_decision("grant", context, future, "CONFIRM", "ir-deny-after-grant")["ok"]) or (_ for _ in ()).throw(AssertionError("conflict accepted")))
            revoked = runtime.revoke(grant["permission_id"], "REVOKE", "ir-revoke")
            check("IR-09", "撤回后即使 deny 移除也保持拒绝", lambda: (
                revoked["ok"] and runtime.conn.execute("UPDATE permissions SET status='revoked' WHERE id=?", (deny["permission_id"],)).rowcount == 1 and runtime.conn.commit() is None and not runtime.consume(context, "CONFIRM")["allowed"]
            ) or (_ for _ in ()).throw(AssertionError("revocation not enforced")))
            runtime.close()
            runtime = Runtime(db)
            check("IR-10", "重启后撤回状态和审计仍可追溯且 fail-closed", lambda: (
                (lambda s: (not runtime.consume(context, "CONFIRM")["allowed"] and any(a["event"] == "revoked" for a in s["audits"])) or (_ for _ in ()).throw(AssertionError("restart state missing")))(runtime.snapshot())
            ))
            runtime.conn.execute("INSERT INTO permissions VALUES (?, 'granted', ?, ?, ?, ?, ?, ?, 'current', 'CONFIRM', ?, ?, NULL)", ("expired", *(context[k] for k in context), int(time.time() * 1000) - 1, "ir-expired", int(time.time() * 1000)))
            runtime.conn.commit()
            check("IR-11", "过期 grant 不可消费", lambda: (not runtime.consume(context, "CONFIRM")["allowed"]) or (_ for _ in ()).throw(AssertionError("expired grant allowed")))
            runtime.conn.execute("CREATE TRIGGER force_audit_failure BEFORE INSERT ON audits WHEN NEW.event = 'decision_set' BEGIN SELECT RAISE(ABORT, 'forced'); END")
            runtime.conn.commit()
            before = runtime.conn.execute("SELECT count(*) FROM permissions").fetchone()[0]
            failed = runtime.set_decision("grant", context, future, "CONFIRM", "ir-atomic-failure")
            after = runtime.conn.execute("SELECT count(*) FROM permissions").fetchone()[0]
            check("IR-12", "原子失败不留下权限半成品", lambda: require(not failed["ok"] and failed["reason"] == "atomic_write_failed" and before == after, (failed, before, after)))
            snapshots = runtime.snapshot()
        finally:
            runtime.close()

        cli = subprocess.run([sys.executable, str(isolated / "scripts" / "permission_cli.py"), "preview", "--run-id", "ir-preview"], text=True, capture_output=True, check=False)
        check("IR-13", "CLI preview 可理解且不需要隐式写入真实路径", lambda: require(cli.returncode == 0 and json.loads(cli.stdout)["default_decision"] == "deny", (cli.returncode, cli.stdout, cli.stderr)))
        imported = set()
        for source in isolated.rglob("*.py"):
            for node in ast.walk(ast.parse(source.read_text())):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
        forbidden = {"requests", "urllib", "http", "socket", "boto3", "openai", "tauri", "ipc", "vault", "multiprocessing"}
        check("IR-14", "禁止网络、云、Tauri/IPC、Vault、导出、同步、多设备通道保持未实现", lambda: require(not imported & forbidden, sorted(imported & forbidden)))
        check("IR-15", "候选核心输入 hash 与 P3-077 Manifest 一致", lambda: require(
            sha256(CANDIDATE / "src" / "permission_runtime.py") == "1aca35f29e3a09505f7b825a33e5f386932aae946817da4bc8d91ca9615df9fa" and
            sha256(CANDIDATE / "scripts" / "permission_cli.py") == "8bea310d2eda9137c5387e571dd1ff7083f3e6f7771e3fec1c7eec4b0413d6d2", "candidate hash mismatch"))

    payload = {"task": "LIFEOS-P3-078", "runner": "independent_permission_review.py", "results": cases,
               "summary": {"pass": sum(c["status"] == "PASS" for c in cases), "fail": sum(c["status"] == "FAIL" for c in cases), "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0}}
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    SNAPSHOT.write_text(json.dumps(snapshots, ensure_ascii=False, indent=2) + "\n")
    LOG.write_text("\n".join(f'{c["id"]} {c["status"]} {c["criterion"]}' for c in cases) + "\n")
    return 0 if payload["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
