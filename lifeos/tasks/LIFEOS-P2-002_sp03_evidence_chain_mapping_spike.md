# LIFEOS-P2-002｜SP-03 来源、版本、Derivation 与证据链最小映射技术 Spike

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

- 任务 ID：LIFEOS-P2-002
- 任务名称：SP-03 来源、版本、Derivation 与证据链最小映射技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵、样例 JSON 和脚本可放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-001` 已完成 SP-01 本地可靠落盘、离线捕获、备份恢复技术 Spike，并通过 PM 验收。用户已确认采纳 SP-01 Pass 结论，允许后续 Spike 继承其最小可靠存储语义：

- commit 后才允许返回“已保存”；
- 用户原文与版本追加保存；
- 幂等重试可解释；
- 离线本地保存与待同步状态分离；
- 墓碑 / 撤回在恢复与旧数据重放前优先生效。

但 SP-01 只证明“内容能可靠存下来”。LifeOS 还必须证明：

> 保存后的内容能否被可信引用、派生、确认、失效，并能从恢复包或 AI 候选反查到精确来源、版本、权限、处理位置和用户反馈。

这就是 SP-03 的目标。

本任务允许在 `lifeos/spikes/SP-03/` 下创建最小本地验证代码、夹具、样例 JSON、日志和证据包，但不能把实验代码视为产品代码、数据库 Schema 冻结或技术架构冻结。

## 目标

本任务完成后，要回答：

1. LifeOS 能否用最小映射表达 `Source / Artifact / Version / Derivation / Feedback / Authorization / AuditEntry / Link` 的关键语义？
2. 任一恢复包、AI 整理、AI 候选或用户确认对象，能否反查到精确输入版本、来源、授权、处理目的、处理位置、生成版本和反馈历史？
3. 用户原文、外部来源、AI Derivation、AI 未确认候选、用户确认内容是否保持身份分离，且不存在可静默覆盖的共享权威字段？
4. 文件修改、删除、来源不可达、断开来源、撤权、Feedback 撤回时，依赖的 Derivation / Link / 用户确认状态是否能正确进入 stale、invalid 或 review_required？
5. Project、文件夹、标签、双链或候选 Link 是否会错误扩权？
6. 删除墓碑、撤回和旧导入包重放时，已删除或已撤回内容是否会复活？
7. 当前候选映射是否足以作为 SP-02 Obsidian 只读接入的证据链包络输入？

## 范围

本任务必须覆盖：

- 最小语义映射验证：
  - `Source`
  - `Artifact`
  - `ArtifactVersion`（测试映射语义，不新增冻结对象）
  - `Derivation`
  - `Feedback`
  - `Authorization`
  - `AuditEntry`
  - `Link`
- 至少两条主证据链：
  1. Obsidian / 外部来源版本 → 恢复包 / 候选下一步 → 用户编辑确认 → 完成 Feedback。
  2. 外部材料 → Decision 证据 → 输入更新 / 删除 / 撤权 → 证据失效 / 待复核。
- 内容身份验证：
  - 用户原文
  - 外部来源原文
  - 外部主张
  - AI 整理 / 恢复包
  - AI 未确认候选
  - 用户确认对象
  - Feedback 追加历史
- 状态与失效验证：
  - valid
  - stale
  - invalid
  - review_required
  - evidence_unavailable
  - active / inactive
  - tombstoned
- 权限与约束验证：
  - 六维 Authorization 最小样本：主体、范围、动作、目的、位置、时效。
  - Project 不扩权。
  - 多输入 Derivation 继承最严格限制。
  - 合法子集生成新 Derivation，并披露缺口。
  - 无合法输入时拒绝生成，而不是编造建议。
- 导出 / 重导入最小验证：
  - 导出包能区分身份、版本、来源、用户确认和部分失败。
  - 重导入前优先应用墓碑 / 撤回。
  - 已删除内容、已撤回活跃状态不得复活。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能。
- 不修改 Stitch。
- 不连接真实 Obsidian Vault。
- 不处理真实敏感数据。
- 不调用真实模型、云服务或第三方 API。
- 不验证真实模型质量。
- 不实现完整知识图谱。
- 不冻结数据库 Schema、API、事件流、图数据库、技术栈或技术架构。
- 不实现 SP-02 Obsidian 只读扫描。
- 不实现 SP-04 运行时授权、SP-05 全链路物理清理、SP-06 同步一致性、SP-08 正式导出迁移协议。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-03/` 下创建和修改验证脚本、夹具、样例 JSON、测试矩阵、日志、环境说明和清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确的任务目录或系统临时目录，且不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话：

- 修改 `PROJECT_CONTEXT.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md` 等 PM 文件。
- 修改现有非 Spike 项目代码或无关文件。
- 删除、覆盖或移动用户真实数据。
- 使用破坏性命令清理宽泛目录。

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

## 角色检查点

主责角色必须重点回答：

- 最小映射是否能证明证据链、依赖失效、权限继承和导出 / 重导入不复活？
- 验证是否足够小，能在有限时间内复跑？
- 证据是否可复核，而不是只给主观结论？
- 候选映射是否暴露出未来 Schema、图关系、索引或查询复杂度风险？
- 是否避免把 Spike 映射当成正式数据库 Schema 或架构冻结？

协审角色必须重点检查：

