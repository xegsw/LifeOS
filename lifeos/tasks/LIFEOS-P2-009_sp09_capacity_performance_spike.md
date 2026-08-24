# LIFEOS-P2-009｜SP-09 100 万内容单元 / 300 万分块容量与性能技术 Spike

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-009
- 任务名称：SP-09 100 万内容单元 / 300 万分块容量与性能技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；基准日志、数据生成器、查询计划、资源数据、失败样例和原始结果放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS 是个人长期使用的终身外脑，V1 不能只在小样本下“看起来可用”。如果底层保存、索引、检索、删除、备份、恢复和派生重建在长期规模下不可控，后续正式 MVP 开发会把技术债直接写进产品地基。

前置 Spike 已完成：

- SP-01 验证本地可靠落盘、离线捕获、备份恢复的最小可靠性语义。
- SP-03 验证来源、版本、Derivation 与证据链最小映射。
- SP-05 验证撤回 / 删除传播、依赖发现、活跃阻断与清理状态。
- SP-06 验证离线同步与 Action / Decision / Link / Feedback 状态一致性。
- SP-07 验证 FTS + 元数据 + 当前授权 / 状态过滤 + 轻量重排、Project 恢复包和可信建议证据；本轮未证明向量默认依赖价值。
- SP-08 验证可迁移导出、恢复与有限重导入候选机制。

现在要执行最后一项阻断型技术 Spike：在合成数据下验证 100 万内容单元 / 300 万分块规模的容量、性能、成本和架构触发阈值。

本任务不是正式开发，不冻结技术架构，不要求连接真实云服务或真实数据库账号。若本机环境不足以完成 100 万 / 300 万全量实测，必须记录真实原因，完成可运行的较小规模阶梯测试与严谨外推，但不得把外推伪装成全量通过。

## 目标

本任务完成后，要回答：

1. 在重度个人使用基线下，LifeOS 的本地权威原文、元数据、FTS、派生索引、搜索、删除、备份和恢复成本是否可控？
2. 100 万内容单元 / 300 万分块是否能在候选最低环境约束内被至少一种架构候选装载或合理降级？
3. V1 是否可以优先采用 SQLite + FTS5 / 元数据过滤 / 轻量重排作为本地与早期搜索地基？
4. 向量是否应成为 V1 默认硬依赖，还是后置为高价值内容、低维、半精度、云端获准索引或后续能力？
5. 删除 / 撤回 / 断源 / 旧 generation / 权限过滤在规模化查询和维护任务下是否仍能保持安全底线？
6. 备份、恢复、墓碑重放、导出校验和索引重建在长期规模下是否有可接受的时间、空间和失败状态？
7. 是否出现必须缩小 V1 范围、调整数据保留策略、改变索引策略或延后某些能力的证据？
8. 当前结果是否足以作为技术架构候选评审和 Stage 2 收口输入？

## 范围

本任务必须覆盖：

- 合成规模数据：
  - 至少 1 万、10 万两档可复跑数据；
  - 尽力完成 100 万内容单元 / 300 万分块全量或分阶段实测；
  - 保持 Project、时间、来源、授权、版本、Link、删除 / 撤回 / 断源分布，避免纯随机无过滤数据；
  - 不使用真实用户数据、真实 Vault、真实 Project 名、真实路径或真实敏感内容。
- 本地候选验证：
  - SQLite / FTS5 候选；
  - 捕获写入、批量导入、FTS 初建 / 增量、checkpoint、integrity check；
  - 删除 / secure-delete 或可解释替代策略；
  - 备份、恢复、墓碑重放和索引重建；
  - 权限 / Project / 状态过滤下的关键词与元数据查询。
- 服务端候选模拟或本地替代验证：
  - 允许用本地脚本、SQLite 扩展模型或文件化模拟估算 PostgreSQL / pgvector 成本；
  - 如环境具备且无需外部付费账号，可使用本地容器或本地服务验证 PostgreSQL / FTS / pgvector 候选；
  - 如无法验证 PostgreSQL / pgvector，必须记录缺口和后续验证条件。
