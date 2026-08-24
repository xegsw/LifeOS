# LIFEOS-P2-008｜SP-08 可迁移导出、恢复与重导入技术 Spike 报告

## 1. 任务边界与结论摘要

**[已验证事实]** 本任务在 `lifeos/spikes/SP-08/` 内完成 48 条合成内容单元、4 个 Project、Python 标准库单进程候选实现，覆盖人可读目录、JSON manifest、Markdown 内容、SHA-256、引用闭包、授权 / 许可检查、5 类破损包、空环境 / 已有环境 / 重复 / 冲突 / 旧代重导入和日志隐私扫描。复跑结果为 **25/25 PASS，P0 失败 0**；详细机器结果见证据入口 `lifeos/spikes/SP-08/README.md`。

**最终结论：`Pass`，严格限于本次非冻结、合成、本地候选机制层。** “人可读目录 + 稳定机器可读 manifest + 内容文件 + checksum”足以作为 V1 基础导出能力的概念候选；它能在无 LifeOS 专有服务时被通用文本 / JSON 工具理解和校验，也能证明重导入不必覆盖已有原文或复活受控内容。

**[限制]** 本结果不冻结正式格式、Schema、API、字段枚举、文件布局、压缩、签名、加密、技术栈或技术架构；不承诺跨版本完全还原、跨产品迁移、真实附件完整性、生产备份 / 灾备 SLA；没有使用真实 Vault、用户数据、模型、云、第三方或付费资源，也不解除正式 MVP 开发阻塞。

**[建议｜需 PM 确认]** V1 保留“基础可读导出 + 包校验 + 安全重导入”作为 Must 候选合同；正式实现前继续把许可政策、版本迁移、附件、加密 / 签名、容量性能和用户体验作为未冻结条件。本专项会话不修改 PM 账本或阶段状态。

## 2. 最小导出、校验与重导入模型

候选包分成三层。第一层是人可读入口：根 `README.md` 解释身份和部分导出，`RESTORE_LIMITS.md` 解释恢复边界，正文按 Project / ArtifactVersion 放在 Markdown 文件。第二层是 `manifest.json`：记录包版本、导出元数据、身份图例、Source / Artifact / 不可变 ArtifactVersion、Derivation、Decision、Action、Link、Feedback、Authorization、最小 AuditEntry、tombstone、restriction 和 gap。第三层是完整性与控制：每个包含正文的 ArtifactVersion 有 SHA-256；没有正文的版本必须引用不可还原 gap；重导入先应用目标环境当前控制状态，再处理内容。

这个模型足以验证 SP-08，是因为核心风险不在最终压缩格式，而在四组不变量是否能同时成立：人能分辨内容身份；机器能验证文件和关系；许可 / 删除状态能阻止正文进入包；旧包不能突破目标环境更高的权威 generation。候选实现只使用文件和 JSON 包络，没有依赖数据库、搜索引擎、向量库、模型或供应商，因此证明了最小可迁移性，同时没有把示例字段误写为正式 Schema。

校验器按 fail closed 执行：不兼容 manifest、缺必需字段、缺文件、checksum 错误、Source / Artifact / Version / Derivation / Link / Feedback 断裂、tombstone 或 restriction 说明缺失、pointer-only 外部内容夹带正文，都会返回明确错误码。它不会猜测缺失关系，也不会因“尽量恢复”跳过控制信息。

重导入候选坚持对象级比较与追加：相同 Version ID / 相同 digest 幂等跳过；相同 ID / 不同 digest 形成显式冲突；已有用户原文不覆盖；ArtifactVersion 不原地改写；不使用字段级 LWW。来源指针可恢复为未授权状态，但恢复指针不等于重新连接、读取、云处理或第三方处理授权。

## 3. 合成数据、目录与 manifest 字段

夹具含 48 个 ArtifactVersion，均关联 4 个 Project 之一，并拥有 Source、Artifact、Authorization 和最小 AuditEntry。内容身份轮换覆盖用户原文、Decision、Action、外部材料、AI 派生和 AI 候选；关系层包含 Derivation、47 条 Link、16 条 Feedback，以及确认对象。特殊样例覆盖来源指针、许可内缓存快照、不可再分发外部内容、已删除、处理授权撤回、Source 断开、唯一证据失效、冲突分支、AI 候选、AI 派生和用户确认对象。

样例布局为：

```text
sample_export/
  README.md
  RESTORE_LIMITS.md
  manifest.json
  content/
    project-1/av-...md
    project-2/av-...md
    project-3/av-...md
    project-4/av-...md
```

