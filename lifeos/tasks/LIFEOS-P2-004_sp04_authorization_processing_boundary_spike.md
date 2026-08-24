# LIFEOS-P2-004｜SP-04 六维授权判定与本地 / 云 / 第三方处理边界技术 Spike

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

- 任务 ID：LIFEOS-P2-004
- 任务名称：SP-04 六维授权判定与本地 / 云 / 第三方处理边界技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵、样例 JSON、决策表和脚本可放入证据目录，不计入正文
- 主责角色：AI 信任与安全负责人
- 协审角色：技术架构负责人、数据 / 领域模型负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 3 AI 权限与信任评审、Gate 2 数据与来源评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-001` 已通过 PM 验收并由用户确认采纳，证明本地可靠保存、版本追加、幂等、离线保存 / 待同步分离、墓碑 / 撤回恢复优先等最小存储语义成立。

`LIFEOS-P2-002` 已通过 PM 验收并由用户确认采纳，证明最小证据链包络成立：任一恢复包、AI 候选或用户确认对象都必须能追溯 Source、Artifact、Version、Derivation、Feedback、Authorization、AuditEntry 与 Link。

`LIFEOS-P2-003` 已通过 PM 验收并由用户确认采纳，项目级结论为 `Pass with Conditions`：Obsidian 只读来源身份在模拟 Vault 范围内具备最小可行性，但真实 Vault、跨平台、同步盘、大 Vault、运行时授权和清理仍未放行。

现在要验证 SP-04：

> LifeOS 能否在每次读取、索引、入队、执行、外发、模型调用、保存输出、跨 Project 展示 / 再派生前，真实执行“六维 Authorization + 强制政策包络 + 运行时状态”判定，而不是只在设置页展示一个 AI 总开关。

本任务允许在 `lifeos/spikes/SP-04/` 下创建最小本地验证代码、授权夹具、处理者 mock、模型网关 mock、样例 JSON、日志和证据包。不得调用真实模型、真实云、真实第三方 API，不得处理真实敏感数据，不得连接真实 Vault，不得冻结 Schema / API / 技术架构，不得进入正式 MVP 开发。

## 目标

本任务完成后，要回答：

1. 六维 Authorization（主体、范围、动作、目的、位置、时效）能否被编码为与数据库无关的决策契约，并在所有处理边界强制执行？
2. 强制政策包络（敏感级别、实际处理者、政策版本、子处理者 / 地区、训练 / 评估、保留 / 删除能力、来源许可、跨 Project 传播、数据最小化、凭据门槛）能否作为硬拒绝条件，而不是被用户宽泛同意覆盖？
3. 本地读取 / 索引、本地 AI 派生、LifeOS 云 mock、第三方模型 mock、训练 / 评估 mock 是否能通过同一授权网关判定？
4. 无授权、过期、撤回、范围扩大、目的不匹配、位置不匹配、处理者政策未知、训练默认开启、删除能力不足、保留超限、子处理者 / 地区未知时，是否全部 fail closed 且零发送？
5. 入队前、执行前、外发前、保存输出前和长任务关键阶段重检是否成立？中途撤回后竞态输出是否不可发布、不可索引、不可进入恢复包？
6. Project、文件夹、标签、双链、候选 Link、用户确认是否会错误扩权？
7. 多输入 Derivation 是否继承最严格约束？合法子集是否新建 Derivation 并披露缺口？无合法输入组合是否拒绝生成？
8. 凭据、私钥、恢复码等高风险内容是否作为额外硬拦截层；同时是否明确它不能替代授权判定？
9. 实际发送字段、处理者、政策版本、目的、位置和最小化清单是否可审计且不泄露正文、路径、提示词或向量？
10. 当前结果是否足以决定本地 AI、云处理、第三方模型处理在 V1 中保留、降级或移出？

## 范围

本任务必须覆盖：

- 决策契约：
  - `ALLOW / DENY / INDETERMINATE`；
  - 原因码；
  - 六维 Authorization；
  - 强制政策包络；
  - 运行时状态；
  - 授权版本、政策版本、输入版本、任务租约。
- 处理边界：
  - 本地读取；
  - 本地解析；
  - 本地 FTS / 索引；
  - 本地 AI / 算法派生 mock；
  - 入队；
  - 队列执行；
  - LifeOS 云 mock；
  - 第三方模型 mock；
  - 保存输出；
  - 跨 Project 展示；
  - 再派生；
  - 候选 Action / Decision / Link 写入。
- 数据与来源夹具：
  - LifeOS 用户原文；
  - Obsidian 外部原文；
  - 外部材料；
  - 公开内容；
  - 个人内容；
  - 客户秘密；
  - 凭据 / 私钥 / 恢复码类高风险内容；
  - 未知敏感级别内容；
  - Project A / Project B / 无 Project；
  - 排除 Source / 排除目录 / 排除 Artifact；
  - 已删除、已撤回处理、来源断开、来源不可达状态。
- 授权组合：
  - 仅本地搜索；
  - 本地恢复；
  - 本地 AI 派生；
  - LifeOS 云同步；
  - 指定第三方模型处理；
  - 训练 / 评估独立授权；
  - 过期授权；
  - 撤回授权；
  - 范围冲突；
  - 多输入授权交集；
  - 空交集。
- 政策包络：
  - 政策未知；
  - 政策版本变化；
  - 子处理者未知；
  - 地区未知或不符合；
  - 训练默认开启；
  - 保留超限；
  - 删除能力不足；
  - 来源禁止外发；
  - 处理者资格失败。
- 竞态与重检：
  - 入队后授权撤回；
  - 执行中授权撤回；
  - 外发前政策变化；
  - 保存输出前输入删除或墓碑出现；
  - 长任务分段重检；
  - 竞态输出隔离。
- 输出约束：
  - Derivation 继承输入约束；
  - 输出可见 Project / 目的 / 位置 / 接收方受限；
  - 非逐字推断、否定查询、候选 Link、排序信号、恢复包都按披露处理；
  - 合法子集必须生成新 Derivation 并披露缺口；
  - 无合法输入组合拒绝生成。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实 `.obsidian` 配置。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不实现正式模型网关、正式队列、正式同步、正式供应商接入或正式策略服务。
- 不做供应商正式选型。
- 不冻结数据库 Schema、API、事件流、权限 UI、桌面框架、技术栈或技术架构。
- 不实现 SP-05 撤回 / 删除物理清理。
- 不实现 SP-06 离线同步。
- 不实现 SP-07 搜索质量。
- 不实现 SP-08 正式导出迁移。
- 不实现 SP-09 容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-04/` 下创建和修改：
  - 授权验证脚本；
  - 合成夹具；
  - 决策表；
  - 处理者能力矩阵模板；
  - 模型网关 mock；
  - 发送字段清单；
  - 长任务撤回竞态报告；
  - 测试矩阵；
  - 样例 JSON；
  - 日志；
  - 环境说明；
  - 清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
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

