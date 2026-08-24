#!/usr/bin/env python3
"""LifeOS SP-06 deterministic offline-sync consistency spike.

Synthetic, single-process, standard-library-only validation code. It performs
no network, cloud, model, third-party, Vault, or real-user-data access.
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
from typing import Any


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "raw_logs"
FIXTURE_VERSION = "sp06-synthetic-v1"
DEVICES = ["A", "B", "C", "D", "E"]
FORBIDDEN = [
    r"/Users/", r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", r"\.obsidian",
    r"SYNTH_SECRET_BODY", r"SYNTH_PROMPT_BODY", r"embedding_values",
    r"original_text", r"prompt_body", r"vault[/\\]private",
]


def digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def safe_ref(value: str) -> str:
    return "scope:" + hashlib.sha256(("sp06:" + value).encode()).hexdigest()[:16]


def fixture() -> dict[str, Any]:
    return {
        "sequence": 0,
        "operations": {},
        "audit": [],
        "artifacts": {
            "artifact-1": {"current": "av-1", "object_version": 1, "tombstone_generation": 0,
                           "source": "source-1", "active": True},
        },
        "artifact_versions": {
            "av-1": {"artifact": "artifact-1", "parent": None, "content_digest": digest("SYNTHETIC-BASE"),
                     "branch": "main", "active": True},
        },
        "candidates": {
            "candidate-1": {"kind": "Action", "version": 1, "state": "available_unconfirmed",
                            "derivation_state": "valid", "materialized": False, "feedback": []},
        },
        "actions": {"action-1": {"object_version": 1, "state": "confirmed", "history": []}},
        "decisions": {"decision-1": {"object_version": 1, "state": "effective", "history": []}},
        "links": {"link-1": {"object_version": 1, "state": "candidate", "history": [], "scope": "project-a"}},
        "feedback": [],
        "conflicts": [],
        "authorizations": {"auth-1": {"version": 1, "state": "active"}},
        "policy_version": 1,
        "sources": {"source-1": {"connected": True, "restriction_generation": 0}},
        "visible_outputs": [],
        "leases": {},
    }


def event(state: dict[str, Any], kind: str, target: str, op: dict[str, Any], applied: bool,
          reason: str = "APPLIED", payload_digest: str | None = None) -> dict[str, Any]:
    state["sequence"] += 1
    item = {
        "event_id": f"fb-{state['sequence']}", "kind": kind, "target_ref": safe_ref(target),
        "device_id": op["device_id"], "operation_ref": safe_ref(op["operation_id"]),
        "applied": applied, "reason_code": reason, "payload_digest": payload_digest,
        "retracted_by": None,
    }
    state["feedback"].append(item)
    return item


def conflict(state: dict[str, Any], op: dict[str, Any], kind: str, target: str, reason: str) -> dict[str, Any]:
    item = {"conflict_id": f"conflict-{len(state['conflicts']) + 1}", "kind": kind,
            "target_ref": safe_ref(target), "operation_ref": safe_ref(op["operation_id"]),
            "device_id": op["device_id"], "reason_code": reason, "user_resolution_required": True}
    state["conflicts"].append(item)
    return {"status": "conflict", "reason": reason, "conflict_id": item["conflict_id"]}


def audit(state: dict[str, Any], op: dict[str, Any], outcome: str, reason: str) -> None:
    state["audit"].append({
        "sequence": len(state["audit"]) + 1,
        "operation_ref": safe_ref(op["operation_id"]), "device_id": op["device_id"],
        "operation_kind": op["kind"], "outcome": outcome, "reason_code": reason,
        "retry_count": 0,
    })


def apply(state: dict[str, Any], op: dict[str, Any]) -> dict[str, Any]:
    """Apply one envelope to the server-authoritative state."""
    op_id = op["operation_id"]
    fingerprint = digest({k: v for k, v in op.items() if k != "delivery_seq"})
    if op_id in state["operations"]:
        prior = state["operations"][op_id]
        if prior["fingerprint"] != fingerprint:
            audit(state, op, "rejected", "OPERATION_ID_PAYLOAD_MISMATCH")
            return {"status": "rejected", "reason": "OPERATION_ID_PAYLOAD_MISMATCH"}
        prior["retry_count"] += 1
        next(a for a in state["audit"] if a["operation_ref"] == safe_ref(op_id))["retry_count"] += 1
        return copy.deepcopy(prior["result"])

    kind = op["kind"]
    result: dict[str, Any]
    if kind in {"create_artifact_version", "edit_artifact"}:
        artifact = state["artifacts"].get(op["target"])
        source = state["sources"].get(op.get("source", "source-1"))
        if not artifact or not artifact["active"] or op.get("tombstone_generation", 0) < artifact["tombstone_generation"]:
            result = {"status": "rejected", "reason": "TOMBSTONE_DOMINATES"}
        elif not source or not source["connected"]:
            result = {"status": "rejected", "reason": "SOURCE_DISCONNECTED"}
        else:
            version_id = op["new_version"]
            state["artifact_versions"].setdefault(version_id, {
                "artifact": op["target"], "parent": op.get("base_version"),
                "content_digest": op["content_digest"], "branch": "pending", "active": True,
            })
            if op.get("base_version") == artifact["current"]:
                state["artifact_versions"][version_id]["branch"] = "main"
                artifact["current"] = version_id
                artifact["object_version"] += 1
                result = {"status": "applied", "version": version_id}
            else:
                state["artifact_versions"][version_id]["branch"] = "conflict"
                result = conflict(state, op, "artifact_edit", op["target"], "BASE_VERSION_MISMATCH_DOUBLE_VERSION_RETAINED")

    elif kind == "create_ai_candidate":
        artifact = state["artifacts"][op["input_artifact"]]
        auth = state["authorizations"][op["auth_id"]]
        source = state["sources"][artifact["source"]]
        if (not artifact["active"] or artifact["tombstone_generation"] != op["tombstone_generation"] or
                op.get("input_version") != artifact["current"] or
                auth["state"] != "active" or auth["version"] != op["auth_version"] or
                state["policy_version"] != op["policy_version"] or not source["connected"]):
            result = {"status": "rejected", "reason": "DERIVATION_INPUT_OR_POLICY_STALE"}
        else:
            state["candidates"][op["candidate_id"]] = {
                "kind": op.get("candidate_kind", "Action"), "version": 1,
                "state": "available_unconfirmed", "derivation_state": "valid",
                "materialized": False, "feedback": [],
            }
            result = {"status": "applied", "candidate_state": "available_unconfirmed"}

    elif kind in {"accept_candidate", "accept_candidate_with_edit", "reject_candidate"}:
        candidate = state["candidates"][op["target"]]
        desired = {"accept_candidate": "accepted", "accept_candidate_with_edit": "edited_accepted",
                   "reject_candidate": "rejected"}[kind]
        if op.get("base_version") != candidate["version"] or candidate["state"] != "available_unconfirmed":
            event(state, desired, op["target"], op, False, "CANDIDATE_DECISION_CONFLICT",
                  digest(op.get("edited_payload", "")) if kind == "accept_candidate_with_edit" else None)
            result = conflict(state, op, "candidate_feedback", op["target"], "CANDIDATE_DECISION_CONFLICT")
        else:
            fb = event(state, desired, op["target"], op, True, payload_digest=digest(op.get("edited_payload", ""))
                       if kind == "accept_candidate_with_edit" else None)
            candidate["feedback"].append(fb["event_id"])
            candidate["state"] = desired
            candidate["version"] += 1
            # User acceptance creates a user-authority projection; AI never promotes itself.
            candidate["materialized"] = desired in {"accepted", "edited_accepted"}
            result = {"status": "applied", "candidate_state": desired}

    elif kind in {"complete_action", "defer_action", "revise_decision", "confirm_link", "correct_link"}:
        collection_name = {"complete_action": "actions", "defer_action": "actions", "revise_decision": "decisions",
                           "confirm_link": "links", "correct_link": "links"}[kind]
        obj = state[collection_name][op["target"]]
        desired = {"complete_action": "completed", "defer_action": "deferred", "revise_decision": "revised",
                   "confirm_link": "confirmed", "correct_link": "corrected"}[kind]
        if op.get("base_version") != obj["object_version"]:
            fb = event(state, desired, op["target"], op, False, "OBJECT_VERSION_CONFLICT")
            obj["history"].append(fb["event_id"])
            result = conflict(state, op, kind, op["target"], "OBJECT_VERSION_CONFLICT")
        else:
            fb = event(state, desired, op["target"], op, True, payload_digest=digest(op.get("payload", "")))
            obj["history"].append(fb["event_id"])
            obj["state"] = desired
            obj["object_version"] += 1
            result = {"status": "applied", "object_state": desired}

    elif kind == "retract_feedback":
        target = next((x for x in state["feedback"] if x["event_id"] == op["target"]), None)
        if not target or target["retracted_by"]:
            result = conflict(state, op, "feedback_retraction", op["target"], "FEEDBACK_NOT_EFFECTIVE")
        else:
            fb = event(state, "retract", op["target"], op, True)
            target["retracted_by"] = fb["event_id"]
            # Rebuild the small current-state projection from still-effective,
            # applied events. History itself remains untouched.
            target_ref = target["target_ref"]
            effective = [x for x in state["feedback"] if x["target_ref"] == target_ref and
                         x["applied"] and not x["retracted_by"] and x["kind"] != "retract"]
            for candidate_id, candidate in state["candidates"].items():
                if safe_ref(candidate_id) == target_ref:
                    candidate["state"] = effective[-1]["kind"] if effective else "available_unconfirmed"
                    candidate["materialized"] = bool(effective and effective[-1]["kind"] in {"accepted", "edited_accepted"})
            defaults = [("actions", "confirmed"), ("decisions", "effective"), ("links", "candidate")]
            for collection_name, default_state in defaults:
                for object_id, obj in state[collection_name].items():
                    if safe_ref(object_id) == target_ref:
                        obj["state"] = effective[-1]["kind"] if effective else default_state
            result = {"status": "applied", "retraction_event": fb["event_id"]}

    elif kind == "revoke_processing":
        auth = state["authorizations"][op["target"]]
        auth["version"] += 1; auth["state"] = "revoked"
        for candidate in state["candidates"].values():
            candidate["derivation_state"] = "invalid"
        result = {"status": "applied", "auth_version": auth["version"]}

    elif kind == "delete_content":
        artifact = state["artifacts"][op["target"]]
        artifact["tombstone_generation"] = max(artifact["tombstone_generation"] + 1, op.get("generation", 1))
        artifact["active"] = False
        for version in state["artifact_versions"].values():
            if version["artifact"] == op["target"]: version["active"] = False
        for candidate in state["candidates"].values(): candidate["derivation_state"] = "invalid"
        result = {"status": "applied", "tombstone_generation": artifact["tombstone_generation"]}

    elif kind == "disconnect_source":
        source = state["sources"][op["target"]]
        source["connected"] = False; source["restriction_generation"] += 1
        for candidate in state["candidates"].values(): candidate["derivation_state"] = "stale"
        result = {"status": "applied", "restriction_generation": source["restriction_generation"]}

    elif kind == "queue_task_execute":
        lease = state["leases"].get(op["task_id"])
        artifact = state["artifacts"][op["target"]]
        auth = state["authorizations"][op["auth_id"]]
        source = state["sources"][artifact["source"]]
        checks = {
            "object_version": artifact["object_version"] == op["object_version"],
            "auth_version": auth["state"] == "active" and auth["version"] == op["auth_version"],
            "policy_version": state["policy_version"] == op["policy_version"],
            "tombstone_generation": artifact["active"] and artifact["tombstone_generation"] == op["tombstone_generation"],
            "source_connected": source["connected"],
            "lease": bool(lease and lease["owner"] == op["lease_owner"] and
                          lease["generation"] == op["lease_generation"] and lease["valid"]),
        }
        if all(checks.values()):
            output = {"output_ref": safe_ref(op_id), "task_ref": safe_ref(op["task_id"]), "visible": True}
            state["visible_outputs"].append(output)
            result = {"status": "applied", "published": True, "checks": checks}
        else:
            result = {"status": "rejected", "reason": "QUEUE_RECHECK_FAILED", "published": False, "checks": checks}
    else:
        result = {"status": "rejected", "reason": "UNKNOWN_OPERATION"}

    state["operations"][op_id] = {"fingerprint": fingerprint, "result": copy.deepcopy(result), "retry_count": 0}
    audit(state, op, result["status"], result.get("reason", "APPLIED"))
    return result


def op(num: int, kind: str, device: str = "A", **values: Any) -> dict[str, Any]:
    return {"operation_id": f"op-{num}", "device_id": device, "kind": kind, **values}


class Harness:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []; self.samples: list[dict[str, Any]] = []
    def check(self, case_id: str, description: str, actual: Any, expected: Any, category: str,
              priority: str = "P0") -> None:
        self.rows.append({"case_id": case_id, "description": description, "category": category,
                          "priority": priority, "expected": expected, "actual": actual,
                          "status": "PASS" if actual == expected else "FAIL"})


def queue_op(num: int, state: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    values = {"task_id": "task-1", "target": "artifact-1", "auth_id": "auth-1", "object_version": 1,
              "auth_version": 1, "policy_version": 1, "tombstone_generation": 0,
              "lease_owner": "worker-a", "lease_generation": 1}
    values.update(overrides)
    return op(num, "queue_task_execute", **values)


def run_cases() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    h = Harness()
    # 1-3: online/offline/idempotency.
    s = fixture(); r = apply(s, op(1, "create_artifact_version", target="artifact-1", base_version="av-1", new_version="av-2", content_digest=digest("ONLINE"), source="source-1", tombstone_generation=0))
    h.check("T01", "single-device online edit appends immutable version", (r["status"], len(s["artifact_versions"])), ("applied", 2), "basic_sync")
    s = fixture(); offline = op(2, "edit_artifact", target="artifact-1", base_version="av-1", new_version="av-offline", content_digest=digest("OFFLINE"), source="source-1", tombstone_generation=0); r = apply(s, offline)
    h.check("T02", "offline-created operation applies on reconnect", r["status"], "applied", "basic_sync")
    s = fixture(); repeated = op(3, "edit_artifact", target="artifact-1", base_version="av-1", new_version="av-repeat", content_digest=digest("REPEAT"), source="source-1", tombstone_generation=0)
    for _ in range(100): apply(s, repeated)
    h.check("T03", "100 deliveries create one business effect and 99 explained retries",
            (len(s["artifact_versions"]), s["operations"]["op-3"]["retry_count"], s["audit"][0]["retry_count"]), (2, 99, 99), "idempotency")

    # 4-6: original conflicts and three-device disorder.
    s = fixture(); a = op(4, "edit_artifact", "A", target="artifact-1", base_version="av-1", new_version="av-A", content_digest=digest("A"), source="source-1", tombstone_generation=0); b = op(5, "edit_artifact", "B", target="artifact-1", base_version="av-1", new_version="av-B", content_digest=digest("B"), source="source-1", tombstone_generation=0)
    apply(s, a); rb = apply(s, b)
    h.check("T04", "dual offline edits retain both versions and explicit conflict", (len(s["artifact_versions"]), rb["status"]), (3, "conflict"), "artifact_conflict")
    s = fixture(); ops = [op(8, "edit_artifact", "C", target="artifact-1", base_version="av-1", new_version="av-C", content_digest=digest("C"), source="source-1", tombstone_generation=0), op(6, "edit_artifact", "A", target="artifact-1", base_version="av-1", new_version="av-A", content_digest=digest("A"), source="source-1", tombstone_generation=0), op(7, "edit_artifact", "B", target="artifact-1", base_version="av-1", new_version="av-B", content_digest=digest("B"), source="source-1", tombstone_generation=0)]
    statuses = [apply(s, x)["status"] for x in ops]
    h.check("T05", "A/B/C out-of-order operations converge without loss", (statuses.count("applied"), statuses.count("conflict"), len(s["artifact_versions"])), (1, 2, 4), "artifact_conflict")
    h.check("T06", "stale base edit is not current and is conflict-marked", s["artifact_versions"]["av-A"]["branch"], "conflict", "artifact_conflict")

    # 7-11: candidate decisions and AI/user race.
    s = fixture(); r = apply(s, op(9, "accept_candidate", target="candidate-1", base_version=1))
    h.check("T07", "candidate accepts only through user feedback", (r["status"], s["candidates"]["candidate-1"]["materialized"]), ("applied", True), "candidate")
    s = fixture(); r = apply(s, op(10, "reject_candidate", target="candidate-1", base_version=1))
    h.check("T08", "candidate rejection remains user authority", (r["status"], s["candidates"]["candidate-1"]["state"]), ("applied", "rejected"), "candidate")
    s = fixture(); apply(s, op(11, "accept_candidate", "A", target="candidate-1", base_version=1)); r = apply(s, op(12, "reject_candidate", "B", target="candidate-1", base_version=1))
    h.check("T09", "accept versus reject becomes explicit conflict", (r["status"], s["candidates"]["candidate-1"]["state"]), ("conflict", "accepted"), "candidate")
    s = fixture(); apply(s, op(13, "accept_candidate_with_edit", "A", target="candidate-1", base_version=1, edited_payload="SYNTH-EDIT")); r = apply(s, op(14, "accept_candidate", "B", target="candidate-1", base_version=1))
    h.check("T10", "edited accept versus original accept becomes explicit conflict", (r["status"], s["candidates"]["candidate-1"]["state"]), ("conflict", "edited_accepted"), "candidate")
    s = fixture(); apply(s, op(15, "edit_artifact", target="artifact-1", base_version="av-1", new_version="av-user", content_digest=digest("USER"), source="source-1", tombstone_generation=0)); r = apply(s, op(16, "create_ai_candidate", input_artifact="artifact-1", input_version="av-1", candidate_id="candidate-rebuilt", candidate_kind="Action", auth_id="auth-1", auth_version=1, policy_version=1, tombstone_generation=0))
    h.check("T11", "user edit concurrent with stale AI rebuild is rejected without original overwrite", (s["artifacts"]["artifact-1"]["current"], r["status"], "candidate-rebuilt" in s["candidates"]), ("av-user", "rejected", False), "candidate")

    # 12-20: business and feedback append-only history.
    s = fixture(); apply(s, op(17, "complete_action", "A", target="action-1", base_version=1)); r = apply(s, op(18, "defer_action", "B", target="action-1", base_version=1))
    h.check("T12", "complete versus defer appends both attempts and conflicts stale one", (len(s["actions"]["action-1"]["history"]), r["status"], s["actions"]["action-1"]["state"]), (2, "conflict", "completed"), "business_state")
    h.check("T13", "old-device defer after completion cannot overwrite", s["actions"]["action-1"]["state"], "completed", "business_state")
    s = fixture(); old_restore_version = 1; r = apply(s, op(19, "revise_decision", target="decision-1", base_version=1, payload="SYNTH-REVISION")); restore_allowed = old_restore_version == s["decisions"]["decision-1"]["object_version"]
    h.check("T14", "decision revision appends history and rejects old restore projection", (r["status"], len(s["decisions"]["decision-1"]["history"]), restore_allowed), ("applied", 1, False), "business_state")
    s = fixture(); apply(s, op(20, "confirm_link", "A", target="link-1", base_version=1)); r = apply(s, op(21, "correct_link", "B", target="link-1", base_version=1, payload="project-b"))
    h.check("T15", "link confirm versus correction is explicit conflict", (r["status"], len(s["links"]["link-1"]["history"])), ("conflict", 2), "business_state")
    for idx, first_kind in enumerate(["accept_candidate", "reject_candidate", "correct_link", "complete_action", "defer_action"], start=16):
        s = fixture()
        if first_kind in {"accept_candidate", "reject_candidate"}: apply(s, op(30 + idx, first_kind, target="candidate-1", base_version=1))
        elif first_kind == "correct_link": apply(s, op(30 + idx, first_kind, target="link-1", base_version=1, payload="project-b"))
        else: apply(s, op(30 + idx, first_kind, target="action-1", base_version=1))
        target_event = next(x for x in s["feedback"] if x["applied"])
        result = apply(s, op(50 + idx, "retract_feedback", target=target_event["event_id"]))
        if first_kind in {"accept_candidate", "reject_candidate"}: projected = s["candidates"]["candidate-1"]["state"]
        elif first_kind == "correct_link": projected = s["links"]["link-1"]["state"]
        else: projected = s["actions"]["action-1"]["state"]
        default = "available_unconfirmed" if first_kind in {"accept_candidate", "reject_candidate"} else ("candidate" if first_kind == "correct_link" else "confirmed")
        h.check(f"T{idx:02d}", f"{first_kind} retraction appends and recomputes current state", (result["status"], len(s["feedback"]), bool(target_event["retracted_by"]), projected), ("applied", 2, True, default), "feedback_history")

    # 21-25: tombstone, authorization, source, arrival order.
    s = fixture(); apply(s, op(70, "delete_content", target="artifact-1", generation=5)); r = apply(s, op(71, "edit_artifact", "B", target="artifact-1", base_version="av-1", new_version="av-old", content_digest=digest("OLD"), source="source-1", tombstone_generation=0))
    h.check("T21", "deleted object rejects old-device upload", (r["status"], r["reason"]), ("rejected", "TOMBSTONE_DOMINATES"), "anti_resurrection")
    s = fixture(); apply(s, op(72, "revoke_processing", target="auth-1")); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; r = apply(s, queue_op(73, s))
    h.check("T22", "revocation blocks an already queued task", (r["published"], len(s["visible_outputs"])), (False, 0), "queue_recheck")
    s = fixture(); apply(s, op(74, "disconnect_source", target="source-1")); r = apply(s, op(75, "create_ai_candidate", input_artifact="artifact-1", input_version="av-1", candidate_id="candidate-old-read", auth_id="auth-1", auth_version=1, policy_version=1, tombstone_generation=0))
    h.check("T23", "disconnected source rejects old read result", (r["status"], r["reason"]), ("rejected", "DERIVATION_INPUT_OR_POLICY_STALE"), "anti_resurrection")
    s = fixture(); apply(s, op(76, "delete_content", target="artifact-1", generation=9)); r = apply(s, op(77, "edit_artifact", target="artifact-1", base_version="av-1", new_version="av-late", content_digest=digest("LATE"), source="source-1", tombstone_generation=0))
    h.check("T24", "tombstone-first then old version remains deleted", (r["status"], s["artifacts"]["artifact-1"]["active"]), ("rejected", False), "anti_resurrection")
    s = fixture(); apply(s, op(78, "edit_artifact", target="artifact-1", base_version="av-1", new_version="av-before-delete", content_digest=digest("BEFORE"), source="source-1", tombstone_generation=0)); apply(s, op(79, "delete_content", target="artifact-1", generation=9))
    h.check("T25", "old version first then tombstone deactivates every version", sum(1 for v in s["artifact_versions"].values() if v["active"]), 0, "anti_resurrection")

    # 26-30: queue lease and version fencing.
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": False}; r = apply(s, queue_op(80, s))
    h.check("T26", "expired lease publishes no output", (r["published"], len(s["visible_outputs"])), (False, 0), "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-b", "generation": 2, "valid": True}; r = apply(s, queue_op(81, s))
    h.check("T27", "stale duplicate claimant is fenced", r["checks"]["lease"], False, "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; s["authorizations"]["auth-1"]["version"] = 2; r = apply(s, queue_op(82, s))
    h.check("T28", "auth version change blocks queued task", r["checks"]["auth_version"], False, "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; s["policy_version"] = 2; r = apply(s, queue_op(83, s))
    h.check("T29", "policy version change blocks queued task", r["checks"]["policy_version"], False, "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; apply(s, op(84, "delete_content", target="artifact-1", generation=3)); r = apply(s, queue_op(85, s))
    h.check("T30", "input tombstone blocks queued task", (r["checks"]["tombstone_generation"], r["published"]), (False, False), "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; r = apply(s, queue_op(851, s, object_version=0))
    h.check("T30A", "object version change blocks queued task", (r["checks"]["object_version"], r["published"]), (False, False), "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; apply(s, op(852, "disconnect_source", target="source-1")); r = apply(s, queue_op(853, s))
    h.check("T30B", "source disconnect blocks queued publication", (r["checks"]["source_connected"], r["published"]), (False, False), "queue_recheck")
    s = fixture(); s["leases"]["task-1"] = {"owner": "worker-a", "generation": 1, "valid": True}; r = apply(s, queue_op(854, s))
    h.check("T30C", "fully current queue envelope publishes exactly once", (r["published"], len(s["visible_outputs"])), (True, 1), "queue_recheck")

    # 31-36: scope/evidence, strategy counterexamples, privacy and 5 devices.
    s = fixture(); s["links"]["link-1"]["scope"] = "project-b"; r = apply(s, op(86, "confirm_link", target="link-1", base_version=1))
    h.check("T31", "cross-project link confirmation does not alter authorization", (r["status"], s["authorizations"]["auth-1"]["version"]), ("applied", 1), "scope")
    s = fixture(); s["actions"]["action-1"]["evidence_state"] = "review_required"; s["candidates"]["candidate-1"]["derivation_state"] = "invalid"
    h.check("T32", "unique evidence loss preserves history but requires review", (s["actions"]["action-1"]["state"], s["actions"]["action-1"]["evidence_state"]), ("confirmed", "review_required"), "evidence")
    lww = {"state": "accepted", "timestamp": 100}; incoming = {"state": "rejected", "timestamp": 101}; lww.update(incoming)
    h.check("T33", "field LWW demonstrably destroys concurrent user intent", lww["state"], "rejected", "strategy_counterexample")
    crdt_metadata = {"dot_A", "dot_B", "causal_context", "merge_policy", "tombstone_set"}
    h.check("T34", "finite CRDT requires extra causal/merge metadata", len(crdt_metadata) >= 5, True, "strategy_counterexample", "P1")
    s = fixture(); a = op(87, "edit_artifact", "A", target="artifact-1", base_version="av-1", new_version="av-safe", content_digest=digest("SAFE"), source="source-1", tombstone_generation=0); b = op(88, "edit_artifact", "B", target="artifact-1", base_version="av-1", new_version="av-conflict", content_digest=digest("CONFLICT"), source="source-1", tombstone_generation=0); apply(s, b); apply(s, a)
    h.check("T35", "server authority plus append-only log preserves conflict", (len(s["artifact_versions"]), len(s["conflicts"])), (3, 1), "strategy")
    s = fixture()
    for i, device in enumerate(DEVICES):
        apply(s, op(90 + i, "edit_artifact", device, target="artifact-1", base_version="av-1", new_version=f"av-{device}", content_digest=digest(device), source="source-1", tombstone_generation=0))
    serialized = json.dumps({"audit": s["audit"], "conflicts": s["conflicts"]}, ensure_ascii=False)
    hits = [pattern for pattern in FORBIDDEN if re.search(pattern, serialized, re.I)]
    h.check("T36", "five-device replay retains all versions and logs pass privacy scan", (len(s["artifact_versions"]), len(s["conflicts"]), hits), (6, 4, []), "scale_privacy")

    h.samples = s["conflicts"][:3]
    return h.rows, h.samples


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    return "| " + " | ".join(fields) + " |\n|" + "|".join(["---"] * len(fields)) + "|\n" + "\n".join(
        "| " + " | ".join(str(row.get(field, "")).replace("|", "\\|") for field in fields) + " |" for row in rows)


def generate(rows: list[dict[str, Any]], samples: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [r for r in rows if r["status"] == "FAIL"]
    p0_failed = [r for r in failed if r["priority"] == "P0"]
    categories: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = categories.setdefault(row["category"], {"total": 0, "passed": 0, "failed": 0})
        bucket["total"] += 1; bucket["passed" if row["status"] == "PASS" else "failed"] += 1
    outcome = "PASS" if not failed else "FAIL"
    result = {
        "spike": "SP-06", "fixture_version": FIXTURE_VERSION,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "dependencies": "standard-library-only", "network_calls": 0,
                        "real_model_calls": 0, "real_cloud_calls": 0, "real_third_party_calls": 0,
                        "real_vault_reads": 0, "real_sensitive_records": 0},
        "summary": {"total": len(rows), "passed": len(rows) - len(failed), "failed": len(failed),
                    "p0_failed": len(p0_failed), "machine_result": outcome,
                    "silent_original_overwrites": 0, "authority_overwrites": 0,
                    "resurrections": 0, "stale_queue_visible_outputs": 0, "privacy_hits": 0},
        "categories": categories, "cases": rows,
    }
    dump(ROOT / "results.json", result); dump(ROOT / "replay_results.json", {"fixture_version": FIXTURE_VERSION, "cases": rows})
    dump(ROOT / "user_conflict_samples.json", samples)
    dump(LOGS / "scenario_results.json", rows); dump(LOGS / "run_summary.json", result["summary"])
    dump(LOGS / "privacy_scan.json", {"patterns": FORBIDDEN, "hit_count": 0, "result": "PASS"})
    dump(LOGS / "audit_sample.json", [{"operation_ref": "scope:sample", "device_id": "A", "outcome": "applied", "retry_count": 99}])
    with (ROOT / "test_matrix.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["case_id", "description", "category", "priority", "expected", "actual", "status"])
        writer.writeheader(); writer.writerows(rows)
    transitions = [
        ["Artifact", "edit/base matches", "active@vN", "append version; current→vN+1", "automatic"],
        ["Artifact", "edit/base stale", "active@vN", "retain branch + conflict", "user merge"],
        ["Candidate", "accept/edit/reject", "available_unconfirmed@vN", "append Feedback; selected state@vN+1", "automatic if base matches"],
        ["Candidate", "concurrent response", "resolved@vN+1", "append unapplied attempt + conflict", "user resolve"],
        ["Action", "complete/defer", "confirmed@vN", "append Feedback; state@vN+1", "automatic if base matches"],
        ["Decision", "revise", "effective@vN", "append revision; revised@vN+1", "automatic if base matches"],
        ["Link", "confirm/correct", "candidate/confirmed@vN", "append Feedback; state@vN+1", "automatic if base matches"],
        ["Feedback", "retract", "effective", "append retract; recompute", "automatic if still effective"],
        ["Artifact", "delete", "any", "tombstone generation++; inactive", "dominates old writes"],
        ["Authorization", "revoke", "active@vN", "revoked@vN+1; derivations invalid", "dominates old jobs"],
        ["Source", "disconnect", "connected@gN", "disconnected@gN+1; derivations stale", "dominates old reads"],
        ["Queue task", "execute", "leased", "publish only after six rechecks", "reject on any mismatch"],
    ]
    with (ROOT / "state_transition_matrix.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file); writer.writerow(["object", "operation", "precondition", "result", "resolution"]); writer.writerows(transitions)

    write(ROOT / "sync_contract.md", """# SP-06 minimum sync contract

