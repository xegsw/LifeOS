# LIFEOS-P2-008｜SP-08 可迁移导出、恢复与重导入技术 Spike

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-008
- 任务名称：SP-08 可迁移导出、恢复与重导入技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；导出包样例、manifest、校验报告、重导入结果、失败样例和脚本放入证据目录，不计入正文
- 主责角色：数据 / 领域模型负责人
- 协审角色：技术架构负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS 的长期价值来自“用户拥有自己的数据”。因此 V1 不能只做到内部可用，还必须验证用户能导出、理解、校验、迁移和有限重导入自己的数据。

`LIFEOS-P2-002` 已验证来源、版本、Derivation 与证据链最小映射成立；导出必须保留 Source、Artifact、ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry 与重要 Link 的身份和追溯关系。

`LIFEOS-P2-005` 已验证撤回 / 删除传播、不复活和清理状态；导出与重导入必须继承墓碑、撤回、断源和证据失效语义，不能让旧导出包绕过删除 / 撤回。

`LIFEOS-P2-006` 已验证离线同步与状态一致性候选机制；重导入必须避免旧版本、旧队列、旧候选或字段级 LWW 覆盖当前用户权威状态。

`LIFEOS-P2-007` 已验证可信搜索与 Project 恢复包候选机制；导出包应能保留恢复包所需证据，但不要求导出 FTS posting、向量、缓存、重排特征等可重建派生产物。

现在要验证 SP-08：

> LifeOS 是否能用“人可读目录 + 稳定机器可读 manifest + 内容文件 + 校验和 + 导出 / 重导入校验器”表达用户原文、来源、版本、确认状态、派生物、Feedback、重要关系、授权 / 删除说明，并在空环境或已有环境中校验与重导入，而不复活已删除、已撤回、已断源或证据失效内容。

本任务允许在 `lifeos/spikes/SP-08/` 下创建最小本地验证代码、合成数据、导出包样例、manifest、校验器、重导入器、失败样例、日志和证据包。不得处理真实敏感数据，不得连接真实 Vault，不得调用真实模型、真实云、真实第三方 API 或付费资源，不得冻结 Schema / API / 正式导出格式 / 技术架构，不得进入正式 MVP 开发。

## 目标

本任务完成后，要回答：

1. V1 是否可以采用“人可读目录 + JSON/JSONL manifest + 内容文件 + checksum”的非冻结导出概念格式？
2. 导出包是否能保留用户原文、来源、版本、确认状态、Derivation、Feedback、重要 Link、Authorization / 删除说明与最小审计说明？
3. 用户在没有 LifeOS 专有服务的情况下，是否能理解导出包中哪些是原文、哪些是 AI 派生、哪些是用户确认、哪些只是来源指针或不可导出说明？
4. 导出前是否能执行授权 / 许可检查，区分用户数据主权与外部内容再分发许可？
5. 已删除正文、已撤回处理、已断开 Source、证据已失效、不可导出的外部内容是否不会被导出或重导入复活？
6. 向量、FTS posting、缓存、重排特征是否可以不导出，并能从合法原始数据重建？
7. 空环境校验是否能发现 checksum 错误、缺失文件、引用断裂、manifest 版本不兼容、权限 / 删除说明缺失？
8. 重导入是否幂等，是否不会覆盖已有原文；遇到重复、旧版本、低 generation、冲突或已删除目标时是否显式冲突或拒绝？
9. 当前结果是否足以决定 V1 基础导出能力保留、降级、后置或阻断正式 MVP 开发？

## 范围

本任务必须覆盖：

- 合成数据：
  - 30-80 条内容单元，覆盖 3-5 个 Project；
  - Source、Artifact、ArtifactVersion、Derivation、Decision、Action、Link、Feedback、Authorization、AuditEntry；
  - 用户原文、外部来源指针、可缓存快照、不可导出外部内容、AI 派生、AI 候选、用户确认对象、已删除对象、已撤回处理、已断源、证据失效、冲突分支。
- 导出包概念格式：
  - 人可读目录；
  - `manifest.json` 或 `manifest.jsonl`；
  - 原文 / 内容文件；
  - 来源指针和不可导出说明；
  - checksum；
  - schema / manifest version；
  - export metadata；
  - 最小 audit / privacy note；
  - restore / reimport report。
- 导出规则：
  - 用户原文和用户确认历史优先保留；
  - AI 派生、AI 候选、用户确认必须身份分离；
  - 外部内容按许可与可导出状态处理；
  - 删除 / 撤回 / 断源 / 证据失效必须有不可还原说明或缺口说明；
  - 不导出可重建索引、向量、缓存、重排特征；
  - 导出日志不得包含真实正文、真实路径、完整 prompt / 输出或可还原敏感内容。
- 校验：
  - checksum；
  - manifest schema；
  - 引用闭包；
  - Source / Artifact / Version 身份；
  - Derivation 输入；
  - Link / Feedback 关系；
  - Authorization / tombstone / restriction generation；
  - 缺失文件说明；
  - 不可导出外部内容说明。
