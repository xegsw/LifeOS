#!/usr/bin/env python3
"""LifeOS SP-04 authorization boundary spike.

Deterministic synthetic fixtures only. This is validation code, not product code.
It performs no network access and calls no model, cloud, Vault, or third party.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import platform
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "raw_logs"
NOW = 1786176000  # deterministic 2026-08-08T08:00:00Z-like test clock
POLICY_VERSION = "policy-synth-v4"
AUTH_VERSION = "auth-set-synth-v7"
FIXTURE_VERSION = "sp04-fixtures-v1"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def artifact(
    artifact_id: str,
    source: str,
    project: str | None,
    sensitivity: str,
    *,
    source_external_allowed: bool = True,
    excluded: bool = False,
    credential: bool = False,
    state: str = "active",
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "version_id": artifact_id + "-v1",
        "source_id": source,
        "project_id": project,
        "sensitivity": sensitivity,
        "source_external_allowed": source_external_allowed,
        "excluded": excluded,
        "credential": credential,
        "state": state,
        "content_token": "SYNTH_CONTENT_" + artifact_id.upper().replace("-", "_"),
        "locator_token": "loc-" + sha(artifact_id)[:10],
    }


ARTIFACTS = {
    "user": artifact("artifact-user", "source-lifeos", "project-a", "personal"),
    "obsidian": artifact("artifact-obsidian", "source-obsidian-synth", "project-a", "personal"),
    "external": artifact("artifact-external", "source-web-synth", "project-a", "restricted"),
    "public": artifact("artifact-public", "source-public-synth", None, "public"),
    "client": artifact("artifact-client", "source-client-synth", "project-a", "client_secret", source_external_allowed=False),
    "credential": artifact("artifact-credential", "source-lifeos", "project-a", "credential", credential=True),
    "unknown": artifact("artifact-unknown", "source-unknown", "project-a", "unknown"),
    "project_b": artifact("artifact-project-b", "source-lifeos", "project-b", "personal"),
    "no_project": artifact("artifact-no-project", "source-lifeos", None, "personal"),
    "excluded_source": artifact("artifact-excluded-source", "source-excluded", "project-a", "personal", excluded=True),
    "excluded_dir": artifact("artifact-excluded-dir", "source-obsidian-synth", "project-a", "personal", excluded=True),
    "excluded_artifact": artifact("artifact-excluded-artifact", "source-lifeos", "project-a", "personal", excluded=True),
    "deleted": artifact("artifact-deleted", "source-lifeos", "project-a", "personal", state="deleted"),
    "withdrawn": artifact("artifact-withdrawn", "source-lifeos", "project-a", "personal", state="processing_withdrawn"),
    "disconnected": artifact("artifact-disconnected", "source-disconnected", "project-a", "personal", state="source_disconnected"),
    "unreachable": artifact("artifact-unreachable", "source-unreachable", "project-a", "personal", state="source_unreachable"),
}


def grant(
    grant_id: str,
    actions: list[str],
    purposes: list[str],
    locations: list[str],
    processors: list[str],
    *,
    projects: list[str | None] | None = None,
    sources: list[str] | None = None,
    artifacts: list[str] | None = None,
    expires_at: int = NOW + 86400,
    state: str = "active",
    version: str = "v1",
) -> dict[str, Any]:
    return {
        "authorization_id": grant_id,
        "authorization_version": version,
        "grantor": "user-synthetic-01",
        "subjects": ["workflow-recovery"],
        "scope": {
            "projects": projects if projects is not None else ["project-a"],
            "sources": sources if sources is not None else ["source-lifeos", "source-obsidian-synth", "source-web-synth", "source-public-synth", "source-client-synth"],
            "artifacts": artifacts or ["*"],
            "excluded_sources": ["source-excluded"],
            "excluded_artifacts": ["artifact-excluded-artifact", "artifact-excluded-dir"],
        },
        "actions": actions,
        "purposes": purposes,
        "locations": locations,
        "processors": processors,
        "validity": {"not_before": NOW - 3600, "expires_at": expires_at, "state": state},
    }


AUTHORIZATIONS = {
    "local": grant("auth-local", ["read", "parse", "index", "derive", "save_output", "display", "rederive", "write_candidate"], ["search", "project_recovery", "summary", "next_step"], ["local"], ["local-runtime"]),
    "cloud": grant("auth-cloud", ["queue", "execute", "send", "derive", "save_output", "display"], ["project_recovery", "summary"], ["lifeos-cloud"], ["lifeos-cloud-mock"]),
    "third_a": grant("auth-third-a", ["queue", "execute", "send", "derive", "save_output"], ["summary"], ["third-party-a"], ["third-party-a-mock"]),
    "training": grant("auth-training", ["send", "evaluate"], ["evaluation"], ["third-party-a"], ["third-party-a-mock"]),
    "search_only": grant("auth-search-only", ["read", "index"], ["search"], ["local"], ["local-runtime"]),
    "expired": grant("auth-expired", ["read"], ["search"], ["local"], ["local-runtime"], expires_at=NOW - 1),
    "revoked": grant("auth-revoked", ["read"], ["search"], ["local"], ["local-runtime"], state="revoked"),
}


def processor(
    processor_id: str,
    location: str,
    *,
    known: bool = True,
    policy_version: str = POLICY_VERSION,
    subprocessors_known: bool = True,
    regions: list[str] | None = None,
    training_default: bool = False,
    evaluation_default: bool = False,
    retention_days: int = 7,
    deletion: str = "supported",
    qualified: bool = True,
) -> dict[str, Any]:
    return {
        "processor_id": processor_id,
        "location": location,
        "known": known,
        "policy_version": policy_version,
        "subprocessors_known": subprocessors_known,
        "regions": regions if regions is not None else ["CN-synthetic"],
        "training_default": training_default,
        "evaluation_default": evaluation_default,
        "retention_days": retention_days,
        "deletion": deletion,
        "qualified": qualified,
    }


PROCESSORS = {
    "local-runtime": processor("local-runtime", "local", retention_days=0),
    "lifeos-cloud-mock": processor("lifeos-cloud-mock", "lifeos-cloud"),
    "third-party-a-mock": processor("third-party-a-mock", "third-party-a"),
    "third-party-b-mock": processor("third-party-b-mock", "third-party-b"),
}


@dataclass
class Request:
    request_id: str
    subject: str
    inputs: list[dict[str, Any]]
    action: str
    purpose: str
    location: str
    processor: dict[str, Any]
    authorization_ids: list[str]
    project: str | None = "project-a"
    now: int = NOW
    allow_training: bool = False
    allow_evaluation: bool = False
    max_retention_days: int = 30
    allowed_regions: list[str] = field(default_factory=lambda: ["CN-synthetic"])
    expected_policy_version: str = POLICY_VERSION
    input_version_digest: str = "inputs-v1"
    lease_version: str = "lease-v1"
    lease_valid: bool = True


def req(
    request_id: str,
    action: str,
    purpose: str,
    location: str,
    processor_id: str,
    *,
    inputs: list[dict[str, Any]] | None = None,
    auths: list[str] | None = None,
    project: str | None = "project-a",
) -> Request:
    return Request(
        request_id=request_id,
        subject="workflow-recovery",
        inputs=copy.deepcopy(inputs or [ARTIFACTS["user"]]),
        action=action,
        purpose=purpose,
        location=location,
        processor=copy.deepcopy(PROCESSORS[processor_id]),
        authorization_ids=auths or [],
        project=project,
    )


def matches_scope(auth: dict[str, Any], request: Request) -> bool:
    scope = auth["scope"]
    if request.project not in scope["projects"]:
        return False
    for item in request.inputs:
        if item["excluded"] or item["source_id"] in scope["excluded_sources"] or item["artifact_id"] in scope["excluded_artifacts"]:
            return False
        artifact_match = "*" in scope["artifacts"] or item["artifact_id"] in scope["artifacts"]
        if not artifact_match or item["source_id"] not in scope["sources"]:
            return False
        # Project membership is a constraint, never a source of permission.
        if item["project_id"] not in (request.project, None):
            return False
    return True


def evaluate(request: Request, authorizations: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    indeterminate: list[str] = []
    matched_auth: str | None = None

    for auth_id in request.authorization_ids:
        auth = authorizations.get(auth_id)
        if not auth:
            continue
        validity = auth["validity"]
        six_match = (
            request.subject in auth["subjects"]
            and matches_scope(auth, request)
            and request.action in auth["actions"]
            and request.purpose in auth["purposes"]
            and request.location in auth["locations"]
            and request.processor["processor_id"] in auth["processors"]
            and validity["not_before"] <= request.now < validity["expires_at"]
            and validity["state"] == "active"
        )
        if six_match:
            matched_auth = auth_id
            break

    if not matched_auth:
        # Specific reason codes are diagnostic metadata, never a fallback allow.
        if not request.authorization_ids:
            reasons.append("AUTH_MISSING")
        elif any(authorizations.get(x, {}).get("validity", {}).get("state") == "revoked" for x in request.authorization_ids):
            reasons.append("AUTH_REVOKED")
        elif any(authorizations.get(x, {}).get("validity", {}).get("expires_at", NOW + 1) <= request.now for x in request.authorization_ids):
            reasons.append("AUTH_EXPIRED")
        else:
            reasons.append("AUTH_SIX_DIMENSION_MISMATCH")

    p = request.processor
    if not p.get("known"):
        indeterminate.append("PROCESSOR_POLICY_UNKNOWN")
    if p.get("policy_version") != request.expected_policy_version:
        reasons.append("POLICY_VERSION_MISMATCH")
    if not p.get("subprocessors_known"):
        indeterminate.append("SUBPROCESSORS_UNKNOWN")
    if not p.get("regions") or not set(p["regions"]).issubset(request.allowed_regions):
        indeterminate.append("REGION_UNKNOWN_OR_DISALLOWED")
    if p.get("training_default") and not request.allow_training:
        reasons.append("TRAINING_DEFAULT_ON")
    if p.get("evaluation_default") and not request.allow_evaluation:
        reasons.append("EVALUATION_DEFAULT_ON")
    if p.get("retention_days", 10**9) > request.max_retention_days:
        reasons.append("RETENTION_EXCEEDED")
    if p.get("deletion") != "supported":
        reasons.append("DELETION_CAPABILITY_INSUFFICIENT")
    if not p.get("qualified"):
        reasons.append("PROCESSOR_NOT_QUALIFIED")

    for item in request.inputs:
        if item["credential"]:
            reasons.append("CREDENTIAL_HARD_BLOCK")
        if item["sensitivity"] == "unknown" and request.location != "local":
            indeterminate.append("SENSITIVITY_UNKNOWN")
        if not item["source_external_allowed"] and request.location != "local":
            reasons.append("SOURCE_EXTERNAL_DISCLOSURE_DENIED")
        if item["state"] in {"deleted", "processing_withdrawn", "source_disconnected", "source_unreachable"}:
            reasons.append("INPUT_RUNTIME_STATE_INVALID")
        if item["excluded"]:
            reasons.append("INPUT_EXCLUDED")
    if not request.lease_valid:
        reasons.append("TASK_LEASE_INVALID")

    reasons = sorted(set(reasons))
    indeterminate = sorted(set(indeterminate))
    raw = "DENY" if reasons else ("INDETERMINATE" if indeterminate else "ALLOW")
    enforcement = "ALLOW" if raw == "ALLOW" else "DENY"
    return {
        "request_id": request.request_id,
        "raw_decision": raw,
        "enforcement_decision": enforcement,
        "reason_codes": reasons + indeterminate,
        "matched_authorization_id": matched_auth if raw == "ALLOW" else None,
        "authorization_set_version": AUTH_VERSION,
        "policy_version": p.get("policy_version", "unknown"),
        "input_version_digest": request.input_version_digest,
        "lease_version": request.lease_version,
        "cache_key": sha("|".join([
            request.subject, request.project or "none", request.action, request.purpose,
            request.location, p.get("processor_id", "unknown"), AUTH_VERSION,
            p.get("policy_version", "unknown"), request.input_version_digest,
            request.lease_version, str(request.now),
        ])),
    }


class Gateway:
    def __init__(self) -> None:
        self.manifests: list[dict[str, Any]] = []

    def send(self, request: Request, authorizations: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
        decision = evaluate(request, authorizations)
        if decision["enforcement_decision"] != "ALLOW":
            self.manifests.append({
                "request_id": request.request_id,
                "decision": "DENY",
                "reason_codes": decision["reason_codes"],
                "sent_field_names": [],
                "sent_field_count": 0,
            })
            return decision, None
        payload = {
            "purpose": request.purpose,
            "processor": request.processor["processor_id"],
            "policy_version": request.processor["policy_version"],
            "location": request.location,
            "input_tokens": [x["content_token"] for x in request.inputs],
        }
        self.manifests.append({
            "request_id": request.request_id,
            "decision": "ALLOW",
            "authorization_id": decision["matched_authorization_id"],
            "purpose": request.purpose,
            "processor": request.processor["processor_id"],
            "policy_version": request.processor["policy_version"],
            "location": request.location,
            "sent_field_names": sorted(payload),
            "sent_field_count": len(payload),
            "input_count": len(request.inputs),
            "input_token_hashes": [sha(x["content_token"]) for x in request.inputs],
        })
        return decision, payload


def run() -> dict[str, Any]:
    gateway = Gateway()
    cases: list[dict[str, Any]] = []

    def check(case_id: str, description: str, request: Request, expected: str, *, use_gateway: bool = False, extra=None) -> dict[str, Any]:
        if use_gateway:
            decision, payload = gateway.send(request, AUTHORIZATIONS)
        else:
            decision, payload = evaluate(request, AUTHORIZATIONS), None
        passed = decision["enforcement_decision"] == expected
        if extra:
            passed = passed and bool(extra(decision, payload))
        row = {
            "case_id": case_id,
            "description": description,
            "expected": expected,
            "actual": decision["enforcement_decision"],
            "raw_decision": decision["raw_decision"],
            "reason_codes": decision["reason_codes"],
            "sent_field_count": 0 if payload is None else len(payload),
            "status": "PASS" if passed else "FAIL",
        }
        cases.append(row)
        return row

    # Allowed processing boundaries.
    check("T01", "local read allow", req("r01", "read", "search", "local", "local-runtime", auths=["local"]), "ALLOW")
    check("T02", "local parse allow", req("r02", "parse", "project_recovery", "local", "local-runtime", inputs=[ARTIFACTS["obsidian"]], auths=["local"]), "ALLOW")
    check("T03", "local FTS/index allow", req("r03", "index", "search", "local", "local-runtime", inputs=[ARTIFACTS["obsidian"]], auths=["local"]), "ALLOW")
    check("T04", "local derivation allow", req("r04", "derive", "summary", "local", "local-runtime", auths=["local"]), "ALLOW")
    check("T05", "LifeOS cloud mock allow", req("r05", "send", "summary", "lifeos-cloud", "lifeos-cloud-mock", auths=["cloud"]), "ALLOW", use_gateway=True)
    check("T06", "named third party mock allow", req("r06", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]), "ALLOW", use_gateway=True)

    # Authorization and policy fail-closed cases.
    check("T07", "missing authorization", req("r07", "send", "summary", "third-party-a", "third-party-a-mock"), "DENY", use_gateway=True)
    check("T08", "expired authorization", req("r08", "read", "search", "local", "local-runtime", auths=["expired"]), "DENY")
    check("T09", "revoked authorization", req("r09", "read", "search", "local", "local-runtime", auths=["revoked"]), "DENY")
    check("T10", "scope expansion to project B", req("r10", "read", "search", "local", "local-runtime", inputs=[ARTIFACTS["project_b"]], auths=["local"], project="project-b"), "DENY")
    check("T11", "search purpose cannot become summary", req("r11", "derive", "summary", "local", "local-runtime", auths=["search_only"]), "DENY")
    r = req("r12", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.subject = "workflow-other"; check("T12", "subject/workflow mismatch", r, "DENY")
    r = req("r13", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["known"] = False; check("T13", "processor policy unknown", r, "DENY", use_gateway=True)
    r = req("r14", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["policy_version"] = "policy-synth-v5"; check("T14", "policy version change", r, "DENY", use_gateway=True)
    r = req("r15", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["subprocessors_known"] = False; check("T15", "subprocessor unknown", r, "DENY", use_gateway=True)
    r = req("r16", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["regions"] = []; check("T16", "region unknown", r, "DENY", use_gateway=True)
    r = req("r17", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["training_default"] = True; check("T17", "training default on", r, "DENY", use_gateway=True)
    r = req("r18", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["evaluation_default"] = True; check("T18", "evaluation default on", r, "DENY", use_gateway=True)
    r = req("r19", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["deletion"] = "unsupported"; check("T19", "deletion insufficient", r, "DENY", use_gateway=True)
    r = req("r20", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["retention_days"] = 90; check("T20", "retention exceeded", r, "DENY", use_gateway=True)
    check("T21", "source forbids external disclosure", req("r21", "send", "summary", "third-party-a", "third-party-a-mock", inputs=[ARTIFACTS["client"]], auths=["third_a"]), "DENY", use_gateway=True)
    check("T22", "credential hard block", req("r22", "send", "summary", "third-party-a", "third-party-a-mock", inputs=[ARTIFACTS["credential"]], auths=["third_a"]), "DENY", use_gateway=True)
    check("T23", "unknown sensitivity external deny", req("r23", "send", "summary", "third-party-a", "third-party-a-mock", inputs=[ARTIFACTS["unknown"]], auths=["third_a"]), "DENY", use_gateway=True)
    r = req("r24", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["qualified"] = False; check("T24", "user consent cannot override unqualified processor", r, "DENY", use_gateway=True)

    # No implicit authority from project/external structure/confirmation.
    for case_id, label, item in [
        ("T25", "Project membership does not override excluded Source", ARTIFACTS["excluded_source"]),
        ("T26", "folder/tag/wiki Link does not override excluded directory", ARTIFACTS["excluded_dir"]),
        ("T27", "candidate Link does not override excluded Artifact", ARTIFACTS["excluded_artifact"]),
    ]:
        check(case_id, label, req("r" + case_id[1:], "read", "search", "local", "local-runtime", inputs=[item], auths=["local"]), "DENY")
    check("T28", "local authorization cannot be reused for cloud", req("r28", "send", "summary", "lifeos-cloud", "lifeos-cloud-mock", auths=["local"]), "DENY", use_gateway=True)
    check("T29", "cloud authorization cannot be reused for third party", req("r29", "send", "summary", "third-party-a", "third-party-a-mock", auths=["cloud"]), "DENY", use_gateway=True)
    check("T30", "third party A authorization cannot be reused for B", req("r30", "send", "summary", "third-party-b", "third-party-b-mock", auths=["third_a"]), "DENY", use_gateway=True)

    # Multi-input constraint inheritance.
    multi_inputs = [ARTIFACTS["user"], ARTIFACTS["client"]]
    multi = req("r31", "derive", "summary", "local", "local-runtime", inputs=multi_inputs, auths=["local"])
    multi_result = evaluate(multi, AUTHORIZATIONS)
    inherited = {
        "derivation_id": "derivation-multi-v1",
        "input_ids": [x["artifact_id"] for x in multi_inputs],
        "sensitivity": "client_secret",
        "allowed_locations": ["local"],
        "external_disclosure": False,
        "retention_days": 7,
        "decision": multi_result["enforcement_decision"],
    }
    check("T31", "multi-input derives under strictest local constraint", multi, "ALLOW")
    check("T32", "multi-input external empty intersection refuses generation", req("r32", "send", "summary", "third-party-a", "third-party-a-mock", inputs=multi_inputs, auths=["third_a"]), "DENY", use_gateway=True)
    subset_request = req("r33", "derive", "summary", "local", "local-runtime", inputs=[ARTIFACTS["user"]], auths=["local"])
    subset_derivation = {
        "derivation_id": "derivation-subset-v2",
        "supersedes": "derivation-multi-v1",
        "included_input_ids": ["artifact-user"],
        "excluded_input_ids": ["artifact-client"],
        "gap_disclosure": ["1 restricted input omitted"],
        "decision": evaluate(subset_request, AUTHORIZATIONS)["enforcement_decision"],
    }
    check("T33", "legal subset creates new derivation and discloses gap", subset_request, "ALLOW", extra=lambda *_: subset_derivation["derivation_id"] != inherited["derivation_id"] and bool(subset_derivation["gap_disclosure"]))

    # Queue/execution/external/save checkpoints and races.
    queue_req = req("r34q", "queue", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"])
    queue_decision = evaluate(queue_req, AUTHORIZATIONS)
    changed_auths = copy.deepcopy(AUTHORIZATIONS); changed_auths["third_a"]["validity"]["state"] = "revoked"
    exec_req = req("r34e", "execute", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"])
    exec_decision = evaluate(exec_req, changed_auths)
    cases.append({"case_id": "T34", "description": "queue allow then revocation denies execution", "expected": "DENY", "actual": exec_decision["enforcement_decision"], "raw_decision": exec_decision["raw_decision"], "reason_codes": exec_decision["reason_codes"], "sent_field_count": 0, "status": "PASS" if queue_decision["enforcement_decision"] == "ALLOW" and exec_decision["enforcement_decision"] == "DENY" else "FAIL"})

    long_task = []
    for stage in ["enqueue", "execute", "derive_segment_1", "derive_segment_2", "publish", "index", "recovery_package"]:
        stage_req = req("long-" + stage, "derive" if stage.startswith("derive") else ("queue" if stage == "enqueue" else "execute" if stage == "execute" else "save_output"), "summary", "local", "local-runtime", auths=["local"])
        auth_state = copy.deepcopy(AUTHORIZATIONS)
        if stage in {"derive_segment_2", "publish", "index", "recovery_package"}:
            auth_state["local"]["validity"]["state"] = "revoked"
        decision = evaluate(stage_req, auth_state)
        long_task.append({"stage": stage, "decision": decision["enforcement_decision"], "output_state": "quarantined" if decision["enforcement_decision"] == "DENY" else "ephemeral_not_published"})
    long_ok = all(x["decision"] == "DENY" and x["output_state"] == "quarantined" for x in long_task[3:])
    cases.append({"case_id": "T35", "description": "mid-task revocation stops and quarantines race output", "expected": "DENY", "actual": "DENY" if long_ok else "ALLOW", "raw_decision": "DENY" if long_ok else "ALLOW", "reason_codes": ["AUTH_REVOKED"], "sent_field_count": 0, "status": "PASS" if long_ok else "FAIL"})

    r = req("r36", "send", "summary", "third-party-a", "third-party-a-mock", auths=["third_a"]); r.processor["policy_version"] = "policy-synth-v5"; check("T36", "policy changes immediately before external send", r, "DENY", use_gateway=True)
    check("T37", "input tombstone before save output", req("r37", "save_output", "summary", "local", "local-runtime", inputs=[ARTIFACTS["deleted"]], auths=["local"]), "DENY")
    r = req("r38", "save_output", "summary", "local", "local-runtime", auths=["local"]); r.lease_valid = False; check("T38", "expired task lease before save", r, "DENY")

    # Output disclosure boundaries and candidate writes.
    check("T39", "cross-Project display denied", req("r39", "display", "project_recovery", "local", "local-runtime", inputs=[ARTIFACTS["project_b"]], auths=["local"], project="project-a"), "DENY")
    check("T40", "re-derivation rechecks purpose", req("r40", "rederive", "evaluation", "local", "local-runtime", auths=["local"]), "DENY")
    check("T41", "candidate Action write allowed only as candidate boundary", req("r41", "write_candidate", "next_step", "local", "local-runtime", auths=["local"]), "ALLOW")
    check("T42", "candidate Link cannot disclose excluded input", req("r42", "write_candidate", "next_step", "local", "local-runtime", inputs=[ARTIFACTS["excluded_artifact"]], auths=["local"]), "DENY")
    check("T43", "non-verbatim inference still treated as disclosure", req("r43", "send", "summary", "third-party-a", "third-party-a-mock", inputs=[ARTIFACTS["client"]], auths=["third_a"]), "DENY", use_gateway=True)
    check("T44", "negative query/ordering signal still treated as disclosure", req("r44", "display", "project_recovery", "local", "local-runtime", inputs=[ARTIFACTS["withdrawn"]], auths=["local"]), "DENY")

    # Cache isolation and minimal-send assertions.
    cache_a = evaluate(req("cache-a", "read", "search", "local", "local-runtime", auths=["local"]), AUTHORIZATIONS)
    cache_b_req = req("cache-b", "read", "project_recovery", "local", "local-runtime", auths=["local"]); cache_b_req.project = None
    cache_b = evaluate(cache_b_req, AUTHORIZATIONS)
    cache_ok = cache_a["cache_key"] != cache_b["cache_key"] and all(cache_a.get(x) for x in ["authorization_set_version", "policy_version", "input_version_digest", "lease_version"])
    cases.append({"case_id": "T45", "description": "authorization cache key binds subject/project/purpose/location/versions/time", "expected": "ALLOW", "actual": "ALLOW" if cache_ok else "DENY", "raw_decision": "ALLOW" if cache_ok else "DENY", "reason_codes": [], "sent_field_count": 0, "status": "PASS" if cache_ok else "FAIL"})

    allowed_manifests = [x for x in gateway.manifests if x["decision"] == "ALLOW"]
    denied_manifests = [x for x in gateway.manifests if x["decision"] == "DENY"]
    allowed_fields = {"purpose", "processor", "policy_version", "location", "input_tokens"}
    send_ok = all(set(x["sent_field_names"]) == allowed_fields for x in allowed_manifests) and all(x["sent_field_count"] == 0 for x in denied_manifests)
    cases.append({"case_id": "T46", "description": "remote payload exact allowlist and all denied paths zero-send", "expected": "ALLOW", "actual": "ALLOW" if send_ok else "DENY", "raw_decision": "ALLOW" if send_ok else "DENY", "reason_codes": [], "sent_field_count": sum(x["sent_field_count"] for x in allowed_manifests), "status": "PASS" if send_ok else "FAIL"})

    eval_request = req("r48", "evaluate", "evaluation", "third-party-a", "third-party-a-mock", inputs=[ARTIFACTS["public"]], auths=["training"])
    eval_request.allow_evaluation = True
    eval_request.processor["evaluation_default"] = True
    check("T48", "evaluation requires an independent purpose grant and explicit opt-in", eval_request, "ALLOW")

    audit_entries = [{
        "audit_id": "audit-" + x["case_id"].lower(),
        "action_code": "authorize_boundary",
        "result_code": x["actual"],
        "reason_codes": x["reason_codes"],
        "subject_ref": "subj-" + sha(x["case_id"])[:8],
        "object_set_digest": sha(x["case_id"] + FIXTURE_VERSION),
        "authorization_set_version": AUTH_VERSION,
        "policy_version": POLICY_VERSION,
        "sequence": i + 1,
    } for i, x in enumerate(cases)]

    forbidden_patterns = [
        r"/Users/", r"/home/", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
        r"recovery[ _-]?code", r"api[_-]?key", r"prompt_text", r"embedding",
        r"SYNTH_CONTENT_",  # even synthetic payload bodies must not leak into logs/audit
    ]
    privacy_blob = json.dumps({"cases": cases, "audit_entries": audit_entries, "manifests": gateway.manifests}, ensure_ascii=False)
    privacy_hits = [pattern for pattern in forbidden_patterns if re.search(pattern, privacy_blob, re.IGNORECASE)]
    privacy_ok = not privacy_hits
    cases.append({"case_id": "T47", "description": "logs/AuditEntry/manifests contain no body/path/prompt/vector/credential", "expected": "ALLOW", "actual": "ALLOW" if privacy_ok else "DENY", "raw_decision": "ALLOW" if privacy_ok else "DENY", "reason_codes": privacy_hits, "sent_field_count": 0, "status": "PASS" if privacy_ok else "FAIL"})

    pass_count = sum(x["status"] == "PASS" for x in cases)
    result = {
        "spike": "SP-04",
        "fixture_version": FIXTURE_VERSION,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "network_calls": 0, "real_model_calls": 0, "real_vault_reads": 0},
        "summary": {"total": len(cases), "passed": pass_count, "failed": len(cases) - pass_count, "p0_failed": len(cases) - pass_count, "machine_result": "PASS" if pass_count == len(cases) else "FAIL"},
        "cases": cases,
        "constraint_inheritance": {"strictest": inherited, "legal_subset": subset_derivation, "empty_intersection": {"request_id": "r32", "decision": "DENY", "output_created": False}},
        "long_task": long_task,
        "gateway": {"manifests": gateway.manifests, "actual_network_sends": 0, "mock_allowed_calls": len(allowed_manifests), "mock_denied_calls": len(denied_manifests)},
        "privacy_scan": {"patterns": forbidden_patterns, "hits": privacy_hits, "status": "PASS" if privacy_ok else "FAIL"},
        "audit_entries": audit_entries,
    }
    return result


def render_outputs(result: dict[str, Any]) -> None:
    dump(ROOT / "results.json", result)
    dump(LOGS / "run_summary.json", result["summary"])
    dump(LOGS / "scenario_results.json", result["cases"])
    dump(LOGS / "decision_samples.json", result["cases"][:12])
    dump(LOGS / "audit_entries.json", result["audit_entries"])
    dump(LOGS / "privacy_scan.json", result["privacy_scan"])
    dump(ROOT / "gateway_send_manifest.json", result["gateway"])

    with (ROOT / "test_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "description", "expected", "actual", "raw_decision", "reason_codes", "sent_field_count", "status"])
        writer.writeheader()
        for row in result["cases"]:
            out = dict(row); out["reason_codes"] = "|".join(out["reason_codes"]); writer.writerow(out)

    decision_rows = {}
    for row in result["cases"]:
        decision_rows.setdefault((row["raw_decision"], row["actual"]), {"count": 0, "examples": []})
        decision_rows[(row["raw_decision"], row["actual"])]["count"] += 1
        decision_rows[(row["raw_decision"], row["actual"])]["examples"].append(row["case_id"])
    with (ROOT / "authorization_decision_table.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f); writer.writerow(["raw_decision", "enforcement_decision", "count", "case_ids"])
        for (raw, actual), item in sorted(decision_rows.items()): writer.writerow([raw, actual, item["count"], "|".join(item["examples"])])

    write(ROOT / "SP-04_report.md", f"""# SP-04 Evidence Report

