# LIFEOS-P1-018｜首批技术 Spike 任务卡：SP-01 / SP-02 / SP-03

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

- 任务 ID：LIFEOS-P1-018
- 任务名称：首批技术 Spike 任务卡：SP-01 / SP-02 / SP-03
- 优先级：P0
- 任务类型：研究型任务
- 建议篇幅：3000-6000 字
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS 当前已完成并由 PM 验收：

- P1-015：自用版 MVP 最小切片准入清单。
- P1-016：核心信息架构与端到端流程。
- P1-017：Obsidian 只读接入条件需求。

正式 MVP 开发仍为 `Blocked / Not Allowed`。进入真实开发前，必须先把关键技术风险拆成可执行、可验收、可失败、可降级的技术 Spike。

本任务只负责把首批技术 Spike 做成任务卡，不执行 Spike、不写代码、不连接真实 Vault、不处理真实敏感数据、不冻结技术架构。

首批 Spike 范围：

1. **SP-01：本地可靠落盘、离线捕获、备份恢复。**
2. **SP-02：Obsidian Vault 只读接入与来源身份。**
3. **SP-03：来源、版本、Derivation 与证据链最小映射。**

这三个 Spike 是自用版能否安全进入真实数据与后续开发的地基：

- SP-01 决定 LifeOS 能否可信地保存用户原始记录。
- SP-02 决定 Obsidian 只读来源是否能在技术上守住边界。
- SP-03 决定恢复包、AI 候选和证据链是否能被追溯、失效和解释。

## 目标

本任务完成后，要回答：

1. SP-01 / SP-02 / SP-03 各自要验证什么，不验证什么？
2. 每个 Spike 的输入夹具、测试数据、状态、异常和断言是什么？
3. 每个 Spike 的 Pass / Pass with Conditions / Fail / 降级标准是什么？
4. 每个 Spike 完成后应产出哪些证据文件？
5. 哪些能力在 Spike 通过前不得进入真实自用数据或正式开发？
6. 三个 Spike 之间如何复用夹具，如何避免各自发明对象身份、保存语义或证据链规则？
7. 哪些结论需要 PM / 用户确认？

## 范围

本任务必须覆盖：

- 三张独立 Spike 任务卡：
  - SP-01：本地可靠落盘、离线捕获、备份恢复。
  - SP-02：Obsidian Vault 只读接入与来源身份。
  - SP-03：来源、版本、Derivation 与证据链最小映射。
- 每张 Spike 任务卡至少包含：
  - Spike 编号与名称。
  - 背景与要验证的风险。
  - 目标。
  - 范围。
  - 非范围。
  - 输入材料。
  - 测试夹具 / 假数据要求。
  - 必测场景。
  - 异常 / 失败场景。
  - 验收断言。
  - Pass / Pass with Conditions / Fail 标准。
  - 允许的降级方案。
  - 交付物路径建议。
  - 不允许触碰的真实数据或外部系统。
- 共用夹具策略：
  - 复用 P1-016 的端到端流程和 SP-01/SP-03 输入。
  - 复用 P1-017 的 Obsidian Vault 确定性夹具和证据链断言。
  - 明确用户原文、外部来源、AI Derivation、AI 未确认候选、用户确认内容、Feedback、Authorization、AuditEntry、Link 的统一身份口径。
- 阶段准入规则：
  - SP-01 通过前，不允许把 LifeOS 作为重要真实数据的唯一副本。
  - SP-02 通过前，不允许承诺 Obsidian V1 正式接入。
  - SP-03 通过前，不允许承诺可信恢复包、AI 候选证据链或真实 AI 辅助恢复。
  - SP-04 通过前，不允许真实 Vault 内容进入云 / 第三方模型处理。
  - 任一 Spike 未通过时，应明确降级为手工导入、来源指针、无 AI 或移出 V1 的条件。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不执行 SP-01 / SP-02 / SP-03。
