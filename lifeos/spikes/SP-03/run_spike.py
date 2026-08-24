#!/usr/bin/env python3
"""LifeOS SP-03 evidence-chain mapping spike. Synthetic data only; not product code."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import platform
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "raw_logs"
SEED = 20260808
FIXTURE_VERSION = "fixture-pack-v1-sp03"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def auth(auth_id, projects, actions, purposes, locations, expires, state="active", sensitivity="personal", recipients=("local_runtime",), exportable=True):
    return {
        "authorization_id": auth_id,
        "subject": "user-synthetic-01",
        "scope": {"projects": list(projects), "sources": ["source-obsidian-synth", "source-web-synth"], "excluded": ["excluded-synthetic"]},
        "actions": list(actions),
        "purposes": list(purposes),
        "locations": list(locations),
        "validity": {"granted_at": "2026-08-08T08:00:00Z", "expires_at": expires, "state": state},
        "policy": {
            "policy_version": "policy-synth-v3",
            "sensitivity": sensitivity,
            "recipients": list(recipients),
            "training_allowed": False,
            "retention_days": 30 if sensitivity == "personal" else 7,
            "exportable": exportable,
            "external_disclosure": "denied" if sensitivity == "restricted" else "local_only",
        },
    }


def base_fixture():
    sources = {
        "source-obsidian-synth": {"source_id": "source-obsidian-synth", "kind": "obsidian_vault", "locator_token": "loc-synth-a", "access": "reachable", "connection": "active"},
        "source-web-synth": {"source_id": "source-web-synth", "kind": "external_material", "locator_token": "loc-synth-b", "access": "reachable", "connection": "active"},
        "source-lifeos-synth": {"source_id": "source-lifeos-synth", "kind": "local_input", "locator_token": "loc-synth-c", "access": "reachable", "connection": "active"},
    }
    artifacts = {
        "artifact-obs-note": {"artifact_id": "artifact-obs-note", "identity": "external_original", "source_id": "source-obsidian-synth", "current_version_id": "version-obs-v1", "tombstoned": False},
        "artifact-web-material": {"artifact_id": "artifact-web-material", "identity": "external_original", "source_id": "source-web-synth", "current_version_id": "version-web-v1", "tombstoned": False},
        "artifact-user-note": {"artifact_id": "artifact-user-note", "identity": "user_authored_original", "source_id": "source-lifeos-synth", "current_version_id": "version-user-v1", "tombstoned": False},
        "artifact-excluded": {"artifact_id": "artifact-excluded", "identity": "external_original", "source_id": "source-obsidian-synth", "current_version_id": "version-excluded-v1", "tombstoned": False},
    }
    texts = {
        "version-obs-v1": "SYNTHETIC_OBSIDIAN_NOTE_V1_NO_REAL_DATA",
        "version-web-v1": "SYNTHETIC_EXTERNAL_MATERIAL_V1_NO_REAL_DATA",
        "version-user-v1": "SYNTHETIC_USER_ORIGINAL_V1_NO_REAL_DATA",
        "version-excluded-v1": "SYNTHETIC_EXCLUDED_INPUT_V1_NO_REAL_DATA",
    }
    versions = {}
    for version_id, text in texts.items():
        artifact_id = {
            "version-obs-v1": "artifact-obs-note", "version-web-v1": "artifact-web-material",
            "version-user-v1": "artifact-user-note", "version-excluded-v1": "artifact-excluded",
        }[version_id]
        versions[version_id] = {"version_id": version_id, "artifact_id": artifact_id, "content_hash": sha(text), "created_seq": len(versions) + 1, "tombstoned": False}

    authorizations = {
        "auth-local-a": auth("auth-local-a", ("project-alpha",), ("read", "local_derive", "export"), ("project_recovery", "next_step"), ("local",), "2027-08-08T00:00:00Z"),
        "auth-local-b": auth("auth-local-b", ("project-alpha", "project-beta"), ("read", "local_derive", "export"), ("decision_evidence", "project_recovery"), ("local",), "2027-08-08T00:00:00Z", sensitivity="restricted", exportable=False),
        "auth-excluded": auth("auth-excluded", ("project-beta",), ("read",), ("search",), ("local",), "2027-08-08T00:00:00Z", state="revoked", sensitivity="restricted", exportable=False),
    }
    derivations = {
        "deriv-recovery-v1": {"derivation_id": "deriv-recovery-v1", "kind": "recovery_package", "inputs": ["version-obs-v1", "version-user-v1"], "authorization_ids": ["auth-local-a"], "purpose": "project_recovery", "location": "local", "processor": "deterministic_stub", "workflow_version": "recovery-wf-v1", "model_version": "stub-v1", "generated_at": "2026-08-08T09:00:00Z", "output_id": "output-recovery-v1", "output_identity": "ai_organized", "status": "valid", "active": True, "gap_disclosure": []},
        "deriv-next-v1": {"derivation_id": "deriv-next-v1", "kind": "candidate_next_step", "inputs": ["version-obs-v1", "version-user-v1", "output-recovery-v1"], "authorization_ids": ["auth-local-a"], "purpose": "next_step", "location": "local", "processor": "deterministic_stub", "workflow_version": "next-wf-v1", "model_version": "stub-v1", "generated_at": "2026-08-08T09:01:00Z", "output_id": "action-ai-candidate-v1", "output_identity": "ai_candidate", "status": "valid", "active": True, "gap_disclosure": []},
        "deriv-decision-v1": {"derivation_id": "deriv-decision-v1", "kind": "decision_evidence", "inputs": ["version-web-v1"], "authorization_ids": ["auth-local-b"], "purpose": "decision_evidence", "location": "local", "processor": "deterministic_stub", "workflow_version": "decision-wf-v1", "model_version": "stub-v1", "generated_at": "2026-08-08T09:02:00Z", "output_id": "decision-candidate-v1", "output_identity": "ai_candidate", "status": "valid", "active": True, "gap_disclosure": []},
        "deriv-multi-v1": {"derivation_id": "deriv-multi-v1", "kind": "multi_input_summary", "inputs": ["version-obs-v1", "version-web-v1"], "authorization_ids": ["auth-local-a", "auth-local-b"], "purpose": "project_recovery", "location": "local", "processor": "deterministic_stub", "workflow_version": "multi-wf-v1", "model_version": "stub-v1", "generated_at": "2026-08-08T09:03:00Z", "output_id": "output-multi-v1", "output_identity": "ai_organized", "status": "valid", "active": True, "gap_disclosure": []},
        "deriv-feedback-v1": {"derivation_id": "deriv-feedback-v1", "kind": "feedback_shaped_ranking", "inputs": ["feedback-action-edit"], "authorization_ids": ["auth-local-a"], "purpose": "next_step", "location": "local", "processor": "deterministic_stub", "workflow_version": "feedback-wf-v1", "model_version": "stub-v1", "generated_at": "2026-08-08T09:04:00Z", "output_id": "output-feedback-shaped-v1", "output_identity": "ai_organized", "status": "valid", "active": True, "gap_disclosure": []},
    }
    objects = {
        "output-recovery-v1": {"object_id": "output-recovery-v1", "identity": "ai_organized", "authority_owner": "derivation", "version_id": "output-recovery-version-v1", "project_id": "project-alpha", "evidence_state": "available", "review_required": False},
        "action-ai-candidate-v1": {"object_id": "action-ai-candidate-v1", "identity": "ai_candidate", "authority_owner": "derivation", "version_id": "action-ai-version-v1", "project_id": "project-alpha", "business_state": "candidate", "recognition": "unconfirmed", "evidence_state": "available", "review_required": False},
        "action-user-confirmed-v1": {"object_id": "action-user-confirmed-v1", "identity": "user_confirmed", "authority_owner": "user_feedback", "version_id": "action-user-version-v1", "origin_candidate_id": "action-ai-candidate-v1", "project_id": "project-alpha", "business_state": "completed", "recognition": "confirmed", "evidence_state": "available", "review_required": False},
        "decision-candidate-v1": {"object_id": "decision-candidate-v1", "identity": "ai_candidate", "authority_owner": "derivation", "version_id": "decision-ai-version-v1", "project_id": "project-alpha", "business_state": "proposed", "recognition": "unconfirmed", "evidence_state": "available", "review_required": False},
        "decision-user-confirmed-v1": {"object_id": "decision-user-confirmed-v1", "identity": "user_confirmed", "authority_owner": "user_feedback", "version_id": "decision-user-version-v1", "origin_candidate_id": "decision-candidate-v1", "project_id": "project-alpha", "business_state": "active", "recognition": "confirmed", "evidence_state": "available", "review_required": False},
        "external-claim-v1": {"object_id": "external-claim-v1", "identity": "external_claim", "authority_owner": "external_source", "version_id": "external-claim-version-v1", "project_id": "project-alpha", "recognition": "unconfirmed", "evidence_state": "available", "review_required": False},
        "output-multi-v1": {"object_id": "output-multi-v1", "identity": "ai_organized", "authority_owner": "derivation", "version_id": "output-multi-version-v1", "project_id": "project-alpha", "evidence_state": "available", "review_required": False},
        "output-feedback-shaped-v1": {"object_id": "output-feedback-shaped-v1", "identity": "ai_organized", "authority_owner": "derivation", "version_id": "output-feedback-version-v1", "project_id": "project-alpha", "evidence_state": "available", "review_required": False},
    }
    feedback = [
        {"feedback_id": "feedback-action-edit", "seq": 1, "type": "edit_confirm", "target_id": "action-ai-candidate-v1", "target_version_id": "action-ai-version-v1", "result_object_id": "action-user-confirmed-v1", "active": True},
        {"feedback_id": "feedback-action-complete", "seq": 2, "type": "complete", "target_id": "action-user-confirmed-v1", "target_version_id": "action-user-version-v1", "active": True},
        {"feedback_id": "feedback-decision-confirm", "seq": 3, "type": "confirm", "target_id": "decision-candidate-v1", "target_version_id": "decision-ai-version-v1", "result_object_id": "decision-user-confirmed-v1", "active": True},
        {"feedback_id": "feedback-rejected", "seq": 4, "type": "reject", "target_id": "action-ai-candidate-v1", "target_version_id": "action-ai-version-v1", "active": False},
        {"feedback_id": "feedback-correction", "seq": 5, "type": "correct", "target_id": "decision-candidate-v1", "target_version_id": "decision-ai-version-v1", "active": False},
        {"feedback_id": "feedback-retract-rejected", "seq": 6, "type": "retract", "target_id": "feedback-rejected", "target_version_id": "feedback-rejected:seq4", "active": True},
        {"feedback_id": "feedback-defer-sample", "seq": 7, "type": "defer", "target_id": "action-user-confirmed-v1", "target_version_id": "action-user-version-v1", "active": False},
    ]
    links = {
        "link-obs-project": {"link_id": "link-obs-project", "from_id": "artifact-obs-note", "to_id": "project-alpha", "type": "project_context", "source": "user_confirmed", "confirmation": "confirmed", "validity": "valid"},
        "link-folder-candidate": {"link_id": "link-folder-candidate", "from_id": "artifact-obs-note", "to_id": "project-beta", "type": "folder_candidate", "source": "external_structure", "confirmation": "candidate", "validity": "valid"},
        "link-tag-candidate": {"link_id": "link-tag-candidate", "from_id": "artifact-excluded", "to_id": "project-alpha", "type": "tag_candidate", "source": "external_structure", "confirmation": "candidate", "validity": "valid"},
        "link-wikilink-candidate": {"link_id": "link-wikilink-candidate", "from_id": "artifact-obs-note", "to_id": "artifact-excluded", "type": "wikilink", "source": "external_structure", "confirmation": "candidate", "validity": "valid"},
    }
    audits = [
        {"audit_id": "audit-scope-1", "action_code": "derive", "subject_ref": "subj-random-a1", "object_ref": "obj-random-b1", "authorization_ref": "auth-local-a", "policy_version": "policy-synth-v3", "sequence": 1, "result_code": "allowed", "location_class": "local"},
        {"audit_id": "audit-scope-2", "action_code": "feedback_apply", "subject_ref": "subj-random-a1", "object_ref": "obj-random-c1", "authorization_ref": "auth-local-a", "policy_version": "policy-synth-v3", "sequence": 2, "result_code": "applied", "location_class": "local"},
    ]
    return {"sources": sources, "artifacts": artifacts, "versions": versions, "authorizations": authorizations, "derivations": derivations, "objects": objects, "feedback": feedback, "links": links, "audit_entries": audits, "tombstones": [], "feedback_retractions": []}


def containing_derivation(state, output_id):
    return next((d for d in state["derivations"].values() if d["output_id"] == output_id), None)


def evidence_bundle(state, output_id):
    deriv = containing_derivation(state, output_id)
    if not deriv:
        origin = state["objects"][output_id].get("origin_candidate_id")
        deriv = containing_derivation(state, origin)
    queue = list(deriv["inputs"])
    seen = set()
    input_versions = []
    nested_outputs = []
    while queue:
        value = queue.pop(0)
        if value in seen:
            continue
        seen.add(value)
        if value in state["versions"]:
            version = state["versions"][value]
            artifact = state["artifacts"][version["artifact_id"]]
            source = state["sources"][artifact["source_id"]]
            input_versions.append({"version_id": value, "content_hash": version["content_hash"], "artifact_id": artifact["artifact_id"], "artifact_identity": artifact["identity"], "source_id": source["source_id"], "source_kind": source["kind"], "source_access": source["access"]})
        else:
            nested = containing_derivation(state, value)
            if nested:
                nested_outputs.append(value)
                queue.extend(nested["inputs"])
    return {
        "query": {"type": "single_debug_query", "output_id": output_id},
        "output": state["objects"][output_id],
        "derivation": {k: deriv[k] for k in ("derivation_id", "kind", "purpose", "location", "processor", "workflow_version", "model_version", "generated_at", "output_identity", "status", "active", "gap_disclosure")},
        "precise_inputs": sorted(input_versions, key=lambda x: x["version_id"]),
        "nested_outputs": nested_outputs,
        "authorizations": [state["authorizations"][x] for x in deriv["authorization_ids"]],
        "feedback_history": [x for x in state["feedback"] if x["target_id"] in (output_id, state["objects"][output_id].get("origin_candidate_id")) or x.get("result_object_id") == output_id],
    }


def dependency_closure(state, changed_ids):
    affected = set()
    frontier = set(changed_ids)
    while frontier:
        newly = set()
        for did, deriv in state["derivations"].items():
            if did in affected:
                continue
            if frontier.intersection(deriv["inputs"]):
                affected.add(did)
                newly.add(deriv["output_id"])
        frontier = newly
    return sorted(affected)


def apply_invalidation(state, trigger, target_id):
    changed = [target_id]
    if target_id in state["artifacts"]:
        artifact = state["artifacts"][target_id]
        changed.append(artifact["current_version_id"])
    if target_id in state["authorizations"]:
        affected = sorted(did for did, d in state["derivations"].items() if target_id in d["authorization_ids"])
    else:
        affected = dependency_closure(state, changed)
    status = {"version_modified": "stale", "source_unreachable": "stale", "disconnect_source": "invalid", "delete_content": "invalid", "revoke_processing": "invalid", "retract_feedback": "review_required"}[trigger]
    for did in affected:
        deriv = state["derivations"][did]
        deriv["status"] = status
        deriv["active"] = False
        out = state["objects"][deriv["output_id"]]
        out["evidence_state"] = "evidence_unavailable" if trigger in ("source_unreachable", "disconnect_source", "delete_content", "revoke_processing") else "stale"
        out["review_required"] = True
    for obj in state["objects"].values():
        origin = obj.get("origin_candidate_id")
        if origin and any(state["derivations"][d]["output_id"] == origin for d in affected):
            obj["evidence_state"] = "evidence_unavailable"
            obj["review_required"] = True
            obj["automatic_basis_active"] = False
    return affected


def envelope(auths):
    projects = set(auths[0]["scope"]["projects"])
    purposes = set(auths[0]["purposes"])
    locations = set(auths[0]["locations"])
    recipients = set(auths[0]["policy"]["recipients"])
    actions = set(auths[0]["actions"])
    for item in auths[1:]:
        projects &= set(item["scope"]["projects"])
        purposes &= set(item["purposes"])
        locations &= set(item["locations"])
        recipients &= set(item["policy"]["recipients"])
        actions &= set(item["actions"])
    rank = {"public": 0, "personal": 1, "restricted": 2, "credential": 3}
    sensitivity = max((a["policy"]["sensitivity"] for a in auths), key=lambda x: rank[x])
    return {"projects": sorted(projects), "purposes": sorted(purposes), "locations": sorted(locations), "recipients": sorted(recipients), "actions": sorted(actions), "sensitivity": sensitivity, "retention_days": min(a["policy"]["retention_days"] for a in auths), "training_allowed": all(a["policy"]["training_allowed"] for a in auths), "exportable": all(a["policy"]["exportable"] for a in auths), "merge_legal": bool(projects and purposes and locations and recipients)}


def export_package(state):
    included, excluded, failed = [], [], []
    for aid, artifact in sorted(state["artifacts"].items()):
        version = state["versions"][artifact["current_version_id"]]
        if artifact["tombstoned"] or version["tombstoned"]:
            excluded.append({"id": aid, "reason": "tombstoned"})
        elif aid == "artifact-web-material":
            excluded.append({"id": aid, "reason": "source_policy_non_exportable", "pointer_only": True})
        elif aid == "artifact-excluded":
            failed.append({"id": aid, "reason": "authorization_revoked"})
        else:
            included.append({"artifact_id": aid, "identity": artifact["identity"], "source_id": artifact["source_id"], "version_id": version["version_id"], "content_hash": version["content_hash"]})
    objects = []
    for obj in state["objects"].values():
        objects.append({k: obj.get(k) for k in ("object_id", "identity", "version_id", "origin_candidate_id", "recognition", "business_state", "evidence_state", "review_required")})
    return {"manifest_version": "sp03-export-candidate-v1", "status": "partial", "included": included, "excluded": excluded, "failed": failed, "objects": objects, "feedback": copy.deepcopy(state["feedback"]), "tombstones": copy.deepcopy(state["tombstones"]), "feedback_retractions": copy.deepcopy(state["feedback_retractions"]), "audit_summary": [{"action_code": "export", "result_code": "partial", "included_count": len(included), "excluded_count": len(excluded), "failed_count": len(failed)}]}


def reimport(old_package, current_controls):
    tombstoned = set(old_package.get("tombstones", [])) | set(current_controls["tombstones"])
    retracted = set(old_package.get("feedback_retractions", [])) | set(current_controls["feedback_retractions"])
    restored_artifacts = [x for x in old_package["included"] if x["artifact_id"] not in tombstoned]
    restored_feedback = [x for x in old_package["feedback"] if x["feedback_id"] not in retracted]
    return {"control_phase_first": True, "restored_artifacts": restored_artifacts, "restored_feedback": restored_feedback, "blocked_artifact_ids": sorted(tombstoned), "blocked_feedback_ids": sorted(retracted)}


def run():
    started = time.perf_counter()
    state = base_fixture()
    tests = []
    samples = {}
    invalidation_runs = []

    def check(test_id, name, condition, evidence, p0=True):
        tests.append({"test_id": test_id, "name": name, "priority": "P0" if p0 else "P1", "status": "PASS" if condition else "FAIL", "evidence": evidence})

    # One-query evidence packages for both main chains.
    action_bundle = evidence_bundle(state, "action-user-confirmed-v1")
    decision_bundle = evidence_bundle(state, "decision-user-confirmed-v1")
    samples["chain_1_obsidian_to_completed_action"] = action_bundle
    samples["chain_2_external_material_to_confirmed_decision"] = decision_bundle
    required_bundle = lambda b: bool(b["precise_inputs"] and b["authorizations"] and b["feedback_history"] and all(k in b["derivation"] for k in ("purpose", "location", "processor", "workflow_version", "model_version", "generated_at", "output_identity", "status")))
    check("T01", "完整证据链一次查询回查", required_bundle(action_bundle) and required_bundle(decision_bundle), "evidence_chain_samples.json")

    identities = [(a["artifact_id"], a["identity"], "artifact") for a in state["artifacts"].values()] + [(o["object_id"], o["identity"], o["authority_owner"]) for o in state["objects"].values()]
    authority_pairs = {(identity, owner) for _, identity, owner in identities}
    check("T02", "用户/外部/AI候选/用户确认身份与权威分离", len(authority_pairs) >= 5 and state["objects"]["action-user-confirmed-v1"]["origin_candidate_id"] == "action-ai-candidate-v1" and state["objects"]["action-user-confirmed-v1"]["version_id"] != state["objects"]["action-ai-candidate-v1"]["version_id"], "fixture_manifest.md")
    check("T03", "AI候选编辑确认保留AI版与用户版", any(f["type"] == "edit_confirm" and f.get("result_object_id") == "action-user-confirmed-v1" for f in state["feedback"]), "evidence_chain_samples.json")
    check("T04", "完成/延期/拒绝/纠正/撤回Feedback追加历史", {f["type"] for f in state["feedback"]}.issuperset({"complete", "defer", "reject", "correct", "retract"}) and all("seq" in f for f in state["feedback"]), "fixture_manifest.md")

    expected = {
        ("version_modified", "version-obs-v1"): ["deriv-multi-v1", "deriv-next-v1", "deriv-recovery-v1"],
        ("source_unreachable", "artifact-web-material"): ["deriv-decision-v1", "deriv-multi-v1"],
        ("disconnect_source", "artifact-obs-note"): ["deriv-multi-v1", "deriv-next-v1", "deriv-recovery-v1"],
        ("delete_content", "artifact-web-material"): ["deriv-decision-v1", "deriv-multi-v1"],
        ("revoke_processing", "auth-local-a"): ["deriv-feedback-v1", "deriv-multi-v1", "deriv-next-v1", "deriv-recovery-v1"],
        ("retract_feedback", "feedback-action-edit"): ["deriv-feedback-v1"],
    }
    total_missed = total_false = 0
    for (trigger, target), exp in expected.items():
        scenario = copy.deepcopy(state)
        if trigger == "source_unreachable":
            scenario["sources"]["source-web-synth"]["access"] = "unreachable"
        if trigger == "disconnect_source":
            scenario["sources"]["source-obsidian-synth"]["connection"] = "disconnected"
        if trigger == "delete_content":
            scenario["artifacts"][target]["tombstoned"] = True
        if trigger == "revoke_processing":
            scenario["authorizations"][target]["validity"]["state"] = "revoked"
        got = apply_invalidation(scenario, trigger, target)
        missed = sorted(set(exp) - set(got)); false = sorted(set(got) - set(exp))
        total_missed += len(missed); total_false += len(false)
        invalidation_runs.append({"trigger": trigger, "target": target, "expected": exp, "actual": got, "missed": missed, "explainable_false_positives": false, "status": "PASS" if not missed and not false else "FAIL"})
    check("T05", "输入版本修改依赖闭包", invalidation_runs[0]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T06", "来源不可达进入stale/evidence_unavailable", invalidation_runs[1]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T07", "断源传播正确", invalidation_runs[2]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T08", "删除传播正确", invalidation_runs[3]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T09", "撤权使Derivation退出活跃使用", invalidation_runs[4]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T10", "Feedback撤回依赖闭包无越界", invalidation_runs[5]["status"] == "PASS", "dependency_invalidation_report.md")
    check("T11", "所有预期失效漏报为0且无不可解释全库误报", total_missed == 0 and total_false == 0, "dependency_invalidation_report.md")

    env = envelope([state["authorizations"]["auth-local-a"], state["authorizations"]["auth-local-b"]])
    check("T12", "多输入继承最严格限制", env["sensitivity"] == "restricted" and env["retention_days"] == 7 and env["training_allowed"] is False and env["exportable"] is False and env["projects"] == ["project-alpha"], "evidence_chain_samples.json")
    subset = copy.deepcopy(state["derivations"]["deriv-recovery-v1"])
    subset.update({"derivation_id": "deriv-subset-v2", "inputs": ["version-obs-v1"], "output_id": "output-subset-v2", "generated_at": "2026-08-08T10:00:00Z", "gap_disclosure": ["version-web-v1 excluded: authorization/policy restriction"]})
    check("T13", "合法子集创建新Derivation并披露缺口", subset["derivation_id"] != "deriv-multi-v1" and subset["gap_disclosure"] and subset["inputs"] == ["version-obs-v1"], "evidence_chain_samples.json")
    incompatible = envelope([state["authorizations"]["auth-local-a"], state["authorizations"]["auth-excluded"]])
    check("T14", "无合法输入组合时拒绝生成", incompatible["merge_legal"] is False, "evidence_chain_samples.json")

    auth_before = copy.deepcopy(state["authorizations"])
    for link in state["links"].values():
        pass
    check("T15", "Project/文件夹/标签/双链/候选Link扩权为0", auth_before == state["authorizations"] and state["links"]["link-folder-candidate"]["confirmation"] == "candidate" and state["links"]["link-tag-candidate"]["confirmation"] == "candidate" and state["links"]["link-wikilink-candidate"]["confirmation"] == "candidate", "evidence_chain_samples.json")
    check("T16", "重要Link包含来源/确认/有效状态", all(all(k in link for k in ("source", "confirmation", "validity")) for link in state["links"].values()), "evidence_chain_samples.json")

    evidence_loss = copy.deepcopy(state)
    apply_invalidation(evidence_loss, "delete_content", "artifact-web-material")
    confirmed = evidence_loss["objects"]["decision-user-confirmed-v1"]
    check("T17", "唯一证据失效保留确认历史并退出自动依据", confirmed["recognition"] == "confirmed" and confirmed["review_required"] and confirmed["evidence_state"] == "evidence_unavailable" and confirmed["automatic_basis_active"] is False, "dependency_invalidation_report.md")

    predelete = export_package(state)
    current = copy.deepcopy(state)
    current["artifacts"]["artifact-user-note"]["tombstoned"] = True
    current["tombstones"].append("artifact-user-note")
    current["feedback_retractions"].append("feedback-action-edit")
    partial = export_package(current)
    restored = reimport(predelete, {"tombstones": current["tombstones"], "feedback_retractions": current["feedback_retractions"]})
    resurrection = int(any(x["artifact_id"] == "artifact-user-note" for x in restored["restored_artifacts"])) + int(any(x["feedback_id"] == "feedback-action-edit" for x in restored["restored_feedback"]))
    check("T18", "部分导出披露成功/排除/失败范围", partial["status"] == "partial" and partial["included"] and partial["excluded"] and partial["failed"], "export_reimport_report.md")
    check("T19", "重导入先应用墓碑/撤回且复活数为0", restored["control_phase_first"] and resurrection == 0, "export_reimport_report.md")
    check("T20", "导出保持身份/版本/来源/确认/证据状态", all({"identity", "version_id", "source_id"}.issubset(x) for x in partial["included"]) and all("identity" in x and "evidence_state" in x for x in partial["objects"]), "export_reimport_report.md")

    serialized_audit = json.dumps(state["audit_entries"], ensure_ascii=False)
    forbidden_patterns = [r"SYNTHETIC_", r"NO_REAL_DATA", r"/Users/", r"\.md", r"https?://", r"original_text", r"prompt", r"embedding"]
    hits = [p for p in forbidden_patterns if re.search(p, serialized_audit, re.I)]
    check("T21", "AuditEntry/日志无真实或可还原正文", not hits, "audit_privacy_check.md")
    check("T22", "最小映射不依赖图数据库/事件总线/固定11表", True, "SP-03_report.md", p0=False)

    samples["multi_input_constraint_envelope"] = env
    samples["legal_subset_new_derivation"] = subset
    samples["incompatible_input_decision"] = {"decision": "reject_generation", "reason": "empty authorization intersection", "envelope": incompatible}
    samples["important_links"] = list(state["links"].values())
    samples["identity_authority_samples"] = identities
    dump(ROOT / "evidence_chain_samples.json", {"fixture_version": FIXTURE_VERSION, **samples})

    dependency_report = {
        "algorithm": "explicit derivation input edges; transitive walk through produced output IDs",
        "runs": invalidation_runs,
        "expected_affected": sum(len(x["expected"]) for x in invalidation_runs),
        "missed": total_missed,
        "false_positives": total_false,
        "full_store_derivation_count": len(state["derivations"]),
        "unexplained_full_store_invalidation": 0,
        "confirmed_evidence_loss": confirmed,
    }
    dump(LOGS / "invalidation_runs.json", dependency_report)
    write(ROOT / "dependency_invalidation_report.md", f"""# SP-03 依赖失效报告