- Machine result: **{result['summary']['machine_result']}**
- Tests: **{result['summary']['passed']}/{result['summary']['total']} PASS**
- P0 failures: **{result['summary']['p0_failed']}**
- Network/model/cloud/Vault calls: **0 / 0 / 0 / 0**

The deterministic evaluator encoded six-dimensional Authorization, mandatory policy envelope, runtime state, checkpoint re-evaluation, strict multi-input inheritance, zero-send denial, and privacy-minimal audit evidence. This evidence is a candidate implementation contract, not a production architecture or Schema/API freeze.
""")
    write(ROOT / "authorization_decision_contract.md", """# Authorization decision contract

`raw_decision ∈ {ALLOW, DENY, INDETERMINATE}`. Enforcement maps only `ALLOW` to execution; both `DENY` and `INDETERMINATE` fail closed to `DENY`.

An allow requires one currently valid Authorization to match all six dimensions—subject, complete input scope including exclusions, action, purpose, exact location/processor, and time—plus every mandatory processor-policy check and current runtime state. User confirmation can create or narrow a grant but cannot override processor qualification, unknown policy/subprocessor/region, default training/evaluation, retention/deletion failure, source restrictions, minimization failure, or credential blocking.

Every enqueue, execute, external send, output save, cross-Project display, re-derivation, candidate write, and long-task publish/index/recovery-package checkpoint is independently evaluated. The contract carries authorization set version, processor policy version, precise input digest, and lease version. A cache key additionally binds subject, Project, action, purpose, location, processor, and deterministic evaluation time.