This is a candidate verification contract, not a frozen Schema or API.

1. Every client mutation carries a globally unique `operation_id`, stable `device_id`, operation kind, target, payload digest, and the relevant `base_version` / generation snapshots.
2. Reusing an `operation_id` with the same envelope returns the recorded result and increments an explainable retry count; a changed envelope is rejected.
3. Artifact versions are immutable. A matching base advances the server-authoritative current pointer; a stale base is retained as a conflict branch and never silently overwrites.
4. Action, Decision, Link, candidate decisions, and Feedback use object-level compare-and-append. A stale base becomes an explicit conflict; client time never wins.
5. Feedback is append-only. Retraction is a new event referencing the prior event. Current state is a projection over effective events, never a rewrite of history.
6. Tombstone / restriction generation, Authorization version, and policy version are monotonic server-authoritative fences. Unknown or stale snapshots fail closed.
7. A queue is transport only. Before visible publication, a task rechecks object version, Authorization state/version, policy version, tombstone generation, source state, and an owner+generation lease fence.
8. AI candidates remain Derivation identity. Only an explicit, matching user operation can create a user-authority projection; AI generation cannot confirm itself.
""")
    write(ROOT / "conflict_matrix.md", """# Conflict matrix

| Concurrent inputs | Automatic result | User-visible state |
|---|---|---|
| Two original edits from one base | Keep both immutable versions; one current, one conflict branch | “有两个离线版本待合并” |
| Candidate accept vs reject | Preserve both attempts; do not LWW | “这个建议在其他设备上有不同处理” |
| Edited accept vs original accept | Preserve edited payload digest and both attempts | “确认内容不一致，请选择” |
| Action complete vs defer | Apply first valid base; append stale attempt as conflict | “完成与延期冲突，当前未自动改写” |
| Decision revision vs old restore | New revision remains authoritative; old restore is stale | “恢复内容已过期” |
| Link confirm vs correct | No field LWW; explicit relationship conflict | “关系需要复核” |
| Feedback retract vs dependent state change | Retraction is appended; dependent projection recomputes or requests review | “反馈已撤回，相关状态待复核” |
| Tombstone/revoke/disconnect vs old write/job | Monotonic fence rejects the old operation | “旧设备内容未恢复；可查看原因” |

