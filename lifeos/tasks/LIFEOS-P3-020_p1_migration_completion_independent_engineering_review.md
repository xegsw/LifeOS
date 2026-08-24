# LIFEOS-P3-020 P3-009 P1 迁移完成独立工程覆盖复评

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`

你是 LifeOS 项目的专项独立工程复评会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-020
- 任务名称：P3-009 P1 迁移完成独立工程覆盖复评
- 优先级：P1
- 任务类型：独立评审型任务 / 工程覆盖复评 / 反例攻击 / Evidence 一致性检查
- 建议篇幅：2000-4000 字；详细测试日志写入或引用 evidence，不粘贴到聊天回复
- 是否适用 P3 Engineering Fast Lane：No。此任务是快车道后的独立覆盖复评，不是继续补丁实现
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要独立视角复核 P3-009 在 P1-3 至 P1-8 迁移后的覆盖完整性、反例攻击和证据一致性；不应由刚执行多项补丁的 Codex 自证闭环
- 是否需要后续独立评审：No，本任务自身就是独立工程复评；若发现 P0 / Rework，需回到 PM 主会话判断后续返工
- 是否允许修改工程文件：No。只允许只读复核；如需复跑测试，可使用临时副本或只读命令，不得修改 `lifeos/engineering/LIFEOS-P3-009/` 源码、测试或 evidence
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人 / 反例攻击负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-3 / P1-4 / P1-5 / P1-6 / P1-7 / P1-8 覆盖完整性、H1-H9 / T-ARCH 回归、P0 消费门回归、evidence 一致性、默认关闭能力、R-0040 边界不误关
- 状态：Ready

## 背景

P3-009 是目标技术栈最小工程骨架与 P3-001 不变量迁移，已在 P3-011 / P3-012 关闭 P0 消费门问题并恢复为后续工程基线候选。随后 P3-013 至 P3-019 在受控边界内陆续完成 P1 迁移：

- P3-013：P1-3 多证据 `derivation_input` 与 P1-5 `important_link` 写入口门迁移。
- P3-014：对 P3-013 做独立工程复评，发现 `suggest()` 旧候选返回路径条件缺口。
- P3-015：关闭 `suggest()` 已有 Derivation 输入消费门缺口。
- P3-016：关闭 P1-4 Artifact / Source generation mismatch 主动 staling。
- P3-017：关闭 P1-8 suggestion ID 完整 generation 绑定。
- P3-018：关闭 P1-6 restore candidates、权威投影与旧包不复活。
- P3-019：关闭 P1-7 授权 `expires_at` 与 `retract_feedback`。

PM 已验收 P3-019，当前 evidence 显示 P3-009 受控测试包为 34 PASS / 0 FAIL / P0=0。但这仍是执行链路的逐项补丁证据，不能自动等同于“P1 迁移整体完成、R-0040 可关闭、工程基线扩展可恢复或冻结”。因此需要独立工程覆盖复评。

## 目标

本任务完成后，需要回答：

- P3-009 当前版本是否真实覆盖 P1-3 / P1-4 / P1-5 / P1-6 / P1-7 / P1-8，而不是仅覆盖每次补丁的局部 happy path？
- 当前 34 项测试、evidence manifest、test_results、test_run.log、矩阵文件是否一致且可复核？
- 是否仍存在 P0 或 P1 缺口，足以阻止后续考虑关闭 R-0040 或恢复 / 冻结工程基线扩展？
- `read`、`search`、`recovery`、`suggest`、`feedback`、`exportMemory`、`restoreCandidates`、`createImportantLink` 是否在撤回、删除、deny、过期、generation mismatch、旧包、feedback 撤回后均 fail closed？
- P1-3 至 P1-8 的组合场景是否存在互相打架：例如 restore candidate 与过期授权、feedback 撤回与 confirmed Derivation、suggestion ID 与 generation staling、important_link 与非主证据撤回。
- 是否有任何代码、报告或 evidence 把合成测试通过误写成真实 Tauri / IPC、真实 Vault、真实数据、生产 Schema / API、导出格式或 SLA 通过？
- 本次复评是否建议 PM 后续启动 R-0040 关闭条件任务、工程基线扩展恢复任务，或要求返工？

## 授权范围

允许：

- 只读检查 `lifeos/engineering/LIFEOS-P3-009/` 当前源码、测试、脚本与 evidence。
- 如本地环境允许，复跑：
  - `cd lifeos/engineering/LIFEOS-P3-009 && node scripts/validate.mjs`
  - 若系统无全局 Node，可尝试使用 Codex bundled Node；若不可用，必须说明原因并改为只读 evidence 复核。
- 构造反例攻击清单并以只读方式判断当前测试是否覆盖；如需运行临时反例代码，只能在临时目录或临时副本中进行，不得修改原工程目录。
- 阅读 P3-013 至 P3-019 的任务卡、交付物、PM Review 和最新 evidence manifest。
- 输出独立复评文件到：`lifeos/reviews/LIFEOS-P3-020_p1_migration_completion_independent_engineering_review.md`。
- 调用本地预检检查评审文件。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/` 源码、测试、脚本或 evidence。
- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 新增工程补丁、修复代码或重写测试。
- 关闭 R-0040，或自行宣布 R-0040 可关闭。
- 恢复、冻结或扩展工程基线。
- 启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 修改 Stitch、PRD、技术架构冻结合同或产品范围。
- 自行启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration.md`
- `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/tasks/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-015_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-016_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-017_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-018_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-019_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-009/evidence/invariant_migration_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/architecture_conformance.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/default_off_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取当前任务直接依赖文件，不主动全量翻历史。
- 对 P3-013 至 P3-019 的交付物和 PM Review，只需定向读取任务结论、修改范围、测试摘要、非范围、剩余风险和 PM 验收判断。
- 对工程目录，优先读取 `src/`、`tests/invariants.test.ts`、`scripts/validate.mjs`、`evidence/MANIFEST.md` 和矩阵文件；不要无差别读取全部日志，除非发现 evidence 冲突。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0157 至 D-0172 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. Evidence 一致性：
   - `MANIFEST.md`、`test_results.json`、`test_run.log`、`invariant_migration_matrix.md`、`architecture_conformance.md`、`default_off_matrix.md` 是否一致。
   - 当前结果是否确为 34 PASS / 0 FAIL / P0=0。
   - Snapshot、运行环境、测试数量、P1 分类计数是否一致。
