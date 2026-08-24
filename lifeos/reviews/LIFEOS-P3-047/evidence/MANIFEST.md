# LIFEOS-P3-047 PM Counterexample Evidence Manifest

## 结论

- P3-047 原专项统计与既有 PM 隔离复跑可复现：P3-047 为 297 PASS / 0 FAIL，P3-031 当前全量为 69 PASS / 0 FAIL，总入口退出码 0，P3-046 只读失败基线保持不变。
- 上述统计未覆盖“先创建普通 Tombstone，再 UPDATE 改绑为 Authorization Tombstone”的路径。
- PM-CE-06 在 memory / file SQLite、`foreign_keys` ON / OFF、`recursive_triggers` ON / OFF 共 8 个配置中稳定得到 0 PASS / 8 BYPASS，P2 bypass=8，反例入口退出码 1。
- 每个实例都可把 `artifact/placeholder` 改绑为 `authorization/auth1`，并同时改写 `generation`、`command_id`、`reason_code` 与 `blocked_at_ms`；数据库未拒绝，且 `integrity_check=ok`、`foreign_key_check=[]`。
- 本 evidence 支持 PM 将 P3-047 判为 `Accepted / PM Adjusted to Rework`；不关闭风险、不冻结资产、不恢复工程基线、不启用真实能力、不允许进入下一阶段。

## 根因与任务合同映射

- 当前 trigger：`authorization_tombstone_control_envelope_immutable`。
- 静态根因：trigger 仅在 `OLD.subject_type='authorization'` 时拦截包络更新；普通 Tombstone 更新为 Authorization 时，旧行不满足该条件。
- 合同映射：P3-047 PM-CE-04 明确要求 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 自 INSERT 起不可变并禁止改绑。
- 级别：PM-CE-06 / P2。该问题不直接恢复 active Authorization，但允许事后伪造清理主体、generation、命令、原因和时间，破坏终态历史与 cleanup 证据可信度。

## 执行命令与退出合同

```bash
python3 lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py
```

- 实际退出码：`1`。
- 退出含义：存在至少一个稳定复现的合同旁路。
- 数据范围：仅合成 SQLite；文件后端位于脚本临时目录并在执行后清理。
- 未连接或修改真实 DB、Vault、用户文件、Tauri/IPC、网络、云、第三方模型、同步、多设备、L3 或外部用户。

## 配置矩阵

| 后端 | foreign_keys | recursive_triggers | 结果 |
|---|---|---|---|
| memory | ON | ON | BYPASS |
| memory | ON | OFF | BYPASS |
| memory | OFF | ON | BYPASS |
| memory | OFF | OFF | BYPASS |
| file | ON | ON | BYPASS |
| file | ON | OFF | BYPASS |
| file | OFF | ON | BYPASS |
| file | OFF | OFF | BYPASS |

汇总：0 PASS / 8 BYPASS；P2 bypass=8。

## 文件与 SHA-256

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py` | PM-CE-06 合成反例脚本 | `54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50` |
| `lifeos/reviews/LIFEOS-P3-047/evidence/counterexample_results.json` | 8 配置结构化结果 | `f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5` |
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | 被攻击的当前候选 SQL | `7000ca397db8c737681bee1edff05caefcebffb1555f30697b61feb4a0df2854` |

## PM 边界

- P3-047 的 PM-CE-01、PM-CE-02、PM-CE-03、PM-CE-05 及其现有回归可作为 R-0048 的候选整改证据，但尚未经过本轮要求的隔离独立复评；R-0048 只可保持开启并进入 Remediation Candidate，不得关闭。
- PM-CE-04 因 PM-CE-06 未完整关闭；R-0049 必须保持 `Open / Rework`。
- P3-046 原报告、runner、原失败 Evidence 与 PM 原反例均未修改。
- 本轮不更新 `FREEZE_STATUS.md`，不创建或启动 P3-048，等待用户确认最终 PM 结论。
