# LIFEOS-P2-010｜技术架构候选综合评审与 Stage 2 收口判断

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-010
- 任务名称：技术架构候选综合评审与 Stage 2 收口判断
- 优先级：P0
- 任务类型：评审型任务 / 决策型任务（综合架构评审，不是冻结任务）
- 建议篇幅：3000-5000 字；证据矩阵、风险清单和整改项可用表格，避免写成大论文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS 已完成 Stage 2 技术验证线的 9 个阻断型 Spike：

- SP-01 本地可靠落盘、离线捕获、备份恢复；
- SP-02 Obsidian Vault 只读接入与来源身份；
- SP-03 来源、版本、Derivation 与证据链最小映射；
- SP-04 六维授权判定与本地 / 云 / 第三方处理边界；
- SP-05 撤回 / 删除传播、依赖发现与清理验证；
- SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性；
- SP-07 混合搜索、Project 恢复包与可信建议证据；
- SP-08 可迁移导出、恢复与重导入；
- SP-09 100 万内容单元 / 300 万分块容量与性能。

当前已知状态：

- 多数 Spike 已被用户采纳为后续输入。
- SP-02 和 SP-09 是 `Pass with Conditions`，不能视为无条件通过。
- SP-09 的关键条件是：全量 FTS rebuild 阻塞前台捕获约 4 秒，正式技术架构必须解决“索引维护不能阻塞权威捕获”的问题。
- 技术架构仍未冻结。
- 正式 MVP 开发仍为 `Blocked / Not Allowed`。

本任务的目的不是继续做新的技术 Spike，也不是冻结技术架构，而是把 SP-01 至 SP-09 的证据收拢成一个可供 PM 判断的“技术架构候选评审包”：哪些候选可以进入冻结前整改，哪些必须降级或后置，哪些风险仍阻塞 Stage 3。

## 目标

本任务完成后，要回答：

1. SP-01 至 SP-09 是否足以支持进入“技术架构冻结前整改 / 独立评审准备”？
2. 当前最合理的 V1 候选技术架构是什么？它只应是候选，不得写成冻结结论。
3. 哪些技术结论已被 Spike 支撑，哪些只是推断，哪些仍未验证？
4. SP-02 与 SP-09 的条件项如何处理：整改、降级、后置、移出 V1，还是列为冻结前阻断条件？
5. V1 是否应采用 FTS-first，而不是把向量作为默认硬依赖？
6. Obsidian 接入、同步、搜索、导出、删除、权限、备份恢复分别应进入 V1 的什么强度？
7. 技术架构冻结前必须补哪些条件整改或独立评审？
8. Stage 2 是否可以收口？如果可以，收口边界是什么？如果不可以，缺什么？
9. 正式 MVP 开发是否仍然阻塞？阻塞项是什么？
10. 下一步建议启动什么任务？

## 范围

本任务必须覆盖：

- 汇总 SP-01 至 SP-09 的 PM 验收状态、用户采纳状态、核心证据、条件项和不可外推内容。
- 形成 V1 候选架构边界：
  - 桌面 / 本地优先候选；
  - 本地权威原文与可重建派生；
  - SQLite / FTS-first 是否作为候选；
  - Fastify / 模块化单体 / PostgreSQL / pgvector 仍处于什么候选状态；
  - Obsidian 只读来源条件；
  - 同步、队列、授权判定、删除清理、导出重导入、备份恢复的候选责任边界。
- 明确每个候选的证据等级：
  - 已实测；
  - 条件通过；
  - 仅估算；
  - 未验证；
  - 不建议进入 V1。
