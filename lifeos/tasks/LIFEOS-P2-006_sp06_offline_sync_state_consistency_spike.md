# LIFEOS-P2-006｜SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性技术 Spike

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的相关文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-006
- 任务名称：SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵、状态转换表、重放结果、冲突样例和脚本可放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 4 技术可行性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审
- 状态：Ready

## 背景

`LIFEOS-P2-001` 已通过 PM 验收并由用户确认采纳，证明本地可靠保存、版本追加、幂等、离线保存 / 待同步分离、墓碑 / 撤回恢复优先等最小存储语义成立。

`LIFEOS-P2-002` 已通过 PM 验收并由用户确认采纳，证明最小证据链包络成立：恢复包、AI 候选或用户确认对象都必须能追溯 Source、Artifact、Version、Derivation、Feedback、Authorization、AuditEntry 与 Link。

`LIFEOS-P2-003` 已通过 PM 验收并由用户确认采纳，项目级结论为 `Pass with Conditions`：Obsidian 只读来源身份在模拟 Vault 范围内具备最小可行性，但真实 Vault、跨平台、同步盘、大 Vault、正式解析库、运行时授权和清理仍未放行。

`LIFEOS-P2-004` 已通过 PM 验收并由用户确认采纳，证明六维 Authorization、强制政策包络、默认拒绝、运行时重检、最小化外发、长任务撤回隔离和审计隐私在合成夹具与 mock 处理者范围内成立。

`LIFEOS-P2-005` 已通过 PM 验收并由用户确认采纳，证明四类命令分离、撤回 / 删除后活跃阻断零遗漏、两阶段清理状态、故障恢复、不复活和供应商受限披露在合成 mock / 单进程候选实现范围内成立。

现在要验证 SP-06：

> 当用户有 3-5 台设备、离线编辑、重复上传、乱序同步、并发反馈、撤回和删除时，LifeOS 是否能保证原文版本、用户确认状态、Action / Decision / Link / Feedback 的权威状态不会被 AI 候选、旧设备、旧队列或 LWW 覆盖。

本任务允许在 `lifeos/spikes/SP-06/` 下创建最小本地验证代码、合成多设备夹具、状态转换矩阵、同步协议候选、消息重放器、队列 mock、冲突样例、日志和证据包。不得处理真实敏感数据，不得连接真实 Vault，不得调用真实模型、真实云或真实第三方 API，不得冻结 Schema / API / 技术架构，不得进入正式 MVP 开发。

## 目标

本任务完成后，要回答：

1. V1 是否可以用“客户端操作 ID + 不可变版本 + 服务端权威状态 + 对象级前置版本 + append-only Feedback / 操作日志 + tombstone 优先”满足最小离线同步，而不引入全量 CRDT 或事件溯源？
2. 同一客户端操作重复提交 100 次是否只产生一个业务效果，且审计可解释重试？
3. 离线 A / B / C 设备并发编辑、重复上传、乱序、延迟和旧队列重试时，原文版本是否不丢、不覆盖、不被 AI 候选改写？
4. 用户对同一 AI 候选一端接受、一端拒绝、一端编辑后接受时，系统是否收敛到确定状态或显式冲突，而不是最后写入者胜出？
5. Action 完成 / 延期、Decision 修订、Link 确认 / 纠正、Feedback 撤回是否能追加记录并重算当前状态，不覆盖历史？
6. 已删除对象、已撤回授权、已断开 Source、已失效证据在离线旧设备重连、旧队列重试或恢复包重建时是否不会复活或重新入模？
7. 队列任务执行前是否重新校验对象版本、Authorization 版本、policy 版本、tombstone generation 和任务租约；过期任务是否不会产生可见输出？
8. L3 候选 Action / Decision / Link 若物化，是否显著增加同步复杂度；是否应继续降级为 L1 Derivation 展示？
9. 当自动合并不安全时，V1 应如何降级：保留双版本、显式冲突、请求用户处理、缩小多设备实时同步范围？
10. 当前结果是否足以决定 V1 的同步能力保留、降级、后置或阻断正式 MVP 开发？

## 范围

本任务必须覆盖：

- 多设备夹具：
  - 3 台默认设备 A / B / C；
  - 可扩展到 5 台设备的重放器；
  - 在线、离线、重连、延迟、重复提交、乱序消息；
  - 同一用户、单账号候选范围；
  - 不涉及多人共享。
