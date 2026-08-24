# LIFEOS-P3-032｜候选 SQL migration 与合成空库合同测试独立工程评审

## 任务信息

- 任务 ID：LIFEOS-P3-032
- 任务名称：候选 SQL migration 与合成空库合同测试独立工程评审
- 优先级：P0
- 任务类型：独立评审型任务 / 工程反例攻击 / 风险关闭候选复核
- 建议篇幅：2000-4000 字；详细复跑日志如有必须写入评审 evidence，不粘贴到聊天
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要独立攻击 P3-031 执行成果，重点检查候选 SQL、trigger、合同测试、evidence 与风险关闭候选是否存在自证循环、旁路或过拟合；WorkBuddy 更适合独立评审、反例攻击和证据链挑错。
- 是否需要后续独立评审：No，本任务自身为独立评审；若发现 P0 或关键 P1，应回到 PM 主会话决定是否创建整改任务。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人、QA / Evidence Reviewer
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 独立评审
- 推荐复用的会话：可复用此前专门承担 P3 独立评审 / 反例攻击的 WorkBuddy 会话，前提是该会话未参与 P3-031 执行、上一任务已结束、上下文未混淆、无未完成修改且能重新读取本任务卡；否则新建 WorkBuddy 独立评审会话。
- 会话判断理由：P3-031 是 Codex 工程实现成果，本任务必须隔离执行上下文，避免由执行 Agent 自评候选 SQL、合同测试和 R-0043 / R-0044 关闭证据。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
  - `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044 相关行
- 可复用既有读取结果：
  - 若同一 WorkBuddy 独立评审会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-031 交付物、PM Review、候选 SQL、测试脚本、evidence manifest 与结果
  - P3-030 独立评审与 PM Review
  - R-0040 / R-0043 / R-0044 风险行
- 任务完成后是否建议保留会话：Yes，作为 SQL migration / DB 合同测试 / 风险关闭候选独立评审线保留。

## 背景

P3-031 已完成候选 SQLite migration、合成空库合同测试和 evidence，PM 验收结论为 Accepted / Pass with Conditions。PM 复跑结果为 33 PASS / 0 FAIL / 0 Not Implemented。P3-031 声称 P3-030 的两项 P1 条件和三项 P2 清洁项已形成候选实现层证据。

但 P3-031 是执行 Agent 自证，且涉及 R-0043 / R-0044 风险关闭候选。因此在任何风险关闭、Schema / API 冻结、真实 DB / Tauri 验证或下一阶段推进前，必须进行独立工程评审和反例攻击。

## 授权边界

本任务明确授权：

- 只读审查 P3-031 的候选 SQL、测试脚本、复跑脚本、evidence manifest、测试结果和 PM Review。
- 可运行只读检查命令，例如 `rg`、`sed`、`sqlite3` schema inspection、hash 校验、静态反例分析。
- 如需复跑 `run_validation.sh`，必须优先复制 `lifeos/engineering/LIFEOS-P3-031/` 到临时目录或评审专用临时目录后运行，避免修改 P3-031 原始 evidence。
- 可将完整独立评审写入 `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`。
- 可创建本地预检文件到 `lifeos/local_prechecks/`。

本任务不授权：

- 不修改 `lifeos/engineering/LIFEOS-P3-031/` 下任何原始候选 SQL、测试、脚本或 evidence。
- 不修改 P3-031 交付物或 PM Review。
- 不修改项目账本。
- 不连接真实数据库、真实 Vault、真实用户文件、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不创建真实 SQL migration、不执行真实 migration。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0040、R-0043 或 R-0044。
- 不启动整改任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P3-031 的候选 SQL 是否真实表达了 P3-029 / P3-030 要求的核心约束，而不是测试过拟合。
- `authorization_activation_complete` trigger 是否足以支持 R-0044 的候选关闭，是否存在 INSERT / UPDATE / supersede / scope-action-policy 组合旁路。
- `tombstone_generation_monotonic` trigger 与 status transition 是否足以支持 R-0043 的候选关闭，是否存在 stale、并发、rollback、cleanup status 反例。
- P3-031 的 33 PASS / 0 FAIL 是否可复核，evidence manifest 是否可信、可追溯、未误导为真实能力。
- P3-031 的 IPC-P0 测试是否严格停留在纯 DTO parser，没有被误读为真实 Tauri / IPC 安全证据。
- 是否允许将 R-0043 / R-0044 标记为“独立评审通过后的关闭候选”，或必须创建 P3-033 条件整改任务。

## 范围

本任务必须覆盖：

1. **候选 SQL 约束反例攻击**
   - 检查表、CHECK、FK、unique / partial index、trigger 是否覆盖 P3-029 / P3-030 的关键不变量。
   - 重点攻击 Authorization、DerivationInput、Feedback、Tombstone、Outbox、FTS/search projection、schema_migration_meta。
2. **R-0043 独立复核**
   - 检查 tombstone generation 单调 trigger 是否覆盖降低 generation 的所有相关路径。
   - 检查 stale / concurrent upgrade、cleanup status transition、active_blocked 前置证明边界。
   - 判断 R-0043 是否可作为关闭候选进入 PM 决策，或是否仍需整改。
3. **R-0044 独立复核**
   - 检查 Authorization active 转换是否覆盖 0 scopes、0 actions、incomplete policy、旧版本未 superseded。
   - 检查是否存在直接 INSERT active、非 status 更新、supersedes / logical_key / version_no 边界、scope/action/policy 删除后 active 悬挂等反例。
   - 判断 R-0044 是否可作为关闭候选进入 PM 决策，或是否仍需整改。
4. **测试与 evidence 复核**
   - 复核 `test_results.json`、`test_run.log`、MANIFEST hash、复跑命令和退出码合同。
   - 检查任一 P0 FAIL 是否确实会导致非零退出。
   - 检查测试是否过拟合固定 happy path，是否遗漏关键负例。
5. **边界声明复核**
   - 确认 P3-031 没有被外推为真实 DB、真实 Tauri / IPC、真实 Vault、真实导出或 Schema / API 冻结。
   - 检查是否有文案把候选 SQL 误写成生产冻结 migration。

## 非范围

本任务暂时不要做：

- 不修改候选 SQL、测试脚本、复跑脚本或 evidence。
- 不修复 P3-031 中发现的问题。
- 不创建 P3-033 或任何后续任务。
- 不修改 PM 账本。
- 不运行真实数据库 migration。
- 不连接真实 Vault、真实用户数据、真实 Tauri / IPC、真实文件能力。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
- `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- P3-031 交付物、PM Review、evidence manifest、候选 SQL、测试脚本、test results 必须完整读取。
- P3-030 独立评审与 PM Review 必须完整读取。
- `RISK_LOG.md` 可定向读取 R-0040、R-0043、R-0044。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0194 至 D-0197。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- P3-031 的候选 SQL / trigger / test harness 是否能经受反例攻击。
- P3-031 的测试结果是否可复核，是否存在自证循环或 happy path 过拟合。
- 是否存在 P0 / P1 问题足以阻断后续真实 DB / Tauri 验证前置路线。
- R-0043 / R-0044 是否具备进入关闭决策的独立证据。

