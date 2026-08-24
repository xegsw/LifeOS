# LIFEOS-P3-090｜三张冻结今日页合成生命周期 UI 全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-089 工程资产的只读副本、只读 Evidence 与固定非敏感合成文本中进行防御性本地 UI 审查、独立体验／安全验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、拒绝、撤回、恢复、失败与反例术语只用于验证本项目内部的合成 fail-closed UI 状态，不授权扩大范围。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-090
- 优先级：P0
- 任务类型：独立评审型任务／P3-089 受控能力包的一次全新隔离独立复评。
- 能力包边界：仅 P3-089 三张纯本地、无持久化、无网络 `file:` 页面的页面内存合成生命周期 UI；不接入 P3-079 Python、SQLite、CLI 或任何真实能力。
- 包内允许工作：只读 hash 核验、干净临时副本、独立静态与动态验证、独立 Evidence、Review 与交付物文案。
- 包内整改授权：无工程整改权；发现问题回流 P3-089 原能力包，结论为 Rework／Blocked。
- 必须独立处理：风险关闭／重开、工程基线恢复、任何冻结、真实 DB／路径／文件／Vault／Tauri/IPC／网络／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 状态：`Accepted / PM Pass / Awaiting User Adoption`。
- 执行授权：用户将本任务卡路径发送至**新建隔离 Codex 独立评审会话**即授权执行。
- 单独确认例外：None；本卡不授权任何真实能力或外部访问。

## Agent、模型与会话

- 推荐 Agent：Codex，新建隔离独立安全／体验评审会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 选择理由：P0 独立复评需与 P3-089 工程执行及 PM 验收隔离，并需形成新的 runner、Chrome 动态 Evidence 与严格边界判断。
- 允许降级：None。
- 禁止降级条件：全任务；P0 独立性、合成／真实能力边界、动态／视觉 Evidence 与关闭态不得降级。
- 必须升级／回报：P0/P1、hash／Evidence 冲突、独立性不足、范围扩大、任何持久化／文件／DB／网络／Tauri/IPC 触达，或无法保持任务边界。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，必须记录原因）。
- 是否允许修改工程文件／项目账本：No / No。

## 会话隔离与最小读取包

- 必须新建会话：Yes；不得复用 P3-089 工程执行会话、P3-089 PM 验收会话、P3-079／080 或 P3-087／088 的任何执行或评审会话。
- 新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、P3-089 任务卡／交付物／PM Review／PM Evidence Manifest／工程 Evidence Manifest、P3-079 交付物与 P3-080 PM Review、`PM_OPERATING_MODEL.md` 的受控能力包、独立评审与本地 `file:` 预检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入均只读：`lifeos/engineering/LIFEOS-P3-089/` 与其 Evidence、上述 Review／Manifest；不得导入、调用或复制 P3-089／079／087 runner／测试作为主验证实现。
- 首份会话报告必须记录任务卡路径、会话类型与接收时间。

## 必须独立核查

1. 在 task-local 干净副本中复算 P3-089 三个 HTML、`app.js`、`styles.css` hash，并复算 P3-079、P3-087、P3-088 指定历史只读 hash；记录 before／after 与副本路径。
2. 新写 task-local 独立静态 runner；不得导入、调用或复制执行侧 runner／测试作为主验证实现。
3. 只用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 控制新标签页，先直接加载 task-local `file:` 入口并记录 URL、时间、加载结果和副本 hash；预检成功后才开始动态矩阵。In-app Browser／Browser-control 拒绝仅为工具限制；只有 Chrome 正常操作连续两次加载同一副本失败且完整记录、未使用 HTTP／网络／CDP／命令行浏览器或策略绕过时，才可提出候选 Blocked。
4. 仅用固定非敏感文本，独立验证：空输入拒绝、明确／重复确认、默认拒绝、明确 grant、恢复预览、精确 `CONFIRM`、重复回执、撤回／拒绝回到 fail-closed、模拟失败清理与披露、刷新／关闭重开清除、三页导航、skip link、Tab／Enter、焦点可见性及窄屏／缩放。
5. 反查不得把合成状态写成真实保存／授权／恢复，也不得存在网络、持久化、文件 API、真实文件／DB／SQLite、Vault、Tauri/IPC、导出、同步、模型调用或第三方依赖。
6. 保存独立 runner、逐项结果、操作日志、视觉记录、hash、Manifest、复跑说明及“验收标准→反例／步骤→Evidence”矩阵；明确 P0/P1/P2/Unknown/Not Implemented 数量。

## 禁止事项与交付

不得修改 P3-089、P3-079、P3-087、P3-088、冻结设计、历史 Review／Evidence 或任何账本；不得输入真实用户文本或触达真实个人文件／DB；不得启用持久化、网络、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不得关闭／重开风险、恢复工程基线、冻结资产或进入 Stage 4。

- 交付物：`lifeos/deliverables/LIFEOS-P3-090_three_frozen_today_pages_synthetic_lifecycle_ui_fresh_isolated_independent_re_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-090/independent_review.md`。
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-090/evidence/MANIFEST.md`。
- 本地预检默认执行；不可用时记录 Skipped，不得阻断。
- 结论仅可为 Pass / Pass with Conditions / Rework / Blocked。即使 Pass，P3-089 仍 Not Frozen；不得自动关闭风险、恢复基线、冻结资产、启用真实能力或进入 Stage 4。

## D-0365 窄 Rework 补充（已获用户确认）

- 原因：PM 验收发现初次 P3-090 提交缺少独立 Chrome 视觉记录，且 Manifest 没有逐文件可复算 SHA-256；这不是 P3-089 工程缺陷。
- 仅允许：在**全新隔离 Codex 独立评审会话**中，以 task-local 干净副本重跑本任务第 1–6 项；工程资产严格只读。
- 必须写入新路径：`lifeos/reviews/LIFEOS-P3-090/rework/attempt-2/`；不得覆盖 `lifeos/reviews/LIFEOS-P3-090/evidence/` 的初次提交。
- 必须补齐：每项动态步骤的结构化结果；Chrome 预检、宽屏／窄屏或缩放、键盘／焦点、刷新或关闭重开、失败清理等视觉记录；runner、结果、日志、每个 Evidence 文件的 SHA-256、Manifest 与复跑说明。
- 不得修改：P3-089 工程、P3-079／087／088 历史资产、风险、冻结、基线、阶段或项目账本；不得新增真实能力。