- 向量与分块成本：
  - 至少比较 384 / 768 / 1536 维确定性合成向量的原始存储估算；
  - 尽力比较不同覆盖率、低维、半精度或非 ANN 方案；
  - 不调用真实 embedding 模型或付费 API。
- 查询与恢复包：
  - 复用 SP-07 的查询思想，构造可复跑查询集；
  - 测关键词 / 元数据查询、权限过滤、Project 恢复包数据组装；
  - 记录 p50 / p95 / p99、资源占用和失败样例。
- 删除 / 撤回 / 清理：
  - 复用 SP-05 的删除与撤回语义；
  - 测单条、单 Source、1% 数据规模的活跃阻断、索引失效、清理推进、ETA / 失败状态；
  - 不以牺牲墓碑优先、权限过滤或活跃阻断换性能。
- 证据包：
  - 数据生成器；
  - 基准脚本；
  - 测试矩阵；
  - 原始结果；
  - 环境说明；
  - 资源曲线或资源摘要；
  - 失败样例；
  - `README.md` 或 `MANIFEST.md` 作为证据入口。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能、UI、服务端、同步服务或搜索服务。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实路径。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不部署生产环境，不购买服务器，不创建外部数据库实例。
- 不冻结 SQLite、PostgreSQL、pgvector、向量维度、分块策略、Schema、API、队列、备份方案、导出格式或技术架构。
- 不为了达成性能指标而取消权限过滤、墓碑优先、删除 / 撤回不复活、来源追踪或用户原文保护。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-09/` 下创建和修改：
  - 合成数据生成器；
  - 基准脚本；
  - 查询集；
  - 测试矩阵；
  - 资源 / 性能结果；
  - 失败样例；
  - 证据入口 `README.md` 或 `MANIFEST.md`；
  - 环境说明与清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确任务目录或系统临时目录；不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话：

- 修改 `PROJECT_CONTEXT.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md` 等 PM 文件。
- 修改现有非 Spike 项目代码或无关文件。
- 删除、覆盖或移动用户真实数据。
- 使用破坏性命令清理宽泛目录。
- 连接真实 Vault、真实用户文件、真实凭据、真实云或真实第三方服务。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-007_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-008_pm_review.md`
- `lifeos/spikes/SP-01/`
- `lifeos/spikes/SP-05/`
- `lifeos/spikes/SP-07/`
- `lifeos/spikes/SP-08/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现任务卡与产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策上下文，只读取 D-0035、D-0039、D-0102、D-0104、D-0106、D-0107 或最近 5-10 条相关决策。
- 若上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 当前候选架构在 1 万 / 10 万 / 100 万内容单元下的容量、性能、资源曲线是否清楚？
- SQLite / FTS5、PostgreSQL / FTS、pgvector / 向量候选是否有可比较证据，而不是偏好判断？
- 哪些指标是实测，哪些是估算，哪些因环境不足只能列为后续验证？
- 何时应垂直扩容、降低向量覆盖、调整分块、改用云端获准索引或评估专用组件？
- 哪些结论可以进入技术架构候选评审，哪些不能外推？

协审角色必须重点检查：

- 数据 / 领域模型负责人：合成数据是否保留 Project、Source、ArtifactVersion、Derivation、Link、Feedback、Authorization、AuditEntry、删除 / 撤回 / 断源分布。
- AI 信任与安全负责人：权限过滤、墓碑优先、撤回 / 删除不复活、日志隐私最小化在规模下是否仍成立。
- 产品架构负责人：性能结论是否服务个人长期外脑，而不是把产品推成企业搜索 / 运维平台。
- 体验设计负责人：等待、失败、部分索引、后台维护、备份恢复、清理 ETA 是否能转化为用户可理解状态。

## 核心问题

请重点回答：

1. 你采用了什么合成数据模型和规模阶梯？它如何代表 LifeOS 长期个人使用，而不是随机压测？
2. 本机实际环境是什么？是否达到 16GB RAM / 足够 NVMe 的最低测试条件？
3. 1 万 / 10 万 / 100 万内容单元分别完成了哪些实测？哪些只完成估算？原因是什么？
4. 捕获写入、FTS 初建 / 增量、checkpoint、integrity check、备份、恢复、墓碑重放分别表现如何？
5. 关键词 / 元数据查询、权限过滤、Project 恢复包组装的 p50 / p95 / p99 是多少？
6. 删除 / 撤回 / 断源 / 低 generation / 旧索引在规模下是否会被复活或泄漏？
7. 向量维度、覆盖率、半精度、ANN / exact 的成本估算或实测说明了什么？向量是否应作为 V1 硬依赖？
8. 100 万内容 / 300 万分块下，磁盘、内存、CPU、索引构建时间、备份恢复时间是否触发 V1 降级或架构调整？
9. 哪些优化可以接受？哪些优化因破坏信任底线必须禁止？
10. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
11. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 证据包可一条命令复跑，或清楚说明分阶段复跑命令和资源要求。
- 合成数据不包含真实敏感内容、真实路径、真实 Vault 名、真实 Project 名或完整真实 prompt / 输出。
- 1 万与 10 万规模至少有可复跑实测；100 万 / 300 万若未完成，必须给出明确阻塞原因、资源缺口和可信外推边界。
- 查询、删除、备份、恢复和索引重建的结果区分实测 / 估算 / 未验证。
- 权限过滤、墓碑优先、撤回 / 删除不复活、来源断开不活跃使用在测试中不能被性能优化绕过。
- 日志和 AuditEntry 不包含真实敏感原文、真实路径、完整 prompt / 输出、向量或可还原真实数据。
- 对 SQLite / FTS5、PostgreSQL / FTS、pgvector / 向量候选给出证据化比较或明确未验证原因。
- 明确列出 V1 可接受降级方案、必须后置能力和触发架构替换的阈值。

## 建议测试矩阵

至少包含：

1. 1 万内容 / 3 万分块生成与导入。
2. 10 万内容 / 30 万分块生成与导入。
3. 尽力完成 100 万内容 / 300 万分块生成、导入或分阶段外推。
4. 捕获单条写入 p95。
5. 批量导入吞吐。
6. FTS 初建与增量更新。
7. checkpoint / integrity check。
8. 关键词查询 p50 / p95 / p99。
9. Project + 时间 + 来源过滤查询。
10. 权限高选择性与低选择性过滤查询。
11. Project 恢复包组装。
12. 单条撤回活跃阻断。
13. 单 Source 删除 / 断源传播。
14. 1% 数据批量清理推进与 ETA。
15. 旧 generation / 旧索引不复活。
16. 备份耗时、额外空间、恢复耗时。
17. 索引重建耗时。
18. 384 / 768 / 1536 维向量成本估算或实测。
19. 向量覆盖率 100% / 部分覆盖 / FTS-first 对比。
20. 日志隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-09/`

证据包至少包含：

- `README.md` 或 `MANIFEST.md`
- 数据生成器与基准脚本
- 测试矩阵
- 原始结果文件
- 环境说明
- 资源 / 性能摘要
- 失败样例
- 清理说明

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存到指定路径。
- 证据包已保存到 `lifeos/spikes/SP-09/`，并提供入口文件。
- 明确区分实测、估算、推断、建议和待确认问题。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过。
- 明确说明结论是 Pass、Pass with Conditions、Fail 还是 Blocked。
- 明确说明哪些结论可以作为技术架构候选输入，哪些不能冻结。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改 Stitch。
- 不修改 PM 主账本。
- 不改变 LifeOS 产品定位。
- 不冻结技术架构、Schema、API、向量方案、数据库方案或性能 SLA。
- 不进入正式 MVP 开发。
- 不连接真实用户数据、真实 Vault、真实云服务、真实第三方 API、真实模型或付费资源。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
