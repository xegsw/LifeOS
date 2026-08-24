# LIFEOS-P3-033｜PM Review：候选 SQL activation INSERT 旁路条件整改

## 验收信息

- 任务 ID：LIFEOS-P3-033
- 任务名称：候选 SQL activation INSERT 旁路条件整改
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-033_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional，建议用户确认后启动 P3-034 轻量独立复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-033 按任务卡在授权范围内完成整改：仅修改 P3-031 候选 SQL、合成空库测试、evidence 与 P3-033 交付物，未修改 PM 账本、P3-032 评审文件或真实能力相关文件。
- PM 在临时副本中复跑 `run_validation.sh`，避免污染 P3-031 原始 evidence；复跑结果为 35 PASS / 0 FAIL / 0 Not Implemented，其中 P0 18、P1 9、P2 8。
- P3-032 的两个 P1 已补齐：新增 `authorization_no_direct_active_insert` 与 `derivation_no_direct_active_insert` 两个 `BEFORE INSERT` trigger，直接拒绝 `status='active'` 父记录插入。
- 新增 CT-P1-08 / CT-P1-09 负测，分别证明 Authorization / Derivation 直接 active INSERT 被拒绝且父行无残留。
- Evidence MANIFEST 已将稳定源文件 hash 与运行快照 hash 分开；PM 核对当前源文件与生成文件 hash 均匹配。
- 本地预检因本地模型连接重置跳过，符合降级规则；PM 未把本地预检作为验收依据。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：本任务涉及 R-0044 / R-0045 权限与 AI 派生安全边界关闭候选，不适用快车道直接推进或自动关闭风险。

## 角色与关卡验收

- 主责角色覆盖情况：通过。Authorization / Derivation direct active INSERT 均已 DB fail closed，且保持两步激活流程。
- 协审角色覆盖情况：通过。整改未放宽 Authorization、Derivation、ContentIdentity、证据链或消费门；边界声明清楚。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass with Conditions；Derivation INSERT active 旁路已补齐，但仍需独立复核。
  - Gate 3 AI 权限与信任评审：Pass with Conditions；Authorization INSERT active 旁路已补齐，但仍需独立复核。
  - Gate 4 技术可行性评审：Pass with Conditions；35 项合成测试通过，真实 DB / Tauri / IPC 未验证。
- 未通过或需后续确认关卡：真实 DB migration、真实 Tauri / IPC、真实 Vault、真实导出、WAL / backup、性能、跨平台均未验证。
- 是否属于关键冻结事项：No。
- 是否需要独立评审：建议 Yes，启动 P3-034 轻量独立复评。
- 独立评审路径：待创建。
- 独立评审结论：待完成。
- 是否允许进入下一任务或下一阶段：允许用户确认后进入 P3-034；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA、工程基线、R-0040 / R-0043 / R-0044 / R-0045 风险状态。
- 是否允许进入下一任务：Conditional，建议启动 P3-034 轻量独立复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-033 的 PM 验收结论，并启动 P3-034 轻量独立复评？
   - PM 建议：采纳，并启动 P3-034。
   - 可选方向：A. 采纳并启动 P3-034；B. 要求 P3-033 返工；C. 暂停 SQL migration 线。
   - 不确认的影响：R-0044 / R-0045 只能停留在 PM 验收后的关闭候选，不能进入风险关闭决策或后续真实 DB / Tauri 前置验证准备。

2. 问题：是否接受 R-0044 / R-0045 进入“关闭候选”，但暂不关闭？
   - PM 建议：接受为关闭候选；等 P3-034 轻量独立复评后，再决定是否创建风险关闭决策包。
   - 可选方向：A. 接受关闭候选；B. 要求 P3-034 再攻击后再标记关闭候选。
   - 不确认的影响：R-0044 / R-0045 继续保持普通 Open 状态，后续真实 DB / Tauri 前置任务仍被阻塞。

## 整改建议

- 不要求 P3-033 返工。
- P3-034 轻量独立复评应重点攻击：
  - `authorization_no_direct_active_insert` 和 `derivation_no_direct_active_insert` 是否可被 INSERT 变体、默认值、事务顺序或 FK 时序绕过。
  - CT-P1-08 / CT-P1-09 是否真正覆盖 P3-032 的两个 P1，而非只覆盖 happy path。
  - MANIFEST 当前 hash 口径是否可接受，PM 复跑不应再次造成误导。
  - 是否可将 R-0044 / R-0045 标记为独立复评后的关闭候选。

## 可接受内容

- P3-033 可作为 P3-034 轻量独立复评输入。
- Authorization / Derivation direct active INSERT 旁路已具备候选实现层关闭证据。
- R-0044 / R-0045 可更新为 Open / Closure Candidate，但不关闭。
- P3-032 指出的 MANIFEST hash 混用问题已按“源文件 hash / 生成快照 hash”口径修复。

## 不接受或需谨慎内容

- 不接受关闭 R-0040、R-0043、R-0044、R-0045。
- 不接受将 35 PASS 外推为真实 DB migration 通过。
- 不接受将 DTO / 合成测试外推为真实 Tauri / IPC 通过。
- 不接受冻结 Schema / API、SQL migration 或工程基线。
- 不接受进入下一阶段。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：将 P3-033 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将 P3-033 更新为 Accepted but Not Frozen / Pass with Conditions。
- `lifeos/DECISION_LOG.md`：新增 D-0200。
- `lifeos/RISK_LOG.md`：更新 R-0044 / R-0045 为 Open / Closure Candidate；R-0043 保持 Open / Closure Candidate；R-0040 保持 Open / Conditional。
- `lifeos/OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：范围纪律清楚，SQL trigger / 合同测试 / evidence hash 修复到位，报告未越权宣布风险关闭。
- 主要问题：本地预检不可用；由于这是执行 Agent 对自身工程线的补丁，仍应交给隔离评审会话轻量复核。
- 以后更适合分派给该 Agent 的任务类型：受控 SQL / 测试补丁、evidence 更新、合成验证复跑。
- 不建议分派给该 Agent 的任务类型：评审自己刚完成的风险关闭候选。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No。

## 下一步任务建议

- 建议用户确认采纳 P3-033 后，启动 P3-034：候选 SQL activation INSERT 旁路整改轻量独立复评。
- 推荐 WorkBuddy 独立评审会话执行 P3-034；P3-033 Codex 工程执行会话不得自评。
- P3-034 前不得关闭 R-0044 / R-0045，不得冻结 Schema / API，不得启用真实 DB / Tauri / IPC。

## 聊天回复边界

PM 主会话只输出验收结论、资产状态、是否允许下一步 / 下一阶段、修改文件和需要用户确认的问题，不复述完整 Review。
