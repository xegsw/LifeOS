# LIFEOS-P3-035｜R-0043 / R-0044 / R-0045 风险关闭决策包

## 任务信息

- 任务 ID：LIFEOS-P3-035
- 任务名称：R-0043 / R-0044 / R-0045 风险关闭决策包
- 优先级：P1
- 任务类型：决策型任务 / 风险关闭评估 / 证据收口
- 建议篇幅：1000-2000 字；证据路径和引用要完整，但不要展开完整测试日志
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务不是工程实现，而是对 R-0043 / R-0044 / R-0045 是否满足关闭条件做独立、克制、可审计的风险决策评估；WorkBuddy 更适合风险复核、反例视角和证据链边界判断。
- 是否需要后续独立评审：No，本任务自身应以独立风险评估方式完成；最终风险关闭仍需 PM 验收和用户确认。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：风险关闭评估负责人
- 协审角色：数据 / 来源负责人、AI 信任与安全负责人、技术架构负责人、QA / Evidence Reviewer
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 风险关闭评估 / 独立决策评估
- 推荐复用的会话：可复用此前专门承担 P3 SQL migration / DB 合同测试独立评审的 WorkBuddy 会话，前提是该会话未参与 P3-031 / P3-033 工程执行，上一任务已结束，上下文未混淆，无未完成修改，且能重新读取本任务卡；否则新建 WorkBuddy 独立评估会话。
- 会话判断理由：本任务涉及风险关闭候选判断，不能由工程整改会话自证，也不能把 P3-034 Pass 直接等同于风险关闭。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
  - `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
  - `lifeos/reviews/LIFEOS-P3-032_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P3-033_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-034_activation_insert_bypass_remediation_light_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-034_pm_review.md`
- 可复用既有读取结果：
  - 若同一 WorkBuddy 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - R-0040 / R-0043 / R-0044 / R-0045 风险行
  - P3-032、P3-033、P3-034 的评审 / PM Review
  - P3-031 evidence manifest
- 任务完成后是否建议保留会话：Yes，作为 P3 风险关闭评估线保留。

## 背景

P3-030 发现候选 SQL migration / 合同测试层存在 R-0043 / R-0044 相关 P1 条件；P3-031 补齐候选 SQL 与合成空库合同测试；P3-032 独立评审后，R-0043 进入 Open / Closure Candidate，但 R-0044 仍因直接 INSERT active 旁路保持 Open，并新增 R-0045。

P3-033 已补齐 Authorization / Derivation 直接 INSERT `active` 旁路，P3-034 已完成轻量独立复评并由 PM 验收为 Accepted / Pass。当前 R-0043 / R-0044 / R-0045 均仍保持 Open / Closure Candidate，尚未关闭。

本任务用于把已有证据整理成风险关闭决策包，明确每个风险是否建议关闭、关闭范围是什么、残留风险是否可接受、哪些内容仍不得外推为真实能力或冻结资产。

## 授权边界

本任务明确授权：

- 只读审查 R-0043 / R-0044 / R-0045 的风险描述、影响、缓解证据和相关交付物。
- 只读引用 P3-030 至 P3-034 的评审、PM Review、交付物和 evidence manifest。
- 可定向读取候选 SQL / 测试脚本中的相关 trigger 和测试编号，但不要求全量重跑测试。
- 可输出完整风险关闭决策包到 `lifeos/deliverables/LIFEOS-P3-035_r0043_r0044_r0045_risk_closure_decision_package.md`。
- 可创建本地预检文件到 `lifeos/local_prechecks/`。

本任务不授权：

- 不修改工程代码、候选 SQL、测试脚本、复跑脚本或 evidence。
- 不修改 PM 账本、风险状态、冻结状态或决策记录。
- 不关闭 R-0040、R-0043、R-0044、R-0045。
- 不执行真实 SQL migration。
- 不连接真实数据库、真实 Vault、真实用户文件、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- R-0043 是否建议关闭、保留 Open / Closure Candidate、降级为后续 P2、或继续保持 Open。
- R-0044 是否建议关闭、保留 Open / Closure Candidate、降级为后续 P2、或继续保持 Open。
- R-0045 是否建议关闭、保留 Open / Closure Candidate、降级为后续 P2、或继续保持 Open。
- 每个建议关闭的风险，其关闭范围是否仅限“候选 SQL + 合成空库合同测试 + 当前受控 evidence”。
- 残留 P2 是否可被接受为后续真实 DB / Tauri 前置验证输入，而不是阻断当前风险关闭。
- R-0040 为什么必须继续保持 Open / Conditional。
- 如果 PM 和用户采纳本决策包，是否可以直接更新 RISK_LOG 关闭对应风险，还是必须另建关闭执行任务。

## 范围

本任务必须覆盖：

1. **逐风险关闭条件判断**
   - R-0043：tombstone generation 单调性，含 UPDATE 降低 generation 证据和 DELETE+INSERT P2 残留。
   - R-0044：Authorization activation completeness，含 INSERT active / UPDATE active 两条路径和 P2-4 授权子表 DELETE 残留。
   - R-0045：Derivation activation completeness，含 INSERT active / UPDATE active 和 ContentIdentity 二级检查。
2. **证据链完整性**
   - 对 P3-031 / P3-032 / P3-033 / P3-034 的证据关系做清晰映射。
   - 标明哪些证据是事实，哪些是推断，哪些是 PM / 用户待确认决策。
3. **关闭范围与不可外推**
   - 明确关闭若成立，仅限候选 SQL、合成空库合同测试、当前 evidence 和有限 Stage 3 受控边界。
   - 明确不代表真实 DB migration、真实 Tauri / IPC、真实 Vault、真实数据、Schema / API 冻结、工程基线冻结、生产 SLA 或下一阶段准入。
4. **残留风险处置**
   - 判断 P2-2 / P2-3 / P2-4 是阻断关闭，还是可作为后续真实 DB 验证前置任务输入。
   - 如建议关闭风险，必须给出残留项的后续追踪方式。
5. **后续动作建议**
   - 若建议关闭部分或全部风险，说明 PM / 用户确认后应如何更新 RISK_LOG。
   - 若不建议关闭，说明需创建何种整改或验证任务。

## 非范围

本任务暂时不要做：

- 不修改工程代码、SQL、测试、脚本或 evidence。
- 不复跑完整测试，除非发现证据矛盾；如复跑，必须使用临时副本并只在交付物中摘要报告。
- 不关闭任何风险。
- 不修改 `lifeos/RISK_LOG.md`、`lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md`。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不执行真实 SQL migration。
- 不连接真实数据库、真实 Vault、真实用户数据、真实 Tauri / IPC、真实文件能力。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045
- `lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-032_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-033_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-034_activation_insert_bypass_remediation_light_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-034_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- `RISK_LOG.md` 可定向读取 R-0040、R-0043、R-0044、R-0045。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0194 至 D-0203。
- 不主动读取无关 Review、Deliverable 或 Evidence。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 每个风险是否满足关闭条件。
- 每个风险若关闭，关闭范围是否准确、克制、可审计。
- 残留 P2 是否会破坏关闭结论，还是可转入后续真实 DB / Tauri 前置验证。
- 是否存在把候选证据误当作真实能力或冻结资产的表达风险。

