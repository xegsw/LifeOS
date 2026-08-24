# LIFEOS-P3-106｜三张冻结 Stitch 页面高保真 Tauri UI 路径合同后继能力包

## 授权与安全语境

> LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-105 的 PM-Validated Blocked／关闭结论，并授权创建本后继任务。本任务仅在新建 P3-106 工程、全新固定非敏感 `/private/tmp` 夹具和本地只读设计／runtime 资产内完成防御性 UI／Tauri 整合验证；不访问 retained pilot、真实个人数据、网络、云、第三方、凭据或外部目标，不扩大 IPC、文件、DB、shell、process 或网络能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-106`
- 任务名称：三张冻结 Stitch 页面高保真 Tauri UI 路径合同后继能力包
- 优先级：P0
- 任务类型：受控高保真 UI／真实 Tauri 整合工程能力包；P3-105 治理冲突的全新后继。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：保持 P3-104 runtime／三项 IPC／Cargo／capability 不变，在新 ABF 精确授权其固定非敏感测试路径，并完成三张 Stitch 页面实际 app 高保真与完整动态 Evidence。
- 包内允许工作：创建 P3-106 干净工程；复制 P3-104 技术底座与 P3-105 六个 UI／窗口草案文件；修改 P3-106 UI、窗口字段、P3-106 runner／测试／Evidence；完成实际 app 回归与文案对齐。
- 包内整改授权：仅限 P3-106 新工程、Frozen `ABF-P3-106-v1` 精确路径和固定非敏感数据；不得修改 P3-104/P3-105、runtime、IPC、依赖、能力、真实数据、风险、冻结或阶段范围。
- 必须拆分：runtime／IPC／Cargo／capability／Schema/API 变化、扩大临时路径正则、真实数据接入、风险关闭／重开、基线恢复、关键冻结、导出、Vault、云、同步、多设备、L3、外部用户、Stage 4 与最终独立复评。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新隔离工程会话。
- 推荐理由：需同时完成复杂 UI、实际 Tauri 动态操作、路径写集静态枚举、P0 runtime 回归和机器可复核视觉 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：路径授权和 Evidence 诚实性为 P0，视觉完成定义为 P1，必须在工程前完整推演写路径。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A。
- 后备模型：None。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后，另建 P3-104 + P3-106 最终组合候选的全新隔离独立工程／安全／视觉复评。本轮不得创建。
- 是否允许修改工程文件：Yes，仅 `lifeos/engineering/LIFEOS-P3-106/`。
- 是否允许修改项目账本：No。
- 主责角色：体验设计／前端 UI 工程 + 桌面 Tauri 整合。
- 协审角色：技术架构、数据／领域、AI 信任安全、可访问性、独立 QA。
- 必须通过关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅固定非敏感内部理解检查，不作用户价值 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-106-v1`
- ABF SHA-256：`1aa076a289173eb0dbd4e17ccfd3a1af89cbd9f815ad656d31d9318a5172a5c4`
- ABF 状态：Frozen。
- 本任务正式 Rework 上限：2；当前 0。
- 生效决策：D-0429。
- 执行授权方式：用户将本任务卡绝对路径投递至全新 Codex 工程会话即授权 Frozen 范围执行；不覆盖 ABF 外路径或能力。
- 投递会话与隔离：必须新建，不复用 P3-104/P3-105 执行会话；P3-105 已关闭且 Evidence 有命名空间污染，必须避免授权和证据继承。
- 投递前额外用户确认：本轮用户采纳与创建授权已覆盖固定非敏感 P3-104 兼容夹具路径；任何其他路径、runtime／IPC／依赖、真实数据或阶段变化仍须新确认。

## 背景与治理修正

P3-105 的 UI 源码预检通过，但不可变 runtime 只接受 `/private/tmp/lifeos-p3-104-*`，其 ABF 只允许 `/private/tmp/lifeos-p3-105-*`，actual app 无合法启动路径。PM 于 D-0428 将 P3-105 关闭；用户随后采纳并授权创建后继。

