# LIFEOS-P2-011｜技术架构冻结前条件整改包

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- 本任务需要的相关模板

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-011
- 任务名称：技术架构冻结前条件整改包
- 优先级：P0
- 任务类型：条件整改 / 补丁型任务
- 建议篇幅：2000-3500 字；如确需补充表格或证据索引，可放入附录，不要扩写成新一轮大论文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与信任、Gate 3 技术可行性、Gate 4 本地优先与可迁移性
- 状态：Ready

## 背景

`LIFEOS-P2-010` 已通过 PM 验收，结论为 `Accepted / Pass with Conditions`，并由用户确认采纳。P2-010 已经完成 SP-01 至 SP-09 的综合判断：技术 Spike 线可以条件收口，但 Stage 2 → Stage 3 仍不通过，技术架构尚未冻结，正式 MVP 开发仍为 `Blocked / Not Allowed`。

当前最关键的问题不是继续做宽泛技术选型，而是把 P2-010 标出的架构冻结前 P0 条件逐项关闭、定界或转化为明确的后续验证任务，避免后续独立评审时仍然停留在“候选架构说得通，但边界不够硬”的状态。

## 目标

本任务完成后，需要回答：

1. 技术架构冻结前的 P0 条件分别处于什么状态：已通过架构合同关闭、仍需独立评审确认、仍需 PM 决策，还是必须追加小型验证？
2. SQLite + FTS-first、本地权威原文、可重建派生、向量后置、Obsidian 条件接入等候选方向，是否已经具备进入独立评审的最小清晰度？
3. 是否仍存在阻止技术架构独立评审的 P0 空洞？
4. 是否仍必须阻止正式 MVP 开发准入？

## 范围

本任务必须覆盖以下 5 个条件整改主题：

### 1. FTS 维护隔离与权威捕获不阻塞

- 针对 P2-009 暴露的“全量 FTS rebuild 阻塞前台捕获约 4 秒”问题，给出架构整改方案。
- 明确权威原文写入必须优先于索引维护、派生更新和长任务。
- 说明候选机制，例如：短事务权威写入、索引异步队列、分块维护、影子 FTS 表 / 影子索引、可中断重建、前台捕获降级策略。
- 明确哪些机制属于冻结前必须写入架构合同，哪些属于实现阶段可选优化。

### 2. 权威数据、派生数据与 outbox 职责合同

- 定义“什么是权威事实、什么是可重建派生、什么是待执行 / 待外发队列”。
- 明确用户原文、用户确认状态、版本、撤回 / 删除 / tombstone、授权状态、审计记录的权威位置。
- 明确摘要、向量、分类、关联、恢复包、AI 建议等派生产物必须可追溯、可失效、可重建。
- 明确 outbox 发布前必须重检授权、版本、tombstone / restriction generation 和来源状态。

### 3. Tauri 文件与 IPC 最小安全边界

- 给出桌面端最小安全边界：Renderer 不直接获得任意文件读写权，文件访问由后端命令白名单和作用域控制。
- 明确路径规范化、目录白名单、Obsidian Vault 只读适配、附件访问、导出目录、日志目录等边界。
- 明确哪些命令可读、可写、可导出、可删除，以及哪些必须默认拒绝。
- 明确 IPC 返回内容不得混淆用户原文、AI 生成内容、AI 推断 / 建议和外部来源。

### 4. Obsidian 条件接入处置

- 继承 Obsidian 为 V1 `Should Have + 条件性需求` 的口径。
- 明确默认不承诺写回 Obsidian，不把 Obsidian 当作 LifeOS 权威数据源。
- 明确启用 Obsidian 接入的条件，例如：用户授权、只读、来源身份稳定、断源不复活、同步盘 / 大 Vault / 跨平台风险可控。
- 给出未满足条件时的降级路径，例如：手动导入、来源指针、暂缓接入或只做引用。

### 5. 同步 / 云端候选范围裁决

- 基于 SP-06 结果，判断 V1 自用版是否应默认保持单机本地优先，还是保留有限同步候选。
- 明确“同步能力是否进入 V1”是 PM 决策项，而不是专项会话单方面冻结项。
- 如果建议保留同步候选，必须给出最小边界：设备数、权威位置、冲突处理、outbox、删除 / 撤回传播、云端可见数据范围。
- 如果建议后置同步，必须说明如何不影响自用 MVP 的核心价值：记录、整理、检索、今日重点、下一步行动、导出 / 备份。

## 非范围

本任务暂时不要做：

- 不冻结技术架构。
- 不进入正式 MVP 工程开发。
- 不创建生产代码、生产数据库 Schema、正式 API 或真实应用目录结构。
- 不修改 Stitch、首页原型、PRD 或产品范围。
- 不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不调用真实模型、真实云服务、真实第三方 API 或付费资源。
- 不重新打开宽泛技术选型研究，例如重新比较所有桌面框架、数据库、向量库或云平台。
- 不替代后续技术架构独立评审。

