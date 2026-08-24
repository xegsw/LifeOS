# LIFEOS-P3-007 Third P0 Narrow Remediation Evidence Manifest

- Fixture version: `lifeos-p3-007-synthetic-v4`
- Data class: synthetic-disposable
- Environment: `macOS-26.5.2-arm64-arm-64bit` / Python `3.9.6` / SQLite `3.51.0`
- Content snapshot SHA-256: `ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`
- Re-run command: `cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py`
- Run at: `2026-08-11T04:44:47.376193+00:00`
- Responsible role: LIFEOS-P3-007 engineering remediation specialist session
- Known limits: no real data, Vault, Tauri/IPC, filesystem export, cloud/model, vector, sync, L3, external user, production packaging or SLA; restore remains a synthetic in-process candidate gate, not a formal export/restore protocol; the public checksum detects only unrecomputed damage and is not authenticity proof; UX is semantic contract walk-through without final UI.

| Test | Result | Priority | Recorded assertions | Evidence |
|---|---|---|---:|---|
| T-ARCH | PASS | P0 | 0 | `architecture_conformance.md` |
| T-DATA | PASS | P0 | 0 | `data_gate_manifest.md` |
| T-DEL | PASS | P0 | 0 | `revocation_delete_e2e.json` |
| T-DEL-OLD-PACKAGE-CONTROLS | PASS | P0 | 17 | `revocation_delete_e2e.json` |
| T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION | PASS | P0 | 6 | `identity_trace.json` |
| T-DERIVATION-GENERATION-BINDING | PASS | P0 | 10 | `identity_trace.json` |
| T-EXPORT | PASS | P0 | 0 | `ux_export_report.md` |
| T-EXPORT-ALL-STATE-PROJECT-CLOSURE | PASS | P0 | 12 | `ux_export_report.md` |
| T-EXPORT-PROJECT-CLOSURE | PASS | P0 | 12 | `ux_export_report.md` |
| T-GATE | PASS | P0 | 0 | `consumption_gate.json` |
| T-GATE-AUTH-CONTEXT | PASS | P0 | 12 | `consumption_gate.json` |
| T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS | PASS | P0 | 14 | `consumption_gate.json` |
| T-ID | PASS | P0 | 0 | `identity_trace.json` |
| T-ID-CONFIRMATION-REGRESSION | PASS | P0 | 10 | `identity_trace.json` |
| T-IPC-OFF | PASS | P0 | 0 | `tauri_ipc_matrix.json` |
| T-OFF | PASS | P0 | 0 | `default_off_matrix.json` |
| T-RESTORE-AUTHORITATIVE-CURRENT-GATE | PASS | P0 | 3 | `revocation_delete_e2e.json` |
| T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION | PASS | P0 | 7 | `revocation_delete_e2e.json` |
| T-SAVE | PASS | P0 | 0 | `durability_report.json` |
| T-SAVE-CRASH-BOUNDARY | PASS | P1 | 11 | `durability_report.json` |
| T-SCOPE | PASS | P0 | 0 | `scope_matrix.md` |
| T-UX | PASS | P0 | 0 | `ux_export_report.md` |
| T-WRITE-GATES-FEEDBACK-AND-LINK | PASS | P0 | 22 | `consumption_gate.json` |

## Evidence files

- `test_results.json`: machine-readable result and environment.
- `test_run.log`: raw unittest output.
- `regression_assertions.json`: regression assertion names, actual values, expected values and pass flags.
- `snapshot_manifest.json`: per-file SHA-256 list and combined content snapshot identifier.
- `scope_matrix.md`: H1 scope proof.
- `identity_trace.json`: H2 identity, complete Derivation evidence and generation binding trace.
- `durability_report.json`: H3 authoritative-save and process-kill boundary evidence.
- `consumption_gate.json`: H4 explicit-context, write-entry and ambiguous-Authorization fail-closed matrix.
- `revocation_delete_e2e.json`: H5 authoritative restore projection and no-revival evidence.
- `tauri_ipc_matrix.json`: H6 closed-state evidence.
- `data_gate_manifest.md`: H7 synthetic-data scan.
- `default_off_matrix.json`: H8 default-off negative matrix.
- `ux_export_report.md`: H9 state/export/restore and Project closure evidence.
- `architecture_conformance.md`: frozen architecture contract check.

Machine-readable assertions and raw logs are authoritative for this run. This manifest is evidence, not PM Review, acceptance, capability enablement, a freeze, or Stage/Gate 5 advancement.