P3-106 不修改 runtime，而是把实际 app 和不可变 unit tests 会写入的固定非敏感路径在启动前精确冻结。P3-105 UI 草案可以只读复制，但 P3-105 Evidence 不得复制、复用或写入。

## 工程目标

在 `lifeos/engineering/LIFEOS-P3-106/` 创建真实可运行 Tauri debug candidate：

1. 从 P3-104 复制不含 `.tooling/`、`target/`、`evidence/` 的技术底座；冻结 Rust、Cargo、IPC 与 capability hash。
2. 仅复制 P3-105 的三张 HTML、`app.js`、`styles.css` 和 `tauri.conf.json` 作为草案；在 P3-106 内继续整改。
3. `evidence/` 必须新建为空；历史 Evidence 只以 hash 引用。
4. 在 ABF 精确路径 allowlist 内运行 unit、actual app、visual、dangling 和清理矩阵；执行前生成机器可读写路径 inventory。
5. 用实际 app 产生三张 1280×1024 全画布截图与 reference side-by-side，逐项证明共享骨架、三态锚点、a11y 和关闭态。
6. composer 只允许冻结的固定非敏感 capture；附件、语音、Project、AI、来源等未实现动作逐项 disabled 或明确“未启用”，并证明零 IPC／DB 副作用。

## 允许修改与严格只读

允许新建／修改：

- `lifeos/engineering/LIFEOS-P3-106/`
- `lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`
- `lifeos/local_prechecks/` 中本任务报告（如适用）
- `ABF-P3-106-v1` 精确列明、由本任务新建并最终精确清理的 `/private/tmp` 路径

P3-106 内允许发生实质变化的文件仅为 UI 五文件、`tauri.conf.json` 的窗口标题／初始／最小尺寸、P3-106 README／测试／runner／Evidence／本地中性装饰资产。

P3-106 内必须与 P3-104 字节一致：`Cargo.lock`、`Cargo.toml`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json` 和全部直接依赖版本。若必须修改，立即停止。

严格只读：P3-104、P3-105 全部目录，P1-004/P1-006/P1-009/P1-011、三张冻结截图、历史 Review／Evidence／Manifest、项目账本、Stitch 在线资产和 retained pilot。

## 精确临时路径摘要

- actual app／P3-106 runner：仅 `^/private/tmp/lifeos-p3-104-p3-106-(app|replay|dangling-final|dangling-journal|dangling-wal|dangling-shm|path|tamper|a11y|visual)-[a-z0-9-]+$`。
- immutable unit tests：仅 ABF 列明的 `lifeos-p3-104-unit-*-[PID]` 十类确定性路径。
- 禁止旧路径：`lifeos-p3-104-app-evidence`、`lifeos-p3-104-rework-replay-*`、`lifeos-p3-104-rework-static-results.json` 及其他未列路径。
- 创建前路径必须不存在且祖先无链接；清理只使用运行台账精确路径，禁止 glob。

完整正则、目录内容限制、legacy metadata 保全和清理规则以 Frozen ABF 为准。

## 最小启动包与定向补读

新建专项会话必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-106-v1`
4. `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（只借用字段，本任务不适用快车道）
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/ACCEPTANCE_GOVERNANCE.md`
8. `lifeos/reviews/LIFEOS-P3-105_pm_review.md`
9. `lifeos/reviews/LIFEOS-P3-105/pm_evidence/initial/MANIFEST.md`
10. `lifeos/reviews/LIFEOS-P3-104_pm_review.md` 与 Rework PM Evidence Manifest
11. 三张权威参考图及 `lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`

定向补读：

