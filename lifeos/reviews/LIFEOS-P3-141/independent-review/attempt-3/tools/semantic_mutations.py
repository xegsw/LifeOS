#!/usr/bin/env python3
"""In-memory semantic mutations owned by P3-141 review attempt 3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[6] / "lifeos/engineering/LIFEOS-P3-141/candidate/src"
runtime = (ROOT / "runtime.rs").read_text()
build = (ROOT.parent / "build.rs").read_text()
memory = (ROOT / "runtime/memory_context.rs").read_text()


def has_receipt_gate(build_source: str) -> bool:
    return (
        'mode == "real_self_use"' in build_source
        and 'phase_b_receipt.as_deref() != Some("LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS")' in build_source
        and "phase_b_independent_pass_required before runtime-root inspection" in build_source
        and build_source.index("let phase_b_receipt") < build_source.index('let raw = env::var("LIFEOS_RUNTIME_ROOT")')
    )


def has_root_ownership(runtime_source: str) -> bool:
    return "fn validate_existing_real_root" in runtime_source and "if !marker || !database" in runtime_source and "validate_ownership_marker(paths)?; reject_sidecars(paths)?" in runtime_source


def has_provider_lock(runtime_source: str) -> bool:
    return "if state.locked_profile.is_none()" in runtime_source and "state.locked_profile = Some(state.settings.profile)" in runtime_source


def has_health_domain_guard(memory_source: str) -> bool:
    return "matches!(task,TaskType::CrossDomain) && health_necessary && authorization==AUTH_CROSS" in memory_source and "removed_for_request" in memory_source


def has_feedback_budget_guards(runtime_source: str, memory_source: str) -> bool:
    return "FeedbackDecision::Correct" in runtime_source and "context_budget_rejected" in memory_source and "receipt_not_found" in memory_source


def mutation(identifier: str, before: bool, after: bool) -> dict[str, object]:
    return {"id": identifier, "baseline_guard_present": before, "mutated_guard_present": after, "detected": before and not after}


def main() -> None:
    receipt_mut = build.replace("phase_b_independent_pass_required before runtime-root inspection", "receipt_guard_removed", 1)
    root_mut = runtime.replace("validate_ownership_marker(paths)?;", "/* ownership invocation removed */", 1)
    provider_mut = runtime.replace("state.locked_profile = Some(state.settings.profile)", "state.locked_profile = None", 1)
    health_mut = memory.replace("matches!(task,TaskType::CrossDomain) && health_necessary && authorization==AUTH_CROSS", "false", 1)
    feedback_mut = memory.replace("context_budget_rejected", "budget_guard_removed")
    results = [
        mutation("receipt_gate", has_receipt_gate(build), has_receipt_gate(receipt_mut)),
        mutation("root_ownership", has_root_ownership(runtime), has_root_ownership(root_mut)),
        mutation("provider_lock", has_provider_lock(runtime), has_provider_lock(provider_mut)),
        mutation("health_boundary", has_health_domain_guard(memory), has_health_domain_guard(health_mut)),
        mutation("feedback_budget", has_feedback_budget_guards(runtime, memory), has_feedback_budget_guards(runtime, feedback_mut)),
    ]
    print(json.dumps({"schema": "lifeos.p3-141.attempt-3.semantic-mutations.v1", "results": results, "detected": sum(item["detected"] for item in results), "total": len(results)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
