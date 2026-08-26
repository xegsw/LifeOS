# LIFEOS-P3-120｜以人为主体的产品 Runtime MVP 实现

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务只允许在全新 P3-120 工程目录和固定 `/private/tmp` 根内，以非敏感合成数据实现本地 Tauri/IPC Runtime MVP；不访问 Pilot-1/Pilot-2、真实个人目录、真实 DB、真实文件、网络、模型、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-120`
- 任务名称：以人为主体的产品 Runtime MVP 实现
- 优先级：P0
- 任务类型：受控本地产品 Runtime MVP 工程能力包
- 是否为受控能力包：Yes
- 唯一用户结果：把获采纳但 Not Frozen 的 Person-centered 产品候选与已通过历史验收的本地 Tauri Runtime 技术底座组合成一个可启动、可导航、可合成 capture、可在 Today 找回、可刷新并可关闭重开的本地 MVP 候选。
- 唯一风险边界：全新 task-local 工程、全新合成 SQLite、既有三项受控 IPC（`capture_record`、`get_today`、`runtime_status`）、离线单进程。
- 包内允许：正向 allowlist 建立 P3-120 candidate；UI/runtime 适配；测试、回归、必要补测；Evidence/Manifest；文案对齐；同一 ABF 内包内修正。
- 包内整改授权：仅 P3-120 自有目录与固定临时根；不得触碰历史候选、Pilot、真实数据或扩大 IPC/Schema/API。
- 必须拆分：真实 DB／路径／输入启用、clear/export/权限/恢复、模型／Global AI 真推理、网络／云／第三方、Schema/API 改变、风险关闭／重开、资产冻结、工程基线恢复、全新隔离独立复评、Stage 4。
- 建议篇幅：1800–3000 字；详细 Evidence 写入工程目录。
- 是否适用 P3 Engineering Fast Lane：No；Tauri/IPC 与本地持久化属于高风险能力。
- 推荐执行 Agent：Codex，全新工程执行会话。
- 推荐理由：需要 Rust/Tauri、SQLite、前端状态整合、离线构建、生命周期与失败关闭测试。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：跨 UI、Tauri IPC、SQLite 生命周期与历史安全边界，需高边界意识与深度回归。
- 允许降级模型：None
- 禁止降级条件：全部范围
- 必须升级条件：N/A；首选不可用则停止
- 后备模型：None
- 是否需要后续独立评审：Yes；PM Pass 且用户采纳后新建全新隔离独立复评任务。
- 是否允许修改工程文件：Yes；仅 P3-120 自有目录。
- 是否允许修改项目账本：No。
- 主责角色：Codex 工程实现、Runtime/IPC、前端产品集成与 QA。
- 协审角色：产品架构、技术架构、数据安全、AI 信任、体验与 Evidence QA。
- 必须通过关卡：固定输入与 positive allowlist、离线 build/test、三项 IPC、合成 capture→Today→刷新→重启、失败关闭、renderer 关闭态、产品 IA/身份语义、历史保全、精确清理。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-120-v1`
- ABF SHA-256：`e18c463ffb59f1bb80ba55d48a61009792cbd36190d998867d6f08a7aaebe219`
- ABF 状态：Frozen。
- 正式 Rework：0/2。
- 生效决策：`D-0478`。
- 执行授权：用户已完成 synthetic-only Tauri/IPC 边界确认；将本任务卡绝对路径投递至符合要求的全新 Codex 工程会话，即启动 Frozen 范围执行。
- 投递前额外确认：Completed。用户明确确认仅在 `lifeos/engineering/LIFEOS-P3-120/` 与 `/private/tmp/lifeos-p3-120-runtime-mvp-v1` 中，使用全新合成 DB 和既有三项 Tauri/IPC；不访问 Pilot、真实 DB、真实路径、网络或模型。
- 会话隔离：冻结后必须新建 Codex 工程会话；不得复用 P3-119 GUI Spike、P3-116 原型、P3-111 真实使用或 PM 主会话。

## 背景与治理判断

