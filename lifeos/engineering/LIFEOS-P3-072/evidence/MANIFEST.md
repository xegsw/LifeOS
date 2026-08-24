# LIFEOS-P3-072 Evidence Manifest

All evidence is local to the P3-072 isolated engineering directory. Runtime
exports use only a newly created system temporary sandbox and non-sensitive
synthetic data; no temporary export file is retained as project evidence.

- `src/sandbox_export.py`: `5afb438bb50f92b9a7892f235429129a41215dd66d6022d3b09e96406e4412fa`
- `tests/test_sandbox_export.py`: `f9106f212d635f7b7de5e995ead09e9f3bffbb6e50da04a9c0aca8a9838aed84`
- `scripts/run_tests.py`: `3c1775d6ed0167963a7dc0c348887f00682678124dab95db763285d38a846590`
- `scripts/make_evidence.py`: `b79baa65782a69c44ea3e7899d7b005b32e1692934e7360fd7d0ef3efb80a24d`
- `evidence/test_results.json`: `8cd985c9c303f601fbe4c3e36ce0eebb9fdc8f7cbe63384b3e51b5e2969b522d`
- `evidence/export_receipt.json`: `6eb8d9c2a83549106d9bbb1e70f061b62dd6e8cbeaf5f36bae8eb1b03857bcbf`

## Verification summary

- `python3 scripts/run_tests.py`: 7 PASS / 0 FAIL.
- `export_receipt.json`: one exact-confirmation export to a new system
  temporary sandbox; receipt hashes match the generated content and the
  temporary sandbox was removed after capture.
- Negative coverage: missing/mismatched confirmation or preview token,
  source/version/unknown/conflict/revoked/tombstoned state, repeat export, and
  injected write failure all block and audit; write failure leaves zero visible
  output.
- Static coverage: no network client, Tauri/IPC, Vault, cloud, subprocess, or
  real-database implementation/import exists. The only persistent state is
  in-memory SQLite; the only filesystem target is a fresh `mkdtemp` sandbox.
