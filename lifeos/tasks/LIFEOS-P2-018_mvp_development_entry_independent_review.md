# LIFEOS-P2-018 正式 MVP 开发准入独立评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。你本次承担“独立评审会话”角色，只做评审，不重写主交付物，不创建工程任务，不进入正式 MVP 开发。

## 任务信息

- 任务 ID：LIFEOS-P2-018
- 任务名称：正式 MVP 开发准入独立评审
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2000-4000 字；如必须超出，请把扩展内容放入“后续任务建议”
- 主责角色：独立评审负责人 / Stage Gate 评审人
- 协审角色：产品架构负责人、技术架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、体验设计负责人、用户价值验证负责人
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4、Gate 5；重点是“进入正式 MVP 开发”独立评审
- 状态：Ready

## 背景

LifeOS 已完成 V1 核心定义线、首页 / 今日页 PRD 与关键静态原型冻结、核心领域模型 V0.1、AI 权限与信任模型 V0.1、技术架构 V0.1 合同冻结，并完成 SP-01 至 SP-09 及 P2-014 / P2-015 窄测。

`LIFEOS-P2-017` 已通过 PM 验收并由用户确认采纳，结论是：当前材料足以启动“正式 MVP 开发准入独立评审”，但不等于已经允许进入 Stage 3 / 正式 MVP 开发。

本任务是进入正式 MVP 开发前的独立评审。评审结果只作为 PM 主会话和用户最终决策输入；不能自行宣布 Stage 3 准入，不能启动工程实现。

## 目标

完成后需要回答：

- 当前 LifeOS 是否满足进入正式 MVP 开发的硬门槛？
- 如果不完全满足，哪些缺口可作为“自用 MVP 有限例外”，哪些不能例外？
- Gate 5 外部验证结果缺失是否可以在“自用、单设备、本地优先、非商用、非外部用户”的前提下被有限接受？
- R-0040、真实数据、真实 Vault、真实 Tauri / IPC、云 / 第三方模型、导出、删除 / 撤回、动态体验等风险是否足以阻塞正式 MVP 开发？
- 独立评审建议 PM 选择：Pass、Pass with Conditions、Rework / Blocked 中的哪一种？

## 范围

本任务必须覆盖：

- 按 `lifeos/STAGE_GATES.md` 的“进入开发前的硬门槛”逐项评审。
- 按 Stage 2 → Stage 3 的必须完成项与必须通过关卡逐项评审。
- 独立判断 P2-017 的建议是否成立，不得无条件复述 P2-017。
- 明确 Gate 1-5 的通过、条件通过、未通过情况。
- 重点评估 Gate 5：
  - P1-012 用户验证计划是否足以满足最低门槛；
  - 外部用户验证线暂停是否可以接受；
  - “自用 MVP 有限例外”的边界、补偿机制和失效条件是否充分。
- 重点评估工程准入风险：
  - R-0040 真实 Tauri / IPC 复测；
  - 真实 Obsidian Vault 接入；
  - 真实敏感数据进入系统；
  - 真实云 / 第三方模型调用；
  - 删除 / 撤回和派生失效；
  - 导出 / 恢复 / 重导入；
  - 动态交互、响应式、可访问性；
  - Schema / API / 技术实现仍未冻结的影响。
- 给出独立评审结论和 PM 决策建议：
  - Pass：可建议 PM 进入 Stage 3 / MVP 开发准入决策；
  - Pass with Conditions：可建议有限准入，但必须列出硬约束；
  - Rework / Blocked：不得准入，需先补齐指定缺口。

## 非范围

本任务暂时不要做：

