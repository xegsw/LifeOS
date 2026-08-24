# LIFEOS-P1-017｜Obsidian 只读接入条件需求

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

- 任务 ID：LIFEOS-P1-017
- 任务名称：Obsidian 只读接入条件需求
- 优先级：P0
- 任务类型：研究型任务
- 建议篇幅：3000-6000 字
- 主责角色：数据 / 领域模型负责人
- 协审角色：产品架构负责人、AI 信任与安全负责人、技术架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS V1 已确认 Obsidian Vault 可作为优先支持的本地文件型来源，但采用**只读接入、来源追踪、AI 派生不写回原文**的策略。这里的“只读”不是说 LifeOS 不能产生新知识，而是说：

> LifeOS 可以读取 Obsidian 作为外部来源，但 V1 不应静默修改、重命名、删除、重排或自动写回用户的 Obsidian Vault 原文件。

用户已进一步确认：采纳该方向，但 P1-017 必须补充说明 LifeOS 自己的新知识如何处理。

因此，本任务要明确：

- Obsidian 作为只读来源时，LifeOS 最低读什么、怎么标记来源、怎么处理更新和不可达状态。
- LifeOS 新捕获、新整理、AI 派生、用户确认、反馈等新知识写入 LifeOS 自己的写入层，而不是默认写回 Obsidian 原文件。
- LifeOS 是否以及如何提供 Obsidian 兼容 Markdown 导出；导出必须是用户明确触发的动作，不能冒充同步或自动写回。
- 哪些内容属于条件性需求，必须等 SP-02 / SP-03 等技术 Spike 证明可行后，才能进入正式开发承诺。

本任务仍是 Stage 1 定义线任务，不是实现任务。正式 MVP 开发仍为 `Blocked / Not Allowed`。

## 目标

本任务完成后，要回答：

1. “Obsidian 只读接入”在 LifeOS V1 中到底是什么意思？
2. LifeOS 读取 Obsidian Vault 时，最低支持哪些内容类型、元数据、关系和变更状态？
3. LifeOS 新知识、AI 派生、用户确认内容、Feedback 写在哪里，如何与 Obsidian 来源建立关系？
4. 用户想把 LifeOS 新内容带回 Obsidian 时，V1 应支持什么级别的 Markdown 导出，哪些写回 / 同步能力不进入 V1？
5. Obsidian 接入如何继承 Source / Artifact 分离、Project 不扩权、六维 Authorization、四类命令和证据链规则？
6. 哪些要求应转化为 SP-02 / SP-03 的验收输入？

## 范围

本任务必须覆盖：

- 只读接入定义：
  - 不自动修改 Obsidian 原文件。
  - 不自动创建、删除、重命名 Vault 文件。
  - 不静默写入 frontmatter、标签、双链、标题、正文或附件。
  - 不做双向同步或后台写回。
  - 若提出“导出到 Vault 内”的可能性，必须将其定义为用户明确触发的一次性导出 / 保存动作，而不是来源同步。
- Obsidian 最低读取对象：
  - Markdown 文件正文。
  - 文件路径、文件名、修改时间、大小、hash 等最低来源元数据。
  - frontmatter、标签、标题、内部链接、外部链接、嵌入、附件指针的最低处理策略。
  - 目录 / 文件排除规则。
  - 文件移动、重命名、删除、重复、编码异常、附件不可达等状态。
- LifeOS 新知识写入层：
  - LifeOS 内部捕获的文本、链接、文件 / 来源指针。
  - 用户在 LifeOS 中确认的 Action / Decision / Project Link。
  - AI 整理、摘要、恢复包、候选下一步等 Derivation。
  - 用户确认、编辑、拒绝、纠正、完成、延期、撤回等 Feedback。
  - 这些内容如何与 Obsidian Source / Artifact 建立 Link，但不污染 Obsidian 原文。
- 内容身份与来源追踪：
  - 用户原文。
  - Obsidian 外部来源内容。
  - LifeOS 内部新记录。
  - AI 派生 / 整理。
  - AI 建议 / 未确认候选。
  - 用户确认内容。
- 权限与处理边界：
  - 连接 Vault 不等于允许云同步或第三方模型处理。
  - 本地读取 / 索引、AI 派生、云同步、第三方模型处理必须分层授权。
  - Project 归属不扩权。
  - 多输入 Derivation 必须继承最严格限制。
  - 权限撤回、断开来源、删除内容、撤回反馈的最低效果。
- 用户可见体验：
  - 连接 Vault。
  - 选择 / 排除目录。
  - 查看来源身份。
  - 查看索引 / 更新 / 不可达状态。
  - 从恢复包或建议回到 Obsidian 来源证据。
  - 对 LifeOS 新内容导出为 Obsidian 兼容 Markdown。
- SP 输入：
  - SP-02：Obsidian Vault 只读接入与来源身份。
  - SP-03：来源、版本、Derivation 与证据链最小映射。
  - 必要时指出对 SP-04 / SP-05 / SP-08 的影响。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不修改 Stitch。