## 角色检查点

主责角色必须重点回答：

- 六维 Authorization 与强制政策包络是否在运行时边界真实执行，而不是只做文档或 UI 展示？
- 任一 `DENY` 或 `INDETERMINATE` 是否都 fail closed？
- 用户确认是否被限制在六维范围内，不能覆盖处理者资格失败？
- 第三方 mock 收到的数据是否严格等于明确授权与最小化后的字段？
- 长任务撤回和政策变化竞态是否能阻断发布、索引和恢复包进入？

协审角色必须重点检查：

- 技术架构负责人：policy evaluator、网关、队列重检和缓存键是否能作为最小可实现候选，不冻结正式架构。
- 数据 / 领域模型负责人：Authorization、Derivation、Source、Artifact、Feedback、AuditEntry、Link 的引用和状态边界是否清楚。
- 产品架构负责人：授权边界是否服务个人可信外脑，不扩成企业 IAM 或管理后台。
- 体验设计负责人：拒绝原因、授权缺口、需重新授权、处理中撤回、供应商受限等状态是否能转成用户可理解体验。

## 核心问题

请重点回答：

1. 你采用了什么最小授权决策契约？为什么足以验证 SP-04，而不是冻结正式 Schema / API？
2. 六维 Authorization 如何判定？是否要求六维全部命中同一条当前有效授权？
3. 强制政策包络包含哪些字段？哪些情况属于硬拒绝？
4. 本地读取、索引、本地派生、云 mock、第三方 mock、保存输出、跨 Project 展示和再派生分别在哪些时点执行判定？
5. 无授权、过期、撤回、范围扩大、目的不匹配、位置不匹配、政策未知、训练默认开启、删除能力不足、保留超限时是否全部零发送？
6. 入队前 / 执行前 / 外发前 / 保存输出前 / 长任务关键阶段如何重检？撤回竞态如何处理？
7. 多输入 Derivation 如何继承最严格约束？合法子集和空交集如何处理？
8. Project、文件夹、标签、双链、候选 Link 和用户确认是否可能扩权？如何证明扩权为 0？
9. 凭据 / 私钥 / 恢复码检测如何作为额外硬拦截？它为什么不能替代授权？
10. 模型网关 mock 的发送字段、处理者、政策版本、目的和位置如何记录？日志如何避免泄露？
11. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
12. 若 SP-04 不是无条件 Pass，哪些 AI / 云 / 第三方能力应降级或移出 V1？
13. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 全部允许路径均能指向一条当时有效且六维匹配的授权。
- Authorization 与政策包络任一不满足或不确定，均为 `DENY`，并且实际发送字段为 0。
- 用户确认不能覆盖处理者资格失败、政策未知、训练默认开启、删除能力不足或来源禁止外发。
- Project 归属、文件夹、标签、双链、候选 Link 不得放宽 Source 排除、仅本地限制或目的限制。
- 搜索授权不得用于摘要、下一步建议、训练 / 评估或第三方处理。
- 本地授权不得用于云；云授权不得用于第三方；第三方 A 授权不得用于第三方 B。
- 多输入 Derivation 继承最严格约束；合法子集必须新建 Derivation 并披露缺口；空交集拒绝生成。
- 远端 mock 收到字段与明确授权范围完全一致；路径、无关元数据、排除内容、凭据和未知敏感级别内容外发为 0。
- 入队和执行前双重判定成立；外发前、保存输出前和长任务关键阶段重检成立。
- 长任务撤回后未完成阶段停止；撤回后完成的竞态结果不可发布、不可索引、不可进入恢复包。
- 政策版本变化、供应商变化、位置变化、目的变化或范围扩大均需新授权，不能沿用旧授权版本。
- 授权缓存若存在，缓存键必须包含授权版本、政策版本、目的、位置、输入约束摘要和时效；不得跨 Project / 主体复用。
- AuditEntry、日志和样例不得包含真实敏感原文、用户真实路径、真实 Vault 名、完整提示词、模型输出、向量或可还原真实数据。

