# LIFEOS-P3-077 Evidence Manifest

## 边界与复跑

- 仅使用 Python 标准库、task-local SQLite 和固定的 `non_sensitive_test_text` 语境。
- 干净副本自检：`python3 lifeos/engineering/LIFEOS-P3-077/scripts/run_self_check.py`
- 结果：**15 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**；退出码 0。
- 自检复制当前工程到系统临时目录后运行；不会写入历史工程、Review 或 Evidence。运行时 SQLite 仅存在于该临时副本（CLI 测试也仅写副本内 `runtime/`）。

## 验收标准 → 测试 → Evidence

| 任务卡标准 | 测试 | Evidence | 结果 |
| --- | --- | --- | --- |
| 默认拒绝；唯一当前 grant + CONFIRM 才允许 | 01、02、09 | `self_check_results.json`、`self_check.log` | PASS |
| deny 优先、歧义／过期／绑定不匹配 fail-closed | 03、04、05、07、08 | 同上 | PASS |
| grant／deny／撤回／拒绝可审计且确认可见 | 06、12 | `snapshot.json`、日志 | PASS |
| 撤回、重复命令、冲突与关闭重开 | 06、10、11、15 | 结果、日志、快照 | PASS |
| 原子失败、无半成品、失败披露 | 14 | 结果、日志、快照 | PASS |
| 操作者可查看受控目的／位置／处理者／边界 | 13 | 结果、日志 | PASS |
| 禁止通道保持关闭 | 源码静态核对：仅 `sqlite3`、`time`、`uuid`、`pathlib`；无网络／云／Tauri／IPC／Vault／导出／同步等导入或实现 | README、源码 hash | PASS |

## 历史只读与关闭态核对

- P3-065／P3-066、P3-075／P3-076 的交付物、Review 与 Manifest 仅作只读语义输入；本任务未写入其目录。提交前的当前 hash 核对见 `historical_input_hashes.json`。
- 未实现真实数据、真实 DB／路径／文件、Vault、Tauri/IPC、网络、云／第三方、AI 消费、导出、同步、多设备、L3 或外部用户。`allowed_local_synthetic` 固定伴随 `external_action: none` 与 `ai_consumption: none`。

## SHA-256

| 文件 | SHA-256 |
| --- | --- |
| `src/permission_runtime.py` | `1aca35f29e3a09505f7b825a33e5f386932aae946817da4bc8d91ca9615df9fa` |
| `scripts/permission_cli.py` | `8bea310d2eda9137c5387e571dd1ff7083f3e6f7771e3fec1c7eec4b0413d6d2` |
| `scripts/run_self_check.py` | `4ea17642fe89c0e0843ffbed7f62a8df140d3c79f2da64eff96a2aad7ce3cb4a` |
| `tests/test_permission_runtime.py` | `f513bbdc973c7f0fdabaac522b0b717c6606f7a294607ac7bca219c8fb81e48f` |
| `README.md` | `4717603999824f097ac9ede6a1d895686af763d0d64252286366d30a24fc395a` |
| `evidence/self_check_results.json` | `5cf22c45b76fe2ece781352b198ac794710a1954eeb52289b8b82bf681f97b5b` |
| `evidence/self_check.log` | `a3a2e7c1f87930e80187c0c045314cf699ea195d94ce2a5d8dc2cce2b3265d9f` |
| `evidence/snapshot.json` | `29cfaf5fd18825fb0735c0192eca77e40e7dbe544822cde4e0e79a6a78398663` |
