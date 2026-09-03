#!/usr/bin/env python3
"""Read-only review-owned source checks for the Closure-2 synthetic adapter matrix."""
import json
import sys
from pathlib import Path

src = Path(sys.argv[1])
runtime = (src / "src/runtime.rs").read_text()
adapter = (src / "src/deepseek.rs").read_text()

def adapter_contract(r: str, d: str) -> bool:
    return (
        r.count('if run_mode() == "real_gate"') >= 2
        and 'Ok(deepseek::synthetic_models(timestamp))' in r
        and 'Ok(deepseek::synthetic_context_response(timestamp, items.len()))' in r
        and d.count('method_class: "NONE"') >= 2
        and d.count('status_class: "synthetic_no_network".into()') >= 2
    )

def key_failure_contract(r: str) -> bool:
    return (
        'if value.credential_reference.is_none()' in r
        and '"credential_required"' in r
        and '"key_material_missing"' in r
        and 'KeychainMissing) => {}' in r
    )

checks = {
    "synthetic_adapter_has_no_network_receipt": adapter_contract(runtime, adapter),
    "credential_missing_fails_before_adapter": key_failure_contract(runtime),
}
mutations = {
    "synthetic_models_replaced_with_real": not adapter_contract(runtime.replace('Ok(deepseek::synthetic_models(timestamp))', 'deepseek::real_models(&api_key, timestamp)', 1), adapter),
    "synthetic_response_replaced_with_real": not adapter_contract(runtime.replace('Ok(deepseek::synthetic_context_response(timestamp, items.len()))', 'deepseek::real_context_response(&api_key, &model, &prompt, timestamp)', 1), adapter),
    "credential_presence_guard_removed": not key_failure_contract(runtime.replace('if value.credential_reference.is_none()', 'if false', 1)),
}
result = {"checks": checks, "mutations_rejected": mutations, "pass": all(checks.values()) and all(mutations.values())}
print(json.dumps(result, sort_keys=True, indent=2))
raise SystemExit(0 if result["pass"] else 1)
