# LIFEOS-P3-119 Acceptance Basis Freeze｜PID 限定原生 GUI 事件注入与截图可行性 Spike

## 冻结信息

- 任务 ID：`LIFEOS-P3-119`
- ABF ID／版本：`ABF-P3-119-v1`
- 生效决策：`D-0476`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

仅在全新 task-local 固定 synthetic HTML fixture 上，证明一种当前环境真实可用、无需 Computer Use app selector 的 GUI 取证入口：直接启动专用 Chrome 主 PID，按 PID 过滤唯一原生窗口，通过 `CGEventPostToPid` 向该精确 PID 发送鼠标／键盘事件，以 `screencapture -l <window-id>` 取得原生窗口截图，并完成首次、重复、关闭重开、负向 fail-closed 与精确清理。

本任务不是 P3-116 候选验收，不读取或运行 P3-116 页面，不执行 46 动作，不证明任何 LifeOS 产品页面、视觉、交互、可访问性或用户价值。

明确不冻结：产品需求、IA、原型、架构、Schema/API、runtime、工程基线、风险或阶段。

## 授权和能力边界

- 允许写入：`lifeos/spikes/LIFEOS-P3-119/`、指定 P3-119 交付物、task-local 本地预检报告、唯一 `/private/tmp/lifeos-p3-119-pid-gui-spike-v1`。
- 允许数据：任务内固定非敏感 fixture 标签、颜色、计数器、PID/window ID、geometry、event/result ID 和 hash。
- 允许入口：直接启动 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`，仅使用唯一临时 profile、`--app=file:` synthetic fixture 和五个禁用后台网络／同步／扩展／首次启动参数。
- 允许工具：P3-119 自有 Swift helper；`CGWindowListCopyWindowInfo` 必须先按专用 PID 过滤后序列化；`CGEventPostToPid` 只能向已验证的专用 Chrome PID发送冻结鼠标／键盘事件；`screencapture -l` 只能捕获该 PID 唯一窗口；离线图像库只做解码、尺寸、像素区域和 lineage 验证。
- 禁止工具／入口：Computer Use、app/bundle selector、AppleScript/System Events、Dock、Mission Control、窗口标题／OCR／AX、CDP、DevTools、WebDriver、headless、HTTP/localhost、全屏／桌面截图、其他浏览器、网络或外部依赖。
- 严格只读：P3-116 至 P3-118 全部任务、ABF、候选、交付物、Review、Evidence 与 PM Evidence；其他历史资产、工程、账本、风险、冻结和 Pilot。
- 投递前额外用户确认：None；用户已采纳 P3-118 Blocked 并授权按本建议创建极窄可行性 Spike。

## 固定历史输入

| 固定输入 | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md` | `3172457dc2c60080100d367acb979f92fbb060f4c4bd6383f60e9d7cfe76ec1b` |
| `lifeos/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor_acceptance_basis_freeze.md` | `d6f12523683beea42ecd9d9db586b41c489991286e0ee41e2eb4afeab5e5c18c` |
| `lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md` | `a0897741169dd127e12cc8bc40d8e11aada01e205341c0a3320be9c415fce085` |
| `lifeos/prototypes/LIFEOS-P3-118/MANIFEST.md` | `0270bea5d1114c01951e7b8b760e39f6f534c48797aea2eccc6cea28b6603e98` |
| `lifeos/prototypes/LIFEOS-P3-118/tools/pid_window_attest.swift` | `bacb9e7275fef2cbbe6201f4c64cc60af26678fb0274242c0b9eac65c2819931` |
| `lifeos/reviews/LIFEOS-P3-118_pm_review.md` | `bea6a010a3c26356c84f18ff2fd2f07d48e0dcc39193b65eaf9aad0933248f41` |
| `lifeos/reviews/LIFEOS-P3-118/pm_evidence/initial/MANIFEST.md` | `1327b037f6459bbe3ed76c935d13dce0f8d09b09e1e13c76760886ed5bcbf2d9` |
| `lifeos/reviews/LIFEOS-P3-118/pm_evidence/initial/blocked_assessment.md` | `b5cd531667c3f23cc8491ad77655f04725aa4c54a98a56406270349758c98cfe` |
| `lifeos/ACCEPTANCE_GOVERNANCE.md` | `86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c` |
| `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | `97385e62510154852fd10da11c697bf5066dcc300e3b0c31633bd52ad940b984` |

## 引用的 L1 长期原则

- L1-1 数据主权：只允许 synthetic fixture 与专用 PID/window；任何其他进程／窗口信息在序列化前丢弃。
- L1-4 失败关闭：PID、window、event target、state transition、capture 或 cleanup 任一失败即停止。
- L1-6 审计可信：launch PID、window ID、event ID、before/after image 和 cleanup 顺序必须一致。
- L1-7 Evidence 诚实：状态变化必须来自实际 `CGEventPostToPid` 事件和原生窗口截图，不得脚本改 DOM/state。
- L1-8 历史保全：P3-116～P3-118 全部只读。
- L1-9 授权不漂移：事件只能发送到精确专用 PID；禁止名称、bundle、pattern 或全局广播。
- L1-10 可复核性：固定 fixture、helper、runner、图片和 mutation 可重复验证。

## 冻结 synthetic fixture

- 单页、离线、无 storage／network／外部资源。
- 初始状态 `S0`：中央大色块 `#D94F4F`，固定标记 `P119-S0`。
- 鼠标按钮区域使用冻结的窗口内相对矩形；首次实际 click 后进入 `S1`：色块 `#3FAE6A`、标记 `P119-S1`。
- 对同一区域第二次实际 click 后进入 `S2`：色块 `#3478F6`、标记 `P119-S2`。
- 实际 Tab 后 Enter 进入 `S3`：色块 `#8E5BD9`、标记 `P119-S3`。
- 关闭专用 PID、以同一 fixture 和全新第二 profile 重开后必须回到 `S0`。
- runner/helper 禁止直接执行 JavaScript、修改 DOM、调用页面 API、写 storage 或用截图后处理伪造颜色。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 固定历史与 Chrome executable 不漂移 | P0 | 10/10 hash 匹配 | Not Pass |
| ABF-I-02 | 专用主 PID 与唯一窗口可证明 | P0 | executable、profile、app URL、PID、恰一 layer-0 onscreen window 成立 | Not Pass |
| ABF-I-03 | 事件精确发送至专用 PID | P0 | helper 仅使用 `CGEventPostToPid(target_pid, event)`；无 global post／selector | Not Pass |
| ABF-I-04 | 实际 GUI 状态转换可由原生截图证明 | P0 | S0→S1→S2→S3 各有独立 raw image、像素区域与 hash | Not Pass |
| ABF-I-05 | 关闭重开语义成立 | P1 | 精确关闭第一 PID，以第二全新 profile 重开回 S0 | Not Pass |
| ABF-I-06 | fail-closed mutation 成立 | P0 | 10 类负向各以唯一原因非零退出且不发错目标事件 | Not Pass |
| ABF-I-07 | 精确清理 | P0 | 两个专用 PID及子进程关闭；唯一临时根不存在；不按名称／pattern kill | Not Pass |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 空临时根 | 复算 10 项输入、模型、工具与权限 | 全匹配；否则不创建根 | P3-116～P3-118 | P119-M001 | fixed-input JSON |
| ABF-M-002 | fixture/helper | 未启动 Chrome | 创建固定 fixture；静态审计并编译 helper | fixture contract 与 PID-only event API 成立 | history | P119-M002 | source + static audit |
| ABF-M-003 | 直接 Chrome | 全新 profile-1 | 启动、取得 PID、按 PID 过滤唯一窗口、原生捕获 S0 | 精确 PID/window/file URL；S0 图片成立 | other apps/windows | P119-M003 | launch attestation + raw S0 |
| ABF-M-004 | `CGEventPostToPid` | S0 | 在冻结矩形实际 click 一次 | S1 绿色；before/after 不同 | target PID/window | P119-M004 | event + raw S1 |
| ABF-M-005 | `CGEventPostToPid` | S1 | 同位置实际 click 第二次 | S2 蓝色；重复动作真实执行 | target PID/window | P119-M005 | event + raw S2 |
| ABF-M-006 | `CGEventPostToPid` | S2 | 实际 Tab，再实际 Enter | S3 紫色；两个 key event 可追溯 | target PID/window | P119-M006 | events + raw S3 |
| ABF-M-007 | restart | S3 | 精确关闭 PID-1；用全新 profile-2 重开 | 新 PID/window；S0 恢复 | fixture/history | P119-M007 | close/reopen + raw S0b |
| ABF-M-008 | disposable copies | clean baseline PASS | wrong PID、executable mismatch、profile mismatch、zero window、multiple windows、out-of-bounds click、wrong window capture、unchanged state、global event API、missing cleanup | 10 类唯一非零失败；不得向错误目标发事件 | canonical evidence | P119-M008 | mutation results |
| ABF-M-009 | 结束 | 全部完成或失败 | 复算、五类计数、关闭专用 PID、精确删根 | history unchanged；root absent | other processes/files | P119-M009 | final results + cleanup |