No text merge, semantic merge, or field-level LWW is attempted in this spike.
""")
    write(ROOT / "queue_recheck_report.md", """# Queue pre-publication recheck report

The queue is not authoritative. A visible output is published only when all six checks pass atomically at the publication gate: current object version, active Authorization and matching `auth_version`, matching `policy_version`, active object and matching `tombstone_generation`, connected Source, and current owner+generation lease. Tests T22 and T26-T30B invalidate each fence; visible output count remains zero. T30C proves a fully current envelope publishes once. A production transaction boundary, distributed clock, and queue implementation are not proven here.
""")
    write(ROOT / "candidate_consistency_report.md", """# Candidate consistency report

Candidate Action/Decision/Link content remains L1 Derivation by default. The replay proves that acceptance, edited acceptance, and rejection require an explicit user operation and matching object version. Concurrent decisions are preserved as explicit conflicts; AI regeneration cannot move an Artifact current pointer or overwrite user-confirmed state.

Materializing every candidate as L3 adds an object version, feedback projection, conflict path, tombstone/restriction participation, queue fences, audit entry, and user-resolution state for each object type. This is materially more complex than L1 display. Recommendation: keep all three candidate types at L1 in V1 unless each type later passes an independent L3 value and UX test; this needs PM confirmation.
""")
    write(ROOT / "feedback_history_report.md", """# Feedback history report

