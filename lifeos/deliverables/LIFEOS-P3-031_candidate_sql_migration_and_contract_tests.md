# LIFEOS-P3-031｜候选 SQL migration 与合成空库合同测试工程报告

## 1. 任务摘要

- **[已验证事实]** 已在授权目录创建单一候选 SQLite migration、合同测试、复跑脚本和 evidence；只使用合成空库 / 合成数据。
- **[已验证事实]** 最终复跑 33 PASS / 0 FAIL / 0 Not Implemented：P0 18/18、P1 7/7、P2 8/8；验证命令退出码 0，任一 FAIL（特别是 P0 FAIL）会非零退出。
- **[已验证事实]** migration 可在 SQLite 3.51.0 空库中原子创建；故障注入在 meta 写入前中断后，rollback 不残留业务表、索引或 trigger。
- **[推断]** P3-030 的两项 P1 和三项 P2 已在候选实现层形成可复跑的关闭候选，但 R-0043、R-0044 仍须 PM 验收且不得由本会话关闭。
- **[建议]** PM 验收后可决定是否启动隔离的 P3-032 独立工程评审；本会话不自行启动。

## 2. 修改范围

实际创建：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
- 本报告。

未修改 P3-009、P3-024/P3-025/P3-027/P3-029/P3-030、Stitch 或任何 PM 账本。

## 3. 候选 migration

候选 SQL 路径：`lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`。

SQL 以 `PRAGMA foreign_keys=ON` 与 `BEGIN IMMEDIATE` 开始，在同一事务创建 migration meta、Project/Source/Artifact/ArtifactVersion/ContentIdentity、SemanticObject、Authorization、Derivation、Feedback、Link、Tombstone、Audit、Submission、Outbox、FTS/search projection 及相关 CHECK、FK、unique/partial index 与 trigger，最后写入 `schema_migration_meta` 并提交。文件首部和 meta 均标明 candidate-only。

主要 DB 强制包括：版本与 Feedback 追加不可变；Artifact/Semantic current pointer ownership；ContentIdentity 条件身份；DerivationInput exact-one、type-column 一致性及显式 `input_type` enum；Derivation/Authorization 激活完整性；Feedback 线性 retract 与同 target dependency；tombstone generation 单调性与 cleanup status 转换；Outbox/idempotency 唯一性。

仍属于应用事务 guard、没有伪装为 DB 单独可证的部分包括：Authorization `strict_intersection`、完整权威消费门、进入 `active_blocked` 前的全入口阻断证明、恢复评估、FTS post-filter、详情 token。测试脚本为这些合同提供纯函数或受控 SQL 组合验证。

## 4. 测试与复跑

复跑命令：

```bash
lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh
```

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 7 | 0 | 0 |
| P2 | 8 | 0 | 0 |
| **Total** | **33** | **0** | **0** |

DB-P0-01 至 DB-P0-15 和 IPC-P0-01 至 IPC-P0-03 全部实现。IPC 测试仅覆盖纯 DTO parser：四 invoke 封闭 action、精确字段、contract version、跨 variant 拒绝和 destruct 必填项；没有真实 Tauri handler、capability 或 IPC。

未实现或降级测试：**无 Not Implemented**。其中 DB-P0-07/08、DB-P0-12、IPC-P0-*、CT-P1-05、CT-P2-02/03/04/05 属于合同/事务 guard 层测试，不得外推为真实进程、真实 IPC 或真实文件能力证据。

## 5. P3-030 条件处理

### 两项 P1

1. **R-0043 / P1-1**：新增 `tombstone_generation_monotonic` BEFORE UPDATE trigger。DB-P0-15 验证 generation 5→4 被拒且原值仍为 5；DB-P0-09、CT-P2-07 同时覆盖 expected generation CAS 和 stale upgrade。
2. **R-0044 / P1-2**：新增 `authorization_activation_complete` trigger 与 CT-P1-07。0 scope、0 action、incomplete policy、旧版本未 superseded 四类均拒绝；旧版本显式 superseded 后新版本才可 active。

因此两项风险可标记为“**候选实现层、待 PM 验收的关闭候选**”，不能在本任务中改写 RISK_LOG 或宣布 Closed。

### 三项 P2

1. DerivationInput 增加独立 enum CHECK，并由 CT-P2-06 读取实际 schema 验证。
2. CT-P2-07 验证第二次 stale tombstone upgrade 为 0 行、generation 降级由 trigger 拒绝。
3. Tombstone 强制层级已明确：CHECK 负责枚举，trigger 负责转换矩阵，应用事务 guard 负责进入 `active_blocked` 前的全路径证明。cleanup failure/vendor-limited 不允许回退到 accepted；终态不允许倒退。

Decision/Action 仍各 5 个专属顶层字段，没有新增第 6 个字段；CT-P2-05 保留拆表硬门。

## 6. 角色检查点与关卡

- **技术架构负责人 / 数据与领域模型负责人**：候选 SQL 可执行；核心表、约束、索引、trigger 和事务边界均有落点；DB 与事务 guard 分责已显式记录。
- **AI 信任与安全负责人**：用户原文、外部来源、AI 派生、用户反馈、授权和 tombstone 继续分离；deny/unknown fail closed；四 invoke 未滑向真实 handler。
- **QA / Evidence Reviewer**：单一复跑命令、机器可读结果、完整日志、hash 与 evidence 入口已提供；P0 fail 非零退出已由 runner 代码保证。
- Gate 2：**执行 Agent 自审 Pass with Conditions**，待 PM 与独立评审复核 DB 约束旁路。
- Gate 3：**执行 Agent 自审 Pass with Conditions**，待独立评审攻击 Authorization/Feedback/DTO；不构成真实 IPC 通过。
- Gate 4：**执行 Agent 自审 Pass with Conditions**，候选空库执行与原子回滚成立；真实升级、耐久、性能、WAL/backup 和目标平台未验证。

## 7. 剩余风险与 PM 决策

- R-0040 保持 Open / Conditional；本任务没有真实 Tauri / IPC 证据。
- R-0043、R-0044 保持 Open，等待 PM 验收与后续独立工程评审；本报告只提出候选关闭证据。
- migration 只验证空库，不证明已有生产库升级、backup/restore、进程杀死耐久、性能容量或发布 rollback。
- `schema_checksum` 仍为候选标识，生产构建期 checksum 机制未设计或冻结。
- **需 PM 决策**：是否接受 P3-031 交付；是否认定 R-0043/R-0044 达到“进入独立评审的关闭候选”；是否允许另行启动 P3-032。建议允许启动独立工程评审，但不允许直接冻结 Schema/API、关闭风险或启用真实能力。

## 8. Evidence 与非冻结声明

Evidence manifest：`lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`。

本地预检：`lifeos/local_prechecks/LIFEOS-P3-031_LIFEOS-P3-031_candidate_sql_migration_and_contract_tests_local_precheck.md`。状态为 **Skipped / Local Model Unavailable**（connection reset by peer），符合失败降级规则；未把该结果用作工程结论或 PM 验收依据。

本任务不冻结 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线；不关闭 R-0040、R-0043、R-0044；不连接真实 DB/Vault/用户数据；不运行真实 Tauri/IPC；不启用真实文件导出、云/第三方模型、向量、同步、多设备、L3 或外部用户；不进入下一阶段，也不自行启动后续任务。