- 重导入：
  - 空环境导入；
  - 已有环境重复导入；
  - 旧包重导入；
  - 低 generation 导入；
  - 删除 / 撤回后的旧包导入；
  - 冲突版本导入；
  - 来源指针恢复但不自动重新授权；
  - 不覆盖已有原文，不用字段级 LWW。

## 非范围

本任务暂时不要做：

- 不开发正式导出 UI。
- 不开发正式产品导入器。
- 不修改 Stitch。
- 不连接、读取或扫描真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件、真实凭据或真实 `.obsidian` 配置。
- 不调用真实模型、真实云服务、真实第三方 API、付费资源或外部账号。
- 不制定正式法律条款、外部内容许可政策或商业数据处理协议。
- 不承诺长期跨版本完全还原、跨产品迁移、真实附件完整性、生产备份 SLA 或灾难恢复 SLA。
- 不冻结导出格式、Schema、API、文件布局、压缩格式、加密方案、技术栈或技术架构。
- 不实现 SP-09 100 万内容单元容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-08/` 下创建和修改：
  - 本地验证脚本；
  - 合成数据；
  - 示例导出包；
  - manifest；
  - 校验器；
  - 重导入器；
  - checksum / 引用闭包报告；
  - 权限 / 删除 / 不可导出说明；
  - 重导入结果；
  - 失败样例；
  - `README.md` 或 `MANIFEST.md`；
  - 环境说明与清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`
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
- `lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-007_sp07_trusted_search_recovery_package_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-007_pm_review.md`
- `lifeos/spikes/SP-03/`
- `lifeos/spikes/SP-05/`
- `lifeos/spikes/SP-06/`
- `lifeos/spikes/SP-07/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现任务卡与产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策上下文，只读取 D-0039、D-0050、D-0055、D-0104、D-0105、D-0106 或最近 5-10 条相关决策。
- 若上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- Source / Artifact / Version / Derivation / Feedback / Link / Authorization / AuditEntry 的导出身份是否清楚且可校验？
- 导出包是否同时对人可读、对机器可校验？
- 删除 / 撤回 / 断源 / 失效证据是否不会被旧导出包或重导入复活？
- 重导入是否幂等，且不会覆盖已有原文或用户权威状态？
- 是否清楚写明概念格式边界，不外推为正式导出格式或跨版本 SLA？

协审角色必须重点检查：

- 技术架构负责人：导出 / 校验 / 重导入候选机制是否避免绑定特定服务、索引、向量库或供应商。
- AI 信任与安全负责人：AI 派生、候选、用户确认、不可导出说明、审计最小化和撤回 / 删除不复活是否成立。
- 产品架构负责人：导出能力是否服务个人数据主权和长期可迁移，而非变成企业归档 / 合规后台。
- 体验设计负责人：导出成功、部分导出、不可导出、缺失文件、校验失败、冲突重导入和恢复限制是否有用户能理解的状态语言。

## 核心问题

请重点回答：

1. 你采用了什么最小导出 / 校验 / 重导入模型？为什么足以验证 SP-08，而不是冻结正式格式？
2. 人可读目录、manifest、内容文件、checksum、缺口说明如何组织？
3. 用户原文、外部来源、AI 派生、AI 候选、用户确认对象、Feedback、Link 和 AuditEntry 如何区分身份？
4. 导出前授权 / 许可检查如何执行？不可导出外部内容如何表达？
5. 已删除、已撤回、已断源、证据失效、低 generation、旧导出包如何避免复活？
6. 空环境校验如何发现 checksum 错误、缺失文件、引用断裂、manifest 版本不兼容和权限 / 删除说明缺失？
7. 重导入如何保证幂等？如何处理重复导入、已有对象、冲突版本和旧包？
8. 向量、FTS posting、缓存、重排特征为什么不必进入导出核心？如何重建？
9. 哪些导出或重导入场景失败？失败后对 V1 范围、导出体验和后续 SP-09 有什么影响？
10. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
11. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 导出包包含人可读入口、机器可读 manifest、内容文件或来源指针、checksum、schema / manifest version 和导出说明。
- 用户原文、外部来源、AI 派生、AI 候选、用户确认对象、Feedback、Link、Authorization、AuditEntry 身份区分清楚。
- 每个可导出 ArtifactVersion 都有 checksum；校验器能发现内容篡改和缺失文件。
- 引用闭包检查能发现 Source、Artifact、Version、Derivation、Link、Feedback 的断裂引用。
- 已删除正文、已撤回处理、已断源、证据失效和不可导出外部内容不会以可活跃使用正文形式导出。
- 旧导出包、低 tombstone / restriction generation、低 Authorization version 重导入不会复活已删除、已撤回或已断源内容。
- 重复重导入幂等；已有原文不被覆盖；冲突版本显式冲突或保留分支。
- 导出包不包含可重建向量、FTS posting、缓存或重排特征作为用户业务资产。
- 日志和 AuditEntry 不包含真实敏感原文、真实路径、真实 Vault 名、完整 prompt / 输出、向量或可还原真实数据。
- 证据包可一条命令复跑，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。

## 建议测试矩阵

至少包含：

1. 导出用户原文与版本。
2. 导出 Source 指针和可缓存快照。
3. 不可导出外部内容只导出指针 / 缺口说明。
4. 导出 AI 派生与 AI 候选，并保持未确认身份。
5. 导出用户确认 Decision / Action / Link / Feedback。
6. checksum 成功校验。
7. 篡改内容后 checksum 失败。
8. 删除内容后旧正文不导出。
9. 撤回处理后派生不导出为活跃内容。
10. Source 断开后不导出旧读取结果为新来源。
11. 唯一证据失效后导出 review_required / 缺口说明。
12. manifest 引用断裂检测。
13. 缺失文件检测。
14. manifest 版本不兼容检测。
15. 空环境重导入成功。
16. 重复重导入幂等。
17. 已有原文不被覆盖。
18. 冲突版本导入显式冲突。
19. 低 generation 旧包导入不复活删除 / 撤回。
20. 向量 / FTS / 缓存不导出且可从合法原始数据重建。
21. 导出日志隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-08/`