## Evidence 合同

- runner／源码：fixture builder、PID/window attest、PID-target event helper、native capture、pixel verifier、restart、mutation、Manifest、cleanup。
- 逐行结果：9 行含唯一 PID/window/event/capture ID、实际操作、结果、Evidence path 和 SHA-256。
- 图片：S0/S1/S2/S3/S0b 均为 `screencapture -l` 的独立原生窗口图片；记录 window ID、bounds、image size、target color region 和 hash。
- 日志：只允许专用 PID/window/event/result；不得包含其他 PID/window/app/title/path。
- Manifest：非自指，覆盖源码、fixture、runner、attestation、events、images、results、mutations、cleanup 和交付物引用。
- 复跑：从空唯一临时根开始；先 clean baseline，再 mutations；最终精确清理。

## 计数与 Pass 公式

- P0：错误进程／窗口事件、global event、其他窗口截图、伪状态、网络／外部访问、verifier fail-open、历史漂移或错误清理。
- P1：重复／重启或原生图像完成定义失败。
- P2：不影响完成定义的 Evidence 可读性；Pass 仍要求 0。
- Unknown：PID、window、event target、state、capture source、hash 或 cleanup 无法独立复核。
- Not Implemented：任一必填动作、原生截图、runner、mutation 或 Evidence 缺失。
- Pass 公式：I-01～I-07、M-001～M-009 全部实际 PASS；S0→S1→S2→S3→restart S0b 成立；10 类 mutation 全部 fail closed；P0/P1/P2/Unknown/Not Implemented 全零。
- 允许 N/A：None。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-119 fixture、helper、runner、pixel/capture verifier、mutation、Manifest 或 Evidence；ABF 不变。
- 必须新建任务：改变事件 API、浏览器、目录、数据、入口、截图来源、权限、网络边界或本 ABF；触达 P3-116 候选；两轮 Rework 未通过。
- Blocked：当前 macOS 权限或 API 使 `CGEventPostToPid`、PID window attestation 或 window-ID capture 不可用，且不能在本 ABF 内安全恢复。Blocked 只关闭可行性结论，不得继续创建最终 Evidence 任务。

## 候选基线与只读保全

- 本任务没有 LifeOS 产品候选；唯一被测对象是 P3-119 synthetic fixture 与 native GUI 工具链。
- P3-116～P3-118 全部只读。
- 允许变化：P3-119 任务卡／ABF、`lifeos/spikes/LIFEOS-P3-119/`、P3-119 交付物、task-local precheck、唯一临时根。
- Spike Pass 只证明工具路径可行；不等于 P3-116 候选 Pass、关键原型 Frozen、风险关闭、runtime Ready 或 Stage 4 准入。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：任何 GUI 动作前核对 `CGEventPostToPid` 可用性、事件仅指向专用 PID、window-ID capture 和精确清理；禁止把 Computer Use 或 app selector带回本任务。
- 最终冻结版本：`ABF-P3-119-v1`。
- 专项启动后不得实质修改 ABF；如需修改，当前任务关闭并新建任务。
