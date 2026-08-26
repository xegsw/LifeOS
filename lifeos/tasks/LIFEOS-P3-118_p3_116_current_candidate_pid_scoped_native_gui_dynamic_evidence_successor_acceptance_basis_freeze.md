# LIFEOS-P3-118 Acceptance Basis Freeze｜P3-116 当前候选 PID 限定原生 GUI 动态 Evidence 最终后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-118`
- ABF ID／版本：`ABF-P3-118-v1`
- 生效决策：`D-0475`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

只读锁定 P3-116 当前八项产品候选／合同，在不接触现有浏览器会话、真实数据、网络或 runtime 的前提下，以全新临时 Chrome profile、直接启动的专用 Chrome 主进程、PID 限定的原生窗口身份／前台证明、Computer Use 对该已证明窗口的实际 GUI 操作、macOS 原生窗口截图和 raw→proof→clean 可审计裁剪链，完成当前候选全量动态／视觉 Evidence、语义／版本／隐私 verifier、mutation 和精确清理。

明确不冻结：产品需求、IA、视觉资产、关键原型、架构、Schema/API、runtime、工程基线、风险或阶段。本 ABF 只冻结 P3-118 如何证明 P3-116 当前候选。

明确非范围：修改 P3-116/P3-117 候选、合同、fixture、Review 或 Evidence；重新设计页面；真实个人／工作／健康数据或文件；现有 Chrome profile／窗口／标签／账户／历史／扩展；retained Pilot；DB、Tauri/IPC、模型、网络／云／第三方、HTTP(S)、localhost、CDP、DevTools、headless、WebDriver、浏览器自动化服务、AX/browser export、全屏／桌面截图；风险关闭／重开、冻结、工程实现、独立评审与 Stage 4。

## 授权和能力边界

- 允许写入：`lifeos/prototypes/LIFEOS-P3-118/`、指定 P3-118 交付物、task-local 本地预检报告，以及唯一 `/private/tmp/lifeos-p3-118-native-capture-v1`。
- 允许数据：P3-116 固定 synthetic fixture 的只读副本；P3-118 自有 capture ID、viewport、route/state、PID/window ID、geometry 和结果元数据。
- 允许浏览器入口：直接启动 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`，参数仅为唯一 `--user-data-dir=/private/tmp/lifeos-p3-118-native-capture-v1/chrome-profile`、`--app=file:///private/tmp/lifeos-p3-118-native-capture-v1/candidate/index.html`、`--disable-background-networking`、`--disable-sync`、`--disable-extensions`、`--no-first-run`、`--no-default-browser-check`。禁止 `open -na` 与按 bundle/app 名称选择 Chrome，避免误绑定既有实例。
- 允许窗口身份工具：task-local 原生 helper 仅接收启动返回的专用 Chrome 主 PID；调用 macOS Quartz/System Events 时必须先按该 PID 过滤，过滤后才允许序列化；只输出 target PID、target window ID、bounds、layer、onscreen、frontmost、process executable hash 和布尔判定，不得输出其他 PID、窗口、标题或应用信息。
- 允许 GUI 操作：先由 PID 限定 helper 将唯一目标窗口置前并取得 attestation；随后 Computer Use 仅对当前已证明的前台窗口做正常点击／键盘操作。禁止调用 Google Chrome 应用选择器、窗口切换器、Dock、Mission Control 或枚举其他窗口。每个动作前后都必须重新证明 frontmost owner PID 和 window ID 未变；失配时动作前停止，动作后失配则该动作失败且不截屏。
- 允许截图：`screencapture -l <attested-window-id>` 仅捕获已证明的唯一 P3-118 窗口；不得全屏捕获。`sips` 或本机既有离线图像库仅解码、核尺寸和裁剪。
- 允许 Evidence probe：仅在临时候选副本附加 hash 固定、离线、无存储、非布局占位的只读 probe，报告 capture ID、`file:` scheme、inner viewport、DPR、route/state、target PID/window ID attestation token；probe 不得读取浏览器 chrome、修改产品状态／fixture 或访问网络／存储。
- 严格只读：P3-113 至 P3-117 的任务、ABF、原型／候选、合同、fixture、交付物、Review、Evidence、PM Evidence；历史 Frozen 资产、工程、账本、风险、冻结与 retained Pilot。
- 投递前额外用户确认：None。用户已授权创建本新任务与新 ABF；任何非范围能力仍须停止回 PM。

## 正确冻结的固定输入