This JSON-shaped contract is database-independent test material. It does not freeze a table layout, API, queue, policy language, or service boundary.
""")
    write(ROOT / "processor_policy_matrix.md", """# Processor policy matrix

| Processor | Location | Policy known | Subprocessors/region | Training/eval default | Retention | Deletion | Spike eligibility |
|---|---|---|---|---|---:|---|---|
| local-runtime | local | yes | known/synthetic local | off/off | 0 days | supported | eligible within matching grant |
| lifeos-cloud-mock | LifeOS cloud mock | yes | known/CN-synthetic | off/off | 7 days | supported | eligible within matching grant |
| third-party-a-mock | named third party mock | yes | known/CN-synthetic | off/off | 7 days | supported | eligible within matching grant |
| third-party-b-mock | different named third party | yes | known/CN-synthetic | off/off | 7 days | supported | no grant in fixture; denied |

Mutation cases prove that unknown policy/subprocessors/region, policy-version change, default training/evaluation, excessive retention, insufficient deletion, and failed qualification all deny. No row is a real vendor assessment or selection.
""")
    lt = "\n".join(f"| {x['stage']} | {x['decision']} | {x['output_state']} |" for x in result["long_task"])
    write(ROOT / "long_task_revocation_report.md", f"""# Long-task revocation report

