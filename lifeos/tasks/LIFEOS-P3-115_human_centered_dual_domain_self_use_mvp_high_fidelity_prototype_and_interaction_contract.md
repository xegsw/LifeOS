# LIFEOS-P3-115｜人本双领域自用 MVP 高保真原型与交互合同

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目；用户已采纳 P3-114 Independent Pass／PM Pass，并授权创建本任务。本任务只使用项目内只读产品材料和固定非敏感合成内容，在本地 task-local 目录制作代码原生交互原型；不访问真实个人／工作／健康数据、retained Pilot、真实 DB、Tauri/IPC、模型、网络、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-115`
- 任务名称：人本双领域自用 MVP 高保真原型与交互合同
- 优先级：P0
- 任务类型：受控产品设计能力包；本地代码原生高保真交互原型 + 交互合同 + Evidence，不是 runtime 工程实现。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：把已通过 P3-114 独立评审的 P3-113 人本双领域候选，转化为可在本地 Chrome `file:` 打开的高保真交互原型，证明关键状态、身份、反馈和安全降级能被清楚表达。
- 包内允许工作：信息层级、视觉系统、HTML/CSS/JS 原型、固定合成场景、交互状态机、响应式／可访问性、动态 Evidence、runner、Manifest 和文案对齐。
- 包内整改授权：仅限 P3-115 task-local 原型与 Evidence；不得扩大到产品重定义、runtime、真实能力、风险、冻结或阶段。
- 必须拆分：P3-113 产品语义变化；Schema/API；Tauri/IPC/DB；真实数据、路径、模型、网络、连接器；风险关闭／重开；关键原型冻结；工程基线；Stage 4；以及最终独立复评。
- 建议篇幅：交付报告 2000–4000 字；完整状态与 Evidence 写入任务目录。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新产品设计／前端原型会话。
- 推荐理由：需要同时处理产品语义、视觉层级、交互状态机、无障碍、响应式和机器可复核动态 Evidence；又必须避免继承旧 Project-first 实现语境。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 关键原型候选涉及产品中心、内容身份、健康安全和复杂交互状态，需要高强度综合判断。
- 允许降级模型：None
- 禁止降级条件：本任务全部范围；不得降低产品／健康／Evidence 判断强度。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用且经用户／PM明确同意后使用。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后另建全新隔离关键原型独立评审。本轮不创建。
- 是否允许修改工程文件：No；不得修改任何 `lifeos/engineering/` 候选。
- 是否允许修改项目账本：No。
- 主责角色：体验设计负责人 + 产品架构负责人。
- 协审角色：数据／领域模型、AI 信任与安全、用户研究、可访问性、技术可行性与 Evidence QA。
- 必须通过：Gate 1、Gate 2、Gate 3；Gate 4 只核对原型可实现性边界；Gate 5 只形成可测试假设，不得判真实价值通过。
- 状态：`Ready / Acceptance Basis Frozen v2 / Awaiting Task-card Re-read / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-115-v2`
- ABF SHA-256：`3dee373444132933bb927a6b8bf39550981663d3f9420d4bdbce5eb7a620f9f2`
- ABF 状态：Frozen
- 本任务正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0466`（v2 启动前谱系对齐；任务创建授权仍来自 D-0465）
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话即授权执行本 Frozen 范围；仅在 PM 主会话查看路径不启动。
- 会话隔离：必须新建产品设计／前端原型会话；不得复用 P3-113 定义、P3-114 独立评审、旧 P3-105/P3-106 工程或当前 PM 主会话。
- 投递前额外用户确认：None。任何真实数据／模型／网络、Tauri/IPC/DB、外部设计服务、付费资源、产品语义变化、冻结或阶段动作必须停止并回 PM。
- 授权证据：首份会话报告记录任务卡绝对路径、接收时间、会话类型、实际模型／推理强度、ABF ID/hash、允许目录和独立性声明。

## 背景与产品继承

P3-113 将 LifeOS 一级主体重基线为 Person，Project 仅是工作领域上下文；定义了工作 + 健康／健身双领域七段闭环、1–3 件首页重点、0–1 个会改变判断的问题、Source／Artifact／Derivation／Advice／Feedback 身份、完整反馈→执行→结果→理解更新链和健康失败关闭。P3-114 已完成全新隔离独立评审并经 PM 复验通过，用户现已采纳。

