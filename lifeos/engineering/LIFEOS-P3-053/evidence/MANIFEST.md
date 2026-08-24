# LIFEOS-P3-053 Engineering Evidence Manifest

## 范围与边界

- 任务：`LIFEOS-P3-053`，仅修复 P3-052 的两条 Outbox P1 与两条 Authorization lifecycle 初始值 P2。
- 执行边界：候选 SQL、合同测试 runner、合成 SQLite；未连接真实数据库、Vault、Tauri/IPC、云服务或外部系统。
- 历史输入：P3-052 任务、独立评审、PM Review、独立 runner 与攻击计划均只读；其本次读取 hash 见 `read_only_input_hashes.txt`。
- 本清单不构成 R-0048 风险关闭、R-0049 变更、任何资产冻结、工程基线恢复或阶段推进。

## 候选整改

1. `authorization_state_change` Outbox INSERT 现要求匹配 canonical lifecycle command、terminal Authorization、唯一 correlation AuditEntry、Submission、subject generation、target payload 与 canonical id/idempotency；伪造 lifecycle 行不能进入 claim/complete 路径。
2. `outbox_retention_binding` 保存唯一 `lifecycle_correlation_id`；删除 lifecycle terminal job 后，原 job id 或 correlation/idempotency 不能重新用于 lifecycle 或 generic job。普通 generic terminal job 的清理路径保留。
3. Authorization INSERT / INSERT OR REPLACE 强制 `generation=1`，非 revoked 初始状态不得携带 `revoked_at_ms`；activation 再次校验两项约束。三种合法 terminal transition 的 generation/time 配对仍由原 lifecycle command 合同验证。

## 回归命令与结果

执行命令：

```sh
python3 -B lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py \
  --results-json lifeos/engineering/LIFEOS-P3-053/evidence/p3_031_regression_results.json \
  --matrix-results-json lifeos/engineering/LIFEOS-P3-053/evidence/lifecycle_matrix_results.json
```

| 验证项 | 结果 |
| --- | --- |
| P3-031 全量回归 | 74 PASS / 0 FAIL / 0 Not Implemented；P0=18、P1=29、P2=27 |
| P3-052 四条迁移反例 | `P3-052-P1-01`、`P3-052-P1-02`、`P3-052-P2-01`、`P3-052-P2-02` 均 PASS |
| PM-CE-01 至 PM-CE-05 | 已纳入全量与八配置矩阵，均 PASS |
| 事务原子性 | `AC-14-atomic-lifecycle` 与 `AC-16-rollback-on-evidence-conflict` 均纳入八配置矩阵并 PASS |
| 八配置矩阵 | 11 个目标用例 × memory/file × FK OFF/ON × recursive triggers OFF/ON = 88 PASS / 0 FAIL |
| 文件模式检查 | 72 个持久化 synthetic SQLite 文件均在 close/reopen 后通过 `integrity_check=ok`、`quick_check=ok`、空 `foreign_key_check` |

## 文件索引

- `p3_031_regression_run.log`：可读运行摘要。
- `p3_031_regression_results.json`：74 条全量合同测试的逐项结果。
- `lifecycle_matrix_results.json`：88 个八配置结果与文件模式检查。
- `candidate_and_runner_hashes.txt`：整改后候选 SQL 与 runner 的 SHA-256。
- `read_only_input_hashes.txt`：本任务读取的 P3-052 只读输入 SHA-256。

## 解释限制

以上仅证明当前候选 SQL 在本地合成 SQLite 的受控测试范围内通过。仍必须由未参与本任务执行的全新隔离会话做独立复评；在 PM 验收和后续独立复评前，R-0048 继续 Open，R-0049 不变，资产保持 Not Frozen。
