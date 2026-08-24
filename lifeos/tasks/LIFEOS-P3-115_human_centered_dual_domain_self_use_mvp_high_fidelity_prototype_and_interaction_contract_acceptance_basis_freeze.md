# LIFEOS-P3-115 Acceptance Basis Freeze｜人本双领域自用 MVP 高保真原型与交互合同

## 冻结信息

- 任务 ID：`LIFEOS-P3-115`
- ABF ID／版本：`ABF-P3-115-v2`
- 生效决策：`D-0466`
- 创建与冻结时间：2026-08-24 22:08:51 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

把已通过 P3-114 独立评审的 P3-113 人本双领域产品候选转化为一个本地、代码原生、可交互、响应式、可访问并可机器复核的高保真原型与交互合同，使 Person-first 今日首页、工作 + 健康／健身双域、Source／内容身份、0–1 问题、1–3 建议、完整反馈→执行→结果→理解更新、有限 Memory candidate 和健康失败关闭可以被真实操作和清楚理解。

明确不冻结：产品需求、视觉系统、页面 IA、交互合同、关键原型、Schema/API、runtime、工程基线、风险或阶段。ABF 只冻结本轮候选凭什么通过。

明确非范围：真实数据／路径／DB／文件、retained Pilot、Tauri/IPC、模型、网络／云／第三方、Vault／连接器、删除／导出／权限设置、同步／多设备、L3、外部用户、真实用户研究、产品冻结、工程实现和 Stage 4。

## 授权和能力边界

- 允许写入：`lifeos/prototypes/LIFEOS-P3-115/`、指定 P3-115 交付物、task-local 本地预检报告、执行时新建并精确清理的 `/private/tmp/lifeos-p3-115-prototype-v1`。
- 允许数据：任务内固定、显著标记为 synthetic 的非敏感工作／健康／交互／反馈 fixture；不得混入任何真实个人内容。
- 允许入口：Chrome 直接打开 task-local `file:` 原型；原型内部纯前端状态转换和固定 scenario route。
- 允许工具／环境：本机既有文本／图像／hash 工具；Google Chrome（`com.google.Chrome`）经 Computer Use 正常控制；不得联网或安装依赖。
- 严格只读：P3-113/P3-114 全部资产；历史 Frozen PRD／原型；P3-105/P3-106；全部工程、账本、风险、冻结与 retained Pilot。
- 禁止能力：持久化真实内容、DB／文件读写接口、Tauri/IPC、模型、网络、远程资源、外部设计平台、后台服务、localhost、CDP、浏览器策略绕过。
- 投递前额外用户确认：None；用户已授权创建本任务。任何上述非范围能力必须另行确认和新任务／新 ABF。

## 固定候选输入

| 输入 | SHA-256 | 用途 |
|---|---|---|
| `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline.md` | `a81d5dd92d826e277f347f5f761a149e93839528c2c3352674b192ff0121dc85` | 人本双领域主候选 |
| `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md` | `c5fdcd30e3886a2f00e260346991714c9b0193e7ddd69abffd9d7bb3fd308ece` | Source 与反馈生命周期收口 |
| `lifeos/reviews/LIFEOS-P3-113_pm_review.md` | `fc387595ec31db54aaa58daf293c18e1602365f23c2f8a210d924b98f4ec1512` | P3-113 最终 PM 边界 |
| `lifeos/reviews/LIFEOS-P3-114_pm_review.md` | `72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78` | P3-114 采纳后 Complete 事实 |
| `lifeos/reviews/LIFEOS-P3-114/rework/rework-1/independent_review.md` | `a7d2cd9fb53eeb4b88ae199e95d1c5dc7049fc93670675ef034c63b7ccbc4351` | 独立产品判断 |
| `lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence/MANIFEST.md` | `486270122e98ea2111ecb4e22b4c91a459a4b5af2ff74b1982d973757ab90449` | 独立 Evidence lineage |
| `lifeos/reviews/LIFEOS-P3-114/pm_evidence/rework-1/MANIFEST.md` | `df384be261f4edb501d3a1ced75a1b4141e1bf15cb7ff4949488564e216f75dc` | PM 复验 lineage |

旧 P1-011 三张 Frozen 原型与 P3-106 响应式 Evidence只允许作为历史空间／克制／可读性参考；不得作为像素权威，不得复制 Project-first IA，也不得嵌入原型。

## 引用的 L1 长期原则