旧三张 `LifeOS 精修版` 静态原型及 P3-105/P3-106 只作为历史事实和空间／克制／可读性参考；其 Project-first 首页、旧信息架构、状态样例和视觉锚点不是 P3-115 的权威输入。P3-115 必须从人本双领域产品结果重新组织界面，不得只是给旧页面换文案。

## 启动前验收依据冻结

- `ABF-P3-115-v2` 已在专项启动前重新冻结；v2 只把 P3-114 PM Review 固定输入从采纳前 hash 对齐到采纳后当前 hash，不改变验收标准、范围、矩阵或授权。它只冻结本轮原型验收依据，不冻结产品需求或最终资产。
- 执行方在任何原型文件创建前必须核对 ABF hash、固定输入、唯一写入目录、Chrome `file:` 预检要求与历史只读边界。
- 执行方拥有一次标准质疑窗口；如页面／状态／身份／交互合同有歧义，必须在开始前停止并回 PM。
- 启动后不得修改 ABF；需要改变 P3-113 语义、页面结果、真实能力或视觉权威时，当前任务关闭并新建任务。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-115-v2`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline.md`
8. `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md`
9. `lifeos/reviews/LIFEOS-P3-113_pm_review.md`
10. `lifeos/reviews/LIFEOS-P3-114_pm_review.md`
11. `lifeos/reviews/LIFEOS-P3-114/rework/rework-1/independent_review.md`

高风险定向补读：

- `lifeos/PROJECT_CONTEXT.md`：产品宪法、产品定位、当前原型状态和历史适用性。
- `lifeos/PM_OPERATING_MODEL.md`：会话隔离、关键原型、两层验收、动态 Evidence、独立复评和冻结区分章节。
- `lifeos/ROLE_MATRIX.md`：产品架构、体验设计、数据／领域、AI 信任、用户研究和技术角色。
- `lifeos/STAGE_GATES.md`：独立评审、Gate 1–5、Stage 3→4。
- `lifeos/FREEZE_STATUS.md`：当前核心资产及“历史工作领域基线”叠加规则。
- `lifeos/TASK_REGISTRY.md`：P3-113 至 P3-115。
- `lifeos/DECISION_LOG.md`：D-0401、D-0457 至 D-0465。
- `lifeos/RISK_LOG.md`：R-0001～R-0018、R-0040、R-0051、R-0052。

只读视觉历史参考：三张 P1-011 Frozen 截图与 P3-106 最终响应式 Evidence；仅学习克制、层级与可读性，不复制其 Project-first 结构，不作为像素比对权威。

## 必须完成的产品原型

在 `lifeos/prototypes/LIFEOS-P3-115/` 交付一个完全本地、无构建依赖、可由 Chrome 直接 `file:` 打开的代码原生原型：

1. **Person-first 今日首页**：首屏仅有 1–3 件值得记录／回答／决定／行动的事；工作与健康／健身并列为领域，Project 只出现在工作项的上下文中。
2. **0–1 个关键问题**：问题只有在回答会改变安全分类、建议是否出现、排序或下一步时出现；支持回答、跳过、未答和健康警示分支。
3. **建议与依据详情**：每条建议可查看 Why now、Source/Artifact、时间／时效、确定性、范围、停止条件和内容身份；合成数据、用户输入、AI 推断／建议、用户确认状态清楚区分。
4. **完整反馈生命周期**：认可、修改后接受、拒绝、忽略、延后、实际执行、结果和理解更新分别可见；任何一步不得互相推定。
5. **长期记忆候选**：一次结果只能形成待确认、有限范围、可撤销的 Memory candidate；用户未确认前不得影响未来日期。
6. **失败关闭状态**：来源缺失／过期／冲突／失权、问题未答、健康警示、反馈撤销和关闭重开均有明确状态；不得伪装可靠建议或医学判断。
7. **全局捕获与导航**：捕获入口可见但明确为原型，不做持久化；导航以 Person 的 Today／Memory／Domains 为主，不回退为 Project 管理后台。
8. **视觉和响应式**：形成一致、克制、温和且个人化的视觉系统，在 1280×1024、1160×768、700×760 三个固定 viewport 中关键内容／操作可达。
9. **可访问性**：语义 HTML、skip link、可见焦点、实际 Tab/Shift+Tab/Enter/Escape、合理对比度、reduced-motion；交互不只依赖颜色或动画。
10. **交互合同**：独立 Markdown／JSON 明确每个事件、前置状态、状态转换、用户可见回执、内容身份、失败后置状态和未来 runtime 对接边界。

## 允许修改与严格只读

仅允许写入：

