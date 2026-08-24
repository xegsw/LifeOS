# LIFEOS-P3-035｜R-0043 / R-0044 / R-0045 风险关闭决策包

## 决策信息

- 任务 ID：LIFEOS-P3-035
- 任务名称：R-0043 / R-0044 / R-0045 风险关闭决策包
- 执行 Agent：WorkBuddy
- 主责角色：风险关闭评估负责人
- 协审角色：数据 / 来源负责人、AI 信任与安全负责人、技术架构负责人、QA / Evidence Reviewer
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 决策包路径：`lifeos/deliverables/LIFEOS-P3-035_r0043_r0044_r0045_risk_closure_decision_package.md`
- 更新时间：2026-08-13

## 执行摘要

1. **[事实]** 独立复跑 P3-031/P3-033 测试套件（临时目录隔离）：35 PASS / 0 FAIL / 0 Not Implemented（P0:18、P1:9、P2:8），退出码 0。源文件和生成文件 SHA-256 hash 全部匹配 MANIFEST。
2. **[事实]** R-0043（Tombstone generation 单调性）：UPDATE 降低 generation 路径已由 `tombstone_generation_monotonic` BEFORE UPDATE trigger 覆盖，DB-P0-15 / CT-P2-07 验证通过。残留 DELETE+INSERT 旁路（P2-2）和 status INSERT 旁路（P2-3）为不同类别攻击或应用层责任。
3. **[事实]** R-0044（Authorization activation completeness）：INSERT 路径由 `authorization_no_direct_active_insert` BEFORE INSERT trigger 封闭（CT-P1-08），UPDATE 路径由 `authorization_activation_complete` BEFORE UPDATE trigger 封闭（CT-P1-07）。15 个反例攻击全部 fail closed。残留 P2-4（子表 DELETE）为审计完整性级别，strict_intersection 运行时仍 fail closed。
4. **[事实]** R-0045（Derivation activation completeness）：INSERT 路径由 `derivation_no_direct_active_insert` BEFORE INSERT trigger 封闭（CT-P1-09），UPDATE 路径由 `derivation_activation_complete` BEFORE UPDATE trigger 封闭（DB-P0-04）。ContentIdentity 二级检查不受影响。无 P1/P2 残留。
5. **[建议]** R-0043 / R-0044 / R-0045 均建议关闭，关闭范围仅限"候选 SQL + 合成空库合同测试 + 当前受控 evidence + 有限 Stage 3 边界"。残留 P2 不阻断关闭，转入后续真实 DB 验证前置任务追踪。
6. **[建议]** PM 和用户确认后可直接更新 RISK_LOG 关闭 R-0043 / R-0044 / R-0045，无需另建关闭执行任务。
7. **[事实]** R-0040（Tauri / IPC 安全风险）必须继续保持 Open / Conditional。本决策包无任何真实 Tauri / IPC 证据。

## 证据链地图

| 阶段 | 任务 | 产出 | 关键证据 | 性质 |
|---|---|---|---|---|
| 设计 | P3-029 | Migration 设计 / 合同测试草案 | 表分层、CHECK/trigger/partial index 分责、17 P0 + 6 P1 + 5 P2 测试清单 | 事实 |
| 评审 | P3-030 | 独立反例评审 | Pass with Conditions；2 P1（tombstone trigger 遗漏、auth 测试遗漏）、3 P2 | 事实 |
| 实现 | P3-031 | 候选 SQL + 合成空库合同测试 | 33 PASS / 0 FAIL；`tombstone_generation_monotonic` trigger + `authorization_activation_complete` trigger | 事实 |
| 评审 | P3-032 | 独立工程评审 | Pass with Conditions；2 P1（Authorization/Derivation INSERT active 旁路）、4 P2；R-0043 关闭候选、R-0044 不建议关闭候选 | 事实 |
| 整改 | P3-033 | INSERT 旁路条件整改 | 35 PASS / 0 FAIL；新增 2 个 BEFORE INSERT trigger + CT-P1-08/09 | 事实 |
| 复评 | P3-034 | 轻量独立复评 | Pass；15 反例全 fail closed；R-0044/R-0045 可进入关闭候选 | 事实 |
| 决策 | P3-035 | 本决策包 | 逐风险关闭判断 + 残留处置 | 建议 + 待 PM/用户确认 |