`export_metadata` 表达 export ID、时间、生成器、包状态、内容 / Project 计数、无专有服务可读性和 non-frozen 标记。Source 包含类型、合成 locator、连接状态、Authorization、许可状态和 restriction generation。Artifact 表达 Project、Source、内容身份、authority、确认状态、current version 与 tombstone generation。ArtifactVersion 表达不可变版本、内容身份、证据 / 冲突状态、相对文件、checksum、导出状态和 gap。Derivation 保留精确输入 / 输出 Version、工作流 / 模型描述、Authorization 与当前状态。

**[推断]** JSON 单文件在 48 条样例下最易审阅；正式容量可能需要 JSONL、分片或索引目录。但不论载体如何变化，稳定身份、精确版本、关系闭包、控制 generation、checksum 与 gap 是不能因性能而删除的语义合同。

## 4. 内容身份、用户确认与最小审计

用户原文和用户确认对象的 `authority=user`，AI 派生为 `ai_derived`，AI 下一步 / 关系建议为 `ai_candidate / unconfirmed`，外部材料为 `external_material`。Decision 和 Action 除指向 Artifact / Version 外，继续保留用户 authority 与 confirmed；候选 Derivation 即使输出内容存在，也不能靠导出或导入自动建立确认状态。

Feedback 是追加事件而非覆盖字段，Link 记录建立者、确认状态和有效性。Derivation 指向精确输入版本而非“当前 Artifact”，避免重导入后证据漂移。唯一证据失效时，用户确认历史仍可保留，但进入 gap / review required，不作为当前活跃证据或自动建议依据。

AuditEntry 只记录作用域化 event / target 引用、事件类型、结果码和政策版本。运行日志只记录计数、错误码与作用域化引用；不包含正文、真实路径、Vault 名、完整 prompt / 输出、向量、凭据或原始稳定对象 ID。隐私模式扫描命中 0。**[限制]** 本次未验证大规模 ID 枚举、时间关联或跨日志重识别；正式实现仍需访问控制、保留期和聚合粒度评审。

## 5. 授权、许可与不可导出内容

导出前分别检查 Authorization、Source 状态、tombstone / restriction generation、证据有效性和外部内容再分发许可。“用户拥有自己的 LifeOS 数据”与“有权再分发第三方全文”被明确拆开：用户原文在当前允许时包含正文；许可内缓存快照可包含内容但仍标为 external；许可未知或禁止的外部材料只含来源指针、许可状态和 gap。

已删除版本只保留 tombstone generation 与不可复活说明；撤回处理只保留 Authorization / restriction 状态与缺口；Source 断开只保留未授权指针，旧读取结果不被包装成当前来源；唯一证据失效只保留确认历史和复核说明。所有没有正文文件的 ArtifactVersion 都必须引用 gap，校验器会拒绝“缺文件但无解释”。

**[建议｜需 PM 确认]** 正式许可政策尚未制定时保持默认 pointer-only / fail closed。法律条款、第三方站点许可和附件再分发不应由本 Spike 冻结；若未来无法给出可信许可判定，V1 应降级为指针与用户自有摘录，而不是放宽导出检查。

## 6. 删除、撤回、断源、证据失效与旧包不复活

候选导入顺序继承 SP-05 / SP-06：恢复或导入开放正常内容前，先加载目标环境当前 tombstone generation、restriction generation 与 Authorization version。包内代际低于目标环境时拒绝；未知控制状态默认拒绝。正文文件存在也不能绕过这一入口门控。

测试建立目标环境更高的删除代、撤回代、断源代和 Authorization version，再导入旧包；至少 3 个受控版本返回 `rejected_stale_generation`，没有写入当前版本集合。已删除、撤回、断源、证据失效及不可导出外部内容在基线包内均无可活跃正文，只有 identity / control / gap。来源指针恢复后 `authorized=false`，不会自动重新连接或发起读取。

这证明“不复活”依赖目标环境的当前控制账本，而不是相信导出包自称最新。**[限制]** 本次是单进程字典环境，不代表生产同步、备份恢复 gate、跨设备乱序或数据库事务已通过；正式实现仍须把控制面加载和内容接纳做成不可绕过的恢复前置。

## 7. checksum、引用闭包、缺失文件与版本验证

基线包 48 个版本全部进入校验；每个包含正文的版本都有 SHA-256，基线 schema、checksum 与引用闭包为 valid。故障注入复制基线包后分别制造：正文篡改、文件缺失、Derivation 输入引用断裂、manifest 版本 99.0、restriction 列表缺失。校验器依次给出 checksum mismatch、content file missing、broken derivation reference、manifest version incompatible 和 restriction note missing，5 类均被发现。

引用闭包同时检查 Source→Authorization、Artifact→Project / Source / current Version、Version→Artifact / Source、Derivation→输入 / 输出 Version、Link→两端 Artifact、Feedback→目标对象。tombstone generation 大于基线却没有 tombstone，或 restriction generation 大于基线却没有 restriction，也会失败。这避免只校验文件完整而忽略语义完整。

