# LIFEOS-P2-002｜SP-03 来源、版本、Derivation 与证据链最小映射技术 Spike 报告

## 1. 任务边界与结论摘要

**任务结论：Pass（仅限本 Spike 的合成语义映射、确定性脚本与 macOS arm64 / Python 3.9.6 环境）。**

**[已验证事实]** 本任务实际创建并运行了隔离本地验证脚本，使用 `fixture-pack-v1-sp03` 合成夹具覆盖两条主证据链和 22 项断言。22/22 全部通过，P0 失败 0；依赖失效漏报 0、误报 0、不可解释全库失效 0；Project / 文件夹 / 标签 / 双链 / 候选 Link 扩权 0；旧包重导入复活 0；审计禁止模式命中 0。任一关键输出均可由一次调试查询返回精确输入版本、Source、Authorization / 政策版本、目的、位置 / 主体、工作流 / 模型版本、生成时间、输出身份、当前状态及 Feedback 历史。

**[合理推断]** 对 V1 的“5 分钟上下文恢复与下一步确认”而言，显式精确版本引用、`Derivation.inputs` 依赖边、六维 Authorization 与政策包络、追加式 Feedback、带身份的重要 Link、最小 AuditEntry 和控制事件优先规则，足以支撑最小证据链、依赖失效、权限继承和基础导出包络，不需要专用图数据库、全量事件溯源或 11 张固定表。

**[建议]** SP-03 可作为 SP-02 Obsidian 只读接入的证据链包络输入；继续保持真实模型、真实敏感恢复、SP-04 运行时授权、SP-05 全链路物理清理、SP-06 同步、SP-08 正式迁移协议和 Stage 3 开发阻塞。不得把 Pass 解释为 Schema、API、事件流、存储、索引、导出格式或技术架构冻结。

## 2. 验证实现与最小映射说明

验证实现位于 `lifeos/spikes/SP-03/run_spike.py`，只使用 Python 标准库，在内存字典中建立语义记录，并把可复核结果写为 JSON、CSV 和 Markdown。它不连接数据库服务、真实 Vault、网络或模型，也不进入正式产品目录。

候选最小映射如下：

| 语义 | 本次最小表达 | 关键不变量 |
|---|---|---|
| `Source` | 独立来源身份、类型、作用域化定位、可达/连接状态 | 不与内容本体或 Project 合并 |
| `Artifact` | 内容本体身份、Source 引用、当前版本指针、墓碑状态 | 用户原文、外部原文身份不可被 AI 改写 |
| `ArtifactVersion` | 独立版本 ID、Artifact、内容 hash、顺序、墓碑 | 精确引用、追加版本，不覆盖旧版；不是新增冻结对象 |
| `Derivation` | 类型、精确输入、授权、目的、位置/处理者、工作流/模型版本、输出、时间、状态、缺口 | AI/算法输出必须反查完整输入与约束；合法子集必须新建 |
| `Feedback` | 目标对象/版本、类型、序列、结果对象、当前效力 | 确认、编辑、拒绝、纠正、完成、撤回均追加，不逆写历史 |
| `Authorization` | 主体、范围、动作、目的、位置、时效六维 + 政策版本、敏感级别、接收方、保留/导出/训练限制 | Project/Link 不产生许可；多输入取交集与最严格值 |
| `AuditEntry` | 动作码、作用域化随机引用、授权/政策引用、序列、结果、位置类别 | 不存正文、路径、URL、提示词、输出、向量或自由错误文本 |
| `Link` | 两端、关系类型、来源、确认状态、有效状态 | 外部结构默认只是候选；重要关系可解释、可失效 |

显式依赖边支持从输出向输入回查，也支持从被修改/删除/撤权对象向下游做传递闭包。JSON 只承载包络，不用单一大文档替代依赖边。候选比较见 `mapping_options.md`。该实现足够小，可一条命令在毫秒级复跑，但没有验证规模、并发、跨设备或长期迁移成本。

## 3. 测试夹具说明

固定种子 `20260808` 生成 3 个合成 Source、4 个 Artifact / 精确版本、3 组六维 Authorization、5 个 Derivation、8 个 AI/业务输出对象、7 条 Feedback、4 条重要/候选 Link 和 2 条 AuditEntry。身份样本覆盖用户原文、外部原文、外部主张、AI 整理、AI 候选和用户确认对象。所有正文仅为 `SYNTHETIC_*_NO_REAL_DATA` 合成串，用于生成版本 hash；正文不进入证据日志或 AuditEntry。

