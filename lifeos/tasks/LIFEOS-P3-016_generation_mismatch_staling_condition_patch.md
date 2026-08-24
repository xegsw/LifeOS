# LIFEOS-P3-016 P1-4 条件补丁：独立 generation mismatch staling 机制

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程补丁会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-016
- 任务名称：P1-4 条件补丁：独立 generation mismatch staling 机制
- 优先级：P1
- 任务类型：P3 Engineering Fast Lane / 补丁 / 条件整改型任务 / 工程硬化 / 回归测试
- 建议篇幅：800-1500 字；详细日志写入 evidence，不粘贴到报告正文
- 是否适用 P3 Engineering Fast Lane：Yes
- 推荐执行 Agent：Codex
- 推荐理由：本任务是 P3-009 受控工程目录内的窄范围工程补丁，需要修改 TypeScript 代码、补测试、复跑验证并更新 evidence，更适合工程执行型 Agent
- 是否需要后续独立评审：No；若 PM 验收发现 P0、范围扩张或触及真实能力，再退出快车道并另行安排
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-4 generation mismatch staling、suggest / feedback / export 回归、P1-3 / P1-5 / P3-015 回归、H1-H9 / T-ARCH 回归、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

`LIFEOS-P3-010` 独立工程评审指出 P3-009 缺少 P1-4：独立 generation mismatch staling 机制。P3-013 / P3-015 已经让消费入口在 generation mismatch 时 fail closed，但目前仍主要依赖消费门“拒绝使用”，不等于把已存在的旧 Derivation 主动标记为 `stale`。

在 LifeOS 的长期外脑语义里，派生内容不仅要在消费时被挡住，还要能在权威原文、Source 或输入 generation 变化后，主动呈现为“已失效”。否则 UI、恢复包、审计或后续任务可能看到一个状态仍为 `candidate` 的旧 AI 建议，造成信任混乱。

本任务只补 P1-4，不迁移 P1-6 / P1-7 / P1-8。

## 目标

本任务完成后，需要回答：