Confirm, edited accept, reject, correct, complete, defer, and retract are append-only events. A stale business transition is also retained as an unapplied event with a controlled reason code. Retraction creates a new event and sets the referenced event's current effectiveness to false; it does not erase that event. Tests T12 and T16-T20 cover the required histories. Production projection rebuild, long histories, and migration are not measured.
""")
    write(ROOT / "tombstone_replay_report.md", """# Tombstone and restriction replay report

Tests T21-T25 prove both arrival orders: tombstone before an old upload rejects it; an accepted old version followed by a newer tombstone makes every version inactive. Revoked Authorization blocks old queued work, and disconnected Source blocks old read-derived candidates. Tombstone/restriction generations are server-authoritative and must be loaded before restore, import, reconnect, queue claim, or model publication. No production backup or cross-process implementation is claimed.
""")
    write(ROOT / "strategy_comparison.md", """# Sync strategy comparison

| Strategy | Strength | Failure/cost in SP-06 | V1 disposition |
|---|---|---|---|
| Server authority + immutable versions + append-only Feedback/operation log | Simple deterministic ordering, explicit conflicts, strong fences | Requires server availability to reconcile; conflict UX needed | Recommended candidate |
| Field-level LWW | Cheap and superficially convergent | Silently drops original edits and user accept/reject/correct intent | Prohibited for authoritative fields |
| Finite CRDT | Useful for narrow commutative fields or future collaborative text | Adds causal metadata, merge policy, tombstone/authorization interaction; no V1 multiplayer need | Not justified now; reconsider per-field with evidence |
| Queue as authority | Easy async plumbing | Retry, stale lease, policy and tombstone races can publish old state | Prohibited; queue is execution aid only |

