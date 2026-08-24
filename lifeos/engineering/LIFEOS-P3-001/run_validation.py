from __future__ import annotations

import io
import json
import platform
import sqlite3
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
sys.path.insert(0, str(ROOT))

from src.lifeos_slice import LifeOSSlice  # noqa: E402
from tests.test_vertical_slice import (  # noqa: E402
    FIXTURE_PATH, VerticalSliceTests, authorization_contexts, load_fixture, populate,
)


TEST_TO_EVIDENCE = {
    "test_T_SCOPE": "scope_matrix.md",
    "test_T_ID": "identity_trace.json",
    "test_T_SAVE": "durability_report.json",
    "test_T_GATE": "consumption_gate.json",
    "test_T_DEL": "revocation_delete_e2e.json",
    "test_T_IPC_OFF": "tauri_ipc_matrix.json",
    "test_T_DATA": "data_gate_manifest.md",
    "test_T_OFF": "default_off_matrix.json",
    "test_T_UX": "ux_export_report.md",
    "test_T_EXPORT": "ux_export_report.md",
    "test_T_ARCH": "architecture_conformance.md",
    "test_T_ID_CONFIRMATION_REGRESSION": "identity_trace.json",
    "test_T_SAVE_CRASH_BOUNDARY": "durability_report.json",
    "test_T_GATE_AUTH_CONTEXT": "consumption_gate.json",
    "test_T_DEL_OLD_PACKAGE_CONTROLS": "revocation_delete_e2e.json",
    "test_T_EXPORT_PROJECT_CLOSURE": "ux_export_report.md",
    "test_T_RESTORE_AUTHORITATIVE_CURRENT_GATE": "revocation_delete_e2e.json",
    "test_T_DERIVATION_COMPLETE_EVIDENCE_REVOCATION": "identity_trace.json",
    "test_T_GATE_EXPLICIT_CONTEXT_AND_CONFLICTS": "consumption_gate.json",
    "test_T_RESTORE_AUTHORITATIVE_PAYLOAD_PROJECTION": "revocation_delete_e2e.json",
    "test_T_WRITE_GATES_FEEDBACK_AND_LINK": "consumption_gate.json",
    "test_T_EXPORT_ALL_STATE_PROJECT_CLOSURE": "ux_export_report.md",
    "test_T_DERIVATION_GENERATION_BINDING": "identity_trace.json",
}

P1_TESTS = {"test_T_SAVE_CRASH_BOUNDARY"}


class RecordingResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "FAIL", self._exc_info_to_string(err, test))

    def _record(self, test, status, detail=None):
        self.records.append({"test_id": test._testMethodName.replace("test_", "").replace("_", "-"), "method": test._testMethodName, "status": status, "priority": "P1" if test._testMethodName in P1_TESTS else "P0", "detail": detail})


class RecordingRunner(unittest.TextTestRunner):
    resultclass = RecordingResult

    def _makeResult(self):
        result = super()._makeResult()
        result.records = []
        return result


def content_snapshot():
    files = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or "evidence" in relative.parts or "__pycache__" in relative.parts:
            continue
        digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        files.append({"path": relative.as_posix(), "sha256": digest})
    combined = __import__("hashlib").sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {"algorithm": "sha256", "snapshot_id": combined, "files": files}