2. P1-3 覆盖复核：
   - Derivation 是否记录完整 evidence version、Artifact、Source、Artifact generation、Source generation。
   - 非主证据撤回 / 删除是否 stale 并阻断 suggest / feedback / export。
3. P1-4 覆盖复核：
   - Artifact generation mismatch 是否主动 stale。
   - Source generation mismatch 是否主动 stale。
   - stale 后是否阻断 suggest / feedback / export / restore candidates。
4. P1-5 覆盖复核：
   - `important_link` 是否必须由用户确认关系写入。
   - 写入口是否检查 from / to / evidence 的授权、generation、Project、tombstone。
   - 是否存在跨项目、缺失授权、过期授权或旧 generation 绕过。
5. P1-6 覆盖复核：
   - `exportMemory()` 是否包含最小权威投影。
   - `restoreCandidates()` 是否只读，不写回权威表或 active projection。
   - revoke / delete / Artifact generation 变化 / Source generation 变化 / stale / invalid / 包篡改是否不可复活。
6. P1-7 覆盖复核：
   - `expires_at_ms` 是否进入统一消费门。
   - 过期授权是否阻断所有已实现消费和写入口。
   - `retractFeedback()` 是否用户显式、幂等、保留历史、移除确认语义。
   - feedback 撤回是否不复活 stale / invalid / 过期 Derivation。
7. P1-8 覆盖复核：
   - suggestion ID 是否绑定 Project 与完整输入集合。
   - 是否绑定 evidence version、Artifact、Source、Artifact generation、Source generation。
   - 输入顺序稳定、非主证据 generation 变化、输入集合变化是否不会复用旧 ID。