| 固定输入 | SHA-256 | 用途 |
|---|---|---|
| `lifeos/prototypes/LIFEOS-P3-116/index.html` | `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b` | 当前候选入口 |
| `lifeos/prototypes/LIFEOS-P3-116/app.js` | `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f` | 当前交互 |
| `lifeos/prototypes/LIFEOS-P3-116/styles.css` | `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3` | 当前视觉 |
| `lifeos/prototypes/LIFEOS-P3-116/fixtures.js` | `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93` | 固定 synthetic fixture |
| `lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md` | `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393` | 交互合同 |
| `lifeos/prototypes/LIFEOS-P3-116/state_machine.json` | `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc` | 状态机 |
| `lifeos/prototypes/LIFEOS-P3-116/visual_contract.json` | `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49` | 视觉合同 |
| `lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md` | `bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467` | IA 调和 |
| `lifeos/reviews/LIFEOS-P3-116_pm_review.md` | `09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa` | D-0473 后权威 P3-116 历史；纠正 P3-117 的旧 hash |
| `lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md` | `19ea3fecef60bfa491a3b4e85c009dfeab3aa228bdab2881f0d08af3a1d34ec1` | 前任务边界 |
| `lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor_acceptance_basis_freeze.md` | `57d6016e338103f4f53b5e979d3ec2d5eca708e7622ade33c3ccfd8be1c2b0e0` | 失败 ABF 历史，只读 |
| `lifeos/deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md` | `8530b08e241355fd169b543863f25d5a492c3dd8f00968ab7cea95c94d79ad39` | Blocked 执行历史 |
| `lifeos/prototypes/LIFEOS-P3-117/MANIFEST.md` | `8fd17280974a1a3889d4c4ac9d469e7ca02522c584e9fa9cf6df7b41d1d04c0a` | P3-117 静态预检／清理历史 |
| `lifeos/reviews/LIFEOS-P3-117_pm_review.md` | `d80747f2b36e03917affdda10a95fd16a8b87e5d4816b7300a060e34339cdaca` | D-0475 用户采纳与关闭后的权威 P3-117 Review |
| `lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/MANIFEST.md` | `d02523ba33e1eee085bb2dec921ebf8ab4e25918b7de3330659b09055c166cf7` | PM Evidence 入口 |
| `lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/blocked_assessment.md` | `948a43294faeeb9b70679d2a740ad36b2582a105bf0cb4d0a40094621c3f4351` | 固定输入／窗口 Unknown 处置 |
| `lifeos/ACCEPTANCE_GOVERNANCE.md` | `86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c` | D-0401 治理 |

## 引用的 L1 长期原则

