# LIFEOS-P3-117 Acceptance Basis Freeze｜P3-116 当前候选隔离原生截图动态 Evidence 后继收口

## 冻结信息

- 任务 ID：`LIFEOS-P3-117`
- ABF ID／版本：`ABF-P3-117-v1`
- 生效决策：`D-0473`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

只读锁定 P3-116 当前最终候选与产品／交互合同，在不接触现有浏览器会话、真实数据、网络或 runtime 的前提下，使用全新临时 Chrome profile、实际 GUI Chrome app-mode 窗口、macOS 原生窗口截图与可审计页面裁剪链，重新完成当前候选的全量动态／视觉 Evidence、语义／版本／隐私 verifier、mutation 和精确清理，从而独立关闭 P3-116 已确认的空白截图、ambient metadata 与最终 source hash 未绑定完整闭环三项缺口。

明确不冻结：产品需求、IA、视觉资产、关键原型、架构、Schema/API、runtime、工程基线、风险或阶段。ABF 只冻结 P3-117 凭什么证明 P3-116 当前候选。

明确非范围：修改 P3-116 候选／合同／fixture；重新设计页面；真实个人／工作／健康数据或文件；现有 Chrome profile／窗口／标签／账户／历史／扩展；retained Pilot；DB、Tauri/IPC、模型、网络／云／第三方、localhost、CDP、DevTools、headless、WebDriver、浏览器自动化服务、Vault／连接器、删除／导出／权限设置、同步／多设备、L3、外部用户、风险关闭／重开、冻结、工程实现、独立评审与 Stage 4。

## 授权和能力边界

- 允许写入：`lifeos/prototypes/LIFEOS-P3-117/`、指定 P3-117 交付物、task-local 本地预检报告，以及唯一 `/private/tmp/lifeos-p3-117-native-capture-v1`。
- 允许数据：P3-116 已有固定 synthetic fixture 的只读副本；P3-117 自有固定非敏感 capture ID、viewport label、状态 label 和测试元数据。
- 允许入口：以 macOS `open -na` 启动实际 Google Chrome app 的全新临时 profile 和单一 `--app=file:///private/tmp/lifeos-p3-117-native-capture-v1/candidate/index.html` 窗口；启动后只能由 Computer Use 正常操作实际 GUI。
- Chrome 启动边界：profile 必须位于唯一临时根；必须启用 `--disable-background-networking`、`--disable-sync`、`--disable-extensions`、`--no-first-run`、`--no-default-browser-check`；不得附加远程调试、自动化、HTTP 或其他外部入口参数。
- 允许取证工具：macOS `screencapture` 仅捕获已唯一确认的 P3-117 app-mode 窗口；`sips` 或本机既有离线图像库仅做解码、尺寸核对和可审计裁剪；`osascript` 仅可定位／调整当前前台 P3-117 专用窗口的 bounds／ID，不得枚举、读取或记录其他窗口／标签标题。
- 允许 Evidence probe：仅在临时候选副本中附加 P3-117 自有、hash 固定、离线、无存储的只读 probe，用于显示并记录 capture ID、`location.protocol`、`innerWidth`、`innerHeight`、DPR、route／state label；probe 不得改动产品状态、fixture、布局或用户内容。每个动作保留 probe 可见的状态证明图及 probe 隐藏后的干净页面图。
- 严格只读：P3-113 至 P3-116 的任务、ABF、原型／候选、合同、fixture、交付物、Review、Evidence、PM Evidence；全部历史 Frozen 资产、工程、账本、风险、冻结和 retained Pilot。
- 禁止能力与外部目标：现有浏览器会话、屏幕全幅截图、其他窗口／桌面捕获、AX/browser raw export、HTTP(S)、搜索、DNS／远程资源、localhost、CDP、DevTools、headless、WebDriver、网络服务、安装依赖、真实数据／文件／DB／runtime。
- 投递前额外用户确认：None；用户已授权关闭 P3-116并创建本后继。任何超出上述入口、截图链或数据边界的替代方案必须停止并回 PM，不能在本任务内修改 ABF。

## 固定候选与历史输入