**[限制]** SHA-256 证明内容与清单一致，不证明发布者身份或包未被整体替换；正式防篡改可能需要签名、密钥管理或可信导出渠道，属于后续架构 / 安全决策，不在本任务冻结。

## 8. 空环境、重复、冲突与已有对象保护

空环境导入将合法版本与缺口身份插入候选存储，未发生冲突；同一包第二次导入的 inserted 为 0，全部版本走 idempotent。已有环境预置 `art-001` 的本地用户原文；导入时目标原文保持不变，incoming version 进入 `user_original_protected` 冲突分支。相同 Version ID 但不同 digest 的包返回显式冲突，也不覆盖已有 digest。

该候选没有字段级 LWW，也不使用客户端时间决定权威。用户 authority、AI candidate、Source state 和 generation 不能被拆成字段后各自“最新者获胜”；任何冲突在对象 / 版本层保留分支，等待用户或后续明确规则处理。旧包与低 generation 在版本插入前拒绝，控制状态不是导入完成后再补打的标签。

**[体验建议]** 导出 / 恢复至少区分：成功、部分导出、不可导出、包损坏、版本不兼容、安全拒绝、重复跳过、原文已保护、冲突待处理和来源未重新授权。证据包提供机器状态到用户语言映射，但正式 UI 和文案仍需后续体验评审。

## 9. 向量、FTS、缓存与重排特征

manifest 明确列出 `fts_postings`、`vectors`、`cache`、`rerank_features` 为排除的可重建派生产物。它们依赖分词器、embedding 模型、索引版本、缓存策略或排序实现，不应伪装成用户长期业务资产，也不应迫使迁移包绑定特定搜索服务或模型供应商。

重建输入只能来自当前合法、许可允许、未删除 / 撤回 / 断源且证据有效的版本集合；重建时再次执行 Authorization 和 generation 检查。指针恢复不能自动抓取外部内容，旧缓存或旧向量也不能成为绕过 restriction 的恢复来源。

**[限制]** 本任务没有真正重建 FTS 或向量，只验证合法重建输入可以由 manifest 枚举、排除项有明确说明。SP-09 需要验证规模、重建时间、磁盘占用、删除传播和恢复窗口；真实 embedding 仍需模型替换、隐私、成本和过滤后召回验证。

## 10. 失败、降级与 V1 影响

校验失败不静默“尽量导入”。checksum、缺文件、断引用、版本不兼容、控制说明缺失属于安全拒绝；许可限制、断源、证据失效属于可解释的部分导出；已有原文或版本分歧属于显式冲突。对用户的关键语言是“正文与清单不一致”“文件缺失”“此包版本不支持”“控制信息不完整”“仅保留来源指针”“旧包不会恢复已停止使用的内容”“已有原文未被覆盖”。不能把 active blocked 写成所有物理副本已删除，也不能把 pointer restored 写成来源已重新连接。

**[建议｜需 PM 确认]** 对 V1 的能力处置为：

1. 保留人可读导出、机器 manifest、内容 checksum、缺口说明和本地校验器作为基础能力候选。
2. 保留安全重导入最小合同：控制状态优先、原文保护、幂等、显式冲突、来源不自动授权。
3. 正式许可政策、附件、加密 / 签名、跨版本迁移和生产恢复 SLA 暂不承诺；可在 UI 中诚实标为部分导出或当前不支持。
4. 若后续无法稳定迁移 manifest，基础“用户可读原文 + 来源 / 身份 / 缺口 + checksum”仍不应删除；可以降级重导入自动化，而不是牺牲数据主权。
5. 本 Pass 是 SP-09 与技术架构冻结准备的输入，不等于 Stage 3 准入。

## 11. 对 SP-09 与技术架构候选的影响

SP-09 应复用相同 4 个 Project / 状态类别并扩大到容量夹具，测量 manifest 生成与解析、checksum 吞吐、包体、引用闭包、Source 级批量删除、索引重建、恢复门控和冲突报告成本。若单 JSON 过大，可测试 JSONL / 分片，但不能丢失稳定 ID、精确 Version、generation、gap 或闭包检查。

技术架构评审可以评估关系型控制账本、流式导出 / 校验、签名、增量迁移和恢复 gate；当前证据只说明这些合同不要求专有云、向量数据库、搜索集群或模型供应商。任何正式组件选择、兼容期、备份窗口和密钥方案仍需独立评审与 PM 确认。

风险建议由 PM 判断是否登记：整体包替换缺少签名、许可判定错误、附件 / 大文件完整性、跨版本迁移失败、控制账本恢复顺序被绕过、超大 manifest 内存占用、冲突过多导致体验失控、最小审计关联重识别。本专项会话未修改 `RISK_LOG.md`。