**独立性验证**：P3-030 / P3-032 / P3-034 均由 WorkBuddy 独立评审会话执行，与 P3-031 / P3-033 工程执行会话（Codex）隔离。P3-035 由 WorkBuddy 独立评估会话执行，未参与 P3-031 / P3-033 工程执行。

## R-0043 关闭判断

### 风险描述

Tombstone generation 单调性若未由 DB trigger 强制，直接 DB 写入可能降低 tombstone generation 并绕过删除 / 撤回消费门。

### 证据评估

| 路径 | 覆盖 trigger | 测试 | 判定 |
|---|---|---|---|
| UPDATE 降低 generation | `tombstone_generation_monotonic` BEFORE UPDATE | DB-P0-15、CT-P2-07 | ✓ 已覆盖 |
| DELETE + INSERT with lower generation | 无（P2-2 残留） | 无 | P2 残留 |
| Tombstone status INSERT 旁路 | 无（P2-3 残留） | 无 | P2 残留 |

### 残留风险分析

- **P2-2（DELETE+INSERT）**：完全移除 tombstone 后重新插入 lower generation，属于不同类别攻击（完全移除 vs 降低）。正常应用流程不包含 tombstone DELETE。此路径需在真实 DB 维护场景中评估。
- **P2-3（status INSERT）**：初始 cleanup_status 由应用层设置，直接 INSERT 场景属于 DB 维护路径。应用事务 guard 应负责初始状态正确性。

两个 P2 均不破坏 R-0043 描述的核心风险路径（UPDATE 降低 generation）的覆盖结论。

### 关闭建议

**建议关闭**。关闭范围：候选 SQL + 合成空库合同测试 + 当前 evidence。残留 P2-2 / P2-3 转入后续真实 DB 验证前置任务追踪。

## R-0044 关闭判断

### 风险描述

Authorization activation completeness 若缺少合同测试，实现可能遗漏 0 scope、0 action、incomplete policy 或旧版本未 superseded 的 active 阻断。

### 证据评估

| 路径 | 覆盖 trigger | 测试 | 判定 |
|---|---|---|---|
| INSERT `status='active'` | `authorization_no_direct_active_insert` BEFORE INSERT | CT-P1-08 | ✓ 已覆盖 |
| UPDATE `status='active'`（propose→active） | `authorization_activation_complete` BEFORE UPDATE | CT-P1-07 | ✓ 已覆盖 |
| 激活后 DELETE scope/action/policy 子表 | 无（P2-4 残留） | 无 | P2 残留 |

### 反例攻击覆盖

P3-034 构造 15 个反例场景（A1-A15），覆盖 SQLite 引擎绕过、大小写变体、INSERT OR REPLACE/IGNORE、事务隔离、两步流程、残留行、ContentIdentity 兼容性、既有测试完整性、默认值、并发、FK 时序，全部 fail closed。

### 残留风险分析

- **P2-4（子表 DELETE）**：授权激活后 DELETE scope/action/policy 行使授权不完整。但 strict_intersection 在运行时查询当前 scope/action，删除后自然无法匹配（fail closed）。此风险为审计完整性级别，不影响 fail-closed 语义。

### 关闭建议

**建议关闭**。关闭范围：候选 SQL + 合成空库合同测试 + 当前 evidence。残留 P2-4 为审计完整性级别，不影响 fail-closed 语义，转入后续真实 DB 验证前置任务追踪。

## R-0045 关闭判断

### 风险描述

Derivation activation completeness 仅覆盖 UPDATE，直接 INSERT `status='active'` 可绕过 inputs / constraints 完整性检查。

### 证据评估