协审角色必须重点检查：

- 用户原文、外部来源、AI 派生、用户反馈、授权、删除 / 撤回、恢复包和搜索投影是否仍 fail closed。
- IPC-P0 是否仅是 DTO parser 合同，没有冒充真实 Tauri / IPC 证据。
- Evidence 是否足以让 PM 快速判断结论、风险、路径和下一步。
- 是否存在候选 SQL 被误写成冻结生产 Schema / API 的表达。

## 核心问题

请重点回答：

- P3-031 是否可以通过独立工程评审？
- 是否发现 P0、P1 或关键 P2？
- R-0043 是否可进入“关闭候选 / 待 PM 与用户确认”，还是必须整改？
- R-0044 是否可进入“关闭候选 / 待 PM 与用户确认”，还是必须整改？
- P3-031 的 33 PASS / 0 FAIL 是否可信、可复核、未污染 evidence？
- 是否允许 PM 启动后续 P3-033 条件整改、风险关闭决策包或真实 DB / Tauri 前置任务？若不允许，原因是什么？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB 验证、真实 Tauri / IPC 通过或 R-0040 关闭？

## 交付物

请将完整独立评审保存为：

`lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`

交付物内容必须包括：

- 评审信息
- 评审摘要
- 已通过内容
- 关键问题
- 必须整改项
- 条件通过项
- 关卡检查
- R-0043 / R-0044 独立判断
- 测试 / evidence 复核
- 风险
- 需要 PM 决策
- 最终建议

如产生评审复跑日志或临时 evidence，请保存到评审文件旁边的评审专用路径，并在评审中引用；不要修改 P3-031 原始 evidence。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整评审文件已保存到指定路径。
- 已覆盖 P3-031 候选 SQL、测试脚本、evidence manifest、test results 和 PM Review。
- 已对 R-0043 / R-0044 分别给出独立判断。
- 已明确是否存在 P0 / P1 / P2。
- 已明确是否建议 P3-031 Pass / Pass with Conditions / Rework / Blocked。
- 已明确是否建议 R-0043 / R-0044 进入关闭候选。
- 已明确哪些结论仍不得外推为 Schema / API 冻结、真实 DB / Tauri 验证或 R-0040 关闭。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、评审文件路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 `lifeos/engineering/LIFEOS-P3-031/` 原始文件。
- 不修改 P3-031 交付物或 PM Review。
- 不修改项目账本。
- 不连接真实数据库、真实 Vault、真实用户数据、真实 Tauri / IPC 或真实文件能力。
- 不执行真实 SQL migration。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整评审或测试日志，只输出摘要、评审文件路径、本地预检路径和是否需要 PM 决策。
