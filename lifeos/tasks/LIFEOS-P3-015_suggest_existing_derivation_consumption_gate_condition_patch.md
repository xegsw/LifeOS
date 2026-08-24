# LIFEOS-P3-015 P3-014 条件补丁：suggest 已有 Derivation 输入消费门补强

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程补丁会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-015
- 任务名称：P3-014 条件补丁：suggest 已有 Derivation 输入消费门补强
- 优先级：P1
- 任务类型：补丁 / 条件整改型任务 / 工程硬化 / 回归测试
- 建议篇幅：1500-3000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：Codex
- 推荐理由：本任务是很窄的工程补丁，需要在 P3-009 受控工程目录内改代码、补测试、复跑验证并更新 evidence，更适合工程执行型 Agent
- 是否需要后续独立评审：Conditional；若只关闭本条件且 PM 复核通过，可由 PM 决定是否需要轻量复评
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P3-014 条件关闭、suggest 已有 Derivation 输入消费门回归、P1-3 / P1-5 回归、H1-H9 / T-ARCH 回归、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

`LIFEOS-P3-014` 独立工程复评已通过 PM 验收，但 PM 将专项会话的 `Pass` 调整为 `Pass with Conditions`。

条件原因：

- P3-014 发现 `suggest()` 在“已有 Derivation 返回路径”上仅检查 `status === "stale"`，没有调用 `derivationInputsConsumable()`。
- PM 定向复现确认：先创建基于 `artifact-1` 与 `artifact-2` 的 suggestion，再直接将非主证据 `artifact-1` 的 authorization 改为 `deny`，不调用 `control()`；随后再次调用 `suggest("project-orbit", evidence)`，旧 suggestion 仍会返回。
- `feedback()` 与 `exportMemory()` 已经通过 `derivationInputsConsumable()` 阻断，所以该问题当前不构成 P0。
- 但 `suggest()` 也是 AI 建议消费入口，返回已有 Derivation 前必须重检全部派生输入证据，否则会破坏 P1-3 多证据约束的一致性。

本任务只关闭这个条件，不迁移其它 P1 项。

## 目标

本任务完成后，需要回答：

- `suggest()` 在返回已有 Derivation 前，是否会调用 `derivationInputsConsumable()`？
- 任一已记录 `derivation_input` 不可消费时，`suggest()` 是否返回 null，而不是返回旧候选？
- 直接 deny 非主证据但不调用 `control()` 后，旧 suggestion 是否不再返回？
- P3-013 已完成的 P1-3 / P1-5 测试是否继续通过？
- 原有 18 项 P3-009 测试是否继续通过，并新增本补丁回归测试？
- evidence manifest、test_results、test_run.log、矩阵文件是否更新且一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` 中与 `suggest()` 返回已有 Derivation 前输入消费门重检相关的最小必要代码。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`，新增 direct-deny 非主证据后 `suggest()` 不得返回旧候选的回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限为新增测试 / evidence 统计服务；如果不需要修改，应说明无需修改。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程补丁报告：`lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 迁移 P1-4、P1-6、P1-7、P1-8。
- 顺手清理 `feedback()` 的 `INSERT OR REPLACE`、`validate.mjs` 的 P0/P1 统计、自引用 Link 或夹具多样性等 P2 观察项。
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
- `lifeos/tasks/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration.md`
- `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-013_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-014_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0158 至 D-0161 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 条件补丁实现：
   - `suggest()` 在已有 Derivation 存在时，不得只检查 `status !== "stale"`。
   - 返回已有 Derivation 前必须调用 `derivationInputsConsumable(id, evidence)` 或等价的全输入消费门检查。
   - 若任一 `derivation_input` 缺失、伪造、generation mismatch、source generation mismatch、authorization deny / missing / conflict / unknown、tombstone 或 Project 不匹配，`suggest()` 必须返回 null。
2. 新增回归测试：
   - 创建 suggestion 后，直接 deny 非主证据 authorization，不调用 `control()`。
   - 再次调用 `suggest()` 时必须返回 null。
   - 同时验证 `feedback()` 和 `exportMemory()` 仍阻断，不引入回归。
3. 原有回归：
   - P3-013 的 P1-3 / P1-5 测试继续通过。
   - P3-011 的 P0 消费门测试继续通过。
   - H1-H9 / T-ARCH 继续通过。
4. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
5. 输出工程补丁报告：
   - `lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`

## 非范围

本任务暂时不要做：

- 不迁移 P1-4 独立 generation mismatch staling 机制。
- 不实现 P1-6 restore_candidates、权威投影与旧包不复活。
- 不实现 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 不实现 P1-8 suggestion ID 的完整 generation 绑定。
- 不清理 `feedback()` 的 `INSERT OR REPLACE`。
- 不改造 `validate.mjs` 的 P0/P1 统计，除非测试数量统计因本任务新增测试必须调整。
- 不禁止 self-link，除非当前测试必须触及；若发现只记录为后续建议。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码改动关闭 P3-014 条件？
- 是否没有顺手迁移其它 P1 或 P2 清洁项？
- 原有 18 项测试和新增测试是否全部可复跑？

数据与权限负责人必须重点检查：

- `suggest()` 是否和 feedback / export 一样重检全部 `derivation_input`？
- 直接 deny、missing、conflict、unknown 或 generation mismatch 是否能阻断旧候选返回？

AI 信任与安全负责人必须重点检查：

- AI suggestion 是否不再使用不可消费证据继续出现？
- 该补丁是否保持 AI 建议、用户原文、用户确认、外部来源身份分离？

QA / 测试负责人必须重点检查：

- 新增测试是否真实复现 P3-014 条件问题，而不是只验证 happy path？
- evidence 是否与实际测试结果一致？

技术架构负责人必须重点检查：

- 是否没有冻结生产 Schema / API / 模块边界？
- 是否没有启用真实 Tauri / IPC 或其它关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程补丁报告保存为：

`lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P3-014 条件关闭说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- P1-4 / P1-6 / P1-7 / P1-8 仍未迁移声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- `suggest()` 已有 Derivation 返回路径已重检全部 `derivation_input`。
- direct-deny 非主证据但不调用 `control()` 后，旧 suggestion 不再返回。
- `feedback()` 与 `exportMemory()` 阻断能力未回退。
- 原有 18 项 P3-009 测试继续通过。
- 新增 P3-015 回归测试通过。
- P0 失败数为 0。
- Evidence manifest 与测试结果一致。
- 未修改 P3-001。
- 未修改项目账本。
- 未启用真实能力。
- 已生成指定工程补丁报告。
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

