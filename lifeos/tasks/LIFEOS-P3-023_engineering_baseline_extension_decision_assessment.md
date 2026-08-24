# LIFEOS-P3-023｜工程基线扩展恢复 / 冻结候选决策评估

## 任务信息

- 任务 ID：LIFEOS-P3-023
- 任务名称：工程基线扩展恢复 / 冻结候选决策评估
- 优先级：P0
- 任务类型：决策型任务 / 独立评估
- 建议篇幅：1000-2000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要站在独立评审、反例攻击、风险复核和工程治理角度，判断 P3-009 是否具备恢复 / 冻结候选条件；不应由持续执行 P3-009 工程补丁的 Codex 自证。
- 是否需要后续独立评审：No（本任务自身为独立评估；若结论建议恢复 / 冻结工程基线，PM 与用户确认后再另行决定是否需要复评）
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 独立工程评审
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：WorkBuddy 独立评审 / 风险评估会话
- 推荐复用的会话：若已有执行 `LIFEOS-P3-020` 或 `LIFEOS-P3-021` 的 WorkBuddy 独立评审线会话，优先复用；否则新建 WorkBuddy 独立评估会话。
- 会话判断理由：本任务延续 P3-020 / P3-021 的只读评审和风险判断链路，适合复用独立评审上下文；但不得复用 Codex 工程执行会话作为最终评估者。
- 是否需要独立性隔离：Yes，与 P3-009 / P3-015 至 P3-022 工程执行会话隔离。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - 本任务卡明确列出的输入材料
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 可复用既有读取结果：
  - 若同一 WorkBuddy 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-022_pm_review.md`
- 任务完成后是否建议保留会话：Yes，作为后续工程基线 / 风险复评线会话保留。

## 背景

P3-009 目标技术栈最小骨架已被恢复为后续工程基线候选，并在 P3-013 至 P3-019 中完成 P1-3 至 P1-8 受控迁移。P3-020 独立复评给出 Pass with Conditions，确认 P1 迁移在合成、单进程、受控测试包边界内完成，但明确不关闭 R-0040，也不恢复 / 冻结工程基线扩展。P3-021 已建议并经用户确认：R-0040 保持 Open / Conditional，不关闭、不拆分。P3-022 又清理了三个 P2 工程噪音项，PM 验收为 Accepted。

现在需要一个只读决策评估任务，判断在“不关闭 R-0040、不启用真实能力、不进入下一阶段”的前提下，P3-009 是否已经足够作为后续受控工程任务的扩展基线；以及是否应进入“恢复 / 冻结工程基线扩展”的用户决策流程。

## 目标

本任务完成后，PM 应能清楚判断：

- P3-009 当前是否具备“受控工程基线扩展候选”的最低条件。
- 是否建议恢复 P3-009 作为后续受控工程任务的工程基线扩展。
- 是否建议冻结该工程基线扩展；若不建议，缺哪些条件。
- 即使建议恢复 / 冻结，哪些能力仍必须保持关闭。
- 是否需要用户确认、独立复评或后续补丁任务。

## 范围

本任务必须覆盖：

- 核对 P3-009 当前 evidence manifest、测试结果和 P3-020 / P3-021 / P3-022 结论是否一致。
- 判断 P3-013 至 P3-022 形成的工程链路是否足以支持“受控工程基线扩展候选”。
- 明确区分：
  - 任务 Accepted
  - 工程基线候选
  - 工程基线恢复
  - 工程基线冻结
  - 真实能力启用
  - R-0040 风险关闭
- 给出 2-4 个 PM 决策选项，至少包含：
  - A：保持现状，仅作为候选，不恢复 / 不冻结。
  - B：恢复为受控工程基线扩展，但不冻结、不关闭 R-0040。
  - C：进入冻结准备流程，但需列出冻结前硬条件。
  - D：不建议恢复，需返工或补充验证。
- 推荐一个首选选项，并说明理由。
- 列出如果 PM / 用户选择恢复或冻结，必须追加的控制条件。

## 非范围

本任务暂时不要做：

- 不修改任何工程代码、测试、evidence 或项目账本。
- 不关闭 R-0040，不拆分 R-0040。
- 不恢复工程基线，不冻结工程基线。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不把 P3-009 合成单进程测试外推为真实 Tauri / IPC、真实 Vault、生产 Schema / API / 导出格式或 SLA 通过。
- 不重新设计技术架构，不改变技术架构 V0.1 冻结合同。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-020_p1_migration_completion_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-020_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-021_r0040_closure_condition_assessment.md`
- `lifeos/reviews/LIFEOS-P3-021_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-022_p2_engineering_cleanup_batch_patch.md`
- `lifeos/reviews/LIFEOS-P3-022_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`，只读任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 当前 evidence 是否足够支持受控工程基线扩展候选。
- 恢复 / 冻结工程基线会不会越过技术架构 V0.1 合同边界。
- 哪些条件属于恢复前必须满足，哪些属于冻结前必须满足。

协审角色必须重点检查：

- AI 建议可信度、用户反馈、撤回、导出、恢复候选、证据链是否仍不被旧包或旧建议复活。
- 用户原文、AI 派生、用户确认事实、外部来源边界是否被工程报告混淆。
- P3-022 清洁项是否真的降低了误读风险，而不是掩盖 R-0040。

## 核心问题

请重点回答：

- P3-009 当前最适合处于哪个状态：候选 / 可恢复 / 可冻结 / 不可恢复？
- 若建议恢复，恢复范围应如何限定？
- 若建议冻结，冻结前还缺哪些硬条件？
- R-0040 保持 Open / Conditional 时，是否允许恢复受控工程基线扩展？为什么？
- 下一步 PM 应让用户确认什么？

## 交付物

请将完整交付物保存为 Markdown 文件，路径建议：

`lifeos/deliverables/LIFEOS-P3-023_engineering_baseline_extension_decision_assessment.md`

请输出的文件内容包括：

- 结论摘要
- 事实依据
- 决策选项 A / B / C / D
- 推荐选项
- 恢复范围建议
- 冻结前硬条件
- 不可越过边界
- R-0040 状态影响
- 角色检查点结果
- 需要 PM / 用户确认的问题
- 后续任务建议

篇幅控制：

- 决策型任务建议 1000-2000 字。
- 超出范围的分析、方案或问题，放入“后续任务建议”，不要在当前任务正文无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 不把本评估结论写成已恢复、已冻结、已关闭风险或已启用真实能力。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改项目账本。
- 不关闭 R-0040。
- 不恢复或冻结工程基线。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不自行启动后续任务。

## 给专项会话的可复制启动提示词

请先读取当前项目根目录的 `AGENTS.md`，并按其中规则执行 LifeOS 专项任务。

任务文件：

`lifeos/tasks/LIFEOS-P3-023_engineering_baseline_extension_decision_assessment.md`

请注意：你是专项独立评估会话，不是 PM 主会话。只读评估，不修改工程文件、Stitch 或项目账本；不得关闭 R-0040，不得恢复 / 冻结工程基线，不得进入下一阶段，不得启用真实能力。完整交付物写入任务卡指定路径，聊天回复只输出摘要、交付物路径、预检路径和是否需要 PM 决策。

