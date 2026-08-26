# LIFEOS-P3-116 Acceptance Basis Freeze｜Person-centered IA V1.0 与高保真产品原型重基线

## 冻结信息

- 任务 ID：`LIFEOS-P3-116`
- ABF ID／版本：`ABF-P3-116-v1`
- 生效决策：`D-0468`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

把用户新确认的 Person-centered 产品规则、`LifeOS高保真原型IA-V1.0` 与兼容的历史信任／架构原则，收敛为一套内部一致、可真实操作、响应式、可访问、可机器复核的本地代码原生高保真产品原型与交互合同。候选必须清楚回答 Today、Me、Contexts、Memory 与 Global AI／AI Workspace 如何共同服务同一个 Person，并通过状态、证据与用户控制证明 AI 不替用户确认。

明确不冻结：最终产品需求、核心领域模型、技术架构、视觉资产、关键原型、Schema/API、runtime、工程基线、风险或阶段。ABF 只冻结本轮候选凭什么通过。

明确非范围：真实个人／工作／健康数据或文件、真实路径／DB、retained Pilot、Tauri/IPC、模型、网络／云／第三方、Vault／连接器、删除／导出／权限设置、同步／多设备、L3、外部用户、真实用户研究、产品／架构冻结、工程实现与 Stage 4。

## 授权和能力边界

- 允许写入：`lifeos/prototypes/LIFEOS-P3-116/`、指定 P3-116 交付物、task-local 本地预检报告，以及执行时新建并精确清理的 `/private/tmp/lifeos-p3-116-prototype-v1`。
- 允许数据：任务内固定、显著标记为 synthetic 的非敏感 Person／Work／Health／Context／Memory／AI 交互 fixture。
- 允许入口：Google Chrome 直接打开 task-local `file:` 原型；纯前端本地状态转换和固定 scenario route。
- 允许工具／环境：本机既有文本、图像、hash 工具；Google Chrome（`com.google.Chrome`）经 Computer Use 正常控制；不得联网或安装依赖。
- 严格只读：P3-113/P3-114/P3-115 全部任务、ABF、交付物、Review、Evidence、PM Evidence 与原型；全部历史 Frozen 资产、工程、账本、风险、冻结与 retained Pilot。
- 禁止能力：持久化真实内容、DB／文件能力接口、Tauri/IPC、模型、网络、远程资源、外部设计平台、后台服务、localhost、CDP 或浏览器策略绕过。
- 投递前额外用户确认：None；用户已授权创建本任务。任何非范围能力必须另行确认并建立新任务／新 ABF。

## 固定候选输入

| 输入 | SHA-256 | 用途 |
|---|---|---|
| `lifeos/architecture/LifeOS高保真原型IA-V1.0.md` | `adcc9daf3b8f0fcf27a13176eabb1581c6079d47b48a26ee88cbaba209704243` | 当前 Person-centered IA 与页面／交互权威输入 |
| `lifeos/architecture/LifeOS架构基线V1.0.md` | `2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32` | 架构原则及待调和的 Project 语义输入 |
| `lifeos/reviews/LIFEOS-P3-113_pm_review.md` | `fc387595ec31db54aaa58daf293c18e1602365f23c2f8a210d924b98f4ec1512` | 已采纳产品候选与历史边界 |
| `lifeos/reviews/LIFEOS-P3-114_pm_review.md` | `72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78` | 已采纳独立产品评审事实 |
| `lifeos/deliverables/LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract.md` | `ccb518b073f5e791a84a18f2e91a37aa008f12ee323596a3357dd96d55242c07` | 原 ABF 下 PM Pass、现作为历史差异输入的原型候选 |
| `lifeos/reviews/LIFEOS-P3-115_pm_review.md` | `f5c0cf27b35619b9450105809255be22aa825f7278dc75859036200e0a19c7f4` | P3-115 历史 PM Pass 与未冻结事实 |
| `lifeos/ACCEPTANCE_GOVERNANCE.md` | `86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c` | L1/L2 与 Rework／新任务治理 |

