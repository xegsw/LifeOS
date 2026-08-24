# LIFEOS-P2-017 MVP 开发准入评审准备包

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-017
- 任务名称：MVP 开发准入评审准备包
- 优先级：P0
- 任务类型：决策型任务 / 准入评审准备
- 建议篇幅：1000-2000 字；如必须超出，请把扩展内容放入“后续任务建议”
- 主责角色：PM / 技术架构负责人
- 协审角色：产品架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、体验设计负责人
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4、Gate 5 的准入准备核对；本任务不替代“进入正式 MVP 开发”的独立评审
- 状态：Ready

## 背景

LifeOS 已完成 Stage 1 核心定义线，并完成 Stage 2 主要技术验证线。用户已采纳 `LIFEOS-P2-016`，并按 D-0123 冻结技术架构 V0.1 合同。

但技术架构冻结不等于正式 MVP 开发准入。根据 `lifeos/STAGE_GATES.md`，进入正式 MVP 工程实现仍属于关键冻结事项，必须单独判断是否满足硬门槛、是否存在例外、是否需要独立评审，以及哪些风险必须迁移为工程启动前约束。

本任务用于准备 PM 后续做“是否允许进入 Stage 3 / 正式 MVP 开发”的决策材料，不启动开发，不写代码，不创建真实产品实现。

## 目标

完成后需要回答：

- LifeOS 当前是否已经具备进入正式 MVP 开发评审的条件？
- 哪些 Stage 3 硬门槛已满足，哪些仍阻塞或需要例外记录？
- 技术架构 V0.1 冻结后，哪些风险必须迁移为工程约束或后续复测项？
- 是否可以建议进入正式 MVP 开发独立评审？
- 若不能进入，应建议下一步补齐哪类准备任务，而不是直接开发。

## 范围

本任务必须覆盖：

- 按 `STAGE_GATES.md` 的“进入开发前硬门槛”和“Stage 2 到 Stage 3”逐项核对当前状态。
- 区分三种状态：
  - 已满足，可作为准入依据
  - 条件满足，需要在开发前/开发中保留约束
  - 未满足，阻塞正式 MVP 开发
- 明确技术架构 V0.1 已冻结的范围和不冻结范围。
- 明确 R-0039、R-0040 以及与真实数据、权限、删除、导出、Obsidian、Tauri / IPC、云 / 第三方模型相关的准入影响。
- 判断外部用户验证线暂停后，是否影响正式 MVP 开发准入；如可例外，必须说明例外边界和补偿机制。
- 输出 PM 可使用的准入决策选项，例如：
  - A：允许进入正式 MVP 开发独立评审
  - B：仅允许开发准备 / 工程脚手架，不允许真实 MVP 开发
  - C：继续阻塞，先补齐指定缺口

## 非范围

本任务暂时不要做：

- 不进入正式 MVP 开发。
- 不写产品代码、脚手架代码、数据库 Schema、API、Tauri 配置或测试脚本。
- 不修改 Stitch 或任何原型。
- 不冻结新的 PRD、Schema、API、同步栈、真实 Tauri capability、真实云 / 第三方模型或生产 SLA。
- 不联系真实用户，不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不替代后续“进入正式 MVP 开发”的独立评审或 PM 最终准入决策。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/RISK_LOG.md` 中 R-0039、R-0040，以及与真实数据、权限、删除、Obsidian、Tauri / IPC、云 / 第三方模型相关的开放 P0 风险
- `lifeos/DECISION_LOG.md` 中 D-0081 至 D-0123，或最近 5-10 条与准入相关的决策
- `lifeos/deliverables/LIFEOS-P1-014_self_use_mvp_dev_readiness_roadmap.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- `lifeos/deliverables/LIFEOS-P1-018_first_technical_spike_task_cards.md`
- `lifeos/deliverables/LIFEOS-P2-010_technical_architecture_candidate_review.md`
- `lifeos/deliverables/LIFEOS-P2-011_technical_architecture_freeze_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P2-012_technical_architecture_independent_review.md`
- `lifeos/deliverables/LIFEOS-P2-013_technical_architecture_freeze_condition_final_patch.md`
- `lifeos/reviews/LIFEOS-P2-014_pm_review.md`
- `lifeos/reviews/LIFEOS-P2-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/reviews/LIFEOS-P2-016_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取摘要、冻结状态、任务验收结论和相关风险行；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；只读取 D-0081 至 D-0123 或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 交付物正文按决策型任务篇幅控制；超出范围的内容放入“后续任务建议”。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。
- 交付物完成后，默认调用本地预检：`python3 lifeos/tools/local_precheck.py <交付物路径>`。
- 会话回复应引用本地预检报告路径；若本地模型不可用、超时、输出为空、任务无明确交付物路径，或用户明确要求不调用本地模型，可跳过并说明原因。

## 角色检查点

主责角色必须重点回答：

- 当前是否满足 `STAGE_GATES.md` 的正式 MVP 开发硬门槛。
- 技术架构 V0.1 冻结后，还剩哪些准入阻塞项。
- 下一步应该是正式准入独立评审、有限开发准备，还是继续补齐缺口。

协审角色必须重点检查：

- 产品架构：不得偏离个人终身外脑定位，不得把 V1 扩成全知全能或企业后台。
- AI 信任与安全：不得因开发准入而放松用户确认、授权重检、撤回、删除和来源区分。
- 数据 / 领域模型：不得把语义模型误读为 Schema/API 冻结；不得混淆用户原文、AI 派生、AI 推断/建议和外部来源。
- 体验设计：不得把首页 / 今日页静态原型冻结误读为动态交互、响应式或可访问性已完成。

## 核心问题

请重点回答：

- Stage 3 / 正式 MVP 开发的硬门槛逐项状态是什么？
- 当前最小自用 MVP 是否存在“可开发但有限制”的入口，还是仍应阻塞？
- 外部用户验证线暂停是否构成 Gate 5 阻塞？如果建议例外，例外理由和补偿机制是什么？
- R-0040 应如何进入后续工程准入条件？
- 哪些 P0/P1 风险必须在工程任务拆解前转为开发约束或复测任务？
- PM 下一步应该如何决策？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P2-017_mvp_development_entry_review_package.md`

请输出的文件内容包括：

- 结论摘要
- Stage 3 硬门槛逐项核对表
- 已满足 / 条件满足 / 未满足清单
- 技术架构 V0.1 冻结对准入的影响
- 外部用户验证线暂停的准入影响
- 必须迁移到工程阶段的风险与约束
- PM 决策选项与推荐
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为指定文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 明确说明本任务不等于正式 MVP 开发准入。
- 明确区分事实、推断、建议。
- 明确列出需要 PM 主会话确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不冻结新的产品、技术、Schema、API 或交互资产。
- 不进入正式 MVP 开发。
- 不处理真实敏感数据。