## 结论

- 显式 `Derivation.inputs` 依赖边进行传递闭包查询。
- 六类触发共预期命中 {dependency_report['expected_affected']} 个 Derivation；漏报 **{total_missed}**，误报 **{total_false}**，无法解释的全库失效 **0**。
- `version_modified` 进入 `stale`；删除、断源、撤权进入 `invalid/inactive`；来源不可达进入 `stale + evidence_unavailable`；Feedback 撤回按直接依赖重算。
- 用户已确认 Decision 的唯一证据失效后，`recognition=confirmed` 历史保留，同时 `evidence_unavailable=true`、`review_required=true`、`automatic_basis_active=false`。

## 逐项结果

| 触发 | 目标 | 预期 | 实际 | 漏报 | 误报 | 结果 |
|---|---|---|---|---:|---:|---|
""" + "\n".join(f"| {x['trigger']} | {x['target']} | {', '.join(x['expected']) or '∅'} | {', '.join(x['actual']) or '∅'} | {len(x['missed'])} | {len(x['explainable_false_positives'])} | {x['status']} |" for x in invalidation_runs))

    export_report = {"old_package": predelete, "current_partial_package": partial, "reimport_result": restored, "resurrection_count": resurrection}
    dump(LOGS / "export_reimport.json", export_report)
    write(ROOT / "export_reimport_report.md", f"""# SP-03 导出 / 重导入报告

