#!/usr/bin/env python3
"""Assert and assemble the task-local black-box CLI recovery evidence chain."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
ready = json.loads((evidence / "operator_chain_ready_preview.json").read_text())
first = json.loads((evidence / "operator_chain_first_confirm.json").read_text())
again = json.loads((evidence / "operator_chain_idempotent.json").read_text())

assert ready["preview"]["status"] == "ready"
assert ready["execution"] == {"status": "not_executed", "reason": "preview_only"}
assert first["preview"]["status"] == "ready"
assert first["execution"]["status"] == "recovered" and first["execution"]["idempotent"] is False
assert again["preview"]["status"] == "ready"
assert again["execution"]["status"] == "recovered" and again["execution"]["idempotent"] is True
assert [item["event"] for item in first["snapshot"]["audit"]] == ["capture_pending", "recovery_completed"]
assert [item["event"] for item in again["snapshot"]["audit"]] == ["capture_pending", "recovery_completed", "recovery_idempotent"]
assert all(item["boundaries"] == ready["preview"]["boundaries"] for item in (ready["preview"], first["execution"], again["execution"]))

chain = {"task": "LIFEOS-P3-067", "assertion": "clean_cli_ready_preview_then_first_confirm_then_idempotent_receipt", "pass": 1, "fail": 0, "events": [ready, first, again]}
(evidence / "operator_cli_chain.json").write_text(json.dumps(chain, indent=2, sort_keys=True) + "\n")
results_path = evidence / "test_results.json"
results = json.loads(results_path.read_text())
results["cases"].append("clean_cli_ready_preview_first_confirm_then_idempotent_receipt")
results["pass"] += 1
results_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
print(json.dumps({"cli_chain_assertion": "PASS", "pass": 1, "fail": 0}, sort_keys=True))
