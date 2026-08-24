# LIFEOS-P3-072 controlled sandbox export

Synthetic-only capability package. The module has an in-memory SQLite state
machine and writes a JSON export only after exact `CONFIRM` bound to a current
preview token. Each success creates a new directory using `tempfile.mkdtemp`;
the one output file is atomically published without overwriting a destination.

Run:

```bash
python3 scripts/run_tests.py
```

No user path, Vault, Tauri/IPC, network, cloud, sync, real database,
multi-device, L3, or external-user capability is present or permitted.