协审角色必须重点检查：

- 删除 / 撤回、授权、AI 派生、来源身份、证据链和恢复包语义是否仍 fail closed。
- R-0040 是否被错误连带关闭。
- 风险关闭建议是否不会绕过 PM / 用户确认。
- 是否清楚区分事实、推断、建议和待确认决策。

## 核心问题

请重点回答：

- R-0043 建议关闭、保留还是整改？依据是什么？
- R-0044 建议关闭、保留还是整改？依据是什么？
- R-0045 建议关闭、保留还是整改？依据是什么？
- 若建议关闭，关闭范围是什么？失效条件是什么？
- P2-2 / P2-3 / P2-4 如何处理？
- 是否允许 PM 在用户确认后直接更新 RISK_LOG 关闭对应风险？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB 验证、真实 Tauri / IPC 通过、R-0040 关闭或下一阶段准入？

## 交付物

请将完整决策包保存为：

`lifeos/deliverables/LIFEOS-P3-035_r0043_r0044_r0045_risk_closure_decision_package.md`

交付物内容必须包括：

- 决策信息
- 执行摘要
- 证据链地图
- R-0043 关闭判断
- R-0044 关闭判断
- R-0045 关闭判断
- R-0040 不关闭声明
- 残留 P2 处置建议
- 关闭范围与失效条件
- 是否建议 PM / 用户确认后直接更新 RISK_LOG
- 风险与待确认事项
- 最终建议

## 验收标准

只有满足以下条件，任务才算完成：

- 完整决策包已保存到指定路径。
- 已分别判断 R-0043 / R-0044 / R-0045。
- 已明确哪些风险建议关闭、哪些建议保留、哪些需要后续整改或验证。
- 已明确关闭范围、失效条件和不可外推边界。
- 已明确 R-0040 仍不可关闭。
- 已明确 P2-2 / P2-3 / P2-4 的处理建议。
- 已明确是否建议 PM / 用户确认后直接更新 RISK_LOG。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改工程文件、SQL、测试、脚本或 evidence。
- 不修改 PM 账本或风险状态。
- 不关闭 R-0040、R-0043、R-0044、R-0045。
- 不执行真实 SQL migration。
- 不连接真实数据库、真实 Vault、真实用户数据、真实 Tauri / IPC 或真实文件能力。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整决策包，只输出摘要、交付物路径、本地预检路径和是否需要 PM 决策。
