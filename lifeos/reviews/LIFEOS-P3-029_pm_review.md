# LIFEOS-P3-029｜PM Review｜SQL migration 设计 / 合同测试任务

## 1. 验收结论

- 验收结论：Accepted / Pass with Conditions
- 资产状态：Accepted but Not Frozen
- 是否允许进入下一步：Yes，用户确认采纳后可启动 P3-030 SQL migration 设计 / 合同测试独立评审
- 是否允许直接进入候选 SQL migration 编写：No
- 是否允许进入下一阶段：No
- 是否关闭 R-0040：No，保持 Open / Conditional
- 是否冻结 Schema / API：No
- 是否启用真实能力：No

## 2. 验收依据

- 任务卡：`lifeos/tasks/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-029_LIFEOS-P3-029_sql_migration_design_and_contract_tests_local_precheck.md`
- 直接依赖：P3-025、P3-027、P3-028、P3-024、D-0190、D-0191、R-0040

本地预检状态为 Skipped / Local Model Unavailable，原因是当前沙盒无法调用局域网模型；该结果不作为 PM 验收依据。

## 3. 范围核对

P3-029 交付物符合任务边界：

- 已产出候选 migration 创建顺序、权威表分层、CHECK / trigger / partial index / transaction guard 分责。
- 已覆盖 ContentIdentity、SemanticObject、DerivationInput、Feedback / retract、Authorization strict_intersection、Tombstone、Outbox、Audit、FTS 等关键数据与信任边界。
- 已承接 P3-028 的 3 个 P2 清洁项：`semantic_object` 聚合 / 拆表门、retract-of-retract 与 dependency trigger、`strict_intersection` 明确定义。
- 已形成四 invoke / DTO 合同测试草案，以及 DB / IPC P0、P1、P2 合同测试清单。
- 已明确非实现 / 非冻结声明：未创建 `.sql` 文件、未写或执行 migration、未连接数据库、未改代码、未运行 Tauri、未启用真实能力、未关闭 R-0040、未冻结 Schema / API。

未发现 P0 / P1 级范围越权。

## 4. 关卡判断

| 关卡 | PM 判断 | 说明 |
|---|---|---|
| Gate 2 数据与来源 | Pass with Conditions | 设计层清楚区分用户原文、外部来源、AI 派生、反馈、授权和删除语义；但仍需独立评审攻击 SQLite 约束表达与跨表 trigger 缺口 |
| Gate 3 AI 权限与信任 | Pass with Conditions | ContentIdentity、Derivation、授权交集、撤回链、tombstone 和四 invoke 均按 fail closed 表达；真实 IPC / capability 仍未验证 |
| Gate 4 技术可行性 | Pass with Conditions | migration 顺序、回滚、索引、触发器、事务 guard 和合同测试具备后续实现输入价值；但无可执行 migration、无 DB 实测、无耐久或性能证据 |

## 5. 条件与后续边界

P3-029 可作为独立评审输入，但后续必须遵守：

1. P3-030 独立评审通过前，不得启动候选 SQL migration 编写。
2. 即使 P3-030 通过，候选 SQL migration 编写也必须另立任务卡，并由 PM / 用户明确授权创建 `.sql` 文件和运行合成空库测试。
3. `semantic_object` 继续聚合仅作为当前候选口径；Decision / Action 任一新增第 6 个持久化顶层专属字段，必须暂停候选 SQL 编写并重新评估拆表。
4. retract-of-retract、跨 target dependency trigger 与 `strict_intersection` 定义必须作为 P3-030 重点攻击点。
5. P3-029 不改变技术架构 V0.1 冻结合同，不冻结 Schema / API、Tauri capability、导出格式、生产 SLA 或工程基线。
6. R-0040 不关闭、不拆分；真实 Tauri / IPC、真实 Vault、真实数据、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 与外部用户仍默认关闭。

## 6. 风险状态

- R-0040：不变，Open / Conditional。
- 新增风险：无。
- RISK_LOG：本次不更新。

## 7. Agent 适配度记录

- 本任务实际执行 Agent：Codex 技术 / 数据设计会话
- 与任务类型匹配度：High
- 适合后续任务：候选 SQL migration 编写、合同测试实现、受控 DB 空库验证、evidence 整理
- 不建议直接承担：P3-029 自身独立评审、Schema / API 冻结判断、R-0040 关闭判断
- 分派建议：下一步 P3-030 应交给 WorkBuddy 独立评审会话，避免执行者自证

## 8. PM 结论

PM 接受 P3-029 作为 SQL migration 设计 / 合同测试草案输入，状态更新为 Accepted / Pass with Conditions；对应资产为 Accepted but Not Frozen。

建议用户确认采纳 P3-029 后，启动 P3-030 SQL migration 设计 / 合同测试独立评审。P3-030 未启动前，不得写 `.sql`、不得执行 migration、不得安装 / 配置 / 运行真实 Tauri、不得启用真实能力、不得冻结 Schema / API、不得关闭 R-0040 或进入下一阶段。
