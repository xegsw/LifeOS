# LIFEOS-P2-005｜SP-05 撤回 / 删除传播、依赖发现与清理验证技术 Spike

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

- 任务 ID：LIFEOS-P2-005
- 任务名称：SP-05 撤回 / 删除传播、依赖发现与清理验证技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵、样例 JSON、状态机、清理证明和脚本可放入证据目录，不计入正文
- 主责角色：AI 信任与安全负责人
- 协审角色：技术架构负责人、数据 / 领域模型负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 3 AI 权限与信任评审、Gate 2 数据与来源评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-001` 已通过 PM 验收并由用户确认采纳，证明本地可靠保存、版本追加、幂等、离线保存 / 待同步分离、墓碑 / 撤回恢复优先等最小存储语义成立。

`LIFEOS-P2-002` 已通过 PM 验收并由用户确认采纳，证明最小证据链包络成立：恢复包、AI 候选或用户确认对象都必须能追溯 Source、Artifact、Version、Derivation、Feedback、Authorization、AuditEntry 与 Link。

`LIFEOS-P2-003` 已通过 PM 验收并由用户确认采纳，项目级结论为 `Pass with Conditions`：Obsidian 只读来源身份在模拟 Vault 范围内具备最小可行性，但真实 Vault、跨平台、同步盘、大 Vault、正式解析库、运行时授权和清理仍未放行。

`LIFEOS-P2-004` 已通过 PM 验收并由用户确认采纳，结论为 `Pass`：六维 Authorization、强制政策包络、默认拒绝、运行时重检、最小化外发、长任务撤回隔离和审计隐私在合成夹具与 mock 处理者范围内成立。

现在要验证 SP-05：

> 当用户撤回处理许可、断开来源、删除内容或撤回反馈后，LifeOS 是否能立即阻断所有活跃使用，并对派生物、索引、缓存、队列、备份、离线副本和第三方 mock 的物理清理给出可追踪、可重试、可诚实披露的状态。

本任务允许在 `lifeos/spikes/SP-05/` 下创建最小本地验证代码、合成夹具、传播状态机、依赖扫描、清理 outbox、mock 第三方删除接口、故障注入日志和证据包。不得处理真实敏感数据，不得连接真实 Vault，不得调用真实模型、真实云或真实第三方 API，不得冻结 Schema / API / 技术架构，不得进入正式 MVP 开发。

## 目标

本任务完成后，要回答：

1. 四类命令 `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 的影响集合是否能被明确计算，且不会互相冒充？
2. 撤回 / 删除事务提交后，受影响数据是否能立即退出活跃读取、FTS / 向量查询、恢复包、今日建议、队列取任务和新模型调用？
3. 原文副本、ArtifactVersion、分块、FTS posting、向量、摘要、候选 Action / Decision / Link、缓存、prompt 副本、队列 payload、对象文件、备份、离线副本、第三方 mock 调用记录是否都能被依赖发现覆盖？
4. “活跃阻断”和“物理清理”是否被实现为两阶段语义，并分别给出准确状态，而不是把 `active_blocked` 误报成“全部删除完成”？
5. 清理任务在进程 kill、重复消息、乱序执行、租约过期、网络失败和第三方删除失败后是否幂等、可恢复、可重试、可进入死信，且死信不解除活跃阻断？
6. 从备份恢复、旧导入包重导入、来源重连、离线副本回放或旧队列重试后，删除墓碑 / 撤回状态是否优先重放，目标数据是否不复活？
7. 第三方 mock 无法即时或完全删除时，系统是否记录 `vendor_limited` / `physical_cleanup_failed`，并且不误报“完全删除”？
8. 用户确认对象、历史 Feedback 和外部来源原件在四类命令下如何保留、失效、待复核或删除？是否避免误删用户历史和误留受限证据？
9. 审计、日志和清理证明是否足以解释发生了什么，同时不能还原正文、完整路径、提示词、向量或敏感内容？
10. 当前结果是否足以决定删除 / 撤回能力在 V1 中保留、降级或阻断正式 MVP 开发？

## 范围

本任务必须覆盖：

- 四类命令：
  - `revoke_processing`：撤回指定主体 / 范围 / 动作 / 目的 / 位置 / 时效下的处理许可；
  - `disconnect_source`：断开 Source 的继续读取、监听或同步；
  - `delete_content`：删除 LifeOS 内指定 Artifact / ArtifactVersion / Source 副本及其可控派生；
  - `retract_feedback`：撤回用户先前确认、拒绝、纠正、完成、延期等 Feedback 的当前效力。
