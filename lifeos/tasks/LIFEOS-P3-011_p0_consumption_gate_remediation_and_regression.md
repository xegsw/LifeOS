# LIFEOS-P3-011 P3-009 P0 消费门返工与回归补测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程返工会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-011
- 任务名称：P3-009 P0 消费门返工与回归补测
- 优先级：P0
- 任务类型：工程返工 / P0 修复 / 回归测试
- 建议篇幅：工程返工报告 1500-3000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要修改 P3-009 工程代码、补充测试、复跑验证并更新 evidence，更适合工程实现型 Agent
- 是否需要后续独立评审：Yes
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P0 修复验证、回归测试、P1 同范围修复评估、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

`LIFEOS-P3-010` 独立工程评审已通过 PM 验收，结论为 `Rework`。独立评审和 PM 复现均确认 `LIFEOS-P3-009` 存在 1 项 P0：

- `canConsume()` 只计数 `decision='allow'` 授权行，不检查 `decision='deny'`。
- 当同一 subject / purpose / location / processor / generation 同时存在 allow 和 deny 时，消费门仍返回 `true`。
- 这违反 H4 “未知 / 冲突即拒绝”原则，也违反 P3-001 历史防线。

P3-009 当前已回退为 `Rework`，不得作为后续工程基线候选。P3-011 的目标是窄范围修复该 P0，并补齐对应反例测试和 evidence。P3-011 完成后仍需独立复评，复评通过前不得恢复 P3-009 工程基线候选。

## 目标

本任务完成后，需要回答：

- P0：allow+deny 授权冲突是否已 fail closed？
- P3-009 原有 10 项测试是否仍然全部通过？
- 是否新增了足够的 P0 回归测试，能防止该漏洞复发？
- P1-1 / P1-2 是否能在不扩大范围的情况下同步修复？
- 修复是否仍未启用真实 Vault、真实 Tauri / IPC、真实数据、外部模型、向量、同步、多设备或 L3？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/` 中与消费门、suggestion、feedback 状态门相关的最小必要代码。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/`，新增 P0 / P1 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限为新增测试 / evidence 统计服务。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程返工报告：`lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 接入真实 Tauri / IPC、真实 Obsidian Vault、真实文件路径、真实用户数据、真实云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 自行关闭 R-0042 或 R-0040。
- 自行启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-010_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0150 至 D-0153 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 修复 P0：
   - `canConsume()` 必须在消费门中处理 deny 授权。
   - 同一 subject / purpose / location / processor / generation 同时存在 allow 和 deny 时，必须 fail closed。
   - 缺失授权、重复 allow、未知 decision、generation / purpose / location / processor / version 错配仍必须 fail closed。
2. 新增 P0 回归测试：
   - allow+deny 冲突不得读取用户原文。
   - allow+deny 冲突不得通过 search / recovery / suggest / exportMemory 等消费入口间接泄漏。
   - duplicate allow 不得被误判为合法唯一授权。
3. 回归 P3-009 原有测试：
   - 原有 10 项迁移测试必须继续通过。
   - 默认关闭能力八项负测必须继续通过。
4. 更新 evidence：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - 如迁移矩阵或默认关闭矩阵需要更新，应同步更新。
5. 输出工程返工报告：
   - `lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`

## P1 同范围处理

在不扩大任务范围、不重构架构、不引入新对象体系的前提下，允许并建议同步处理：

- P1-1：`suggest()` 使用 `INSERT OR REPLACE` 导致重复建议静默重置确认状态。
- P1-2：`feedback()` 不显式检查 derivation status。

处理规则：

- 若能用小范围改动修复，应修复并新增对应测试。
- 若修复会牵涉 `derivation_input`、restore、important_link、复杂 generation staling 或架构重构，应暂不修复，只在报告中列入后续迁移清单。
- P1-3 至 P1-8 不在本任务强制范围内，不得一次性扩散。

## 非范围

本任务暂时不要做：

- 不迁移 P3-001 的全部 23 项测试 / 136 条断言。
- 不实现完整 restore_candidates、important_link、derivation_input、多证据撤回传播、真实文件导出或正式备份恢复协议。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0042 或 R-0040。
- 不创建 P3-012；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- P0 是否被最小改动关闭？
- 原有测试和新增测试是否全部可复跑？
- 代码和 evidence 修改是否严格限制在 P3-009 工程目录与 P3-011 报告？

数据与权限负责人必须重点检查：

- deny、conflict、duplicate allow、missing auth 是否全部 fail closed？
- 所有消费入口是否复用同一消费门，避免绕路？

AI 信任与安全负责人必须重点检查：

- suggestion / feedback 是否避免静默重置用户确认或在 stale 状态继续写入？
- 若 P1 未修复，是否清楚标为后续风险？

QA / 测试负责人必须重点检查：

- 新增 P0 测试是否先能证明旧问题会失败，再证明修复后通过？
- 测试结果是否不是只测 happy path？
- evidence 是否与实际测试一致？

技术架构负责人必须重点检查：

- 是否没有借修复 P0 之名冻结 Schema / API / 模块边界？
- 是否没有启用真实 Tauri / IPC 或其他关闭能力？

## 交付物格式

请将完整返工报告保存为：

`lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P0 根因与修复说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- P1-1 / P1-2 处理结果
- P1-3 至 P1-8 后续迁移清单
- 未启用真实能力声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- P0 allow+deny 冲突已 fail closed。
- 新增 P0 回归测试覆盖 read / search / recovery / suggest / exportMemory 等消费入口。
- 原有 P3-009 测试全部通过。
- P0 失败数为 0；如 P0 失败数大于 0，结论必须为 Rework 或 Blocked。
- Evidence manifest 与测试结果一致。
- P1-1 / P1-2 已修复或明确说明为何留作后续。
- 未修改 P3-001。
- 未修改项目账本。
- 未启用真实能力。
- 已生成指定返工报告。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 交付物路径
- evidence manifest 路径
- 测试摘要
- 是否需要 PM 决策

不要修改项目账本，不要自行启动 P3-012，不要宣布资产冻结或风险关闭。