- 不设计 Obsidian 插件。
- 不设计双向同步。
- 不自动写回 Obsidian。
- 不设计完整数据库 Schema、API、事件流或服务架构。
- 不执行 SP-02 / SP-03 技术 Spike。
- 不连接真实 Obsidian Vault。
- 不读取、处理或要求用户提供真实敏感笔记。
- 不冻结技术架构。
- 不进入正式 MVP 开发。
- 不改变 LifeOS 产品定位或 V1 范围。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/reviews/LIFEOS-P1-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/reviews/LIFEOS-P1-016_pm_review.md`

## 角色检查点

主责角色必须重点回答：

- Obsidian `Source` 与 LifeOS `Artifact` 如何分离？
- 一个 Obsidian 文件、文件版本、附件、链接、frontmatter、标签和目录选择在 LifeOS 中分别应表达什么语义？
- LifeOS 新写入内容、AI 派生和用户确认内容如何保存，不污染 Obsidian 原文？
- 文件移动、删除、重命名、来源不可达、权限撤回后，来源、派生和证据链如何变化？

协审角色必须重点检查：

- 产品架构负责人：方案是否服务个人终身外脑和 V1 第一场景，而不是把 LifeOS 做成 Obsidian 插件或同步工具。
- AI 信任与安全负责人：AI 是否只在授权范围内读取和派生；AI 输出、用户确认和 Obsidian 原文是否明确分离。
- 技术架构负责人：要求是否能转化为 SP-02 / SP-03 验收任务，不提前冻结具体实现方案。
- 体验设计负责人：用户是否能理解只读、索引、来源不可达、导出、断开来源、撤回处理许可和删除 LifeOS 副本之间的区别。

## 核心问题

请重点回答：

1. “只读接入”允许什么、禁止什么？
2. Obsidian Vault 的哪些内容进入 LifeOS 的来源层，最低要保留哪些来源元数据？
3. LifeOS 新知识写在哪里，如何与 Obsidian 来源建立关系？
4. AI 派生、AI 建议、用户确认内容和 Feedback 如何处理，如何避免写回污染？
5. 用户如何把 LifeOS 内容导出为 Obsidian 兼容 Markdown？导出与写回 / 同步的边界是什么？
6. Project 与 Obsidian 文件夹、标签、双链之间是什么关系？为什么 Project 不应自动等于文件夹、标签或授权范围？
7. 目录排除、权限撤回、断开来源、删除 LifeOS 内容、来源不可达、文件移动 / 重命名 / 删除时，用户可见状态和系统最低行为是什么？
8. 哪些需求是 Must / Should / Not Now？
9. 哪些要求必须进入 SP-02 / SP-03 的夹具、断言和验收案例？
10. 哪些结论需要 PM / 用户确认？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`

请输出的文件内容包括：

1. 任务边界与结论摘要
2. “Obsidian 只读接入”的定义
3. Obsidian Source / Artifact 最小语义映射
4. LifeOS 新知识写入层设计
5. 内容身份、AI 派生和用户确认规则
6. 权限、Project 与处理边界
7. 用户可见流程与状态
8. Markdown 导出与非写回边界
9. 异常、撤回、断开、删除和来源不可达处理
10. Must / Should / Not Now 条件需求清单
11. SP-02 / SP-03 输入清单
12. 风险、开放问题与需要 PM / 用户确认的事项
13. 角色与关卡自检

篇幅控制：

- 研究型任务建议 3000-6000 字。
- 超出当前任务范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 会话回复中提供交付物路径。
- 明确说明“只读接入”允许什么、禁止什么。
- 明确说明 LifeOS 新知识写在哪里，以及如何与 Obsidian 来源关联。
- 明确区分 Obsidian 原文、LifeOS 原始记录、AI 派生、AI 建议 / 候选、用户确认内容。
- 明确 Markdown 导出与自动写回 / 双向同步的边界。
- 明确 Project、文件夹、标签、双链、授权范围之间的关系。
- 明确目录排除、来源不可达、文件变更、断开来源、撤回处理许可、删除 LifeOS 内容的最低规则。
- 明确 Must / Should / Not Now。
- 明确给出 SP-02 / SP-03 输入清单。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 1、Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不写代码、不修改 Stitch、不连接真实 Vault、不冻结技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不读取或处理真实敏感 Obsidian 内容。
- 不把 LifeOS 定义成 Obsidian 插件、双向同步工具或知识库管理器。
- 不把 Obsidian 文件夹、标签或双链自动解释为 LifeOS Project、授权范围或用户确认事实。
- 不允许 AI 静默改写用户原文或 Obsidian 原文。
- 不允许把导出能力写成后台同步或自动写回。
- 不擅自冻结技术架构、数据库 Schema、API、V1 范围或正式开发准入。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
