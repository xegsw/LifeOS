# LIFEOS-P1-003｜V1 范围冻结条件整改

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P1-003
- 任务名称：V1 范围冻结条件整改
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字
- 主责角色：产品架构负责人
- 协审角色：用户研究 / 市场验证负责人、体验设计负责人、数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；辅助检查 Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审、Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-001` 已产出 V1 范围冻结草案，并通过 PM 验收。  
`LIFEOS-P1-002` 已完成 V1 范围独立评审，结论为 `Pass with Conditions`。  
PM 已验收 P1-002，并确认 V1 范围当前状态为 `Pass with Conditions`，尚未冻结。

用户已采纳 PM 建议：在首页 / 今日页 PRD 前，先启动一个有限条件整改任务，只回应独立评审提出的 M-01 至 M-04，不重写 P1-001，不扩大 V1 范围。

## 目标

本任务完成后，需要回答：

1. P1-002 提出的 M-01 至 M-04 是否已被逐项补齐？
2. V1 Must Have 的最低可验收切片是否清楚？
3. 四类用户命令是否在 V1 范围层被显式继承？
4. Obsidian 在 V1 中的优先级、条件和失败降级是否清楚？
5. 用户验证合同是否足以支撑后续 PRD、原型和 Stage 2 验证？
6. 完成整改后，是否建议 PM 冻结 V1 范围？

## 范围

本任务必须覆盖 P1-002 的四项必须整改项：

### M-01｜给 Must 补最小范围合同

必须明确：

- Must 捕获的文件能力最低仅为文件 / 来源指针及必要来源元数据。
- 完整文件摄取、解析、附件管理和格式覆盖属于 Should / 条件项。
- Must 的 AI 最低产出围绕 Project 恢复信息与 1 个可核对的候选下一步。
- 摘要、分类、关联是允许的支撑手段，不应被解释为每项都要形成独立完整功能面。
- 今日页 1–3 个候选属于场景呈现上限，不是强制凑数。
- FTS + 元数据是最低找回路径；向量、混合重排和跨源自动关联不得成为 Must 验收的隐含前提。

### M-02｜显式继承四类命令

必须在 V1 范围层显式引用并区分：

- `revoke_processing`：撤回处理许可。
- `disconnect_source`：断开来源。
- `delete_content`：删除内容。
- `retract_feedback`：撤回反馈 / 纠正 / 确认。

必须说明四者不得互相冒充；活跃阻断、物理清理状态、用户确认历史、来源连接和内容保留按已冻结 AI 权限与信任模型、核心领域模型分别处理。

### M-03｜固定 Obsidian 的优先级和失效条件

必须明确：

- Obsidian 是 Should Have + 条件性需求。
- Obsidian 是首批用户的高价值来源和重要验证对象，但不是 V1 最小闭环成立前提。
- 只有 SP-02 / SP-03 通过，并满足只读、来源身份、分层授权、不写回原文时，才进入实现范围。
- 如果 SP-02 / SP-03 失败，降级为手工导入 / 来源指针或移出 V1，并由 PM 记录范围结果。
- 不得在排期或 PRD 中将 Should 静默升级为 Must。

### M-04｜补最小用户验证方案与判定动作

必须定义：

- 目标用户招募门槛。
- 测试使用真实或等价的中断项目。
- 与用户当前拼接工具方式的基线比较。
- 测量恢复可信上下文、找到依据、确认下一步的完成情况与认知负担。
- 需要记录的反证：不愿导入、建议误导、确认成本过高、只被理解为开发者工具等。
- 如果没有明显改善，应如何收窄来源、首页或 AI 建议面，并重审价值假设。

## 非范围

本任务暂时不要做：

- 不重写 P1-001 主交付物。
- 不产出完整 V1 PRD。
- 不产出首页 / 今日页 PRD。
- 不设计首页 / 今日页详细交互。
- 不修改 Stitch。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不执行真实用户访谈或原型测试。
- 不虚构留存、付费或性能数字。
- 不扩大 V1 为全知全能 Agent。
- 不直接冻结 V1 范围；只输出冻结补丁和 PM 冻结建议。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/reviews/LIFEOS-P1-001_pm_review.md`
- `lifeos/reviews/LIFEOS-P1-002_v1_scope_independent_review.md`
- `lifeos/reviews/LIFEOS-P1-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：产品架构负责人必须重点回答：

- 本补丁是否只补齐冻结条件，没有重写或扩大 V1 范围？
- Must / Should / Could / Non-goals 的边界是否更清楚？
- V1 是否仍然服务第一目标用户和第一场景？
- 是否足以防止首页 / 今日页 PRD 误把范围做大？

协审角色必须重点检查：

- 用户研究 / 市场验证负责人：M-04 是否形成可执行的验证合同，而不是泛泛说“做用户访谈”。
- 体验设计负责人：补丁是否给首页 / 今日页 PRD 足够边界，尤其是非焦虑表达、证据不足、权限受限和用户主动选择 Project。
- 数据 / 领域模型负责人：M-01 / M-02 是否继承 Source、Artifact、Derivation、Feedback、Authorization、AuditEntry 和四类命令语义。
- AI 信任与安全负责人：AI 输出身份、用户确认、撤回、删除、派生失效和高风险边界是否保持清楚。
- 技术架构负责人：Obsidian、文件、搜索、AI、导出、审计、撤回 / 删除是否仍然绑定 Spike 和失败降级，不写成已实现承诺。

## 核心问题

请重点回答：

1. P1-002 的 M-01 至 M-04 是否逐项完成？
2. V1 Must 的最小范围合同是什么？
3. 四类命令在 V1 范围层如何被引用和约束？
4. Obsidian 为什么不是 Must？进入 V1 的条件和失败降级是什么？
5. 最小用户验证合同是什么？失败后如何调整范围？
6. 本补丁完成后，哪些内容建议与 P1-001 一起作为 V1 范围冻结基线？
7. 哪些内容仍不应被冻结？
8. 是否建议 PM 冻结 V1 范围？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`

请输出的文件内容包括：

- 文档状态与补丁范围声明
- P1-002 M-01 至 M-04 逐项整改矩阵
- V1 Must 最小范围合同
- 四类命令范围级约束
- Obsidian V1 条件合同
- 最小用户验证合同
- 对 P1-001 的冻结补丁说明
- 建议冻结范围与不冻结范围
- 风险与待确认问题
- 是否建议 PM 冻结 V1 范围

篇幅控制：

- 本任务为补丁 / 条件整改型任务，建议 1500-3000 字。
- 不要重写 P1-001。
- 超出当前整改范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整交付物已保存到指定路径。
- 明确逐项回应 P1-002 的 M-01 至 M-04。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 明确说明本补丁是否建议与 P1-001 一起冻结 V1 范围。
- 明确说明冻结范围和不冻结范围。
- 不修改 P1-001 主交付物。
- 不修改代码、Stitch 或外部系统。
- 不擅自冻结 V1 范围。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 为全知全能 Agent。
- 不启动首页 / 今日页 PRD。
- 不擅自冻结 V1 范围、技术架构或产品原型。
- 不把技术 Spike 计划误认为已经实测通过。
- 不把用户验证合同误认为已经完成用户验证。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
