# LIFEOS-P3-104｜三页 UI→本地 Runtime 与受控 Tauri/IPC 整合能力包

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-103，授权创建本能力包，并进一步授权后续专项会话仅从 Frozen ABF 列明的 Rust／Tauri 官方分发和 registry 下载精确版本，写入 `/Users/xxe/.rustup`、`/Users/xxe/.cargo` 与 P3-104 task-local `.tooling/`。本任务只允许在新建隔离工程目录、全新 task-local DB 和固定非敏感夹具中实现与验证；不得接入、读取、复制、迁移或清理 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1` 及其中 retained DB／页面，不得处理其他真实个人数据、凭据、网络目标或第三方系统。

## 任务信息

- 任务 ID：`LIFEOS-P3-104`
- 任务名称：三页 UI→本地 Runtime 与受控 Tauri/IPC 整合能力包
- 优先级：P0
- 任务类型：受控 UI／本地持久化／桌面 IPC 工程能力包；直接实现，不是评估任务。
- 是否为受控能力包：Yes。
- 唯一能力边界：把 P3-091 已验收的三页 UI 叙事与 P3-097 已验证的本地 capture/today 语义整合进一个真实可运行、仅固定非敏感夹具的本地桌面候选；renderer 只能调用三项窄 IPC，不拥有文件、路径、DB、shell、process 或 network 能力。
- 包内允许工作：新建工程、实现、回归、必要补测、固定非敏感动态／视觉 Evidence、Manifest 和文案对齐。
- 包内整改授权：仅限 P3-104 工程目录、固定非敏感夹具和 Frozen ABF；不得扩大数据、路径、IPC、依赖来源、真实能力、风险、冻结或阶段边界。
- 必须拆分：真实 retained 数据接入、真实个人输入、风险关闭／重开、工程基线恢复、Schema/API／关键资产冻结、导出、Vault、云／第三方、同步、多设备、L3、外部用户、Stage 4。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐 Agent：Codex 新建隔离工程会话。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 模型理由：实际桌面 IPC、SQLite 生命周期、renderer 权限、路径边界和三页动态 Evidence 均属 P0。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：None。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后必须全新隔离独立复评。
- 是否允许修改工程文件：仅 `lifeos/engineering/LIFEOS-P3-104/`。
- 是否允许修改项目账本：No。
- 主责：桌面 UI／本地 runtime／IPC 工程。
- 协审：技术架构、AI 信任安全、数据／领域、独立 QA、产品体验与可访问性。
- 关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅固定非敏感内部可用性，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-104-v1`
- ABF SHA-256：`2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b`。
- 正式 Rework：0/2。
- 生效决策：D-0423、D-0424。

## 已授权的工具链 bootstrap 边界

- 本机当前无 Rust、Cargo 或 Tauri CLI；本任务要求实际 Tauri debug desktop candidate，不得用 Python harness、纯 `file:` 页面、mock bridge、静态 Rust 源码或 Swift/WKWebView 替代。
- Frozen ABF 已锁定 Rust `1.98.0`、Tauri CLI `2.11.4`、Tauri crate `2.11.5`、直接依赖版本、唯一官方下载域名、写入路径、程序性 lock freeze 与离线 clean rebuild。
- 前端采用本地静态 HTML/CSS/JS 和 Tauri global API，不使用 npm、全局 npm、dev server 或 localhost。
- 任务卡路径投递到新隔离 Codex 工程会话，即授权其在 Frozen ABF 内完成一次受控 bootstrap；bootstrap 后必须 `CARGO_NET_OFFLINE=true` 且所有 build/test/runner/app Evidence 使用 `--locked` 离线完成。
- 任何额外版本、域名、包管理器、系统安装、shell profile 修改、lock 漂移或无法离线复现均立即停止并回报 PM。

## 工程目标

在 `lifeos/engineering/LIFEOS-P3-104/` 创建可运行的三页桌面候选：

1. `default-recovery`：允许固定非敏感文本的明确捕获确认，显示 saved／idempotent repeat／blocked，关闭重启后从 backend `today` 读取并明确标注“用户原文”“本地捕获”“AI 未启用”。
2. `no-reliable-suggestion`：读取同一 backend 状态，但不生成建议；只提供用户控制的“选择 Project”与“记录停点”等本地动作，不把系统状态冒充 AI 建议。
3. `restricted-offline`：明确展示离线、renderer 无直接文件／DB／网络能力、IPC allowlist 和失败披露；未知／越权命令 fail closed。

三页必须保留 P3-091 的视觉层级、响应式、skip link、可见焦点、Tab／Enter、reduced-motion、身份边界和刷新／关闭重开语义；真实持久化状态由 backend 权威管理，renderer 内存不得冒充保存成功。

## 固定 IPC 与数据边界

- Renderer 只允许调用：`capture_record`、`get_today`、`runtime_status`。
- `capture_record` 参数只允许固定非敏感 text 与 task-local idempotency key；路径、DB、output、SQL、shell 参数均不存在。
- `get_today` 只返回最小结构化 records、source、status 和审计所需非敏感字段；不返回 raw DB、路径控制或通用查询能力。
- `runtime_status` 只返回 offline／AI disabled／capability flags 和受控错误码。
- 未知命令默认拒绝；`clear`、delete、export、generic read/write/path、raw SQL、shell、process spawn、network、Vault、模型和外部 URL 均不得注册。
- Backend 独占 task-local DB 路径；renderer 不得选择或观察任意路径。动态测试 DB 必须位于新建 `/private/tmp/lifeos-p3-104-*` 或任务自有 test fixture 目录，结束时精确清理。
- capture/today 的保存、幂等、冲突、重启、审计、页面状态和失败关闭语义必须继承 P3-097/P3-103 已验证合同；不得修改历史候选。

