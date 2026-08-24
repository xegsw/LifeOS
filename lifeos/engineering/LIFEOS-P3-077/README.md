# LIFEOS-P3-077

Synthetic-only, task-local SQLite permission settings exercise. It accepts only
the fixed `BOUNDARY` context in `src/permission_runtime.py`; an allow response
is `allowed_local_synthetic` and always has `external_action: none`.

Run the clean-copy self-check:

```sh
python3 lifeos/engineering/LIFEOS-P3-077/scripts/run_self_check.py
```

Operator preview (the CLI only creates `runtime/<safe-run-id>.sqlite` here):

```sh
python3 lifeos/engineering/LIFEOS-P3-077/scripts/permission_cli.py preview
```

No real data, paths/files, network, cloud/third parties, Tauri/IPC, export,
Vault, sync, multi-device, L3, or external-user capability is implemented.