- 不进入正式 MVP 开发。
- 不创建工程任务、开发计划、代码脚手架、数据库 Schema、API、Tauri 配置或测试脚本。
- 不修改 Stitch 或任何原型。
- 不冻结新的产品、技术、交互、Schema、API、同步栈、真实 Tauri capability、真实云 / 第三方模型或生产 SLA。
- 不联系真实用户，不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不替 PM 主会话和用户做最终 Stage 3 准入决策。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/RISK_LOG.md` 中 R-0039、R-0040，以及与真实数据、权限、删除、Obsidian、Tauri / IPC、云 / 第三方模型相关的开放 P0/P1 风险
- `lifeos/DECISION_LOG.md` 中 D-0081 至 D-0125，或最近 5-10 条与准入相关的决策
- `lifeos/deliverables/LIFEOS-P2-017_mvp_development_entry_review_package.md`
- `lifeos/reviews/LIFEOS-P2-017_pm_review.md`
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
- 优先读取摘要、冻结状态、PM Review、独立评审、风险行和准入相关决策；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；只读取 D-0081 至 D-0125 或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 交付物正文按独立评审型任务篇幅控制；超出范围的内容放入“后续任务建议”。
- 聊天回复只输出摘要、评审文件路径、是否需要 PM 决策。
- 评审完成后，默认调用本地预检：`python3 lifeos/tools/local_precheck.py <评审文件路径>`。
- 会话回复应引用本地预检报告路径；若本地模型不可用、超时、输出为空、任务无明确交付物路径，或用户明确要求不调用本地模型，可跳过并说明原因。

## 角色检查点

主责角色必须重点回答：

- 是否建议允许进入正式 MVP 开发准入决策？
- 若建议条件准入，条件是否足够硬、可执行、可验收？
- 若建议阻塞，阻塞项是否具体、可补齐、可转成后续任务？

协审角色必须重点检查：

- 产品架构：仍服务个人终身外脑、V1 第一目标用户和第一场景；不得滑向企业后台、IT 运维或开发者工具。
- 技术架构：技术架构 V0.1 合同是否足以支撑有限 MVP；未冻结实现细节是否构成准入阻塞。
- AI 信任与安全：真实数据、授权重检、撤回 / 删除、第三方处理者和高风险内容边界是否可控。
- 数据 / 领域模型：用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认事实是否继续可区分、可追溯、可失效。
- 体验设计：首页 / 今日页静态原型冻结是否足以进入工程；动态交互、响应式、可访问性是否应作为准入条件或工程验收条件。
- 用户价值验证：Gate 5 计划层满足但结果层缺失是否可以作为自用 MVP 有限例外。

## 核心问题

请重点回答：

- Stage 3 / 正式 MVP 开发硬门槛逐项结论是什么？
- Gate 1-5 各自结论是什么？
- 是否接受 Gate 5 自用 MVP 有限例外？边界、补偿机制和失败退出条件是什么？
- R-0040 是否阻塞整个 MVP 开发，还是只阻塞真实 Tauri 文件能力 / Obsidian / 导出 / IPC 扩权等能力启用？
- 是否允许使用合成数据、低敏副本、默认关闭外部能力的方式进入有限工程实现？
- 如果允许，哪些能力必须默认关闭，哪些测试 / 复测必须在启用前完成？
- 独立评审最终建议是什么：Pass、Pass with Conditions、Rework / Blocked？

## 交付物

请将完整评审保存为：

`lifeos/reviews/LIFEOS-P2-018_mvp_development_entry_independent_review.md`

请输出的文件内容包括：

- 评审结论摘要
- Stage 3 硬门槛逐项评审表
- Gate 1-5 逐项评审
- Gate 5 自用 MVP 有限例外评估
- R-0040 与关键工程风险评估
- 可接受的准入条件 / 不可接受的准入条件
- 若条件准入，必须迁移为工程硬约束的清单
- 独立评审结论：Pass / Pass with Conditions / Rework / Blocked
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整评审已保存为指定文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供评审文件路径。
- 明确说明本任务不等于正式 MVP 开发准入。
- 明确区分事实、推断、建议和需 PM 确认事项。
- 明确列出各 Gate 是否通过、条件通过或未通过。
- 明确列出是否建议 PM 进入最终准入决策。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建工程任务或开发计划。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不冻结新的产品、技术、Schema、API 或交互资产。
- 不进入正式 MVP 开发。
- 不处理真实敏感数据。