- L1-1 数据主权：只允许 P3-118 task-local synthetic 数据与 PID 限定窗口；其他浏览器／窗口不可见、不可记录。
- L1-4 失败关闭：固定输入、PID、唯一窗口、frontmost、`file:`、图像链或清理任一失败即停止，不产出 PASS。
- L1-6 审计可信：PID/window/capture/action/source/geometry/cleanup 的顺序与身份必须一致。
- L1-7 Evidence 诚实：每个动作必须真实 Computer Use GUI 操作并生成独立原生图像链。
- L1-8 历史保全：P3-116/P3-117 全部资产只读，不覆盖失败历史。
- L1-9 授权不漂移：不得把专用 PID 授权扩展到任何其他 Chrome 进程、窗口或系统界面。
- L1-10 可复核性：固定 source、PID attestation、runner、Manifest 与 mutation 可确定性复算。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 17 项固定输入准确且只读 | P0 | before/after 全匹配；P3-116 PM Review 必须为 `09d810…` | Not Pass |
| ABF-I-02 | 专用进程身份唯一 | P0 | 启动主 PID、可执行路径/hash、完整允许参数一致；不复用现有 profile | Not Pass |
| ABF-I-03 | 原生窗口身份仅由 PID 过滤得出 | P0 | 过滤后恰一层 0、onscreen 窗口；序列化内容不含其他 PID/window/app | Not Pass |
| ABF-I-04 | GUI 动作只发生在已 attested 前台窗口 | P0 | 每个动作前后 target PID/window/frontmost token 一致；Computer Use 不用 app selector | Not Pass |
| ABF-I-05 | 精确 task-local `file:` 且无网络 | P0 | probe 与进程参数均为冻结 URL；无 HTTP/localhost/远程内容 | Not Pass |
| ABF-I-06 | 原生 raw→proof→clean 链可信 | P0 | window ID、geometry、parent hash、crop bounds、probe visible/hidden 完整 | Not Pass |
| ABF-I-07 | 图像真实、非空、非单色且动作语义匹配 | P0 | 解码、尺寸、像素变化、锚点和状态差异均通过 | Not Pass |
| ABF-I-08 | 三个 inner viewport 精确 | P1 | `1280×1024`、`1160×768`、`700×760` probe 实测匹配且可操作 | Not Pass |
| ABF-I-09 | 页面／状态／用户权威合同完整 | P0 | M-004～M-010 全部子动作实际通过 | Not Pass |
| ABF-I-10 | 键盘与 reduced-motion 实际通过 | P1 | Tab/Shift+Tab/Enter/Escape/skip link/motion 可见且逐动作留证 | Not Pass |
| ABF-I-11 | verifier 与 mutation fail closed | P0 | clean control PASS；14 类 mutation 各以唯一原因非零失败 | Not Pass |
| ABF-I-12 | 历史、Manifest 与精确清理可信 | P0 | P3-116/P3-117 hash 不变；专用 PID 关闭；临时根不存在 | Not Pass |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 空临时根 | 复算 17 项输入、模型、工具、允许目录 | 全匹配；不匹配时未创建临时根 | 所有历史输入 | P118-M001 | fixed-input JSON + hashes |
| ABF-M-002 | 直接 Chrome executable | 新 profile | 启动并保存主 PID；PID 过滤唯一窗口；置前；Computer Use 观察已证明窗口 | PID、参数、window ID、frontmost、精确 `file:` 全成立；无 ambient | 现有 Chrome 状态 | P118-M002 | process/window attestation + probe + isolation |
| ABF-M-003 | 专用窗口 | 初始 Today | 取得 raw window、probe proof、隐藏 probe 后 clean crop | 原生页面级图像和 lineage／geometry/hash 完整 | candidate state | P118-M003 | raw + geometry + proof + clean |
| ABF-M-004 | Global Shell | 初始 | 导航、hover Icon Rail、弱 Settings、Global AI | 一级入口和禁止元素符合合同 | fixture | P118-M004 | per-action attestation + image pairs |
| ABF-M-005 | Today | 固定 fixture | 默认、合法空、证据不足、Why | Focus 0–1；空／不足诚实 | source/fixture | P118-M005 | per-state image pairs |
| ABF-M-006 | Me | 固定 identity | 四层、Domain 状态、依据、纠正／撤回入口 | 非 Profile；Work/Health 深度；可追溯纠正 | memory identity | P118-M006 | actions + image pairs |
| ABF-M-007 | Contexts／Detail | 固定 Context | 三组关系、创建建议、Detail／Evidence | 非 Kanban；创建待确认；Detail 完整 | domain/source | P118-M007 | actions + image pairs |
| ABF-M-008 | Memory／Detail | 固定七类身份 | 七类筛选及 Understanding→Source 回溯 | 身份／来源／断链诚实 | user original | P118-M008 | trace + image pairs |
| ABF-M-009 | Global AI／Workspace | 固定三层 Context | 核对／临时移除／渐进展开 | 不改持久事实；Workspace 非 ChatGPT Clone | context selection | P118-M009 | context diff + image pairs |
| ABF-M-010 | 用户权威／第三 Domain | 固定 candidates | 确认、编辑、拒绝、忽略、纠正并尝试启用 | 无自动确认；四 Gate 未满足时关闭 | original output | P118-M010 | transitions + image pairs |
| ABF-M-011 | 三 viewport | 每次重校准窗口 | 在三个 inner size 操作核心路线 | probe 精确；无关键裁切，操作可达 | product state | P118-M011 | geometry + full crops |
| ABF-M-012 | 键盘／motion | 对应页面 | Tab/Shift+Tab/Enter/Escape/skip link/reduced-motion/关闭重开 | 实际顺序、焦点、关闭、低动态和重启状态成立 | source/fixture | P118-M012 | per-action image pairs |
| ABF-M-013 | verifier baseline | canonical Evidence | 从 raw/proof/clean/attestation/logs 重算全部行 | 全部 PASS；无自述替代 | canonical evidence | P118-M013 | results + verifier output |
| ABF-M-014 | disposable 副本 | clean control PASS | 变异空白、单色、重复、错 viewport、错 crop、browser chrome、错语义、source drift、ambient marker、probe leak、缺 raw link、缺 cleanup、错 PID、多个 target window | 14 类各以唯一预期原因非零退出 | canonical evidence | P118-M014 | mutation results |
| ABF-M-015 | 结束 | 全部执行完成或失败停止 | 关闭精确专用 PID；复算历史、Evidence、计数与清理 | history unchanged；五类计数披露；profile/candidate/temp root 不存在 | all read-only assets | P118-M015 | final results + cleanup |