- L1-1 数据主权：仅固定 synthetic fixture 和 task-local 文件；真实数据与能力为零。
- L1-2 内容身份：用户输入、Source、Artifact、Derivation、Advice、Feedback、执行、结果、理解和 Memory candidate 可见区分。
- L1-3 生命周期完整：问题、建议、处置、执行、结果、理解、撤销、刷新和关闭重开的原型语义一致。
- L1-4 失败关闭：来源／授权／时效／健康条件失败时不出现可靠或训练型建议。
- L1-5 用户控制：建议不自动执行；反馈、暂停、撤销和长期记忆确认均由用户显式操作。
- L1-6 审计可信：事件顺序、作用对象、状态变化和用户可见回执一致。
- L1-7 Evidence 诚实：每个动态动作单独执行并绑定截图／日志／hash，不由静态 DOM 或汇总 Pass 推定。
- L1-8 历史保全：P3-113/P3-114 与历史 Frozen 资产只读。
- L1-9 授权不漂移：原型授权不扩展为真实 runtime、数据、模型、冻结或阶段权限。
- L1-10 可复核性：固定 viewport、fixture、scenario route、runner 和 Manifest 可重复得到一致结果。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | Person 是一级主体 | P0 | 首页无需先选 Project；Project 只出现在工作领域语境 | Not Pass，停止外推 |
| ABF-I-02 | 双领域与克制首页 | P1 | 工作与健康／健身并列；首屏 1–3 件事、0–1 问题 | Not Pass |
| ABF-I-03 | 内容身份与依据可见 | P0 | Source/Artifact/Derivation/Advice/Feedback/确认状态可区分和追溯 | Not Pass |
| ABF-I-04 | 问题门槛与失败关闭 | P0 | 未答／跳过／警示分别阻断或降级建议，不伪装已知 | 无相关建议 |
| ABF-I-05 | 建议不自动成为行动 | P0 | 认可、修改后接受、实际执行和结果相互独立 | Not Pass |
| ABF-I-06 | 反馈到理解更新完整 | P0 | 拒绝／忽略／延后／撤销及关闭重开均保持正确语义 | Not Pass |
| ABF-I-07 | 长期记忆必须再确认 | P0 | 一次结果只形成有限待确认 Memory candidate，未确认不跨日生效 | Not Pass |
| ABF-I-08 | 健康安全边界 | P0 | 非医疗、无诊断／治疗／保证；警示信号停止并建议适当专业支持 | 停止相关建议 |
| ABF-I-09 | 原型诚实且代码原生 | P0 | 不假称持久化／AI/runtime；无截图背景、远程资源或静态拼图冒充 | 停止并 Rework |
| ABF-I-10 | 响应式和可访问性 | P1 | 三 viewport 关键内容可达；键盘、焦点、Escape、reduced-motion 成立 | Not Pass |
| ABF-I-11 | Evidence 与历史可信 | P0 | 动态逐行、raw Evidence、hash、Manifest、历史保全和清理可复核 | Not Pass |
| ABF-I-12 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 保持 Open，R-0051 原有限关闭；Not Frozen；Stage 4 未准入 | 停止并报告 |

## 冻结验收矩阵

每行必须独立执行并产生唯一 test／fixture／execution ID；不得从总 Pass 批量映射。

| 行 ID | 入口／前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 核对会话、授权、模型、ABF 与固定输入 hash | 全部匹配；质疑窗口关闭 | 历史输入 | P115-M001 | session + hash log |
| ABF-M-002 | 新 task-local 副本 | Chrome 新标签页直接加载 `file:` 原型 | 首次正常加载成功；无网络／服务 | workspace 原型 | P115-M002 | precheck log + screenshot |
| ABF-M-003 | 默认 Today | 打开首页并核对首屏 | Person-first、双领域、1–3 件事、0–1 问题；无 Project-first | fixture | P115-M003 | full screenshot + structure JSON |
| ABF-M-004 | 建议卡 | 展开 Why now／Evidence | Source/Artifact/time/certainty/scope/safety/identity 可见 | 原始 fixture | P115-M004 | action log + screenshot |
| ABF-M-005 | 未回答关键问题 | 尝试查看健康建议 | 训练型建议不出现；只显示保守停止／记录选项 | 工作建议状态 | P115-M005 | state result + screenshot |
| ABF-M-006 | 问题分支 | 分别执行无警示、跳过、有警示 | 无警示才进入低风险候选；跳过降级；警示停止并建议专业支持 | 无诊断 | P115-M006 | 3 independent rows |
| ABF-M-007 | 可用建议 | 认可、修改后接受、拒绝、延后 | 四种处置各自可见；均不推定执行 | 原 Advice | P115-M007 | 4 independent rows |
| ABF-M-008 | 修改后接受 | 记录未执行、执行、结果 | FDB/EXE/RES 分离；结果后生成当天理解更新 | Source/Advice | P115-M008 | timeline + screenshots |
| ABF-M-009 | 已有结果 | 查看 Memory candidate 并拒绝／确认 | 默认待确认且有限范围；未确认不影响未来；拒绝不删历史 | 当日理解 | P115-M009 | state diff + screenshot |
| ABF-M-010 | 来源异常 | 分别注入 missing/stale/conflict/unauthorized | 个性化建议 fail-closed，缺口／冲突可见 | 原文和历史 | P115-M010 | 4 independent rows |
| ABF-M-011 | 已完成链 | 撤销 ANS/FDB/EXE/RES 并刷新／关闭重开 | 依赖理解／建议 stale 或重算；身份和历史不混淆、不复活 | Source 历史 | P115-M011 | 6 independent rows |
| ABF-M-012 | 全局导航／捕获 | 导航 Today/Memory/Domains；触发原型捕获 | Person IA 成立；捕获明确不持久化且不假成功 | 浏览器外状态 | P115-M012 | action log + screenshots |
| ABF-M-013 | 三固定 viewport | 1280×1024、1160×768、700×760 实际操作 | 无关键裁切／遮挡／横向丢失，信息层级稳定 | fixture | P115-M013 | 3 full screenshots |
| ABF-M-014 | 键盘／motion | 实际 Tab/Shift+Tab/Enter/Escape/skip link；启用 reduced-motion | 顺序、焦点、关闭和低动态均可观察 | 原型状态 | P115-M014 | per-action closure |
| ABF-M-015 | 源码／资源／Evidence | 扫描远程资源、整页图片、假持久化；运行 mutation verifier | 全部关闭；任一 raw Evidence/hash/row 变异使 verifier 非零 | fixed inputs | P115-M015 | scan + mutation results |
| ABF-M-016 | 结束 | 复算历史／source hash、Manifest、风险对账、精确清理 | 历史不变、真实数据/网络 0、残留 0、账本未改 | 所有只读资产 | P115-M016 | final results + cleanup |