- 数据 / 领域模型负责人：Source、Artifact、Version、Derivation、Feedback、Authorization、AuditEntry、Link 的语义边界是否清楚。
- AI 信任与安全负责人：AI 输出身份、证据、用户确认、纠正、撤回、权限继承和失效是否成立。
- 产品架构负责人：Spike 是否服务“5 分钟上下文恢复与下一步确认”，没有扩成完整知识图谱或企业审计平台。
- 体验设计负责人：输出是否能转成用户可理解的证据入口、缺口、待复核、无可靠建议和导出状态。

## 核心问题

请重点回答：

1. 你采用了什么最小验证映射？为什么足以验证 SP-03，而不是冻结 Schema？
2. 夹具如何生成？是否包含两条主证据链、跨 Project、多输入冲突、合法子集、Feedback 撤回、部分导出和旧包重导入？
3. 任一关键输出如何反查完整证据包？
4. 用户原文、外部来源、AI Derivation、AI 候选、用户确认对象是否存在身份混淆或共享权威字段？
5. 修改、删除、不可达、断源、撤权和 Feedback 撤回如何触发依赖闭包？漏报和误报如何统计？
6. Project、文件夹、标签、双链和候选 Link 是否存在扩权？
7. 多输入 Derivation 如何继承最严格限制？合法子集如何形成新 Derivation 并披露缺口？
8. 用户确认但唯一证据失效时，如何保留历史并退出自动建议依据？
9. 导出 / 重导入如何证明身份不丢失、墓碑 / 撤回优先、不复活？
10. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
11. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 任一关键输出可在一次调试查询中返回完整证据包：精确输入版本、Source、Authorization / 政策版本、目的、位置 / 主体、工作流 / 模型版本、生成时间、输出身份、状态和 Feedback。
- 用户原文、外部来源、AI Derivation、AI 候选与用户确认对象不存在共享的可静默覆盖权威字段。
- 重要 Link 有来源、确认状态和有效状态。
- 所有预期受影响 Derivation 漏报为 0。
- 误报必须可列举解释，不得产生无法解释的全库失效。
- Project、文件夹、标签、双链和 Link 扩权为 0。
- 多输入限制继承成立；合法子集变化必须生成新 Derivation 并显示缺口。
- 用户确认历史在证据失效时不被删除，而是进入待复核 / 退出自动建议依据。
- 删除墓碑 / 撤回在导出重导入或旧包重放前优先生效，复活数为 0。
- AuditEntry、日志和样例不得包含真实敏感原文或可还原真实数据。

## 建议测试矩阵

至少包含：

1. 完整证据链回查。
2. AI 候选 → 用户确认 → 完成 Feedback。
3. AI 候选 → 用户编辑确认，保留 AI 版本与用户版本。
4. AI 候选 → 拒绝 / 纠正 / 撤回 Feedback。
5. 输入版本修改导致旧 Derivation stale / invalid。
6. 来源删除 / 不可达导致 evidence_unavailable / review_required。
7. 断开来源导致依赖输出失效或待复核。
8. 撤权导致相关 Derivation 退出活跃使用。
9. 多输入不同授权，继承最严格限制。
10. 合法子集生成新 Derivation 并披露缺口。
11. Project Link 不扩权。
12. 文件夹 / 标签 / 双链不自动成为 Project 或授权范围。
13. 用户已确认但唯一证据失效，历史保留、自动依据退出。
14. 部分导出披露成功 / 排除 / 失败范围。
15. 重导入先应用墓碑 / 撤回，不复活。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-03/`

证据包至少包括：

- `SP-03_report.md`
- `test_matrix.csv` 或等价测试矩阵文件
- `environment.md`
- `fixture_manifest.md`
- `evidence_chain_samples.json`
- `dependency_invalidation_report.md`
- `export_reimport_report.md`
- `audit_privacy_check.md`
- `raw_logs/`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 验证实现与最小映射说明
3. 测试夹具说明
4. 证据链回查验证
5. 身份分离与用户确认验证
6. 依赖失效与权限继承验证
7. Project / 外部结构不扩权验证
8. 导出 / 重导入与不复活验证
9. 测试矩阵与验收断言结果
10. 日志与隐私检查
11. 结论：Pass / Pass with Conditions / Fail / Blocked
12. 降级建议与后续影响
13. 需要 PM / 用户确认的问题
14. 角色与关卡自检
15. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 原始日志、测试矩阵、脚本、样例 JSON 和夹具说明可放证据包，不在正文无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-03/`。
- 会话回复中提供完整交付物路径和证据包路径。
- 已实际运行本地验证，不只是写计划。
- 覆盖至少两条主证据链。
- 覆盖建议测试矩阵中所有 P0 场景，或明确说明无法覆盖的阻塞原因。
- 明确给出 Pass / Pass with Conditions / Fail / Blocked 结论。
- 明确说明 Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不处理真实敏感数据、不连接真实 Vault、不调用云 / 第三方 / 真实模型、不修改 Stitch、不冻结 Schema / API / 技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 只能使用合成、脱敏或可丢弃数据。
- 不得使用 LifeOS 作为真实重要数据的唯一副本。
- 不得读取、复制、移动、删除用户真实文档、Obsidian Vault 或敏感文件。
- 不得调用外部模型、云服务、第三方 API 或付费资源。
- 不得修改 PM 文件。
- 不得把本地验证代码迁入正式产品目录。
- 不得把候选映射、表结构、查询方式、图关系或脚本写成 Schema / API / 技术架构冻结结论。
- 不得以“显示效果正确”替代真实证据链、身份分离、权限继承和依赖失效验证。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要、完整交付物路径、证据包路径和是否需要 PM 决策。