## Evidence 合同

- 可运行 runner／源码：固定输入、probe audit、PID launch、PID-filtered window attestation、GUI action record、capture/crop、semantic/privacy verifier、14 类 mutation、Manifest、cleanup。
- 逐行结构化结果：15 行及全部子动作含唯一 test/execution/capture/attestation ID、实际操作、预期／实际、结论、严重级别和 Evidence path。
- before／after：17 项固定输入、candidate hash、target PID/window、page state、viewport、profile/temp root。
- 图像链：每个必填动作至少含 raw isolated-window、probe-visible proof、probe-hidden clean crop、geometry、PID/window attestation 与 SHA-256；禁止跨语义状态复用。
- 隐私日志：序列化前按 target PID 过滤；只允许 P3-118 IDs、固定 synthetic state、target PID/window、bounds、file scheme 与布尔结果。不得写入其他 PID/window/app/title/path。
- source/history hash：17 项固定输入 before/after、P3-116 八项 candidate/contract 与 P3-117 历史一致。
- Manifest：非自指，覆盖 runner、probe、attestation、raw/proof/clean、geometry、actions、results、mutations、cleanup 与交付物引用。
- 复跑入口：从空唯一临时根开始；GUI 动作必须由 Computer Use 在 PID attestation 后实际执行，不得脚本直接修改 DOM／state 冒充 GUI。
- 临时清理：仅关闭已核验命令行仍含唯一 profile 的专用主 PID及其子进程，并精确删除 `/private/tmp/lifeos-p3-118-native-capture-v1`；禁止按名称／pattern 终止 Chrome。

## 计数与 Pass 公式

- P0：固定输入／历史漂移、其他浏览器／窗口／真实或 ambient 数据访问、错误 PID/window、网络、伪造／错误来源截图、图像／动作／source／verifier fail-open。
- P1：viewport、页面 crop、键盘、motion 或响应式完成定义失败。
- P2：不影响完成定义的 Evidence 可读性；Pass 仍要求 0。
- Unknown：任一模型、PID、window、frontmost、截图来源、viewport、geometry、动作语义、source、历史或清理无法独立复核。
- Not Implemented：任一必填行／子动作、图像链、attestation、runner、mutation 或 Evidence 缺失。
- Pass 公式：ABF-I-01～I-12、ABF-M-001～M-015 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；17 项输入、专用 PID/window、Computer Use GUI、原生图像链、三个 viewport、语义／隐私 verifier、14 类 mutation、历史保全和精确清理同时成立。
- 允许 N/A：None。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅限 P3-118 自有 helper、probe、attestation、截图／裁剪、runner、verifier、mutation、Manifest 或 Evidence；不得修改 P3-116/P3-117 或本 ABF。
- 必须新建任务：任何候选／产品修改；改变目录、数据、入口、PID/window 策略、GUI 工具、截图来源、网络边界、依赖、能力、授权、架构、风险、冻结或阶段；实质修改本 ABF；或两轮正式 Rework 未通过。
- Blocked：直接专用 Chrome 进程无法返回可核验主 PID、PID 过滤无法得到恰一原生窗口、Computer Use 无法在不使用 app selector／其他窗口的情况下操作已 attested 前台窗口、或必要原生工具不可用且不能在本 ABF 内安全恢复。不得使用其他浏览器、进程、窗口或截图路径替代。

## 候选基线与只读保全

- 候选输入：上表 17 项；P3-116/P3-117 整体只读。
- 允许变化：仅 P3-118 任务卡／ABF、`lifeos/prototypes/LIFEOS-P3-118/`、P3-118 交付物、task-local precheck 和唯一临时根。
- P3-118 Pass 不等于 P3-116/P3-117 Accepted、关键原型 Frozen、风险关闭、runtime Ready 或 Stage 4 准入；仍需 PM 验收、用户采纳和后续全新隔离独立评审。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：专项在任何临时文件／浏览器动作前须独立复算全部 17 项，特别确认 P3-116 PM Review 为 `09d810…`，并静态核对 helper 的“先 PID 过滤、后序列化”与 Computer Use 禁止 app selector 合同。
- 最终冻结版本：`ABF-P3-118-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