- 不连接真实 Obsidian Vault。
- 不读取、复制、索引或处理真实敏感笔记。
- 不调用真实模型、云服务或第三方 API。
- 不修改 Stitch。
- 不创建外部账号、部署服务或使用付费资源。
- 不设计完整数据库 Schema、API、事件流或服务架构。
- 不冻结技术架构。
- 不冻结 Obsidian 正式实现承诺。
- 不进入正式 MVP 开发。
- 不重写 P1-015 / P1-016 / P1-017。

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
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/reviews/LIFEOS-P1-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/reviews/LIFEOS-P1-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- `lifeos/reviews/LIFEOS-P1-017_pm_review.md`

## 角色检查点

主责角色必须重点回答：

- 每个 Spike 是否足够小，能在有限时间内验证关键风险？
- 每个 Spike 是否有明确的 Pass / Fail / 降级标准？
- 每个 Spike 是否能产出可复核证据，而不是只产出主观结论？
- 是否避免提前冻结数据库、框架、同步架构或模型供应商？

协审角色必须重点检查：

- 数据 / 领域模型负责人：夹具和断言是否保留 Source、Artifact、Version、Derivation、Feedback、Authorization、AuditEntry、Link 的语义边界。
- AI 信任与安全负责人：SP-03 是否能验证 AI 输出身份、证据链、确认、撤回和权限继承；SP-02 是否防止 Obsidian 内容越权进入 AI/云/第三方处理。
- 产品架构负责人：Spike 是否服务自用版最小闭环和 V1 第一场景，未变成过度技术研究。
- 体验设计负责人：Spike 结果是否能转化为用户可理解的保存、来源、不可达、证据缺口、导出和撤回状态。

## 核心问题

请重点回答：

1. SP-01 的最小可验证技术任务卡是什么？
2. SP-02 的最小可验证技术任务卡是什么？
3. SP-03 的最小可验证技术任务卡是什么？
4. 三个 Spike 应共用哪些夹具、对象身份、状态和验收断言？
5. 每个 Spike 通过前，哪些真实数据或产品承诺必须禁止？
6. 每个 Spike 失败后，允许哪些降级路径？
7. 三个 Spike 的执行顺序应如何建议？是否可并行？
8. 哪些结论必须回到 PM / 用户确认？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-018_first_technical_spike_task_cards.md`

请输出的文件内容包括：

1. 任务边界与结论摘要
2. 首批 Spike 总体策略
3. 共用夹具与统一语义口径
4. SP-01 技术 Spike 任务卡
5. SP-02 技术 Spike 任务卡
6. SP-03 技术 Spike 任务卡
7. 三个 Spike 的依赖、顺序与可并行性
8. 阶段准入与禁止承诺清单
9. 失败降级与后续决策路径
10. 需要 PM / 用户确认的问题
11. 角色与关卡自检

篇幅控制：

- 研究型任务建议 3000-6000 字。
- 超出当前任务范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 会话回复中提供交付物路径。
- 分别产出 SP-01、SP-02、SP-03 的可执行任务卡。
- 每张任务卡均包含目标、范围、非范围、夹具、必测场景、异常场景、验收断言、Pass / Fail 标准、降级路径和交付物建议。
- 明确共用夹具和统一语义口径。
- 明确 Spike 通过前的禁止承诺和真实数据限制。
- 明确三项 Spike 的建议执行顺序和可并行性。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不写代码、不执行 Spike、不连接真实 Vault、不处理真实敏感数据、不修改 Stitch、不冻结技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不执行真实技术验证。
- 不连接真实 Obsidian Vault。
- 不读取或处理真实敏感数据。
- 不调用真实模型、云服务或第三方 API。
- 不创建外部账号、部署服务或使用付费资源。
- 不把技术 Spike 任务卡写成正式开发任务。
- 不把候选技术栈写成冻结结论。
- 不擅自解除 MVP 开发阻塞。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