视觉探索图片若由用户在专项会话中重新提供，只能作为空间、密度、层级与 Apple/macOS 风格参考，不进入固定输入 hash，不得覆盖以上文字规则；未重新提供不得阻塞本任务。

## 引用的 L1 长期原则

- L1-1 数据主权：只使用固定 synthetic fixture 与 task-local 文件，真实数据和外部能力为零。
- L1-2 内容身份：用户原文、确认事实、AI Observation、AI Inference、Decision、Derivation、External Source 与候选 Action 必须可区分。
- L1-3 生命周期完整：观察、推断、候选、确认／编辑／拒绝／忽略／纠正、执行、结果和后续理解不互相替代。
- L1-4 失败关闭：证据不足、来源异常、权限移除或健康警示时不强行给结论或建议。
- L1-5 用户控制：Context、事实、Action、Decision、长期理解与上下文使用不得由 AI 静默确认。
- L1-6 审计可信：重要判断能沿 Understanding → Derivation → Evidence → Source 回溯。
- L1-7 Evidence 诚实：每个页面状态与动态动作分别绑定 raw Evidence、结构化结果和 hash。
- L1-8 历史保全：P3-113 至 P3-115 及历史 Frozen 资产只读，不追溯改写其 Pass／冻结事实。
- L1-9 授权不漂移：原型授权不扩展为真实 runtime、模型、数据、冻结、风险或阶段权限。
- L1-10 可复核性：固定 fixture、viewport、scenario、runner 与 Manifest 能重复得到一致结果。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | Person 是一级主体 | P0 | 所有页面和注意力分配围绕 Person；Domain 是长期视角，Project 仅为 Context 子型 | Not Pass |
| ABF-I-02 | 一级 IA 唯一且克制 | P0 | 一级仅 Today、Me、Contexts、Memory；Settings 弱化；Work/Health/Project/Task/Calendar/Agent 均非一级 | Not Pass |
| ABF-I-03 | Global AI 是全局层 | P0 | 主要页面均可达；继承 Person/Page/Selection Context；复杂任务渐进进入 AI Workspace | Not Pass |
| ABF-I-04 | Today 按整体优先级分配注意力 | P0 | Today's Focus 最多一个，不按 Domain 配额；空状态与证据不足状态合法 | Not Pass |
| ABF-I-05 | Me 不是 Profile | P1 | 呈现现在的我、关注、长期视角与可追溯／可纠正理解；无头像账户区冒充主体模型 | Not Pass |
| ABF-I-06 | Context 不等于 Project | P0 | Contexts 按正在进行／持续关注／已结束组织；Context 创建建议必须用户确认 | Not Pass |
| ABF-I-07 | Memory 是证据层 | P0 | 类型区分清楚；Memory Detail 可回到 Derivation、Evidence 与 Source，不退化为笔记／KPI Dashboard | Not Pass |
| ABF-I-08 | AI 不替用户确认 | P0 | Observation、Suggestion、candidate Action／Decision／Plan 等均有确认、编辑、拒绝、忽略或纠正控制 | Not Pass |
| ABF-I-09 | Evidence／为什么可达 | P0 | 重要判断有依据；不足时明确表达没有足够证据，不为填充页面生成建议 | Not Pass |
| ABF-I-10 | 双领域深度边界 | P0 | MVP 仅 Work 与 Health/Fitness 启用深度智能；其他数据可承接但明确未启用；新 Domain 一次一个并显示四类 Gate | Not Pass |
| ABF-I-11 | Global Shell 符合确认方向 | P1 | 窄 Icon Rail、hover 提示、弱 Settings、无通知铃铛／中心、无左下头像／账户区、Global AI 常驻可达 | Not Pass |
| ABF-I-12 | 视觉、响应式与无障碍 | P1 | 克制、轻量、留白、弱 Dashboard；三个 viewport、键盘、焦点、Escape 与 reduced-motion 成立 | Not Pass |
| ABF-I-13 | 架构／IA 冲突被显式调和 | P0 | 明确 Project 在 Core Domain／Repository 与产品 IA 中的不同层级，不静默改写架构或产品事实 | Not Pass／PM 决策 |
| ABF-I-14 | Evidence、历史与授权可信 | P0 | 动态逐行、mutation fail-closed、历史 hash、网络／真实数据关闭态和精确清理成立 | Not Pass |

