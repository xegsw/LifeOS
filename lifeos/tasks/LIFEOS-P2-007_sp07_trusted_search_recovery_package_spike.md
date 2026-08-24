# LIFEOS-P2-007｜SP-07 混合搜索、Project 恢复包与可信建议证据技术 Spike

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-007
- 任务名称：SP-07 混合搜索、Project 恢复包与可信建议证据技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、标注集、检索结果、恢复包样例、失败查询和脚本放入证据目录，不计入正文
- 主责角色：搜索 / AI 工程负责人
- 协审角色：技术架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、体验设计负责人
- 必须通过的评审关卡：Gate 4 技术可行性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审
- 状态：Ready

## 背景

`LIFEOS-P2-002` 已验证来源、版本、Derivation 与证据链最小映射成立；恢复包、AI 候选和用户确认对象必须能反查 Source、Artifact、Version、Authorization、Derivation、Feedback、AuditEntry 与 Link。

`LIFEOS-P2-004` 已验证六维 Authorization、强制政策包络、默认拒绝、运行时重检和最小化外发在合成夹具与 mock 处理者范围内成立。

`LIFEOS-P2-005` 已验证撤回 / 删除后活跃阻断零遗漏、两阶段清理状态、旧队列不复活和供应商限制披露在合成 mock 范围内成立。

`LIFEOS-P2-006` 已验证离线同步与状态一致性候选机制：原文版本不覆盖、AI 候选不替用户确认、Feedback 追加历史、tombstone / restriction 优先、队列发布前重检、字段级 LWW 不可用于用户权威对象。

现在要验证 SP-07：

> LifeOS 是否能在当前授权、证据状态、冲突状态和 Project 边界下，返回可信的搜索结果、Project 恢复包和 1-3 个候选下一步，而不是只生成流畅但不可核对的文本。

本任务允许在 `lifeos/spikes/SP-07/` 下创建最小本地验证代码、合成语料、标注查询集、检索基线、恢复包 JSON、deterministic AI stub、证据完整性报告、失败查询集和证据包。不得处理真实敏感数据，不得连接真实 Vault，不得调用真实模型、真实云、真实第三方 API 或付费资源，不得冻结 Schema / API / 搜索架构 / 技术架构，不得进入正式 MVP 开发。

## 目标

本任务完成后，要回答：

1. V1 是否可以采用 FTS + 元数据过滤 + 轻量重排作为可信搜索底线，而不是默认依赖向量搜索？
2. 在合成 Project / Source / Artifact / Decision / Action / Link / Feedback / Derivation 数据中，搜索是否能返回当前 Authorization 内的结果，权限泄漏是否为 0？
3. 检索结果是否能带回精确证据：Source、ArtifactVersion、Derivation、用户确认状态、证据时效、冲突状态和权限缺口？
4. Project 恢复包是否能组装“上次停点、近期变化、确认 Decision、开放 Action、未处理材料、关键冲突 / 缺口”，且每项都可追溯？
5. deterministic AI stub 生成的 1-3 个候选下一步是否全部带证据 ID / 版本 / 理由 / 置信边界 / 反馈入口，且不会伪装成用户确认？
6. 删除、撤回、断源、证据失效、离线冲突分支和旧队列输出是否不会进入搜索结果、恢复包或候选建议？
7. 向量 / 语义召回在合成标注集上是否相对 FTS + 元数据有明确增益；若无明显增益，V1 是否应后置向量能力？
8. 搜索失败、空结果、权限受限、来源不可达和证据冲突时，系统是否能给出用户可理解的降级状态？
9. 当前结果是否足以决定 V1 搜索 / 恢复包能力保留、降级、后置或阻断正式 MVP 开发？

## 范围

本任务必须覆盖：

- 合成语料：
  - 50-100 条内容单元，覆盖 3-5 个 Project；
  - Source、Artifact、ArtifactVersion、Derivation、Decision、Action、Link、Feedback、Authorization、AuditEntry；
  - 正常证据、冲突证据、来源不可达、权限排除、已撤回、已删除、已断源、证据失效、跨 Project 干扰；
  - 不包含真实敏感数据、真实路径、真实 Vault、真实 prompt 或真实模型输出。
- 标注查询集：
  - 精确找回；
  - 同义 / 语义找回；
  - 最近变化；
  - 已确认 Decision；
  - 未完成 Action；
  - 用户反馈后的候选；
  - 冲突证据；
  - 来源不可达；
  - 权限排除；
  - 跨 Project 干扰；
  - 删除 / 撤回后不应出现的内容。
- 检索方案：
  - SQLite FTS5 或等价本地关键词索引；
  - 元数据过滤；
  - Authorization / policy / tombstone / Source restriction 过滤；
  - 轻量重排；
  - deterministic 语义向量或 embedding stub，用于比较语义召回增益，不代表真实模型能力；
  - 可选模拟 pgvector exact / ANN 行为；如本地环境不支持真实 pgvector，必须明确“pgvector 未被生产级验证”。
