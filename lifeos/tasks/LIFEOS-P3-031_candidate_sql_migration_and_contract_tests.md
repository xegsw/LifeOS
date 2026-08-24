# LIFEOS-P3-031｜候选 SQL migration 编写 + 合成空库合同测试实现

## 任务信息

- 任务 ID：LIFEOS-P3-031
- 任务名称：候选 SQL migration 编写 + 合成空库合同测试实现
- 优先级：P0
- 任务类型：工程实现型任务 / 受控 DB 合同验证
- 建议篇幅：短工程报告 1500-3000 字；详细测试日志写入 evidence
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务首次允许把 P3-029 / P3-030 的 migration 设计转成候选 `.sql` 文件，并在合成空库中实现合同测试；Codex 更适合受控工程实现、SQLite 约束、测试脚本、回归复跑和 evidence 整理。
- 是否需要后续独立评审：Yes。P3-031 完成后必须启动独立工程评审 / 反例复核；不得由本任务执行会话自评为通过。
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-031/`
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人、数据 / 领域模型负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：Codex 工程执行
- 推荐复用的会话：可复用此前承担 P3 工程实现 / 测试的 Codex 工程执行会话，前提是该会话上一任务已结束、无未完成修改、上下文未混淆且能重新读取本任务卡；否则新建 Codex 工程执行会话。
- 会话判断理由：本任务是受控工程实现任务，适合 Codex；但它首次授权创建候选 `.sql` 文件，必须重新确认授权边界，不能继承 P3-029 设计任务的非实现限制，也不能由 P3-030 独立评审会话执行。
- 是否需要独立性隔离：Yes。P3-030 独立评审会话不得执行本任务；P3-031 执行会话不得执行后续独立评审。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅参考短报告结构；本任务不适用快车道）
  - `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-029_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044 相关行
- 可复用既有读取结果：
  - 若同一工程执行会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-029 交付物
  - P3-030 独立评审与 PM Review
  - R-0043 / R-0044 风险行
- 任务完成后是否建议保留会话：Yes，作为后续候选 SQL migration 条件整改 / 合同测试补充 / evidence 复跑任务线保留。

## 背景

P3-029 已完成 SQL migration 设计 / 合同测试草案，P3-030 独立评审结论为 Accepted / Pass with Conditions，未发现 P0，但提出 2 项 P1 条件和 3 项 P2 清洁项。用户已确认采纳 P3-030，并授权启动 P3-031。

本任务是首次从 migration 设计进入受控候选 SQL 和合成空库合同测试。它不代表生产 Schema / API 冻结，不代表真实数据库可迁移，不代表真实 Tauri / IPC 安全，不代表 R-0040 可关闭。

## 授权边界

本任务明确授权：

- 可在 `lifeos/engineering/LIFEOS-P3-031/` 内创建候选 `.sql` migration 文件。
- 可在 `lifeos/engineering/LIFEOS-P3-031/` 内创建测试脚本、合成夹具、临时 SQLite 数据库和 evidence。
- 可运行合成空库 / 合成夹具上的 SQLite migration 与合同测试。

本任务不授权：

- 不连接、读取、迁移、修改任何真实数据库。
- 不连接真实 Vault、真实用户文件或真实敏感数据。
- 不安装、配置或运行真实 Tauri。
- 不创建或修改真实 IPC handler。
- 不修改 `lifeos/engineering/LIFEOS-P3-009/`、P3-025、P3-027、P3-029、P3-030 或项目账本。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0040、R-0043 或 R-0044。
- 不进入下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P3-029 的候选 migration 设计是否能落成可执行 SQLite `.sql` 候选文件。
- P3-030 的 2 项 P1 条件是否已在候选 SQL / 合同测试中补齐。
- P3-030 的 3 项 P2 清洁项是否已纳入候选 SQL / 测试清单。
- P3-029 §7 的 P0 / P1 / P2 合同测试是否已有可运行的合成空库覆盖。
- 候选 migration 是否可在空库中原子创建 schema、触发器、索引和必要 meta。
- 是否存在 P0 / P1 级实现缺口，需要返工或独立评审阻断。
- 是否允许后续启动 P3-032 独立工程评审。

## 范围

本任务必须覆盖：

1. **候选 SQL migration 文件**
   - 在 `lifeos/engineering/LIFEOS-P3-031/` 下创建候选 `.sql` migration。
   - 至少覆盖 P3-029 中权威内容、来源 / 版本、SemanticObject、Authorization、Derivation、Feedback、Tombstone、Audit、Outbox、FTS / search projection 支撑所需的候选表、CHECK、FK、unique / partial index、trigger 和 meta。
   - 明确标注候选文件不是生产冻结 migration。
2. **P3-030 两项 P1 必须关闭**
   - R-0043 / P1-1：补齐 tombstone generation monotonicity trigger，禁止 tombstone generation 降低。
   - 增加 DB-P0 测试：降低 tombstone generation 必须被拒绝，原 tombstone 不变。
   - R-0044 / P1-2：增加 Authorization activation completeness 合同测试，覆盖 0 scopes、0 actions、incomplete policy、旧版本未 superseded 均不得 active。
3. **P3-030 三项 P2 必须纳入**
   - DerivationInput `input_type` 显式 enum CHECK。
   - 并发 tombstone upgrade / stale generation 负测。
   - Tombstone status 转换矩阵和强制层级。