- 依赖类型登记：
  - 用户原文；
  - 外部来源原文副本 / 指针；
  - ArtifactVersion；
  - 内容分块；
  - FTS posting / 搜索索引；
  - 向量或向量 mock；
  - 摘要 / 恢复包片段；
  - AI 候选 Action / Decision / Link；
  - 用户确认对象与历史 Feedback；
  - 重要 Link；
  - 缓存；
  - prompt / 模型输入副本；
  - 队列 payload；
  - 对象文件 / 附件指针；
  - 备份包；
  - 离线副本 / 待同步 outbox；
  - 第三方 mock 输入 / 输出 / 删除状态；
  - AuditEntry / 清理证明。
- 影响集合生成：
  - 单个 Artifact 删除；
  - 单个 ArtifactVersion 删除；
  - Source 删除；
  - Source 断开；
  - 目录排除 / 撤权；
  - Project 范围撤回处理许可；
  - 特定目的撤回处理许可；
  - 特定位置 / 处理者撤回许可；
  - 输入版本更新导致派生失效；
  - 用户纠正或撤回 Feedback；
  - 跨 Project 候选 Link 或恢复包受限。
- 两阶段执行：
  - 阶段 A：同一事务内写入墓碑 / 授权版本变化 / 对象状态变化，使目标不可被活跃消费，并写入清理 outbox；
  - 阶段 B：异步清理或重建 FTS、向量、缓存、队列、派生、备份、离线副本和第三方 mock 状态，带租约、幂等键、重试、死信和验证。
- 活跃阻断路径：
  - 本地读取；
  - FTS 查询；
  - 向量 / 近邻查询 mock；
  - Project 恢复包；
  - 首页 / 今日建议；
  - AI 候选生成；
  - 队列取任务；
  - 模型网关 mock 发送；
  - 跨 Project 展示；
  - 再派生；
  - 导出 / 重导入前置过滤。
- 故障与竞态：
  - 清理前 kill；
  - 清理中 kill；
  - 清理完成写状态前 kill；
  - 重复 outbox 消息；
  - 乱序清理；
  - 租约过期；
  - 网络失败；
  - 第三方 mock 删除失败 / 延迟 / 不支持；
  - 备份恢复；
  - 旧导入包重导入；
  - 来源重连；
  - 离线副本回放；
  - 旧队列重试。
- 用户可见状态语义：
  - `accepted`；
  - `active_blocked`；
  - `physical_cleanup_pending`；
  - `physical_cleanup_failed`；
  - `vendor_limited`；
  - `physically_cleaned`；
  - `completed_no_physical_cleanup_required`；
  - `review_required`。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实 `.obsidian` 配置。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不实现正式删除 UI、正式权限 UI、正式供应商删除接口、正式同步、正式导出迁移或正式搜索质量排序。
