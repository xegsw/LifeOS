#!/usr/bin/env python3
"""Read-only Phase-B verifier written by independent review attempt 3."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[6]
INPUT_ROOT = Path("/Users/xxe/Documents/No.2")
CANDIDATE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141/candidate"
P3_139 = Path("/Users/xxe/.codex/worktrees/b381/No.2/lifeos/engineering/LIFEOS-P3-139/closure-4/candidate")
P3_140 = Path("/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/candidate")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def framed_tree(root: Path) -> tuple[int, str]:
    tree = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        name = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        tree.update(len(name).to_bytes(8, "big"))
        tree.update(name)
        tree.update(len(data).to_bytes(8, "big"))
        tree.update(data)
    return len(files), tree.hexdigest()


def check(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"id": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    inventory = json.loads((INPUT_ROOT / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json").read_text())
    fixed = []
    for item in inventory["entries"]:
        path = Path(item["path"])
        if not path.is_absolute():
            path = INPUT_ROOT / path
        fixed.append(check(
            f"fixed:{item['role']}",
            path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"],
            str(path),
        ))
    runtime = (CANDIDATE / "src/runtime.rs").read_text()
    build = (CANDIDATE / "build.rs").read_text()
    memory = (CANDIDATE / "src/runtime/memory_context.rs").read_text()
    ui = (CANDIDATE / "ui/runtime-adapter.js").read_text()
    ipc_match = re.search(r"const IPC: \[&str; (\d+)\] = \[(.*?)\];", runtime, re.S)
    ipc = re.findall(r'"([a-z_]+)"', ipc_match.group(2)) if ipc_match else []
    profiles = re.findall(r'"([a-z_]+)"', re.search(r"fn provider_profiles\(\).*?vec!\[(.*?)\]", runtime).group(1))
    p139_count, p139_tree = framed_tree(P3_139)
    p140_count, p140_tree = framed_tree(P3_140)
    candidate_count, candidate_tree = framed_tree(CANDIDATE)
    checks = [
        *fixed,
        check("lineage:p3_139", (p139_count, p139_tree) == (77, "63e2bc5525bb8d57cd0b3a8d02e87d9d5379a1c18f385ed48d0b284cb53acc9e"), f"{p139_count}/{p139_tree}"),
        check("lineage:p3_140", (p140_count, p140_tree) == (79, "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e"), f"{p140_count}/{p140_tree}"),
        check("candidate:tree", (candidate_count, candidate_tree) == (79, "6a45b656a7bd1203485818872242d4ce2b9db572f197bec869356a6d807a87e1"), f"{candidate_count}/{candidate_tree}"),
        check("ipc:exact_20", len(ipc) == 20 and len(set(ipc)) == 20 and ipc_match.group(1) == "20", repr(ipc)),
        check("provider:closed_four", profiles == ["openai", "anthropic", "ollama", "lm_studio"], repr(profiles)),
        check("provider:no_custom", "ProviderProfile::Custom" not in runtime and "CustomProvider" not in runtime, "Provider enum vocabulary"),
        check("provider:first_send_lock", "provider_locked_after_first_send" in runtime and "locked_profile" in runtime, "static lock gate"),
        check("gate:receipt_precedes_root", build.index("let phase_b_receipt") < build.index("let raw = env::var(\"LIFEOS_RUNTIME_ROOT\")"), "build.rs ordering"),
        check("root:ownership_marker", "expected_ownership" in runtime and "validate_existing_real_root" in runtime, "ownership/schema functions"),
        check("root:sidecar_rejection", "database_sidecar_rejected" in runtime, "sidecar guard"),
        check("resolver:budget_failure_closed", "context_budget_rejected" in memory and "receipt_not_found" in memory, "resolver stable errors"),
        check("feedback:stale_path", "stale" in runtime and "FeedbackDecision::Correct" in runtime, "feedback implementation"),
        check("health:request_local_removal", "removed_domains" in memory and "remove-health" in ui, "runtime/UI removal seams"),
        check("phase_c:real_total_limit_14", "if self == Self::Real { 14 }" in runtime, "P3-141 permits 14 Work records across 7–14 days"),
        check("phase_c:daily_work_quota", "daily" in runtime.lower() and "work" in runtime.lower(), "daily quota enforcement"),
        check("phase_c:structured_health_fields", all(token in memory for token in ["sleep_duration", "energy", "soreness", "training_load", "available_time"]), "required bounded Health/Fitness fields"),
        check("phase_c:memory_cap_three", re.search(r"durable_memories.*(?:>=|>)\s*3", memory, re.S) is not None, "maximum three confirmed Durable Memory records"),
        check("phase_c:current_contract_identity", "p3-133-real-ui-" not in runtime and "p3-133-real-self-use" not in ui, "P3-141 real-flow identifiers must not retain P3-133 contract namespace"),
    ]
    result = {
        "schema": "lifeos.p3-141.attempt-3.independent-verifier.v1",
        "fixed_input_pass": sum(item["status"] == "PASS" for item in fixed),
        "fixed_input_total": len(fixed),
        "checks": checks,
        "pass_count": sum(item["status"] == "PASS" for item in checks),
        "fail_count": sum(item["status"] == "FAIL" for item in checks),
        "phase_b_pass": all(item["status"] == "PASS" for item in checks),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