| 输入 | SHA-256 | 用途 |
|---|---|---|
| `lifeos/prototypes/LIFEOS-P3-116/index.html` | `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b` | 只读候选 |
| `lifeos/prototypes/LIFEOS-P3-116/app.js` | `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f` | 只读候选 |
| `lifeos/prototypes/LIFEOS-P3-116/styles.css` | `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3` | 只读候选 |
| `lifeos/prototypes/LIFEOS-P3-116/fixtures.js` | `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93` | 固定 synthetic fixture |
| `lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md` | `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393` | 交互合同 |
| `lifeos/prototypes/LIFEOS-P3-116/state_machine.json` | `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc` | 状态机 |
| `lifeos/prototypes/LIFEOS-P3-116/visual_contract.json` | `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49` | 视觉合同 |
| `lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md` | `bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467` | IA／架构调和 |
| `lifeos/reviews/LIFEOS-P3-116_pm_review.md` | `f698ade8695fc966034031129d271f25fcb35f2dd714acd3ba85a04cb3acef0d` | P3-116 最终 PM 历史与三项缺口 |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/MANIFEST.md` | `58e778aeeb3f8c7306d8981409a1a0aae234c7137fae9eb3b660355c1cdc969b` | 首次停止尝试只读记录 |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/attempt-2/MANIFEST.md` | `e41fe9514af6df1b6e272f92cf4c100f4b9f1bc1c3f4137c69a8a2a591aa3799` | 第二次阻断只读记录 |
| `lifeos/reviews/LIFEOS-P3-116/pm_evidence/rework-1/attempt_2_blocked_assessment.md` | `4dde5d041f7d29875a5efb131c1568c425f2ff63d359eb90dd1f4a32a797fc2a` | 后继触发依据 |
| `lifeos/ACCEPTANCE_GOVERNANCE.md` | `86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c` | L1/L2 与后继治理 |

## 引用的 L1 长期原则

- L1-1 数据主权：专用临时 Chrome profile 与窗口，不接触或记录现有浏览器／桌面／真实数据。
- L1-6 审计可信：每个动作绑定 capture ID、窗口／裁剪几何、probe 状态、raw／clean image、hash 与实际结果。
- L1-7 Evidence 诚实：真实 GUI 动作、实际原生截图和动作级视觉证据；不得用缩略图、空白图、静态扫描或相邻动作替代。
- L1-8 历史保全：P3-116 全部资产只读；新任务独立目录。
- L1-9 授权不漂移：新授权只增加隔离 app-mode 启动与原生截图／裁剪链，不扩展网络、现有浏览器或真实能力。
- L1-10 可复核性：固定 source hash、fixture、probe、viewport、截图链、verifier、mutation 与唯一临时根可重复验证。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | P3-116 当前候选完全只读 | P0 | 8 项候选／合同 before-after hash 全部一致 | Not Pass |
| ABF-I-02 | 专用浏览器隔离 | P0 | 新临时 profile、单 app-mode 窗口、无现有标签／账户／扩展／历史／ambient metadata | Not Pass |
| ABF-I-03 | 真实本地入口且网络关闭 | P0 | 精确 `file:` URL；无搜索、HTTP(S)、localhost、远程资源或后台服务 | Not Pass |
| ABF-I-04 | 原生截图来源真实 | P0 | raw image 来自唯一确认的专用 app-mode 窗口；非 Computer Use 缩略图、非合成渲染 | Not Pass |
| ABF-I-05 | 页面裁剪链可审计 | P0 | raw window→geometry→page crop 一一绑定；crop 在 raw 内且无浏览器／桌面／其他窗口内容 | Not Pass |
| ABF-I-06 | viewport 可独立证明 | P1 | probe 证明 1280×1024、1160×768、700×760 的 inner viewport 与 DPR；clean crop 尺寸关系一致 | Not Pass |
| ABF-I-07 | 动作与状态语义匹配 | P0 | 每个冻结动作有唯一 capture ID、状态证明图、clean page图和至少一个确定性视觉语义锚点 | Not Pass |
| ABF-I-08 | 截图非空且非批量复用 | P0 | 可解码、合理尺寸、非空／非单色；语义不同状态不得共用同一图或同 hash | Not Pass |
| ABF-I-09 | probe 不污染产品结论 | P1 | probe hash 固定、只读／无网络／无存储；clean 图中隐藏且不改变布局／产品状态 | Not Pass |
| ABF-I-10 | 页面与交互合同完整 | P0 | P3-116 ABF-M-003～M-015 对应页面／状态／动作全部实际执行 | Not Pass |
| ABF-I-11 | verifier fail-closed | P0 | source、capture、geometry、viewport、语义、隐私、重复图和清理任一异常均精确非零退出 | Not Pass |
| ABF-I-12 | 历史、Manifest 与清理可信 | P0 | P3-116 历史 hash 不变；P3-117 非自指 Manifest 完整；窗口／profile／临时根精确关闭清理 | Not Pass |