两条主链为：

1. 模拟 Obsidian 外部原文版本 → Project 恢复包 → AI 未确认候选下一步 → 用户编辑确认的新对象与新版本 → 完成 Feedback。
2. 外部材料版本 → AI Decision 候选 → 用户确认 Decision → 输入修改、不可达、删除或撤权 → 派生失效、确认历史保留、证据不可用并待复核。

补充夹具覆盖跨 Project、多输入不同限制、合法子集、空交集拒绝、候选 Project / 文件夹 / 标签 / 双链、Feedback 撤回依赖、部分导出和删除前旧包重导入。夹具明细见 `fixture_manifest.md`。

## 4. 证据链回查验证

`evidence_chain_samples.json` 保存两条一次查询结果。以用户编辑确认并完成的 Action 为例，查询先由用户对象的 `origin_candidate_id` 找到原 AI 候选，再找到 `deriv-next-v1`；它直接引用 Obsidian v1、用户原文 v1 与恢复包输出。查询继续展开嵌套恢复包，最终返回两条精确输入版本及 hash、Artifact 身份、Source 类型/可达性、`auth-local-a` 六维授权与 `policy-synth-v3`、`next_step` 目的、local 位置、deterministic stub、工作流/模型版本、生成时间、AI 候选身份，以及编辑确认、完成和历史拒绝样本。

Decision 链同样返回唯一外部材料版本、Source、严格政策包络、AI 候选身份、确认和纠正历史。两条查询未用摘要正文替代证据，也未暴露模型思维链；证据包回答“用了什么、在何权限下、在哪里、为何处理、产出了什么、用户如何响应”。T01 通过。

## 5. 身份分离与用户确认验证

内容身份与权威所有者分开表达：用户原文和外部原文属于 Artifact/Version；AI 整理与候选属于 Derivation；用户编辑确认产生独立 `user_confirmed` 对象与独立用户版本，其 `origin_candidate_id` 永久保留 AI 起点；Feedback 只改变认可或业务效力，不把 AI 文本改写成用户原文。

本夹具同时证明：候选 Action 的 AI 版本与用户编辑版本不同；完成只作用于用户确认 Action；拒绝、纠正和撤回均作为带序列的新记录保留。身份、用户认可、业务状态、证据状态和派生状态可同时存在，未被压成一个“已确认”字段。T02-T04 通过。

## 6. 依赖失效与权限继承验证

失效算法只遍历显式 `Derivation.inputs`，并通过“Derivation 产出 ID 再被下游消费”完成传递闭包。六类触发共预期影响 15 个 Derivation，实际命中 15 个：

- 输入版本修改：精确依赖旧版者进入 `stale/inactive`；
- 来源不可达：依赖者进入 `stale`，输出标 `evidence_unavailable/review_required`；
- 断开来源、删除内容、撤回处理许可：相关派生进入 `invalid/inactive`；
- Feedback 撤回：直接消费该 Feedback 的排序派生进入 `review_required/inactive`。

漏报和误报均为 0，没有把不相关 Decision 链或全库派生一起失效。该结果证明候选映射能表达正确依赖集合；它不代替 SP-05 对 FTS、向量、缓存、队列、备份和第三方副本的物理传播测试。

多输入 `auth-local-a + auth-local-b` 计算结果为：允许 Project 交集仅 `project-alpha`、目的交集仅 `project_recovery`、位置仅 local、敏感级别取 `restricted`、保留期取 7 天、训练保持禁止、导出取 false。合法子集场景没有从旧多输入输出删引用后继续使用，而是生成 `deriv-subset-v2` 并披露被排除的材料；与已撤回排除授权组合时交集为空，结果为拒绝生成，而非编造建议。T05-T14 通过。

## 7. Project / 外部结构不扩权验证

用户确认 Project Link、文件夹候选、标签候选、Wikilink 候选均有独立 Link 身份、来源、确认与有效状态。测试前后 Authorization 集合完全一致，候选关系不创建、修改或传播许可；标签连接到排除材料也不能让 Project A 读取它。扩权计数为 0，重要 Link 字段完整。T15-T16 通过。