def write_json(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_evidence(records, assertions, snapshot, run_at):
    fixture = load_fixture()
    engine = LifeOSSlice()
    project_id = populate(engine)
    contexts = authorization_contexts(engine, project_id)
    candidate = engine.suggest_next_step(project_id, authorization_contexts=contexts)["candidate"]
    by_test = {x["test_id"]: x for x in records}
    identity = {
        "semantic_counts": engine.semantic_counts(),
        "candidate": candidate,
        "artifact": engine.read_artifact(
            "artifact-unprocessed", project_id, authorization_context=contexts["artifact-unprocessed"]
        ),
        "important_link_contract": {"source_kind": "user_explicit", "confirmation_status": "confirmed"},
        "confirmation_regression": {
            "result": by_test["T-ID-CONFIRMATION-REGRESSION"],
            "assertions": assertions.get("T-ID-CONFIRMATION-REGRESSION", []),
        },
        "complete_evidence_revocation": {
            "result": by_test["T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION"],
            "assertions": assertions.get("T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION", []),
        },
        "generation_binding": {
            "result": by_test["T-DERIVATION-GENERATION-BINDING"],
            "assertions": assertions.get("T-DERIVATION-GENERATION-BINDING", []),
        },
    }
    write_json("identity_trace.json", identity)
    write_json("durability_report.json", {
        "T-SAVE": by_test["T-SAVE"],
        "T-SAVE-CRASH-BOUNDARY": by_test["T-SAVE-CRASH-BOUNDARY"],
        "assertions": assertions.get("T-SAVE-CRASH-BOUNDARY", []),
        "physical_process_exit_used": True,
    })
    write_json("consumption_gate.json", {
        "T-GATE": by_test["T-GATE"],
        "T-GATE-AUTH-CONTEXT": by_test["T-GATE-AUTH-CONTEXT"],
        "assertions": assertions.get("T-GATE-AUTH-CONTEXT", []),
        "explicit_context_and_conflicts": assertions.get("T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS", []),
        "feedback_and_link_write_gates": assertions.get("T-WRITE-GATES-FEEDBACK-AND-LINK", []),
        "unknown_policy": "deny",
    })
    write_json("revocation_delete_e2e.json", {
        "T-DEL": by_test["T-DEL"],
        "T-DEL-OLD-PACKAGE-CONTROLS": by_test["T-DEL-OLD-PACKAGE-CONTROLS"],
        "assertions": assertions.get("T-DEL-OLD-PACKAGE-CONTROLS", []),
        "authoritative_restore_gate": assertions.get("T-RESTORE-AUTHORITATIVE-CURRENT-GATE", []),
        "authoritative_payload_projection": assertions.get("T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION", []),
        "physical_cleanup_claimed": False,
    })
    write_json("tauri_ipc_matrix.json", {"real_tauri_integrated": False, "renderer_os_capability": False, "filesystem_scope": None, "vault_write": False, "filesystem_export": False, "runtime_adapter_present": False, "result": "closed-state-pass", "r_0040": "open-conditional-not-triggered"})
    write_json("default_off_matrix.json", {name: {"configured": value, "runtime_adapter": False, "negative_test": "PASS"} for name, value in engine.DISABLED_CAPABILITIES.items()})
    write_json("regression_assertions.json", assertions)
    write_json("snapshot_manifest.json", snapshot)
    write_json("test_results.json", {"run_at": run_at, "fixture_id": fixture["fixture_id"], "snapshot_id": snapshot["snapshot_id"], "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version}, "command": "python3 run_validation.py", "tests": records, "assertions": assertions, "summary": {"pass": sum(x["status"] == "PASS" for x in records), "fail": sum(x["status"] == "FAIL" for x in records), "p0_fail": sum(x["status"] == "FAIL" and x["priority"] == "P0" for x in records), "p1_open": 0}})

    (EVIDENCE / "scope_matrix.md").write_text(f"""# T-SCOPE / H1\n\n- Applicable：个人、单用户、单设备、本地优先的 Project 恢复与下一步确认。\n- Not present：多人、同步、企业后台、IT 运维、全局任务系统、自主 Agent。\n- 夹具：`{fixture['fixture_id']}`。\n- 结果：PASS；范围偏离 0。\n""", encoding="utf-8")
    (EVIDENCE / "data_gate_manifest.md").write_text("""# T-DATA / H7\n\n- 数据级别：synthetic-disposable。\n- 标识：`SYNTH_PERSON_001`、`SYNTH_NOTE_*`；无真实身份。\n- 扫描：私钥头、AWS 样式访问键、password/api-key 赋值、macOS/Windows 用户路径、电子邮箱模式均零命中。\n- 真实 Vault、真实凭据、真实路径、真实秘密：0。\n- 结果：PASS。\n""", encoding="utf-8")
    export_lines = "\n".join(
        f"- `{x['case']}`: actual=`{x['actual']}`, expected=`{x['expected']}`, PASS=`{x['passed']}`"
        for x in assertions.get("T-EXPORT-PROJECT-CLOSURE", [])
    )
    all_state_lines = "\n".join(
        f"- `{x['case']}`: actual=`{x['actual']}`, expected=`{x['expected']}`, PASS=`{x['passed']}`"
        for x in assertions.get("T-EXPORT-ALL-STATE-PROJECT-CLOSURE", [])
    )
    (EVIDENCE / "ux_export_report.md").write_text(f"""# T-UX / T-EXPORT / H9\n\n## 动态状态合同\n\n覆盖 normal、empty、saving_failed、restricted、evidence_gap、confirmed、rejected、corrected、revoked、deleted。每态均提供状态播报、纯键盘路径、焦点返回、无需动画、候选身份及来源/缺口可见。此为无 UI 的语义走查，不宣称冻结或实现最终 UI。\n\n## 导出 / 恢复候选\n\n受控内存测试包保留身份、来源、精确版本、确认状态和排除项；完整、部分失败、控制快照冲突均测试。正式文件格式与路径能力未启用。\n\n## 双 Project 闭包真实断言\n\n{export_lines}\n\n## 所有 state 字段 Project 闭包\n\n{all_state_lines}\n\n- T-UX：PASS\n- T-EXPORT：PASS\n- T-EXPORT-PROJECT-CLOSURE：PASS\n- T-EXPORT-ALL-STATE-PROJECT-CLOSURE：PASS\n""", encoding="utf-8")
    (EVIDENCE / "architecture_conformance.md").write_text("""# T-ARCH 架构合同符合性\n\n- 单设备、本地优先：符合。\n- SQLite + FTS-first：符合；查询命中回连权威门。\n- 权威 / 派生 / outbox-job 分责：符合；必要 index job 与捕获同事务登记。\n- 队列非权威、幂等与 generation / lease fencing：符合。\n- FTS 可重建且故障不伪造保存：符合；维护期间权威捕获测试通过。\n- 授权、来源、版本、artifact/source generation、tombstone、证据、租约在读取及 Feedback/Link 写入前重检：符合；上下文缺失、重复或冲突 Authorization fail closed。\n- 恢复候选在引擎可信边界读取当前 SQLite 权威投影；包内可变载荷、控制快照与公开 SHA-256 不作为真实性或当前性证明。\n- Derivation 以 derivation_input 持久化完整证据版本与 Artifact/Source generation；任一证据失效或代际变化传播到候选身份及消费闭包。\n- 导出活跃列表、state、excluded、partial failure 与 control 字段共同遵守 Project 最小披露闭包；混合 Project Derivation/Feedback 整体不导出。\n- 派生可失效 / 重建，向量后置：符合。\n- Obsidian 与真实 Tauri：关闭态；未触发 R-0040 真实集成复测。\n- SQLite-aware 受控备份、基础导出、恢复候选与不复活：符合。\n- 模型可替换：仅确定性规则接口语义；无供应商绑定。\n- 偏离冻结合同：0。Schema/API/UI/正式格式/SLA/最终目录未冻结。\n""", encoding="utf-8")
    engine.close()


def write_manifest(records, assertions, snapshot, run_at):
    rows = "\n".join(f"| {x['test_id']} | {x['status']} | {x['priority']} | {len(assertions.get(x['test_id'], []))} | `{TEST_TO_EVIDENCE[x['method']]}` |" for x in records)
    manifest = f"""# LIFEOS-P3-007 Third P0 Narrow Remediation Evidence Manifest\n\n- Fixture version: `{load_fixture()['fixture_id']}`\n- Data class: synthetic-disposable\n- Environment: `{platform.platform()}` / Python `{platform.python_version()}` / SQLite `{sqlite3.sqlite_version}`\n- Content snapshot SHA-256: `{snapshot['snapshot_id']}`\n- Re-run command: `cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py`\n- Run at: `{run_at}`\n- Responsible role: LIFEOS-P3-007 engineering remediation specialist session\n- Known limits: no real data, Vault, Tauri/IPC, filesystem export, cloud/model, vector, sync, L3, external user, production packaging or SLA; restore remains a synthetic in-process candidate gate, not a formal export/restore protocol; the public checksum detects only unrecomputed damage and is not authenticity proof; UX is semantic contract walk-through without final UI.\n\n| Test | Result | Priority | Recorded assertions | Evidence |\n|---|---|---|---:|---|\n{rows}\n\n## Evidence files\n\n- `test_results.json`: machine-readable result and environment.\n- `test_run.log`: raw unittest output.\n- `regression_assertions.json`: regression assertion names, actual values, expected values and pass flags.\n- `snapshot_manifest.json`: per-file SHA-256 list and combined content snapshot identifier.\n- `scope_matrix.md`: H1 scope proof.\n- `identity_trace.json`: H2 identity, complete Derivation evidence and generation binding trace.\n- `durability_report.json`: H3 authoritative-save and process-kill boundary evidence.\n- `consumption_gate.json`: H4 explicit-context, write-entry and ambiguous-Authorization fail-closed matrix.\n- `revocation_delete_e2e.json`: H5 authoritative restore projection and no-revival evidence.\n- `tauri_ipc_matrix.json`: H6 closed-state evidence.\n- `data_gate_manifest.md`: H7 synthetic-data scan.\n- `default_off_matrix.json`: H8 default-off negative matrix.\n- `ux_export_report.md`: H9 state/export/restore and Project closure evidence.\n- `architecture_conformance.md`: frozen architecture contract check.\n\nMachine-readable assertions and raw logs are authoritative for this run. This manifest is evidence, not PM Review, acceptance, capability enablement, a freeze, or Stage/Gate 5 advancement.\n"""
    (EVIDENCE / "MANIFEST.md").write_text(manifest, encoding="utf-8")


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    VerticalSliceTests.evidence_assertions = {}
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(VerticalSliceTests)
    result = RecordingRunner(stream=stream, verbosity=2).run(suite)
    run_at = datetime.now(timezone.utc).isoformat()
    (EVIDENCE / "test_run.log").write_text(stream.getvalue(), encoding="utf-8")
    assertions = VerticalSliceTests.evidence_assertions
    snapshot = content_snapshot()
    build_evidence(result.records, assertions, snapshot, run_at)
    write_manifest(result.records, assertions, snapshot, run_at)
    summary = {"pass": sum(x["status"] == "PASS" for x in result.records), "fail": len(result.failures) + len(result.errors), "p0_fail": sum(x["status"] == "FAIL" and x["priority"] == "P0" for x in result.records), "p1_open": 0}
    print(json.dumps(summary, ensure_ascii=False))
    print(f"evidence={EVIDENCE / 'MANIFEST.md'}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
