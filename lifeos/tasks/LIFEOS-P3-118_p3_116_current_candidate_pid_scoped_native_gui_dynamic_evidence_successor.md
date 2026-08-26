# LIFEOS-P3-118｜P3-116 当前候选 PID 限定原生 GUI 动态 Evidence 最终后继

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务只读验证 P3-116 当前固定 synthetic 原型候选，使用全新 task-local Chrome profile、专用 Chrome PID、PID 限定原生窗口、实际 GUI 与 macOS 原生窗口截图；不访问现有浏览器会话、真实个人／工作／健康数据、真实文件／DB、Pilot、网络、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-118`
- 任务名称：P3-116 当前候选 PID 限定原生 GUI 动态 Evidence 最终后继
- 优先级：P0
- 任务类型：受控 Evidence／隐私能力包；只读候选的本地 GUI 动态／视觉取证、verifier 与 mutation，不是产品重设计或 runtime 工程。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：用专用 Chrome 主 PID 与 PID 限定的原生窗口 attestation，消除 P3-117 的旧 hash 冲突和应用级 Chrome 选择器歧义，证明 P3-116 当前 source 的完整动态／视觉闭环。
- 包内允许工作：P3-118 自有 PID-filter helper、临时 probe、专用 profile、Computer Use GUI 操作、原生窗口截图、可审计裁剪、动作结果、verifier、mutation、Manifest、清理与交付说明。
- 包内整改授权：仅限 P3-118 自有目录、指定交付物、task-local precheck 和唯一临时根；P3-116/P3-117 及历史资产全部只读。
- 必须拆分：产品／候选／合同修改；非 PID 限定入口；其他浏览器／窗口／截图来源；真实数据／文件／DB、Tauri/IPC、模型调用、网络、CDP/DevTools/headless/WebDriver；风险关闭／重开、冻结、工程基线、独立评审和 Stage 4。
- 建议篇幅：交付报告 1800–3000 字；完整 Evidence 写入 P3-118 目录。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新本地视觉 Evidence 执行会话。
- 推荐理由：需要高风险 hash 谱、专用进程／窗口身份、GUI 隔离、原生图像 lineage、隐私 fail-closed verifier 和机器可复核 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 Evidence 真实性、浏览器隐私隔离、进程／窗口／截图身份链和历史保全需要高强度综合判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：None。
- 是否需要后续独立评审：Yes；仅在 P3-118 PM Pass 且用户采纳后，由 PM 另建全新隔离关键原型独立评审。本轮不创建。
- 是否允许修改工程文件：No。
- 是否允许修改 P3-116/P3-117：No；任务、候选、合同、Evidence、Review 与 PM Evidence 全部只读。
- 是否允许修改项目账本：No。
- 主责角色：Evidence QA + 本地 GUI 技术执行。
- 协审角色：隐私／安全、体验验证、可访问性、产品架构、视觉设计与技术可行性。
- 必须通过关卡：17 项正确固定输入、专用 Chrome PID、PID 限定唯一原生窗口、Computer Use 实际 GUI、原生 raw→proof→clean、三个 viewport、页面／状态、键盘／motion、semantic/privacy verifier、14 类 mutation、历史保全与精确清理。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-118-v1`
- ABF SHA-256：`d6f12523683beea42ecd9d9db586b41c489991286e0ee41e2eb4afeab5e5c18c`
- ABF 状态：Frozen。
- 本任务正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0475`
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话，即授权执行 Frozen 范围；仅在 PM 主会话查看不启动。
- 投递会话：必须新建 Codex 本地视觉 Evidence 会话；不得复用 P3-116/P3-117 执行会话、PM 主会话或未来独立评审会话。
- 投递前额外用户确认：None。用户已授权创建本后继与新 ABF；任何非范围入口／能力必须停止回 PM。
- 授权证据：首份会话报告记录任务卡绝对路径、接收时间、会话类型、实际模型／推理强度、ABF ID/hash、允许写入、专用 PID/window 隔离与 P3-116/P3-117 全只读声明。

## 背景与治理结论

P3-117 的执行侧正确 fail closed；PM 独立复核确认 `ABF-P3-117-v1` 错误冻结了 P3-116 PM Review 采纳前 hash `f698…`，而 D-0473 后权威文件为 `09d810…`。P3-117 还报告按 Chrome 应用选择器读取到既有普通窗口，但缺少可保留的独立窗口 Evidence，PM 将其保持 Unknown。用户已采纳 Blocked，并授权关闭 P3-117、创建全新后继与正确新 ABF。

P3-118 修正两点且不改变产品候选：第一，固定输入明确使用 D-0473 后 `09d810…`；第二，不再按 app/bundle 名称选择 Chrome，而是直接启动专用主进程、取得 PID、先按 PID 过滤唯一原生窗口并置前，再允许 Computer Use 操作。任何其他 PID/window 信息必须在序列化前丢弃。

## 启动前验收依据冻结

- `ABF-P3-118-v1` 已在专项启动前冻结，只冻结本轮 Evidence 依据，不冻结产品或原型。
- 在创建临时根、启动浏览器或写 runner Evidence 前，执行方必须独立复算 17 项固定输入，特别确认 P3-116 PM Review 为 `09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa`。
- 必须静态审计 PID helper：先按专用 PID 过滤、后序列化；禁止写出其他 PID/window/app/title/path。必须确认 Computer Use 不调用 Google Chrome app selector。
- 存在任何歧义时在动作前停止回 PM；启动后不得修改 ABF。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-118-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/reviews/LIFEOS-P3-116_pm_review.md`
8. `lifeos/reviews/LIFEOS-P3-117_pm_review.md`
9. `lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/blocked_assessment.md`
10. P3-116 八项固定候选／合同文件，仅按 ABF 列表读取
11. P3-117 任务、ABF、交付物和 Manifest，仅核对历史边界与失败原因