## 冻结验收矩阵

每行及其子动作必须独立执行并生成唯一 test／execution ID，不得从汇总 Pass 批量映射。

| 行 ID | 入口／前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 核对投递、隔离、模型、ABF 与七项固定输入 | 全部匹配；质疑窗口关闭 | 历史输入 | P116-M001 | session + hashes |
| ABF-M-002 | 两份新基线与历史候选 | 建立 IA／架构／P3-113／P3-115 Gap 与调和矩阵 | 每个冲突有事实层级、当前处置和 PM 待决策项 | 原文件 | P116-M002 | reconciliation matrix |
| ABF-M-003 | Global Shell | 实际导航并 hover Icon Rail | 一级入口唯一；文字提示、弱 Settings、Global AI 可达；禁止元素不存在 | fixture | P116-M003 | actions + screenshots |
| ABF-M-004 | Today 默认／空／证据不足 | 分别加载三种状态并展开 Why | Focus 0–1；noticed 与确认安排分离；空与不足状态诚实 | 原始 fixture | P116-M004 | 3 rows + screenshots |
| ABF-M-005 | Me | 查看四层结构、Domain 状态与理解依据 | 非 Profile；Work/Health 深度启用，其他仅承接；可纠正／撤回 | Memory identity | P116-M005 | actions + screenshots |
| ABF-M-006 | Contexts | 切换进行／关注／结束并触发创建建议 | 非 Kanban／Domain 分栏；Project 仅为类型；创建须确认 | Domain 状态 | P116-M006 | actions + screenshots |
| ABF-M-007 | Context Detail | 查看现在／Next／最近／理解／Related-Evidence | 结构完整；Global AI 自动继承当前 Context | Source 历史 | P116-M007 | actions + screenshots |
| ABF-M-008 | Memory | 浏览、筛选并区分七类身份 | 非笔记列表／KPI；身份、来源和确认状态可见 | 原文 | P116-M008 | actions + screenshots |
| ABF-M-009 | Memory Detail | 沿 Understanding→Derivation→Evidence→Source 回溯 | 原始依据可达；断链／不足明确披露 | Evidence identity | P116-M009 | trace + screenshots |
| ABF-M-010 | 任意主要页面 | 打开 Global AI，核对 Person/Page/Selection，临时移除一类 Context | 当前使用范围透明；移除即时影响候选输出且不改持久事实 | 页面状态 | P116-M010 | context diff + screenshots |
| ABF-M-011 | AI Workspace | 从 Global AI 渐进展开复杂 Work+Health 场景 | 中区 Conversation+Work、右侧 Context Inspector；不是 ChatGPT Clone | Context selection | P116-M011 | actions + screenshots |
| ABF-M-012 | AI 候选对象 | 依次确认／编辑／拒绝／忽略／纠正 Observation、Action、Decision 候选 | 用户权威和身份生命周期清楚；无自动执行／确认 | 原始 AI 输出 | P116-M012 | state transitions |
| ABF-M-013 | Domain activation | 尝试启用第三 Domain | 一次仅一个；数据、价值、反馈、安全 Gate 均可见且未满足时关闭 | Work/Health | P116-M013 | gate states |
| ABF-M-014 | 三固定 viewport | 1280×1024、1160×768、700×760 操作核心路线 | 关键内容／操作可达，无要求系统适应屏幕、无关键裁切或横向丢失 | fixture | P116-M014 | full screenshots |
| ABF-M-015 | 键盘／motion | Tab/Shift+Tab/Enter/Escape/skip link；启用 reduced-motion | 顺序、焦点、关闭与低动态可观察 | 原型状态 | P116-M015 | per-action closure |
| ABF-M-016 | 源码与关闭态 | 扫描通知、头像、宽 Sidebar、远程资源、网络、存储与假 AI/runtime | 禁止项为零；原型诚实披露本地 synthetic 状态 | fixed inputs | P116-M016 | scans |
| ABF-M-017 | disposable Evidence 副本 | 变异矩阵、raw Evidence、hash、身份链与禁止项 | 每类变异均使 verifier 以精确原因非零退出 | canonical evidence | P116-M017 | mutation results |
| ABF-M-018 | 结束 | 复算历史／source hash、Manifest、计数、风险对账与精确清理 | 历史不变、五类计数披露、网络／真实数据 0、残留 0 | 全部只读资产 | P116-M018 | final results |

