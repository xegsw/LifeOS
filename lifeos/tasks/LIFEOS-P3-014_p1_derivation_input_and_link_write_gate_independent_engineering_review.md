# LIFEOS-P3-014 P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口独立工程复评

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立工程复评会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-014
- 任务名称：P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口独立工程复评
- 优先级：P1
- 任务类型：独立评审型任务 / P1 工程迁移复评 / 反例攻击 / 证据链复核
- 建议篇幅：2000-4000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：WorkBuddy
- 推荐理由：P3-013 由 Codex 执行并经 PM 验收，本任务需要不同 Agent 独立复评，避免执行者自证循环，重点攻击多证据 Derivation、非主证据撤回传播、important_link 写入口门和 evidence 一致性
- 是否需要后续独立评审：No，本任务自身就是独立复评
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人
- 必须通过的评审关卡：独立只读复跑 / 临时副本验证、P1-3 多证据派生输入反例攻击、P1-5 important_link 写入口门反例攻击、evidence 一致性检查、默认关闭能力检查、R-0040 保留检查
- 状态：Ready

## 背景

`LIFEOS-P3-012` 独立工程复评已确认 P3-009 的 P0 消费门问题关闭，用户已采纳并恢复 P3-009 为合成、单进程、受控测试包边界内的后续工程基线候选，`R-0042` 已关闭，`R-0040` 继续保持 `Open / Conditional`。

`LIFEOS-P3-013` 已完成 P3-009 的两个 P1 迁移：

- P1-3：多证据 `derivation_input` 与非主证据撤回 / 删除传播。
- P1-5：`important_link` / `important_link_evidence` 写入口门。

PM 已验收 P3-013，复跑结果为 18 PASS / 0 FAIL / P0=0，并确认任务未启用真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型、向量、同步 / 多设备或 L3。

但 P3-013 是工程执行任务，不是独立复评任务；新增写入口与证据依赖路径必须经独立反例攻击，才能判断是否可作为 P3-009 工程基线候选的安全不变量补强输入。

## 目标

本任务完成后，需要回答：

- P3-013 是否真实完成 P1-3 多证据 `derivation_input` 迁移？
- Derivation 是否记录所有输入证据版本、artifact generation、source generation，而不是只依赖单一主证据？
- 任一输入证据，尤其是非主证据，被 revoke / delete 后，相关 Derivation 是否 stale，并阻断 feedback / export / suggest？
- P3-013 是否真实完成 P1-5 `important_link` 写入口门迁移？
- `important_link` 是否只允许用户确认关系写入，并显式绑定 Project、from/to Artifact 或 Version、source identity、confirmation status 和 evidence？
- deny、missing auth、generation mismatch、source generation mismatch、cross Project、tombstone、重复 evidence 或伪造 context 后，`important_link` 是否全部 fail closed？
- P3-013 的 evidence manifest、test_results、test_run.log、矩阵文件是否与代码和实际复跑一致？
- 是否建议 P3-013 作为 P3-009 工程基线候选的 P1 补强输入？
- 是否发现 P0 / 关键 P1，需要回退 P3-013 或启动返工？
- R-0040 是否必须继续保持 Open / Conditional？

## 授权范围

允许：

