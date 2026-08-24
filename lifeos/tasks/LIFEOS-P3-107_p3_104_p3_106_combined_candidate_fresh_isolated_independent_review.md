# LIFEOS-P3-107｜P3-104 + P3-106 组合候选全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-106 PM Pass，并授权创建本全新隔离独立复评与 ABF。本任务只在项目工作区只读候选和 `/private/tmp` 全新固定非敏感夹具中，防御性验证 Tauri UI/runtime 组合候选的视觉、生命周期、路径、IPC、失败关闭和 Evidence；不访问 retained pilot、真实个人文件／DB、网络、云、第三方、凭据或外部目标，不授权扩大攻击、文件、数据库、shell、process 或网络能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-107`
- 任务名称：P3-104 + P3-106 组合候选全新隔离独立复评
- 优先级：P0
- 任务类型：全新隔离独立工程／安全／视觉／可访问性复评
- 是否为受控能力包：Yes。
- 能力包边界／唯一风险边界：只读评估当前固定 P3-106 高保真 Tauri candidate 与 P3-104 runtime 安全底座的组合一致性；不修复候选。
- 包内允许工作：独立测试设计、固定非敏感临时副本、离线 clean build、实际 app 动态复跑、视觉／响应式／a11y 评估、生命周期／路径反例、Evidence／Manifest 和独立 Review。
- 包内整改授权：仅限 P3-107 自身 runner、Evidence、Review 和交付文案；不得修改 P3-104/P3-105/P3-106、ABF、账本或风险。
- 必须拆分为独立任务：候选修复、runtime／IPC／Cargo／capability／Schema/API 变化、临时路径扩大、真实数据／路径、系统显示设置修改、风险关闭／重开、基线恢复、关键冻结、Stage 4。
- 建议篇幅：独立 Review 2500–4500 字；聊天仅摘要。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 独立评审。
- 推荐理由：需要在不复用工程 runner 的前提下完成真实 Tauri 离线构建、实际 app 动态操作、P0 路径／生命周期反例和 P1 高保真视觉／响应式判断。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 独立性、路径、IPC、失败关闭和 Evidence 真实性与 P1 视觉完成定义必须同时判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选配置不可用时停止并回报 PM。
- 后备模型：None。
- 是否需要后续独立评审：No；本任务自身即全新隔离独立复评，之后仍须 PM 验收和用户采纳。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／安全与数据生命周期评审。
- 协审角色：体验设计、可访问性、技术架构、数据／领域、AI 信任安全。
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查固定非敏感内部理解，不作用户价值或阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理文件：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-107-v1`
- ABF SHA-256：`1088f7bcfa3a014c526ff3e13d5a9fe923053ddbc877938d362a3aa2b038acee`
- ABF 状态：Frozen。
- 本任务正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 生效决策：D-0434。
- 执行授权方式：用户将本任务卡绝对路径投递至符合隔离条件的全新 Codex 独立评审会话，即授权执行 Frozen ABF 范围；仅创建任务卡不执行。
- 投递授权的会话类型与隔离要求：必须全新，不得复用 P3-104/P3-106 工程会话、本 PM 主会话或参与相关 runner／Evidence／PM 验收的会话。
- 本地 `file:` 动态／视觉 Evidence 预检：N/A；本任务必须操作实际 Tauri app，不得以浏览器、file、HTTP 或 DOM mock 替代。
- 本地动态 Evidence 闭环：使用 `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或结构等价 JSON；每个实际动作独立记录前置、操作、可观察结果、结果 ID、截图／日志和 SHA-256。
- 投递前仍需单独用户确认的例外：None，当前固定非敏感独立复评已获授权。任何真实数据／路径、系统显示设置、runtime／IPC／依赖、风险／冻结／阶段变化仍需新的明确确认。
- 授权证据记录：首份会话报告须记录任务卡路径、ABF 路径／ID／hash、会话类型、接收时间、实际模型／推理强度、独立性声明和歧义检查。

