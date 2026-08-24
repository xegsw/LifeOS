# LIFEOS-P3-067 合成恢复与失败披露演练

这是隔离、一次性的防御性工程演练。它只使用 Python 标准库、任务目录内 SQLite 文件和非敏感合成文本；不读取或扫描任务目录外路径。

## 操作者 CLI

先以 `LIFEOS_SYNTHETIC_ONLY=1` 预览受控合成计划，再将 `--confirm CONFIRM` 明确加入命令后执行。CLI 不接受数据库或任意文件路径；`--run-id` 仅允许字母、数字与连字符，并固定映射到本目录 `runtime/`。

```sh
LIFEOS_SYNTHETIC_ONLY=1 python3 scripts/recovery_cli.py --run-id demo --record-id synthetic-1 --source synthetic-source --version 1
LIFEOS_SYNTHETIC_ONLY=1 python3 scripts/recovery_cli.py --run-id demo --record-id synthetic-1 --source synthetic-source --version 1 --confirm CONFIRM
```

`saved` 仅在 SQLite 事务提交返回后出现。故障、非法输入、未知计划、来源/版本不匹配、撤回或 tombstone 都显示可见失败/受阻原因，且绝不复活或消费目标。

运行 `scripts/run_tests.sh` 会产生任务内结构化结果、日志、快照与 hash Manifest。每次运行使用新的、受限的任务内 `run-id`：脚本先建立一个已提交且尚未恢复的合成记录，再连续保存 `ready preview`、首次 `CONFIRM` 恢复和后续幂等回执。`evidence/operator_cli_chain.json` 对这三段 CLI 输出做端到端断言；当前 Manifest 中的 `operator_chain_*` 文件是本 Rework 的主 Evidence。

## 固定关闭态

网络、Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、L3、外部用户与外部动作均关闭。本目录不是正式恢复、备份、导出、真实权限、真实 MVP、工程基线或 Stage 4 准入资产。
