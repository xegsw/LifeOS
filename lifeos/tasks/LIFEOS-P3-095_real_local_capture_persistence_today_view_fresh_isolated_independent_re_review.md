# LIFEOS-P3-095｜真实本地捕获、持久化与今日页展示全新隔离独立复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅对 P3-094 当前已通过 PM 验收的工程 hash 进行防御性、只读、全新隔离独立复评；允许在独立 task-local 临时目录新建 SQLite 和内部 HTML，但只使用评审侧自建的固定非敏感测试文本。

不得读取或使用用户真实文本、既有个人文件／数据库、真实用户路径、凭据或外部目标；不得启用网络、HTTP、云／第三方、Tauri/IPC、Vault、同步、多设备、文件导出、L3 或外部用户。权限、拒绝、失败、清理与反例术语仅用于验证本项目本地 fail-closed 边界，不授权扩大范围或规避安全控制。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-095
- 优先级：P0
- 任务类型：P3-094 当前 hash 的全新隔离独立安全／数据边界／体验复评。
- 被评审范围：`lifeos/engineering/LIFEOS-P3-094/` 当前源码，以及 attempt-1／2／3、PM Review 与 PM Evidence 的只读事实链。
- 允许工作：只读 hash 核验；独立 task-local 临时 SQLite／HTML；新写独立 runner；Google Chrome 本地 `file:` 动态验证；独立 Review、Evidence 与交付物。
- 禁止工作：修改 P3-094 工程、runner、交付物、历史 Evidence／Review／Manifest 或项目账本；使用／复制／调用 P3-094 的执行侧 runner 作为独立验证；风险关闭／重开、冻结、基线恢复或阶段切换。
- 状态：`Ready / Task-card Delivery Authorizes Execution`。
- 执行授权：用户将本任务卡路径投递至**新建隔离 Codex 独立评审会话**即授权上述固定非敏感 task-local 范围；无需额外“授权执行”口令。
- 单独确认例外：任何用户真实文本、既有文件／DB、网络、Tauri/IPC、导出或其他禁止能力均不在本授权内，必须停止并回报 PM。

## Agent、模型与隔离

- 推荐 Agent：Codex，新建隔离独立评审会话；不得复用 P3-094 任一工程执行会话、PM 会话或此前独立复评会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 允许降级：None；后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，必须记录原因）。
- 禁止降级条件：全任务；真实本地数据边界、清理、动态 Evidence、独立性、P0/P1 或 hash 冲突不得降级。
- 必须停止并回报：任何真实用户内容、既有个人文件／DB、外部访问、网络、无法清理的残留、P0/P1、Evidence 冲突、hash 变化或独立性不足。

## 最小读取包与直接输入

- 必读：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`。
- 定向补读：P3-094 任务卡；attempt-3 交付物；P3-094 PM Review 与 PM Evidence attempt-3 Manifest；P3-094 attempt-1／2／3 Evidence Manifest、事件记录和最终结构化结果；`PM_OPERATING_MODEL.md` 的真实数据、P0、受控能力包、独立复评与 `file:` 预检章节；`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入只读：`lifeos/engineering/LIFEOS-P3-094/`、`lifeos/deliverables/LIFEOS-P3-094_rework_attempt_3_dynamic_evidence.md`、`lifeos/reviews/LIFEOS-P3-094_pm_review.md` 及其 PM Evidence。
- 首份会话报告必须记录任务卡路径、会话类型、接收时间、实际模型和固定非敏感 task-local 授权范围。

## 必须独立核查

1. 复算 P3-094 当前源码、attempt-1／2／3 Manifest 与 PM Evidence hash，记录评审前后结果；不得覆盖任何被评审资产。
2. 新写独立 runner，不导入、调用或复制 P3-094 的执行侧测试／runner；可直接调用被评审的最小公开运行时接口，以全新固定非敏感输入独立验证。
3. 在新的独立 task-local SQLite 中验证：首次捕获、幂等重复、同键异文拒绝、空输入拒绝、进程重启复读、今日页用户原文身份／时间／本地来源、原子失败无半成品、损坏 DB fail-closed、精确确认清理、清理后不可展示、运行期与系统临时残留为零。
4. 静态反查代码和依赖，确认无网络／HTTP、云／第三方、Tauri/IPC、Vault、导出、同步、多设备、L3、外部用户或既有个人路径访问；用户原文不得进入评审日志、Manifest 或持久 Evidence。
5. 仅使用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky`，在新标签页直接加载评审侧生成的完整 task-local `file:` URL。先预检地址栏保持 `file:`，再独立验证成功今日页、空输入拒绝、关闭标签与运行期清理。不得使用 In-app Browser、HTTP、CDP、命令行浏览器、搜索引擎、网络或规避路径。
6. 每项动态动作必须记录时间、前置状态、实际操作、可观察结果、结构化结果 ID、截图／日志路径与 SHA-256；同一 attempt 不得同时保留 Blocked 与 Pass。若连续两次正常 `file:` 预检失败，诚实记录 Blocked 并停止。
7. 保存独立 runner 源码、逐项结构化结果、操作日志、截图、source／历史 hash、全量非自指 Manifest、复跑说明及“验收标准→独立测试→Evidence”矩阵；明确 P0/P1/P2/Unknown/Not Implemented。
8. 明确区分：P3-095 是否完成、独立工程结论是否通过、P3-094 是否冻结、R-0051 是否关闭、是否允许恢复基线、是否允许进入 Stage 4。

## 交付与判定

- 交付物：`lifeos/deliverables/LIFEOS-P3-095_real_local_capture_persistence_today_view_fresh_isolated_independent_re_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-095/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-095/evidence/MANIFEST.md`
- 结论仅可为 Pass / Pass with Conditions / Rework / Blocked。
- Pass 条件：独立性成立；当前 hash 一致；离线、动态与清理矩阵完整；P0/P1/Unknown/Not Implemented 为零；无真实用户内容、外部访问或禁止能力触达。
- 即使 Pass，P3-094 仍 Not Frozen、R-0051 仍 Open；风险关闭、冻结、基线恢复和 Stage 4 必须另行独立决策与用户确认。
- 会话回复仅输出结论摘要、Review／Evidence 路径与是否需要 PM 决策，不粘贴真实文本、完整日志或长篇历史。