- 恢复包：
  - Project 当前边界；
  - 上次停点 / 近期 Event；
  - 已确认 Decision；
  - 开放 Action；
  - 未处理材料；
  - 关键冲突 / Assertion / Link；
  - 来源、版本、证据状态、确认状态、权限缺口和反馈入口。
- 候选下一步：
  - 使用 deterministic AI stub 或规则生成器；
  - 只允许生成候选建议，不得自动确认 Action / Decision / Link；
  - 每条建议必须包含证据、理由、时效、冲突、权限缺口和反馈入口。
- 失败与降级：
  - 空结果；
  - 权限受限；
  - 来源不可达；
  - 证据冲突；
  - 唯一证据失效；
  - 删除 / 撤回后被排除；
  - 向量无明显增益；
  - 延迟或恢复包组装超阈值。

## 非范围

本任务暂时不要做：

- 不开发正式搜索服务。
- 不开发正式产品 UI。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实 `.obsidian` 配置。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不实现正式向量数据库、独立搜索集群、生产 pgvector、生产 ANN 索引或在线重排服务。
- 不承诺生产搜索 SLA、真实召回率、真实模型效果或真实容量性能。
- 不冻结搜索 Schema、API、索引策略、排序策略、向量维度、分块策略、模型供应商、技术栈或技术架构。
- 不实现 SP-08 正式导出迁移。
- 不实现 SP-09 100 万内容单元容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-07/` 下创建和修改：
  - 本地验证脚本；
  - 合成语料和标注查询集；
  - FTS / 元数据 / 权限过滤 / 轻量重排候选实现；
  - deterministic semantic / vector stub；
  - 恢复包 JSON 样例；
  - 候选下一步样例；
  - 证据完整性报告；
  - 失败查询集；
  - 检索对比结果；
  - 结果 JSON；
  - 日志；
  - `README.md` 或 `MANIFEST.md`；
  - 环境说明与清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`
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

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-004_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/spikes/SP-03/`
- `lifeos/spikes/SP-04/`
- `lifeos/spikes/SP-05/`
- `lifeos/spikes/SP-06/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现任务卡与产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策上下文，只读取 D-0039、D-0045、D-0050、D-0102、D-0103、D-0104 或最近 5-10 条相关决策。
- 若上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- FTS + 元数据 + 权限过滤 + 轻量重排是否足以作为 V1 可信搜索底线？
- 语义 / 向量检索是否在标注集上有明确增益；若无，是否应后置？
- Project 恢复包是否能从证据链、确认状态、冲突状态、Authorization 和 tombstone 状态中组装，而不是只由 AI 编写？
- 性能阈值、召回阈值和证据完整性是否真实进入验证路径？
- 是否清楚写明合成验证边界，不外推为生产搜索 SLA 或模型能力？

协审角色必须重点检查：

- 技术架构负责人：搜索候选机制是否避免引入独立搜索集群、重型向量平台或不可替换供应商绑定。
- 数据 / 领域模型负责人：Source、ArtifactVersion、Derivation、Decision、Action、Link、Feedback、Authorization、AuditEntry 是否能被结果追溯。
- AI 信任与安全负责人：撤回 / 删除 / 断源 / 权限受限 / 证据失效是否不会进入搜索、恢复包或候选建议。
- 体验设计负责人：空结果、受限结果、来源不可达、证据冲突、待复核和候选建议是否有用户能理解的状态语言。

## 核心问题

请重点回答：

1. 你采用了什么最小搜索与恢复包状态模型？为什么足以验证 SP-07，而不是冻结正式 Schema / API？
2. 查询集、标注答案、内容单元、Project、Authorization 和证据状态如何构造？
3. FTS、元数据过滤、权限过滤、轻量重排和 deterministic 语义向量分别如何参与结果排序？
4. Recall@k、nDCG、首条有效结果、空结果原因、权限泄漏、证据完整性如何计算？
5. 删除、撤回、断源、证据失效、冲突分支、旧队列输出如何被排除或降级？
6. Project 恢复包包含哪些字段？每个字段如何追溯到证据、版本、用户确认状态和权限状态？
7. 候选下一步如何生成？如何保证它仍是 AI 推断 / 建议，而不是用户确认 Action？
8. 向量或语义召回是否明显优于 FTS + 元数据？若没有，V1 如何降级？
9. 哪些查询或恢复包场景失败？失败后对 V1 范围、搜索体验和后续 Spike 有什么影响？
10. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
11. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 权限泄漏为 0：无当前 Authorization 的内容不得进入结果、恢复包、候选建议或日志。
- 删除 / 撤回 / 断源后，受影响内容不得被搜索、恢复包或候选建议活跃使用。
- 冲突分支、证据不可用、来源不可达和唯一证据失效必须显示降级或待复核，不生成看似完整的恢复叙述。
- 每条重点搜索结果至少能返回 Source、ArtifactVersion、Derivation / Link、确认状态、生成时间、证据状态和权限状态。
- Project 恢复包中每个 Decision / Action / Next Step 候选都必须有 1-3 条可打开证据或明确缺口。
- AI / deterministic stub 生成的下一步必须标记为候选建议，不得自动形成用户确认 Action / Decision / Link。
- 跨 Project 候选不得放宽 Source 排除、授权限制或用户确认条件。
- 字段级 LWW、旧队列输出或旧恢复包不得覆盖当前用户权威状态。
- 标注查询 Recall@20、关键查询 Recall@10、证据完整性、空结果解释和延迟必须有机器可读结果。
- 日志和 AuditEntry 不包含真实敏感原文、真实路径、真实 Vault 名、完整 prompt / 输出、向量或可还原真实数据。