- P1-004/P1-006 的信息层级、内容身份、Project 选择、渐进披露条款。
- P1-009 报告、P1-010 独立评审、P1-011 条件补丁的三态意图。
- P3-104 的 Cargo、Rust、capability、配置和 runtime path validation/test sections；只读。
- P3-105 六个 UI／窗口草案文件；只读。不得读取 P3-105 Evidence 内容，除本任务列明的 Review／Manifest。
- `lifeos/PM_OPERATING_MODEL.md`：P0、真实 Tauri、受控能力包、两层验收、动态 Evidence、独立复评章节。
- `lifeos/ROLE_MATRIX.md`：体验、技术架构、数据、AI 信任安全、独立 QA。
- `lifeos/STAGE_GATES.md`：Gate 1–5、有限 Stage 3、Stage 3→4。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- `lifeos/DECISION_LOG.md`：D-0401、D-0414、D-0424 至 D-0429。

仅在发现账本冲突时再定向补读其他历史。

## 实现和自检要求

- 工程动作前完成 `write_path_inventory.json`：逐个列出 test／runner／cleanup 的路径生成表达式、实际正则、创建类型、清理方式和 ABF 行；任何未覆盖项立即 Blocked。
- 对 immutable unit tests，必须先静态证明写路径仅为 ABF 十类，再执行 `cargo test --locked`；测试前后分别扫描精确匹配，残留必须为 0。
- 前端必须代码实现；参考图 background／canvas 大图／整页 img／base64／透明覆盖为 P0。
- 实际 app 三页各生成 1280×1024 全画布和并列对照；浏览器、file、HTTP、mock、DOM 计数不得替代。
- 动态闭环覆盖三页导航、capture、repeat、conflict、注入失败、刷新、关闭重开、未实现控件、unknown IPC、额外字段、四类 dangling、Tab、Enter、skip、focus、窄屏、reduced motion。
- runner 必须因路径 inventory 缺失、任何动态缺行、FAIL、Unknown、Not Implemented、hash mismatch、旧 temp metadata 变化或残留非零而非零退出。
- 提交前报告 P0/P1/P2/Unknown/Not Implemented；全部为 0 才可提交 PM Pass 候选。

## 禁止事项与停止条件

- 不访问、读取、复制、迁移或清理 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`。
- 不联网、不安装依赖、不使用 npm／dev server／localhost／远程 asset，不修改 shell profile 或系统工具链。
- 不修改 P3-104/P3-105；不改 runtime/main/Cargo/Cargo.lock/capability，不增加 IPC。
- 不创建或清理 ABF 未列的任一 `/private/tmp` 路径；不使用 glob、目录链接或 broad prefix 解释授权。
- 不注册 clear/delete/export、generic path/read/write、raw SQL、shell、process、network、Vault、模型、同步或外部 URL。
- 不声称高保真等于资产冻结、真实使用启用、用户价值验证或 Stage 4。
- 发现固定 hash 漂移、路径 inventory 不完整、需要新依赖／runtime 改动、实际 app 无法操作、Evidence 不可复核或历史被写入时立即停止。

## 交付物

- 工程：`lifeos/engineering/LIFEOS-P3-106/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`
- Engineering Evidence：`lifeos/engineering/LIFEOS-P3-106/evidence/MANIFEST.md`
- 必须包含：空 Evidence 起步证明、写路径 inventory、三张 actual-app 全图与并列对照、visual contract、动态闭环、runtime 回归、四类 dangling、离线 clean runner、结构化结果、hash/Manifest、旧路径保全和精确清理证明。
- 完成后只提交 PM 验收；不自行创建独立复评、关闭风险、冻结或进入 Stage 4。

## 会话路由与回复

- 建议新建会话：Yes。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 工程执行。
- 隔离原因：P3-105 已关闭且 Evidence namespace 污染；P3-106 必须从空 Evidence 与新授权开始，不能继承旧执行上下文。
- 任务完成后建议保留会话：Yes，仅用于本 ABF 内包内修正；不得承担最终独立复评。
- 会话回复必须使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径、自检计数和 PM 待确认项。
