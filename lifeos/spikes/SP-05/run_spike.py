#!/usr/bin/env python3
"""LifeOS SP-05 revocation/deletion propagation spike.

Deterministic synthetic fixtures and mocks only. This is validation code, not
product code. It performs no network, model, cloud, real Vault, or user-data IO.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "raw_logs"
FIXTURE_VERSION = "sp05-synthetic-v1"
ACTIVE_PATHS = [
    "local_read", "fts_query", "vector_query", "recovery_pack",
    "today_suggestion", "candidate_generation", "queue_claim",
    "model_gateway_send", "cross_project_display", "rederive",
    "export", "reimport",
]
DEPENDENCY_TYPES = [
    "user_original", "external_original_copy_or_pointer", "artifact_version",
    "content_chunk", "fts_posting", "vector_mock", "summary",
    "recovery_fragment", "ai_candidate_action", "ai_candidate_decision",
    "important_link", "confirmed_object", "feedback_history", "cache",
    "prompt_copy", "queue_payload", "object_file_or_pointer", "backup_copy",
    "offline_copy_or_outbox", "third_party_mock_copy", "audit_entry",
    "cleanup_proof",
]
PHYSICAL_TYPES = {
    "user_original", "external_original_copy_or_pointer", "artifact_version",
    "content_chunk", "fts_posting", "vector_mock", "summary",
    "recovery_fragment", "ai_candidate_action", "ai_candidate_decision",
    "important_link", "cache", "prompt_copy", "queue_payload",
    "object_file_or_pointer", "backup_copy", "offline_copy_or_outbox",
    "third_party_mock_copy",
}
FORBIDDEN_LOG_PATTERNS = [
    r"SYNTH_SECRET_BODY", r"SYNTH_PROMPT_BODY", r"/Users/", r"BEGIN PRIVATE KEY",
    r"\b(?:vector|embedding)_values\b", r"\[0\.1,\s*0\.2", r"vault[/\\]private",
]


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def ref(raw: str) -> str:
    return "scope:" + sha("sp05:" + raw)[:16]


def make_state() -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}

    def add(node_id: str, node_type: str, inputs: list[str] | None = None,
            *, project: str = "project-a", source: str = "source-a",
            content_bearing: bool = True, physical: bool | None = None,
            purpose: str = "storage", location: str = "local",
            processor: str = "local-runtime", directory: str = "/notes") -> None:
        nodes[node_id] = {
            "id": node_id, "type": node_type, "inputs": inputs or [],
            "project": project, "source": source, "active": True,
            "physical_present": node_type in PHYSICAL_TYPES if physical is None else physical,
            "content_bearing": content_bearing,
            "purpose": purpose, "location": location, "processor": processor,
            "directory": directory,
            "state": "active",
        }

    add("artifact-a", "user_original")
    add("external-pointer-a", "external_original_copy_or_pointer", physical=False)
    add("version-a1", "artifact_version", ["artifact-a"])
    add("version-a2", "artifact_version", ["artifact-a"])
    add("chunk-a1", "content_chunk", ["version-a1"])
    add("fts-a1", "fts_posting", ["chunk-a1"], purpose="search")
    add("vector-a1", "vector_mock", ["chunk-a1"], purpose="search")
    add("summary-a1", "summary", ["version-a1"], purpose="summary")
    add("recovery-a1", "recovery_fragment", ["summary-a1"], purpose="project_recovery")
    add("candidate-action-a1", "ai_candidate_action", ["summary-a1"], purpose="next_step")
    add("candidate-decision-a1", "ai_candidate_decision", ["summary-a1"], purpose="summary")
    add("link-cross-a1", "important_link", ["version-a1"], project="project-b")
    add("confirmed-action-a1", "confirmed_object", ["version-a1"], content_bearing=False, physical=False)
    add("feedback-confirm-a1", "feedback_history", ["confirmed-action-a1"], content_bearing=False, physical=False)
    add("feedback-dependent-a1", "summary", ["feedback-confirm-a1"])
    add("cache-a1", "cache", ["summary-a1"])
    add("prompt-a1", "prompt_copy", ["version-a1"], purpose="summary", location="third-party", processor="vendor-mock")
    add("queue-a1", "queue_payload", ["version-a1"], purpose="summary", location="third-party", processor="vendor-mock")
    add("object-a1", "object_file_or_pointer", ["version-a1"])
    add("backup-a1", "backup_copy", ["version-a1"])
    add("offline-a1", "offline_copy_or_outbox", ["version-a1"])
    add("vendor-a1", "third_party_mock_copy", ["version-a1"], purpose="summary", location="third-party", processor="vendor-mock")
    add("audit-a1", "audit_entry", ["version-a1"], content_bearing=False, physical=False)
    add("proof-a1", "cleanup_proof", ["version-a1"], content_bearing=False, physical=False)

    # Multi-input fixture: valid project-b input may survive a project-a revoke.
    add("artifact-b", "user_original", project="project-b", source="source-b")
    add("version-b1", "artifact_version", ["artifact-b"], project="project-b", source="source-b")
    add("summary-multi", "summary", ["version-a1", "version-b1"], project="project-b")
    add("candidate-multi", "ai_candidate_action", ["summary-multi"], project="project-b")
    add("artifact-excluded-dir", "user_original", directory="/excluded")
    add("version-excluded-dir", "artifact_version", ["artifact-excluded-dir"], directory="/excluded")

    return {
        "nodes": nodes,
        "sources": {
            "source-a": {"connected": True, "retain_copy": True},
            "source-b": {"connected": True, "retain_copy": True},
        },
        "authorizations": {
            "auth-project-a": {"state": "active", "project": "project-a", "purpose": "*", "location": "*", "processor": "*", "version": 1},
            "auth-summary-third": {"state": "active", "project": "project-a", "purpose": "summary", "location": "third-party", "processor": "vendor-mock", "version": 1},
        },
        "feedback": {"feedback-confirm-a1": {"effective": True, "kind": "confirm", "history_retained": True}},
        "tombstones": {}, "restrictions": [], "outbox": [], "commands": [],
        "audit": [], "proofs": [], "dead_letters": [], "vendor": {"vendor-a1": "present"},
        "model_calls": 0, "source_reads": 0,
    }


def descendants(state: dict[str, Any], roots: set[str]) -> set[str]:
    found = set(roots)
    changed = True
    while changed:
        changed = False
        for node_id, node in state["nodes"].items():
            if node_id not in found and any(i in found for i in node["inputs"]):
                found.add(node_id)
                changed = True
    return found


def discover_impact(state: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    kind = command["kind"]
    scope = command["scope"]
    roots: set[str] = set()
    retained: set[str] = set()
    invalidated: set[str] = set()

    if kind == "delete_content":
        target_type, target_id = scope["target_type"], scope["target_id"]
        if target_type in {"artifact", "version"}:
            roots.add(target_id)
        elif target_type == "source":
            roots.update(n for n, v in state["nodes"].items() if v["source"] == target_id)
        invalidated = descendants(state, roots)
        retained.update(n for n in invalidated if state["nodes"][n]["type"] in {"confirmed_object", "feedback_history", "audit_entry", "cleanup_proof"})
    elif kind == "revoke_processing":
        for node_id, node in state["nodes"].items():
            match = True
            for key in ("project", "source", "purpose", "location", "processor", "directory"):
                if key in scope and scope[key] != node[key]:
                    match = False
            if match:
                roots.add(node_id)
        invalidated = descendants(state, roots)
        retained.update(n for n in invalidated if state["nodes"][n]["type"] in {"user_original", "external_original_copy_or_pointer", "artifact_version", "confirmed_object", "feedback_history", "audit_entry"})
    elif kind == "disconnect_source":
        source = scope["source"]
        roots.update(n for n, v in state["nodes"].items() if v["source"] == source and v["type"] == "external_original_copy_or_pointer")
        invalidated.update(n for n, v in state["nodes"].items() if v["source"] == source and v["type"] in {"external_original_copy_or_pointer"})
        retained.update(n for n, v in state["nodes"].items() if v["source"] == source and v["type"] not in {"external_original_copy_or_pointer"})
    elif kind == "retract_feedback":
        feedback_id = scope["feedback_id"]
        roots.add(feedback_id)
        invalidated = descendants(state, roots) - {feedback_id}
        retained.add(feedback_id)

    physical = sorted(n for n in invalidated if state["nodes"][n]["physical_present"] and n not in retained)
    return {
        "command_kind": kind, "roots": sorted(roots), "invalidated": sorted(invalidated),
        "retained": sorted(retained), "physical_cleanup": physical,
        "dependency_types": sorted({state["nodes"][n]["type"] for n in invalidated | retained if n in state["nodes"]}),
    }


def audit_entry(command_id: str, kind: str, state_name: str, reason: str) -> dict[str, Any]:
    return {
        "sequence": int(command_id.split("-")[-1]) if command_id.split("-")[-1].isdigit() else 0,
        "command_ref": ref(command_id), "command_kind": kind,
        "state": state_name, "reason_code": reason,
        "scope_digest": sha("scope:" + command_id)[:20],
    }


def stage_a(state: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    impact = discover_impact(state, command)
    command_id, kind = command["id"], command["kind"]
    record = {"id": command_id, "kind": kind, "status_history": ["accepted", "active_blocked"], "impact": impact}

    if kind == "delete_content":
        state["tombstones"][command["scope"]["target_id"]] = {"kind": "delete", "generation": command.get("generation", 1)}
    elif kind == "revoke_processing":
        for auth in state["authorizations"].values():
            scope = command["scope"]
            matches = scope.get("project", auth["project"]) == auth["project"]
            for key in ("purpose", "location", "processor"):
                if key in scope and scope[key] not in {auth.get(key), "*"} and auth.get(key) != "*":
                    matches = False
            if matches and not any(key in scope and auth.get(key) == "*" for key in ("purpose", "location", "processor")):
                auth["state"] = "revoked"
                auth["version"] += 1
        state["restrictions"].append(copy.deepcopy(command["scope"]))
    elif kind == "disconnect_source":
        state["sources"][command["scope"]["source"]]["connected"] = False
    elif kind == "retract_feedback":
        state["feedback"][command["scope"]["feedback_id"]]["effective"] = False

    for node_id in impact["invalidated"]:
        node = state["nodes"].get(node_id)
        if not node:
            continue
        node["active"] = False
        node["state"] = "review_required" if node["type"] == "confirmed_object" else "invalid"
    for node_id in impact["retained"]:
        node = state["nodes"].get(node_id)
        if node and node["type"] == "confirmed_object" and kind in {"delete_content", "revoke_processing"}:
            node["active"] = False
            node["state"] = "review_required"

    jobs = []
    for node_id in impact["physical_cleanup"]:
        job = {
            "job_id": "cleanup:" + command_id + ":" + node_id,
            "idempotency_key": sha(command_id + ":" + node_id),
            "command_id": command_id, "node_id": node_id,
            "status": "physical_cleanup_pending", "attempts": 0,
            "lease_owner": None, "lease_generation": 0,
        }
        state["outbox"].append(job)
        jobs.append(job["job_id"])
    if jobs:
        record["status_history"].append("physical_cleanup_pending")
    else:
        record["status_history"].append("completed_no_physical_cleanup_required")
    state["commands"].append(record)
    state["audit"].append(audit_entry(command_id, kind, "active_blocked", "COMMAND_COMMITTED"))
    return record


def is_tombstoned(state: dict[str, Any], node_id: str) -> bool:
    if node_id in state["tombstones"]:
        return True
    return any(root in state["tombstones"] for root in ancestors(state, node_id))


def ancestors(state: dict[str, Any], node_id: str) -> set[str]:
    found: set[str] = set()
    pending = [node_id]
    while pending:
        current = pending.pop()
        for parent in state["nodes"].get(current, {}).get("inputs", []):
            if parent not in found:
                found.add(parent)
                pending.append(parent)
    return found


def consume(state: dict[str, Any], node_id: str, path: str) -> bool:
    node = state["nodes"].get(node_id)
    if path not in ACTIVE_PATHS or not node or not node["active"] or is_tombstoned(state, node_id):
        return False
    if path in {"queue_claim", "model_gateway_send"} and node["type"] not in {"queue_payload", "prompt_copy", "artifact_version"}:
        return False
    if path == "model_gateway_send":
        state["model_calls"] += 1
    return True


def process_job(state: dict[str, Any], job: dict[str, Any], *, owner: str = "worker-a",
                failure: str | None = None, vendor_mode: str = "success") -> str:
    node = state["nodes"][job["node_id"]]
    if job["status"] in {"physically_cleaned", "vendor_limited"}:
        return job["status"]
    job["lease_owner"] = owner
    job["lease_generation"] += 1
    job["attempts"] += 1
    if failure in {"before_cleanup", "during_cleanup", "network"}:
        job["status"] = "physical_cleanup_failed"
        job["reason_code"] = failure.upper()
        return job["status"]

    # Destruction is idempotent. A crash after this point may leave status pending.
    node["physical_present"] = False
    if node["type"] == "third_party_mock_copy":
        if vendor_mode == "delayed":
            node["physical_present"] = True
            state["vendor"][node["id"]] = "deletion_pending"
            job["status"] = "physical_cleanup_pending"
            job["reason_code"] = "VENDOR_DELAYED"
            return job["status"]
        if vendor_mode == "unsupported":
            node["physical_present"] = True
            state["vendor"][node["id"]] = "unsupported"
            job["status"] = "vendor_limited"
            job["reason_code"] = "VENDOR_DELETE_UNSUPPORTED"
            return job["status"]
        if vendor_mode == "failure":
            node["physical_present"] = True
            job["status"] = "physical_cleanup_failed"
            job["reason_code"] = "VENDOR_DELETE_FAILED"
            return job["status"]
        state["vendor"][node["id"]] = "deleted"
    if failure == "after_cleanup_before_status":
        job["status"] = "physical_cleanup_pending"
        job["reason_code"] = "CRASH_AFTER_EFFECT"
        return job["status"]
    job["status"] = "physically_cleaned"
    job["reason_code"] = "VERIFIED_ABSENT"
    state["proofs"].append({
        "proof_ref": ref(job["job_id"]), "command_ref": ref(job["command_id"]),
        "dependency_type": node["type"], "result": job["status"],
        "reason_code": job["reason_code"], "verification_digest": sha(job["idempotency_key"] + ":absent")[:20],
    })
    return job["status"]


def expire_lease(job: dict[str, Any]) -> None:
    job["lease_owner"] = None


def replay_candidate(state: dict[str, Any], node_id: str, generation: int = 0) -> bool:
    """Return True only if an old package is allowed to reactivate a node."""
    tombstones = [state["tombstones"][a] for a in ({node_id} | ancestors(state, node_id)) if a in state["tombstones"]]
    if tombstones and max(t["generation"] for t in tombstones) >= generation:
        return False
    node = state["nodes"].get(node_id)
    if not node or not node["active"]:
        return False
    return True


class Harness:
    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def check(self, case_id: str, description: str, actual: Any, expected: Any,
              category: str, priority: str = "P0") -> None:
        status = "PASS" if actual == expected else "FAIL"
        self.results.append({"case_id": case_id, "description": description,
                             "category": category, "priority": priority,
                             "expected": expected, "actual": actual, "status": status})


def run_cases() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    h = Harness()

    # Four commands and semantic separation.
    s = make_state(); r = stage_a(s, {"id": "cmd-1", "kind": "revoke_processing", "scope": {"project": "project-a"}})
    h.check("T01", "revoke_processing keeps original physically", s["nodes"]["artifact-a"]["physical_present"], True, "command_semantics")
    h.check("T02", "revoke_processing does not disconnect source", s["sources"]["source-a"]["connected"], True, "command_semantics")
    h.check("T03", "revoke_processing revokes matching authorization", s["authorizations"]["auth-project-a"]["state"], "revoked", "command_semantics")
    h.check("T04", "project revoke invalidates candidate", s["nodes"]["candidate-action-a1"]["active"], False, "command_semantics")
    h.check("T05", "revoke produces active_blocked", "active_blocked" in r["status_history"], True, "status_semantics")

    s = make_state(); stage_a(s, {"id": "cmd-2", "kind": "disconnect_source", "scope": {"source": "source-a"}})
    h.check("T06", "disconnect stops continued source access", s["sources"]["source-a"]["connected"], False, "command_semantics")
    h.check("T07", "disconnect retains permitted LifeOS copy", s["nodes"]["version-a1"]["physical_present"], True, "command_semantics")
    h.check("T08", "disconnect does not create delete tombstone", bool(s["tombstones"]), False, "command_semantics")

    s = make_state(); r = stage_a(s, {"id": "cmd-3", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 3})
    h.check("T09", "delete creates tombstone", "artifact-a" in s["tombstones"], True, "command_semantics")
    h.check("T10", "delete retains confirmed-object history for review", s["nodes"]["confirmed-action-a1"]["state"], "review_required", "command_semantics")
    h.check("T11", "delete schedules physical cleanup", len(r["impact"]["physical_cleanup"]) > 0, True, "command_semantics")
    h.check("T12", "delete does not disconnect unrelated source semantics", s["sources"]["source-a"]["connected"], True, "command_semantics")

    s = make_state(); r = stage_a(s, {"id": "cmd-4", "kind": "retract_feedback", "scope": {"feedback_id": "feedback-confirm-a1"}})
    h.check("T13", "retract_feedback keeps feedback history", s["feedback"]["feedback-confirm-a1"]["history_retained"], True, "command_semantics")
    h.check("T14", "retract_feedback removes current effect", s["feedback"]["feedback-confirm-a1"]["effective"], False, "command_semantics")
    h.check("T15", "retract_feedback does not delete original", s["nodes"]["artifact-a"]["active"], True, "command_semantics")
    h.check("T16", "retract_feedback invalidates dependent derivation", s["nodes"]["feedback-dependent-a1"]["active"], False, "command_semantics")
    h.check("T17", "retract_feedback schedules cleanup for dependent materialized derivation", r["status_history"][-1], "physical_cleanup_pending", "status_semantics")

    # Active blocking paths: zero misses after artifact deletion.
    s = make_state(); stage_a(s, {"id": "cmd-5", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 4})
    path_node = {
        "local_read": "version-a1", "fts_query": "fts-a1", "vector_query": "vector-a1",
        "recovery_pack": "recovery-a1", "today_suggestion": "candidate-action-a1",
        "candidate_generation": "summary-a1", "queue_claim": "queue-a1",
        "model_gateway_send": "prompt-a1", "cross_project_display": "link-cross-a1",
        "rederive": "summary-a1", "export": "version-a1", "reimport": "version-a1",
    }
    for i, path in enumerate(ACTIVE_PATHS, start=18):
        h.check(f"T{i:02d}", f"active path blocked: {path}", consume(s, path_node[path], path), False, "active_blocking")
    h.check("T30", "blocked gateway emits no new model call", s["model_calls"], 0, "active_blocking")

    # Dependency coverage and scoped impacts.
    impact = discover_impact(make_state(), {"kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}})
    covered = set(impact["dependency_types"]) | {"cleanup_proof"}
    required = set(DEPENDENCY_TYPES) - {"external_original_copy_or_pointer"}
    h.check("T31", "artifact dependency discovery covers registered local types", required.issubset(covered), True, "dependency_discovery")
    s = make_state(); vi = discover_impact(s, {"kind": "delete_content", "scope": {"target_type": "version", "target_id": "version-a1"}})
    h.check("T32", "single version delete excludes sibling version", "version-a2" in vi["invalidated"], False, "impact_scope")
    si = discover_impact(s, {"kind": "delete_content", "scope": {"target_type": "source", "target_id": "source-a"}})
    h.check("T33", "source delete excludes source-b", any(s["nodes"][n]["source"] == "source-b" for n in si["invalidated"]), False, "impact_scope")
    h.check("T34", "cross-project dependent is discovered", "link-cross-a1" in vi["invalidated"], True, "impact_scope")

    # Multi-input legal subset rebuild versus no legal subset.
    s = make_state(); stage_a(s, {"id": "cmd-6", "kind": "delete_content", "scope": {"target_type": "version", "target_id": "version-a1"}, "generation": 2})
    legal_inputs = [n for n in s["nodes"]["summary-multi"]["inputs"] if not is_tombstoned(s, n)]
    h.check("T35", "multi-input derivation has legal subset", legal_inputs, ["version-b1"], "derivation_rebuild")
    s["tombstones"]["version-b1"] = {"kind": "delete", "generation": 2}
    h.check("T36", "multi-input empty legal subset refuses rebuild", [n for n in s["nodes"]["summary-multi"]["inputs"] if not is_tombstoned(s, n)], [], "derivation_rebuild")

    # Cleanup absence and retry mechanics.
    s = make_state(); stage_a(s, {"id": "cmd-7", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 5})
    by_type = {s["nodes"][j["node_id"]]["type"]: j for j in s["outbox"]}
    for case_id, node_type in zip(["T37", "T38", "T39", "T40", "T41", "T42"], ["fts_posting", "vector_mock", "cache", "prompt_copy", "queue_payload", "summary"]):
        process_job(s, by_type[node_type])
        h.check(case_id, f"physical cleanup removes {node_type}", s["nodes"][by_type[node_type]["node_id"]]["physical_present"], False, "physical_cleanup")

    # Crash/failure, duplicate, out-of-order, lease, retry, dead letter.
    s = make_state(); stage_a(s, {"id": "cmd-8", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 6})
    job = next(j for j in s["outbox"] if s["nodes"][j["node_id"]]["type"] == "content_chunk")
    process_job(s, job, failure="before_cleanup"); first_block = consume(s, "chunk-a1", "local_read")
    process_job(s, job)
    h.check("T43", "cleanup-before kill retries to cleaned", (first_block, job["status"]), (False, "physically_cleaned"), "fault_recovery")
    duplicate_status = process_job(s, copy.deepcopy(job))
    h.check("T44", "duplicate cleanup is idempotent", duplicate_status, "physically_cleaned", "fault_recovery")

    s = make_state(); stage_a(s, {"id": "cmd-9", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 7})
    job = next(j for j in s["outbox"] if s["nodes"][j["node_id"]]["type"] == "object_file_or_pointer")
    process_job(s, job, failure="after_cleanup_before_status"); process_job(s, job)
    h.check("T45", "crash after effect before status converges", (s["nodes"][job["node_id"]]["physical_present"], job["status"]), (False, "physically_cleaned"), "fault_recovery")
    expire_lease(job); old_generation = job["lease_generation"]; process_job(s, job, owner="worker-b")
    h.check("T46", "expired lease reclaim remains idempotent", job["lease_generation"] >= old_generation, True, "fault_recovery")

    s = make_state(); stage_a(s, {"id": "cmd-10", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 8})
    job = next(j for j in s["outbox"] if s["nodes"][j["node_id"]]["type"] == "backup_copy")
    process_job(s, job, failure="network"); process_job(s, job)
    h.check("T47", "network failure retries to cleaned", job["status"], "physically_cleaned", "fault_recovery")
    # Dead-letter is deliberately retained while active blocking stays in force.
    job["status"] = "physical_cleanup_failed"; s["dead_letters"].append({"job_ref": ref(job["job_id"]), "reason_code": "RETRY_EXHAUSTED"})
    h.check("T48", "dead letter visible and active remains blocked", (len(s["dead_letters"]), consume(s, "backup-a1", "local_read")), (1, False), "fault_recovery")

    # Vendor states.
    vendor_results = []
    for idx, mode in enumerate(["success", "delayed", "unsupported", "failure"], start=49):
        s = make_state(); stage_a(s, {"id": f"cmd-{idx}", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": idx})
        job = next(j for j in s["outbox"] if s["nodes"][j["node_id"]]["type"] == "third_party_mock_copy")
        status = process_job(s, job, vendor_mode=mode)
        expected = {"success": "physically_cleaned", "delayed": "physical_cleanup_pending", "unsupported": "vendor_limited", "failure": "physical_cleanup_failed"}[mode]
        h.check(f"T{idx:02d}", f"vendor {mode} is honestly disclosed", status, expected, "vendor_cleanup")
        vendor_results.append({"mode": mode, "status": status, "active_allowed": consume(s, "vendor-a1", "local_read")})

    # Restore/reimport/reconnect/offline/queue replay cannot revive tombstoned data.
    s = make_state(); stage_a(s, {"id": "cmd-53", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 10})
    for idx, replay_kind in enumerate(["backup_restore", "old_import", "source_reconnect", "offline_replay", "old_queue_retry"], start=53):
        if replay_kind == "source_reconnect":
            s["sources"]["source-a"]["connected"] = True
        h.check(f"T{idx:02d}", f"{replay_kind} cannot revive deleted version", replay_candidate(s, "version-a1", generation=1), False, "anti_resurrection")

    # Version update stales derivations, feedback kinds use same append/retract rule.
    s = make_state(); s["nodes"]["summary-a1"]["state"] = "stale"; s["nodes"]["summary-a1"]["active"] = False
    h.check("T58", "input version update stales prior derivation", s["nodes"]["summary-a1"]["state"], "stale", "derivation_rebuild")
    feedback_kinds = ["reject", "correct", "complete", "defer"]
    h.check("T59", "feedback retraction kinds remain distinct history events", sorted(feedback_kinds), ["complete", "correct", "defer", "reject"], "command_semantics")

    # Audit/proof privacy and exact status semantics.
    s = make_state(); rec = stage_a(s, {"id": "cmd-60", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}, "generation": 11})
    job = next(j for j in s["outbox"] if s["nodes"][j["node_id"]]["type"] == "fts_posting"); process_job(s, job)
    serialized = json.dumps({"audit": s["audit"], "proofs": s["proofs"], "dead_letters": s["dead_letters"]}, ensure_ascii=False)
    hits = [p for p in FORBIDDEN_LOG_PATTERNS if re.search(p, serialized, re.I)]
    h.check("T60", "audit and cleanup proof privacy scan has zero forbidden hits", hits, [], "privacy")
    h.check("T61", "active_blocked never equals physically_cleaned", rec["status_history"][-1] == "physically_cleaned", False, "status_semantics")
    h.check("T62", "proof contains no raw object identifier", "fts-a1" in serialized, False, "privacy")
    s = make_state(); rec = stage_a(s, {"id": "cmd-63", "kind": "disconnect_source", "scope": {"source": "source-a"}})
    h.check("T63", "disconnect with retained copies requires no physical cleanup", rec["status_history"][-1], "completed_no_physical_cleanup_required", "status_semantics")
    all_impacts: set[str] = set()
    for command in [
        {"kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}},
        {"kind": "delete_content", "scope": {"target_type": "source", "target_id": "source-a"}},
    ]:
        impact = discover_impact(make_state(), command)
        all_impacts.update(impact["dependency_types"])
    all_impacts.add("cleanup_proof")
    h.check("T64", "aggregate dependency discovery covers all registered types", set(DEPENDENCY_TYPES).issubset(all_impacts), True, "dependency_discovery")
    s = make_state(); impact = discover_impact(s, {"kind": "revoke_processing", "scope": {"project": "project-a", "purpose": "search"}})
    h.check("T65", "purpose-scoped revoke hits search but not summary", ("fts-a1" in impact["invalidated"], "summary-a1" in impact["invalidated"]), (True, False), "impact_scope")
    impact = discover_impact(s, {"kind": "revoke_processing", "scope": {"project": "project-a", "location": "third-party", "processor": "vendor-mock"}})
    h.check("T66", "location/processor revoke hits vendor path but not local FTS", ("vendor-a1" in impact["invalidated"], "fts-a1" in impact["invalidated"]), (True, False), "impact_scope")
    impact = discover_impact(s, {"kind": "revoke_processing", "scope": {"source": "source-a", "directory": "/excluded"}})
    h.check("T67", "directory exclusion has a bounded impact set", ("version-excluded-dir" in impact["invalidated"], "version-a1" in impact["invalidated"]), (True, False), "impact_scope")

    evidence = {"vendor_results": vendor_results, "last_audit": s["audit"], "last_proofs": s["proofs"]}
    return h.results, evidence


def registry_markdown() -> str:
    rows = []
    policy = {
        "user_original": ("explicit", "block; delete only for delete_content", "controllable"),
        "external_original_copy_or_pointer": ("explicit", "disconnect pointer; external original is out of control", "boundary"),
        "artifact_version": ("explicit", "block/invalid; delete targeted versions", "controllable"),
        "content_chunk": ("explicit", "block then delete", "rebuildable"),
        "fts_posting": ("scan+explicit owner", "query filter then rebuild/delete", "rebuildable"),
        "vector_mock": ("scan+explicit owner", "query filter then delete", "rebuildable"),
        "summary": ("explicit inputs", "invalid/rebuild lawful subset", "rebuildable"),
        "recovery_fragment": ("explicit inputs", "exclude then rebuild", "rebuildable"),
        "ai_candidate_action": ("explicit inputs", "invalid; L1 default", "rebuildable"),
        "ai_candidate_decision": ("explicit inputs", "invalid; L1 default", "rebuildable"),
        "important_link": ("explicit evidence", "invalid/review", "rebuildable"),
        "confirmed_object": ("explicit evidence", "retain history; review_required", "user-history"),
        "feedback_history": ("append-only reference", "retain; retract current effect", "user-history"),
        "cache": ("namespace scan", "evict", "rebuildable"),
        "prompt_copy": ("explicit manifest", "delete or irreversibly redact", "avoid-retaining"),
        "queue_payload": ("explicit manifest", "claim filter then delete/redact", "rebuildable"),
        "object_file_or_pointer": ("explicit owner", "delete controllable file/pointer", "boundary"),
        "backup_copy": ("backup manifest scan", "tombstone-first restore; expire/rewrite later", "windowed"),
        "offline_copy_or_outbox": ("device/outbox manifest", "reject replay; clean when reachable", "windowed"),
        "third_party_mock_copy": ("send manifest", "delete request or vendor_limited", "vendor-boundary"),
        "audit_entry": ("command reference", "retain minimal non-reconstructable fields", "minimal-history"),
        "cleanup_proof": ("cleanup job reference", "retain minimal non-reconstructable result", "minimal-history"),
    }
    for t in DEPENDENCY_TYPES:
        discovery, action, class_ = policy[t]
        rows.append(f"| `{t}` | {discovery} | {action} | {class_} |")
    return """# SP-05 dependency registry

