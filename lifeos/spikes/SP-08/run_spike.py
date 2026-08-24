#!/usr/bin/env python3
"""SP-08 deterministic portable export/validation/reimport spike.

Standard-library only. It creates synthetic evidence below this directory and never
reads user documents, a Vault, the network, a model, cloud, or third-party APIs.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import platform
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPORT = ROOT / "sample_export"
BROKEN = ROOT / "broken_package_cases"
LOGS = ROOT / "raw_logs"
NOW = "2026-08-09T14:00:00+08:00"
SUPPORTED_MANIFEST = "1.0"
SCHEMA_VERSION = "sp08-candidate-0.1"


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def scoped(value: str) -> str:
    return "ref-" + hashlib.sha256(value.encode()).hexdigest()[:12]


def build_manifest() -> dict:
    projects = [{"id": f"project-{n}", "name": f"Synthetic Project {n}"} for n in range(1, 5)]
    sources, artifacts, versions, derivations = [], [], [], []
    decisions, actions, links, feedback = [], [], [], []
    authorizations, audit, gaps, tombstones, restrictions = [], [], [], [], []

    special = {
        6: "external_pointer_only",
        7: "external_snapshot_allowed",
        8: "external_non_exportable",
        9: "deleted",
        10: "processing_revoked",
        11: "source_disconnected",
        12: "evidence_invalid",
        13: "conflict_branch",
        14: "ai_candidate",
        15: "ai_derived",
        16: "user_confirmed",
    }
    content_types = ["user_original", "decision", "action", "ai_derived", "ai_candidate", "external_material"]

    for i in range(1, 49):
        sid, aid, vid = f"src-{i:03d}", f"art-{i:03d}", f"av-{i:03d}-v1"
        pid = f"project-{((i - 1) % 4) + 1}"
        case = special.get(i, "normal")
        ctype = content_types[(i - 1) % len(content_types)]
        authority = "user" if ctype in {"user_original", "decision", "action"} else "ai" if ctype.startswith("ai_") else "external"
        confirmation = "confirmed" if ctype in {"decision", "action"} or case == "user_confirmed" else "unconfirmed"
        if case in {"ai_candidate", "ai_derived"}:
            confirmation = "unconfirmed"
        source_kind = "external_pointer" if case in {"external_pointer_only", "external_non_exportable"} else "external_snapshot" if case == "external_snapshot_allowed" else "lifeos_capture"
        export_permission = case not in {"external_pointer_only", "external_non_exportable"}
        source_state = "disconnected" if case == "source_disconnected" else "connected"
        auth_state = "revoked" if case == "processing_revoked" else "active"
        evidence_state = "invalid" if case == "evidence_invalid" else "current"
        tombstone_generation = 4 if case == "deleted" else 1
        restriction_generation = 5 if case in {"processing_revoked", "source_disconnected"} else 1
        auth_version = 3 if case == "processing_revoked" else 1

        authorizations.append({
            "id": f"auth-{i:03d}", "subject": "synthetic-user", "scope_ref": sid,
            "actions": ["local_export"], "purpose": "portable_export_spike", "location": "local",
            "expires_at": None, "state": auth_state, "version": auth_version,
            "redistribution": "allowed" if export_permission else "not_licensed",
        })
        sources.append({
            "id": sid, "kind": source_kind, "locator": f"synthetic://source/{i:03d}",
            "state": source_state, "authorization_id": f"auth-{i:03d}",
            "license_status": "export_allowed" if export_permission else "pointer_only",
            "restriction_generation": restriction_generation,
        })
        artifacts.append({
            "id": aid, "project_id": pid, "source_id": sid, "content_identity": ctype,
            "authority": authority, "confirmation_status": confirmation,
            "current_version_id": vid, "tombstone_generation": tombstone_generation,
        })

        inactive_reason = None
        if case == "deleted":
            inactive_reason = "deleted_content_body_withheld"
        elif case == "processing_revoked":
            inactive_reason = "processing_revoked_body_withheld"
        elif case == "source_disconnected":
            inactive_reason = "source_disconnected_old_read_withheld"
        elif case == "evidence_invalid":
            inactive_reason = "unique_evidence_invalid_review_required"
        elif not export_permission:
            inactive_reason = "external_content_not_licensed_pointer_only"

        export_body = inactive_reason is None
        relpath = f"content/{pid}/{vid}.md" if export_body else None
        body = (
            f"# Synthetic content {i:03d}\n\n"
            f"Identity: {ctype}\nAuthority: {authority}\nConfirmation: {confirmation}\n"
            f"Project: {pid}\nCase: {case}\nSynthetic body token SP08-{i:03d}.\n"
        )
        checksum = sha256_bytes(body.encode()) if export_body else None
        versions.append({
            "id": vid, "artifact_id": aid, "source_id": sid, "version_number": 1,
            "created_at": NOW, "immutable": True, "content_identity": ctype,
            "authority": authority, "confirmation_status": confirmation,
            "evidence_state": evidence_state, "conflict_branch": case == "conflict_branch",
            "file": relpath, "checksum": {"algorithm": "sha256", "value": checksum} if checksum else None,
            "export_state": "content_included" if export_body else "pointer_or_gap_only",
            "gap_id": f"gap-{i:03d}" if inactive_reason else None,
        })
        if export_body:
            text(EXPORT / relpath, body)
        else:
            gaps.append({
                "id": f"gap-{i:03d}", "artifact_id": aid, "version_id": vid,
                "reason": inactive_reason, "restorable": False,
                "user_message": {
                    "deleted": "正文已删除；仅保留不可还原说明，导入不会复活。",
                    "processing_revoked": "处理授权已撤回；正文未包含，恢复时保持阻断。",
                    "source_disconnected": "来源已断开；仅恢复指针，不自动重新授权或读取。",
                    "evidence_invalid": "唯一证据已失效；保留确认历史但需要复核。",
                }.get(case, "外部内容无再分发许可；仅包含来源指针和缺口说明。"),
            })
        if case == "deleted":
            tombstones.append({"target_id": aid, "generation": 4, "reason": "user_delete", "content_recoverable": False})
        if case in {"processing_revoked", "source_disconnected"}:
            restrictions.append({"target_id": sid, "generation": restriction_generation, "reason": case, "active": True})

        if ctype in {"ai_derived", "ai_candidate"} or case in {"ai_candidate", "ai_derived"}:
            input_idx = max(1, i - 1)
            derivations.append({
                "id": f"deriv-{i:03d}", "output_version_id": vid,
                "input_version_ids": [f"av-{input_idx:03d}-v1"], "identity": "ai_candidate" if ctype == "ai_candidate" or case == "ai_candidate" else "ai_derived",
                "workflow_version": "synthetic-workflow-1", "model_descriptor": "deterministic-stub",
                "authorization_id": f"auth-{i:03d}", "status": "invalid" if case in {"processing_revoked", "source_disconnected", "evidence_invalid"} else "current",
            })
        if ctype == "decision" or case == "user_confirmed":
            decisions.append({"id": f"decision-{i:03d}", "artifact_id": aid, "version_id": vid, "authority": "user", "confirmation_status": "confirmed"})
        if ctype == "action":
            actions.append({"id": f"action-{i:03d}", "artifact_id": aid, "version_id": vid, "authority": "user", "confirmation_status": "confirmed", "state": "open"})
        if i > 1:
            links.append({
                "id": f"link-{i:03d}", "from_artifact_id": aid, "to_artifact_id": f"art-{i-1:03d}",
                "kind": "supports", "established_by": "user" if i % 2 else "ai_candidate",
                "confirmation_status": "confirmed" if i % 2 else "unconfirmed", "validity": "current",
            })
        if i % 3 == 0:
            target = f"action-{i:03d}" if ctype == "action" else aid
            feedback.append({"id": f"feedback-{i:03d}", "target_id": target, "event": "confirm" if confirmation == "confirmed" else "reject_candidate", "authority": "user", "effective": True, "sequence": i})
        audit.append({
            "event_ref": scoped(f"event-{i}"), "target_ref": scoped(aid), "event_type": "export_evaluated",
            "result_code": "included" if export_body else "withheld_with_note", "policy_version": "export-policy-candidate-1",
        })

    return {
        "manifest_version": SUPPORTED_MANIFEST,
        "schema_version": SCHEMA_VERSION,
        "export_metadata": {
            "export_id": "sp08-synthetic-export-g5", "created_at": NOW,
            "generator": "LifeOS SP-08 deterministic local spike", "package_status": "partial_with_explanations",
            "content_units": 48, "projects": 4, "portable_without_proprietary_service": True,
            "non_frozen_candidate": True,
        },
        "identity_legend": {
            "user_original": "用户权威原文，不被 AI 或导入覆盖",
            "external_material": "外部来源内容，受再分发许可约束",
            "ai_derived": "AI 派生，不是用户原文",
            "ai_candidate": "AI 候选，未经用户确认",
            "user_confirmed": "用户确认对象或历史",
        },
        "projects": projects, "sources": sources, "artifacts": artifacts, "artifact_versions": versions,
        "derivations": derivations, "decisions": decisions, "actions": actions, "links": links,
        "feedback": feedback, "authorizations": authorizations, "audit_entries": audit,
        "tombstones": tombstones, "restrictions": restrictions, "gaps": gaps,
        "excluded_rebuildable_artifacts": [
            {"kind": "fts_postings", "reason": "rebuildable_from_current_legal_content"},
            {"kind": "vectors", "reason": "rebuildable_and_model_specific"},
            {"kind": "cache", "reason": "ephemeral_not_user_business_asset"},
            {"kind": "rerank_features", "reason": "rebuildable_implementation_detail"},
        ],
        "privacy_note": "Synthetic package. Audit/log entries omit body, real path, prompt, model output, vector, credential, and raw stable object IDs.",
        "restore_policy": {
            "control_state_first": True, "field_level_lww": False, "source_pointer_does_not_reauthorize": True,
            "user_original_overwrite": "forbidden", "conflict_behavior": "retain_explicit_branch",
        },
    }


def validate_package(package: Path) -> dict:
    errors, warnings = [], []
    path = package / "manifest.json"
    if not path.exists():
        return {"valid": False, "errors": ["manifest_missing"], "warnings": []}
    m = json.loads(path.read_text(encoding="utf-8"))
    if m.get("manifest_version") != SUPPORTED_MANIFEST:
        errors.append("manifest_version_incompatible")
    for field in ("schema_version", "export_metadata", "privacy_note", "restore_policy", "identity_legend"):
        if not m.get(field):
            errors.append(f"required_field_missing:{field}")
    collections = {k: {x["id"] for x in m.get(k, []) if "id" in x} for k in (
        "projects", "sources", "artifacts", "artifact_versions", "derivations", "decisions", "actions", "links", "feedback", "authorizations", "gaps"
    )}
    for s in m.get("sources", []):
        if s.get("authorization_id") not in collections["authorizations"]:
            errors.append(f"broken_source_authorization:{s['id']}")
    for a in m.get("artifacts", []):
        if a.get("source_id") not in collections["sources"] or a.get("project_id") not in collections["projects"]:
            errors.append(f"broken_artifact_reference:{a['id']}")
        if a.get("current_version_id") not in collections["artifact_versions"]:
            errors.append(f"broken_current_version:{a['id']}")
    for v in m.get("artifact_versions", []):
        if v.get("artifact_id") not in collections["artifacts"] or v.get("source_id") not in collections["sources"]:
            errors.append(f"broken_version_reference:{v['id']}")
        if v.get("file"):
            fp = package / v["file"]
            if not fp.exists():
                errors.append(f"content_file_missing:{v['id']}")
            elif sha256_bytes(fp.read_bytes()) != (v.get("checksum") or {}).get("value"):
                errors.append(f"checksum_mismatch:{v['id']}")
        elif not v.get("gap_id") or v.get("gap_id") not in collections["gaps"]:
            errors.append(f"missing_file_explanation:{v['id']}")
    targets = collections["artifacts"] | collections["actions"] | collections["decisions"] | collections["links"]
    for d in m.get("derivations", []):
        if d.get("output_version_id") not in collections["artifact_versions"] or any(x not in collections["artifact_versions"] for x in d.get("input_version_ids", [])):
            errors.append(f"broken_derivation_reference:{d['id']}")
    for l in m.get("links", []):
        if l.get("from_artifact_id") not in collections["artifacts"] or l.get("to_artifact_id") not in collections["artifacts"]:
            errors.append(f"broken_link_reference:{l['id']}")
    for f in m.get("feedback", []):
        if f.get("target_id") not in targets:
            errors.append(f"broken_feedback_reference:{f['id']}")
    tomb_targets = {x.get("target_id") for x in m.get("tombstones", [])}
    restricted_targets = {x.get("target_id") for x in m.get("restrictions", [])}
    for a in m.get("artifacts", []):
        if a.get("tombstone_generation", 0) > 1 and a["id"] not in tomb_targets:
            errors.append(f"tombstone_note_missing:{a['id']}")
    for s in m.get("sources", []):
        if s.get("restriction_generation", 0) > 1 and s["id"] not in restricted_targets:
            errors.append(f"restriction_note_missing:{s['id']}")
        if s.get("license_status") == "pointer_only":
            associated = [v for v in m.get("artifact_versions", []) if v.get("source_id") == s["id"]]
            if any(v.get("file") for v in associated) or any(not v.get("gap_id") for v in associated):
                errors.append(f"external_license_explanation_missing:{s['id']}")
    return {"valid": not errors, "errors": sorted(errors), "warnings": warnings, "checked_versions": len(m.get("artifact_versions", []))}


def import_package(package: Path, env: dict) -> dict:
    m = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    report = {"inserted": 0, "idempotent": 0, "conflicts": 0, "rejected_control_state": 0, "protected_original": 0, "pointers_restored_without_authorization": 0, "decisions": []}
    package_tomb = {x["target_id"]: x["generation"] for x in m.get("tombstones", [])}
    package_restrict = {x["target_id"]: x["generation"] for x in m.get("restrictions", [])}
    for v in m["artifact_versions"]:
        aid, sid = v["artifact_id"], v["source_id"]
        current_tomb = env["tombstone_generation"].get(aid, 0)
        current_restrict = env["restriction_generation"].get(sid, 0)
        auth_current = env["authorization_version"].get(sid, 0)
        auth_pkg = next(a["version"] for a in m["authorizations"] if a["scope_ref"] == sid)
        if current_tomb > package_tomb.get(aid, 0) or current_restrict > package_restrict.get(sid, 0) or auth_current > auth_pkg:
            report["rejected_control_state"] += 1
            report["decisions"].append({"version_id": v["id"], "result": "rejected_stale_generation"})
            continue
        key = v["id"]
        digest = (v.get("checksum") or {}).get("value") or f"gap:{v.get('gap_id')}"
        if key in env["versions"]:
            if env["versions"][key] == digest:
                report["idempotent"] += 1
                continue
            report["conflicts"] += 1
            env["conflict_branches"].append({"version_id": key, "incoming_digest": digest})
            continue
        existing_original = env["artifact_current"].get(aid)
        if existing_original and v.get("authority") == "user":
            report["protected_original"] += 1
            env["conflict_branches"].append({"artifact_id": aid, "incoming_version_id": key, "reason": "user_original_protected"})
            continue
        env["versions"][key] = digest
        env["artifact_current"].setdefault(aid, key)
        report["inserted"] += 1
        source = next(s for s in m["sources"] if s["id"] == sid)
        if source["kind"] == "external_pointer":
            env["source_authorized"][sid] = False
            report["pointers_restored_without_authorization"] += 1
    return report


def fresh_env() -> dict:
    return {"versions": {}, "artifact_current": {}, "conflict_branches": [], "tombstone_generation": {}, "restriction_generation": {}, "authorization_version": {}, "source_authorized": {}}


def make_broken_cases() -> dict:
    results = {}
    cases = ["tampered_checksum", "missing_file", "broken_reference", "incompatible_version", "missing_restriction_note"]
    for case in cases:
        dst = BROKEN / case
        shutil.copytree(EXPORT, dst)
        manifest_path = dst / "manifest.json"
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        if case == "tampered_checksum":
            first = next(v for v in m["artifact_versions"] if v["file"])
            (dst / first["file"]).write_text("tampered synthetic content\n", encoding="utf-8")
        elif case == "missing_file":
            first = next(v for v in m["artifact_versions"] if v["file"])
            (dst / first["file"]).unlink()
        elif case == "broken_reference":
            m["derivations"][0]["input_version_ids"] = ["av-missing-v1"]
            dump(manifest_path, m)
        elif case == "incompatible_version":
            m["manifest_version"] = "99.0"
            dump(manifest_path, m)
        elif case == "missing_restriction_note":
            m["restrictions"] = []
            dump(manifest_path, m)
        results[case] = validate_package(dst)
    return results


def run() -> None:
    for target in (EXPORT, BROKEN, LOGS):
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

    manifest = build_manifest()
    dump(EXPORT / "manifest.json", manifest)
    text(EXPORT / "README.md", """# LifeOS SP-08 synthetic portable export