## 建议测试矩阵

至少包含：

1. 本地读取 allow。
2. 本地 FTS / 索引 allow。
3. 本地 AI 派生 allow。
4. LifeOS 云 mock allow。
5. 指定第三方 mock allow。
6. 无授权 deny。
7. 过期授权 deny。
8. 撤回授权 deny。
9. 范围扩大 deny。
10. 目的不匹配 deny。
11. 位置不匹配 deny。
12. 主体 / 工作流不匹配 deny。
13. 政策未知 deny。
14. 政策版本变化触发重新评估。
15. 子处理者 / 地区未知 deny。
16. 训练 / 评估默认开启 deny。
17. 删除能力不足 deny。
18. 保留超限 deny。
19. 来源禁止外发 deny。
20. 凭据 / 私钥硬拦截。
21. Project 不扩权。
22. 标签 / 双链 / 文件夹不扩权。
23. 搜索授权不得复用为摘要。
24. 本地授权不得复用为云。
25. 云授权不得复用为第三方。
26. 第三方 A 授权不得复用为第三方 B。
27. 多输入最严格约束。
28. 合法子集新建 Derivation 并披露缺口。
29. 空交集拒绝生成。
30. 入队后撤回，执行前拒绝。
31. 执行中撤回，长任务停止。
32. 外发前政策变化，零发送。
33. 保存输出前输入删除 / 墓碑，输出隔离。
34. 授权缓存键包含必要版本与时效。
35. 非逐字推断 / 否定查询 / 候选 Link 泄漏为 0。
36. 日志与 AuditEntry 隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-04/`

证据包至少包括：

- `SP-04_report.md`
- `authorization_decision_contract.md`
- `authorization_decision_table.csv`
- `processor_policy_matrix.md`
- `gateway_send_manifest.json`
- `long_task_revocation_report.md`
- `constraint_inheritance_report.md`
- `test_matrix.csv`
- `results.json`
- `environment.md`
- `raw_logs/`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 授权决策契约与最小实现说明
3. 夹具、数据等级、处理者与政策包络说明
4. 六维 Authorization 判定结果
5. 强制政策包络与处理者资格判定结果
6. 本地 / 云 / 第三方处理边界验证
7. 入队、执行、外发、保存输出和长任务重检验证
8. Project / 外部结构 / 候选 Link 不扩权验证
9. 多输入 Derivation 约束继承、合法子集和空交集验证
10. 凭据硬拦截、最小化发送字段和日志隐私检查
11. 测试矩阵与最低验收断言结果
12. 最终结论：Pass / Pass with Conditions / Fail / Blocked
13. 对 V1 AI、云、第三方处理、后续 Spike 和技术架构候选的影响
14. 需要 PM / 用户确认的问题
15. 角色与关卡自检
16. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-04 的问题放入“后续任务建议”，不要扩写 SP-05 / SP-06 / SP-07 / SP-08 / SP-09。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-04/`。
- 证据包可复跑、可复核，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 3、Gate 2、Gate 4 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：全部运行时授权、政策包络、默认拒绝、处理边界、竞态重检、约束继承、最小化外发和隐私 P0 断言通过；证据可复跑。
- **Pass with Conditions**：P0 断言全部通过，仅性能、策略表达复杂度、非核心处理者能力模板或体验打包存在有界缺口，且已有明确降级和复验条件。
- **Fail**：任何运行边界绕过判定、任何不合格处理者收到数据、任何授权不匹配仍发送、任何 Project / Link 扩权、任何撤回后竞态输出发布、任何日志泄露真实敏感信息，或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实模型、真实云或真实第三方弥补 mock 不足。

## 降级路径

若 SP-04 无法无条件通过，应明确建议以下一种或多种降级：

- V1 仅保留本地读取 / 本地索引，不启用本地 AI 派生。
- V1 仅保留本地 AI 派生，不启用 LifeOS 云处理。
- V1 不启用第三方模型处理。
- 对敏感级别未知、客户秘密、凭据 / 私钥类内容默认排除 AI / 云 / 第三方路径。
- L3 候选继续降级为 L1 Derivation 展示，不写入候选 Action / Decision / Link。
- 云 / 第三方处理只允许不可逆最小化摘要或来源指针；若仍无法证明合规，则移出 V1。
- 授权 UI 可后续体验打包，但技术语义不得降级为 AI 总开关。

默认拒绝、六维判定、强制政策包络、用户确认不能覆盖处理者资格失败、凭据硬拦截、最小化外发、撤回后竞态阻断不可降级。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-04/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据、真实凭据、真实笔记或真实附件。
- 不调用真实模型、真实云服务或真实第三方 API。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-04 Pass 解释为真实云 / 第三方上线许可、供应商选型、技术架构冻结或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