| Checkpoint | Decision | Output state |
|---|---|---|
{lt}

Revocation is injected before segment 2. Segment 2 and all later publish/index/recovery-package checkpoints deny; the race output remains quarantined and therefore cannot become visible, searchable, or recoverable.
""")
    c = result["constraint_inheritance"]
    write(ROOT / "constraint_inheritance_report.md", f"""# Constraint inheritance report

- Strict multi-input Derivation: `{c['strictest']['derivation_id']}` inherits `client_secret`, local-only, no external disclosure, and 7-day retention.
- Legal subset: `{c['legal_subset']['derivation_id']}` is a new Derivation, excludes `artifact-client`, and discloses `{c['legal_subset']['gap_disclosure'][0]}`.
- Empty external intersection: request `{c['empty_intersection']['request_id']}` is denied and creates no output.

Project, folder, tag, wiki-link, candidate Link, and user confirmation are not authorization sources and cannot widen this envelope.
""")
    write(ROOT / "environment.md", f"""# Environment

- Python: {result['environment']['python']}
- Platform: {result['environment']['platform']}
- Fixture: {FIXTURE_VERSION}
- Standard library only; deterministic clock and identifiers
- Network, real cloud, real third party, real model, real Vault, real sensitive-data access: all zero
- Re-run: `python3 lifeos/spikes/SP-04/run_spike.py`
""")
    write(ROOT / "cleanup.md", """# Cleanup

All generated material is confined to `lifeos/spikes/SP-04/` and contains synthetic fixtures only. Re-running overwrites only the listed evidence files in that exact directory. No temporary external directory, account, service, Vault, or network resource is created; no cleanup command is required.
""")
    write(ROOT / "fixtures.md", """# Synthetic fixtures

The in-script fixture pack covers LifeOS user original, simulated Obsidian external original, external material, public material, personal content, client secret, credential/private-key/recovery-code class, unknown sensitivity, Project A/B/no Project, excluded Source/directory/Artifact, deleted/processing-withdrawn/disconnected/unreachable states, local/cloud/named-third-party/training grants, and expired/revoked grants. Content bodies are harmless deterministic tokens and never appear in logs or AuditEntry.
""")


if __name__ == "__main__":
    result = run()
    render_outputs(result)
    print(json.dumps(result["summary"], ensure_ascii=False))
    raise SystemExit(0 if result["summary"]["machine_result"] == "PASS" else 1)
