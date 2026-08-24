# LIFEOS-P3-104 Rework 1/2 Evidence Manifest

## Result

- PM findings addressed: `PM-P3-104-CE-01` PASS candidate; `PM-P3-104-EV-01` PASS candidate.
- Existing static: 44/44 PASS.
- Rework static: 19/19 PASS.
- Rust unit: 7/7 PASS.
- Clean offline actual-app bundle/replay: PASS.
- Actual dangling-final startup: rejected before process/window/success UI; link, missing target and sentinel preserved; residue 0.
- Counts: P0=0, P1=0, P2=0, Unknown=0, Not Implemented=0.

The Manifest does not hash itself. The initial Engineering Evidence and PM Evidence remain read-only. `offline_actual_app_replay.log` is retained first-run history; `offline_actual_app_replay_pass.log` is the authoritative run after adding explicit no-process/no-success-UI disclosures.

## SHA-256 inventory

```text
e0550e5c69d9ed3b958d8d064f0448edcff02a6067196adf8da5d770755e9f43  REWORK_REPORT.md
39d4bec6d98c20ac857e2f15ff3883e4b6fea2b773f3b2213aab7140733c49af  cargo_test.log
ffde8159e848d49a77ba4f73ed12efe381b0e96131db86c1614a2ce700cff8d8  offline_actual_app_replay.log
3c986279ed51a4b33632eace4f76e0f895e6f5fc4c1cdc60f6ee7085a5bb10ab  offline_actual_app_replay_pass.log
720baf06eca62e7c55bafd7fbee7f3d5c39258e873229e4a4ae3275b68af42fa  rework_results.json
b63f91f570291370c0f40a99ccf9786a3367c38792005f2a5384f42b3d9985c4  results.json
1c1b10364e6e748f20e051f934f981d72fa2b2a8ece6a1e10e00cc098d083e4b  static_results.json
```

## Current candidate and runner hashes

```text
430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1  ../../../Cargo.lock
cf82f88faa7b80d5818f85d5f23e87dbae228ac0314b9b8642be8ef55157db73  ../../../scripts/offline_actual_app_replay.sh
0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529  ../../../src/runtime.rs
944161fa4a43a83707413cf28eae75a5814df1450a051533c9fb3065dc8363f1  ../../../tests/rework_checks.py
5e245968d4bab7d29c503bdf120292297d5b631ba4c3e7529b0f40422be44bd8  ../../../tests/static_checks.py
```

## Immutable governance and prior Evidence hashes

```text
861d0be5bc40d1ebac41cc8b5a695d154d3bf073407b5fc6e3e85e42532a3f46  ../../MANIFEST.md
dbce89510ea161181b9e997579ff92da0019bb93a2e9857ae415ba5484faf9c6  ../../../../../reviews/LIFEOS-P3-104/pm_evidence/initial/MANIFEST.md
da83f2adbe4aff8449d153c9eb32a6000a2b9dce54c24a218ab4e89b2b0d8aba  ../../../../../reviews/LIFEOS-P3-104_pm_review.md
2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b  ../../../../../tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration_acceptance_basis_freeze.md
```
