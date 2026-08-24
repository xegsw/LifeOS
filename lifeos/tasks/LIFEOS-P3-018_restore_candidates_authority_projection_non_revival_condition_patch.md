# LIFEOS-P3-018 P1-6 条件补丁：restore candidates、权威投影与旧包不复活

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程补丁会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-018
- 任务名称：P1-6 条件补丁：restore candidates、权威投影与旧包不复活
- 优先级：P1
- 任务类型：P3 Engineering Fast Lane / 补丁 / 条件整改型任务 / 工程硬化 / 回归测试
- 建议篇幅：800-1500 字；详细日志写入 evidence，不粘贴到报告正文
- 是否适用 P3 Engineering Fast Lane：Yes
- 推荐执行 Agent：Codex
- 推荐理由：本任务是 P3-009 受控工程目录内的窄范围工程补丁，需要修改 TypeScript 代码、补测试、复跑验证并更新 evidence，更适合工程执行型 Agent
- 是否需要后续独立评审：No；若 PM 验收发现 P0、范围扩张、真实恢复写入或触及真实能力，再退出快车道并另行安排
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-6 restore candidates、权威投影、旧包不复活、P1-8 suggestion ID 回归、P1-4 staling 回归、P3-015 suggest 旧候选消费门回归、P1-3 / P1-5 回归、H1-H9 / T-ARCH 回归、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

P3-014 独立工程复评记录了 P1-6 未迁移：restore candidates、权威投影与旧包不复活。P2-019 / P2-020 已将“基础导出 / 恢复候选与不复活验证”列为最小纵向切片的 Must 边界；当前 P3-009 只有受控内存 `exportMemory()`，能够验证 Project 闭包和当前合法导出，但还没有独立表达：

- 导出 / 恢复包中到底基于哪一代权威 Artifact、Source、Authorization 和 Derivation 输入。
- 旧包在权威状态变化后如何变成不可恢复候选。
- 删除、撤回、generation 变化、stale 派生是否能在恢复候选阶段被拦截，而不是等真正导入后才发现。

本任务只做合成、单进程、内存测试包内的 P1-6 最小补丁：允许生成和评估 restore candidates，但不得执行真实文件导出、真实导入、真实备份恢复或写回权威数据。它不迁移 P1-7，不关闭 R-0040，不启用真实能力。

## 目标

本任务完成后，需要回答：