## 建议测试矩阵

至少包含：

1. 精确原文关键词找回。
2. 同义 / 语义查询找回。
3. 最近变化查询。
4. 已确认 Decision 查询。
5. 未完成 Action 查询。
6. 用户拒绝后的 AI 候选不进入下一步。
7. 用户编辑后接受的候选进入恢复包但保留证据。
8. 删除内容后搜索不返回。
9. 撤回处理后恢复包不使用相关 Derivation。
10. Source 断开后旧读取结果不进入候选建议。
11. 唯一证据失效后已确认对象显示待复核。
12. 冲突原文双版本均保留，但恢复包标注冲突。
13. 跨 Project 相似内容不串扰。
14. 仅本地搜索授权不得被摘要 / 建议用途复用。
15. 空结果给出“无匹配 / 权限受限 / 来源不可达 / 证据失效”原因。
16. FTS-only、语义-only、混合 + 重排对比。
17. 向量无增益或低增益时的降级样例。
18. 恢复包 JSON 证据完整性检查。
19. 候选下一步 1-3 条的证据和反馈入口检查。
20. 日志隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-07/`

证据包至少包括：

- `README.md` 或 `MANIFEST.md`
- `SP-07_report.md`
- `run_spike.py` 或等价本地验证脚本
- `fixtures.md`
- `query_set.json`
- `golden_labels.json`
- `retrieval_results.json`
- `test_matrix.csv`
- `recovery_package_samples.json`
- `evidence_integrity_report.md`
- `permission_filter_report.md`
- `strategy_comparison.md`
- `failed_queries.md`
- `raw_logs/`
- `environment.md`
- `cleanup.md`

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 最小搜索 / 恢复包模型与非冻结说明
3. 合成语料、查询集和标注答案说明
4. FTS / 元数据 / 权限过滤 / 语义 stub / 轻量重排方案
5. 权限过滤、撤回删除、断源、证据失效和冲突降级验证
6. Project 恢复包结构与证据链完整性验证
7. 候选下一步生成与 AI 身份边界验证
8. 召回、排序、空结果、延迟和失败查询分析
9. FTS-only / 语义-only / 混合方案对比
10. 向量能力是否保留、后置或降级的建议
11. 最终结论：Pass / Pass with Conditions / Fail / Blocked
12. 对 V1 搜索、恢复包、AI 建议、权限体验、SP-08 / SP-09 和技术架构候选的影响
13. 需要 PM / 用户确认的问题
14. 角色与关卡自检
15. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-07 的问题放入“后续任务建议”，不要扩写 SP-08 / SP-09 或技术架构冻结。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-07/`，且包含 `README.md` 或 `MANIFEST.md`。
- 证据包可复跑、可复核，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 4、Gate 2、Gate 3 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：权限泄漏为 0；删除 / 撤回 / 断源不被活跃使用；证据完整性 100% 通过；关键查询满足任务阈值；恢复包和候选建议均可追溯；证据可复跑。
- **Pass with Conditions**：P0 安全断言全部通过，但召回、语义增益、延迟、冲突体验、向量候选或非核心查询存在有界缺口，并已有明确降级与复验条件。
- **Fail**：任何权限泄漏；任何删除 / 撤回 / 断源内容进入活跃结果；任何候选建议伪装成用户确认；任何恢复包缺少关键证据却生成完整叙述；任何日志泄露真实敏感信息；或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实云、真实模型、真实 Vault 或真实敏感数据弥补 mock 不足。

## 降级路径

若 SP-07 无法无条件通过，应明确建议以下一种或多种降级：

- V1 采用 FTS + 元数据优先，向量搜索后置。
- V1 只支持当前 Project 内可信恢复，不做跨 Project 语义推荐。
- 候选下一步只显示“证据不足 / 待复核”，不生成完整建议。
- 权限受限、来源不可达、证据失效和冲突分支默认降级为可解释空结果或待用户处理。
- 首页 / 今日页恢复包只展示用户确认 Decision、开放 Action 和最近原文，不展示 AI 推断排序。
- 搜索结果不进入 AI 建议，直到授权过滤和证据链验证通过。

不可降级底线：权限过滤不能泄漏；删除 / 撤回 / 断源不能被活跃使用；AI 候选不能替用户确认；证据缺口不能伪装完整；用户原文和确认历史不能被旧结果覆盖；审计不可还原真实内容。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-07/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API、搜索策略或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据、真实凭据、真实笔记或真实附件。
- 不调用真实模型、真实云服务或真实第三方 API。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-07 Pass 解释为正式搜索 SLA、正式向量能力、真实模型效果、技术架构冻结或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