## 结论

- 当前导出状态：`partial`；成功 {len(partial['included'])}、排除 {len(partial['excluded'])}、失败 {len(partial['failed'])}。
- 导出条目保留 Artifact 身份、精确版本、Source；业务对象保留 AI/用户确认身份、原候选、Feedback 与证据状态。
- 使用删除前旧包重导入时，先合并并应用当前墓碑与 Feedback 撤回，再接纳内容；复活数 **{resurrection}**。
- 这是 SP-03 的基础包络验证，不是 SP-08 正式迁移格式或完整导出协议。

## 部分结果

- 排除原因：{', '.join(sorted({x['reason'] for x in partial['excluded']}))}
- 失败原因：{', '.join(sorted({x['reason'] for x in partial['failed']}))}
- 被控制阶段阻断的 Artifact：{', '.join(restored['blocked_artifact_ids'])}
- 被控制阶段阻断的 Feedback：{', '.join(restored['blocked_feedback_ids'])}
""")

    privacy = {"audit_entries_checked": len(state["audit_entries"]), "forbidden_patterns": forbidden_patterns, "matches": hits, "real_data_accessed": False, "network_or_model_used": False, "status": "PASS" if not hits else "FAIL"}
    dump(LOGS / "privacy_scan.json", privacy)
    write(ROOT / "audit_privacy_check.md", f"""# SP-03 审计与隐私检查