- `exportMemory()` 或等价受控导出包是否包含可核对的权威投影，而不是只有无上下文的 artifacts / derivations？
- restore candidates 是否在恢复前基于当前权威状态重检 Project、version、Artifact generation、Source generation、Authorization、tombstone、Derivation status 与 derivation inputs？
- 旧包在删除 / 撤回后是否不能复活 Artifact 或 Derivation？
- 旧包在 Artifact 或 Source generation 变化后是否不能复活旧内容或旧 AI 建议？
- restore candidates 是否只是候选 / 诊断输出，不会把旧包写回权威表？
- 原有 25 项 P3-009 测试是否继续通过，并新增 P1-6 回归测试？
- evidence manifest、test_results、test_run.log、矩阵文件是否更新且一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` 中与受控内存导出包、权威投影、restore candidates 评估相关的最小必要代码。
- 如确有必要，可修改 `lifeos/engineering/LIFEOS-P3-009/src/types.ts` 或 `src/store.ts`，但必须说明原因，并保持最小改动。
- 可以新增只读/候选型方法，例如 `restoreCandidates(...)`、`evaluateRestoreCandidates(...)` 或等价命名；该方法不得写入 `artifact`、`artifact_version`、`source`、`authorization`、`derivation`、`feedback`、`important_link` 等权威表。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`，新增 P1-6 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限同步新增测试统计、snapshot 和 evidence 内容。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程快车道短报告：`lifeos/deliverables/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 实现真实文件导出、真实导入、真实备份恢复、真实路径选择或正式导出格式。
- 把 restore candidate 直接写回权威库，或实现“正式重导入”。
- 迁移 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 顺手重构 `feedback()` 的 `INSERT OR REPLACE`、自引用 Link、夹具多样性、真实 UI、真实 IPC 或其它 P2 清洁项。
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
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-020_min_vertical_slice_engineering_task_card.md`
- `lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-017_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 对 P2-019 / P2-020 只需定向读取“导出 / 恢复候选、不复活、H4/H5/H9/T-ARCH”相关段落，不要全量展开成新 PRD。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0163 至 D-0168 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 权威投影：
   - 受控导出包必须能表达恢复判断所需的最小权威投影。
   - 每个可恢复候选至少应能核对：Project、Artifact、Artifact version、Source、Artifact generation、Source generation、Authorization decision / generation、tombstone 状态。
   - Derivation 候选必须能核对：Derivation status、evidence version、完整 `derivation_input` 集合及其 Artifact / Source generation。
2. Restore candidates 评估：
   - 新增候选评估能力，只输出候选状态与原因，不直接写回权威表。
   - 候选状态可以采用 `restorable` / `blocked` / `stale` / `excluded` 或等价表达，但必须清楚。
   - 评估前必须基于当前权威库重检，不信任旧包自带结论。
3. 旧包不复活：
   - 先导出包，再执行 revoke / delete，随后用旧包评估 restore candidates，Artifact 和 Derivation 必须不可恢复。
   - 先导出包，再让 Artifact generation 变化，随后旧包不可复活旧 Artifact 或旧 Derivation。
   - 先导出包，再让 Source generation 变化，随后旧包不可复活旧 Artifact 或旧 Derivation。
   - stale / invalid Derivation 不得作为可恢复 AI 建议出现。
4. 非写入保证：
   - restore candidate 评估不得增加 `artifact`、`artifact_version`、`source`、`authorization`、`derivation`、`feedback`、`important_link` 等权威表行数。
   - 不得把旧包内容写入 FTS、outbox 或其它 active projection。
5. 原有回归：
   - P1-8 suggestion ID 完整 generation 绑定测试继续通过。
   - P1-4 generation mismatch staling 测试继续通过。
   - P3-015 direct-deny 测试继续通过。
   - P1-3 / P1-5 测试继续通过。
   - P3-011 P0 消费门测试继续通过。
   - H1-H9 / T-ARCH 继续通过。
6. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
7. 输出工程快车道短报告：
   - `lifeos/deliverables/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`

## 非范围

本任务暂时不要做：

- 不实现正式导出格式、正式重导入流程、真实文件写入、真实备份恢复或路径权限。
- 不把 restore candidates 变成自动恢复、自动合并或自动覆盖。
- 不迁移 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 不改造真实 UI、真实 Tauri / IPC、真实 Obsidian Vault 或真实导出目录。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码补上 restore candidates 与权威投影？
- restore candidate 评估是否只读、不写回权威表？
- 是否没有顺手迁移 P1-7 或其它清洁项？
- 原有 25 项测试和新增 P1-6 测试是否全部可复跑？

数据与权限负责人必须重点检查：

- 权威投影是否足以判断 Project、version、Source、Authorization、tombstone 和 generation？
- 旧包是否不能绕过当前权威状态？
- Derivation 候选是否仍以完整 `derivation_input` 集合为准？

AI 信任与安全负责人必须重点检查：

- 旧 AI suggestion 是否不会通过恢复候选重新变成可用建议？
- stale / invalid / 证据错配的 Derivation 是否被阻断？
- 是否保持用户原文、AI 建议、用户反馈和外部来源身份分离？

QA / 测试负责人必须重点检查：

- 测试是否真实模拟“先导出旧包，再删除 / 撤回 / generation 变化，再评估旧包”？
- 测试是否断言没有权威表写入副作用？
- evidence 是否与实际测试结果一致？

技术架构负责人必须重点检查：

- 是否没有新增外部依赖或引入重型恢复系统？
- 是否没有冻结正式导出 / 恢复格式或生产 Schema / API？
- 是否没有启用真实 Tauri / IPC、真实文件导出或其它关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程快车道短报告保存为：

`lifeos/deliverables/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`

报告建议使用：

`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P1-6 条件关闭说明
- restore candidates / 权威投影设计说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- P1-7 仍未迁移声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 受控导出包包含恢复判断所需的最小权威投影。
- restore candidates 评估基于当前权威状态，不信任旧包自带结论。
- revoke / delete 后，旧包不可复活 Artifact 或 Derivation。
- Artifact generation 变化后，旧包不可复活旧 Artifact 或旧 Derivation。
- Source generation 变化后，旧包不可复活旧 Artifact 或旧 Derivation。
- stale / invalid Derivation 不会作为可恢复 AI 建议出现。
- restore candidate 评估不写回权威表、FTS 或 outbox。
- 原有 25 项 P3-009 测试继续通过。
- 新增 P1-6 回归测试通过。
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