## 会话路由

- 是否建议新建会话：Yes。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 独立评审。
- 推荐复用会话：None。
- 会话判断理由：P3-107 必须避免 P3-104/P3-106 实现、测试和 PM 判断的自证循环；先独立冻结测试设计，再反查候选与提交 Evidence。
- 是否需要独立性隔离：Yes，P0 强制。
- 任务完成后是否建议保留会话：Yes，仅用于 P3-107 自身 Evidence／Review 的 ABF 内修正；不得修复候选或承担后续任务。

## 最小启动包与高风险定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. Frozen ABF
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
7. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
8. `lifeos/ACCEPTANCE_GOVERNANCE.md`
9. `lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
10. `lifeos/reviews/LIFEOS-P3-104_pm_review.md`
11. `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md`
12. `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md`
13. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`
14. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md`
15. `lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_rework_1.md`
16. `lifeos/reviews/LIFEOS-P3-106_pm_review.md`
17. `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md`
18. `lifeos/reviews/LIFEOS-P3-106/pm_evidence/rework-1/MANIFEST.md`
19. 三张冻结 Stitch 权威参考图及 `lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：P0、真实 Tauri/IPC、独立复评、两层验收、动态 Evidence、用户确认章节。
- `lifeos/ROLE_MATRIX.md`：PM、独立 QA、体验、架构、数据、AI 信任安全职责。
- `lifeos/STAGE_GATES.md`：Gate 1–5、有限 Stage 3 与 Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0424 至 D-0434。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- P1-004/P1-006 的信息层级、内容身份、Project 选择、渐进披露；P1-009/P1-010/P1-011 的三态视觉意图。

只在发现账本冲突时再定向补读；不要全文重读无关历史。P3-104/P3-106 提交 runner 源码必须等独立测试设计落盘并固定 SHA-256 后才可读取。

## 背景

P3-104 已提供用户采纳的真实 Tauri/runtime 三项窄 IPC 安全底座，但其 UI 不是冻结 Stitch 的高保真实现。P3-105 因路径合同冲突关闭；P3-106 在新 ABF 中保持 P3-104 runtime 字节不变并实现三张高保真页面，经过一次正式 Rework 后获得 PM Pass，现已获用户采纳。

本任务不是继续实现，而是对最终组合候选做预先承诺的独立复评，防止工程与 PM 自证循环，并确认 UI 整合没有破坏 runtime、路径、失败关闭或用户控制不变量。

## 启动前验收依据冻结

- `ABF-P3-107-v1` 已在专项会话启动前 Frozen；只冻结本轮复评依据，不冻结产品需求。
- 执行方在任何复制、构建、测试或 app 操作前必须核对 ABF 路径、ID、hash、固定候选和路径合同。
- 必须使用一次标准质疑窗口；有歧义立即停止回报 PM，不得修改或自行扩展 ABF。
- 新增反例只能映射既有 L1/L2；需要实质修改 ABF 时关闭本任务并新建任务。

## 独立性执行顺序

1. 只依据本任务卡、Frozen ABF、长期 L1 和用户结果设计测试。
2. 在 `lifeos/reviews/LIFEOS-P3-107/evidence/` 写入测试设计、夹具规范、预期断言和时间记录，并固定 SHA-256。
3. 之后才可读取 P3-104/P3-106 runner 源码和结构化提交结果作静态反查；不得导入、执行、复制或改写其 runner。
4. 独立 runner、测试 ID、fixture ID、execution ID 和结果结构不得沿用提交实现。
5. 提交的 18/18、PM Pass 或视觉结论只能作为待核事实，不能替代独立动作。

## 目标

独立回答：当前固定 P3-106 candidate 是否同时保留 P3-104 runtime 安全边界、实现三张冻结 Stitch 高保真用户结果、适应原屏与窄屏，并在固定非敏感 actual-app 生命周期和失败反例下完整 fail-closed。

