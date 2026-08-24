# LIFEOS-P3-084｜三张冻结今日页 `file:` 动态 Evidence 补齐与全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-082 当前 hash 的只读工程资产、只读 Evidence、固定非敏感文本与新建临时副本中，进行防御性本地 UI 审查、独立体验／安全验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、离线、失败与边界术语只用于验证本项目内部防御性体验，不授权扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-084
- 优先级：P0
- 任务类型：评审型任务／P3-082 同能力包的 Evidence 补齐后全新隔离独立复评
- 是否为受控能力包：Yes
- 能力包边界：仅 P3-082 三张冻结今日页的纯本地、无持久化、无网络 UI 前置验证；本任务自身即完成新的独立复评，不得将其拆成再一个微型评审任务。
- 包内允许工作：只读 hash 核验、干净临时副本、独立静态／动态验证、Evidence 整理与独立 Review／交付物文案。
- 包内整改授权：无工程整改权；发现问题只报告 Rework／Blocked，不修改 P3-082。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实 DB／路径／Vault／Tauri/IPC／文件导出／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 建议篇幅：2000–4000 字
- 是否适用 P3 Engineering Fast Lane：No

## Agent、模型与授权

- 推荐执行 Agent：Codex
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`
- 选择理由：需要新隔离会话、独立浏览器动态验证、严格 Evidence 和 P0 完成定义判断。
- 允许降级模型：None
- 禁止降级条件：本任务所有范围；P0 独立复评、Evidence 完整性与浏览器动态验证不适用降级。
- 必须升级条件：发现 P0/P1、hash 或 Evidence 冲突、独立性不足、任何网络／持久化／文件／Tauri/IPC 触达，或无法维持任务边界时，停止并回报 PM。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时；须记录原因）
- 是否需要后续独立评审：No；本任务就是 P3-082 所需的新的全新隔离独立复评。若本任务 Rework／Blocked，由 PM 决定后续路径。
- 是否允许修改工程文件／项目账本：No / No
- 主责角色：独立安全／体验评审
- 协审角色：产品架构、AI 信任与安全、技术架构
- 必须通过的关卡：Gate 1／3／4 的有限 UI 边界；Gate 2、Gate 5 不作运行时批准。
- 状态：Ready / Task-card Delivery Authorizes Execution
- 执行授权方式：用户将本任务卡路径投递至**新建隔离 Codex 独立评审会话**即授权执行。
- 投递前仍需单独用户确认的例外：None；任务卡不授权任何真实能力或外部访问。
- 授权证据记录：首份会话报告记录任务卡路径、会话类型与接收时间。

## 会话路由与读取

- 必须新建会话：Yes。不得复用 P3-082 工程执行、P3-082 PM 验收、P3-083 独立评审、P3-079／080／081 的任何会话。
- 会话类型：Codex 独立安全／体验评审。
- 隔离理由：P3-083 的动态 Evidence 未完成；本次必须独立于所有既有执行与评审上下文，避免以先前 PM 动态复跑自证。
- 必须重新读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、P3-082 交付物／PM Review／PM Evidence、P3-083 的交付物／独立 Review／PM Review／Evidence、P3-082 工程 Evidence Manifest、`PM_OPERATING_MODEL.md` 的独立评审与受控能力包章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 可复用既有读取结果：无（新会话）。

## 范围与禁止事项

必须：

1. 复算 P3-082 `index.html`、`app.js`、`styles.css` hash；在 task-local 干净临时副本中验证，副本路径与 before／after hash 写入 Evidence。
2. 新写独立静态 runner；不得导入、调用或复制 P3-082、P3-083 任一 runner／测试作为主验证实现。
3. 使用**新的图形化本地浏览器会话**，仅以 `file:` 打开该临时副本。若需要使用浏览器／计算机操作工具，遵循其正常技能说明；不得使用原始 CDP、命令行浏览器、HTTP 服务或绕过 URL 安全策略。
4. 仅用固定非敏感文本，动态验证：三态切换；非空文本的显式确认；空文本拒绝；模拟失败不展示记录；无建议两条路径；权限受限／离线与 AI 未启用；刷新和关闭重开后文本／记录／状态均清除；视觉层级不误称真实持久化或 AI 功能。
5. 形成独立 Evidence：runner 源码、逐项结构化结果、逐步操作日志、视觉核验记录（含可复查截图或所用 GUI 工具的截图引用）、hash、Manifest、复跑说明与“验收标准 → 反例／步骤 → Evidence”矩阵。
6. 核对禁止能力关闭态：无网络／远程 URL、HTTP 服务、浏览器持久化、文件 API、Tauri/IPC、Vault、导出、同步、模型调用、真实数据／文件／DB。
7. 清楚报告 P0、P1、P2、Unknown、Not Implemented 数量。动态验证若再被阻断，必须 Blocked；不得把静态通过写成端到端 Pass。

禁止：修改 P3-082、冻结原型、历史 Review／Evidence 或任何账本；输入用户实际文本；触达真实个人文件／DB；启用持久化、网络、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；关闭／重开风险、恢复基线、冻结资产或进入 Stage 4。

## 交付、验收与回复

- 交付物：`lifeos/deliverables/LIFEOS-P3-084_three_frozen_today_pages_file_dynamic_evidence_fresh_isolated_independent_re_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-084/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-084/evidence/MANIFEST.md`
- 本地预检：默认执行；不可用时记录 Skipped，但不得阻断。
- 结论只能为 Pass / Pass with Conditions / Rework / Blocked。发现 P0/P1、明确合同违反、Evidence 冲突／不可复核、独立性不足、范围扩大、关闭态失效或影响完成定义的 Unknown／Not Implemented，必须 Rework 或 Blocked。
- 即使 Pass，P3-082 仍为 Accepted but Not Frozen；不得自动关闭风险、恢复工程基线、冻结资产、启用真实能力或进入 Stage 4。任务完成后使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 简短汇报。