- 读取 P3-009、P3-011、P3-012、P3-013 的任务卡、报告、PM Review、代码、测试、fixtures 和 evidence。
- 读取 P3-001 / P3-008 相关材料，用于历史 P0 防线和多证据 / Link 语义参考。
- 读取 P2-019 验收合同，用于核对 H1-H9 / T-ARCH 安全不变量。
- 在原目录运行不会改写文件的只读测试命令。
- 如需运行会改写 evidence 的验证脚本，必须先复制 `lifeos/engineering/LIFEOS-P3-009/` 到系统临时目录后运行。
- 在系统临时目录中编写一次性反例脚本或临时测试。
- 输出独立复评报告到 `lifeos/reviews/`。
- 调用本地预检检查复评报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/` 中任何源码、测试、fixtures、evidence 或 README。
- 在原目录运行会改写 evidence 的 `scripts/validate.mjs`；如需运行，必须先复制到系统临时目录。
- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改项目账本：`CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 处理真实数据、真实 Vault、真实系统路径、真实外部用户资料。
- 启用真实 Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部自动化。
- 自行宣布 Accepted、Frozen、工程基线扩展完成、风险关闭、阶段切换或启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-012_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration.md`
- `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-013_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/`
- `lifeos/engineering/LIFEOS-P3-009/fixtures/synthetic_v1.json`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/reviews/LIFEOS-P3-008_third_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-008_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0156 至 D-0159 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 只读边界复核：
   - 是否未修改 P3-009 / P3-001 工程文件。
   - 是否未启用真实能力。
   - 是否未冻结实现细节、工程基线扩展或关闭 R-0040。
2. 独立复跑 / 临时副本验证：
   - 可在原目录运行只读 Node test runner。
   - 如需运行 `scripts/validate.mjs`，必须复制到系统临时目录后运行。
   - 记录 PASS / FAIL、P0 失败数、关键失败与证据路径。
3. P1-3 多证据派生输入反例攻击：
   - Derivation 是否记录所有输入证据，不只记录主 evidence。
   - revoke / delete 非主证据后，Derivation 是否 stale。
   - stale 后 feedback 是否拒绝写入。
   - stale 后 export 是否不包含该 Derivation。
   - stale 后 suggest 是否不会继续返回旧候选。
   - artifact generation 或 source generation 不匹配时是否 fail closed。
   - 伪造 / 缺失 input context 是否不能消费旧派生。
4. P1-5 important_link 写入口门反例攻击：
   - 只有 `user_confirmed + confirmed` 的 Link 可写入。
   - AI inference、unconfirmed、空 evidence、重复 evidence、伪造 version、source generation mismatch、artifact generation mismatch 必须拒绝。
   - deny、missing auth、unknown decision、duplicate allow、allow+deny、purpose / location / processor mismatch 必须拒绝。
   - cross Project、tombstone 后必须拒绝。
   - 事务内二次重检是否存在竞态旁路；如无法实测，需要说明剩余风险。
5. Evidence 一致性检查：
   - `MANIFEST.md`、`test_results.json`、`test_run.log`、`invariant_migration_matrix.md`、`architecture_conformance.md`、默认关闭矩阵是否一致。
   - evidence 是否反映 P3-013 的 18 PASS / 0 FAIL，而不是旧 P3-011 的 14 PASS。
   - 是否存在测试输出解析错误、自证循环、只测 happy path 或 PASS 数量误导。
6. 结论判断：
   - Pass：可建议 PM 采纳 P3-013 作为 P3-009 工程基线候选的 P1 补强输入。
   - Pass with Conditions：P1-3 / P1-5 主体成立，但仍有明确条件，不影响有限边界内继续。
   - Rework：存在 P0 / 关键 P1 阻断，P3-013 不应作为后续输入。
   - Blocked：证据不足或无法复核。

## 非范围

本任务暂时不要做：

- 不修复 P3-009 代码。
- 不新增工程功能。
- 不迁移 P1-4、P1-6、P1-7、P1-8。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言，除非作为只读差异说明。
- 不实现完整 restore_candidates、正式恢复包、真实文件导出或正式备份恢复协议。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

独立工程评审负责人必须重点回答：

- P3-013 是否经得起独立反例攻击？
- 是否存在执行者自证循环或测试弱化？
- 最终建议是 Pass、Pass with Conditions、Rework 还是 Blocked？

技术架构负责人必须重点检查：

- P3-013 是否只在目标技术栈最小骨架内补强 P1 安全不变量，而未冻结实现细节？
- `node:sqlite` experimental warning 是否仍被正确视为非冻结提醒？
- R-0040 是否被正确保留？

数据与权限负责人必须重点检查：

- Derivation 输入证据是否完整、可追溯、可失效？
- Link 是否显式区分用户确认关系、AI 推断和外部来源？
- authorization、source、version、tombstone、generation、evidence 是否在新增消费 / 写入口重检？

AI 信任与安全负责人必须重点检查：

- AI suggestion / derivation 是否仍需要证据并可失效？
- stale Derivation 是否不会继续接受反馈、导出或作为建议出现？
- Link 是否不会把 AI 推断、用户确认事实、外部引用来源混成同一种身份？

QA / 测试负责人必须重点检查：

- 新增 P1-3 / P1-5 测试是否包含反例，而非只覆盖 happy path？
- PASS 数量和 evidence 是否可独立复核、可重跑且无自证循环？
- 关键失败是否被准确分级为 P0 / P1 / P2？

## 交付物格式

请将完整独立复评保存为：

`lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`

报告必须包含：

- 任务摘要
- 读取材料清单
- 只读复跑 / 临时副本验证结果
- P1-3 多证据派生输入反例攻击清单与结果
- P1-5 important_link 写入口门反例攻击清单与结果
- Evidence 一致性检查
- P0 / P1 / P2 问题清单
- 可接受内容
- 必须整改内容
- 是否建议 P3-013 作为 P3-009 工程基线候选的 P1 补强输入
- 是否建议保持 R-0040 Open / Conditional
- 本地预检结果或跳过原因
- 最终结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、评审路径、反例攻击摘要、最终结论、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 已输出指定独立复评文件。
- 已只读复核或在临时副本中复跑 P3-009。
- 已复核 P1-3 多证据派生输入是否成立。
- 已执行非主证据 revoke / delete 后 Derivation stale 与 feedback / export / suggest 阻断反例攻击。
- 已复核 P1-5 important_link 写入口门是否成立。
- 已执行 important_link 的身份、证据、授权、generation、Project、tombstone 反例攻击。
- 已检查 evidence manifest 与测试结果一致。
- 已明确 P0 / P1 / P2 问题。
- 已明确是否建议 P3-013 作为 P3-009 工程基线候选的 P1 补强输入。
- 已明确 R-0040 是否必须保持 Open / Conditional。
- 未修改 P3-009 / P3-001 工程文件。
- 未修改项目账本。
- 未启用真实能力。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 独立复评路径
- 反例攻击摘要
- 最终结论
- 是否需要 PM 决策

不要修改项目账本，不要自行宣布工程基线扩展完成，不要关闭 R-0040，不要自行启动后续任务。

