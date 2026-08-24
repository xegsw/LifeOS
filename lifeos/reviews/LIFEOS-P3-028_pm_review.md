# LIFEOS-P3-028｜PM Review｜Schema / API 条件整改轻量独立复核

## 验收信息

- 任务 ID：LIFEOS-P3-028
- 任务名称：Schema / API 条件整改轻量独立复核
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-028_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Pass
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

1. P3-028 按任务卡完成了对 P3-027 的只读轻量独立复核，覆盖 P1-1 至 P1-7、四 invoke 拆分、P3-024 M-01 / M-04 / M-20 影响、`semantic_object` 聚合与拆表门。
2. PM 接受其核心结论：P3-026 的 7 个 P1 条件已在设计层关闭，P3-027 未新增 P0 / P1 风险。
3. PM 接受四 invoke 拆分作为后续候选输入：`lifeos_read`、`lifeos_export_candidate`、`lifeos_mutate`、`lifeos_destruct`。该方向符合最小权限与可验证性，但仍不是 Schema / API 冻结。
4. P3-028 发现 3 个 P2 清洁项：retract-of-retract 语义、`feedback_dependency` 跨 target 强制级别、`strict_intersection` 形式化定义。PM 判断不要求 P3-028 返工，应纳入后续 migration 设计 / 合同测试检查清单。
5. P3-028 正文中的“本地预检路径”引用了 P3-027 预检文件；PM 已额外运行正确的 P3-028 本地预检，结果仍为本地模型不可用。该问题为 P2 文档瑕疵，不影响评审主体结论。
6. 本次不冻结 Schema / API，不写 SQL migration，不运行 Tauri，不关闭 R-0040，不进入下一阶段。

## P3 快车道 Review

不适用。P3-028 是独立评审任务，不是 P3 Engineering Fast Lane 工程补丁。

## 角色与关卡验收

- 主责角色覆盖情况：通过。评审覆盖 AI 信任与安全、数据 / 领域模型视角，明确检查用户原文、AI 输出、外部来源、用户确认事实、授权、撤回、来源身份、诊断脱敏与候选建议可信度。
- 协审角色覆盖情况：通过。评审覆盖技术可行性、QA / Evidence 和体验状态表达影响，尤其指出 P3-024 M-01 / M-04 / M-20 需要随四 invoke 调整。
- 已通过关卡：Gate 2 数据与来源评审 Pass；Gate 3 AI 权限与信任评审 Pass；Gate 4 技术可行性评审 Pass。
- 未通过或需后续确认关卡：无 P0 / P1；P2 清洁项进入后续任务检查清单。
- 是否属于关键冻结事项：No。本任务是冻结前或实现前的独立复核输入。
- 是否需要独立评审：本任务自身即独立评审。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
- 独立评审结论：Pass
- 是否允许进入下一任务或下一阶段：允许进入下一任务需用户确认；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQLite migration、Tauri capability 配置、IPC handler、导出格式、生产 SLA、工程基线、R-0040 风险状态。
- 是否允许进入下一任务：Conditional。用户确认采纳 P3-028 后，可启动 P3-029 SQL migration 设计 / 合同测试任务；仍不得写或执行 migration。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 是否采纳 P3-028 的 Pass 结论。
   - PM 建议：采纳。
   - 不确认的影响：P3-029 不启动，Schema / API 线停留在轻量独立复核完成但未采纳状态。

2. 是否确认四 invoke 拆分作为后续候选输入。
   - PM 建议：确认采用 `lifeos_read` / `lifeos_export_candidate` / `lifeos_mutate` / `lifeos_destruct`。
   - 不确认的影响：后续 migration / DTO / Tauri capability 设计无法稳定收口。

3. 是否同意下一步启动 P3-029：SQL migration 设计 / 合同测试任务。
   - PM 建议：启动，但只做设计与合同测试定义，不写、不执行 migration。
   - 不确认的影响：不能进入 production schema 的可执行约束设计。

## 整改建议

无需 P3-028 返工。

后续 P3-029 必须纳入以下 P2 检查项：

- 明确 retract-of-retract 是否允许及其状态效果。
- 明确 `feedback_dependency` 跨 target 依赖由 DB CHECK、触发器还是事务级校验强制。
- 形式化定义 authorization `strict_intersection`。
- 复查 Decision / Action 专属字段是否因 migration 设计新增字段而触发拆表门。
- 将 P3-024 M-01 / M-04 / M-20 从三 invoke 调整为四 invoke 验证矩阵输入，但不在 P3-029 中实际运行 Tauri。

## 可接受内容

- P3-027 设计层关闭 P3-026 七项 P1 的判断。
- 四 invoke 拆分作为后续候选输入。
- `semantic_object` 暂时聚合可继续，拆表门足够硬。
- 允许启动 SQL migration 设计 / 合同测试任务，但不得写或执行 migration。
- 最小 Tauri shell / handler 任务仍需等待 P3-024 矩阵补丁、migration 设计或 DTO 合同进一步明确。

## 不接受或需谨慎内容

- 不接受将 P3-028 Pass 误读为 Schema / API Frozen。
- 不接受将 P3-028 Pass 误读为 R-0040 可关闭。
- 不接受直接进入真实 Tauri / IPC、真实 Vault、真实数据或真实文件导出。
- 不接受直接写或执行 SQL migration。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：更新 P3-028 为 Accepted。
- `lifeos/FREEZE_STATUS.md`：更新 P3-028 状态，并记录 Schema / API 仍未冻结。
- `lifeos/DECISION_LOG.md`：新增 PM 接受 P3-028 的决策记录。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-028 并启动 P3-029。
- `lifeos/RISK_LOG.md`：暂不更新。P3-028 发现的是 P2 清洁项，先纳入 P3-029 检查清单；R-0040 保持 Open / Conditional。
- `lifeos/OPEN_QUESTIONS.md`：暂不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：反例覆盖完整，能清楚区分 P0 / P1 / P2，并把四 invoke 与 P3-024 验证矩阵影响说清楚。
- 主要问题：本地预检路径引用了 P3-027 文件，属于轻微文档瑕疵。
- 以后更适合分派给该 Agent 的任务类型：独立评审、反例攻击、风险复核、冻结前条件检查。
- 不建议分派给该 Agent 的任务类型：需要直接修改工程代码或生成 evidence 的实现任务。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No，本次表现符合既有路由判断。

## 下一步任务建议

建议用户确认采纳 P3-028 后，启动 `LIFEOS-P3-029` SQL migration 设计 / 合同测试任务。

P3-029 应只产出 migration 设计、约束清单、合同测试草案和 P3-028 P2 检查项处理口径；不得写或执行 SQL migration，不得修改工程代码，不得安装、配置或运行真实 Tauri，不得冻结 Schema / API，不得关闭 R-0040。

