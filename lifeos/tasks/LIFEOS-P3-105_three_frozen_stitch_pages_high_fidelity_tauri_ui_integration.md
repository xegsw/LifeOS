# LIFEOS-P3-105｜三张冻结 Stitch 页面高保真 Tauri UI 整合能力包

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-104 技术候选，并明确要求创建高保真 UI 新任务、继承全部 runtime 安全不变量，最终对组合候选统一做全新隔离独立复评。本任务仅在新建 P3-105 工程目录、全新 `/private/tmp` 固定非敏感夹具和本地只读设计资产内完成防御性 UI／runtime 整合验证；不访问 retained pilot、真实个人数据、网络、云、第三方、凭据或外部目标，不扩大 IPC、文件、DB、shell、process 或网络能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-105`
- 任务名称：三张冻结 Stitch 页面高保真 Tauri UI 整合能力包
- 优先级：P0
- 任务类型：受控高保真 UI／真实 Tauri 整合工程能力包；直接实现，不是评估任务。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：在不改变 P3-104 runtime、三项 IPC、Cargo lock、capability、数据和路径边界的前提下，以三张冻结 Stitch 截图为视觉权威，在新 Tauri candidate 中高保真实现三态界面。
- 包内允许工作：复制 P3-104 到新目录；修改 P3-105 UI HTML/CSS/JS、窗口尺寸／标题相关配置；实现、回归、视觉合同验证、实际 app 动态 Evidence、Manifest 和文案对齐。
- 包内整改授权：仅限 P3-105 新工程、固定非敏感夹具与 `ABF-P3-105-v1`；不得修改 P3-104、runtime、IPC、依赖、能力、真实数据、风险、冻结或阶段范围。
- 必须拆分：runtime／IPC／Cargo／capability／Schema/API 变化、真实 retained 数据接入、风险关闭／重开、工程基线恢复、关键资产冻结、导出、Vault、云／第三方、同步、多设备、L3、外部用户、Stage 4 和最终独立复评。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离工程会话。
- 推荐理由：任务同时包含代码级高保真前端实现、真实 Tauri 动态操作、P0 runtime 不变量回归和机器可复核视觉 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：需要在严禁改动安全底座的情况下完成复杂视觉还原、状态映射、可访问性和实际 app Evidence。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围；视觉误判或 runtime 回退均影响 P0/P1 完成定义。
- 必须升级条件：N/A；当前配置已为本任务冻结配置。
- 后备模型：None。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后，必须对 P3-105 最终组合候选做全新隔离独立工程／安全／视觉复评。本轮不提前创建该评审任务。
- 是否允许修改工程文件：Yes，仅 `lifeos/engineering/LIFEOS-P3-105/`。
- 是否允许修改项目账本：No。
- 主责角色：产品体验／前端 UI 工程 + 桌面 Tauri 整合。
- 协审角色：技术架构、AI 信任安全、数据／领域、可访问性、独立 QA。
- 必须通过关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅固定非敏感内部理解检查，不作用户价值 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-105_three_frozen_stitch_pages_high_fidelity_tauri_ui_integration_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-105-v1`
- ABF SHA-256：`3db798ab392c663ca4099491ed10ef8f70429542ef7b43809c97fb0774be6a4c`
- ABF 状态：Frozen。
- 本任务正式 Rework 上限：2；当前 0。
- 生效决策：D-0427。
- 执行授权方式：用户将本任务卡绝对路径投递至新建 Codex 工程会话即授权 Frozen 范围内执行；该投递不授权任何 ABF 外能力。
- 投递会话与隔离：必须新建 Codex 工程会话。不得复用 P3-104 工程执行会话，因为新任务改变视觉用户结果和 ABF，需避免旧范围／授权／Evidence 混用。
- 投递前额外用户确认：本轮用户指令已覆盖新高保真 UI 任务及不变 Tauri/runtime 边界。任何 runtime、IPC、依赖、capability、真实数据／路径、风险或阶段变化仍须新确认。

## 背景与治理纠偏

P3-104 已在 `ABF-P3-104-v1` 下通过 PM 验收，其技术结果是可离线重建的真实 Tauri app、三项窄 IPC、task-local SQLite 和失败关闭候选。用户随后指出当前绿色工程验证 UI 与此前冻结的三张 `LifeOS 精修版` Stitch 页面明显不一致。PM 核对确认：P3-082 以后只继承“状态与信息层级”，高保真视觉实现从未进入验收路线。