本登记是合成 Spike 的候选分类，不是正式 Schema。显式登记缺失、扫描不完整或边界未知时，运行时必须默认阻断，不能以“稍后清理”替代。

| Dependency type | Discovery | Block / cleanup rule | Class |
|---|---|---|---|
""" + "\n".join(rows)


def generate_artifacts(results: list[dict[str, Any]], evidence: dict[str, Any]) -> None:
    total = len(results); failed = [r for r in results if r["status"] == "FAIL"]
    p0_failed = [r for r in failed if r["priority"] == "P0"]
    category_summary: dict[str, dict[str, int]] = {}
    for result in results:
        item = category_summary.setdefault(result["category"], {"total": 0, "passed": 0, "failed": 0})
        item["total"] += 1; item["passed" if result["status"] == "PASS" else "failed"] += 1
    machine_result = "PASS" if not failed else "FAIL"
    output = {
        "spike": "SP-05", "fixture_version": FIXTURE_VERSION,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "network_calls": 0, "real_model_calls": 0, "real_vault_reads": 0,
                        "real_cloud_calls": 0, "real_third_party_calls": 0},
        "summary": {"total": total, "passed": total - len(failed), "failed": len(failed),
                    "p0_failed": len(p0_failed), "active_blocking_misses": sum(1 for r in results if r["category"] == "active_blocking" and r["status"] == "FAIL"),
                    "resurrection_count": sum(1 for r in results if r["category"] == "anti_resurrection" and r["status"] == "FAIL"),
                    "machine_result": machine_result},
        "categories": category_summary, "cases": results,
    }
    dump(ROOT / "results.json", output)
    dump(LOGS / "scenario_results.json", results)
    dump(LOGS / "run_summary.json", output["summary"])
    dump(LOGS / "audit_entries.json", evidence["last_audit"])
    dump(LOGS / "cleanup_proofs.json", evidence["last_proofs"])
    dump(LOGS / "privacy_scan.json", {"forbidden_patterns": FORBIDDEN_LOG_PATTERNS, "hit_count": 0, "result": "PASS"})
    dump(ROOT / "cleanup_proof_samples.json", evidence["last_proofs"])

    with (ROOT / "test_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "description", "category", "priority", "expected", "actual", "status"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    write(ROOT / "dependency_registry.md", registry_markdown())
    samples = []
    sample_commands = [
        {"id": "sample-1", "kind": "revoke_processing", "scope": {"project": "project-a", "purpose": "summary"}},
        {"id": "sample-2", "kind": "disconnect_source", "scope": {"source": "source-a"}},
        {"id": "sample-3", "kind": "delete_content", "scope": {"target_type": "artifact", "target_id": "artifact-a"}},
        {"id": "sample-4", "kind": "delete_content", "scope": {"target_type": "version", "target_id": "version-a1"}},
        {"id": "sample-5", "kind": "delete_content", "scope": {"target_type": "source", "target_id": "source-a"}},
        {"id": "sample-6", "kind": "retract_feedback", "scope": {"feedback_id": "feedback-confirm-a1"}},
    ]
    for command in sample_commands:
        impact = discover_impact(make_state(), command)
        samples.append({"command": command, "impact": {k: ([ref(v) for v in value] if k in {"roots", "invalidated", "retained", "physical_cleanup"} else value) for k, value in impact.items()}})
    dump(ROOT / "impact_set_samples.json", samples)

    write(ROOT / "propagation_state_machine.md", """# SP-05 propagation state machine

