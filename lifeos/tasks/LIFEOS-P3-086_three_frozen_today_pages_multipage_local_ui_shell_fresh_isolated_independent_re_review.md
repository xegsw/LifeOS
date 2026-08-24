# LIFEOS-P3-086｜三张冻结今日页多页本地 UI 壳全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-085 当前工程资产的只读副本、只读 Evidence 与固定非敏感文本中进行防御性本地 UI 审查、独立体验／安全验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、离线、失败与边界术语只用于验证本项目内部防御性体验，不授权扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-086
- 优先级：P0
- 任务类型：独立评审型任务／P3-085 受控能力包的全新隔离独立复评
- 是否为受控能力包：Yes
- 能力包边界：仅 P3-085 三张冻结今日页的多页、纯本地、无持久化、无网络 UI 壳；本任务即完成该能力包所需的一次独立复评，不得拆为新的微型评审任务。
- 包内允许工作：只读 hash 核验、干净临时副本、独立静态与动态验证、Evidence 整理、独立 Review 与交付物文案。
- 包内整改授权：无工程整改权；发现问题仅报告 Rework／Blocked，回流 P3-085 能力包处理。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实 DB／真实路径／真实文件／Vault／Tauri/IPC／网络／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 是否适用 P3 Engineering Fast Lane：No

## Agent、模型与执行授权

- 推荐执行 Agent：Codex
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`
- 选择理由：P0 独立复评需要与 P3-085 执行和 PM 验收会话隔离，并需形成独立 runner、可重放动态 Evidence 和严格完成定义判断。
- 允许降级模型：None
- 禁止降级条件：全任务；P0 独立性、Evidence 完整性和本地浏览器动态验证不得降级。
- 必须升级条件：发现 P0/P1、hash/Evidence 冲突、独立性不足、任何网络／持久化／文件／Tauri/IPC 触达，或无法维持任务边界时，停止并回报 PM。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时；必须记录原因）
- 是否需要后续独立评审：No；本任务就是 P3-085 所需的唯一一次新鲜独立复评。若结论为 Rework／Blocked，由 PM 决定后续路径。
- 是否允许修改工程文件／项目账本：No / No
- 主责角色：独立安全／体验评审
- 协审角色：产品架构、AI 信任与安全、技术架构
- 必须通过的关卡：Gate 1／3／4 的有限 UI 边界；Gate 2、Gate 5 不作运行时批准。
- 状态：`Ready / Task-card Delivery Authorizes Execution`
- 执行授权方式：用户将本任务卡路径投递至**新建隔离 Codex 独立评审会话**即授权执行。
- 投递前仍需单独用户确认的例外：None；本任务不授权任何真实能力或外部访问。
- 授权证据：首份会话报告记录任务卡路径、会话类型与接收时间。

## 会话路由与最小读取包

- 必须新建会话：Yes。不得复用 P3-085 工程执行会话、P3-085 PM 验收会话或 P3-082／083／084 任一执行、评审会话。
- 会话类型：Codex 独立安全／体验评审。
- 隔离理由：必须避免执行侧和 PM 动态复验的自证循环。
- 新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、P3-085 交付物、P3-085 PM Review、P3-085 PM Evidence Manifest、P3-085 工程 Evidence Manifest、`PM_OPERATING_MODEL.md` 的独立评审与受控能力包章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入：`lifeos/engineering/LIFEOS-P3-085/`、`lifeos/engineering/LIFEOS-P3-085/evidence/`、`lifeos/reviews/LIFEOS-P3-085_pm_review.md`、`lifeos/reviews/LIFEOS-P3-085/pm_evidence/`、P3-082／084 的工程 Manifest（仅用于历史只读 hash 核对）。
- 可复用既有读取结果：无（新会话）。

## 必须独立核查的范围

1. 复算 P3-085 三个 HTML、`app.js`、`styles.css` 与历史 P3-082 只读资产 hash；使用 task-local 干净临时副本，记录 before／after hash 与副本路径。
2. 新写 task-local 独立静态 runner；不得导入、调用或复制 P3-085 执行侧或 P3-082／084 的 runner／测试作为主验证实现。
3. **先做浏览器预检，再做完整动态矩阵：**使用 Computer Use 的 `@oai/sky` 正常控制新 Google Chrome 标签页（`com.google.Chrome`），直接以 `file:` 打开临时副本的 `default-recovery.html`；在 Evidence 记录入口 URL、时间、加载结果与副本 hash。预检成功后才执行完整动态验证。In-app Browser 或 Browser-control 表面的 `file:` 拒绝只能记录为工具限制，不得作为 Blocked 依据。只有 Chrome 正常操作连续两次均不能加载相同副本、两次结果均有记录且未采用 HTTP、网络、CDP、命令行浏览器或安全策略绕过时，才可提出候选 Blocked。
4. 只用固定非敏感文本，动态验证三个独立页面和显式导航；默认恢复的空文本拒绝、显式确认、重复确认、模拟失败披露；无可靠建议的两条人工路径；权限受限／离线与 AI 未启用；刷新和关闭重开后会话文本／记录清除。
5. 核对关闭态：无网络或远程 URL、HTTP 服务、浏览器持久化、文件 API、真实文件／DB、Tauri/IPC、Vault、导出、同步、模型调用或第三方依赖。
6. 形成独立 Evidence：runner 源码、逐项结构化结果、逐步操作日志、可复查视觉记录、hash、Manifest、复跑说明，以及“验收标准 → 反例／步骤 → Evidence”矩阵。
7. 明确 P0、P1、P2、Unknown、Not Implemented 数量。出现 P0/P1、明确合同违反、Evidence 冲突／不可复核、独立性不足、范围扩大、关闭态失效或影响完成定义的 Unknown／Not Implemented，结论必须为 Rework 或 Blocked。

## 禁止事项

不得修改 P3-085、P3-082、P3-084、冻结设计、历史 Review／Evidence 或任何账本；不得输入实际用户文本、触达真实个人文件／DB；不得启用持久化、网络、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不得关闭／重开风险、恢复工程基线、冻结资产或进入 Stage 4。

## 交付、验收与回复

- 交付物：`lifeos/deliverables/LIFEOS-P3-086_three_frozen_today_pages_multipage_local_ui_shell_fresh_isolated_independent_re_review.md`
- 原独立 Review／Evidence：只读保留在 `lifeos/reviews/LIFEOS-P3-086/`。
- 本轮重跑独立 Review：`lifeos/reviews/LIFEOS-P3-086/rework/attempt-3/independent_review.md`
- 本轮重跑 Evidence：`lifeos/reviews/LIFEOS-P3-086/rework/attempt-3/evidence/MANIFEST.md`
- 本地预检：默认执行；不可用时记录 Skipped，但不得阻断。
- 结论只能为 Pass / Pass with Conditions / Rework / Blocked。即使 Pass，P3-085 仍 Not Frozen；不得自动关闭风险、恢复工程基线、冻结资产、启用真实能力或进入 Stage 4。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和是否需要 PM 决策。
