# LIFEOS-P3-032｜PM Review：候选 SQL migration 与合成空库合同测试独立工程评审

## 验收信息

- 任务 ID：LIFEOS-P3-032
- 任务名称：候选 SQL migration 与合成空库合同测试独立工程评审
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-032_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional，用户确认后可启动 P3-033 条件整改任务
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-032 按任务卡完成只读独立工程评审，未修改 P3-031 原始候选 SQL、测试、脚本或 evidence，未修改 PM 账本，未连接真实 DB / Vault / Tauri / IPC。
- 评审结论为 Pass with Conditions：未发现 P0；发现 2 项 P1 与 4 项 P2。
- PM 定向复核确认两个 P1 成立：`authorization_activation_complete` 和 `derivation_activation_complete` 均只覆盖 `BEFORE UPDATE OF status`，不覆盖直接 `INSERT status='active'`。
- PM 接受 P3-032 对 R-0043 / R-0044 的区分判断：R-0043 可进入“关闭候选 / 待用户确认”，但仍保持 Open；R-0044 不可进入关闭候选，必须先补齐 Authorization INSERT active 旁路。
- PM 将 Derivation 直接 INSERT active 旁路登记为新增 P1 风险 R-0045。
- 本地预检因本地模型连接重置跳过，符合降级规则；不作为 PM 验收依据。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：P3-032 是 P0 独立评审，涉及风险关闭候选和 P1 问题判定，不适用快车道直接推进。

## 角色与关卡验收

- 主责角色覆盖情况：通过。评审覆盖候选 SQL、trigger、test harness、MANIFEST、hash、复跑结论与 P3-030 条件。
- 协审角色覆盖情况：通过。评审覆盖数据来源、AI 权限、DTO / IPC 边界、evidence 不误导、候选 SQL 非冻结声明。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass with Conditions；Derivation INSERT active 旁路需整改。
  - Gate 3 AI 权限与信任评审：Pass with Conditions；Authorization INSERT active 旁路需整改。
  - Gate 4 技术可行性评审：Pass with Conditions；MANIFEST 生成文件 hash 需更新。
- 未通过或需后续确认关卡：真实 DB、真实 Tauri / IPC、真实 Vault、导出、性能、WAL / backup、跨平台仍未验证。
- 是否属于关键冻结事项：No。本任务不冻结 Schema / API。
- 是否需要独立评审：本任务自身为独立评审。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- 独立评审结论：Pass with Conditions
- 是否允许进入下一任务或下一阶段：允许用户确认后进入 P3-033 条件整改；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA、工程基线、R-0040 / R-0043 / R-0044 / R-0045 风险状态。
- 是否允许进入下一任务：Conditional，用户确认后启动 P3-033。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-032 的 Pass with Conditions 结论，并启动 P3-033 条件整改？
   - PM 建议：采纳，并启动 P3-033。
   - 可选方向：A. 采纳并启动 P3-033；B. 要求 P3-032 补充评审；C. 暂停 SQL migration 线。
   - 不确认的影响：Authorization / Derivation INSERT active 旁路无法进入整改，R-0044 和新增 R-0045 保持 Open，后续真实 DB / Tauri 前置任务继续被阻塞。

2. 问题：是否接受 R-0043 进入“关闭候选 / 待用户确认”，但暂不关闭？
   - PM 建议：接受为关闭候选，保持 Open，等待 P3-033 后再统一处理风险关闭决策。
   - 可选方向：A. 接受关闭候选；B. 要求 P3-033 同时补 tombstone DELETE 保护后再评估。
   - 不确认的影响：R-0043 继续保持普通 Open 状态，无法进入后续风险关闭决策包。

## 整改建议

建议创建 P3-033 条件整改任务，范围限定为：

1. 增加 Authorization `BEFORE INSERT` trigger，拒绝或完整校验 `status='active'` 的直接插入。
2. 增加 Derivation `BEFORE INSERT` trigger，拒绝或完整校验 `status='active'` 的直接插入。
3. 增加对应 DB 合同测试：直接 INSERT active Authorization / Derivation 必须被拒绝。
4. 更新或重建 P3-031 evidence MANIFEST 中生成文件 hash，避免 PM 复跑后 manifest 与结果文件不一致。
5. 可将 tombstone DELETE 保护作为 P2 项进入整改清单，但不得扩大为真实 DB migration 或 Schema/API 冻结。

## 可接受内容

- P3-032 的独立复跑、hash 核对、P1/P2 分类和风险关闭候选判断可作为 PM 决策输入。
- P3-031 仍可作为候选 SQL / 合成空库合同测试输入，但必须经过 P3-033 条件整改后再进入下一类前置验证。
- R-0043 可进入关闭候选状态，但不应在本轮直接关闭。

## 不接受或需谨慎内容

- 不接受关闭 R-0044；Authorization INSERT active 旁路未补齐前，R-0044 必须保持 Open。
- 不接受关闭 R-0045；Derivation INSERT active 旁路为新增 P1。
- 不接受冻结 Schema / API、SQL migration、Tauri capability 或工程基线。
- 不接受启动真实 DB / Tauri / IPC 验证。
- 不接受将 P3-032 的 Pass with Conditions 解读为 P3-031 无条件通过。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：将 P3-032 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将 P3-032 更新为 Accepted / Pass with Conditions，并记录等待用户确认 P3-033。
- `lifeos/DECISION_LOG.md`：新增 D-0198。
- `lifeos/RISK_LOG.md`：更新 R-0043 / R-0044，新增 R-0045。
- `lifeos/OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：独立性清楚，能发现执行 Agent 自证遗漏的 INSERT active 旁路，并准确区分 P0 / P1 / P2 与风险关闭候选。
- 主要问题：本地预检不可用；评审建议中“R-0043 建议关闭”仍需 PM 收紧为“关闭候选，暂不关闭”。
- 以后更适合分派给该 Agent 的任务类型：独立评审、反例攻击、风险关闭候选复核、evidence 可信度检查。
- 不建议分派给该 Agent 的任务类型：直接修复候选 SQL 或修改工程目录。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：可暂不更新。

## 下一步任务建议

- 建议用户确认采纳 P3-032 后，启动 P3-033：候选 SQL activation INSERT 旁路条件整改。
- P3-033 推荐交给 Codex 工程执行会话；不得由 P3-032 独立评审会话自行修改工程文件。
- P3-033 前不得关闭 R-0044 / R-0045，不得冻结 Schema / API，不得启用真实 DB / Tauri / IPC。

## 聊天回复边界

PM 主会话只输出验收结论、资产状态、是否允许下一步 / 下一阶段、修改文件和需要用户确认的问题，不复述完整 Review。