4. **P3-029 P0 合同测试实现**
   - 优先实现 P3-029 §7.1 的 DB-P0-01 至 DB-P0-14 以及 P3-030 新增 DB-P0-15。
   - IPC-P0-01 至 IPC-P0-03 可用纯 DTO / contract parser 层测试表达，不得创建真实 Tauri handler。
   - 若部分测试因实现范围不能落地，必须明确标记为 Not Implemented，并说明阻塞原因和风险级别。
5. **合成空库验证**
   - 使用临时 / 受控 SQLite 空库。
   - migration 失败必须整体失败，不能生成半可用状态。
   - 测试输出需统计 total / P0 / P1 / P2 PASS / FAIL。
   - 任何 P0 FAIL 必须使验证命令非零退出。
6. **Evidence 包**
   - 创建 `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`。
   - 保存测试命令、环境、结果摘要、关键日志路径、候选 SQL 文件路径、测试脚本路径。
   - 大日志写入 evidence，不在聊天中粘贴。
7. **短工程报告**
   - 输出到 `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`。
   - 报告应说明修改范围、测试摘要、P0 / P1 / P2 状态、R-0043 / R-0044 是否在候选实现层关闭、剩余风险和下一步建议。

## 非范围

本任务暂时不要做：

- 不迁移真实数据库。
- 不连接任何真实 LifeOS 数据库或用户数据。
- 不连接真实 Vault。
- 不修改真实应用代码、真实 IPC handler、真实 Tauri 配置。
- 不运行真实 Tauri。
- 不修改 `lifeos/engineering/LIFEOS-P3-009/` 或其他既有工程基线目录。
- 不修改 P3-025、P3-027、P3-029、P3-030 主交付物。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md` 或 `OPEN_QUESTIONS.md`。
- 不关闭 R-0040、R-0043、R-0044。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动 P3-032 或其他后续任务。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-029_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- P3-029、P3-030 独立评审、P3-030 PM Review 必须完整读取。
- P3-025 / P3-027 / P3-024 可按 Schema / API / DB / DTO / M-01 / M-04 / M-20 相关章节定向读取。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 候选 SQL 是否能表达 P3-029 的核心表、约束、索引、触发器和事务边界。
- 哪些不变量已由 DB 强制，哪些仍需应用事务 guard。
- R-0043 / R-0044 是否在候选实现层被测试覆盖。
- 测试是否能在合成空库中稳定复跑，并对 P0 fail 使用非零退出。

协审角色必须重点检查：

- 用户原文、外部来源、AI 派生、用户确认、撤回 / 删除、授权和恢复包是否仍 fail closed。
- 四 invoke / DTO 合同是否没有滑向真实 Tauri handler。
- evidence 是否足以支撑后续独立工程评审。
- 是否存在将候选 SQL 误写成生产冻结 Schema / API 的表述。

## 核心问题

请重点回答：

- 候选 `.sql` migration 是否可在合成空库执行成功？
- P3-030 的 2 项 P1 条件是否已补齐？
- P3-030 的 3 项 P2 清洁项是否已纳入？
- P3-029 §7 的 P0 合同测试覆盖到什么程度？
- 是否存在 P0 / P1 FAIL？
- R-0043 / R-0044 是否可以在候选实现层标记为“待 PM 验收的关闭候选”？
- 是否允许启动 P3-032 独立工程评审？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB 验证或 R-0040 关闭？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`

同时创建或更新：

- `lifeos/engineering/LIFEOS-P3-031/`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`

建议工程目录结构：

```text
lifeos/engineering/LIFEOS-P3-031/
  migrations/
    001_candidate_schema.sql
  tests/
    ...
  scripts/
    ...
  evidence/
    MANIFEST.md
    ...
```

交付物内容必须包括：

- 任务摘要
- 修改范围
- 候选 SQL 文件路径
- 测试脚本路径
- 复跑命令
- 测试摘要：total / P0 / P1 / P2 PASS / FAIL
- R-0043 / R-0044 处理情况
- P3-030 P2 清洁项处理情况
- 未实现或降级测试清单
- evidence manifest 路径
- 剩余风险
- 是否建议启动 P3-032 独立工程评审
- 非冻结 / 非真实能力声明

## 验收标准

只有满足以下条件，任务才算完成：

- 候选 `.sql` migration 文件已创建在授权目录内。
- 合成空库 migration 能执行，或失败被清楚记录并归类。
- P3-030 两项 P1 均有实现和测试证据，或明确说明未完成并标记 Rework 风险。
- P3-030 三项 P2 均已纳入候选 SQL / 测试 / 报告。
- P0 合同测试有明确 PASS / FAIL / Not Implemented 统计。
- 任一 P0 FAIL 会导致验证命令非零退出。
- evidence `MANIFEST.md` 存在且可作为 PM / 独立评审入口。
- 完整报告已保存到 `lifeos/deliverables/`。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、evidence 路径、预检路径、是否需要 PM 决策。
- 明确声明本任务不冻结 Schema / API、不关闭 R-0040、不启用真实能力、不进入下一阶段。

## 限制条件

- 只允许修改 `lifeos/engineering/LIFEOS-P3-031/` 和本任务交付物路径。
- 不修改项目账本。
- 不修改其他工程目录。
- 不连接真实数据库、真实 Vault 或真实用户数据。
- 不运行真实 Tauri，不创建真实 IPC handler。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整报告或测试日志，只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
