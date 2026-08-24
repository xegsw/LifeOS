# LIFEOS-P3-079 — 合成本地 MVP 整合闭环

仅处理操作者输入的非敏感测试文本与调用方指定的 task-local SQLite。没有真实用户数据、真实路径、网络、云、AI 消费、文件导出、Tauri/IPC、Vault、同步、多设备、L3 或外部用户通道。

## CLI 示例

```bash
python3 scripts/operator_cli.py --db /tmp/p3-079.sqlite save --text '非敏感测试文本' --key demo-save --confirmation CONFIRM
python3 scripts/operator_cli.py --db /tmp/p3-079.sqlite permission --decision grant --expires-at-ms 9999999999999 --key demo-grant --confirmation CONFIRM
```

恢复预览与确认均需要记录 ID、来源、版本和 `CONFIRM`。唯一精确 grant 的成功结果只会是 `allowed_local_synthetic`；默认、歧义、过期、撤回、deny、错误确认和绑定不匹配都阻断。

## 复跑

```bash
python3 scripts/run_self_check.py
python3 scripts/make_manifest.py
```
