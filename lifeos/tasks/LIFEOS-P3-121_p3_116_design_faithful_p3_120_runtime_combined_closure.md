# LIFEOS-P3-121｜P3-116 设计忠实继承与 P3-120 Runtime 组合收口

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务拟仅在全新 P3-121 工程目录与固定 `/private/tmp` 根内，使用 P3-116 的只读产品／视觉合同、P3-120 的只读 Runtime 候选、全新非敏感合成 DB 和既有三项窄 Tauri/IPC，形成视觉与 Runtime 一致的组合候选。不访问 Pilot、真实个人数据、真实 DB／路径／文件、网络、模型、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-121`
- 任务名称：P3-116 设计忠实继承与 P3-120 Runtime 组合收口
- 优先级：P0
- 任务类型：受控本地产品 UI＋Runtime 组合工程能力包
- 是否为受控能力包：Yes
- 唯一用户结果：在不改变 P3-120 Runtime 能力边界的前提下，使实际 Tauri App 忠实继承 P3-116 已确定的 Person-centered IA、视觉层级、空间关系、产品气质和交互身份合同，并保持合成 capture→Today→刷新→关闭重开的完整 Runtime 闭环。
- 唯一风险边界：全新 task-local P3-121 工程、全新合成 SQLite、既有 `capture_record`／`get_today`／`runtime_status` 三项 IPC、离线单进程；P3-116 与 P3-120 全部资产只读。
- 包内允许：从冻结 positive allowlist 逐文件建立新候选；UI 结构／样式／交互适配；三项既有 IPC 的组合接线；离线 build/test；实际 App 回放；响应式、键盘、reduced-motion、失败关闭、Evidence／Manifest 与包内修正。
- 包内整改授权：仅在 Frozen ABF、P3-121 自有目录、唯一临时根、合成数据和三项既有 IPC 内；不得扩大能力、数据、目录、风险、冻结或阶段。
- 必须拆分：新增／修改 IPC、Schema/API 或架构；真实数据／DB／路径／输入；clear/export/权限/恢复；模型、网络、云／第三方；风险关闭／重开；资产冻结；工程基线恢复；Stage 4；以及组合候选完成后的全新隔离独立复评。
- 是否适用 P3 Engineering Fast Lane：No；关键产品 UI 与 Tauri/IPC、SQLite 生命周期组合属于 P0 高风险。
- 推荐执行 Agent：Codex，全新工程执行会话。
- 推荐理由：需要同时理解 P3-116 产品／视觉合同、P3-120 Rust/Tauri/SQLite 实现和实际 App Evidence，且必须避免由旧执行上下文自证。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：跨关键产品视觉、交互身份、Tauri IPC、SQLite 生命周期与 Evidence 真实性，需要高强度综合判断。
- 允许降级模型：None
- 禁止降级条件：全部范围。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：None
- 是否需要后续独立评审：Yes；本任务 PM Pass、用户采纳后，另建全新隔离组合候选独立复评任务。本轮不创建。
- 是否允许修改工程文件：Yes；仅 P3-121 自有目录。
- 是否允许修改项目账本：No。
- 主责角色：产品 UI／前端集成、Tauri Runtime、QA 与 Evidence。
- 协审角色：产品架构、体验设计、技术架构、数据安全、AI 信任、无障碍与 Evidence QA。
- 必须通过关卡：设计合同继承、实际 App 三 viewport、核心页面／态、三 IPC 合成生命周期、身份语义、失败关闭、禁止能力关闭态、历史保全、Manifest 与精确清理。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/2 / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-121-v1`
- ABF SHA-256：`b5d3597a5460983ffda923aa65f9aa23218dc1aa6730a171b0183e5062c53a03`
- ABF 状态：Frozen
- 正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0485`。
- 执行授权方式：用户将本最终任务卡绝对路径投递至全新合格 Codex 工程会话即启动 Frozen 范围；只在 PM 主会话查看路径或转述不启动。
- 投递前额外用户确认：Completed；用户已明确确认 `lifeos/engineering/LIFEOS-P3-121/`、`/private/tmp/lifeos-p3-121-combined-v1`、全新合成 DB、仅既有三项 IPC，并禁止 Pilot、真实 DB、真实路径、真实文本、网络和模型。

## 为什么这是新任务而不是 P3-120 Rework

P3-120 已在其 Frozen ABF 下 PM Pass，并且两轮正式 Rework 已用完。P3-116 视觉忠实度未被冻结入 P3-120 L2，不能追溯改成 P3-120 的失败标准。把明确的视觉用户结果加入实际 Runtime 候选会改变本轮完成定义与候选目录，因此依 D-0401 必须新建 P3-121、新授权和新 ABF，而不是继续膨胀 P3-120。

P3-116 的关闭原因主要是动态 Evidence／隐私取证链未闭合，不等于其产品方向被否定。P3-121 继承的是 P3-116 当前只读源码及 `visual_contract.json`、`interaction_contract.md`、`ia_reconciliation.md` 中可机器／人工复核的设计合同；不得把 P3-116 受污染、空白或过时截图作为通过依据。

## 唯一用户结果与设计忠实口径

组合候选必须同时成立：

1. **同一产品 Shell**：窄 Icon Rail；一级 IA 仅 Today、Me、Contexts、Memory；Settings 为底部弱化入口；无宽 Sidebar、通知中心／铃铛、左下头像或账户 Profile；Global AI 始终可达，Quick Capture 为独立次级动作。
2. **同一产品气质**：克制、轻量、大量留白、Apple/macOS 邻近、弱 Dashboard、个人空间感；系统字体、柔和非纯白背景、低饱和层次、安静卡片与克制蓝／薄荷／淡紫身份色。
3. **同一信息层级**：Today、Me、Contexts、Context Detail、Memory、Memory Detail、Global AI Side Panel、AI Workspace 的顺序、对象身份和用户权威符合 P3-116 合同及 IA V1.0。
4. **同一响应式合同**：1280×1024、1160×768、700×760 使用同一 DOM 自适应；不得要求用户调整系统显示缩放；窄屏堆叠但保留 Icon Rail、Global AI、主操作与完整标题。
5. **同一可访问性合同**：语义 landmarks、skip link、原生按钮、可见焦点、真实键盘关闭、reduced-motion、非纯颜色身份标签。
6. **Runtime 不退化**：P3-120 已通过的三项 IPC、合成 capture→Today→重复→第二次 capture→刷新→关闭重开、离线状态、失败关闭、路径／文件类型和禁止能力边界全部保持。
7. **内容身份不混淆**：持久化 synthetic capture、只读 fixture、AI Observation／Inference／candidate、用户确认内容和 disabled 模型状态在 UI 与数据层均可区分。

本任务不是逐像素复制 P3-116 的历史截图。Pass 依据是冻结 source／contract、实际 P3-121 App 状态和逐项可观察合同；视觉差异若不改变冻结层级、空间关系、身份色语义、响应式或产品气质，只能记为 P2，不能移动终点。

## 允许写入与环境

本任务仅允许：

- `lifeos/engineering/LIFEOS-P3-121/`
- `lifeos/deliverables/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md`
- `lifeos/local_prechecks/` 中 P3-121 专属报告（如适用）
- `/private/tmp/lifeos-p3-121-combined-v1`

编译 cache、测试 DB、app data、截图辅助物和 disposable mutation 必须位于 P3-121 自有目录或唯一临时根。结束时精确清理唯一临时根；不得使用宽前缀、glob、`find` 或不确定变量删除。

## 只读输入与 positive allowlist

PM 已在正式冻结时复算并固定：

- `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- P3-116 的 `index.html`、`styles.css`、`app.js`、`fixtures.js`、`visual_contract.json`、`interaction_contract.md`、`ia_reconciliation.md`、`state_machine.json`
- `lifeos/reviews/LIFEOS-P3-116_pm_review.md`（只用于理解历史状态和不可使用的旧 Evidence）
- `lifeos/engineering/LIFEOS-P3-120/evidence/final-manifest-closure/FINAL_MANIFEST.json`
- `lifeos/reviews/LIFEOS-P3-120_pm_reacceptance_review.md`
- `lifeos/tasks/LIFEOS-P3-121_source_allowlist.md`：P3-120 candidate 70/70 精确 positive source allowlist，SHA-256 `99220398b03baad9acdc3d88d38ab822ed661b926ec740317c5f05ce6e14a242`