## Evidence 合同

- 可运行源码：P3-115 自有静态／结构／状态机／动态闭环／mutation verifier。
- 逐行结果：16 行及全部子动作具有唯一 ID、实际操作、PASS/FAIL、严重级别和 Evidence 路径。
- 视觉 Evidence：三个 viewport 的完整实际 Chrome 原型截图；主状态、依据、反馈链、健康停止、来源异常均有独立截图。
- 动态闭环：使用 `UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或结构等价 JSON；刷新、关闭重开、Tab／Enter 不得互相替代。
- before／after：原型状态机快照、事件顺序、可见回执和历史输入 hash。
- source/history hash：固定输入与所有历史只读资产 before/after 一致。
- Manifest：非自指，覆盖源码、fixture、合同、runner、raw logs、screenshots、结构化结果和清理证明。
- 复跑：从空 `/private/tmp/lifeos-p3-115-prototype-v1` 复制固定候选、Chrome 预检、完整矩阵、verifier、Manifest、精确清理。
- 临时清理：只删除本任务创建的精确根；结束后路径不存在。

## 计数与 Pass 公式

- P0：Person 中心、身份、健康安全、用户控制、历史、授权、Evidence 真实性、远程能力或冻结／阶段边界任一底线失败。
- P1：完成定义内页面／状态、视觉层级、响应式、可访问性或交互可理解性失败。
- P2：不影响完成定义的轻量文案／Evidence 可读性问题；本轮 Pass 仍要求为 0。
- Unknown：任何关键状态、动作、视觉、hash、身份或边界无法复核。
- Not Implemented：任一必填页面／状态／动作／viewport／runner／Evidence 缺失。
- Pass 公式：ABF-I-01～I-12、ABF-M-001～M-016 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；Chrome `file:` 动态闭环、三个 viewport、状态机、interaction contract、mutation fail-closed、历史保全、网络／真实数据 0 和临时残留 0 同时成立。
- 允许 N/A：仅操作系统无法暴露的装饰性视觉差异可逐项说明；任何产品身份、健康停止、反馈生命周期、关键状态、动态动作、viewport、键盘或 Evidence 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅限不改变唯一产品结果、P3-113 语义、目录、数据、入口、能力、授权与 ABF 的原型 UI、状态机、交互合同、测试、Evidence 或文案问题。
- 必须新建任务：需要改变 P3-113 产品语义、页面结果、领域、能力、目录、数据、入口、真实目标、依赖、架构、Schema/API、授权、风险、冻结或阶段边界；或达到两轮正式 Rework。
- Blocked：固定输入/hash、合格 Chrome/Computer Use、必要本地字体／图像环境或唯一临时根空基线不可用，且不能在原 ABF 内安全恢复。

## 候选基线与只读保全

- 候选输入：本 ABF 固定的七项 P3-113/P3-114 文件。
- 历史只读：P3-113/P3-114 全部资产、旧 Frozen PRD／原型、P3-105/P3-106、工程、账本、风险与冻结文件。
- 允许变化：仅 P3-115 task card、ABF、原型目录、交付物和 task-local precheck／临时根。
- P3-115 Pass 不等于关键原型 Frozen。必须经过 PM Pass、用户采纳、全新隔离独立评审、PM 验收和用户单独冻结决定。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：专项启动前质疑确认 v1 固定了采纳前 Review hash `7edd…`，而当前 Review 因 D-0465 更新为 `72d…`。经只读核对，P3-115 原型目录与唯一临时根均不存在，尚未发生任何原型动作；PM 在启动前仅更新该固定输入谱系并重新冻结 v2，不改变任何验收标准、范围、矩阵、授权或完成定义。
- 最终冻结版本：`ABF-P3-115-v2`。
- 专项开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