## Evidence 合同

- 可运行 runner／测试源码：P3-116 自有静态、状态机、动态闭环、视觉、可访问性和 mutation verifier。
- 逐行结构化结果：18 行及全部子动作有唯一 ID、实际操作、结论、严重级别和 Evidence 路径。
- before／after：页面状态、Context 使用范围、对象身份、历史输入 hash 和禁止能力关闭态。
- 日志／快照：三个 viewport 的实际 Chrome 完整截图，覆盖所有核心页面、空／不足／失败状态和关键交互。
- source／history hash：七项固定输入及 P3-113/P3-114/P3-115 指定历史资产 before/after 一致。
- Manifest：非自指，覆盖源码、fixture、合同、runner、raw logs、screenshots、结构化结果和清理证明。
- 复跑命令：从空 task-local 临时根复制候选、Chrome 预检、完整矩阵、verifier、Manifest 与精确清理。
- 临时清理：只删除 `/private/tmp/lifeos-p3-116-prototype-v1`；结束后路径不存在。

## 计数与 Pass 公式

- P0：主体、IA、AI 权威、内容身份、证据、安全、领域边界、历史、授权或 Evidence 真实性失败。
- P1：完成定义内页面／状态、视觉层级、响应式、可访问性或交互可理解性失败。
- P2：不影响完成定义的轻量文案或 Evidence 可读性问题；本轮 Pass 仍要求为 0。
- Unknown：任何关键页面、状态、动作、视觉、hash、身份、调和结论或边界无法复核。
- Not Implemented：任一必填页面、状态、动作、viewport、runner 或 Evidence 缺失。
- Pass 公式：ABF-I-01～I-14、ABF-M-001～M-018 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；代码原生原型、Chrome `file:` 动态闭环、交互／视觉合同、三个 viewport、mutation fail-closed、历史保全、网络／真实数据 0 和临时残留 0 同时成立。
- 允许 N/A：仅未重新提供的聊天视觉探索图片可标 N/A；任何正式文字规则、核心页面／状态／动作、身份、安全、viewport、键盘或 Evidence 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅限不改变本唯一用户结果、两份新基线、目录、数据、入口、能力、授权和本 ABF 的原型 UI、状态机、交互／视觉合同、测试、Evidence 或文案问题。
- 必须新建任务：需要改变一级 IA、Context／Memory／Global AI 核心语义、页面结果、领域范围、真实能力、目录、数据、入口、依赖、架构、Schema/API、授权、风险、冻结或阶段；需要实质修改本 ABF；或达到两轮正式 Rework。
- Blocked：固定输入/hash、合格 Chrome/Computer Use、必要本地呈现环境或唯一临时根空基线不可用，且不能在原 ABF 内安全恢复。

## 候选基线与只读保全

- 候选输入：本 ABF 固定的七项文件。
- 历史只读：P3-113/P3-114/P3-115 全部资产、历史 Frozen 产品／原型、全部工程、账本、风险、冻结与 retained Pilot。
- 允许变化：仅 P3-116 task card、ABF、原型目录、交付物、task-local precheck 和精确临时根。
- P3-116 Pass 不等于关键原型 Frozen、架构冻结、runtime Ready 或 Stage 4 准入。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：待专项在任何原型动作前核对固定输入、规则优先级、完整页面／状态集合、允许目录和动态 Evidence 合同。
- 最终冻结版本：`ABF-P3-116-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