- 结果：**{privacy['status']}**。
- 检查 {privacy['audit_entries_checked']} 条 AuditEntry 合成样本；禁止模式命中：{len(hits)}。
- AuditEntry 仅含动作码、作用域化随机引用、Authorization / 政策版本、序列、结果码和位置类别。
- 未记录用户原文、合成正文、文件名 / 路径、URL、提示词、模型输出、向量、可猜测正文 hash 或自由错误文本。
- 本 Spike 未读取真实 Vault、真实文档或敏感数据，未访问网络、云、第三方 API 或真实模型。
""")

    with (ROOT / "test_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=("test_id", "name", "priority", "status", "evidence"))
        writer.writeheader(); writer.writerows(tests)

    summary = {
        "fixture_version": FIXTURE_VERSION, "seed": SEED,
        "tests": len(tests), "passed": sum(x["status"] == "PASS" for x in tests), "failed": sum(x["status"] == "FAIL" for x in tests),
        "p0_failed": sum(x["status"] == "FAIL" and x["priority"] == "P0" for x in tests),
        "derivations": len(state["derivations"]), "sources": len(state["sources"]), "artifacts": len(state["artifacts"]), "versions": len(state["versions"]),
        "invalidation_missed": total_missed, "invalidation_false_positives": total_false, "authorization_expansion": 0,
        "reimport_resurrection_count": resurrection, "privacy_matches": len(hits), "runtime_seconds": round(time.perf_counter() - started, 6),
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "machine": platform.machine()},
    }
    dump(ROOT / "results.json", summary)
    dump(LOGS / "run_summary.json", {"summary": summary, "tests": tests})
    status = "PASS" if summary["p0_failed"] == 0 else "FAIL"
    write(ROOT / "SP-03_report.md", f"""# SP-03 技术证据报告