- 给出“架构冻结前条件整改清单”。
- 给出“Stage 2 收口判断”。
- 给出“正式 MVP 开发准入判断”。
- 给出下一步任务建议。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不修改 Stitch。
- 不连接真实 Vault、真实云、真实模型、真实第三方 API 或付费资源。
- 不处理真实敏感数据。
- 不执行新的性能测试或技术 Spike。
- 不冻结技术架构。
- 不冻结数据库、Schema、API、队列、同步方案、模型供应商、向量方案、备份 / 灾备 SLA 或性能 SLA。
- 不进入正式 MVP 开发。
- 不改变产品定位、V1 范围、AI 权限模型或核心领域模型。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/deliverables/LIFEOS-P1-014_self_use_mvp_dev_readiness_roadmap.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-004_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-007_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-008_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-009_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`。
- 优先读取各 SP 的 PM Review，再按需读取对应交付物的结论摘要、条件项和证据路径。
- 不主动读取完整证据日志；只有发现交付物和 PM Review 冲突时，才读取对应 Spike 证据入口。
- 不主动读取全量 `DECISION_LOG.md`；如需决策上下文，只读取 D-0035、D-0038、D-0039、D-0050、D-0055、D-0108、D-0109、D-0110 或最近 5-10 条相关决策。
- 若上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 技术架构候选是否有证据支撑，而不是“看起来先进”？
- 是否控制了过早引入微服务、Kafka、Kubernetes、图数据库、专用向量库等重型方案的冲动？
- 是否明确了 SQLite / FTS5、PostgreSQL、pgvector、Tauri、React、Fastify、模型网关等候选状态？
- 是否明确哪些能力 Must / Should / Not Now？
- 是否明确 Stage 3 仍不能启动的原因？

协审角色必须重点检查：

- 数据 / 领域模型负责人：候选架构是否保留 Source、ArtifactVersion、Derivation、Authorization、Feedback、AuditEntry、Link、墓碑和可重建派生语义。
- AI 信任与安全负责人：授权、撤回、删除、外发、本地 / 云 / 第三方边界和用户确认是否继承冻结模型。
- 产品架构负责人：技术方案是否服务个人终身外脑和 V1 第一场景，而不是偏向企业后台、IT 运维或炫技架构。
- 体验设计负责人：保存、索引中、恢复、删除清理、离线同步、导出失败等技术状态是否能转成用户可理解语言。
- PM：是否清楚区分“任务验收”“资产冻结”“下一阶段准入”。

## 核心问题

请重点回答：

1. SP-01 至 SP-09 的总体验收矩阵是什么？
2. 哪些技术能力已经足够进入 V1 候选架构？
3. 哪些技术能力只能条件进入？
4. 哪些技术能力应后置或移出 V1？
5. 候选架构的最小组成是什么？每一部分解决什么问题？
6. 哪些内容必须在技术架构冻结前整改？
7. 哪些内容可以在正式开发中边做边验证，哪些绝不能？
8. 是否建议 Stage 2 收口？收口后进入的不是 Stage 3 开发，而是什么？
9. 正式 MVP 开发准入还缺哪些硬门槛？
10. 下一步任务应该是技术架构条件整改、技术架构独立评审，还是补充 Spike？

## 交付物

请将完整交付物保存为 Markdown 文件：

`lifeos/deliverables/LIFEOS-P2-010_technical_architecture_candidate_review.md`

文件内容至少包含：

- 执行摘要；
- SP-01 至 SP-09 证据矩阵；
- V1 候选技术架构；
- 条件进入 / 后置 / 禁止项；
- 技术架构冻结前整改清单；
- Stage 2 收口判断；
- Stage 3 MVP 开发准入判断；
- 需要 PM / 用户确认的问题；
- 下一步任务建议。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存到指定路径。
- 明确区分事实、推断、建议和需 PM 确认事项。
- 明确区分 Accepted、Pass with Conditions、Frozen、Blocked / Not Allowed。
- 不把 P2-010 结论写成技术架构冻结。
- 不把 Stage 2 收口写成正式 MVP 开发准入。
- 覆盖 Gate 2 / Gate 3 / Gate 4。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改 PM 主账本。
- 不执行新的 Spike 或性能测试。
- 不连接真实 Vault、真实云、真实模型、真实第三方或付费资源。
- 不处理真实敏感数据。
- 不冻结技术架构。
- 不进入正式 MVP 开发。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、是否需要 PM 决策。
