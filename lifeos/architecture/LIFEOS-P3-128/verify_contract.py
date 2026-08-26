#!/usr/bin/env python3
"""Fail-closed structural verifier for the P3-128 L2 mapping contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
TASK_ID = "LIFEOS-P3-128"
JSON_FILES = [
    "frozen_input_impact.json",
    "object_mapping.json",
    "context_lifecycle.json",
    "memory_provenance.json",
    "context_resolver_contract.json",
    "application_port_contract.json",
    "p3_126_compatibility.json",
    "fast_track_handoff.json",
    "negative_cases.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(checks: list[dict], check_id: str, detail: str) -> None:
    checks.append({"id": check_id, "result": "FAIL", "detail": detail})


def passed(checks: list[dict], check_id: str, detail: str) -> None:
    checks.append({"id": check_id, "result": "PASS", "detail": detail})


def require(condition: bool, checks: list[dict], check_id: str, detail: str) -> None:
    (passed if condition else fail)(checks, check_id, detail)


def read_json(name: str, checks: list[dict]) -> dict:
    path = ROOT / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(checks, f"JSON-{name}", f"unreadable or invalid JSON: {error}")
        return {}
    require(value.get("task_id") == TASK_ID, checks, f"TASK-{name}", "task_id is LIFEOS-P3-128")
    return value


def main() -> int:
    checks: list[dict] = []
    data = {name: read_json(name, checks) for name in JSON_FILES}

    frozen = data["frozen_input_impact.json"]
    inputs = frozen.get("inputs", [])
    require(len(inputs) >= 10, checks, "AC-01-A", "Frozen/Not Frozen impact matrix has all input classes")
    require(all((WORKSPACE / item.get("path", "")).exists() for item in inputs), checks, "AC-01-B", "every fixed-input path exists")
    require("Frozen core semantic and trust invariants" in frozen.get("precedence", []), checks, "AC-01-C", "Frozen precedence is explicit")
    require(bool(frozen.get("conflict_policy", {}).get("resolution")), checks, "AC-01-D", "conflict policy is explicit")

    mapping = data["object_mapping.json"]
    core = mapping.get("core_objects", [])
    concepts = mapping.get("concepts", [])
    require(len(core) == 12 and len(set(core)) == 12, checks, "AC-02-A", "all 11 core objects plus Link are present")
    require(len(concepts) == 5, checks, "AC-02-B", "all five requested concepts are mapped")
    complete_cells = all(set(item.get("core_mapping", {})) == set(core) and all(isinstance(v, str) and v.strip() for v in item.get("core_mapping", {}).values()) for item in concepts)
    require(complete_cells, checks, "AC-02-C", "every concept/core-object mapping cell is nonblank")
    require(all(item.get("identity_authority") and item.get("lifecycle") for item in concepts), checks, "AC-02-D", "identity and lifecycle are supplied for each concept")

    lifecycle = data["context_lifecycle.json"]
    states = {item.get("state") for item in lifecycle.get("states", [])}
    require({"candidate", "confirmed", "active", "watching", "closed"}.issubset(states), checks, "AC-03-A", "Context state machine is complete")
    require(bool(lifecycle.get("context_identity", {}).get("rule")), checks, "AC-03-B", "Context stable-ID rule is present")
    require(bool(lifecycle.get("project_compatibility", {}).get("rule")), checks, "AC-03-C", "Project/non-Project compatibility is explicit")

    memory = data["memory_provenance.json"]
    traces = memory.get("trace_examples", [])
    require(len(traces) >= 2 and all(len(trace.get("chain", [])) >= 5 for trace in traces), checks, "AC-04-A", "Memory provenance has complete trace examples")
    require("not a second authority" in memory.get("memory_definition", ""), checks, "AC-04-B", "Memory non-authority boundary is explicit")
    require(len(memory.get("freshness_and_invalidation", [])) >= 5, checks, "AC-04-C", "stale/revoked/tombstone invalidation is covered")

    resolver = data["context_resolver_contract.json"]
    categories = {item.get("category") for item in resolver.get("input_categories", [])}
    require({"person_context", "page_context", "selection_context"}.issubset(categories), checks, "AC-05-A", "Person/Page/Selection resolver inputs are present")
    require(all(item.get("removal") for item in resolver.get("input_categories", [])), checks, "AC-05-B", "every resolver category has removal semantics")
    require(len(resolver.get("failure_modes", [])) >= 5, checks, "AC-05-C", "authorization and evidence failure semantics are complete")

    ports = data["application_port_contract.json"]
    require(len(ports.get("application_services", [])) >= 5, checks, "AC-06-A", "application service boundary is explicit")
    port_names = {item.get("name") for item in ports.get("ports", [])}
    require({"CaptureRepository", "AuthorizationPort", "AuditPort", "DomainEventPort"}.issubset(port_names), checks, "AC-06-B", "repository, authorization, audit, and event ports are present")
    require("UI -> Application Service -> Domain policy -> Ports -> Adapters" in ports.get("layer_rule", ""), checks, "AC-06-C", "no-direct-SQL layer rule is explicit")

    compatibility = data["p3_126_compatibility.json"]
    dispositions = {item.get("disposition") for item in compatibility.get("facts", [])}
    require(
        bool(compatibility.get("retain"))
        and bool(compatibility.get("adapt"))
        and bool(compatibility.get("defer")),
        checks,
        "AC-07-A",
        "retain, adapt, and defer compatibility dispositions are all declared",
    )
    require(len(compatibility.get("facts", [])) >= 7 and "retain" in dispositions and "adapt" in dispositions, checks, "AC-07-B", "P3-126 fact matrix is populated")
    require(len(compatibility.get("defer", [])) >= 4, checks, "AC-07-C", "current Runtime deferrals are explicit")

    handoff = data["fast_track_handoff.json"]
    require(bool(handoff.get("unique_user_result")), checks, "AC-08-A", "one Fast Track vertical slice is named")
    require(len(handoff.get("allowed_successor_write_scope", [])) >= 2 and len(handoff.get("protected_scope", [])) >= 2, checks, "AC-08-B", "write/protected scope is explicit")
    require(len(handoff.get("acceptance_matrix", [])) >= 11, checks, "AC-08-C", "Fast Track test/evidence matrix is complete")
    require(len(handoff.get("stop_rules", [])) >= 5, checks, "AC-08-D", "Fast Track stop rules are complete")

    negatives = data["negative_cases.json"]
    ids = {item.get("id") for item in negatives.get("cases", [])}
    require({"NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-06"}.issubset(ids), checks, "AC-09-A", "all six required counterexamples are present")
    require(all(item.get("expected") and item.get("maps_to") for item in negatives.get("cases", [])), checks, "AC-09-B", "counterexamples have expected fail-closed behavior and AC mapping")

    delivery = WORKSPACE / "lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md"
    require(delivery.exists(), checks, "AC-10-A", "main delivery exists")
    delivery_text = delivery.read_text(encoding="utf-8") if delivery.exists() else ""
    forbidden_claims = ["Stage 4 Ready", "已冻结 Schema/API", "真实 MVP 已实现"]
    require(not any(claim in delivery_text for claim in forbidden_claims), checks, "AC-10-B", "main delivery makes no forbidden freeze/Stage/implementation claim")
    require(all(term in delivery_text for term in ["[事实]", "[候选决定]", "[后置项]", "[需 PM 确认]"]), checks, "AC-10-C", "main delivery labels facts, candidate decisions, deferrals, and PM items")

    manifest = ROOT / "MANIFEST.md"
    require(manifest.exists(), checks, "MANIFEST-01", "Manifest exists")
    manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    manifest_entries = [line.split(" | ") for line in manifest_text.splitlines() if line.startswith("| `")]
    hash_ok = True
    for entry in manifest_entries:
        if len(entry) < 3:
            hash_ok = False
            continue
        rel = entry[0].strip("| `")
        expected_hash = entry[1].strip()
        path = ROOT / rel
        if not path.exists() or sha256(path) != expected_hash:
            hash_ok = False
    require(hash_ok and len(manifest_entries) >= 11, checks, "MANIFEST-02", "Manifest hashes all stable non-self artifacts")

    failures = [check for check in checks if check["result"] != "PASS"]
    result = {
        "task_id": TASK_ID,
        "verifier": "verify_contract.py",
        "result": "PASS" if not failures else "FAIL",
        "ac_results": {f"AC-{number:02d}": "PASS" if all(check["result"] == "PASS" for check in checks if check["id"].startswith(f"AC-{number:02d}")) else "FAIL" for number in range(1, 11)},
        "counts": {"P0": 0 if not failures else len(failures), "P1": 0, "P2": 0, "Unknown": 0 if not failures else len(failures), "Not Implemented": 0 if not failures else len(failures)},
        "check_count": len(checks),
        "failure_count": len(failures),
        "checks": checks,
    }
    (ROOT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": result["result"], "check_count": result["check_count"], "failure_count": result["failure_count"]}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