禁止递归复制 P3-116／P3-120 根；只能从 Frozen allowlist 逐文件复制。P3-116/P3-120 的任务卡、ABF、候选、Review 与全部 Evidence 保持只读；不得复制受污染 AX、空白动态截图、历史临时 DB、target/cache 或任何 Pilot 资产。

## 最小启动包与定向补读

专项会话必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 Frozen `ABF-P3-121-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. 两份架构／IA 输入
8. P3-116 `visual_contract.json`、`interaction_contract.md`、`ia_reconciliation.md`
9. `lifeos/reviews/LIFEOS-P3-116_pm_review.md`
10. `lifeos/reviews/LIFEOS-P3-120_pm_reacceptance_review.md`
11. P3-120 Final Manifest 与 `lifeos/tasks/LIFEOS-P3-121_source_allowlist.md`

高风险定向补读：`PM_OPERATING_MODEL.md` 的 Tauri/IPC、P0、真实能力、Evidence、会话隔离与独立评审章节；`ROLE_MATRIX.md` 的 Codex 工程、产品／技术架构、数据安全、AI 信任、体验与 QA；`STAGE_GATES.md` 的关键原型独立评审、正式 MVP 和 Stage 3→4 区分；`PROJECT_CONTEXT.md` 的产品定位与当前 Person-centered 方向；`TASK_REGISTRY.md` P3-113～P3-121；`DECISION_LOG.md` D-0468、D-0472～D-0485；`RISK_LOG.md` R-0024/R-0025/R-0040/R-0051/R-0052。

## 实现与 Evidence 合同

1. 工程动作前复算正式 Frozen 输入、positive allowlist、模型、目录和授权；任一冲突在创建工程／临时根前停止。
2. 仅逐文件建立 P3-121 新候选；P3-116 只提供产品／视觉合同，P3-120 只提供已通过 Runtime 源码，不原地修改任何历史候选。
3. 实际 App 逐页证明 Shell、信息层级、身份、交互和三个 viewport；不得用源码存在、单张总图、旧 P3-116 screenshot 或相邻动作代替。
4. 视觉 Evidence 每一冻结页面／状态分别记录 app build hash、viewport、操作、可观察结果、结构化结果 ID、实际 screenshot path/hash 和结论；重复 screenshot hash 若对应不同可观察状态必须 fail closed。
5. 实际 App 复跑 P3-120 合成 Runtime 生命周期与负向边界；不得用 unit test 替代 renderer→IPC→DB→UI 的实际闭环。
6. 对刷新、关闭重开、键盘、reduced-motion、合法空状态、证据不足、Context/Memory identity、Global AI disabled/model-off、路径链接、DB/sidecar 类型和失败先于变更分别生成 Evidence。
7. runner 必须验证页面／状态闭环、source/candidate lineage、screenshot 非空／尺寸／唯一语义绑定、结构化结果、历史 hash、Manifest 和 cleanup；在 pristine disposable control 通过后，对关键遗漏／篡改执行 mutation fail-closed。
8. 提交 Final Manifest 前不得再修改 candidate；Final Manifest 必须明确区分历史只读输入、P3-121 current candidate、执行 Evidence、交付物和授权输入。

## 非范围与停止条件

- 不访问、定位、stat、hash、打开、复制或清理 Pilot-1/Pilot-2、真实用户目录、真实 DB、真实文件或真实文本。
- 不新增或改变三项 IPC、capability、Schema/API、技术架构或核心领域语义。
- 不启用 clear、export、权限设置、恢复、Vault、文件选择／导入、模型、网络、云／第三方、同步、多设备、L3、外部用户、通知中心或真实健康建议。
- 不把 P3-116 历史动态 Evidence 当作当前 App Pass；不恢复已删除污染文件；不覆盖 P3-116/P3-120 历史资产。
- 不使用 P3-119 GUI event helper、全局事件注入、AX export、CDP/HTTP/WebDriver 作为 Pass 依赖。
- 如实现必须改变 IPC、Schema/API、数据类型、真实路径、系统权限、网络、模型、目录或正式 ABF，立即停止并回 PM；不得在 P3-121 内无限膨胀。
- 不冻结产品／Runtime／架构，不关闭／重开风险，不恢复工程基线，不创建独立复评，不进入 Stage 4。

## 交付与治理边界

- 交付物：`lifeos/deliverables/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md`
- 工程／Evidence：`lifeos/engineering/LIFEOS-P3-121/`
- 专项只可报告 Candidate Ready / Not Pass / Blocked，并明确 P0/P1/P2/Unknown/Not Implemented。
- 本地模型预检可因关键 UI、Tauri/IPC、持久化和 Evidence 高风险最终判断跳过，但必须说明；不得替代 PM 判断。
- PM Pass 后仍须用户采纳；随后才可由 PM 创建全新隔离组合候选独立复评任务与新 ABF。
- 独立 Pass 仍不自动 Frozen、不关闭风险、不恢复工程基线、不启用真实数据或进入 Stage 4。

## 当前启动状态

精确 synthetic-only Tauri/IPC 执行确认、固定输入复算、70/70 positive allowlist 和 `ABF-P3-121-v1` 冻结均已完成。用户可将本任务卡绝对路径投递至全新 `gpt-5.6-terra + xhigh` Codex 工程会话启动；专项必须先完成启动前质疑窗口，且不得越出 Frozen 边界。