8. 组合反例攻击：
   - restore candidates + 过期授权。
   - restore candidates + feedback_retracted。
   - suggestion ID + 非主 Source generation 变化。
   - important_link + 过期 / revoked / stale evidence。
   - feedback 撤回 + confirmed / edited_confirmed / invalid / stale。
   - exportMemory + staleGenerationMismatches + derivationInputsConsumable。
9. 非范围与边界：
   - 是否未启用真实 Tauri / IPC、真实 Vault、真实数据、真实导出、真实时间服务、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
   - 是否未冻结生产 Schema / API / Tauri 配置 / 导出格式 / SLA。
   - 是否未关闭 R-0040，未恢复或冻结新的工程基线扩展。

## 非范围

本任务暂时不要做：

- 不修改任何业务代码、测试或 evidence。
- 不新增补丁实现。
- 不关闭 R-0040。
- 不恢复或冻结工程基线扩展。
- 不准入下一阶段。
- 不启用真实能力。
- 不创建后续任务；如认为需要，只写入“最终建议 / 后续任务建议”。

## 角色检查点

独立工程评审负责人必须重点回答：

- 当前 P3-009 是否足以被视为 P1-3 至 P1-8 的受控迁移完成候选？
- 是否存在 P0 / P1 反例，足以要求 Rework？
- evidence 是否能独立支撑结论，还是存在自证循环？

数据与权限负责人必须重点检查：

- Source / Artifact / Derivation / Feedback / Authorization / Link 的身份、来源、generation、权限和状态是否没有混淆。
- 删除、撤回、过期、generation mismatch 是否不能被旧包、旧 suggestion、旧 feedback 或 link 绕过。

AI 信任与安全负责人必须重点检查：

- AI suggestion 是否始终是候选，不会绕过证据、授权、用户撤回或反馈撤回。
- 用户确认、纠正、撤回是否可区分，不被 AI 静默改写。
- 旧 AI 建议是否不会通过导出 / 恢复 / ID 复用重新变成可信建议。

QA / 测试负责人必须重点检查：

- 现有 34 项测试是否覆盖核心路径和关键反例。
- 是否有遗漏组合场景，需要 PM 后续创建补丁或补测任务。
- evidence 是否与实际测试结果一致。

技术架构负责人必须重点检查：

- 结论是否仍限定于合成、单进程、受控测试包。
- 是否没有把真实 Tauri / IPC、真实 Vault、真实导出、生产 Schema / API 或 SLA 偷渡为已通过。
- R-0040 是否保持 Open / Conditional，除非后续另走关闭流程。

## 交付物格式

请将完整独立复评文件保存为：

`lifeos/reviews/LIFEOS-P3-020_p1_migration_completion_independent_engineering_review.md`

报告建议使用：

`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`

报告必须包含：

- 评审结论：Pass / Pass with Conditions / Rework / Blocked
- 复跑能力说明：是否实际复跑测试；若未复跑，说明原因
- Evidence 一致性检查
- P1-3 至 P1-8 覆盖复核
- 组合反例攻击清单与结论
- P0 / P1 / P2 问题清单
- 是否建议 PM 后续考虑关闭 R-0040：Yes / No / Conditional
- 是否建议 PM 后续考虑恢复 / 冻结工程基线扩展：Yes / No / Conditional
- 必须整改项
- 条件通过项
- 需要 PM 决策
- 本地预检结果或跳过原因

注意：聊天回复不要粘贴完整报告，只输出摘要、评审路径、复跑摘要、结论、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整复核 P1-3 至 P1-8。
- 完成 evidence 一致性检查。
- 完成组合反例攻击清单。
- 明确是否存在 P0 / P1。
- 明确结论为 Pass / Pass with Conditions / Rework / Blocked。
- 明确 R-0040 是否仍应保持 Open / Conditional。
- 明确是否建议恢复 / 冻结工程基线扩展，但不得自行执行。
- 未修改工程文件、项目账本、Stitch 或冻结资产。
- 已生成指定独立评审文件。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 独立评审路径
- 复跑摘要
- 评审结论
- 是否需要 PM 决策

不要修改项目账本，不要自行宣布 R-0040 关闭，不要恢复或冻结工程基线扩展，不要自行启动后续任务。
