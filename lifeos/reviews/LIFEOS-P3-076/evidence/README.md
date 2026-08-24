# P3-076 独立复评 Evidence

## 复跑

```bash
python3 lifeos/reviews/LIFEOS-P3-076/evidence/independent_runner.py
```

该命令会在系统临时目录复制 P3-075 候选目录，忽略候选 `runtime/`，以新的非敏感文本及新幂等键调用其 CLI；临时副本在退出时删除。它不会导入、调用或复制 `tests/test_runtime.py` 或 `scripts/run_self_check.py`。未知项目恢复没有 CLI 参数，因此以单独的最小公开运行时接口调用补充覆盖；不使用候选测试文件。

## 验收 → 独立反例 → Evidence

| 验收点 | 独立反例 | Evidence 键 |
| --- | --- | --- |
| 显式输入、保存与下一步确认 | 首次 CLI 正路径 | `first_explicit_confirmed_submission` |
| 幂等与关闭重开 | 同键重复、SQLite 新连接读取 | `idempotent_repeat`、`close_reopen_persistence` |
| 空输入和确认缺失 fail-closed | 空文本、缺保存确认、缺下一步确认 | `empty_input_fail_closed`、`missing_save_confirmation_fail_closed`、`missing_next_step_confirmation_blocked` |
| 冲突和提交前失败 | 同键不同文本、注入 pre-commit failure | `same_key_different_text_rejected_without_overwrite`、`precommit_failure_atomic_rollback` |
| 受控项目恢复 | unknown project | `unknown_project_restore_rejected` |
| 禁止能力关闭 | 源码 URL／网络导入与边界声明扫描 | `prohibited_external_channels_static_closed` |
| Evidence 与历史资产保全 | 临时副本与原件 hash、复评前后 hash | `candidate_copy_matches_original_hash`、`historical_assets_preserved` |
| 执行侧 Manifest 完整性 | Manifest 所列每个 SHA-256 与当前文件核对 | `candidate_execution_manifest_matches_current_hash` |

逐项状态在 `independent_results.json`，简明日志在 `independent_runner.log`。所有输入和输出限于非敏感测试文本、任务临时副本和 task-local SQLite；不接触个人数据、真实路径／文件、真实 DB、Tauri/IPC、网络、云、导出、Vault、同步、多设备、L3 或外部用户。
