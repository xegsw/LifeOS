# LIFEOS-P3-012 P3-009 P0 消费门返工独立工程复评

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立工程复评会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-012
- 任务名称：P3-009 P0 消费门返工独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务 / P0 返工复评 / 反例攻击 / 工程复核
- 建议篇幅：2000-4000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：WorkBuddy
- 推荐理由：P3-011 由 Codex 执行并经 PM 验收，本任务需要不同 Agent 独立复评，避免执行者自证循环，重点攻击授权冲突、消费门旁路、evidence 自证和 P1 同范围修复是否真实成立
- 是否需要后续独立评审：No，本任务自身就是独立复评
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、数据与权限负责人、QA / 测试负责人、AI 信任与安全负责人
- 必须通过的评审关卡：独立只读复跑 / 临时副本验证、P3-010 AD-1 回归复核、消费入口反例攻击、P1-1 / P1-2 修复复核、evidence 一致性检查、默认关闭能力检查
- 状态：Ready

## 背景

`LIFEOS-P3-010` 独立工程评审发现 `LIFEOS-P3-009` 存在 1 项 P0：`canConsume()` 只计数 allow，不检查 deny，导致同一授权上下文 allow+deny 冲突时仍可读取用户原文。PM 已接受该 Rework 结论，并新增 `R-0042`。

`LIFEOS-P3-011` 已完成窄范围返工：`canConsume()` 改为要求当前 subject / purpose / location / processor / generation 授权集合总数恰好 1 且该行是 allow 才放行；新增 P0 / P1 回归测试；PM 复跑结果为 14 PASS / 0 FAIL / P0=0，并抽样复核 read / search / recovery / suggest / export 均已 fail closed。

但 P3-011 仍是工程执行者交付与 PM 验收，不等于 P3-009 已恢复工程基线候选，也不等于 `R-0042` 可关闭。本任务用于独立复评 P3-011 是否真正关闭 P3-010 的 P0，并确认是否存在新的旁路或证据不足。

P3-012 通过前，不得恢复 P3-009 工程基线候选，不得关闭 R-0042，不得启动真实 Tauri / IPC、真实 Vault、真实数据、文件导出、云 / 第三方模型、向量、同步、多设备或 L3。

## 目标

本任务完成后，需要回答：

- P3-011 是否真实关闭 P3-010 的 P0 allow+deny 授权冲突放行问题？
- read / search / recovery / suggest / exportMemory 等所有已实现消费入口是否都复用同一消费门并 fail closed？
- missing auth、duplicate allow、unknown decision、allow+unknown、generation / purpose / location / processor mismatch 是否仍 fail closed？
- P1-1 `suggest()` 静默重置确认状态是否已修复且未引入新副作用？
- P1-2 `feedback()` 非 candidate 状态写入口是否已显式拒绝？
- P3-011 的 evidence 是否与代码、测试和验证脚本一致，能否被独立复核？
- 是否建议将 P3-009 恢复为后续工程基线候选，并是否建议关闭或降级 R-0042？

## 授权范围

允许：