这一结果足以作为 SP-02 包络：Vault/文件/版本、frontmatter/标签/双链解析结果可进入外部来源或候选 Link，但任何读取、索引、派生、云/第三方处理仍须独立授权判定。

## 8. 导出 / 重导入与不复活验证

基础导出候选如实返回 `partial`：1 个 Artifact 成功，2 个因墓碑或来源政策被排除，1 个因授权撤回失败；成功项保留 Artifact 身份、精确版本和 Source，业务对象保留 AI/用户身份、原候选、Feedback、证据状态与待复核状态。

测试先生成删除前旧包，再在当前环境加入 `artifact-user-note` 墓碑和 `feedback-action-edit` 撤回。重导入函数第一阶段合并包内与当前控制事件，第二阶段才接纳内容与 Feedback。旧包中的已删 Artifact 和已撤回活跃确认均被阻断，复活数 0。T18-T20 通过。

该结果只证明最小包络和优先级；没有冻结 SP-08 的正式格式、冲突策略、签名、批量恢复、跨版本迁移或完整用户资产覆盖。

## 9. 测试矩阵与验收断言结果

`test_matrix.csv` 共 22 项：21 项 P0、1 项 P1，全部 PASS。最低验收断言结果如下：

| 验收断言 | 结果 |
|---|---|
| 一次调试查询返回完整证据包 | Pass |
| 原文、外部来源、AI Derivation、AI 候选、用户确认无共享可静默覆盖权威字段 | Pass |
| 重要 Link 有来源、确认和有效状态 | Pass |
| 预期受影响 Derivation 漏报 | 0 |
| 不可解释误报 / 全库失效 | 0 / 0 |
| Project / 外部结构扩权 | 0 |
| 多输入最严格限制、合法子集新建、空交集拒绝 | Pass |
| 唯一证据失效后保留用户确认历史、退出自动依据 | Pass |
| 墓碑 / Feedback 撤回重导入复活 | 0 |
| AuditEntry / 日志禁止内容命中 | 0 |

## 10. 日志与隐私检查

`audit_privacy_check.md` 与 `raw_logs/privacy_scan.json` 记录检查结果。AuditEntry 只含允许列表字段；禁止模式覆盖合成正文标记、用户绝对路径、Markdown 文件名、URL、`original_text`、prompt、embedding，命中 0。原始日志只含测试结果、计数、状态、作用域化合成 ID 和 hash；版本 hash 位于证据样本，用于合成内容完整性定位，不进入 AuditEntry，也不可关联真实数据。

**[已验证事实]** 本任务未读取真实 Vault、用户文档或敏感数据，未调用网络、云、第三方 API、付费资源或真实模型，未修改 Stitch、PM 文件或非 Spike 产品代码。T21 通过。

## 11. 最终结论

**Pass。** 全部 P0 追溯、身份、失效、权限继承、外部结构不扩权、用户确认历史和不复活断言均通过，证据包可一条命令复跑。因此，当前候选映射足以证明 SP-03 明确范围内的证据链包络，并足以作为 SP-02 只读扫描结果的下游输入合同。

Pass 的边界必须保留：本任务没有证明真实 Obsidian 身份/扫描、真实模型质量、运行时逐次授权、全链路活跃阻断/物理清理、离线同步冲突、可信检索质量、正式导出迁移或百万级性能。它也不冻结数据模型核心实体、ArtifactVersion 为新核心对象、Schema、API、技术栈或技术架构。

## 12. 降级建议与后续影响

**[建议]** 后续实现候选应保留显式 Derivation 输入依赖语义；若查询复杂，优先增加专用依赖索引，而不是引入通用知识图谱。若 SP-02 无法稳定识别文件移动，应仍以 Source + 精确内容版本作为证据，移动只保留候选。若后续 SP-04/05/06 证明 L3 持久候选成本过高，候选可降为 L1 Derivation 展示，但 Source、版本、Derivation、Feedback、Authorization 和身份/状态边界不得删除。

**[推断]** 当前映射风险主要转移到未来工程：依赖边完整性约束、批量失效与索引成本、跨设备控制事件排序、正式导出兼容性和 AuditEntry 标识反关联。这些分别应由 SP-04/05/06/08/09 验证，不在本任务扩写。