证据包至少包括：

- `README.md` 或 `MANIFEST.md`
- `SP-08_report.md`
- `run_spike.py` 或等价本地验证脚本
- `fixtures.md`
- `export_format_candidate.md`
- `sample_export/`
- `manifest.json` 或 `manifest.jsonl`
- `validation_report.json`
- `reimport_results.json`
- `test_matrix.csv`
- `broken_package_cases/`
- `permission_and_license_report.md`
- `rebuildable_artifacts_report.md`
- `failed_cases.md`
- `raw_logs/`
- `environment.md`
- `cleanup.md`

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 最小导出 / 校验 / 重导入模型与非冻结说明
3. 合成数据、导出包结构和 manifest 字段说明
4. 用户原文、外部来源、AI 派生、用户确认、Feedback、Link、AuditEntry 身份区分
5. 授权 / 许可检查与不可导出内容处理
6. 删除 / 撤回 / 断源 / 证据失效 / 旧包不复活验证
7. checksum、引用闭包、缺失文件和版本不兼容验证
8. 空环境重导入、重复导入、冲突导入和已有对象保护验证
9. 向量 / FTS / 缓存 / 重排特征不导出与重建说明
10. 失败样例、降级状态和用户可理解语言
11. 最终结论：Pass / Pass with Conditions / Fail / Blocked
12. 对 V1 导出、数据主权、删除 / 撤回、SP-09 和技术架构候选的影响
13. 需要 PM / 用户确认的问题
14. 角色与关卡自检
15. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-08 的问题放入“后续任务建议”，不要扩写 SP-09 或技术架构冻结。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-008_sp08_portable_export_restore_reimport_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-08/`，且包含 `README.md` 或 `MANIFEST.md`。
- 证据包可复跑、可复核，且不依赖真实模型、真实云、真实第三方、真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2、Gate 3、Gate 4 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：导出身份清楚；checksum 与引用闭包可校验；删除 / 撤回 / 断源 / 证据失效不复活；重导入幂等且不覆盖原文；不可导出内容有说明；证据可复跑。
- **Pass with Conditions**：P0 安全断言全部通过，但外部许可、附件范围、跨版本兼容、正式加密、压缩、性能或非核心对象存在有界缺口，并已有明确降级与复验条件。
- **Fail**：任何已删除 / 撤回 / 断源内容被复活；任何重导入覆盖用户原文；任何导出包无法区分原文 / AI / 用户确认；任何校验无法发现篡改或断链；任何日志泄露真实敏感信息；或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实 Vault、真实云、真实模型、真实第三方或真实敏感数据弥补 mock 不足。

## 降级路径

若 SP-08 无法无条件通过，应明确建议以下一种或多种降级：

- V1 只提供只读导出，不提供重导入。
- V1 只导出用户原文、来源指针、版本和用户确认对象，AI 派生与候选后置。
- V1 对外部内容只导出指针和许可说明，不导出缓存快照。
- V1 重导入只进入隔离区，需用户确认后合并。
- V1 不承诺跨版本完整产品还原，只承诺可读、可校验、可迁移的基础包。
- 导出失败或部分导出时必须生成清晰缺口清单。

不可降级底线：用户原文和身份必须可导出；删除 / 撤回 / 断源不能复活；AI 不能伪装用户确认；导出包必须可校验；重导入不得覆盖已有原文；审计不可还原真实内容。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-08/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API、导出格式或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据、真实凭据、真实笔记或真实附件。
- 不调用真实模型、真实云服务或真实第三方 API。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-08 Pass 解释为正式导出格式、正式迁移能力、生产备份 / 恢复 SLA、技术架构冻结或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
