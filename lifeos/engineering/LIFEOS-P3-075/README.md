# LIFEOS-P3-075 controlled local runtime

Only run this with non-sensitive test text. It uses a task-local SQLite database under `runtime/`; it has no network, cloud, Tauri/IPC, filesystem export, Vault, sync, multi-device, L3, or external-user channel.

Example:

```bash
python3 scripts/runtime_cli.py --non-sensitive-test-only --text "测试文本" --idempotency-key "test-001" --confirm-save --next-step "人工确认下一步" --confirm-next-step
```

Reproduce the package self-check:

```bash
python3 scripts/run_self_check.py
python3 scripts/make_manifest.py
```