P3-119 已证明当前 PID-scoped 原生事件工具链不能形成可观察 GUI 状态转换。该结论不否定产品候选，但继续围绕截图工具增加 successor 会延误真实产品闭环。用户已采纳关闭 P3-119，并授权创建本任务。

本任务不是 P3-116 的 Evidence Rework，也不是 P3-119 的技术 successor；它以新的用户结果重新组合：

- P3-104/P3-111 的已验收本地 Tauri/IPC 与 capture/today 生命周期代码，只作为 Not Frozen 技术输入；
- P3-113/P3-114 获采纳的人本双领域产品定义和 P3-116 当前静态 Person-centered 候选，只作为 Not Frozen 产品输入；
- P3-119 只提供“不要依赖 PID GUI 自动注入作为完成条件”的历史事实。

## 产品完成定义

同一个实际 Tauri App 至少包含并可导航：Today、Me、Contexts、Memory、Context Detail、Memory Detail、Global AI Side Panel、AI Workspace；Settings 仅为弱化入口。Icon Rail、Person 主体、Domain 作为长期视角、Context/Memory 语义、用户内容与 AI 候选身份区分必须继承当前产品候选。

本轮真正接入 Runtime 的最小闭环仅为：

1. 用户在 Global AI/Quick Capture 的明确“合成演示模式”输入固定非敏感短文本；
2. renderer 仅通过 `capture_record` IPC 写入全新 task-local SQLite；
3. Today 仅通过 `get_today` 读取并展示；
4. `runtime_status` 显示离线、本地、合成 DB 和允许能力；
5. 刷新、关闭重开后记录仍可见，重复提交具有冻结的确定语义；
6. Me/Contexts/Memory 及详情页使用明确标记的固定 synthetic read-only fixture，不伪称已接入真实领域持久化；
7. Global AI/AI Workspace 只展示本地合成交互壳和“模型未启用”，不得调用模型、伪造智能结果或落库 AI 推断。

## 允许写入与环境

本任务执行仅允许：

- `lifeos/engineering/LIFEOS-P3-120/`
- `lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md`
- `lifeos/local_prechecks/` 中 P3-120 专属报告
- `/private/tmp/lifeos-p3-120-runtime-mvp-v1`

工程根从不存在开始；candidate、tests、tools、Evidence 与 build 配置均在 P3-120 自有目录。编译 cache、测试 DB、截图辅助物和临时 app 运行数据必须在唯一临时根或 P3-120 自有目录，结束时按 ABF 精确清理。

## 只读输入与 positive allowlist

专项只允许按 Frozen ABF 固定 hash 读取：

- P3-104、P3-111、P3-114、P3-119 的最终 PM Review；
- `LifeOS高保真原型IA-V1.0.md` 与 `LifeOS架构基线V1.0.md`；
- `lifeos/tasks/LIFEOS-P3-120_source_allowlist.md` 冻结的 P3-111 candidate 72/72 positive allowlist；
- P3-116 当前 `index.html`、`app.js`、`styles.css`、`fixtures.js`、interaction/state/visual contract。

禁止读取 P3-111 retained Pilot 路径、DB、真实输入、screenshots、raw logs、Evidence、PM Evidence 或任何保存的真实内容。禁止整体递归复制 P3-111／P3-116 根；必须先建立 source inventory，再逐文件复制 allowlist。

## 最小启动包与定向补读