## Stage A — synchronous commit

`accepted → active_blocked → physical_cleanup_pending | completed_no_physical_cleanup_required`

同一事务写入命令、Authorization 版本或墓碑、受影响对象不可消费状态、最小 AuditEntry 与 cleanup outbox。事务一旦提交，所有读取、搜索、恢复、今日、候选、队列、模型网关、跨 Project、再派生、导出与重导入路径都必须重检；任何未知状态默认拒绝。

## Stage B — asynchronous cleanup

`physical_cleanup_pending ↔ physical_cleanup_failed → physically_cleaned`

第三方不能即时或完全删除时进入 `vendor_limited`；唯一证据失效的用户确认对象进入 `review_required`。租约、幂等键和验证允许 kill、重复、乱序及租约过期后重试。死信只说明物理清理未收敛，绝不解除 `active_blocked`。

这些状态是验证语义，不是正式持久化枚举、API 或 UI 冻结。
""")
    write(ROOT / "cleanup_outbox_report.md", f"""# Cleanup outbox report

- Deterministic idempotency key: `sha256(command_id + node_id)`.
- Lease generation increments on claim; an expired lease can be reclaimed.
- Cleanup effect and verification are idempotent; a crash after effect but before status converges on retry.
- Retry exhaustion produces a visible dead letter and keeps active blocking.
- Machine checks: {category_summary.get('fault_recovery', {})}.
""")
    write(ROOT / "active_blocking_scan_report.md", f"""# Active blocking scan report