该问题不违反 P3-104 的 Frozen ABF，不能追溯判 P3-104 Rework；但它是新的明确用户结果，必须新建 P3-105、新 ABF 和独立 Evidence。P3-104 只作为技术底座，不得再被描述为原始设计已实现。

## 启动前验收依据冻结

- `ABF-P3-105-v1` 已在专项会话启动前冻结；它只冻结本轮验收依据，不冻结产品需求或最终设计系统。
- 执行方在任何复制、构建或修改前必须核对 ABF 路径、ID、hash、三张参考图、P3-104 不可变文件和允许修改清单。
- 执行方拥有一次标准质疑窗口；若高保真锚点、状态映射或不可变边界存在歧义，必须停止并回报 PM。
- 启动后不得修改 ABF；新增反例只能映射既有 L1/L2。需要改 runtime、IPC、依赖或视觉权威输入时，当前任务关闭并新建任务。

## 工程目标

在 `lifeos/engineering/LIFEOS-P3-105/` 创建真实可运行的 Tauri debug candidate：

1. 从 P3-104 复制完整技术底座，但 `Cargo.lock`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json` 必须保持冻结 hash。
2. 以三张冻结 1280×1024 截图为权威视觉输入，用真实 HTML/CSS/JS 元素实现桌面左侧导航轨、顶部语境、三态主内容卡、底部捕获 composer、蓝灰视觉语言和状态差异。
3. 不得把参考截图作为背景／蒙层／主体 UI；不得下载第三方图片。缺少的缩略图使用本地代码生成的中性占位构图。
4. 视觉稿中的用户原文、来源、AI 建议和保存事实必须映射为固定非敏感、backend 权威或明确关闭／未启用状态，不得把设计占位内容冒充真实事实。
5. composer 只允许任务冻结的固定非敏感文本调用 `capture_record`；附件、语音、Project、AI、来源等未实现控件必须 disabled 或明确披露未启用，并证明零副作用。
6. 三页导航、capture、repeat、conflict、失败、刷新、关闭重开、离线与权限关闭态必须继续由 P3-104 backend 权威状态驱动。

## 允许修改与严格只读

允许新建／修改：

- `lifeos/engineering/LIFEOS-P3-105/`
- `lifeos/deliverables/LIFEOS-P3-105_three_frozen_stitch_pages_high_fidelity_tauri_ui_integration.md`
- `lifeos/local_prechecks/` 中本任务报告（如适用）
- 执行时新建并最终精确清理的 `/private/tmp/lifeos-p3-105-*`

P3-105 内允许发生实质变化的文件仅为：

- `ui/default-recovery.html`
- `ui/no-reliable-suggestion.html`
- `ui/restricted-offline.html`
- `ui/app.js`
- `ui/styles.css`
- `tauri.conf.json` 中窗口标题、初始／最小尺寸字段
- P3-105 自有 README、测试、runner、Evidence、图标或代码生成的中性本地装饰资产

P3-105 内必须与 P3-104 字节一致：`Cargo.lock`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json`，以及所有直接依赖版本。若必须修改，立即停止。

严格只读：P3-104 全部目录、P1-004/P1-006/P1-009/P1-011、三张冻结截图、所有历史 Review／Evidence／Manifest、项目账本、Stitch 在线资产和 retained pilot。

## 三张权威参考图

- 默认恢复：`lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg`，SHA-256 `7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1`。
- 暂无可靠建议：`lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg`，SHA-256 `55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697`。
- 权限受限／离线：`lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg`，SHA-256 `9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661`。

具体共享骨架、三态锚点、严重级别和 16 行逐项矩阵以 Frozen ABF 为唯一验收口径。

## 最小启动包与定向补读