完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 Frozen 后的 ABF
4. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
5. `lifeos/ACCEPTANCE_GOVERNANCE.md`
6. `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
7. `lifeos/architecture/LifeOS架构基线V1.0.md`
8. `lifeos/reviews/LIFEOS-P3-104_pm_review.md`
9. `lifeos/reviews/LIFEOS-P3-111_pm_review.md`
10. `lifeos/reviews/LIFEOS-P3-114_pm_review.md`
11. `lifeos/reviews/LIFEOS-P3-119_pm_review.md`

定向补读：`PM_OPERATING_MODEL.md` 的执行授权、高风险确认、受控能力包、P0、Evidence 与独立评审章节；`ROLE_MATRIX.md` 的 Codex 工程、产品／技术架构、数据安全、AI 信任与 QA；`STAGE_GATES.md` 的关键原型独立评审及 Stage 3→4 区分；`TASK_REGISTRY.md` P3-104/P3-111/P3-114/P3-116/P3-119/P3-120；`DECISION_LOG.md` D-0448～D-0477；`RISK_LOG.md` R-0040/R-0051/R-0052。

## 实现合同

1. 工程动作前复算所有 Frozen 输入，建立正向 source inventory；任一 hash、路径或授权冲突时，在创建候选／临时根前停止。
2. 仅逐文件复制 positive allowlist 到新 P3-120 candidate；不复制历史 Evidence、runner、target、Pilot、DB 或真实使用资产。
3. 保持 renderer 无 SQLite/file/shell/network 直接能力；仅 expose 三项窄 Tauri IPC。不得新增 command、capability、allowlist permission 或 Schema/API。
4. 将 P3-116 Person-centered UI 适配进 Tauri，并把 runtime 数据与 synthetic read-only fixture 清晰分层；不得把 fixture 伪装为持久化事实。
5. 使用全新 synthetic DB 完成首次 capture、重复/幂等、Today read、刷新、关闭重开；所有失败路径在持久化或 UI 成功状态前 fail closed。
6. Global AI/AI Workspace 保持无模型、无网络、无执行能力；候选 Action/Decision 与已确认对象视觉和语义分离。
7. 提交前在干净副本完成 offline locked test/build、实际 `.app` 启动与受控功能回放；视觉截图仅作为辅助 Evidence，不得用 GUI 自动注入或截图像素链替代功能测试。
8. 对路径链接、DB/sidecar 类型、缺失 DB、失败回执、重复、关闭重开、renderer 越权入口和 network/model/clear/export 关闭态做负向测试。
9. 生成逐行矩阵、结构化结果、日志、source/candidate hash、Manifest、复跑命令和精确 cleanup；所有 P3-120 临时产物结束时清理，工程 Evidence 保留。

## 非范围与停止条件

- 不访问、定位、stat、hash、打开、复制、覆盖或清理 Pilot-1/Pilot-2 或其他真实用户目录/DB。
- 不接受用户真实文本；只用任务卡固定的 synthetic 文本。
- 不启用 clear、export、权限设置、恢复、Vault、文件选择／导入、模型、网络、云／第三方、同步、多设备、L3、外部用户或通知中心。
- 不改变 Schema/API、技术架构、核心领域语义、AI 权限合同或 Tauri IPC 数量／签名。
- 不使用 P3-119 GUI event helper、Computer Use 自动验收、app selector、global event、AppleScript/AX、CDP/HTTP/WebDriver 作为 Pass 依赖。
- 不修改任何历史任务、ABF、候选、Review、Evidence、账本、风险或冻结记录。
- 如需要新 IPC、Schema/API、真实路径、模型、网络、系统权限或不同临时根，立即停止并回 PM；当前任务不得膨胀。

## 交付与自检

- 交付物：`lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md`
- 工程 Evidence：`lifeos/engineering/LIFEOS-P3-120/evidence/MANIFEST.md`
- 必须提交 candidate、source inventory、tests/runner、逐行 results、actual-app launch/reopen logs、辅助 screenshots、negative results、cleanup、非自指 Manifest 与从空副本复跑命令。
- 自检必须明确：P0/P1/P2/Unknown/Not Implemented 数量；任一矩阵行缺失不得提交概括性 Pass。
- 本地模型预检可因 Tauri/IPC、路径和持久化高风险最终判断跳过，但必须说明；其输出不得决定 PM 结论。
- 专项只能报告 Candidate Ready / Not Pass / Blocked；不得修改账本、宣告 Accepted/Frozen、创建独立评审或进入 Stage 4。

## 后续边界

- Candidate Ready 后由 PM 验收；PM Pass 后仍等待用户采纳。
- 用户采纳后才可新建全新隔离独立复评任务；独立复评不得由 P3-120 执行会话承担。
- 独立 Pass 仍不自动冻结产品/工程、关闭风险、启用真实数据或进入 Stage 4。
