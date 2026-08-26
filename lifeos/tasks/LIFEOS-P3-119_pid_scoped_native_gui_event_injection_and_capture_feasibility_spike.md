# LIFEOS-P3-119｜PID 限定原生 GUI 事件注入与截图可行性 Spike

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务仅在全新 task-local 固定 synthetic HTML fixture、专用临时 Chrome profile/PID 和 `/private/tmp` 唯一根内验证本地 GUI 事件与窗口截图能力；不读取或运行 P3-116 候选，不访问现有浏览器、真实数据、网络、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-119`
- 任务名称：PID 限定原生 GUI 事件注入与截图可行性 Spike
- 优先级：P0
- 任务类型：受控本地 GUI 工具可行性 Spike；不是产品实现、候选验收或独立评审。
- 是否为受控能力包：Yes。
- 唯一风险边界：证明 `CGEventPostToPid` + PID-filtered native window + `screencapture -l` 能否安全完成 synthetic fixture 的实际首次／重复／键盘／重启闭环。
- 包内允许：fixture、Swift helper、runner、native screenshots、pixel verifier、negative mutations、Manifest、cleanup 和交付报告。
- 包内整改授权：仅 P3-119 自有范围；不得扩大到 P3-116 候选、Computer Use、其他浏览器／窗口或产品验收。
- 必须拆分：最终 46 动作 Evidence、P3-116 候选运行、产品修改、风险／冻结／runtime／Stage 4、网络或其他工具入口。
- 建议篇幅：1200–2200 字；完整 Evidence 写入 Spike 目录。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，全新本地 GUI 技术 Spike 会话。
- 推荐理由：需要实现并验证 task-local Swift PID event/capture helper、原生截图、像素断言和 fail-closed 边界。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：PID 定向 GUI 事件可能影响桌面输入，必须以最高边界意识验证且 fail closed。
- 允许降级模型：None。
- 禁止降级条件：全部范围。
- 必须升级条件：N/A；首选不可用则停止。
- 后备模型：None。
- 是否需要后续独立评审：No；Spike 由 PM 验收和用户采纳。未来最终 Evidence 任务仍需单独独立评审。
- 是否允许修改工程文件：No；只允许 Spike 自有文件。
- 是否允许修改项目账本：No。
- 主责角色：本地 GUI 技术 Spike + Evidence QA。
- 协审角色：隐私／安全、技术可行性、失败关闭和清理。
- 必须通过关卡：固定输入、专用 PID/window、PID-target mouse/keyboard、S0→S1→S2→S3、restart S0、10 类 mutation、历史保全与精确清理。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-119-v1`
- ABF SHA-256：`cbec1018c2e3317fc1fdd9f9de325349e12d12d85ceea707031a3510b74d9071`
- ABF 状态：Frozen。
- 正式 Rework：0/2。
- 生效决策：`D-0476`
- 执行授权：用户将本任务卡绝对路径投递至全新合格 Codex 会话即授权 Frozen 范围；仅在 PM 主会话查看不启动。
- 会话隔离：必须新建，不复用 P3-118 执行会话、PM 主会话或未来最终 Evidence／独立评审会话。
- 投递前额外确认：None；用户已采纳 P3-118 关闭与本 Spike 建议。
- 授权证据：首份报告记录路径、接收时间、会话类型、实际模型、ABF hash、允许写入、synthetic-only、no Computer Use、no existing Chrome 声明。

## 背景

P3-118 在 Chrome launch 前发现 Frozen GUI 路径不可执行：Computer Use 只有 app-scoped target，没有 PID/window target，而 ABF 正确禁止 app selector。PM 确认这是治理／工具可行性未先验证，不是 P3-116 UI 失败。用户采纳关闭建议，并同意先做本极窄 Spike；本任务不再承载产品验收。

## 启动前验收依据冻结

- `ABF-P3-119-v1` 已冻结；只冻结工具 Spike 的通过依据。
- 在创建临时根或 GUI 动作前，必须复算 10 项固定输入，确认 P3-118 关闭后 Review hash。
- 必须在静态质疑窗口确认当前 SDK 实际提供 `CGEventPostToPid`。若 API 不存在、需要改为 global event、Computer Use、AppleScript 或 app selector，动作前停止；不得自行改 ABF。

## 最小启动包与定向补读