- 读取 P3-009、P3-010、P3-011 的任务卡、报告、PM Review、代码、测试、fixtures 和 evidence。
- 读取 P3-001 / P3-008 相关材料，用于历史 P0 防线回归参考。
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
- 自行宣布 Accepted、Frozen、工程基线恢复、风险关闭、阶段切换或启动后续任务。

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
- `lifeos/tasks/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-011_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
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
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0150 至 D-0155 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 只读边界复核：
   - 是否未修改 P3-009 / P3-001 工程文件。
   - 是否未启用真实能力。
   - 是否未冻结实现细节、恢复工程基线或关闭 R-0042 / R-0040。
2. 独立复跑 / 临时副本验证：
   - 可在原目录运行只读 Node test runner。
   - 如需运行 `scripts/validate.mjs`，必须复制到系统临时目录后运行。
   - 记录 PASS / FAIL、P0 失败数、关键失败与证据路径。
3. P3-010 AD-1 回归：
   - 插入同一 subject / purpose / location / processor / generation 的 allow+deny 冲突授权后，read 必须返回 null。
   - search / recovery / suggest / exportMemory 不得间接泄漏用户原文、derivation 或 Project 状态。
4. 授权不确定态反例：
   - missing auth 必须拒绝。
   - duplicate allow 必须拒绝。
   - unknown decision 必须拒绝。
   - allow+unknown 必须拒绝。
   - generation / purpose / location / processor mismatch 必须拒绝。
5. P1-1 / P1-2 复核：
   - 重复 suggest 不得静默重置 confirmed / edited_confirmed / rejected / invalid 状态。
   - feedback 必须拒绝非 candidate derivation，不得在 stale / confirmed / edited_confirmed / invalid 等状态继续写入。
   - 若发现当前修复只覆盖部分状态，应标为 P1 或 P0，并解释影响。
6. Evidence 一致性检查：
   - `MANIFEST.md`、`test_results.json`、`test_run.log`、迁移矩阵、默认关闭矩阵、架构符合性文件是否一致。
   - evidence 是否反映 P3-011 的 14 PASS / 0 FAIL，而不是旧 P3-009 的 10 PASS。
   - 是否存在测试输出解析错误、自证循环、只测 happy path 或 PASS 数量误导。
7. 结论判断：
   - Pass：可建议 PM 将 P3-009 恢复为后续工程基线候选，并建议关闭或降级 R-0042。
   - Pass with Conditions：P0 关闭但仍有明确条件，不影响有限边界内继续。
   - Rework：仍有 P0 / 关键 P1 阻断，P3-009 不得恢复基线。
   - Blocked：证据不足或无法复核。

## 非范围

本任务暂时不要做：

- 不修复 P3-009 代码。
- 不新增工程功能。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言，除非作为只读差异说明。
- 不实现完整 restore_candidates、important_link、derivation_input、多证据撤回传播、真实文件导出或正式备份恢复协议。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0042 或 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

独立工程评审负责人必须重点回答：

- P3-011 是否经得起独立反例攻击？
- 是否存在执行者自证循环或测试弱化？
- 最终建议是 Pass、Pass with Conditions、Rework 还是 Blocked？

技术架构负责人必须重点检查：

- P3-011 是否只修复目标技术栈最小骨架内的 P0，而未冻结实现细节？
- `node:sqlite` experimental warning 是否仍被正确视为非冻结提醒？
- R-0040 是否被正确保留？

数据与权限负责人必须重点检查：

- 用户原文、AI 内容、AI 推断 / 建议、外部引用身份是否仍分离？
- authorization、source、version、tombstone、generation、evidence 是否在所有消费入口重检？
- deny、冲突、重复、未知、不匹配上下文是否全部 fail closed？

QA / 测试负责人必须重点检查：

- P0 回归测试是否覆盖所有已实现消费入口？
- P1-1 / P1-2 测试是否覆盖足够状态，而非只覆盖单一 happy path？
- evidence 是否可独立复核、可重跑且无自证循环？

AI 信任与安全负责人必须重点检查：

- AI suggestion / inference / generated content 是否仍需要证据并可失效？
- 用户确认、拒绝、纠正后的状态是否不会被重复建议静默覆盖？
- 非候选状态是否不能继续接受反馈写入？

## 交付物格式

请将完整独立复评保存为：

`lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`

报告必须包含：

- 任务摘要
- 读取材料清单
- 只读复跑 / 临时副本验证结果
- P3-010 AD-1 回归复核
- 授权不确定态反例攻击清单与结果
- P1-1 / P1-2 修复复核
- Evidence 一致性检查
- P0 / P1 / P2 问题清单
- 可接受内容
- 必须整改内容
- 是否建议 P3-009 恢复为后续工程基线候选
- 是否建议关闭或降级 R-0042
- 是否建议保持 R-0040 Open / Conditional
- 本地预检结果或跳过原因
- 最终结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、评审路径、反例攻击摘要、最终结论、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 已输出指定独立复评文件。
- 已只读复核或在临时副本中复跑 P3-009。
- 已复核 P3-010 AD-1 是否关闭。
- 已执行授权不确定态与消费入口旁路反例攻击。
- 已复核 P1-1 / P1-2 修复是否成立。
- 已检查 evidence manifest 与测试结果一致。
- 已明确 P0 / P1 / P2 问题。
- 已明确是否建议 P3-009 恢复为后续工程基线候选。
- 已明确是否建议关闭或降级 R-0042。
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

不要修改项目账本，不要自行恢复 P3-009 工程基线，不要关闭 R-0042，不要自行启动后续任务。