这是人可读入口。`manifest.json` 是机器可读清单，`content/` 只含许可且当前可用的正文；`gaps` 解释删除、撤回、断源、证据失效或外部许可限制。AI 派生、AI 候选和用户确认身份彼此分离。本包是非冻结 Spike 样例，不是正式备份 SLA 或跨版本保证。
""")
    text(EXPORT / "RESTORE_LIMITS.md", """# Restore limitations

- 先合并当前 tombstone、restriction generation 和 Authorization version，再接纳内容。
- 来源指针可恢复，但不会自动恢复读取、云处理或第三方授权。
- 用户原文不可覆盖；同 ID 异内容形成显式冲突分支。
- 向量、FTS posting、缓存和重排特征未包含，可从合法且当前可用内容重建。
""")
    base_validation = validate_package(EXPORT)
    broken = make_broken_cases()

    env = fresh_env()
    empty_import = import_package(EXPORT, env)
    repeat_import = import_package(EXPORT, env)

    protected_env = fresh_env()
    protected_env["artifact_current"]["art-001"] = "local-user-original-v2"
    protected = import_package(EXPORT, protected_env)

    conflict_root = BROKEN / "conflicting_version"
    shutil.copytree(EXPORT, conflict_root)
    cm = json.loads((conflict_root / "manifest.json").read_text(encoding="utf-8"))
    cv = next(v for v in cm["artifact_versions"] if v["file"])
    cv["checksum"]["value"] = "different-incoming-digest"
    dump(conflict_root / "manifest.json", cm)
    conflict_env = fresh_env()
    conflict_env["versions"][cv["id"]] = "existing-digest"
    conflict = import_package(conflict_root, conflict_env)

    stale_env = fresh_env()
    stale_env["tombstone_generation"]["art-009"] = 6
    stale_env["restriction_generation"]["src-010"] = 7
    stale_env["restriction_generation"]["src-011"] = 8
    stale_env["authorization_version"]["src-010"] = 5
    stale = import_package(EXPORT, stale_env)

    content_files = [v for v in manifest["artifact_versions"] if v["file"]]
    withheld = [v for v in manifest["artifact_versions"] if not v["file"]]
    all_json_text = json.dumps(manifest, ensure_ascii=False) + json.dumps({"events": manifest["audit_entries"]}, ensure_ascii=False)
    banned = ["/Users/", "PRIVATE KEY", "real-vault", "prompt_body", "embedding_vector"]
    privacy_hits = [x for x in banned if x in all_json_text]
    rebuildable_kinds = {x["kind"] for x in manifest["excluded_rebuildable_artifacts"]}

    tests = []
    def check(tid, name, ok, p0=True, evidence=""):
        tests.append({"id": tid, "name": name, "priority": "P0" if p0 else "P1", "passed": bool(ok), "evidence": evidence})

    check("T01", "人可读入口与机器 manifest", (EXPORT / "README.md").exists() and (EXPORT / "manifest.json").exists())
    check("T02", "48 内容单元覆盖 4 Project", len(manifest["artifact_versions"]) == 48 and len(manifest["projects"]) == 4)
    check("T03", "核心身份集合存在", {"user_original", "external_material", "ai_derived", "ai_candidate"}.issubset({v["content_identity"] for v in manifest["artifact_versions"]}))
    check("T04", "Decision Action Link Feedback Authorization AuditEntry 存在", all(manifest[x] for x in ["decisions", "actions", "links", "feedback", "authorizations", "audit_entries"]))
    check("T05", "所有正文版本含 SHA-256", all(v["checksum"] and v["checksum"]["algorithm"] == "sha256" for v in content_files))
    check("T06", "基线 checksum/schema/reference 校验通过", base_validation["valid"], evidence="validation_report.json")
    check("T07", "篡改 checksum 被发现", any("checksum_mismatch" in x for x in broken["tampered_checksum"]["errors"]))
    check("T08", "缺失文件被发现", any("content_file_missing" in x for x in broken["missing_file"]["errors"]))
    check("T09", "断裂引用被发现", any("broken_derivation_reference" in x for x in broken["broken_reference"]["errors"]))
    check("T10", "manifest 版本不兼容被发现", "manifest_version_incompatible" in broken["incompatible_version"]["errors"])
    check("T11", "权限/删除说明缺失被发现", any("restriction_note_missing" in x for x in broken["missing_restriction_note"]["errors"]))
    check("T12", "删除撤回断源失效与许可限制无活跃正文", len(withheld) >= 5 and all(v["gap_id"] for v in withheld))
    check("T13", "外部不可导出只含指针/缺口", all(not v["file"] for v in manifest["artifact_versions"] if next(s for s in manifest["sources"] if s["id"] == v["source_id"])["license_status"] == "pointer_only"))
    check("T14", "空环境重导入成功", empty_import["inserted"] > 0 and empty_import["conflicts"] == 0, evidence="reimport_results.json")
    check("T15", "重复导入幂等", repeat_import["inserted"] == 0 and repeat_import["idempotent"] == len(manifest["artifact_versions"]))
    check("T16", "已有用户原文不覆盖", protected["protected_original"] >= 1)
    check("T17", "冲突版本显式保留分支", conflict["conflicts"] == 1 and len(conflict_env["conflict_branches"]) == 1)
    check("T18", "低 tombstone/restriction/auth generation 拒绝", stale["rejected_control_state"] >= 3)
    check("T19", "来源指针恢复但不重新授权", empty_import["pointers_restored_without_authorization"] >= 1 and all(v is False for v in env["source_authorized"].values()))
    check("T20", "可重建派生产物不导出", rebuildable_kinds == {"fts_postings", "vectors", "cache", "rerank_features"} and not any(k in manifest for k in rebuildable_kinds))
    check("T21", "日志与审计隐私扫描", not privacy_hits)
    check("T22", "AI 候选未伪装确认", all(d["identity"] != "ai_candidate" or next(v for v in manifest["artifact_versions"] if v["id"] == d["output_version_id"])["confirmation_status"] == "unconfirmed" for d in manifest["derivations"]))
    check("T23", "用户确认对象 authority 为 user", all(x["authority"] == "user" and x["confirmation_status"] == "confirmed" for x in manifest["decisions"] + manifest["actions"]))
    check("T24", "不使用字段级 LWW", manifest["restore_policy"]["field_level_lww"] is False)
    check("T25", "包不依赖专有服务", manifest["export_metadata"]["portable_without_proprietary_service"] is True)

    total, passed = len(tests), sum(t["passed"] for t in tests)
    summary = {"spike": "SP-08", "total": total, "passed": passed, "failed": total - passed, "p0_failed": sum(not t["passed"] and t["priority"] == "P0" for t in tests), "result": "PASS" if passed == total else "FAIL"}
    dump(ROOT / "validation_report.json", {"summary": summary, "baseline": base_validation, "broken_cases": broken})
    dump(ROOT / "reimport_results.json", {"empty_environment": empty_import, "repeat": repeat_import, "existing_original_protection": protected, "conflict": conflict, "stale_generation": stale})
    dump(ROOT / "results.json", {"summary": summary, "tests": tests})
    dump(LOGS / "run_summary.json", summary)
    dump(LOGS / "validation_events.json", [{"case": k, "valid": v["valid"], "error_codes": v["errors"]} for k, v in broken.items()])
    dump(LOGS / "reimport_events.json", {k: {x: y for x, y in v.items() if x != "decisions"} for k, v in {"empty": empty_import, "repeat": repeat_import, "protected": protected, "conflict": conflict, "stale": stale}.items()})
    dump(LOGS / "privacy_scan.json", {"patterns_checked": banned, "hits": privacy_hits, "result": "PASS" if not privacy_hits else "FAIL"})
    with (ROOT / "test_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "priority", "passed", "evidence"])
        writer.writeheader(); writer.writerows(tests)
    text(ROOT / "SP-08_report.md", f"""# SP-08 evidence report

Result: **{summary['result']}** — {passed}/{total} assertions passed; P0 failures: {summary['p0_failed']}.

Scope: 48 synthetic content units, 4 projects, Python {platform.python_version()} standard library, local deterministic files only. This is a non-frozen candidate format and does not prove production backup, cross-version restore, attachment, encryption, cloud, vendor, capacity, or SLA behavior.
""")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    run()
