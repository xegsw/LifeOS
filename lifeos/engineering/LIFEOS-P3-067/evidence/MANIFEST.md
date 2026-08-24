# LIFEOS-P3-067 Evidence Manifest

仅包含任务目录内 Python 标准库与 SQLite 的非敏感合成演练证据。所有外部能力关闭；不构成真实恢复、备份、导出、权限、工程基线或 Stage 4 证明。

| 文件 | SHA-256 |
|---|---|
| `test_results.json` | `5d520f09338d72d25a7d27b24ddb152339e57774d08a3d76578756fef6aa082a` |
| `test_run.log` | `faf915d31bec257be4270b5b77c86ebf3409f96f2ab35b9d48e492c0bba9ec87` |
| `cross_restart_audit_snapshots.json` | `7b17e6d20e2eafcfda800f3e82b931d60a91914eaf98e85368de8e5ee6a66203` |
| `operator_chain_ready_preview.json` | `887872d281c634e2a2a6e553eae855c16779db1914eabc5cba040bb928095667` |
| `operator_chain_first_confirm.json` | `6e163ef5054d456acfe63f26678a697fda628579aaf9c4e586014128b280a70e` |
| `operator_chain_idempotent.json` | `f1405ba6122b336b4f3dd3e1daa98d205815328cfcb2bddd6d7dd2bf675fedc9` |
| `operator_cli_chain.json` | `f8121095f13f48add2c2319ba52ccced51d77d1160f152541c7be332078115e1` |

Rework canonical CLI chain：以当前 Manifest 列出的 `operator_chain_*` 与 `operator_cli_chain.json` 为准；它们证明同一干净 task-local run 先 ready preview、再首次 CONFIRM 恢复、最后幂等回执。`cross_restart_audit_snapshots.json` 证明 `recovery_not_confirmed` 与 `recovery_blocked` 在关闭并重开合成 SQLite 后仍保留且顺序可核验。先前未列入本 Manifest 的 CLI Evidence 保留为历史，不作为本次 Rework 主证据。

边界静态检查：代码和结果明确声明 network、Tauri/IPC、Vault、真实路径、导出、cloud、sync、多设备、L3、外部用户均为 disabled/not_used；不存在网络库、目录扫描或外部动作实现。
