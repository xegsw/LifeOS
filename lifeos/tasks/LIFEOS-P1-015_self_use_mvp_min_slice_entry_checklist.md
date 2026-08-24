# LIFEOS-P1-015｜自用版 MVP 最小切片准入清单

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

- 任务 ID：LIFEOS-P1-015
- 任务名称：自用版 MVP 最小切片准入清单
- 优先级：P0
- 任务类型：决策型任务
- 建议篇幅：1000-2000 字；如需补充细节，请放入表格或“后续任务建议”，不要扩展成完整 PRD
- 主责角色：PM / 项目总负责人
- 协审角色：产品架构负责人、技术架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、体验设计负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P1-014` 已通过 PM 验收，并被用户确认采纳。当前项目已确认：

- 可以进入自用版开发准备。
- 技术 Spike 条件准入，可开始准备夹具、任务卡和可丢弃验证。
- 正式 Stage 3 MVP 工程实现继续阻塞。
- 外部用户验证线继续暂停，P1-012 / P1-013 作为未来资产保留。

但在进入具体信息架构、Obsidian 接入需求和技术 Spike 之前，需要先形成一份“最小切片准入清单”。它不是完整 PRD，也不是工程实现计划，而是用来约束后续任务：到底做哪条最小自用闭环、哪些能力必须有、哪些可以降级、什么时候允许接入真实数据、怎样算通过、失败时如何降级或退出。

## 目标

本任务完成后，要回答：

1. 自用版 MVP 的最小切片到底包含哪些用户可感知能力？
2. 哪些能力属于 Must，哪些明确 Not Now？
3. 进入自用版开发准备、技术 Spike、真实自用数据启用、正式 MVP 开发各自需要满足什么条件？
4. 每个关键能力的完成定义是什么？
5. 哪些失败必须阻断后续任务，哪些失败可以降级？
6. 下一步 IA、Obsidian 需求和 SP-01/SP-03 应继承哪些准入条件？

## 范围

本任务必须覆盖：

- 自用版 MVP 最小切片一句话定义。
- 最小闭环：捕获 → 保存 → 来源 / Project → 找回 / 今日恢复 → AI 候选 → 用户反馈 → 导出 / 删除底线。
- Must / Should / Not Now 清单，但只覆盖自用版最小切片，不重写 V1 全范围。
- 真实自用数据启用条件，尤其 SP-01 前不得使用重要真实数据。
- 技术 Spike 进入条件与退出条件。
- 正式 MVP 开发仍阻塞的条件说明。
- 每个关键能力的“完成定义 / 验收证据 / 失败降级”。
- 不可降级底线：可靠落盘、原文保护、来源 / 派生身份、对象级确认、默认拒绝授权、撤回 / 删除活跃阻断、基础导出。
- 可降级项：单设备、本地优先、手选 Project、FTS-first、假模型、手工导入 / 来源指针等。
- 后续任务依赖：核心 IA / 端到端流程、Obsidian 只读接入条件需求、SP-01/SP-03 共用夹具与技术验证。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不修改 Stitch。
- 不创建技术架构冻结方案。
- 不冻结数据库 Schema、API、前端框架、后端框架或部署方案。
- 不重写 V1 范围、首页 / 今日页 PRD、核心领域模型或 AI 权限模型。
- 不恢复外部用户验证线。
- 不设计完整信息架构或完整端到端交互。
- 不写 Obsidian 接入详细需求。
- 不执行任何技术 Spike。
- 不进入正式 MVP 开发。
- 不输出完整工程排期、工时估算或发布计划。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/deliverables/LIFEOS-P1-014_self_use_mvp_dev_readiness_roadmap.md`
- `lifeos/reviews/LIFEOS-P1-014_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`

## 角色检查点

主责角色必须重点回答：

- 这份准入清单是否足够让后续任务不再泛化讨论？
- 是否清楚区分自用版开发准备、技术 Spike、真实数据启用和正式 MVP 开发？
- 是否能作为后续 IA、Obsidian、SP-01/SP-03 的共同约束？

协审角色必须重点检查：

- 产品架构负责人：最小切片是否仍服务个人终身外脑、V1 第一场景和“找回上下文 > 下一步/减少遗漏 > 今日重点”。
- 技术架构负责人：完成定义和验收证据是否能转成 Spike / 工程任务，不是抽象愿望。
- 数据 / 领域模型负责人：是否保护用户原文、Source、Artifact、Derivation、Feedback、Authorization、AuditEntry 和 Link 语义。
- AI 信任与安全负责人：AI 候选、用户确认、权限默认拒绝、撤回 / 删除活跃阻断是否被列为底线。
- 体验设计负责人：首页 / 今日页自用闭环是否可感知，不只是底层存储。

## 核心问题

请重点回答：

1. 自用版 MVP 最小切片的一句话定义是什么？
2. Must / Should / Not Now 分别是什么？
3. 自用版开发准备、技术 Spike、真实自用数据启用、正式 MVP 开发四个门槛分别是什么？
4. 每个关键能力的完成定义、验收证据和失败降级是什么？
5. 哪些条件不满足时必须阻断后续任务？
6. 哪些结论必须回到 PM / 用户确认？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`

请输出的文件内容包括：

1. 任务边界与结论摘要
2. 自用版 MVP 最小切片一句话定义
3. Must / Should / Not Now 清单
4. 四类准入门槛：开发准备 / 技术 Spike / 真实数据启用 / 正式 MVP 开发
5. 关键能力准入矩阵：能力、完成定义、验收证据、失败降级、是否阻断
6. 不可降级底线
7. 可接受降级项
8. 后续任务依赖与输入要求
9. PM 推荐决策
10. 需要 PM / 用户确认的问题
11. 角色与关卡自检

篇幅控制：

- 决策型任务建议 1000-2000 字。
- 超出当前任务范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 会话回复中提供交付物路径。
- 明确区分自用版开发准备、技术 Spike、真实数据启用、正式 MVP 开发。
- 给出清晰的 Must / Should / Not Now。
- 给出关键能力准入矩阵，而不是泛泛描述。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 1、Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不写代码、不修改 Stitch、不恢复外部用户验证线、不冻结技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不联系真实外部用户。
- 不处理真实敏感数据。
- 不改变 LifeOS 产品定位。
- 不擅自冻结技术架构、数据库 Schema、API、V1 范围或数据模型。
- 不把“自用版开发准备”或“技术 Spike 条件准入”误写成“正式 MVP 开发已准入”。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