- 不承诺删除 SLA、备份保留窗口、第三方供应商能力或法律合规结论。
- 不冻结数据库 Schema、API、事件流、队列实现、搜索实现、桌面框架、技术栈或技术架构。
- 不实现 SP-06 离线同步一致性。
- 不实现 SP-07 搜索质量。
- 不实现 SP-08 正式导出迁移。
- 不实现 SP-09 容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-05/` 下创建和修改：
  - 本地验证脚本；
  - 合成夹具；
  - 依赖类型登记；
  - 影响集合样例；
  - 传播状态机；
  - 清理 outbox / tombstone mock；
  - FTS / 向量 / 缓存 / 队列 / 备份 / 离线副本 mock；
  - 第三方删除能力 mock；
  - 故障注入报告；
  - 遗漏扫描报告；
  - 备份恢复 / 重导入 / 来源重连报告；
  - 第三方限制矩阵；
  - 清理证明样例；
  - 测试矩阵；
  - 结果 JSON；
  - 日志；
  - 环境说明；
  - 清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
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

## 角色检查点

主责角色必须重点回答：

- 撤回 / 删除是否真正改变运行时可消费状态，而不是只改变设置页或审计记录？
- 任一活跃路径是否都在事务提交后立即被阻断，漏阻断是否为 0？
- 四类命令是否语义分离，避免“撤回处理”冒充“删除内容”，或“断开来源”误删用户保留副本？
- 物理清理失败、第三方受限、备份窗口和离线副本是否被诚实披露，而不是被隐藏成成功？
- 审计和清理证明是否能解释事故，同时不能还原内容或形成新的隐私数据库？

协审角色必须重点检查：

- 技术架构负责人：tombstone、outbox、依赖索引、幂等清理状态机、租约、死信和恢复流程是否能作为最小实现候选，不冻结正式架构。
- 数据 / 领域模型负责人：Source、Artifact、ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry、Link、墓碑和清理状态边界是否清楚。
- 产品架构负责人：删除 / 撤回语义是否服务个人可信外脑，不扩成企业合规后台或 IT 运维控制台。
- 体验设计负责人：`active_blocked`、`cleanup_pending`、`failed`、`vendor_limited`、`review_required` 等状态是否能转成用户能懂的产品文案。

## 核心问题

请重点回答：

1. 你采用了什么最小撤回 / 删除传播模型？为什么足以验证 SP-05，而不是冻结正式 Schema / API？
2. 四类命令分别影响哪些对象、副本、派生、索引、缓存、队列、备份、第三方 mock 与用户确认状态？
3. 依赖类型登记如何设计？哪些依赖必须显式登记，哪些可以重建扫描，哪些必须默认保守阻断？
4. 事务提交后如何立即实现活跃阻断？哪些读取、搜索、恢复包、今日建议、队列和模型调用路径被验证？
5. 异步物理清理状态机如何设计？如何处理 pending、failed、vendor_limited、physically_cleaned 和 no_cleanup_required？
6. kill、重复消息、乱序执行、租约过期、网络失败、第三方删除失败下是否幂等、可恢复、可重试？
7. FTS、向量 mock、缓存、队列 payload、prompt 副本和可还原摘要是否被清理或不可逆处理？如何证明不再命中？
8. 备份恢复、旧导入包重导入、来源重连、离线副本回放和旧队列重试是否会复活被删 / 被撤回数据？
9. 用户确认对象、历史 Feedback 和证据失效之间如何处理？是否保留用户历史但退出自动建议依据？
10. 第三方 mock 删除能力不足时如何记录和披露？它对 V1 云 / 第三方处理边界有什么影响？
11. 日志、AuditEntry、清理证明和遗漏扫描如何避免泄露正文、完整路径、提示词、向量或敏感存在性？
12. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
13. 若 SP-05 不是无条件 Pass，哪些能力必须降级、后置或阻断正式 MVP 开发？
14. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 四类命令不可互相冒充；每类命令的对象后果、保留后果和用户可见状态不同。
- 撤回 / 删除事务提交后，活跃读取、FTS / 向量查询、恢复包、今日建议、队列取任务、新模型调用和再派生立即无法使用受影响数据；测试集漏阻断为 0。
- 任一活跃阻断失败均为 P0 失败，不能以“物理清理稍后完成”绕过。
- 依赖集合覆盖用户原文、外部来源副本 / 指针、ArtifactVersion、分块、FTS、向量 mock、摘要、恢复包、AI 候选、重要 Link、缓存、prompt 副本、队列 payload、备份、离线副本、第三方 mock 和 AuditEntry。
- 清理任务在 kill、重复、乱序、租约过期和故障恢复后收敛；死信可见且不解除活跃阻断。
- FTS、向量 mock、缓存、队列 payload、prompt 副本和可还原摘要不再命中或携带目标内容。
- 从任一测试备份恢复后，在开放正常查询前必须重放墓碑 / 撤回状态；目标数据复活数为 0。
- 旧导入包、来源重连、离线副本回放和旧队列重试不能复活删除内容或重新入模。
- `retract_feedback` 只撤回 Feedback 当前效力，不删除原文或伪装外部效果；依赖派生按需失效或重建。
- 用户确认对象在唯一证据被删除 / 失效时保留历史，但标记 `evidence_unavailable` / `review_required`，不得继续作为自动建议依据。
- 第三方 mock 无法即时 / 完全删除时状态为 `vendor_limited` 或 `physical_cleanup_failed`，不得显示“完全删除”。
- 审计和清理证明只保留不可还原引用、动作类别、状态、结果和原因码；不得包含正文、完整路径、提示词、模型输出、向量或可还原真实数据。

## 建议测试矩阵

至少包含：

1. `revoke_processing` 单 Artifact 本地搜索阻断。
2. `revoke_processing` Project 范围 AI 候选阻断。
3. `revoke_processing` 第三方 mock 后续调用阻断。
4. `disconnect_source` 停止继续读取 / 监听。
5. `disconnect_source` 既有副本按保留许可进入 pending / invalid。
6. `delete_content` 单 Artifact 删除。
7. `delete_content` 单 ArtifactVersion 删除。
8. `delete_content` Source 级删除。
9. `retract_feedback` 撤回确认。
10. `retract_feedback` 撤回拒绝 / 纠正 / 完成 / 延期。
11. 输入版本更新导致 Derivation stale / invalid。
12. 目录排除导致依赖集合生成。
13. 跨 Project 候选 Link 受限。
14. 多输入 Derivation 合法子集重建。
15. 多输入无合法子集拒绝。
16. FTS 查询不再命中目标 token。
17. 向量 mock ID / 邻近查询不再返回目标。
18. 缓存不携带目标内容。
19. prompt / 模型输入副本被删除或不可逆处理。
20. 队列 payload 清理或取任务前拒绝。
21. 清理前 kill 后恢复。
22. 清理中 kill 后恢复。
23. 清理完成写状态前 kill 后恢复。
24. 重复 outbox 消息幂等。
25. 乱序清理幂等。
26. 租约过期后重新领取不重复破坏。
27. 网络失败重试。
28. 第三方 mock 删除成功。
29. 第三方 mock 删除延迟。
30. 第三方 mock 不支持删除。
31. 死信可见且活跃阻断仍成立。
32. 备份恢复后墓碑优先。
33. 旧导入包重导入不复活。
34. 来源重连不复活已删内容。
35. 离线副本回放不复活。
36. 旧队列重试不重新入模。
37. 用户确认对象证据失效后进入 review_required。
38. 审计 / 日志 / 清理证明隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-05/`