高风险定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：P0、浏览器动态 Evidence、会话隔离、历史保全和 PM／独立评审分界章节。
- `lifeos/ROLE_MATRIX.md`：Evidence QA、隐私／安全、体验、可访问性与技术角色。
- `lifeos/STAGE_GATES.md`：关键原型独立复评、冻结与 Stage 3→4 区分章节。
- `lifeos/FREEZE_STATUS.md`：P3-116～P3-118 Not Frozen 与历史 Frozen 叠加。
- `lifeos/TASK_REGISTRY.md`：P3-116～P3-118。
- `lifeos/DECISION_LOG.md`：D-0401、D-0469～D-0475。
- `lifeos/RISK_LOG.md`：R-0024、R-0025、R-0040、R-0051、R-0052。

不要读取真实 Pilot、现有浏览器 profile／标签／账户／历史／扩展、其他窗口／桌面、无关工程 Evidence 或无关历史。不得恢复已删除的 P3-116 AX 文件。

## 目标

回答并证明：P3-116 当前固定 source 能否在严格 task-local、无 ambient、无网络的实际 GUI Chrome 环境中，通过专用 PID 和 PID 限定窗口身份完成冻结页面／状态／交互、三个 viewport、键盘／motion、语义／隐私 verifier、mutation 与精确清理闭环。

## 允许写入与严格只读

仅允许写入：

- `lifeos/prototypes/LIFEOS-P3-118/`
- `lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md`
- `lifeos/local_prechecks/` 中本任务报告
- `/private/tmp/lifeos-p3-118-native-capture-v1`

严格只读：P3-113 至 P3-117 全部任务、ABF、原型／候选、合同、fixture、交付物、Review、Evidence、PM Evidence；历史 Frozen 资产、工程、账本、风险、冻结和 retained Pilot。

## 执行合同

1. 在任何临时写入前复算 17 项固定输入；任一不匹配立即 `BLOCKED_FIXED_INPUT_MISMATCH`，不得创建临时根。
2. 从空唯一临时根复制 P3-116 八项候选／合同；复制前后 source hash 一致，仅在临时 `index.html` 附加 hash 固定的只读 probe。
3. 直接启动冻结的 Chrome executable 与参数，保存返回主 PID；不得使用 `open -na`、按名称／bundle 选择 Chrome、地址栏输入、HTTP、localhost 或其他入口。
4. task-local helper 只接收该 PID，必须先 PID 过滤再序列化。过滤后须恰一层 0、onscreen window；只允许记录 target PID/window ID/bounds/layer/frontmost/executable hash/布尔结果。
5. helper 将唯一窗口置前并生成 attestation 后，Computer Use 才可在当前前台窗口做正常 GUI 点击／键盘；禁止 app selector、窗口切换器、Dock、Mission Control。每个动作前后重新 attestation；不一致立即停止且不截屏。
6. `screencapture` 仅用已 attested window ID；保留 raw window、probe-visible proof、probe-hidden clean crop、geometry、parent hash 和 action lineage。
7. 完整执行 ABF-M-004～M-012 每个子动作；每项唯一 capture/attestation ID，不得用静态扫描、脚本 DOM/state 修改、空白／重复图或相邻动作替代。
8. verifier 从 raw Evidence 重算固定输入、PID/window、图片、crop、viewport、动作/state、source、probe 隐藏、ambient/browser chrome 禁止项、Manifest 与 cleanup。
9. clean disposable control 先 PASS 后运行 14 类 mutation；每类必须以唯一精确原因非零退出。
10. 结束时只关闭命令行仍含精确 task-local profile 的专用 PID及其子进程；禁止 `pkill`、按名称／pattern 关闭 Chrome。随后精确删除唯一临时根并验证不存在。
11. 任一必填行缺失，自检必须 Not Pass／Not Implemented，不得提交概括性 Pass。