新建专项会话必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-105-v1`
4. `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（只借用工程报告字段，本任务不适用快车道）
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/ACCEPTANCE_GOVERNANCE.md`
8. `lifeos/reviews/LIFEOS-P3-104_pm_review.md`
9. `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md`
10. 三张权威参考图及 `lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`

定向补读：

- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md` 与 `LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md` 的信息层级、内容身份、Project 选择和渐进披露条款。
- `lifeos/deliverables/LIFEOS-P1-009_home_today_stitch_rework_report.md`、`lifeos/reviews/LIFEOS-P1-010_home_today_stitch_re_review.md` 的三态意图与已知条件。
- P3-104 `Cargo.lock`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json`、`tauri.conf.json`、UI 五文件、实际 app runner 和 Rework Manifest；仅复制到 P3-105，P3-104 原件只读。
- `lifeos/PM_OPERATING_MODEL.md`：P0、真实 Tauri/IPC、受控能力包、两层验收、动态 Evidence、独立复评相关章节。
- `lifeos/ROLE_MATRIX.md`：产品体验、前端／桌面工程、技术架构、数据／领域、AI 信任安全、独立 QA。
- `lifeos/STAGE_GATES.md`：Gate 1–5、有限 Stage 3 和 Stage 3→4。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- `lifeos/DECISION_LOG.md`：D-0078、D-0401、D-0414、D-0424 至 D-0427。

仅在发现账本冲突时定向补读其他历史，不全文翻阅无关任务。

## 实现和自检要求

- 在新目录复制 P3-104，先复算冻结输入，再开始 UI 修改。
- 前端必须代码实现；对参考图的任何 `background-image`、canvas 大图绘制、整页 `<img>`、base64 截图或透明覆盖均为 P0。
- 实际 Tauri app 必须在 1280×1024 规范化 webview 画布分别产生三张完整截图和并列参考对照；局部图、浏览器 `file:`、HTTP、mock、DOM 计数不能代替。
- 为共享骨架与三态锚点生成机器可读 `visual_contract.json` 和逐项 verifier；每个锚点独立 PASS/FAIL，不得批量继承总分。
- 实际动作覆盖：三页导航、首次 capture、repeat、conflict、注入失败、刷新、关闭重开、未实现控件、unknown IPC、额外字段、四类 dangling、Tab、Enter、skip link、focus、窄屏和 reduced motion。
- 动态闭环逐行填写操作、可观察结果、唯一结果 ID、截图／日志路径和 SHA-256；runner 必须因任一缺行、FAIL、Unknown 或 Not Implemented 非零退出。
- 在没有 build target 的干净 task-local 副本、完全离线 `--locked` 重建实际 `.app`；保留 binary/lock/source hash、进程、网络 0 和清理日志。
- 执行侧提交前必须报告 P0/P1/P2/Unknown/Not Implemented，全部为 0 才可提交 PM。

## 禁止事项与停止条件

- 不访问、读取、复制、迁移或清理 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`。
- 不联网、不安装依赖、不使用 npm／dev server／localhost／远程 asset，不修改 shell profile 或系统工具链。
- 不修改 P3-104 或任何历史资产；不改 runtime/main/Cargo.lock/capability，不增加 IPC。
- 不注册 clear/delete/export、generic path/read/write、raw SQL、shell、process、network、Vault、模型、同步或外部 URL。
- 不把参考截图、局部裁图或设计导出嵌进 app 冒充实现。
- 不声称高保真等于视觉资产冻结、真实使用启用、用户价值验证或 Stage 4。
- 发现冻结 hash 漂移、需要新依赖／runtime 改动、实际 app 无法操作、视觉权威歧义、Evidence 不可复核或历史被写入时立即停止。

## 交付物

- 工程：`lifeos/engineering/LIFEOS-P3-105/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-105_three_frozen_stitch_pages_high_fidelity_tauri_ui_integration.md`
- Engineering Evidence：`lifeos/engineering/LIFEOS-P3-105/evidence/MANIFEST.md`
- 必须包含：三张全画布实际 app 截图、三张并列对照、visual contract、动态闭环、runtime 回归、离线 clean runner、结构化结果、hash/Manifest、清理证明和复跑命令。
- 完成后只提交 PM 验收，不自行创建独立复评、关闭风险、冻结或进入 Stage 4。

## 会话路由与回复

- 建议新建会话：Yes。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 工程执行。
- 隔离原因：P3-105 是新用户结果、新目录和新 ABF；不得让 P3-104 授权／Evidence 与高保真实现混合。
- 任务完成后建议保留会话：Yes，仅供同一 P3-105 ABF 内可能的包内修正；不得承担最终独立复评。
- 会话回复必须使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径、自检计数和 PM 待确认项。