- `lifeos/prototypes/LIFEOS-P3-115/`
- `lifeos/deliverables/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract.md`
- `lifeos/local_prechecks/` 中本任务报告（如适用）
- `/private/tmp/lifeos-p3-115-prototype-v1`（动态验证时新建，结束精确清理）

原型目录至少包含：`index.html`、本地 CSS/JS、固定合成 fixture、`interaction_contract.md`、`state_machine.json`、`visual_contract.json`、`tests/`、`evidence/` 与非自指 `MANIFEST.md`。允许本地代码生成的小型装饰资产；不得下载远程字体、图标、图片或依赖。

严格只读：P3-113/P3-114 全部任务、交付物、Review、Evidence、PM Evidence；旧 Frozen PRD／原型与 P3-105/P3-106；全部工程目录、retained Pilot、账本、风险和冻结文件。

## 动态与视觉 Evidence

- 唯一允许的本地动态环境：Google Chrome（`com.google.Chrome`），由 Computer Use 正常控制，在新标签页直接加载 task-local 副本 `file:///private/tmp/lifeos-p3-115-prototype-v1/index.html`。
- 先做两次上限内的正常 `file:` 加载预检；首轮成功即停止预检并执行完整矩阵。不得使用 In-app Browser、HTTP、localhost、CDP、命令行浏览器或绕过浏览器安全策略替代。
- 每个动态动作必须分别记录前置状态、实际操作、可观察结果、结构化结果 ID、截图／日志路径及 SHA-256；刷新不代替关闭重开，静态可聚焦不代替实际 Tab／Enter。
- 截图必须来自实际原型，不得把参考图、设计稿或静态拼图嵌入页面伪装实现；至少覆盖三个 viewport、首页主状态、依据详情、反馈生命周期、健康停止和来源失败状态。
- runner 必须从原始 Evidence 重算行级结果与 Manifest；任一必填动作、hash 或路径缺失即 fail-closed。

## 非范围与停止条件

- 不修改 `lifeos/engineering/`，不运行 Tauri，不调用 IPC、DB、文件系统能力、真实模型或网络。
- 不处理真实个人／工作／健康内容，不查找或核对 retained Pilot。
- 不做删除、导出、权限设置、Vault、连接器、同步、多设备、L3、外部用户或真实健康建议。
- 不把原型状态写成已实现、已持久化、已由 AI 生成或已产生真实用户价值。
- 不修改 P3-113 产品语义；若高保真呈现必须增加页面结果、领域、能力、身份或安全合同，立即停止并回 PM。
- 不冻结原型，不替换历史 Frozen 资产，不恢复工程基线，不关闭／重开风险，不进入 Stage 4。

## 交付与自检

- 原型：`lifeos/prototypes/LIFEOS-P3-115/`
- 完整交付物：`lifeos/deliverables/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract.md`
- Evidence：`lifeos/prototypes/LIFEOS-P3-115/evidence/MANIFEST.md`
- 必须提交：页面／状态清单、交互合同、状态机、视觉合同、动态闭环、完整截图、结构化逐行结果、历史 hash、隐私／网络／远程资产扫描、复跑命令、非自指 Manifest 和精确清理证明。
- 包内自检必须从干净 task-local 副本覆盖首次、重复、刷新、关闭重开、失败关闭、反馈撤销、键盘、reduced-motion 与三个 viewport；所有 ABF 行及子动作 PASS 后才可提交 PM。
- 执行侧必须报告 P0/P1/P2/Unknown/Not Implemented；缺项不得概括性写 Pass。
- 本地预检默认执行：`python3 lifeos/tools/local_precheck.py <交付物路径>`；它不决定 PM、独立评审、冻结或 Stage 4。

## 结论与后续边界

- 专项只可报告 Candidate Ready / Not Pass / Blocked；PM 最终验收。
- PM Pass 后仍须用户采纳；随后另建全新隔离关键原型独立评审，不由本执行会话或 PM 自证。
- 独立评审通过、PM 验收和用户明确确认后，才可单独决定是否冻结新关键原型或创建受控合成工程纵切任务；本任务不预授权。
- 聊天必须使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径、计数、Evidence 与 PM 待确认项。

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 产品设计／前端原型
- 独立性隔离：Yes；新产品结果、新 ABF、新目录，且旧 Project-first 工程语境可能污染判断。
- 任务完成后建议保留会话：Yes，仅供同一 P3-115 Frozen ABF 内包内修正；不得承担后续独立评审。