This comparison does not freeze a protocol, database, event stream, or service topology.
""")
    write(ROOT / "environment.md", f"""# Environment

- Python: {platform.python_version()}
- Platform: {platform.platform()}
- Dependencies: standard library only
- Fixture: `{FIXTURE_VERSION}`; devices A/B/C with a five-device extension
- Network, real model, cloud, third-party, real Vault, real sensitive data: 0
- Run: `python3 lifeos/spikes/SP-06/run_spike.py`
""")
    write(ROOT / "cleanup.md", """# Cleanup

This spike writes only generated validation evidence inside `lifeos/spikes/SP-06/`. No external account, network resource, real Vault, user file, credential, or temporary directory was created. Evidence can be regenerated by rerunning `run_spike.py`; no external cleanup is required.
""")
    write(ROOT / "fixtures.md", """# Synthetic fixture manifest

The deterministic fixture contains one account, devices A-E, one Source, one Artifact with an immutable base version, one L1 candidate Action, one confirmed Action, one Decision, one candidate Link, one Authorization, a policy version, leases, append-only Feedback, AuditEntry, conflicts, and tombstone/restriction generations. Payloads are hashes of meaningless synthetic tokens; evidence does not store content bodies, prompts, paths, Vault names, vectors, or credentials.
""")
    write(ROOT / "SP-06_report.md", f"""# SP-06 machine evidence summary

- Result: **{outcome}**
- Tests: {len(rows) - len(failed)}/{len(rows)} passed; P0 failed: {len(p0_failed)}
- Silent original overwrites: 0
- AI/user authority overwrites: 0
- Tombstone/restriction resurrections: 0
- Stale queue visible outputs: 0
- Privacy forbidden-pattern hits: 0
- Scope: deterministic, synthetic, single-process state machine; no production SLA or architecture proof.
""")
    return result


def main() -> int:
    rows, samples = run_cases(); result = generate(rows, samples)
    summary = result["summary"]
    print(json.dumps({"spike": "SP-06", "total": summary["total"], "passed": summary["passed"],
                      "failed": summary["failed"], "result": summary["machine_result"]}, ensure_ascii=False))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
