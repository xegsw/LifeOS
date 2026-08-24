# LIFEOS-P2-012｜技术架构独立评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- 本任务需要的相关模板

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-012
- 任务名称：技术架构独立评审
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2500-4500 字；正文应聚焦评审结论、风险和条件，不要重写技术架构大论文
- 主责角色：技术架构独立评审人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-010` 已完成技术架构候选综合评审与 Stage 2 收口判断，并由用户确认采纳。`LIFEOS-P2-011` 已完成技术架构冻结前条件整改包，PM 验收结论为 `Accepted / Pass with Conditions`，用户已确认采纳。

用户同时确认两条评审基线：

1. V1 自用版默认单设备、本地优先；同步 / 服务端具体栈后置，不作为当前技术架构冻结默认范围。
2. Obsidian 当前只冻结“条件适配器与降级合同”，不承诺 V1 正式启用、写回、插件或双向同步。

当前技术架构仍未冻结，正式 MVP 开发仍为 `Blocked / Not Allowed`。本任务是关键冻结事项前的独立评审，不是冻结补丁，也不是正式开发准入。

## 目标

本任务完成后，需要独立判断：

1. P2-010 与 P2-011 是否足以作为技术架构冻结前最终补丁的输入？
2. 当前候选架构是否仍存在 P0 级不清楚、不可信或不安全的空洞？
3. FTS 维护隔离与 Tauri / IPC 最小安全边界窄测，是否必须在技术架构冻结前先完成？
4. “单设备本地优先、同步 / 服务端后置”和“Obsidian 条件适配器 / 降级合同”两条 PM 决策是否被 P2-010/P2-011 正确继承？
5. 是否允许进入下一步“技术架构冻结条件补丁”，还是必须先返工或补 Spike？

## 范围

本任务必须评审：

1. 技术架构候选是否服务 LifeOS V1 自用闭环，而不是企业后台、IT 运维平台或过早重型架构。
2. 本地权威原文、SQLite + FTS-first、可重建派生、向量后置、模型 / 供应商可替换等方向是否有足够证据支持进入冻结前补丁。
3. FTS 维护隔离方案是否足以避免后台索引重建阻塞前台快速捕获。
4. 权威数据、派生数据、outbox / job 三类职责是否清楚，能支撑撤回 / 删除、离线状态、可信搜索、导出 / 恢复。
5. Tauri 文件与 IPC 边界是否足够保守，是否存在 Renderer 任意文件读写、路径越界、Vault 写回、身份混淆等高风险缺口。
6. Obsidian 是否被正确限制为条件接入、只读、可降级，不被误写成默认正式能力。
7. 同步 / 云端 / 服务端具体栈是否已被正确后置，且不影响 V1 自用版核心价值闭环。
8. Gate 2 / Gate 3 / Gate 4 是否可以在“合同层”通过，哪些条件必须保留。

## 非范围

本任务暂时不要做：

- 不重写技术架构方案。
- 不冻结技术架构。
- 不创建技术架构冻结补丁。
- 不进入正式 MVP 工程开发。
- 不编写生产代码、Schema、API、Tauri capability 或真实应用目录结构。
- 不运行新的技术 Spike，除非只做文件存在性或证据索引核对；不得创建新的证据包。
- 不修改 Stitch、首页原型、PRD 或 V1 范围。
- 不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不调用真实模型、真实云服务、真实第三方 API 或付费资源。
- 不重新比较所有技术栈、云平台、数据库或向量库。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P2-010_technical_architecture_candidate_review.md`
- `lifeos/deliverables/LIFEOS-P2-010_technical_architecture_candidate_review.md`
- `lifeos/reviews/LIFEOS-P2-010_pm_review.md`
- `lifeos/tasks/LIFEOS-P2-011_technical_architecture_freeze_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P2-011_technical_architecture_freeze_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P2-011_pm_review.md`
- `lifeos/reviews/LIFEOS-P2-009_pm_review.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- `lifeos/DECISION_LOG.md` 中 D-0109 至 D-0114

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`。
- 优先读取 P2-010、P2-011 的交付物和 PM Review。
- 其他 Spike 文件默认只读 PM Review 摘要；只有发现结论冲突或证据不足，才定向读取对应交付物的相关段落。
- 不主动读取完整 evidence 日志。
- 不主动读取完整 `PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `DECISION_LOG.md`，只读取 D-0109 至 D-0114 或最近相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 聊天回复只输出摘要、评审文件路径、是否需要 PM 决策。

## 角色检查点

主责角色必须重点回答：

- 候选技术架构是否有足够合同清晰度进入冻结前最终补丁？
- 是否仍存在 P0 技术空洞、证据缺口或高风险乐观推断？
- FTS / IPC 窄测是冻结前必做，还是可以作为实现前 / 开发准入前条件？
- 当前是否继续阻止正式 MVP 开发？

协审角色必须重点检查：

- 数据 / 领域模型负责人：权威原文、版本、Source、Artifact、Derivation、tombstone、generation、outbox 边界是否清楚。
- AI 信任与安全负责人：授权、来源、AI 输出身份、派生失效、外发前重检、重大动作确认是否无漏洞。
- 产品架构负责人：技术方案是否服务 V1 第一场景和自用闭环，不变成重型平台。
- 体验设计负责人：前台记录、搜索恢复、今日重点、下一步行动是否不会被后台维护或同步复杂度拖垮。
- PM：是否明确哪些结论可沉淀，哪些必须作为后续任务或用户决策。

## 核心问题

请重点回答：

1. 独立评审总体结论是什么：Pass / Pass with Conditions / Rework / Blocked？
2. P2-010 与 P2-011 是否足以进入技术架构冻结前最终补丁？
3. FTS 维护隔离是否仍是冻结前 P0 阻断？是否必须先做窄测？
4. Tauri 文件与 IPC 最小安全边界是否仍是冻结前 P0 阻断？是否必须先做窄测？
5. 单设备本地优先、同步 / 服务端后置的基线是否合理？
6. Obsidian 条件适配器 / 降级合同是否合理？是否存在被误读为正式启用承诺的风险？
7. 当前是否仍必须阻止正式 MVP 开发？
8. 下一步应启动冻结条件补丁、补窄测、返工，还是阶段盘点？

## 交付物

请将完整评审保存为 Markdown 文件：

`lifeos/reviews/LIFEOS-P2-012_technical_architecture_independent_review.md`

请输出的文件内容包括：

1. 评审摘要
2. 评审依据与范围
3. 总体结论
4. Gate 2 数据与来源评审
5. Gate 3 AI 权限与信任评审
6. Gate 4 技术可行性评审
7. 五个重点条件逐项评审：FTS、权威 / 派生 / outbox、Tauri / IPC、Obsidian、同步 / 云端
8. 对 P2-010 / P2-011 的可接受内容
9. 必须修正、补证或 PM 决策的问题
10. 是否允许进入技术架构冻结前最终补丁
11. 是否允许进入正式 MVP 开发
12. 后续任务建议

篇幅控制：

- 独立评审型任务建议 2000-4000 字。
- 本任务若因评审矩阵略超，允许到 4500 字，但不要重写完整技术方案。
- 超出当前评审范围的实现细节、代码方案、长期云架构和性能调优，放入“后续任务建议”。
- 交付物必须完整，但聊天回复必须简短。

## 验收标准

只有满足以下条件，任务才算完成：

- 独立给出 Pass / Pass with Conditions / Rework / Blocked 结论。
- 覆盖 Gate 2 / Gate 3 / Gate 4。
- 明确评审 FTS、权威 / 派生 / outbox、Tauri / IPC、Obsidian、同步 / 云端五项条件。
- 明确是否允许进入技术架构冻结前最终补丁。
- 明确 FTS / IPC 窄测是否必须先做。
- 明确是否仍阻止正式 MVP 开发。
- 明确哪些问题需要 PM 主会话确认。
- 未修改生产代码、Stitch、PRD、V1 范围或技术架构冻结状态。
- 完整评审已保存到指定路径。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，且不粘贴完整评审正文。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不进入正式 MVP 开发。
- 不处理真实敏感数据、真实 Vault 或真实第三方数据。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评审正文，只输出摘要和评审路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入评审文件。
