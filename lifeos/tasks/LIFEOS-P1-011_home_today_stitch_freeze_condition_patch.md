# LIFEOS-P1-011｜首页 / 今日页 Stitch 原型冻结条件补丁

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P1-011
- 任务名称：首页 / 今日页 Stitch 原型冻结条件补丁
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字
- 主责角色：体验设计负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；辅助检查 Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-010` 对 P1-009 三张 `LifeOS 精修版` 完成重新独立评审，结论为 **Pass with Conditions**。

P1-010 已确认三张 `LifeOS 精修版` 具备首页 / 今日页关键原型冻结候选资格，但冻结前必须关闭两个轻量条件：

- C-01：统一受限态的用户确认身份。
- C-02：补强无建议态冻结证据。

本任务只允许关闭 C-01、C-02。完成后，PM 主会话再判断是否可进入首页 / 今日页 Stitch 原型冻结确认。

## 当前 Stitch 原型

https://stitch.withgoogle.com/projects/7778510350051176390

## 允许修改对象

本任务只允许修改 / 取证以下 `LifeOS 精修版` 候选：

- `今日 - 暂无可靠建议 (LifeOS 精修版)`
- `今日 - 权限受限·离线 (LifeOS 精修版)`

默认恢复态原则上不需要修改；如发现默认态因证据一致性必须微调，只能做命名、截图或证据引用层面的最小校准，并在报告中说明原因。

旧三张 P1-007 历史画面不得作为当前冻结候选。

## 目标

本任务完成后，需要：

1. 关闭 C-01：受限态用户确认身份表达清楚。
2. 关闭 C-02：无建议态冻结截图证据完整、可读、可核对。
3. 提供 PM 可核对的截图路径与哈希。
4. 输出条件补丁报告。
5. 明确是否建议 PM 进入首页 / 今日页 Stitch 原型冻结确认。

## 必须关闭的条件

### C-01｜统一受限态的用户确认身份

在 `今日 - 权限受限·离线 (LifeOS 精修版)` 中：

- 将“已确认：……”明确为“你已确认”或等价用户主体表达。
- 在“今日安排”区块或条目层至少一次明确说明其仅包含用户已确认 Action / Commitment。
- 不得把系统状态、AI 判断和用户确认混为一谈。
- 不得新增完整权限设置、审计、清理或技术状态机。

### C-02｜补强无建议态冻结证据

为 `今日 - 暂无可靠建议 (LifeOS 精修版)` 重新取得一张无编辑器外壳、可读尺寸一致的预览截图。

截图必须完整保留：

- 页面标题 / 状态原因。
- “尚未选择 Project”或等价未选状态。
- “暂无可靠建议”或等价无建议说明。
- 最近痕迹身份。
- “不据此生成恢复或建议”或等价跨 Project 护栏说明。

必须记录新截图路径与 SHA-256 哈希。

建议路径：

`lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg`

若需要同步提交受限态修正截图，建议路径：

`lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg`

## 范围

本任务可以做：

- 对受限态进行 C-01 所需的最小文案调整。
- 对无建议态进行 C-02 所需的截图重取。
- 如截图暴露证据不完整，可对无建议态做最小布局 / 文案显性化调整。
- 输出截图路径、哈希和条件关闭说明。

## 非范围

本任务暂时不要做：

- 不修改首页 / 今日页以外的任何页面。
- 不新增页面或状态。
- 不重写首页 / 今日页 PRD。
- 不重写 P1-009 或 P1-010。
- 不重新设计三张候选状态。
- 不做全面返工。
- 不执行真实用户测试。
- 不执行技术 Spike。
- 不写代码。
- 不冻结原型。
- 不进入正式用户验证、Stage 2 或 MVP 开发。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P1-009_home_today_stitch_rework_report.md`
- `lifeos/reviews/LIFEOS-P1-009_pm_review.md`
- `lifeos/reviews/LIFEOS-P1-010_home_today_stitch_re_review.md`
- `lifeos/reviews/LIFEOS-P1-010_pm_review.md`
- 当前 Stitch 原型：https://stitch.withgoogle.com/projects/7778510350051176390
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：体验设计负责人必须重点回答：

- C-01 是否已用最少改动关闭？
- C-02 的新截图是否可读、完整、无编辑器外壳？
- 两项补丁是否没有改变三张候选状态的主叙事和信息结构？
- 是否足以支持 PM 冻结确认？

协审角色必须重点检查：

- 数据 / 领域模型负责人：用户确认内容、Action / Commitment、AI 建议和系统状态是否没有混淆。
- AI 信任与安全负责人：受限态是否没有伪造建议、没有把 AI 或系统判断包装成用户确认。
- 用户研究 / 市场验证负责人：新无建议态截图是否可作为后续 5-10 秒理解测试刺激物。

## 核心问题

请重点回答：

1. C-01 是否关闭？具体改了什么？
2. C-02 是否关闭？新截图路径和哈希是什么？
3. 是否只修改 / 取证了授权范围内的对象？
4. 是否仍保留 P1-010 的 Pass with Conditions 主结论，不引入新问题？
5. 是否建议 PM 进入首页 / 今日页 Stitch 原型冻结确认？

## 交付物

请将完整条件补丁报告保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`

请输出的文件内容包括：

- 任务状态与范围声明
- C-01 关闭说明
- C-02 关闭说明
- 修改 / 取证对象清单
- 截图路径与 SHA-256 哈希
- 证据一致性核对
- 未修改内容和原因
- 风险与待确认问题
- 是否建议 PM 进入原型冻结确认

篇幅控制：

- 本任务为补丁 / 条件整改型任务，建议 1500-3000 字。
- 超出 C-01、C-02 的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 只关闭 C-01、C-02，不做全面返工。
- 受限态用户确认身份清楚。
- 今日安排只包含用户已确认 Action / Commitment 的规则可见。
- 无建议态新截图完整、可读、无编辑器外壳。
- 新截图路径与 SHA-256 哈希已记录。
- 报告、截图、当前候选画面一致。
- 完整补丁报告已保存到指定路径。
- 明确说明是否建议 PM 进入原型冻结确认。
- 不写代码、不修改其他页面、不擅自冻结原型。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不允许改变 LifeOS 产品定位。
- 不允许扩大 V1 范围。
- 不允许修改其他页面。
- 不允许把补丁完成视为自动冻结。
- 不允许进入正式用户验证、Stage 2 或 MVP 开发。
- 不允许用报告文字替代实际画面证据。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整补丁报告正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