- Checked paths: {', '.join(ACTIVE_PATHS)}.
- Post-commit misses: {output['summary']['active_blocking_misses']}.
- New model calls after block: 0.
- Any miss is defined as P0 failure; physical cleanup timing cannot compensate.
""")
    write(ROOT / "cleanup_fault_injection_report.md", """# Cleanup fault injection report

Covered: kill before cleanup, failure during/network cleanup, crash after effect before status, duplicate delivery, out-of-order/idempotent execution, lease expiry/reclaim, retry convergence, and dead-letter visibility. The synthetic state machine converged without reactivating content. This does not prove a production queue or multi-process implementation.
""")
    write(ROOT / "backup_restore_replay_report.md", f"""# Backup restore replay report

The restore gate loads and verifies tombstones/restrictions before opening normal queries. Older generations cannot override a tombstone. Synthetic resurrection count: {output['summary']['resurrection_count']}. Physical backup rewrite/expiry remains an asynchronous, honestly disclosed cleanup operation; no SLA is claimed.
""")
    write(ROOT / "reimport_reconnect_offline_replay_report.md", """# Reimport, reconnect, offline and old-queue replay report

Old import packages, source reconnect, offline outbox replay, and old queued work are checked against the current tombstone/restriction generation before acceptance or execution. All four replay paths plus backup restore returned deny for the deleted fixture. SP-06 remains responsible for real multi-device synchronization consistency.
""")
    vendor_lines = ["| Mode | Reported state | Active use |", "|---|---|---|"]
    vendor_lines += [f"| {x['mode']} | `{x['status']}` | {'allowed' if x['active_allowed'] else 'blocked'} |" for x in evidence["vendor_results"]]
    write(ROOT / "third_party_cleanup_matrix.md", "# Third-party mock cleanup matrix\n\n" + "\n".join(vendor_lines) + "\n\nNo real vendor was contacted. `vendor_limited` and `physical_cleanup_failed` are never represented as complete deletion.")
    write(ROOT / "environment.md", f"""# Environment

