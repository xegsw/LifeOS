# LIFEOS-P3-010 目标技术栈最小工程骨架独立工程评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立评审会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-010
- 任务名称：目标技术栈最小工程骨架独立工程评审
- 优先级：P0
- 任务类型：独立评审型任务 / 反例攻击 / 工程复核
- 建议篇幅：2000-4000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：WorkBuddy
- 推荐理由：P3-009 由 Codex 执行，本任务需要独立视角对 P3-009 的工程自证、测试覆盖、证据链和安全边界进行反例攻击，避免执行者自证循环
- 是否需要后续独立评审：No，本任务自身就是独立评审
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、数据与权限负责人、QA / 测试负责人、AI 信任与安全负责人
- 必须通过的评审关卡：独立复跑 / 只读验证、P3-001→P3-009 不变量覆盖差异检查、P0 反例攻击、默认关闭能力检查、证据链完整性检查
- 状态：Ready

## 背景

`LIFEOS-P3-009` 已通过 PM 验收，结论为 `Accepted / Pass with Conditions`。PM 复跑结果为 10 PASS / 0 FAIL / P0=0，并追加抽样反例 4 PASS。但 P3-009 仍只是合成、单进程、受控测试包边界内的目标技术栈最小骨架迁移候选。

本任务的目的不是继续实现功能，而是独立验证 P3-009 是否真实继承了 P3-001 的核心安全不变量，是否存在测试聚合导致的关键子断言遗漏，是否有恢复包、generation、Project 闭包、Feedback / Link 写入口、导出或消费门旁路。

P3-010 通过前，不得把 P3-009 作为后续工程基线，不得启动真实 Tauri / IPC、真实 Vault、真实数据、文件导出、云 / 第三方模型、向量、同步、多设备或 L3。

## 目标

本任务完成后，需要回答：

- P3-009 是否严格遵守任务卡边界，未修改 P3-001、未启用真实能力、未冻结实现细节？
- P3-009 的 10 个聚合测试是否足以覆盖 P3-001 历史 23 个测试 / 136 个断言中的 P0 根风险？
- 是否存在 P3-009 自测未覆盖的 P0 / P1 漏洞？
- P3-009 的 evidence 是否可复核、可重跑、没有自证循环？
- P3-009 能否作为后续工程基线候选，还是必须返工？

## 授权范围

允许：

- 读取 P3-009 任务卡、交付报告、PM Review、代码、测试、fixtures 和 evidence。
- 读取 P3-001 任务卡、报告、测试和 evidence manifest，用于差异对照。
- 读取 P3-008 独立复评和 PM Review，用于历史 P0 反例回归参考。
- 运行只读测试或临时反例验证。
- 在系统临时目录复制 `lifeos/engineering/LIFEOS-P3-009/` 后运行会改写 evidence 的验证脚本。
- 在原目录运行不会改写文件的只读命令，例如直接执行 Node test runner。
- 输出独立评审报告到 `lifeos/reviews/`。
- 调用本地预检检查评审报告。

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
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0148 至 D-0151 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 复核 P3-009 是否遵守任务卡边界：
   - 是否只在授权目录创建工程文件。
   - 是否未修改 P3-001。
   - 是否未启用真实能力。
   - 是否未冻结实现细节或关闭 R-0040。
2. 独立复跑或只读验证 P3-009：
   - 优先使用只读测试命令。
   - 如需运行 `scripts/validate.mjs`，必须复制到系统临时目录后运行，避免改写原 evidence。
3. 对照 P3-001 与 P3-009：
   - P3-001 的 23 项历史测试 / 136 个断言中，哪些被 P3-009 10 个聚合测试覆盖。
   - 哪些被弱化、合并、只映射或遗漏。
   - 哪些遗漏构成 P0 / P1。
4. 至少设计并执行以下反例攻击：
   - 删除 / 撤回后旧 context、旧 derivation、旧 feedback 不得复活或写入。
   - 跨 Project recovery / export / suggestion 不得泄漏。
   - purpose / location / processor / version / generation mismatch 必须 fail closed。
   - AI suggestion / inference / external reference 缺 evidence 必须拒绝。
   - Project mixed state、stale generation、authorization deny 后的消费入口必须拒绝。
   - 默认关闭能力不得存在隐藏启用路径。
5. 检查 evidence：
   - `MANIFEST.md`、`test_results.json`、`test_run.log`、迁移矩阵和默认关闭矩阵是否一致。
   - 是否存在测试输出解析错误、自证循环、只测 happy path 或 PASS 数量误导。
6. 输出独立评审结论：
   - Pass
   - Pass with Conditions
   - Rework
   - Blocked

## 非范围

本任务暂时不要做：

- 不修复 P3-009 代码。
- 不新增工程功能。
- 不创建 P3-011。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0040。

## 角色检查点

独立工程评审负责人必须重点回答：

- P3-009 是否经得起反例攻击？
- 是否存在执行者自证循环或测试弱化？
- 最终建议是 Pass、Pass with Conditions、Rework 还是 Blocked？

技术架构负责人必须重点检查：

- P3-009 是否只继承技术架构 V0.1 合同，而未冻结实现细节？
- `node:sqlite` experimental warning 是否影响后续工程基线候选？
- R-0040 是否被正确保留？

数据与权限负责人必须重点检查：

- 用户原文、AI 内容、AI 推断 / 建议、外部引用身份是否真的分离？
- authorization、source、version、tombstone、generation、evidence 是否在所有消费入口重检？
- 删除、撤回、恢复、导出和反馈写入口是否有旁路？

QA / 测试负责人必须重点检查：

- P3-009 测试覆盖是否足够，是否过度聚合？
- P0 / P1 分类是否合理？
- evidence 是否足够支持结论？

AI 信任与安全负责人必须重点检查：

- AI suggestion / inference / generated content 是否需要证据并可失效？
- 是否存在 AI 候选被用户反馈、撤回或删除后仍活跃的问题？

## 交付物格式

请将完整独立评审保存为：

`lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`

报告必须包含：

- 任务摘要
- 读取材料清单
- 复跑 / 只读验证结果
- P3-001 → P3-009 覆盖差异矩阵
- 反例攻击清单与结果
- Evidence 一致性检查
- P0 / P1 / P2 问题清单
- 可接受内容
- 必须整改内容
- 是否建议 P3-009 作为后续工程基线候选
- 是否建议保持 R-0040 Open / Conditional
- 本地预检结果或跳过原因
- 最终结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、评审路径、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 已输出指定独立评审文件。
- 已只读复核或在临时副本中复跑 P3-009。
- 已完成 P3-001→P3-009 覆盖差异检查。
- 已执行至少 6 类反例攻击并记录结果。
- 已明确 P0 / P1 / P2 问题。
- 已明确是否建议 P3-009 进入后续工程基线候选。
- 已明确 R-0040 是否必须保持 Open / Conditional。
- 未修改 P3-009 / P3-001 工程文件。
- 未修改项目账本。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 独立评审路径
- 反例攻击摘要
- 最终结论
- 是否需要 PM 决策

不要修改项目账本，不要自行启动 P3-011，不要宣布资产冻结。