| 路径 | 覆盖 trigger | 测试 | 判定 |
|---|---|---|---|
| INSERT `status='active'` | `derivation_no_direct_active_insert` BEFORE INSERT | CT-P1-09 | ✓ 已覆盖 |
| UPDATE `status='active'`（draft→active） | `derivation_activation_complete` BEFORE UPDATE | DB-P0-04 | ✓ 已覆盖 |
| ContentIdentity 二级检查 | `content_identity_ai_derivation_complete` BEFORE INSERT | 隐式覆盖 | ✓ 不受影响 |

### 残留风险分析

无 P1 或 P2 残留风险。INSERT 和 UPDATE 两条路径均有候选 SQL trigger + 合成空库合同测试覆盖。ContentIdentity 二级检查不受 P3-033 新增 trigger 影响。

### 关闭建议

**建议关闭**。关闭范围：候选 SQL + 合成空库合同测试 + 当前 evidence。无残留风险。

## R-0040 不关闭声明

R-0040（Tauri / IPC 安全风险）必须继续保持 Open / Conditional。理由：

1. 本决策包的全部证据来自候选 SQL + 合成空库合同测试，使用内存 SQLite + 合成夹具，无真实 Tauri / IPC / capability / handler / WebView / CSP / debug-release bundle / 平台路径行为验证。
2. P3-031 的 IPC-P0-01 至 IPC-P0-03 仅测试纯 DTO parser，不创建 handler、capability 或 Tauri 配置。
3. R-0040 的关闭条件仍为：真实 Tauri / IPC 验证 + 进程杀死耐久 + 独立复评 + 用户确认。
4. P3-021 用户已确认保持 R-0040 Open / Conditional，不关闭不拆分。

**R-0040 不得被本决策包连带关闭。**

## 残留 P2 处置建议

| P2 项 | 描述 | 是否阻断关闭 | 后续追踪方式 |
|---|---|---|---|
| P2-2 | Tombstone 无 DELETE 保护，DELETE+INSERT 可绕过 generation 单调性 | 否 | 转入后续真实 DB 验证前置任务，评估是否需 tombstone BEFORE DELETE trigger |
| P2-3 | Tombstone status INSERT 旁路，直接 INSERT 可设置任意 cleanup_status | 否 | 转入后续真实 DB 验证前置任务，应用事务 guard 负责初始状态正确性 |
| P2-4 | Authorization 子表无 DELETE 保护，激活后 DELETE scope/action/policy 使授权不完整 | 否 | 转入后续真实 DB 验证前置任务；strict_intersection 运行时 fail closed，审计完整性风险 |

**处置原则**：三个 P2 均不破坏候选 SQL + 合成空库合同测试层的 fail-closed 语义，不阻断当前风险关闭。但必须在后续真实 DB 验证前置任务中统一评估是否需要补齐 DB 级保护。

## 关闭范围与失效条件

### 关闭范围

若 PM 和用户确认关闭，关闭范围仅限：

- 候选 SQL migration（`001_candidate_schema.sql`，candidate-only 标识）
- 合成空库合同测试（`run_contract_tests.py`，内存 SQLite + 合成夹具）
- 当前 evidence（MANIFEST §4.1 源文件 hash + §4.2 生成快照 hash）
- 有限 Stage 3 受控边界（合成数据、单进程、受控测试包、本地 evidence）

### 不可外推边界

关闭**不代表**以下任何内容：

- 真实 DB migration 通过或生产 migration 已验证
- 真实 Tauri / IPC / capability / handler 通过
- 真实 Vault、真实用户数据或真实文件能力可用
- Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线冻结
- R-0040 关闭
- 进入下一阶段或启用真实能力

### 失效条件

关闭在以下任一条件发生时自动失效，需重新评估：

1. 候选 SQL 被修改但未重新运行测试和更新 evidence
2. 真实 DB migration 发现新的旁路路径
3. P2-2 / P2-3 / P2-4 中任一残留风险在真实 DB 场景中被证明为可直接利用
4. Schema / API 冻结前未将 P2 残留项纳入检查清单

## 是否建议 PM / 用户确认后直接更新 RISK_LOG