## 范围

- 独立复算全部固定 candidate、Engineering／PM Manifest 和历史只读 hash。
- 在全新 `/private/tmp` 副本离线 locked clean test/build/bundle。
- 独立验证三项 IPC、capability、runtime／依赖字节继承和全部写路径。
- 独立目视比较三张固定 1280×1024 actual-app Evidence 与权威 Stitch；检查截图嵌入／远程资源欺骗。
- 在原显示环境实际运行三态，验证 1160×768、700×760、滚动、composer、capture、导航和错误披露；不得修改显示设置。
- 独立复跑 saved、repeat、conflict、注入失败、refresh、三页往返、close/reopen。
- 独立复跑 unknown IPC、额外字段、路径／链接／hardlink／文件类型、四类 dangling、content/schema tamper。
- 实际 Tab、Enter、skip、focus、reduced-motion 和未实现控件零副作用。
- Evidence 负门、隐私／网络扫描、历史只读保全和精确清理。

## 非范围

- 不修改任何 P3-104/P3-105/P3-106 文件、配置、runner、Evidence 或交付物。
- 不访问 retained pilot、真实 DB、真实个人文件或任何未列路径。
- 不联网、不安装依赖、不使用 npm／dev server／localhost／远程资源。
- 不改变系统显示缩放；应用必须适应现有显示环境。
- 不新增 IPC、capability、依赖、clear/delete/export、generic path/file/DB、shell/process/network、Vault、模型、同步或外部能力。
- 不关闭／重开风险，不冻结／恢复工程基线、Schema/API、视觉资产或阶段，不进入 Stage 4。

## 允许修改

只允许新建／修改：

- `lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-107/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-107/evidence/`
- Frozen ABF 精确列出的全新 `/private/tmp` 路径，结束时按台账精确清理

不得创建 `lifeos/engineering/LIFEOS-P3-107/`；不得修改项目账本。

## 交付物与 Evidence

- 独立 Review：`lifeos/reviews/LIFEOS-P3-107/independent_review.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-107/evidence/MANIFEST.md`
- 必须包含：独立性声明、先冻结测试设计、16 行 ABF 矩阵、独立 runner、clean build、actual-app 动态／负向／视觉／a11y、hash 与 Manifest 复算、路径 inventory、before/after、隐私／网络扫描、cleanup、final verifier、复跑说明和非自指 Manifest。
- 本地模型预检可因 P0 独立性、真实 Tauri/IPC 与本地文件边界最终判断跳过；若跳过必须在 Review 写明理由。

## 验收结论与回退

- 结论只可为 Pass / Rework / Blocked，不得用条件性措辞掩盖 Unknown 或 Not Implemented。
- Pass：Frozen ABF 14 项不变量、16 行矩阵及全部子项独立通过；P0/P1/P2/Unknown/Not Implemented 全零；候选／历史未变；临时残留 0。
- P3-107 自身 Evidence／runner 缺陷可在 ABF、独立性、候选、目录、能力不变时原任务 Rework，最多两轮。
- 发现组合候选 P0/P1 或完成定义缺口：结论 Rework，返回 PM；评审不得修复。PM 依据 ABF 和剩余预算判断是否让 P3-106 使用其剩余一轮 Rework。
- 独立性不足、固定 hash 不明漂移、离线工具链或正常 app 控制在授权内不可用：Blocked。
- 即使 Pass，也不关闭 R-0040/R-0052、不扩大 R-0051、不冻结、不恢复基线、不进入 Stage 4；必须等待 PM 验收和用户采纳。

## 聊天回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出：独立结论；ABF/hash；测试与 Evidence 摘要；P0/P1/P2/Unknown/Not Implemented；资产与 R-0040/R-0051/R-0052 状态；下一步许可；Review／Evidence 路径；需要 PM 确认事项。