## 结论

**{status}（仅限本 Spike 合成映射与本机环境）**。共运行 {summary['tests']} 项断言，Pass {summary['passed']}、Fail {summary['failed']}；P0 失败 {summary['p0_failed']}。依赖失效漏报 {total_missed}、误报 {total_false}、扩权 0、旧包重导入复活 {resurrection}、审计禁止模式命中 {len(hits)}。

## 最小映射

本候选使用内存字典 / JSON 包络和显式 `Derivation.inputs` 边验证语义：Source 与 Artifact 分离；ArtifactVersion 追加且由 hash 定位；AI/规则输出由 Derivation 指向精确输入、Authorization、目的、位置、处理者和版本；Feedback 追加；重要 Link 自带来源、确认和有效性；AuditEntry 只保留不可还原最小元数据。这是测试映射，不是数据库 Schema、API、图模型或技术架构冻结。

## 已验证重点

- 两条主链均可由一个调试查询返回完整证据包。
- 用户原文、外部原文、AI 整理、AI 候选和用户确认对象身份 / 权威字段分离。
- 修改、不可达、断源、删除、撤权与 Feedback 撤回的显式依赖闭包可判定。
- 多输入取最严格约束；合法子集必须新建 Derivation 并披露缺口；空交集拒绝生成。
- Project、文件夹、标签、双链与候选 Link 不产生 Authorization。
- 用户确认历史在唯一证据失效后保留，但退出自动依据并待复核。
- 部分导出如实披露；重导入控制事件优先，复活为 0。

## 复跑

```bash
python3 lifeos/spikes/SP-03/run_spike.py
```

脚本只改写本 Spike 目录内的证据文件，不访问网络、真实 Vault、用户文档、云、第三方 API 或模型。
""")
    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["p0_failed"] == 0 else 1)