- 对象与状态：
  - 用户原文新增 / 编辑；
  - ArtifactVersion 不可覆盖；
  - AI 候选 Action；
  - 用户确认 Action；
  - Decision 修订；
  - Link 确认 / 纠正；
  - Feedback：确认、编辑、拒绝、纠正、完成、延期、撤回；
  - Derivation stale / invalid / review_required；
  - Authorization 版本；
  - tombstone / restriction generation；
  - AuditEntry 最小化。
- 同步操作：
  - `create_artifact_version`；
  - `edit_artifact`；
  - `create_ai_candidate`；
  - `accept_candidate`；
  - `accept_candidate_with_edit`；
  - `reject_candidate`；
  - `retract_feedback`；
  - `complete_action`；
  - `defer_action`；
  - `revise_decision`；
  - `confirm_link`；
  - `correct_link`；
  - `revoke_processing`；
  - `delete_content`；
  - `disconnect_source`；
  - `queue_task_execute`。
- 冲突与异常：
  - 同一原文双端离线编辑；
  - 同一候选一端接受、一端拒绝；
  - 一端编辑后接受，另一端接受原候选；
  - 用户编辑与 AI 重建并发；
  - 已删除对象被旧设备重新上传；
  - 撤回授权时仍有离线队列；
  - Feedback 撤回与 Action 完成并发；
  - Decision 修订与旧恢复包生成并发；
  - Link 确认与纠正并发；
  - Source 断开后旧设备继续提交读取结果；
  - tombstone 与旧版本乱序到达。
- 对比方案：
  - 服务端权威 + append-only Feedback / 操作日志；
  - 字段级 LWW；
  - 有限 CRDT；
  - 队列作为辅助执行，不作为权威状态来源。
- 验证输出：
  - 状态转换 / 冲突矩阵；
  - 同步协议最小契约；
  - 重放测试结果；
  - 队列故障报告；
  - 需要用户解决的冲突清单；
  - 降级建议。

## 非范围

本任务暂时不要做：

- 不开发正式同步服务。
- 不开发正式产品 UI。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实 `.obsidian` 配置。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不实现多人协作、共享空间、企业权限、组织审计或团队协同。
- 不实现完整 CRDT 框架。
- 不实现正式云同步、正式队列、正式数据库迁移或正式冲突 UI。
- 不承诺同步 SLA、跨设备数量、实时性、离线窗口或生产容量。
- 不冻结数据库 Schema、API、事件流、队列实现、同步协议、桌面框架、技术栈或技术架构。
- 不实现 SP-07 搜索质量。
- 不实现 SP-08 正式导出迁移。
- 不实现 SP-09 容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-06/` 下创建和修改：
  - 本地验证脚本；
  - 合成多设备夹具；
  - 状态转换矩阵；
  - 冲突矩阵；
  - 同步协议候选；
  - 消息重放器；
  - 队列 / 租约 mock；
  - tombstone / generation mock；
  - 幂等操作记录；
  - 测试矩阵；
  - 重放结果；
  - 队列故障报告；
  - 冲突样例；
  - 方案对比；
  - 结果 JSON；
  - 日志；
  - 环境说明；
  - 清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确任务目录或系统临时目录；不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话：

- 修改 `PROJECT_CONTEXT.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md` 等 PM 文件。
- 修改现有非 Spike 项目代码或无关文件。
- 删除、覆盖或移动用户真实数据。
- 使用破坏性命令清理宽泛目录。
- 读取真实 Vault、真实用户文件、真实凭据或真实敏感内容。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/OPEN_QUESTIONS.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/reviews/LIFEOS-P1-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/reviews/LIFEOS-P1-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- `lifeos/reviews/LIFEOS-P1-017_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-018_first_technical_spike_task_cards.md`
- `lifeos/reviews/LIFEOS-P1-018_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-001_pm_review.md`
- `lifeos/spikes/SP-01/`
- `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-002_pm_review.md`
- `lifeos/spikes/SP-03/`
- `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- `lifeos/spikes/SP-02/`
- `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-004_pm_review.md`
- `lifeos/spikes/SP-04/`
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- `lifeos/spikes/SP-05/`

## 角色检查点

主责角色必须重点回答：

