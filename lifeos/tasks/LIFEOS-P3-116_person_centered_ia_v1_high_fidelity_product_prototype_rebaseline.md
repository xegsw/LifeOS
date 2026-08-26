# LIFEOS-P3-116｜Person-centered IA V1.0 与高保真产品原型重基线

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务只使用项目内只读产品材料、固定非敏感合成内容和 task-local 本地原型目录；不访问真实个人／工作／健康数据、retained Pilot、真实 DB／文件、Tauri/IPC、模型、网络、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-116`
- 任务名称：Person-centered IA V1.0 与高保真产品原型重基线
- 优先级：P0
- 任务类型：受控产品设计能力包；本地代码原生高保真交互原型、交互／视觉合同与 Evidence，不是 runtime 工程实现。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：把用户最新确认的 Person-centered IA、产品规则和视觉方向收敛为一套一致、可操作、可评审的高保真产品原型；不修改真实能力、架构、风险、冻结或阶段。
- 包内允许工作：IA 调和、页面／状态设计、信息层级、视觉系统、HTML/CSS/JS 原型、固定合成场景、交互状态机、响应式、无障碍、动态 Evidence、runner、Manifest 和文案对齐。
- 包内整改授权：仅限 P3-116 task-local 原型、合同、测试与 Evidence；不得扩大到 runtime、真实数据／模型／网络、工程、风险、冻结或阶段。
- 必须拆分：核心 IA／领域／架构／Schema/API 的后续改变；Tauri/IPC/DB；真实数据、路径、文件、模型、网络、连接器；风险关闭／重开；关键资产冻结；工程基线；Stage 4；以及最终全新隔离独立评审。
- 建议篇幅：交付报告 3000–5000 字；完整页面、状态与 Evidence 写入任务目录。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新产品设计／前端原型会话。
- 推荐理由：需要同时调和产品 IA 与架构语义，完成多页面信息层级、Global AI 上下文、用户权威、证据链、无障碍、响应式及机器可复核动态 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 关键产品候选涉及主体、核心 IA、领域语义、AI 权威、健康边界和复杂交互状态，需要高强度综合判断。
- 允许降级模型：None
- 禁止降级条件：本任务全部范围；不得降低产品、信任、安全、Evidence 或多页面一致性判断强度。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用且经用户／PM明确同意后使用。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后另建全新隔离关键产品原型独立评审。本轮不创建。
- 是否允许修改工程文件：No；不得修改任何 `lifeos/engineering/` 或 Tauri/runtime 候选。
- 是否允许修改项目账本：No。
- 主责角色：产品架构负责人 + 体验设计负责人。
- 协审角色：数据／领域模型、AI 信任与安全、用户研究、可访问性、技术可行性和 Evidence QA。
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3；Gate 4 只核对原型与架构调和边界；Gate 5 只形成可测试假设，不得判真实价值通过。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-116_person_centered_ia_v1_high_fidelity_product_prototype_rebaseline_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-116-v1`
- ABF SHA-256：`220d3d73ef7a54f6be689bf2cdb05fb85c25d8118562fbb4788ef6a48a4d63cf`
- ABF 状态：Frozen
- 本任务正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0468`
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话，即授权执行本 Frozen 范围；只在 PM 主会话查看路径不启动。
- 会话隔离：必须新建产品设计／前端原型会话；不得复用 P3-113 产品定义、P3-114 独立评审、P3-115 原型执行或当前 PM 主会话。
- 投递前额外用户确认：None。任何真实数据／文件／DB／模型／网络、Tauri/IPC、外部设计服务、付费资源、架构／Schema/API、风险、冻结或阶段动作必须停止并回 PM。
- 授权证据：首份会话报告记录任务卡绝对路径、接收时间、会话类型、实际模型／推理强度、ABF ID/hash、允许目录和独立性声明。

## 背景与治理结论

P3-113 已完成、获用户采纳并转为只读；P3-114 已完成独立产品评审并获用户采纳。P3-115 在其原 Frozen ABF 下获得 PM Pass，但用户最新确认的 IA 将首页从 1–3 建议改为最多一个 Today's Focus，新增 Today／Me／Contexts／Memory 一级 IA、Global AI／AI Workspace、扩展 Context 与 Memory 产品语义，并确认新的 Global Shell 视觉规则。这些变化需要实质修改旧 ABF，因此依 D-0401 不能在 P3-113 或 P3-115 内继续 Rework。

用户已确认不把 P3-115 采纳为当前目标版本；其 PM Pass 仍是原 ABF 下的历史事实，全部资产只读保全。P3-116 是全新结果、目录、授权和 ABF，不追溯否定旧候选。

## 正式产品规则优先级

遇到冲突时依次使用：

1. 当前项目正式 Frozen／Accepted 主账本和 L1 长期质量原则。
2. 本任务卡记录的用户最新 Person-centered 产品规则。
3. `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`。
4. `ABF-P3-116-v1` 的本轮一次性验收依据。
5. `lifeos/architecture/LifeOS架构基线V1.0.md` 中与前述规则兼容的架构原则。
6. P3-115、旧 Frozen 原型及用户可能重新提供的探索图片，仅作历史／视觉参考。

若 1–5 出现不能通过语义分层调和的冲突，停止并提交 PM 待决策问题；不得自行覆盖。

## 启动前验收依据冻结

- `ABF-P3-116-v1` 已在专项启动前冻结；它只冻结本轮验收依据，不冻结产品、架构或视觉资产。
- 执行方在创建任何原型文件前必须核对 ABF hash、七项固定输入、规则优先级、页面／状态集合、唯一写入目录和 Chrome `file:` Evidence 合同。
- 执行方拥有一次标准质疑窗口；任何主体、IA、Context、Memory、AI 权威、页面结果或架构调和歧义必须在开始前停止并回 PM。
- 启动后不得修改 ABF；若需改变本轮用户结果、核心语义、目录、能力或授权，当前任务关闭并新建任务。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-116-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
8. `lifeos/architecture/LifeOS架构基线V1.0.md`
9. `lifeos/reviews/LIFEOS-P3-113_pm_review.md`
10. `lifeos/reviews/LIFEOS-P3-114_pm_review.md`
11. `lifeos/deliverables/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract.md`
12. `lifeos/reviews/LIFEOS-P3-115_pm_review.md`

高风险定向补读：

- `lifeos/PROJECT_CONTEXT.md`：产品定位、宪法、历史产品资产及其适用性。
- `lifeos/PM_OPERATING_MODEL.md`：关键原型、两层验收、会话隔离、动态 Evidence、独立复评和冻结区分章节。
- `lifeos/ROLE_MATRIX.md`：产品架构、体验、数据／领域、AI 信任、用户研究和技术角色。
- `lifeos/STAGE_GATES.md`：Gate 1–5、关键原型独立评审与 Stage 3→4。
- `lifeos/FREEZE_STATUS.md`：历史 Frozen 资产与 Not Frozen 后继候选叠加规则。
- `lifeos/TASK_REGISTRY.md`：P3-113 至 P3-116。
- `lifeos/DECISION_LOG.md`：D-0401、D-0457 至 D-0468。
- `lifeos/RISK_LOG.md`：R-0001～R-0018、R-0040、R-0051、R-0052。

不要主动读取真实 Pilot、无关工程 Evidence 或无关历史交付物。探索图片只有在用户于专项会话重新提供时才读取；未提供不阻塞。

## 必须继承的产品定义

1. Person 是一级主体；Domain 是长期生活视角；Project 只是 Context 的一种。
2. MVP 1.0 广泛承接人生数据，但仅 Work 与 Health/Fitness 启用深度智能。
3. 新 Domain 一次只激活一个，须经过数据、价值、反馈和安全 Gate。
4. Today 按 Person 整体优先级分配注意力，不按 Domain 平均发卡。
5. 一级 IA 仅 Today、Me、Contexts、Memory；Settings 为底部弱化辅助入口。
6. Global AI 常驻所有主要页面，继承 Person/Page/Selection Context；复杂任务渐进展开为 AI Workspace。
7. Context 是 Person 当前正在经历、推进或持续关注之事的上下文容器；系统只能建议，不能静默创建。
8. Memory 是长期记忆与 Evidence Browser，必须区分用户原文、确认事实、AI Observation、AI Inference、Decision、Derivation、External Source。
9. AI 不替用户确认；重要事实、Action、Decision 和状态变化必须允许确认、编辑、拒绝、忽略或纠正。
10. 重要 AI 判断必须有 Evidence／为什么；不足时明确表达没有足够证据。

## 必须完成的页面与状态集合

在 `lifeos/prototypes/LIFEOS-P3-116/` 交付完全本地、无构建依赖、可由 Chrome 直接 `file:` 打开的代码原生原型：

1. **Global Shell**：窄 Icon Rail，仅图标默认可见并有 hover 文字提示；无宽 Sidebar、通知中心／铃铛、左下头像或账户 Profile；Settings 弱化；Global AI 始终可达。
2. **Today**：整体状态 → 最多一个 Today's Focus → LifeOS noticed → 用户已确认安排 → Recent → Global AI；覆盖正常、合法空状态和证据不足状态。
3. **Me**：现在的我 → 正在关注 → 长期视角 → LifeOS 对我的理解；不是 Profile；显示 Work/Health 深度智能与其他 Domain 未启用状态；理解可追溯、纠正、撤回。
4. **Contexts**：按正在进行／持续关注／已结束组织，不做 Kanban 或 Domain 分栏；覆盖 Project、Period/Program、Goal-related、Life Event、Observed Context 类型以及“建议创建但待确认”。
5. **Context Detail**：现在 → Next → 最近发生 → LifeOS understands → Related/Evidence；Global AI 自动继承当前 Context。
6. **Memory**：长期记忆与 Evidence Browser；身份、来源、确认状态和适用范围可见，不做笔记列表、文件夹知识库或 KPI Dashboard。
7. **Memory Detail**：可沿 AI Understanding → Derivation → Evidence → Source/Artifact 回到原始依据，覆盖断链和证据不足。
8. **Global AI 展开态**：显示 Person/Page/Selection Context，允许临时移除某类 Context，且不得静默改变持久事实。
9. **AI Workspace**：左侧全局导航，中部 Conversation + Work，右侧 Context Inspector；可嵌入 Observation、Evidence、Suggested Action、Decision Candidate、Plan 与未来 Agent Task，占位必须诚实；重点验证 Work + Health 跨领域理解。

## 核心交互与视觉合同

- Today → 查看 Focus/noticed 依据 → 进入 Context → 确认／调整下一步。
- 任意页面 → Global AI／Quick Capture → 输入固定 synthetic 内容 → 保留原文 → 建议关联 Domain／Context → 用户确认或忽略。
- Global AI／AI Workspace → 选择 Work + Health Context → 查看依据 → 区分 Observation/Inference → 生成候选 → 用户确认 Action／Feedback。
- Contexts → Context Detail → 继续工作并查看 Next／Evidence。
- Memory／Global AI → 回答“为什么当时这么决定”并回溯 Decision／理由／Source。
- 视觉方向：克制、轻量、大量留白、接近 Apple/macOS、弱 Dashboard 感和个人空间感；不得为填充页面强行生成模块。
- 应用适应 1280×1024、1160×768、700×760 三个固定 viewport；不得要求调整系统显示缩放来适应原型。
- 语义 HTML、skip link、可见焦点、实际 Tab/Shift+Tab/Enter/Escape、合理对比度和 reduced-motion 必须成立。

## 允许修改与严格只读

仅允许写入：

- `lifeos/prototypes/LIFEOS-P3-116/`
- `lifeos/deliverables/LIFEOS-P3-116_person_centered_ia_v1_high_fidelity_product_prototype_rebaseline.md`
- `lifeos/local_prechecks/` 中本任务报告（如适用）
- `/private/tmp/lifeos-p3-116-prototype-v1`（动态验证时新建，结束精确清理）

原型目录至少包含：`index.html`、本地 CSS/JS、固定 synthetic fixture、`interaction_contract.md`、`state_machine.json`、`visual_contract.json`、`ia_reconciliation.md`、`tests/`、`evidence/` 与非自指 `MANIFEST.md`。允许本地代码生成的小型装饰资产；不得下载远程字体、图标、图片或依赖。

严格只读：P3-113/P3-114/P3-115 全部资产；两份新增架构／IA 输入；全部历史 Frozen PRD／原型；全部工程、retained Pilot、账本、风险和冻结文件。

## 动态与视觉 Evidence

- 唯一允许的本地动态环境：Google Chrome（`com.google.Chrome`），由 Computer Use 正常控制，在新标签页直接加载 `file:///private/tmp/lifeos-p3-116-prototype-v1/index.html`。
- 先做最多两次正常 `file:` 加载预检；首轮成功即停止预检并执行完整矩阵。不得使用 In-app Browser、HTTP、localhost、CDP、命令行浏览器或绕过浏览器安全策略替代。
- 每个动态动作分别记录前置状态、实际操作、可观察结果、结构化结果 ID、截图／日志路径与 SHA-256；刷新不代替关闭重开，静态可聚焦不代替实际 Tab／Enter。
- 使用 `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或结构等价 JSON；runner 必须从 raw Evidence 重算行级结果和 Manifest，缺行／hash／路径时 fail-closed。
- 截图必须来自实际代码原型，不得把探索图或静态拼图作为整页背景冒充实现。

## 非范围与停止条件

- 不修改工程或运行 Tauri，不调用 IPC、DB、文件系统能力、真实模型或网络。
- 不处理真实个人／工作／健康数据、真实文件或 retained Pilot。
- 不做删除、导出、权限设置、Vault、连接器、同步、多设备、L3、外部用户或真实健康建议。
- 不把原型状态写成已持久化、已由真实 AI 生成、已经验证用户价值或已经实现 runtime。
- 不自行修改一级 IA、Context／Memory／Global AI 核心语义或架构基线；无法调和时停止并列为 PM 决策。
- 不冻结产品／原型／架构，不替换历史 Frozen 记录，不关闭／重开风险，不恢复工程基线，不进入 Stage 4。

## 交付、自检与 PM 所需输出

- 原型：`lifeos/prototypes/LIFEOS-P3-116/`
- 完整交付物：`lifeos/deliverables/LIFEOS-P3-116_person_centered_ia_v1_high_fidelity_product_prototype_rebaseline.md`
- Evidence：`lifeos/prototypes/LIFEOS-P3-116/evidence/MANIFEST.md`
- 交付物至少包括：当前状态与继承原则、与 IA V1.0／架构基线对应关系、最终页面／状态集合、核心交互、与 P3-115 变化矩阵、未解决问题、用户／PM 待决策项、PM 验收建议和下一阶段准入判断。
- 自检从干净 task-local 副本覆盖首次、重复、刷新、关闭重开、空／不足／失败状态、上下文移除、用户确认生命周期、键盘、reduced-motion 和三个 viewport。
- 必须提供结构化逐行结果、raw logs、完整截图、历史 hash、隐私／网络／远程资源扫描、mutation fail-closed、复跑命令、非自指 Manifest 和精确清理证明。
- 执行侧明确报告 P0/P1/P2/Unknown/Not Implemented 数量；任一 ABF 行或子动作缺失不得概括性 Pass。
- 本地预检默认执行：`python3 lifeos/tools/local_precheck.py <交付物路径>`；它不能决定 PM、独立评审、冻结或 Stage 4。

## 结论与后续边界

- 专项只能报告 Candidate Ready / Not Pass / Blocked；PM 主会话作正式验收。
- PM Pass 后仍需用户采纳；随后才可由 PM 在单独授权下创建全新隔离关键原型独立评审与新 ABF。
- 独立评审、PM 验收和用户单独决定前，不形成 Frozen 产品／原型，不启动 runtime／工程，不进入 Stage 4。
- 聊天必须使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径、计数、Evidence 和 PM 待确认项。

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 产品设计／前端原型
- 独立性隔离：Yes；这是新产品结果、新 ABF 与新目录，P3-115 的旧完成定义可能污染当前判断。
- 任务完成后建议保留会话：Yes，仅用于同一 P3-116 Frozen ABF 内包内修正；不得承担后续独立评审。