## 允许修改与严格只读

允许新建／修改：

- `lifeos/engineering/LIFEOS-P3-104/`
- `lifeos/deliverables/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
- `lifeos/local_prechecks/` 中本任务预检报告（若适用）

严格只读：P3-091/P3-092 三页 UI 资产和 Evidence、P3-093、P3-097 至 P3-103 的 candidate／任务／交付物／Review／Evidence、所有项目账本、Frozen Stitch／PRD 资产和 retained pilot 目录。

## 最小启动包与定向补读

任务进入 Ready 后，新会话必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 Frozen ABF
4. `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/ACCEPTANCE_GOVERNANCE.md`
8. `lifeos/deliverables/LIFEOS-P3-093_three_frozen_today_pages_controlled_ui_closure_and_next_capability_decision_package.md`
9. `lifeos/reviews/LIFEOS-P3-093_pm_review.md`
10. `lifeos/reviews/LIFEOS-P3-103_pm_review.md`

定向补读：

- `lifeos/engineering/LIFEOS-P3-091/` 当前五个页面资产文件及 attempt-2 Manifest；P3-092 PM Review。
- P3-097 `local_capture.py`／CLI 及 P3-103 PM Review／Manifest，仅用于继承语义和 hash，不直接复制测试。
- `lifeos/spikes/P2-015-tauri-ipc-boundary/README.md` 与 `equivalent_capability_contract.json`。
- `lifeos/PM_OPERATING_MODEL.md`：P0、真实能力、受控能力包、两层验收、Tauri/IPC、动态 Evidence 和独立复评。
- `lifeos/ROLE_MATRIX.md`：工程、技术架构、数据／领域、AI 信任安全、独立 QA、产品体验。
- `lifeos/STAGE_GATES.md`：Gate 1–5 与 Stage 3→4。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- `lifeos/DECISION_LOG.md`：D-0376、D-0401、D-0414、D-0420 至最新 P3-104 冻结决策。

仅在账本冲突时补读无关历史。

## 实现与包内自检要求

- 必须创建真实 Tauri desktop debug candidate；不得用 mock/equivalent harness 替代核心动态通过。
- 前端从 P3-091 资产复制到 P3-104 后修改；不得修改历史资产。
- Backend 必须窄 allowlist、deny-by-default、无 renderer 直接 capability；CSP 禁止网络与远程资源。
- 覆盖首次保存、幂等重复、同 key 异文本冲突、关闭重启 today、三页导航、失败注入、unknown IPC、参数 schema、路径不可控、DB／页面／哨兵不变和真实 app 关闭重开。
- 包内自检必须在干净 task-local 副本运行首次、重复、重启、失败、宽／窄屏、键盘、关闭重开和 debug config 静态扫描。
- 动态／视觉 Evidence 必须实际操作 Tauri app，不得用 `file:` Chrome、In-app Browser、HTTP、mock renderer、静态扫描或 AX 暴露代替；每项记录操作、可观察结果、结构化 ID、截图／日志路径和 SHA-256。
- runner 必须验证闭环表每个必填行 PASS；缺项必须 Not Implemented 并非零退出。
- 保留源码、Cargo.lock、toolchain／registry／bootstrap hash、联网停止证明、离线 clean build log、测试 runner、逐项结果、IPC trace（脱敏）、screenshots、hash、Manifest、复跑命令和临时清理证明。
- 提交前自检发现的同范围问题在本能力包内修正；不另建微任务。

## 禁止事项与停止条件

- 不得访问 retained pilot、真实个人内容、既有个人 DB 或任意用户目录。
- 不得调用 clear/delete/export；不得连接网络运行 app；不得启用 updater、遥测、远程 asset、dev server 或 localhost HTTP。
- 不得给 renderer 文件系统、raw DB、shell、process、network 或 generic invoke 权限。
- 不得安装未在 Frozen ABF/lockfile 内的依赖；不得使用系统级安装、任意镜像或未授权脚本。
- 发现工具链不可复现、lock/hash 漂移、实际 app 无法运行、需要真实数据、IPC 越权、CSP／capability 默认关闭失效、Evidence 不可复核或历史 hash 变化时停止。
- 不关闭／重开 R-0040、R-0051、R-0052；不冻结、不恢复基线、不进入 Stage 4。

## 交付物

- 工程：`lifeos/engineering/LIFEOS-P3-104/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
- Engineering Evidence：`lifeos/engineering/LIFEOS-P3-104/evidence/MANIFEST.md`
- 结论计数：必须报告 P0/P1/P2/Unknown/Not Implemented。
- 即使执行侧自检 Pass，也必须等待 PM 验收、用户采纳和全新隔离独立复评；不得自动启用 retained 数据或创建下一任务。

## 当前回复与投递规则

- 当前任务为 Ready；用户将本任务卡明确路径投递至新建隔离 Codex 工程会话，即构成本任务及 Frozen bootstrap 边界内的执行授权。
- 专项会话不得继承上一任务授权，不得自行启动独立复评或后续任务。
