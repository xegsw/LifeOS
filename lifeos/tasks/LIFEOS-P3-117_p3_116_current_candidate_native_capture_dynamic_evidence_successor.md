# LIFEOS-P3-117｜P3-116 当前候选隔离原生截图动态 Evidence 后继收口

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务只读验证 P3-116 当前固定合成原型候选，使用全新 task-local Chrome profile、实际本地 `file:` GUI 窗口与 macOS 原生窗口截图；不访问现有浏览器会话、真实个人／工作／健康数据、真实文件／DB、retained Pilot、网络、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-117`
- 任务名称：P3-116 当前候选隔离原生截图动态 Evidence 后继收口
- 优先级：P0
- 任务类型：受控 Evidence／隐私能力包；只读候选的本地 GUI 动态／视觉取证、verifier 与 mutation，不是产品重设计或 runtime 工程。
- 是否为受控能力包：Yes。
- 唯一能力／风险边界：以新的 Frozen 取证入口证明 P3-116 当前 source hash 的完整动态／视觉结果，并关闭空白截图、ambient metadata 和 stale Evidence 三项既有缺口。
- 包内允许工作：P3-117 自有临时 Evidence probe、专用 Chrome app-mode 启动／隔离、原生窗口截图、可审计裁剪、动作级结构化结果、语义／隐私 verifier、mutation、Manifest、精确清理和交付说明。
- 包内整改授权：仅限 `lifeos/prototypes/LIFEOS-P3-117/`、指定交付物、task-local precheck 和唯一临时根；P3-116 及历史资产全部只读。
- 必须拆分：任何 P3-116 产品／候选／合同修改；其他浏览器／截图入口；真实数据／文件／DB、Tauri/IPC、模型、网络、localhost、CDP／DevTools／headless／WebDriver、外部设计服务；风险关闭／重开、冻结、工程基线、独立评审和 Stage 4。
- 建议篇幅：交付报告 1800–3000 字；完整 Evidence 写入 P3-117 目录。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新本地视觉 Evidence 执行会话。
- 推荐理由：需要严格隔离现有浏览器状态，协调 Computer Use 实际交互、macOS 原生截图、图像裁剪、语义／隐私 fail-closed verifier 和机器可复核 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 Evidence 真实性、浏览器隐私隔离、截图来源／几何／语义链和历史保全需要高强度综合判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围；不得降低 Evidence、隐私、候选版本、视觉语义或清理判断强度。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用且经用户／PM明确同意后使用。
- 是否需要后续独立评审：Yes；仅在 P3-117 PM Pass 且获用户采纳后，由 PM 另建全新隔离关键原型独立评审。本轮不创建。
- 是否允许修改工程文件：No。
- 是否允许修改 P3-116：No；整个任务、候选、合同、Evidence、Review 和 PM Evidence 只读。
- 是否允许修改项目账本：No。
- 主责角色：Evidence QA + 体验验证负责人。
- 协审角色：隐私／安全、可访问性、产品架构、视觉设计和技术可行性。
- 必须通过的评审关卡：P3-116 当前候选 source 绑定、实际 GUI 动态／视觉闭环、浏览器隔离与 privacy fail-closed、三个 viewport、键盘／motion、mutation、历史保全和精确清理；不评独立性冻结或真实价值。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-117-v1`
- ABF SHA-256：`57d6016e338103f4f53b5e979d3ec2d5eca708e7622ade33c3ccfd8be1c2b0e0`
- ABF 状态：Frozen。
- 本任务正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0473`
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话，即授权执行本 Frozen 范围；只在 PM 主会话查看路径不启动。
- 投递授权的会话类型与隔离要求：必须新建 Codex 本地视觉 Evidence 会话；不得复用 P3-116 执行会话、P3-116 PM 主会话或未来独立评审会话。
- 投递前额外用户确认：None。任何非范围入口／能力必须停止并回 PM。
- 授权证据：首份会话报告记录任务卡绝对路径、接收时间、会话类型、实际模型／推理强度、ABF ID/hash、允许写入目录、专用 Chrome 隔离声明和 P3-116 全只读声明。

## 背景与治理结论

P3-116 初次 PM 验收发现两项 P0 和一个 Not Implemented：36 张动作截图为空白重复图却被 verifier 判 PASS；46 个 AX logs 收入 ambient Chrome metadata；最终候选 source hash 没有完整动态闭环。用户采纳 Rework 并授权删除 46 个受污染文件。

Rework-1 第一次预检误导航网络后 fail closed；第二次且最后一次 `file:` 预检成功，但当前 Computer Use 只能提供 136×159 缩略图，无法取得合格页面级高分辨率 Evidence。两次预算耗尽，P3-116 依 D-0401 已关闭为 `Closed — Acceptance Not Met / Superseded`。该失败没有否定候选产品方向，但原 ABF 的取证入口已不可继续。

P3-117 只替换取证边界：专用临时 Chrome profile + app-mode GUI + macOS 原生窗口截图 + 可审计页面裁剪链。P3-116 当前候选和产品完成定义不变、全部只读。

## 启动前验收依据冻结

- `ABF-P3-117-v1` 已在专项启动前冻结，只冻结本轮 Evidence 依据，不冻结产品或原型。
- 执行方在任何 GUI、临时文件或原型复制动作前必须核对 ABF hash、13 项固定输入、专用 Chrome 参数、probe 合同、raw→crop 链、唯一写入目录和精确清理。
- 执行方拥有一次标准质疑窗口；若 app-mode 唯一窗口定位、原生窗口截图、页面裁剪、probe 非侵入或 viewport 证明不可执行，必须在动作前停止并回 PM。
- 启动后不得修改 ABF；不能用其他浏览器、全屏截图、AX export、HTTP、localhost、CDP、DevTools、headless、WebDriver 或安装依赖替代。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-117-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. `lifeos/reviews/LIFEOS-P3-116_pm_review.md`
8. `lifeos/reviews/LIFEOS-P3-116/pm_evidence/rework-1/attempt_2_blocked_assessment.md`
9. P3-116 八项固定候选／合同文件，仅按 ABF 列表读取
10. P3-116 两个 Rework 停止 Manifest，仅核对记录与边界，不读取已删除或 ambient 内容

高风险定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：P0、动态 Evidence、会话隔离、历史保全和 PM／独立评审分界章节。
- `lifeos/ROLE_MATRIX.md`：Evidence QA、体验、隐私／安全、可访问性与技术角色。
- `lifeos/STAGE_GATES.md`：关键原型独立复评、冻结与 Stage 3→4 区分章节。
- `lifeos/FREEZE_STATUS.md`：P3-116/P3-117 Not Frozen 与历史 Frozen 叠加。
- `lifeos/TASK_REGISTRY.md`：P3-116/P3-117。
- `lifeos/DECISION_LOG.md`：D-0401、D-0469～D-0473。
- `lifeos/RISK_LOG.md`：R-0024、R-0025、R-0040、R-0051、R-0052。

不要读取真实 Pilot、现有浏览器 profile／标签／账户／历史／扩展、无关工程 Evidence 或无关历史。不得尝试恢复已删除的 P3-116 AX 文件。

## 目标

回答且证明一个问题：P3-116 当前固定 source hash 的 Person-centered 高保真原型，能否在严格 task-local、无 ambient、无网络的实际 GUI Chrome 环境中，完成原冻结页面／状态／交互、三个 viewport 和可访问性动态闭环，并由真实非空页面级图像、动作语义、版本绑定、fail-closed verifier、mutation 和精确清理支持。

## 允许写入与严格只读

仅允许写入：

- `lifeos/prototypes/LIFEOS-P3-117/`
- `lifeos/deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md`
- `lifeos/local_prechecks/` 中本任务报告
- `/private/tmp/lifeos-p3-117-native-capture-v1`

P3-117 目录至少包含：`evidence_probe.js`、probe 静态审计、launch／capture／crop／verify／mutation／cleanup runner、逐行动作闭环、raw/proof/clean image chain、geometry、structured results、mutation results、cleanup 和非自指 Manifest。

严格只读：P3-116 整个目录与交付物／Review／PM Evidence；P3-113～P3-115；历史 Frozen 资产；工程、账本、风险、冻结与 retained Pilot。

## 执行合同

1. 从空唯一临时根创建 `candidate/` 和 `chrome-profile/`；复制 P3-116 八项候选／合同，复制后 source hash 必须与 ABF 完全一致。
2. 仅在临时副本附加 P3-117 hash 固定 probe；probe 只能报告 capture ID、file scheme、inner viewport、DPR、route/state，不得网络、存储、读取浏览器 chrome 或修改产品状态／布局。
3. 用 ABF 冻结的 `open -na` 参数启动实际 Google Chrome 单一 app-mode 窗口；不得在地址栏输入路径，不得接触现有 Chrome 状态。
4. Computer Use 只操作该实际 GUI 窗口。窗口不是唯一前台 P3-117 app-mode、URL／probe 不是精确 task-local `file:`、出现其他窗口／桌面／浏览器 chrome／远程内容时立即停止，不写 Evidence。
5. `screencapture` 只捕获唯一专用 app-mode 窗口；不得全屏捕获。raw window image 保留，页面 crop 必须有 geometry JSON 和 parent hash；probe 可见 proof 与隐藏后的 clean image 分别保存。
6. 完整执行 ABF-M-004～M-012 的每一动作和子状态；每项唯一 capture ID，不得以静态扫描、缩略图、空白图、重复图或相邻动作替代。
7. verifier 从 raw Evidence 重算：候选／历史 hash、图片解码／尺寸／非空、raw→crop 边界、viewport、action/state 语义锚点、不同状态图、probe 隐藏、ambient/browser chrome 禁止项、Manifest 与 cleanup。
8. 在 clean disposable control 先 PASS 后执行 ABF 规定的 12 类 mutation；每类必须以唯一精确原因非零退出。
9. 结束时关闭专用窗口，只精确删除唯一临时根，验证 profile／candidate copy／working capture 与根路径不存在。不得关闭或修改用户既有 Chrome。
10. 任一必填行缺失，专项自检必须为 Not Pass／Not Implemented，不得提交概括性 Pass。

## 非范围与停止条件

- 不修改 P3-116 candidate、fixture、合同、任务、ABF、交付物、Evidence、Review 或 PM Evidence。
- 不重新设计 IA、页面、视觉、交互或文案；若发现候选本身不满足原合同，记录 Not Pass 并停止，不能在 P3-117 修复产品。
- 不读取／控制／截图现有 Chrome 或其他 app／窗口／桌面，不导出 AX/browser metadata。
- 不使用网络、搜索、HTTP(S)、localhost、CDP、DevTools、headless、WebDriver、浏览器服务、全屏截图、远程资源或新依赖。
- 不运行工程／Tauri／IPC／DB／模型，不处理真实数据／文件／Pilot。
- 不关闭／重开风险，不冻结产品／原型／架构，不恢复基线，不进入 Stage 4。

## 交付、自检与 PM 所需输出

- 完整交付物：`lifeos/deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md`
- Evidence：`lifeos/prototypes/LIFEOS-P3-117/MANIFEST.md`
- 交付物必须包括：授权／会话／模型、ABF hash、13 项固定输入、P3-116 只读保全、专用 Chrome 隔离、probe 审计、逐行矩阵、raw→proof→clean 图像链、三个 viewport、语义／隐私 verifier、12 类 mutation、精确清理、五类计数和 PM 待决策项。
- 必须提供完整可运行 runner、结构化 JSON、动作级日志、图像与 geometry、逐文件 hash、复跑说明和非自指 Manifest。
- 本地预检默认执行：`python3 lifeos/tools/local_precheck.py <交付物路径>`；不可用则记录 Skipped，不得阻塞。
- 专项只能报告 Candidate Ready / Not Pass / Blocked；不得修改账本、宣告 PM Pass／Accepted／Frozen、创建后续任务或启动独立评审。

## 结论与后续边界

- P3-117 提交后由 PM 按 `ABF-P3-117-v1` 独立复算和抽查。
- PM Pass 后仍需用户采纳；采纳后才可由 PM 在单独授权下创建全新隔离关键原型独立评审。
- P3-117 Pass 仅证明当前 P3-116 source hash 的受控本地原型动态／视觉闭环，不追溯把 P3-116 改写为 Accepted，不冻结资产，不证明 runtime／真实使用价值或 Stage 4 准入。

## 会话路由

- 是否建议新建会话：Yes。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 本地视觉 Evidence 执行。
- 会话判断理由：P3-116 已关闭且旧会话经历 ambient metadata 与两次取证环境失败；新任务改变 Frozen capture 入口，必须隔离旧浏览器／Evidence 状态和授权。
- 是否需要独立性隔离：Yes；但本任务是执行／取证，不是最终独立评审。
- 必须重新读取：本任务“最小启动包与定向补读”全部文件。
- 可复用既有读取结果：None；新会话不得继承 P3-116 授权或已读状态。
- 任务完成后建议保留会话：Yes，仅用于 P3-117 同一 Frozen ABF 内包内修正；不得承担后续独立评审。
- 聊天回复：严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径、计数、Evidence 和 PM 待确认项。