- 最小同步协议是否能支撑 V1，而不是过早引入完整 CRDT、事件溯源或重型同步平台？
- 操作幂等、前置版本、tombstone 优先、租约 fencing、旧队列重检是否真实进入验证路径？
- 队列是否只是执行辅助，而不是权威状态来源？
- 在自动合并不安全时，是否能清楚降级为显式冲突和用户处理？
- 单进程 / 合成验证的边界是否写清，不外推为生产同步 SLA？

协审角色必须重点检查：

- 数据 / 领域模型负责人：ArtifactVersion、Action、Decision、Link、Feedback、Derivation、Authorization、AuditEntry 的身份、状态和历史是否不被覆盖。
- AI 信任与安全负责人：AI 候选是否不能自动覆盖用户确认、拒绝、纠正、撤回；撤回 / 删除是否仍活跃阻断。
- 产品架构负责人：同步能力是否服务个人外脑和自用 MVP，不扩成多人协作或企业工作台。
- 体验设计负责人：冲突、待复核、旧设备被拒绝、同步延迟、撤回生效等状态是否能转成用户能懂的体验语言。

## 核心问题

请重点回答：

1. 你采用了什么最小同步状态模型？为什么足以验证 SP-06，而不是冻结正式 Schema / API？
2. `operation_id`、`device_id`、`base_version`、`object_version`、`tombstone_generation`、`auth_version`、`policy_version`、`lease` 如何参与判定？
3. 同一操作重复提交 100 次是否只有一个业务效果？如何审计重试？
4. 乱序 / 延迟 / 并发消息如何处理？哪些能自动收敛，哪些必须显式冲突？
5. 字段级 LWW 为什么是否可接受？在哪些对象上必须禁止？
6. AI 候选、用户确认 Action、Decision、Link、Feedback 的当前状态如何重算？历史如何保留？
7. Feedback 撤回、Action 完成 / 延期、Decision 修订、Link 确认 / 纠正的并发如何处理？
8. 删除 / 撤回 tombstone 如何在离线旧设备重连、旧队列重试、备份 / 导入恢复时保持优先？
9. 队列任务执行前如何重新校验对象版本、授权版本、policy 版本和任务租约？
10. L3 候选物化是否会导致同步复杂度过高？是否建议继续降级为 L1 Derivation 展示？
11. 若多设备同步无法无条件通过，V1 应如何降级：单设备、本地优先、非实时、显式冲突、手动合并或后置云同步？
12. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
13. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 同一客户端操作重复 100 次只产生一个业务效果，AuditEntry 可解释重试。
- 原文编辑不会静默覆盖旧版本；冲突原文至少保留双版本或显式冲突。
- AI 候选不能自动覆盖用户确认、拒绝、纠正或撤回。
- 同一候选一端接受、一端拒绝、一端编辑后接受时，系统收敛到确定状态或显式冲突，不能字段级 LWW。
- Action 完成 / 延期、Decision 修订、Link 确认 / 纠正、Feedback 撤回均追加历史，不覆盖旧事件。
- Feedback 当前状态可由 Feedback / 版本解释；撤回 Feedback 以新记录表达。
- 删除 / 撤回 tombstone 优先阻断活跃使用；离线旧版本重连不得复活对象或重新入模。
- Source 断开后旧设备提交读取结果不得重新接入 Source 或生成新派生。
- 队列任务执行前重新校验对象版本、Authorization 版本、policy 版本、tombstone generation 和租约；过期任务不产生可见输出。
- 乱序 / 延迟 / 重复消息不能让 AI 候选转正为用户确认对象。
- L3 候选若物化，必须证明其同步 / 冲突 / 撤回成本可控；否则建议降级为 L1 Derivation 展示。
- 日志和 AuditEntry 不包含真实敏感原文、真实路径、真实 Vault 名、完整 prompt / 输出、向量或可还原真实数据。

## 建议测试矩阵

至少包含：