## 冻结验收矩阵

每行及全部子动作必须独立执行并生成唯一 test／execution／capture ID；不得从总 PASS 批量映射。

| 行 ID | 入口／前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 核对任务投递、全新会话、模型、ABF、13 项固定输入 | 全部一致；质疑窗口关闭 | P3-116 全部资产 | P117-M001 | session + hashes |
| ABF-M-002 | 空唯一临时根 | 复制候选并附加只读 probe；启动专用 Chrome app-mode | source hash 可回溯；单窗口／单 profile；精确 `file:`；无 ambient | 现有 Chrome 状态 | P117-M002 | launch + probe + isolation |
| ABF-M-003 | 专用窗口 | 取得 raw window、probe 状态图和 clean page crop | 原生高分辨率、链路／几何／hash 完整；clean 图页面级 | candidate state | P117-M003 | raw + geometry + proof + clean |
| ABF-M-004 | Global Shell | 导航、hover Icon Rail、打开弱 Settings／Global AI | 一级入口与禁止元素符合合同 | fixture | P117-M004 | actions + image pairs |
| ABF-M-005 | Today | 分别执行默认、合法空、证据不足和 Why | Focus 0–1；空／不足诚实；动作语义清楚 | fixture | P117-M005 | per-state image pairs |
| ABF-M-006 | Me | 四层结构、Domain 状态、理解依据、纠正／撤回入口 | 非 Profile；Work/Health 深度、其他未启用；可追溯／纠正 | Memory identity | P117-M006 | actions + image pairs |
| ABF-M-007 | Contexts／Detail | 切换三组关系、创建建议、进入 Detail／Evidence | 非 Kanban／Domain 分栏；创建待确认；Detail 结构完整 | Domain/Source | P117-M007 | actions + image pairs |
| ABF-M-008 | Memory／Detail | 七类身份筛选并完成 Understanding→Source 回溯 | 非笔记/KPI；身份／来源／断链清楚 | user original | P117-M008 | trace + image pairs |
| ABF-M-009 | Global AI／Workspace | 核对三层 Context、临时移除、Work+Health 渐进展开 | 不改持久事实；Workspace 非 ChatGPT Clone | context selection | P117-M009 | context diff + image pairs |
| ABF-M-010 | 用户权威／第三 Domain | 确认、编辑、拒绝、忽略、纠正候选并尝试启用第三 Domain | 无自动确认；四 Gate 未满足时关闭 | original output / Work+Health | P117-M010 | transitions + image pairs |
| ABF-M-011 | 三 viewport | 分别校准并操作核心路线 | probe inner size 精确；关键内容／操作可达，无关键裁切 | product state | P117-M011 | geometry + full page crops |
| ABF-M-012 | 键盘／motion | Tab/Shift+Tab/Enter/Escape/skip link；reduced-motion | 实际顺序、焦点、关闭与低动态可见 | page state | P117-M012 | per-action image pairs |
| ABF-M-013 | verifier baseline | 从 raw／proof／clean／logs 重算全部行、source 与 Manifest | 全部 PASS；无自述替代 | canonical evidence | P117-M013 | results + verifier output |
| ABF-M-014 | disposable 副本 | 依次变异空白、单色、重复图、错 viewport、错 crop、browser chrome、错语义、source drift、ambient marker、probe 泄漏、缺 raw link、缺 cleanup | clean control 先 PASS；每个 mutation 唯一预期原因非零退出 | canonical evidence | P117-M014 | mutation results |
| ABF-M-015 | 结束 | 复算 13 项历史、候选、全部 Evidence、计数与精确清理 | history unchanged；五类计数披露；专用窗口关闭、profile／临时根不存在 | all read-only assets | P117-M015 | final results + cleanup |

## Evidence 合同