完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-119-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/reviews/LIFEOS-P3-118_pm_review.md`
7. `lifeos/reviews/LIFEOS-P3-118/pm_evidence/initial/blocked_assessment.md`
8. `lifeos/prototypes/LIFEOS-P3-118/tools/pid_window_attest.swift`，仅作只读输入

定向补读：`PM_OPERATING_MODEL.md` 的 P0、会话隔离、Evidence／Blocked／Spike 章节；`ROLE_MATRIX.md` 的技术执行、Evidence QA、隐私／安全角色；`STAGE_GATES.md` 的关键原型独立评审与 Stage 3→4 区分；`TASK_REGISTRY.md` P3-118/P3-119；`DECISION_LOG.md` D-0474～D-0476；`RISK_LOG.md` R-0024、R-0025、R-0051。

禁止读取 P3-116 页面／源码内容、现有 Chrome profile／窗口／标签／账户／历史、Pilot、其他 app／桌面或无关 Evidence。

## 允许写入与环境

仅允许写入：

- `lifeos/spikes/LIFEOS-P3-119/`
- `lifeos/deliverables/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike.md`
- `lifeos/local_prechecks/` 中本任务报告
- `/private/tmp/lifeos-p3-119-pid-gui-spike-v1`

唯一临时根必须从不存在开始。Chrome profile-1/profile-2、fixture copy、working screenshots 和编译 cache 均在该根内；项目内 Spike Evidence 保留。

## 执行合同

1. 临时写入前复算 10 项输入、任务卡／ABF、Chrome executable 和临时根不存在；失败不得创建根。
2. 创建 ABF 冻结的纯 synthetic fixture；无 network/storage/external resource。静态审计 helper 只用 PID filter、`CGEventPostToPid`、window-ID capture，禁止 global post、Computer Use、selector、AppleScript、AX、CDP、HTTP、全屏截图。
3. 直接以 profile-1 启动专用 Chrome，保存主 PID；按 PID 过滤后必须恰一 layer-0 onscreen window，序列化前丢弃其他窗口数据。
4. 以 `screencapture -l` 取得 S0；helper 对精确 PID发送第一次 click，取得 S1；重复 click 得 S2；实际 Tab + Enter 得 S3。禁止脚本 DOM/state mutation。
5. 每次事件前验证 executable/profile/PID/window/坐标在 bounds 内；事件后重新 attestation。任一失配停止，不发送后续事件或截图。
6. 精确关闭 PID-1，以全新 profile-2 重开同一 fixture，证明回到 S0。
7. clean baseline PASS 后在 disposable copies 执行 ABF 10 类 mutation；每类唯一非零原因，wrong PID/out-of-bounds/global event 等不得实际触达错误目标。
8. 结束时仅关闭经命令行精确核验的两个专用 PID及其子进程；禁止 `pkill`、名称或 pattern kill。精确删除唯一临时根并验证不存在。
9. 任一行缺失，自检必须 Not Pass／Unknown／Not Implemented，不得把 helper compile 或静态 fixture 当作 GUI Pass。

## 非范围与停止条件

- 不读取／运行／截图 P3-116 候选，不执行 46 动作，不判断产品质量。
- 不使用 Computer Use、app selector、AppleScript、AX、CDP、DevTools、WebDriver、headless、HTTP/localhost、网络、OCR、全屏／桌面截图或其他浏览器。
- 不发送 global CGEvent；不操作、查询、记录或关闭其他 PID/window/app。
- 不运行 Tauri／DB／IPC／模型，不处理真实数据、文件或 Pilot。
- 不关闭风险、不冻结、不创建最终 Evidence 任务或独立评审、不进入 Stage 4。

## 交付与自检

- 交付物：`lifeos/deliverables/LIFEOS-P3-119_pid_scoped_native_gui_event_injection_and_capture_feasibility_spike.md`
- Evidence：`lifeos/spikes/LIFEOS-P3-119/MANIFEST.md`
- 必须交付 fixture、helper、runner、S0/S1/S2/S3/S0b 原生截图、PID/window/event/geometry JSON、pixel verification、10 类 mutation、cleanup、非自指 Manifest 和复跑命令。
- 必须报告 9 行矩阵、首次／重复／重启、P0/P1/P2/Unknown/Not Implemented 和未覆盖项。
- 本地模型预检因任务禁止网络可跳过，但必须说明。
- 专项只能报告 Spike Ready / Not Pass / Blocked；不得改账本、宣告产品 Pass、创建后续任务或启动独立评审。

## 后续边界

- Spike PM Pass 后仍需用户采纳；只有采纳后，PM 才可创建一次新的最终 P3-116 Evidence 任务并冻结基于已证明工具能力的 ABF。
- Spike Pass 不等于产品候选 Pass、Accepted、Frozen、风险关闭、runtime Ready 或 Stage 4 准入。

## 会话路由

- 建议：新建 `gpt-5.6-terra + xhigh` Codex 本地 GUI 技术 Spike 会话。
- 隔离原因：必须与 P3-118 的不可执行 Computer Use 假设和未来最终验收隔离。
- 可复用读取：None。
- 完成后保留会话：Yes，仅用于 P3-119 同 ABF 内包内修正；不得承担最终 Evidence 或独立评审。
- 回复格式：严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