如确有必要，可且仅可在 `lifeos/spikes/P2-011/` 下创建可丢弃的小型补证脚本、合成夹具、日志和 evidence manifest，用于验证本任务的局部条件；这些内容不得被描述为产品代码或正式实现。

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
- `lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-009_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`
- `lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`
- `lifeos/DECISION_LOG.md` 中 D-0102 至 D-0112

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`。
- 优先读取 P2-010 交付物和 PM Review；其他 Spike 文件只定向读取与本任务 5 个整改主题直接相关的段落。
- 不主动读取全量历史交付物、无关 Review 或完整 evidence 日志。
- 不主动读取完整 `PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `DECISION_LOG.md`，只读取 D-0102 至 D-0112 或最近相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。

## 角色检查点

主责角色必须重点回答：

- 技术架构候选是否已经能被写成可评审的条件合同，而不是抽象倾向。
- P2-009 FTS 阻塞问题是否有明确、不牺牲前台记录体验的整改方案。
- 权威数据、派生数据和 outbox 的职责是否足够清楚，能支撑撤回 / 删除、离线同步、可信搜索、导出 / 恢复。
- Tauri 文件与 IPC 边界是否足够保守，符合个人数据主权和本地优先定位。
- 同步 / 云端范围是否被清晰标记为 PM 决策，而不是默默进入架构冻结。

协审角色必须重点检查：

- 数据 / 领域模型负责人：是否保护用户原文、版本、来源、证据链、撤回 / 删除语义和可重建派生。
- AI 信任与安全负责人：是否区分用户原文、AI 生成内容、AI 推断 / 建议、外部引用来源；是否保证重大行动需用户确认。
- 产品架构负责人：是否仍围绕自用 V1 第一场景，不扩展成企业后台或 IT 运维平台。
- 体验设计负责人：是否保证前台快速记录、今日重点、搜索恢复和下一步确认不被后台维护任务拖垮。
- PM：是否明确哪些结论可进入独立评审，哪些仍需 PM 决策或后续验证。

## 核心问题

请重点回答：

1. P2-010 列出的 P0 条件逐项如何处理？
2. 哪些条件可以通过架构合同关闭？
3. 哪些条件需要独立评审确认？
4. 哪些条件需要 PM 决策？
5. 哪些条件需要追加小型验证或后续任务？
6. 是否建议 V1 自用版默认单机本地优先，并将多设备同步后置或条件化？
7. 当前是否可以进入“技术架构独立评审”？如果不能，缺口是什么？
8. 当前是否仍必须阻止正式 MVP 开发？原因是什么？

## 交付物

请将完整交付物保存为 Markdown 文件：

`lifeos/deliverables/LIFEOS-P2-011_technical_architecture_freeze_condition_remediation.md`

请输出的文件内容包括：

1. 执行摘要
2. P2-010 条件继承说明
3. 条件整改总表
4. FTS 维护隔离与权威捕获不阻塞方案
5. 权威 / 派生 / outbox 职责合同
6. Tauri 文件与 IPC 最小安全边界
7. Obsidian 条件接入处置
8. 同步 / 云端候选范围裁决建议
9. 架构独立评审前准备状态
10. 正式 MVP 开发准入状态判断
11. 风险、待确认问题与后续任务建议
12. 附录：如有小型补证，列出 evidence manifest 路径与摘要

篇幅控制：

- 条件整改 / 补丁型任务建议 1500-3000 字；本任务因涉及技术架构冻结前条件，允许正文 2000-3500 字。
- 超出范围的技术比较、实现细节、测试日志和长期方案，请放入“后续任务建议”或 evidence 附录，不要在正文无限展开。
- 交付物必须完整，但聊天回复必须简短。

## 验收标准

只有满足以下条件，任务才算完成：

- 已逐项处理 5 个条件整改主题。
- 明确区分：已关闭、需独立评审、需 PM 决策、需后续验证。
- 对 P2-009 FTS 阻塞问题给出架构层整改方案。
- 给出权威 / 派生 / outbox 的职责合同。
- 给出 Tauri 文件与 IPC 最小安全边界。
- 明确 Obsidian 仍为条件接入，不写成默认已实现能力。
- 明确同步 / 云端范围裁决建议，并标记是否需要 PM 决策。
- 明确当前是否可以进入技术架构独立评审。
- 明确当前不得进入正式 MVP 开发。
- 未修改生产代码、Stitch、PRD、范围或核心冻结资产。
- 完整交付物已保存到指定路径。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，且不粘贴完整交付物正文。

## 限制条件

- 不修改代码，除非仅在 `lifeos/spikes/P2-011/` 下创建可丢弃小型补证。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不进入正式 MVP 开发。
- 不处理真实敏感数据、真实 Vault 或真实第三方数据。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入交付物文件。