**建议允许 PM 在用户确认后直接更新 RISK_LOG 关闭 R-0043 / R-0044 / R-0045。**

理由：

1. 关闭证据链完整：P3-031 实现 → P3-032 独立评审发现 P1 → P3-033 整改 → P3-034 独立复评 Pass → P3-035 决策包评估。每一步均有独立会话隔离和 PM 验收。
2. 残留 P2 不阻断关闭，且已有明确后续追踪方式。
3. 无需另建关闭执行任务——关闭本身只是状态更新，不涉及代码修改或新验证。
4. RISK_LOG 更新时应记录：关闭范围、残留 P2 清单、失效条件。

**更新建议**：

- R-0043 → Closed，备注："关闭范围限候选 SQL + 合成空库合同测试。残留 P2-2（DELETE+INSERT 旁路）、P2-3（status INSERT 旁路）转入后续真实 DB 验证前置任务。"
- R-0044 → Closed，备注："关闭范围限候选 SQL + 合成空库合同测试。残留 P2-4（子表 DELETE）为审计完整性级别，strict_intersection 运行时 fail closed。"
- R-0045 → Closed，备注："关闭范围限候选 SQL + 合成空库合同测试。无残留 P1/P2。"
- R-0040 → 不变，Open / Conditional。

## 风险与待确认事项

### 风险

| 风险 | 级别 | 说明 |
|---|---|---|
| 候选 SQL 被误读为生产 migration | P2 | 已在 SQL 首部注释和 meta 行标明 candidate-only；需持续在引用时注明 |
| P2-2 DELETE+INSERT 旁路在真实 DB 维护中成为现实威胁 | P2 | 需在真实 DB 验证前置任务中评估 tombstone BEFORE DELETE trigger |
| 风险关闭被误读为 R-0040 关闭 | P1 | 本决策包明确声明 R-0040 不关闭；RISK_LOG 更新时必须保持 R-0040 不变 |

### 待确认事项

1. **[需 PM 确认]** 是否采纳本决策包建议，关闭 R-0043 / R-0044 / R-0045？
2. **[需 PM 确认]** 残留 P2-2 / P2-3 / P2-4 是否纳入后续真实 DB 验证前置任务检查清单？
3. **[需用户确认]** 是否授权 PM 更新 RISK_LOG 关闭对应风险？
4. **[需 PM 确认]** 关闭后是否启动后续真实 DB / Tauri 前置验证任务规划？

## 最终建议

1. **R-0043 / R-0044 / R-0045 均建议关闭**，关闭范围限候选 SQL + 合成空库合同测试 + 当前 evidence。三个风险的核心路径均已有候选 SQL trigger + 合成空库合同测试 + 独立评审覆盖。残留 P2 不阻断关闭。

2. **PM 和用户确认后可直接更新 RISK_LOG**，无需另建关闭执行任务。更新时必须记录关闭范围、残留 P2 清单和失效条件。

3. **R-0040 必须保持 Open / Conditional**。本决策包无任何真实 Tauri / IPC 证据。R-0040 关闭仍需真实 Tauri / IPC 验证 + 进程杀死耐久 + 独立复评 + 用户确认。

4. **残留 P2-2 / P2-3 / P2-4 转入后续真实 DB 验证前置任务**。三个 P2 均不破坏候选层的 fail-closed 语义，但需在真实 DB 场景中统一评估是否需要补齐 DB 级保护。

5. **关闭不代表 Schema / API 冻结、真实 DB migration 通过、真实 Tauri / IPC 通过或下一阶段准入。** 关闭仅表示候选 SQL + 合成空库合同测试层的风险已被 trigger + 测试 + 独立评审覆盖。

6. **声明**：本决策包为只读风险评估，未修改工程文件、候选 SQL、测试、脚本、evidence、PM 账本、RISK_LOG 或冻结资产；未连接真实 DB / Vault / Tauri / IPC；未执行真实 SQL migration；未关闭任何风险；未冻结任何资产；未启动后续任务。
