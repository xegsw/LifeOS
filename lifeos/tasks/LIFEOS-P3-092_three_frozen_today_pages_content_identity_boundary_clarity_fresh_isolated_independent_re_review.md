# LIFEOS-P3-092｜三张冻结今日页内容身份与处理边界可见性全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在本地工作区、P3-091 工程资产的只读副本、只读 Evidence 与固定非敏感合成文本中进行防御性 UI 审查与独立验证。

不涉及外部目标、真实数据、真实凭据、未授权访问、网络、持久化、数据获取或安全控制规避。权限、撤回、恢复、失败与反例术语仅用于验证合成 fail-closed UI。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-092
- 优先级：P0
- 任务类型：P3-091 的全新隔离独立安全／体验复评。
- 范围：仅核验 P3-091 当前 hash 的三张纯本地、无持久化、无网络 `file:` 页面中内容身份与处理边界可见性；不连接 P3-079 运行时、SQLite、CLI 或任何真实能力。
- 允许工作：只读 hash 核验、task-local 干净副本、独立静态／Chrome 动态验证、独立 Evidence、Review 与交付物文案。
- 不允许：工程整改、修改 P3-091／P3-089／P3-090／历史 Evidence／项目账本、风险关闭／重开、冻结、基线恢复、Stage 4 或任何真实能力。
- 状态：`Accepted / Pass / Awaiting User Adoption`。
- 执行授权：用户将本任务卡路径发送至**新建隔离 Codex 独立评审会话**即授权执行。
- 单独确认例外：None。

## Agent、模型与隔离

- 推荐 Agent：Codex，新建隔离独立安全／体验评审会话；不得复用 P3-091 工程执行会话、PM 会话或此前独立评审会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 允许降级：None；后备模型：`gpt-5.5` + `xhigh`（仅首选不可用，必须记录原因）。
- 禁止降级条件：全任务；动态／视觉 Evidence、身份／边界语义、关闭态、P0/P1 与独立性不得降级。
- 必须回报：P0/P1、hash／Evidence 冲突、独立性不足、范围扩大、任何真实能力触达或 Chrome 预检失败。

## 最小读取包与直接输入

- 必读：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`。
- 定向补读：P3-091 任务卡、交付物、PM Review、PM Evidence attempt-2 Manifest、工程 Evidence 初始与 attempt-2 Manifest；`PM_OPERATING_MODEL.md` 的受控能力包／交付前自检／`file:` 预检章节，`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入只读：`lifeos/engineering/LIFEOS-P3-091/` 及上述文件；不得导入、调用或复制 P3-091 runner／测试作为独立验证主实现。
- 首份会话报告记录任务卡路径、会话类型与接收时间。

## 必须独立核查

1. 在 task-local 干净副本复算 P3-091 五项源文件及指定 P3-089／P3-090／P3-091 历史 Evidence hash，记录 before／after 与副本路径。
2. 新写独立 runner，核验三页均清晰、可访问地标识固定非敏感演示文本、用户确认、合成系统状态、AI 未启用和未发生真实处理；并反查禁止网络、持久化、文件／DB、SQLite、Vault、Tauri/IPC、导出、同步、模型调用或第三方依赖。
3. 仅使用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 在新标签页直接加载 task-local `file:` 入口；先记录 URL、时间、加载结果与副本 hash。不得使用 In-app Browser、Browser-control、HTTP、网络、CDP、命令行浏览器或策略绕过替代。
4. 对空输入、确认／重复确认、默认拒绝、grant／revoke、精确 `CONFIRM`、失败清理、刷新、**关闭重开**、实际 **Tab／Enter**、三页导航、宽／窄屏，分别进行独立动态验证。
5. 对每一项动作使用 `UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或等价 JSON：必须保存前置状态、实际操作、可观察结果、结构化结果 ID、视觉／日志路径与 SHA-256。刷新不得替代关闭重开；AX／静态可聚焦不得替代实际 Tab／Enter。闭环 runner 必须在提交前验证无缺行。
6. 保存独立 runner、逐项结果、操作日志、视觉记录、hash、Manifest、复跑说明及验收标准→步骤→Evidence 矩阵；明确 P0/P1/P2/Unknown/Not Implemented。

## 交付与判定

- 交付物：`lifeos/deliverables/LIFEOS-P3-092_three_frozen_today_pages_content_identity_boundary_clarity_fresh_isolated_independent_re_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-092/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-092/evidence/MANIFEST.md`
- 结论仅可为 Pass / Pass with Conditions / Rework / Blocked。即使 Pass，P3-091 仍 Not Frozen；不得自动关闭风险、恢复基线、冻结资产、启用真实能力或进入 Stage 4。

## D-0374 窄 Rework 补充（已获用户确认）

- 原因：初次 P3-092 的新隔离会话未暴露任务卡指定的 Chrome Computer Use 控制接口，13 项动态闭环诚实标记为 Not Implemented；这不是 P3-091 工程缺陷。
- 仅允许：在**具备 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 正常控制能力的全新隔离 Codex 独立评审会话**，以新的 task-local 只读副本完整重跑本任务第 1–6 项。
- 必须保存：Chrome 预检与 13 项动态动作的逐项闭环表、结构化结果、视觉／日志 Evidence、逐文件 SHA-256、独立 runner、Manifest 与复跑说明。
- 输出必须写入：`lifeos/reviews/LIFEOS-P3-092/rework/attempt-2/`；不得覆盖初次 Blocked Review／Evidence。
- 不得修改 P3-091 工程、P3-089／P3-090、历史 Evidence、风险、冻结、基线、阶段或项目账本；不得启用真实能力或使用替代／绕过浏览器路径。