## 12. 事实、推断、建议与待确认区分

- **[事实]** 25 项断言在确定性本地合成实现中全部通过；基线包 valid；5 类破损包被识别；重复导入幂等；已有原文不覆盖；冲突显式；旧代被拒绝；隐私扫描命中 0。
- **[推断]** 最小目录 / manifest 合同可支持 V1 基础可迁移性，不需要把索引、向量或供应商状态做成导出核心；真实容量和跨版本行为仍未知。
- **[建议]** 将基础导出与安全重导入合同保留为 V1 Must 候选，同时后置正式格式、许可政策、附件、签名 / 加密和 SLA 冻结。
- **[待确认]** 任务是否 Accepted、V1 能力处置是否采纳、哪些风险进入 PM 账本、是否允许启动 SP-09，以及是否继续保持技术架构未冻结和 Stage 3 Blocked。

## 13. 需要 PM / 用户确认

1. 是否验收 SP-08 为上述有限边界内 `Pass`，并允许作为 SP-09 和技术架构候选输入。
2. 是否采纳 V1 基础合同：人可读导出 + manifest + checksum + gap + 校验；重导入控制状态优先、幂等、原文保护、显式冲突、来源不自动授权。
3. 是否确认本次不冻结正式导出格式、Schema、API、文件布局、压缩、加密 / 签名、技术栈、技术架构、备份 / 灾备 SLA 或跨版本保证，且不解除 Stage 3 阻塞。
4. 是否把许可判定、附件完整性、整体包签名、跨版本迁移、控制账本恢复顺序、容量与审计重识别列为后续风险 / 验证条件。
5. 是否在采纳后启动 SP-09 容量与性能 Spike。以上均属于 PM 主会话决策；专项会话未修改主账本。

## 14. 角色与关卡自检

- **主责｜数据 / 领域模型负责人：Pass（合成导出语义层）。** Source、Artifact、Version、Derivation、Feedback、Link、Authorization、AuditEntry 身份和闭包清楚；删除 / 撤回 / 断源 / 失效以控制状态和 gap 表达；没有把 JSON 字段当数据库表冻结。
- **技术架构负责人：Pass（候选机制层）。** 一条命令复跑，无专有服务、模型、向量库或供应商依赖；校验和重导入合同可执行；生产并发、容量、签名、附件与迁移框架未外推。
- **AI 信任与安全负责人：Pass（身份与不复活层）。** AI 派生、候选和用户确认分离；低 generation / 旧包拒绝；来源指针不重新授权；日志最小化。真实供应商与法律许可未通过。
- **产品架构负责人：Pass。** 导出服务个人数据主权、长期理解与迁移，没有扩成企业合规归档后台、管理员控制台或 IT 运维产品。
- **体验设计负责人：Pass（状态语言层）。** 成功、部分、不可导出、损坏、缺文件、不兼容、安全拒绝、冲突、待复核与恢复限制均有可理解语言；正式 UI / 可用性未验证。

| 关卡 | 本任务自检 | 边界 |
|---|---|---|
| Gate 2 数据与来源 | **Pass（合成导出 / 重导入语义层）** | 身份、版本、来源、关系、控制和 gap 可校验；未冻结 Schema / 格式 / 许可政策 |
| Gate 3 AI 权限与信任 | **Pass（本地候选实现层）** | AI 身份分离、旧包不复活、来源不再授权、审计最小化；未验证真实云 / 第三方 / 法律许可 |
| Gate 4 技术可行性 | **Pass（48 条、单进程、标准库层）** | 25/25 可复跑；未验证生产容量、并发、附件、签名 / 加密、跨版本与 SLA |

以上是专项会话自检。是否正式通过项目关卡、是否 Accepted、是否进入 SP-09 或后续技术架构独立评审，仍需 PM 主会话决定。本任务不是技术架构冻结或正式 MVP 准入事项，因此本次无需独立评审；未来冻结技术架构或进入 Stage 3 时必须独立评审。

## 15. 证据包路径清单

- 入口：`lifeos/spikes/SP-08/README.md`
- 可复跑脚本：`lifeos/spikes/SP-08/run_spike.py`
- 机器结论：`lifeos/spikes/SP-08/results.json`、`validation_report.json`、`reimport_results.json`、`test_matrix.csv`
- 格式与夹具：`export_format_candidate.md`、`fixtures.md`、`sample_export/`
- 许可与重建：`permission_and_license_report.md`、`rebuildable_artifacts_report.md`
- 失败样例：`broken_package_cases/`、`failed_cases.md`
- 日志与边界：`raw_logs/`、`environment.md`、`cleanup.md`

复跑命令：`python3 lifeos/spikes/SP-08/run_spike.py`