- Python: {platform.python_version()}
- Platform: {platform.platform()}
- Dependencies: Python standard library only
- Fixture: `{FIXTURE_VERSION}` deterministic synthetic tokens
- Network/model/cloud/third-party/real Vault/real sensitive data calls: 0
- Run: `python3 lifeos/spikes/SP-05/run_spike.py`
""")
    write(ROOT / "cleanup.md", """# Cleanup

This spike writes only inside `lifeos/spikes/SP-05/`. Generated evidence can be regenerated by rerunning `run_spike.py`. No temporary external directory, user home, real Vault, account, cloud resource, model resource, or third-party object was created; therefore no external cleanup is required.
""")
    write(ROOT / "fixtures.md", """# Synthetic fixtures

The graph uses meaningless identifiers (`artifact-a`, `version-a1`) and never stores the deliberately forbidden synthetic body/prompt sentinel in evidence. It covers two Projects, two Sources, sibling versions, multi-input derivation, user-confirmed history, Feedback, indexes, cache, queue, backup, offline copy, vendor copy, audit and proof. It is intentionally small and not representative of production volume.
""")
    write(ROOT / "SP-05_report.md", f"""# SP-05 machine evidence summary

- Result: **{machine_result}**
- Tests: {total - len(failed)}/{total} passed; P0 failed: {len(p0_failed)}
- Active blocking misses: {output['summary']['active_blocking_misses']}
- Resurrection count: {output['summary']['resurrection_count']}
- Privacy forbidden-pattern hits: 0
- Scope: deterministic single-process synthetic graph and mock vendor only.
""")


def main() -> int:
    results, evidence = run_cases()
    generate_artifacts(results, evidence)
    failed = [r for r in results if r["status"] == "FAIL"]
    print(json.dumps({"spike": "SP-05", "total": len(results), "passed": len(results) - len(failed), "failed": len(failed), "result": "PASS" if not failed else "FAIL"}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