- 可运行 runner／测试源码：P3-117 自有 launch preflight、probe audit、capture geometry、image verifier、semantic mapping、privacy scan、mutation、Manifest 与 cleanup runner；不得复用 P3-116 已失效 verifier 作为通过依据。
- 逐行结构化结果：15 行及全部子动作有唯一 test／execution／capture ID、实际动作、预期／实际状态、结论、严重级别和 Evidence 路径。
- before／after：13 项固定输入、P3-116 candidate/contract hash、页面状态、viewport、profile／窗口／临时根。
- 图像链：每个必填动作至少包含 raw isolated-window image、probe-visible state proof、probe-hidden clean page crop、capture geometry JSON 与各自 SHA-256；同一 raw 可支持同一瞬间的 proof/clean 配对时必须明确 lineage，不得跨语义状态复用。
- 页面级日志：只记录 P3-117 capture ID、固定 synthetic action/state、target window、file scheme、geometry 和结果；禁止 AX/browser export、其他窗口／标签／账户／标题／路径。
- 语义证明：每个动作至少有一个由固定 probe／页面可见元素导出的确定性视觉锚点；verifier 必须能把错误 state/action 映射判为非零，PM 仍独立视觉抽查。
- source／history hash：13 项固定输入、8 项 candidate／contract before-after，以及所有 P3-116 停止资产只读一致。
- Manifest：非自指，覆盖 P3-117 tests／probe、runner、raw/proof/clean images、geometry、logs、structured results、mutations、cleanup 和交付物引用。
- 复跑入口：从空唯一临时根开始，复制候选、审计 probe、启动专用 app-mode、完成矩阵、关闭窗口、精确清理；GUI 动作必须由 Computer Use 实际执行，不得脚本伪造。
- 临时清理：只精确删除 `/private/tmp/lifeos-p3-117-native-capture-v1`；结束后 profile、candidate copy、raw working captures 与根路径均不存在。项目内 P3-117 Evidence 保留。

## 计数与 Pass 公式

- P0：候选／历史漂移、现有浏览器或真实／ambient 数据访问、网络／外部入口、伪造或错误来源截图、裁剪链／动作语义／版本绑定／verifier fail-open、Evidence 不诚实。
- P1：固定 viewport、页面级裁剪、布局／probe 隔离、视觉／键盘／motion 完成定义失败。
- P2：不影响完成定义的 Evidence 可读性问题；本轮 Pass 仍要求为 0。
- Unknown：任一窗口身份、截图来源、viewport、crop geometry、动作语义、source hash、历史保全或清理无法独立复核。
- Not Implemented：任一必填行／子动作、raw/proof/clean 图像链、runner、mutation 或 Evidence 缺失。
- Pass 公式：ABF-I-01～I-12、ABF-M-001～M-015 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；P3-116 当前 source hash、实际 GUI 动作、专用 Chrome 隔离、原生高分辨率截图链、三个 viewport、语义／隐私 verifier、12 类 mutation、历史保全和精确清理同时成立。
- 允许 N/A：None。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework：仅限 P3-117 自有 probe、capture geometry、截图／裁剪、runner、verifier、mutation、Manifest 或 Evidence 问题；不得修改 P3-116 candidate／contract 或本 ABF。
- 必须新建任务：任何 P3-116 候选／产品修改；需要改变用户结果、目录、数据、入口、截图来源、浏览器隔离、网络边界、依赖、能力、授权、架构、Schema/API、风险、冻结或阶段；需要实质修改本 ABF；或两轮正式 Rework 未通过。
- Blocked：专用 GUI Chrome app-mode、唯一窗口原生截图、页面裁剪、Computer Use 或必要本地工具在冻结入口下不可用，且不能在本 ABF 内安全恢复。不得用其他浏览器／截图路径替代。

## 候选基线与只读保全

- 候选输入：上表 13 项固定文件；P3-116 整个目录只读。
- 历史只读：P3-113 至 P3-116 全部资产、全部历史 Frozen 产品／原型、工程、账本、风险、冻结与 retained Pilot。
- 允许变化：仅 P3-117 task card、ABF、`lifeos/prototypes/LIFEOS-P3-117/`、P3-117 交付物、task-local precheck 和唯一临时根。
- P3-117 Pass 不等于 P3-116 Accepted、关键原型 Frozen、风险关闭、runtime Ready 或 Stage 4 准入；仍需 PM 验收、用户采纳和后续全新隔离独立评审。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：专项须在任何 GUI／临时文件动作前核对候选 hash、专用 Chrome app-mode 启动参数、窗口唯一性、probe 非侵入合同、raw→crop 链和精确清理。
- 最终冻结版本：`ABF-P3-117-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。