## 13. 需要 PM / 用户确认的问题

1. **[需 PM 确认]** 是否验收 SP-03 为 Pass，并允许 SP-02 继承本报告的 Source / Artifact / Version / Derivation / Feedback / Authorization / AuditEntry / Link 最小证据包络；确认不冻结 Schema 或架构。
2. **[需 PM 确认]** 是否继续维持 Obsidian 的条件规则：只有 SP-02 与 SP-03 均 Pass 才可进入正式接入判断；若 SP-02 Fail，按既有基线降级为手工导入 / 来源指针或移出 V1。
3. **[需 PM 持续确认]** 正式 MVP 开发、真实敏感恢复和真实 AI 辅助仍保持阻塞；不得用本次 Pass 绕过 SP-04-SP-09、技术架构独立评审或 PM 冻结。
4. **[建议 PM 评估风险登记]** 未来应关注“显式依赖边遗漏导致失效漏报”和“Spike 导出包络被误当正式迁移协议”两项风险；本专项会话不修改 `RISK_LOG.md`。

## 14. 角色与关卡自检

- **主责｜技术架构负责人：Pass。** 映射足够小、可复跑、可机器判定；证据不是主观演示；已暴露依赖索引、批量传播和查询复杂度风险；未冻结实现。
- **协审｜数据 / 领域模型负责人：Pass（SP-03 实现语义层）。** 八类指定语义边界清楚，ArtifactVersion 仅作测试映射；身份、版本、来源、确认、失效与导出成立。
- **协审｜AI 信任与安全负责人：Pass（SP-03 包络层）。** AI 身份、对象级 Feedback、六维授权/政策引用、最严格约束、撤回失效和审计最小化成立；运行时执行仍待 SP-04/05。
- **协审｜产品架构负责人：Pass。** 验证直接服务可信恢复与一个候选下一步，没有扩成知识图谱、企业审计台或正式产品开发。
- **协审｜体验设计负责人：Pass（信息语义层）。** 证据入口、缺口、`stale/invalid/review_required/evidence_unavailable`、暂无可靠建议和部分导出均可转成用户可理解状态；具体 UI 未设计。

| 关卡 | 自检结论 | 边界 |
|---|---|---|
| Gate 2 数据与来源 | **Pass（SP-03 候选实现层）** | 身份、Source/Artifact/版本、证据链、Feedback、失效、基础导出通过；正式 Schema/迁移未冻结 |
| Gate 3 AI 权限与信任 | **Pass（SP-03 包络与继承层）** | AI/用户身份、授权引用、最严格限制、撤回与待复核通过；运行时判定和物理清理待 SP-04/05 |
| Gate 4 技术可行性 | **Pass（SP-03 候选实现层）** | 22 项本地断言通过，无图数据库等重型依赖；规模、同步、生产架构仍未通过 |

本任务不是技术架构冻结或 MVP 开发准入，不需要本专项会话启动独立评审；未来技术架构冻结与进入正式开发必须另行独立评审和 PM 确认。

## 15. 证据包路径清单

- `lifeos/spikes/SP-03/run_spike.py`：可复跑本地验证脚本
- `lifeos/spikes/SP-03/results.json`：结构化运行摘要
- `lifeos/spikes/SP-03/test_matrix.csv`：22 项测试矩阵
- `lifeos/spikes/SP-03/SP-03_report.md`：技术证据摘要
- `lifeos/spikes/SP-03/environment.md`：环境与范围边界
- `lifeos/spikes/SP-03/fixture_manifest.md`：夹具与两条主链说明
- `lifeos/spikes/SP-03/mapping_options.md`：候选映射比较
- `lifeos/spikes/SP-03/evidence_chain_samples.json`：一次查询证据包、约束继承与 Link 样例
- `lifeos/spikes/SP-03/dependency_invalidation_report.md`：依赖闭包、漏报/误报与确认历史结果
- `lifeos/spikes/SP-03/export_reimport_report.md`：部分导出与重导入不复活结果
- `lifeos/spikes/SP-03/audit_privacy_check.md`：日志 / AuditEntry 隐私检查
- `lifeos/spikes/SP-03/raw_logs/`：结构化运行、失效、导出重导入与隐私日志
- `lifeos/spikes/SP-03/cleanup.md`：精确清理与可重建说明
