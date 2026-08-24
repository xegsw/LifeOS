# LIFEOS-P1-016｜核心信息架构与端到端流程

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

- 任务 ID：LIFEOS-P1-016
- 任务名称：核心信息架构与端到端流程
- 优先级：P0
- 任务类型：研究型任务
- 建议篇幅：3000-6000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P1-015` 已通过 PM 验收，并被用户确认采纳为后续共同输入。当前项目已明确：

- 自用版 MVP 最小切片围绕“捕获 → 保存 → 来源 / Project → 找回 / 今日恢复 → AI 候选 → 用户反馈 → 导出 / 删除底线”。
- 正式 MVP 开发仍为 `Blocked / Not Allowed`。
- 技术架构、数据库 Schema、API、前后端框架仍未冻结。
- 外部用户验证线暂停。

在进入 Obsidian 条件需求和 SP-01 / SP-03 技术验证前，需要先把自用版最小切片的核心信息架构和端到端流程画清楚：用户从哪里捕获、在哪里看到保存回执、如何选择 Project、如何恢复上下文、如何识别 AI 候选与证据、如何反馈，以及删除 / 撤回 / 导出的入口在哪里。

本任务不是完整 PRD，不是视觉稿，也不是工程实现方案；它是后续 Obsidian 需求、SP-01 / SP-03 夹具、技术任务卡和未来界面设计的共同流程输入。

## 目标

本任务完成后，要回答：

1. 自用版最小切片需要哪些一级信息区 / 页面 / 功能入口？
2. 捕获、保存、Project 选择、今日恢复、AI 候选、用户反馈、四类命令、导出 / 删除如何串成端到端流程？
3. 每个关键流程中，用户原文、外部来源、AI 派生 / 建议、用户确认内容分别在哪里展示和转换？
4. 正常态、未选 Project、无可靠建议、离线、权限受限、来源不可达、保存失败、撤回 / 删除中等状态如何进入流程？
5. 哪些信息架构和流程结论可以作为 SP-01 / SP-03 的夹具与验收输入？

## 范围

本任务必须覆盖：

- 自用版最小切片的一层信息架构：只覆盖必须支撑最小闭环的区域 / 页面 / 入口。
- 端到端主流程：
  - 捕获文本 / 链接 / 文件或来源指针
  - 本地耐久保存与保存回执
  - 手动归入 / 选择 Project
  - 今日 / Project 恢复
  - 无可靠建议
  - AI 未确认候选下一步
  - 用户确认 / 编辑 / 拒绝 / 纠正 / 完成 / 延期 / 撤回反馈
  - 基础导出
  - 删除 / 撤回处理入口
- 异常与边界状态：
  - 未选择 Project
  - 离线
  - 权限受限
  - 来源不可达
  - 保存失败 / 保存中
  - AI 证据不足
  - 删除 / 撤回活跃阻断中
  - 导出失败或部分导出
- 内容身份规则：
  - 用户原文
  - 外部来源
  - AI 派生 / 整理
  - AI 推断 / 建议 / 未确认候选
  - 用户确认内容
- 领域语义映射：说明流程中如何涉及 `Artifact / Source / Project / Derivation / Feedback / Authorization / AuditEntry / Link`，但不得设计数据库表。
- 后续任务输入：明确 P1-017 Obsidian 条件需求、SP-01、SP-03 需要从本任务继承哪些流程、状态和验收案例。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不修改 Stitch。
- 不制作高保真视觉稿、组件样式、颜色、布局像素或动效。
- 不重写首页 / 今日页 PRD 或冻结原型。
- 不设计完整产品信息架构，只做自用版最小切片。
- 不写 Obsidian 接入详细需求。
- 不设计数据库 Schema、API、事件流或服务架构。
- 不执行技术 Spike。
- 不调用真实模型、云服务或付费资源。
- 不处理真实敏感数据。
- 不进入正式 MVP 开发。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/reviews/LIFEOS-P1-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-014_self_use_mvp_dev_readiness_roadmap.md`
- `lifeos/reviews/LIFEOS-P1-014_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`

## 角色检查点

主责角色必须重点回答：

- 用户是否能从捕获一路走到恢复、候选、反馈和导出 / 删除入口？
- 首页 / 今日页是否仍然是“从哪里继续”的恢复入口，而不是全局任务墙或后台工作台？
- 异常状态是否在流程上可理解，而不是只靠技术错误提示？

协审角色必须重点检查：

- 产品架构负责人：流程是否服务个人终身外脑、V1 第一场景和 P1-015 最小切片，不扩成完整工作台。
- 数据 / 领域模型负责人：流程是否保留用户原文、Source / Artifact、Derivation、Feedback、Authorization、AuditEntry、Link 的语义边界。
- AI 信任与安全负责人：AI 候选是否始终未确认，用户确认与反馈是否明确，权限、撤回、删除是否有入口和状态。
- 技术架构负责人：流程是否能转化为 SP-01 / SP-03 夹具、验收用例和后续任务卡，不依赖未冻结架构。

## 核心问题

请重点回答：

1. 自用版最小切片的信息架构应包含哪些一级区域、页面或入口？
2. 捕获 → 保存 → Project → 恢复 → AI 候选 → Feedback → 导出 / 删除的端到端主流程是什么？
3. 每个流程节点需要显示哪些内容身份和状态？
4. 异常 / 降级状态如何进入用户可理解的流程？
5. 四类命令 `revoke_processing / disconnect_source / delete_content / retract_feedback` 在 IA 中出现在哪里、最低要表达什么？
6. 哪些流程和状态应成为 SP-01 / SP-03 的共用夹具与验收输入？
7. 哪些结论必须回到 PM / 用户确认？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`

请输出的文件内容包括：

1. 任务边界与结论摘要
2. 自用版最小切片信息架构
3. 端到端主流程
4. 关键异常 / 降级流程
5. 内容身份与状态规则
6. 四类命令入口与最低流程
7. 领域语义映射
8. SP-01 / SP-03 输入清单
9. 后续任务依赖
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
- 明确给出最小切片信息架构。
- 明确给出端到端主流程和关键异常流程。
- 明确区分用户原文、外部来源、AI 派生、AI 建议 / 未确认候选、用户确认内容。
- 明确四类命令的入口与最低流程。
- 明确给出 SP-01 / SP-03 输入清单。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 1、Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不写代码、不修改 Stitch、不冻结技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不联系真实外部用户。
- 不处理真实敏感数据。
- 不改变 LifeOS 产品定位。
- 不擅自冻结技术架构、数据库 Schema、API、V1 范围、首页 / 今日页 PRD 或数据模型。
- 不把 IA / 流程设计写成正式 MVP 开发准入。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
