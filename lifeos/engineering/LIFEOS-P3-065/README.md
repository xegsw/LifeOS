# LIFEOS-P3-065 受控基础权限设置

仅使用 Python 标准库、SQLite 与合成枚举值；不接受路径或真实身份。默认拒绝，且只能在操作者输入 `CONFIRM` 后创建授予／拒绝设置，撤回要求 `REVOKE`。

```sh
./scripts/run_tests.sh
python3 scripts/permission_cli.py preview --synthetic-only --category synthetic_note --purpose local_recovery --location local_sqlite --processor local_rules --expires-at-ms 5000
```

“allow”仅返回合成 SQLite 中的本地决定，绝不读取或发送内容、调用 AI、使用网络，或产生外部动作。此资产不是生产权限系统、真实 AI 授权、Tauri/IPC 证明、风险关闭或 Stage 4 准入。

冲突语义为 fail-closed：同一精确绑定的当前有效 `deny` 优先于任意 `grant`；没有 deny 时，只有一项有效 grant 才能 allow，多个并列 grant 也会拒绝。