1. 单设备在线新增原文。
2. 单设备离线新增后同步。
3. 同一操作重复提交 100 次。
4. A / B 离线编辑同一原文。
5. A / B / C 乱序提交不同操作。
6. 旧 base_version 编辑被显式冲突化。
7. AI 候选创建后用户接受。
8. AI 候选创建后用户拒绝。
9. 同一候选 A 接受、B 拒绝。
10. 同一候选 A 编辑后接受、B 接受原候选。
11. 用户编辑与 AI 重建并发。
12. Action 完成与延期并发。
13. Action 完成后旧设备延期。
14. Decision 修订与旧恢复包生成并发。
15. Link 确认与纠正并发。
16. Feedback 撤回确认。
17. Feedback 撤回拒绝。
18. Feedback 撤回纠正。
19. Feedback 撤回完成。
20. Feedback 撤回延期。
21. 删除对象后旧设备重新上传。
22. 撤回处理后旧队列执行。
23. Source 断开后旧设备提交读取结果。
24. tombstone 先到、旧版本后到。
25. 旧版本先到、tombstone 后到。
26. 队列任务租约过期。
27. 队列任务重复领取。
28. 队列任务执行前 auth_version 变化。
29. 队列任务执行前 policy_version 变化。
30. 队列任务执行前输入 tombstone 出现。
31. 跨 Project 候选 Link 不扩权。
32. 用户确认对象唯一证据失效后 review_required。
33. 字段级 LWW 对用户权威对象失败样例。
34. 有限 CRDT 复杂度 / 适用边界样例。
35. 服务端权威 + append-only 方案通过样例。
36. 审计 / 日志隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-06/`

证据包至少包括：

- `SP-06_report.md`
- `sync_contract.md`
- `state_transition_matrix.csv`
- `conflict_matrix.md`
- `replay_results.json`
- `queue_recheck_report.md`
- `candidate_consistency_report.md`
- `feedback_history_report.md`
- `tombstone_replay_report.md`
- `strategy_comparison.md`
- `user_conflict_samples.json`
- `test_matrix.csv`
- `results.json`
- `environment.md`
- `raw_logs/`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 最小同步模型与非冻结说明
3. 对象状态、版本、操作 ID、设备 ID 和 generation 合同
4. 状态转换 / 冲突矩阵
5. 幂等、重复、乱序、延迟和离线重放验证
6. 原文版本、AI 候选、用户确认 Action / Decision / Link / Feedback 一致性验证
7. Feedback 追加历史与当前状态重算验证
8. tombstone / 撤回 / Source 断开 / 旧队列不复活验证
9. 队列执行前版本、授权、policy 和租约重检验证
10. LWW / 有限 CRDT / 服务端权威 + append-only 方案对比
11. L3 候选物化成本与降级建议
12. 测试矩阵与最低验收断言结果
13. 最终结论：Pass / Pass with Conditions / Fail / Blocked
14. 对 V1 同步能力、AI 候选、删除 / 撤回、后续 Spike 和技术架构候选的影响
15. 需要 PM / 用户确认的问题
16. 角色与关卡自检
17. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-06 的问题放入“后续任务建议”，不要扩写 SP-07 / SP-08 / SP-09。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-06/`。
- 证据包可复跑、可复核，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 4、Gate 2、Gate 3 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：全部幂等、乱序、并发、离线重放、用户确认不被 AI 覆盖、tombstone 优先、队列重检、状态历史和隐私 P0 断言通过；证据可复跑。
- **Pass with Conditions**：P0 断言全部通过，仅实时性、设备数、非核心对象类型、性能预算或冲突体验存在有界缺口，且已有明确降级和复验条件。
- **Fail**：任何用户原文被静默覆盖、任何 AI 候选覆盖用户确认 / 拒绝 / 纠正、任何删除 / 撤回被旧设备复活、任何过期队列产生可见输出、任何字段级 LWW 破坏用户权威、任何日志泄露真实敏感信息，或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实云、真实设备账号、真实 Vault 或真实敏感数据弥补 mock 不足。

## 降级路径

若 SP-06 无法无条件通过，应明确建议以下一种或多种降级：

- V1 暂不启用多设备云同步，只保留单设备本地优先。
- V1 仅支持单账号少设备、非实时同步。
- 冲突原文保留双版本并请求用户处理，不自动合并。
- Action / Decision / Link 采用对象级前置版本检查，冲突时显式提示。
- L3 候选继续降级为 L1 Derivation 展示，不进入持久业务集合。
- 队列只作为本地 / 服务端辅助执行，不作为权威状态来源。
- 向量、云 AI、第三方处理继续关闭，直到同步和撤回重检通过。

不可降级底线：用户原文不可静默覆盖；AI 候选不可替用户确认；Feedback 历史不可被改写；删除 / 撤回 tombstone 优先；过期队列不可产生可见输出；审计不可还原真实内容。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-06/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据、真实凭据、真实笔记或真实附件。
- 不调用真实模型、真实云服务或真实第三方 API。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-06 Pass 解释为正式同步 SLA、正式云架构、真实多设备生产能力、技术架构冻结或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
