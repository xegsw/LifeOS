#!/usr/bin/env python3
"""Read-only static contract verifier for LIFEOS-P3-114 fixed synthetic fixtures."""
from __future__ import annotations

import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[5]


def load(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_counterexamples.py FIXTURE.json")
    fixture_path = pathlib.Path(sys.argv[1])
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    source = load("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/source_identity_and_provenance_matrix.json")
    feedback = load("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/feedback_lifecycle_state_machine.json")
    home = load("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/home_question_advice_feedback_contract.json")
    scenario = load("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/cross_domain_scenario.json")
    gates = load("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/gate_assessment.json")

    tests: list[dict[str, object]] = []

    source_ids = {row["source_id"] for row in source["sources"]}
    expected_sources = {
        "SRC-SYN-WORK-001",
        "SRC-SYN-HEALTH-001",
        "SRC-SYN-INTERACTION-001",
        "SRC-SYN-FEEDBACK-001",
    }
    tests.append({"id": "IR-006-source-identities", "pass": source_ids == expected_sources})
    health = next(row for row in source["sources"] if row["source_id"] == "SRC-SYN-HEALTH-001")
    tests.append({
        "id": "IR-006-missing-revoked-health-degrades",
        "pass": "no personalized health/fitness suggestion" in health["on_expiry_or_revoke"],
    })
    tests.append({
        "id": "IR-006-advice-stale-rule",
        "pass": "missing, conflicting, expired or unauthorized" in source["provenance_chain"]["advice"]["stale_rule"],
    })

    states = {row["id"]: row for row in feedback["states"]}
    tests.append({
        "id": "IR-008-accept-not-execution",
        "pass": states["FDB-ACCEPT"]["affects_future_date"] == "no" and "not execution" in states["FDB-MODIFIED-ACCEPT"]["affects_current_understanding"],
    })
    tests.append({
        "id": "IR-008-result-not-memory",
        "pass": "MEM-CAND only" in states["RES"]["affects_future_date"] and "blocked" in states["MEM-CAND"]["affects_future_date"],
    })
    tests.append({
        "id": "IR-007-home-controls-and-no-automation",
        "pass": home["home_contract"]["advice_limit"] == "1-3" and home["home_contract"]["question_limit"] == "0-1" and home["advice_identity_contract"]["non_automation"] == "Advice never creates or executes an action.",
    })
    tests.append({
        "id": "IR-009-health-warning-stop",
        "pass": scenario["negative_paths"]["warning_signal"] == "stop health/fitness advice and suggest appropriate professional support" and {"diagnosis", "treatment", "safety guarantee", "automatic action"}.issubset(set(scenario["advice"]["not_allowed"])),
    })
    tests.append({
        "id": "IR-008-close-reopen-identities",
        "pass": "remain separately traceable" in scenario["close_reopen"] and "activate MEM-CAND" in scenario["close_reopen"],
    })
    names = [row["gate"] for row in gates["gates"]]
    tests.append({
        "id": "IR-010-formal-gates-and-limits",
        "pass": names == [
            "Gate 1: product consistency",
            "Gate 2: data and source review",
            "Gate 3: AI permission and trust",
            "Gate 4: technical feasibility",
            "Gate 5: user value validation",
        ] and gates["gates"][4]["result"] == "falsifiable hypothesis only",
    })

    required_case_ids = {
        "CE-PROV-001", "CE-PROV-002", "CE-FEEDBACK-001", "CE-FEEDBACK-002", "CE-HEALTH-001", "CE-IDENTITY-001"
    }
    tests.append({"id": "IR-012-fixed-fixture-complete", "pass": {row["id"] for row in fixture["cases"]} == required_case_ids})
    failures = [row["id"] for row in tests if not row["pass"]]
    result = {
        "runner": "verify_counterexamples.py",
        "mode": "static candidate-contract verification only; no app/model/network/database execution",
        "fixture_id": fixture["fixture_id"],
        "tests": tests,
        "passed": len(tests) - len(failures),
        "failed": len(failures),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