- 当已记录 `derivation_input.artifact_generation` 与当前 Artifact generation 不一致时，相关 Derivation 是否会被主动标记为 `stale`？
- 当已记录 `derivation_input.source_generation` 与当前 Source generation 不一致时，相关 Derivation 是否会被主动标记为 `stale`？
- generation mismatch 后，`suggest()`、`feedback()`、`exportMemory()` 是否全部阻断旧 Derivation？
- 这次 staling 是否独立于 `control("revoke" | "delete")`，也就是不依赖 tombstone / deny side effect？
- 原有 19 项 P3-009 测试是否继续通过，并新增 P1-4 回归测试？
- evidence manifest、test_results、test_run.log、矩阵文件是否更新且一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` 中与 generation mismatch 主动 staling 相关的最小必要代码。
- 如确有必要，可修改 `lifeos/engineering/LIFEOS-P3-009/src/store.ts` 或 `src/types.ts`，但必须说明原因，并保持最小改动。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`，新增 P1-4 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限同步新增测试统计、snapshot 和 evidence 内容。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程快车道短报告：`lifeos/deliverables/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 迁移 P1-6 restore candidates、P1-7 `expires_at` / `retract_feedback`、P1-8 suggestion ID 完整 generation 绑定。
- 顺手清理 `feedback()` 的 `INSERT OR REPLACE`、validate 统计结构、自引用 Link、夹具多样性或其它 P2 清洁项。
- 接入真实 Tauri / IPC、真实 Obsidian Vault、真实文件路径、真实用户数据、真实云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 自行关闭 R-0040 或新增 / 关闭风险。
- 自行启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`
- `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-015_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0160 至 D-0164 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 独立 staling 实现：
   - 当 `derivation_input.artifact_generation` 与当前 Artifact generation 不一致时，相关 Derivation 必须被标记为 `stale`。
   - 当 `derivation_input.source_generation` 与当前 Source generation 不一致时，相关 Derivation 必须被标记为 `stale`。
   - 该 staling 机制不得依赖 `control("revoke" | "delete")` 的 tombstone / deny side effect。
   - 可在 `suggest()`、`feedback()`、`exportMemory()` 等消费入口前调用该机制，或采用等价的最小实现；但必须保证旧 Derivation 状态最终变为 `stale`，不能只返回 `null`。
2. 新增回归测试：
   - 创建 suggestion 后，直接修改某个已记录输入的 Artifact generation，不调用 `control()`。
   - 触发消费入口后，断言相关 Derivation 被主动标记为 `stale`。
   - 验证 `suggest()`、`feedback()`、`exportMemory()` 均阻断旧 Derivation。
   - 覆盖 Source generation mismatch；可以单独测试，也可以在同一测试中覆盖，但断言必须清楚。
3. 原有回归：
   - P3-015 direct-deny 测试继续通过。
   - P1-3 / P1-5 测试继续通过。
   - P3-011 P0 消费门测试继续通过。
   - H1-H9 / T-ARCH 继续通过。
4. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
5. 输出工程快车道短报告：
   - `lifeos/deliverables/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`

## 非范围

本任务暂时不要做：

- 不迁移 P1-6 restore_candidates、权威投影与旧包不复活。
- 不迁移 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 不迁移 P1-8 suggestion ID 的完整 generation 绑定。
- 不重构 suggestion ID 生成策略；除非为 P1-4 的最小测试不可避免，否则只记录为后续建议。
- 不清理 `feedback()` 的 `INSERT OR REPLACE`。
- 不改造导出格式、恢复包格式、真实文件导出或真实备份。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码补上独立 generation mismatch staling？
- 是否没有顺手迁移 P1-6 / P1-7 / P1-8 或其它清洁项？
- 原有 19 项测试和新增 P1-4 测试是否全部可复跑？

数据与权限负责人必须重点检查：

- Derivation 的 `stale` 状态是否真实来自当前权威 Artifact / Source generation 与已记录输入 generation 的错配？
- 是否同时覆盖 artifact generation 与 source generation？
- 该机制是否仍以 `derivation_input` 全集为准，而不是只看主证据字段？

AI 信任与安全负责人必须重点检查：

- generation mismatch 后，旧 AI suggestion 是否不能继续作为可用候选出现？
- 用户是否不会看到状态仍为 `candidate` 的失效 AI 派生物？
- 该补丁是否保持用户原文、AI 建议、用户反馈和外部来源身份分离？

QA / 测试负责人必须重点检查：

- 新增测试是否真实制造 generation mismatch，而不是只验证 tombstone / deny / control happy path？
- 测试是否断言 Derivation 状态变为 `stale`，而不仅仅断言消费入口返回 `null`？
- evidence 是否与实际测试结果一致？

技术架构负责人必须重点检查：

- 是否没有冻结生产 Schema / API / 模块边界？
- 是否没有启用真实 Tauri / IPC 或其它关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程快车道短报告保存为：

`lifeos/deliverables/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`

报告建议使用：

`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P1-4 条件关闭说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- P1-6 / P1-7 / P1-8 仍未迁移声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- generation mismatch 时，相关 Derivation 会被主动标记为 `stale`。
- artifact generation mismatch 已覆盖。
- source generation mismatch 已覆盖。
- `suggest()`、`feedback()`、`exportMemory()` 不使用旧 Derivation。
- 机制不依赖 `control()`、tombstone 或 deny side effect。
- 原有 19 项 P3-009 测试继续通过。
- 新增 P1-4 回归测试通过。
- P0 失败数为 0。
- Evidence manifest 与测试结果一致。
- 未修改 P3-001。
- 未修改项目账本。
- 未启用真实能力。
- 已生成指定工程快车道短报告。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 交付物路径
- evidence manifest 路径
- 测试摘要
- 是否需要 PM 决策

不要修改项目账本，不要自行宣布工程基线扩展完成，不要关闭 R-0040，不要自行启动后续任务。

