# LIFEOS-P3-013 P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口迁移

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-013
- 任务名称：P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口迁移
- 优先级：P1
- 任务类型：工程硬化 / P1 迁移 / 回归测试
- 建议篇幅：工程报告 1500-3000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在 P3-009 目标技术栈最小骨架内做受控代码修改、补测试、更新 evidence，更适合工程实现型 Agent
- 是否需要后续独立评审：Yes
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-3 多证据派生输入迁移、P1-5 important_link 写入口门迁移、H1-H9 回归、默认关闭能力回归、evidence manifest 更新
- 状态：Ready

## 背景

`LIFEOS-P3-012` 独立工程复评已通过 PM 验收，结论为 `Pass`。用户已确认采纳，并授权恢复 `LIFEOS-P3-009` 为后续工程基线候选、关闭 `R-0042`、保持 `R-0040` 为 `Open / Conditional`。

P3-012 同时确认：P3-009 的 P0 消费门问题已关闭，P1-1 / P1-2 已修复；但 P1-3 至 P1-8 仍是未迁移项。PM 判断下一步不应直接接真实 Tauri / IPC 或真实 Vault，而应继续在合成、单进程、受控测试包边界内缩小 P3-001 与 P3-009 的安全不变量差距。

本任务只处理影响面最大的两个缺口：

- P1-3：多证据 `derivation_input` 与非主证据撤回传播。
- P1-5：`important_link` 及其写入口门。

P1-4 / P1-6 / P1-7 / P1-8 暂不在本任务实现，避免范围过大。

## 目标

本任务完成后，需要回答：

- P3-009 是否能记录一个 Derivation 依赖的多个证据版本，而不是只依赖单一 `evidence_version_id`？
- 任一派生输入证据被撤回 / 删除后，相关 Derivation 是否会 stale，并且不得继续导出或接受 feedback？
- 是否能新增 `important_link` 写入口，并确保它必须经过 Project、来源、版本、授权、generation 和证据门检查？
- deny、missing auth、generation mismatch、cross Project、tombstone 后，important_link 是否全部 fail closed？
- 原有 14 项 P3-009 测试是否继续通过？
- 新增 P1 迁移测试是否可复跑，且 evidence manifest 与测试结果一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/` 中与 Derivation 多证据输入、撤回传播、important_link 写入口和消费门复用相关的最小必要代码。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/`，新增 P1-3 / P1-5 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限为新增测试 / evidence 统计服务。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程迁移报告：`lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 接入真实 Tauri / IPC、真实 Obsidian Vault、真实文件路径、真实用户数据、真实云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
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
- `lifeos/tasks/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-012_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0154 至 D-0157 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. P1-3 多证据派生输入：
   - 为 Derivation 记录多个 evidence version / artifact generation / source generation 输入。
   - 派生物不能只凭单一主证据保持 active。
   - 任一输入证据被 revoke / delete 后，相关 Derivation 必须 stale。
   - stale 后不得导出、不得接受 feedback、不得作为下一步候选继续出现。
2. P1-5 important_link 写入口：
   - 新增最小 `important_link` 写入口或等价领域函数。
   - Link 必须显式绑定 Project、from/to Artifact 或 Version、来源身份、确认状态和证据。
   - 写入前必须重检 Project、版本、授权、generation、tombstone 和证据门。
   - deny / missing auth / generation mismatch / cross Project / tombstone 后必须 fail closed。
3. 回归测试：
   - 原有 14 项 P3-009 测试继续通过。
   - 新增 P1-3 测试覆盖多证据、非主证据撤回传播、stale 后 feedback / export / suggest 阻断。
   - 新增 P1-5 测试覆盖合法 Link 写入、deny 后拒绝、cross Project 拒绝、tombstone 后拒绝。
4. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
5. 输出工程迁移报告：
   - `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`

## 非范围

本任务暂时不要做：

- 不迁移 P1-4 独立 generation mismatch staling 机制，除非是 P1-3 的最小必要联动；若触及必须说明边界。
- 不实现完整 P1-6 restore_candidates、权威投影与旧包不复活。
- 不实现 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 不实现 P1-8 suggestion ID 的完整 generation 绑定。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码改动迁移 P1-3 / P1-5？
- 原有 14 项测试和新增测试是否全部可复跑？
- 是否严格限制在 P3-009 工程目录和 P3-013 报告？

数据与权限负责人必须重点检查：

- 多证据依赖是否完整表达，不再只依赖单一主证据？
- 任一证据撤回 / 删除是否能使派生物 stale？
- important_link 写入口是否重检 Project、版本、授权、generation、tombstone 和证据？

AI 信任与安全负责人必须重点检查：

- stale Derivation 是否不能继续作为 AI 建议、导出项或 feedback 目标？
- Link 是否不会把 AI 推断、用户确认事实、外部引用来源混成同一种身份？

QA / 测试负责人必须重点检查：

- 新增测试是否不是 happy path。
- 是否覆盖撤回、删除、deny、cross Project、generation mismatch、tombstone。
- evidence 是否与实际测试一致。

技术架构负责人必须重点检查：

- 是否没有借 P1 迁移冻结生产 Schema / API / 模块边界？
- 是否没有启用真实 Tauri / IPC 或其他关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程迁移报告保存为：

`lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P1-3 迁移说明
- P1-5 迁移说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- P1-4 / P1-6 / P1-7 / P1-8 后续迁移状态
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- P1-3 多证据派生输入已实现并有测试。
- 任一派生输入证据撤回 / 删除后，相关 Derivation 会 stale，且 feedback / export / suggest 阻断。
- P1-5 important_link 写入口已实现并有测试。
- Link 写入口在 deny、missing auth、generation mismatch、cross Project、tombstone 后 fail closed。
- 原有 P3-009 测试全部通过。
- P0 失败数为 0；P1 迁移测试全部通过。
- Evidence manifest 与测试结果一致。
- 未修改 P3-001。
- 未修改项目账本。
- 未启用真实能力。
- 已生成指定工程迁移报告。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 交付物路径
- evidence manifest 路径
- 测试摘要
- 是否需要 PM 决策

不要修改项目账本，不要自行启动 P3-014，不要宣布资产冻结或风险关闭。
