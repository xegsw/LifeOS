# LIFEOS-P3-088｜三张冻结今日页响应式与键盘可达性全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限指定本地工作区、P3-087 工程资产的只读副本、只读 Evidence 与固定非敏感文本，用于防御性本地 UI 审查、独立体验／安全验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、离线、失败、反例与边界术语只用于验证本项目内部的防御性体验，不授权扩大范围。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-088
- 优先级：P0
- 任务类型：独立评审型任务／P3-087 受控能力包的全新隔离独立复评。
- 是否为受控能力包：Yes；本任务是该能力包所需的一次独立复评，不得拆成新的微型评审。
- 能力包边界：仅 P3-087 三张冻结今日页在纯本地、无持久化、无网络 `file:` UI 范围内的响应式布局、键盘可达性、焦点可见性与受控状态交互。
- 包内允许工作：只读 hash 核验、干净临时副本、独立静态与动态验证、独立 Evidence、独立 Review 与交付物文案。
- 包内整改授权：无工程整改权；发现问题只记录 Rework／Blocked，回流 P3-087 原能力包整改。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实 DB／路径／文件／Vault／Tauri/IPC／网络／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 状态：`Ready / Task-card Delivery Authorizes Execution`。
- 执行授权：用户将本任务卡路径发送至**新建隔离 Codex 独立评审会话**即授权执行。
- 单独确认例外：None；本卡不授权任何真实能力或外部访问。

## Agent、模型与会话

- 推荐执行 Agent：Codex，新建隔离独立安全／体验评审会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 选择理由：P0 独立复评必须与 P3-087 工程执行和 PM 验收隔离，且需形成新的 runner、可重放 Chrome Evidence 与严格完成定义判断。
- 允许降级：None。
- 禁止降级条件：全任务；P0 独立性、动态／视觉 Evidence、可访问性、关闭态与完成定义不得降级。
- 必须升级／回报：发现 P0/P1、hash／Evidence 冲突、独立性不足、范围扩大、任何网络／持久化／文件／Tauri/IPC 触达，或无法维持任务边界时立即停止并回报 PM。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时；必须记录原因）。
- 是否允许修改工程文件／项目账本：No / No。

## 会话隔离与最小读取包

- 必须新建会话：Yes；不得复用 P3-087 工程执行会话、P3-087 PM 验收会话、P3-085／086 的任何执行或评审会话。
- 隔离理由：避免执行侧、既有独立评审和 PM 动态抽查形成自证循环。
- 新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、P3-087 任务卡／交付物／PM Review／PM Evidence Manifest／工程 Evidence Manifest、`PM_OPERATING_MODEL.md` 的受控能力包、独立评审与本地 `file:` 预检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入：`lifeos/engineering/LIFEOS-P3-087/` 与其 `evidence/`、`lifeos/reviews/LIFEOS-P3-087_pm_review.md`、`lifeos/reviews/LIFEOS-P3-087/pm_evidence/`；P3-085／086 的 Manifest 仅用于历史只读 hash 核对。
- 可复用既有读取结果：无（新会话）。首份会话报告必须记录任务卡路径、会话类型与接收时间。

## 必须独立核查的范围

1. 在 task-local 干净临时副本中复算 P3-087 的三个 HTML、`app.js`、`styles.css` hash，并核对 P3-085 五项历史只读 hash；记录 before／after hash 与副本路径。
2. 新写独立静态 runner；不得导入、调用或复制 P3-087 执行侧 runner／测试，或 P3-085／086 的 runner／测试作为主验证实现。
3. 先进行 Chrome 预检：只用 Computer Use 的 `@oai/sky` 正常控制新 Google Chrome 标签页（`com.google.Chrome`），直接以 `file:` 打开 task-local 副本的 `default-recovery.html`；记录 URL、时间、加载结果和副本 hash。预检成功后才执行动态矩阵。In-app Browser／Browser-control 的拒绝仅可记录为工具限制；只有 Chrome 正常操作连续两次都无法加载同一副本、两次均完整记录且未使用 HTTP、网络、CDP、命令行浏览器或安全策略绕过时，才可提出候选 Blocked。
4. 仅用固定非敏感文本，动态核验：Tab 到跳过链接和主导航、Enter 导航三页、焦点可见性及合理顺序；宽屏与窄屏／缩放下的状态边界和可读性；默认恢复空输入拒绝、显式确认、重复确认、模拟失败清理与披露；无可靠建议的两条受控人工路径；受限／离线与 AI 未启用；刷新和关闭重开后的会话清除。
5. 反查关闭态：无远程 URL、HTTP 服务、网络、浏览器持久化、文件 API、真实文件／DB、Tauri/IPC、Vault、导出、同步、模型调用或第三方依赖。
6. 形成独立 Evidence：runner 源码、逐项结构化结果、操作日志、视觉记录、hash、Manifest、复跑说明与“验收标准 → 反例／步骤 → Evidence”矩阵。
7. 明确 P0、P1、P2、Unknown、Not Implemented 数量。出现 P0/P1、明确合同违反、Evidence 冲突／不可复核、独立性不足、范围扩大、关闭态失效或影响完成定义的 Unknown／Not Implemented，结论必须为 Rework 或 Blocked。

## 禁止事项

不得修改 P3-087、P3-085、P3-086、冻结设计、历史 Review／Evidence 或任何账本；不得输入真实用户文本或触达真实个人文件／DB；不得启用持久化、网络、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不得关闭／重开风险、恢复工程基线、冻结资产或进入 Stage 4。

## 交付、验收与回复

- 交付物：`lifeos/deliverables/LIFEOS-P3-088_three_frozen_today_pages_responsive_accessibility_fresh_isolated_independent_re_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-088/independent_review.md`。
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-088/evidence/MANIFEST.md`。
- 本地预检：默认执行；不可用时记录 Skipped，但不得阻断。
- 结论仅可为 Pass / Pass with Conditions / Rework / Blocked。即使 Pass，P3-087 仍 Not Frozen；不得自动关闭风险、恢复工程基线、冻结资产、启用真实能力或进入 Stage 4。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和是否需要 PM 决策。