## 动态闭环与 Evidence

- 逐行动作集合继承 P3-117 `test_plan.json` 的 46 个冻结动作语义，但必须在 P3-118 自有计划中重新生成，不得把 P3-117 静态计划当作实际 Evidence。
- 每个动作必须记录：前置 state、PID/window attestation、Computer Use 实际操作、可观察结果、结构化 result ID、raw/proof/clean/geometry/log path 与 SHA-256。
- 三个 viewport 必须由 probe 实测 inner size，不得用 outer window config 或截图尺寸推断。
- 刷新不得替代关闭重开；AX/静态 focus 不得替代实际 Tab/Enter；脚本 state mutation 不得替代 GUI。
- Manifest 非自指并覆盖全部 runner、helper、probe、attestation、图像、geometry、actions、results、mutations、cleanup 和交付物引用。

## 非范围与停止条件

- 不修改 P3-116/P3-117 或本 ABF；不重新设计 IA、视觉、交互或文案。
- 不读取、控制、截图或记录其他 Chrome 进程／窗口、其他 app 或桌面；不得导出 AX/browser metadata。
- 不使用网络、搜索、HTTP(S)、localhost、CDP、DevTools、headless、WebDriver、浏览器服务、全屏截图、远程资源或新外部依赖。
- 不运行工程／Tauri／IPC／DB／模型，不处理真实数据／文件／Pilot。
- PID、window ID、frontmost、精确 `file:` 或唯一性任一无法证明，立即停止；不得改用 app selector、其他浏览器或其他取证路径。
- 不关闭／重开风险，不冻结产品／原型／架构，不恢复基线，不进入 Stage 4。

## 交付、自检与 PM 所需输出

- 交付物：`lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md`
- Evidence：`lifeos/prototypes/LIFEOS-P3-118/MANIFEST.md`
- 必须报告授权／会话／实际模型、ABF hash、17 项输入、P3-116/P3-117 保全、PID/window 隔离、probe 审计、15 行矩阵及46个子动作、图像链、三个 viewport、verifier、14 类 mutation、清理、五类计数与 PM 待决策项。
- 完整保存 runner、结构化 JSON、动作日志、attestation、图像、geometry、hash、Manifest 和复跑说明。
- 本地预检默认执行；但禁止网络的本任务可因本地模型需要局域网而跳过，必须记录理由。
- 专项只能报告 Candidate Ready / Not Pass / Blocked；不得改账本、宣告 PM Pass／Accepted／Frozen、创建后续任务或启动独立评审。

## Pass、Rework 与后续边界

- Pass 公式以 `ABF-P3-118-v1` 为唯一 L2；P0/P1/P2/Unknown/Not Implemented 必须全零。
- 同任务 Rework 仅限 P3-118 自有 Evidence 实现且 ABF 不变；入口、PID/window 策略、工具或 ABF 变化必须关闭并新建任务。
- PM Pass 后仍需用户采纳；采纳后才可由 PM另建全新隔离关键原型独立评审。
- P3-118 Pass 不追溯把 P3-116/P3-117 改写为 Accepted，不冻结资产，不证明 runtime／真实使用价值或 Stage 4 准入。

## 会话路由

- 是否建议新建会话：Yes。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 本地视觉 Evidence 执行。
- 隔离原因：P3-117 已关闭且其会话遇到固定输入和 app selector 冲突；新任务改变 Frozen 进程／窗口身份入口，必须隔离旧上下文、浏览器和授权。
- 是否需要独立性隔离：Yes；本任务是执行，不是最终独立评审。
- 可复用既有读取结果：None。
- 任务完成后建议保留会话：Yes，仅用于 P3-118 同一 Frozen ABF 内包内修正；不得承担后续独立评审。
- 聊天回复：严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径、计数、Evidence 和 PM 待确认项。