证据包至少包括：

- `SP-05_report.md`
- `dependency_registry.md`
- `impact_set_samples.json`
- `propagation_state_machine.md`
- `cleanup_outbox_report.md`
- `active_blocking_scan_report.md`
- `cleanup_fault_injection_report.md`
- `backup_restore_replay_report.md`
- `reimport_reconnect_offline_replay_report.md`
- `third_party_cleanup_matrix.md`
- `cleanup_proof_samples.json`
- `test_matrix.csv`
- `results.json`
- `environment.md`
- `raw_logs/`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 最小撤回 / 删除传播模型与非冻结说明
3. 四类命令效果矩阵
4. 依赖类型登记与影响集合生成
5. 两阶段活跃阻断与物理清理状态机
6. 活跃读取 / 搜索 / 恢复包 / 今日建议 / 队列 / 模型调用阻断验证
7. FTS / 向量 mock / 缓存 / prompt 副本 / 队列 payload 清理验证
8. 故障注入、幂等、租约、重试和死信验证
9. 备份恢复、旧导入包、来源重连、离线副本和旧队列不复活验证
10. 第三方 mock 删除成功、延迟、不支持与供应商受限状态验证
11. 用户确认对象、Feedback 撤回、证据失效与 review_required 处理
12. 审计、日志、清理证明与隐私扫描
13. 测试矩阵与最低验收断言结果
14. 最终结论：Pass / Pass with Conditions / Fail / Blocked
15. 对 V1、删除 / 撤回体验、云 / 第三方处理、后续 Spike 和技术架构候选的影响
16. 需要 PM / 用户确认的问题
17. 角色与关卡自检
18. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-05 的问题放入“后续任务建议”，不要扩写 SP-06 / SP-07 / SP-08 / SP-09。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-05/`。
- 证据包可复跑、可复核，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 3、Gate 2、Gate 4 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：全部四命令分离、依赖发现、活跃阻断、物理清理状态机、故障恢复、不复活、第三方受限披露和隐私 P0 断言通过；证据可复跑。
- **Pass with Conditions**：P0 活跃阻断断言全部通过，仅物理清理窗口、非核心副本类型、第三方 mock 删除延迟、性能预算或用户状态文案存在有界缺口，且已有明确降级和复验条件。
- **Fail**：任何活跃路径漏阻断、任何墓碑 / 撤回状态被备份恢复或离线回放复活、任何清理失败解除活跃阻断、任何四命令语义混淆、任何可还原敏感内容进入审计 / 日志 / 清理证明，或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实模型、真实云、真实第三方或真实 Vault 弥补 mock 不足。

## 降级路径

若 SP-05 无法无条件通过，应明确建议以下一种或多种降级：

- V1 暂不启用云 / 第三方模型处理，只保留本地读取、索引和本地可重建派生。
- V1 暂不启用向量搜索，仅保留 FTS + 元数据 + 权限过滤。
- V1 暂不保留可还原 prompt 副本或模型输入缓存。
- V1 对 Obsidian 只保留来源指针 / 手工导入，不做持续监听或长期副本。
- V1 不支持 Source 级批量删除，只支持单 Artifact / 单 Project 小范围删除，直到容量和批量清理通过后再开放。
- 第三方处理保持关闭，直到真实供应商删除能力和保留边界通过专项验证。
- 候选 Action / Decision / Link 继续降级为 L1 Derivation 展示，不进入持久候选业务对象。

默认拒绝、四命令分离、活跃阻断零遗漏、墓碑优先、不复活、审计不可还原、供应商受限诚实披露不可降级。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-05/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据、真实凭据、真实笔记或真实附件。
- 不调用真实模型、真实云服务或真实第三方 API。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-05 Pass 解释为正式删除 SLA、真实第三方删除承诺、技术架构冻结或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
