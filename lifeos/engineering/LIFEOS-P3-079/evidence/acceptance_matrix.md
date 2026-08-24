# P3-079 验收标准 → 测试 → Evidence 矩阵

| 验收标准 | 可运行测试／演练 | Evidence |
|---|---|---|
| 确认保存、失败披露与原子清理 | T01–T05 | `self_check_results.json`, `self_check.log` |
| 来源、状态、权限预览、仅本地允许 | T02、T07、CLI 链 | `operator_cli_chain.json`, `operator_snapshot.json` |
| 默认拒绝、精确 grant、deny 优先及 fail-closed | T06–T11 | `self_check_results.json` |
| 审计及跨重启追溯 | T14–T15 | `self_check_results.json`, `operator_snapshot.json` |
| 显式恢复、撤回阻断与幂等 | T12–T13、CLI 链 | `operator_cli_chain.json`, `operator_snapshot.json` |
| 干净临时副本、结构化结果、日志、快照、hash、Manifest | `run_self_check.py` | `self_check_results.json`, `self_check.log`, `operator_snapshot.json`, `MANIFEST.md` |
| 历史资产只读与静态关闭态 | `run_self_check.py` 静态检查 | `historical_input_hashes.json`, `self_check_results.json` |

T01–T16 对应 `tests/test_integrated_runtime.py` 中按序命名的测试。所有适用项均已覆盖；不适用项：真实能力演练（任务明确禁止，静态关闭）。
