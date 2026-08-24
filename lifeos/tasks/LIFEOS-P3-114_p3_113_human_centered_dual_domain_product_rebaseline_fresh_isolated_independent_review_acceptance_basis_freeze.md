# LIFEOS-P3-114 Acceptance Basis Freeze｜P3-113 人本双领域产品重基线全新隔离独立评审

## 冻结信息

- 任务 ID：`LIFEOS-P3-114`
- ABF ID／版本：`ABF-P3-114-v1`
- 生效决策：`D-0461`
- 冻结时间：2026-08-24 20:50:00 CST (+0800)
- ABF 文件 SHA-256：由 PM 在本文件写入完成后记录于任务卡与 D-0461；本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 由未参与 P3-113 产品定义、整改或 PM 验收的全新隔离会话，独立判断 P3-113 初次候选 + Rework 1 的组合产品候选是否内部自洽、可测试、满足 LifeOS 长期原则，并可作为后续高保真原型任务的产品输入。
- 结论只能是 Pass／Rework／Blocked；Pass 只表示候选通过独立产品评审，不冻结产品定位、V1、领域模型、首页、原型、Schema/API、风险或阶段。
- 明确不冻结的产品需求：人本双领域产品定义、首页合同、长期记忆语义、Source/反馈合同及历史资产替代关系。
- 明确非范围：工程实现、原型制作、真实个人／健康／工作数据、真实 DB／路径／文件、真实模型、Vault／连接器、Tauri/IPC、网络／云／第三方、同步／多设备、L3、外部用户、风险关闭／重开、工程基线、关键资产冻结、Stage 4。

## 授权和能力边界

- 允许目录：只写 `lifeos/deliverables/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review.md`、`lifeos/reviews/LIFEOS-P3-114/independent_review.md`、`lifeos/reviews/LIFEOS-P3-114/evidence/` 与唯一 `/private/tmp/lifeos-p3-114-product-review-v1`。
- 允许数据与夹具：任务卡列明的项目只读产品／治理文件、P3-113 脱敏结构化 Evidence、评审会话自行设计的固定非敏感反例。
- 允许入口／接口：本地文本读取、JSON 解析、hash／Manifest 复算、固定非敏感结构化验证；不得运行候选应用或数据库。
- 允许工具／环境：离线本地文件工具；禁止模型调用、本地模型、网络或外部来源作为评审证据。
- 严格只读资产：P3-113 全部任务卡、ABF、交付物、专项／PM Review 与 Evidence；P3-111/P3-112；历史 Frozen 产品／领域／信任／架构资产；全部账本。
- 禁止能力与外部目标：不得修改候选、工程、账本、风险或冻结；不得访问任何真实或 retained Pilot 资产；不得创建后续原型任务。
- 投递前额外用户确认：None；用户已授权创建本只读独立评审任务。用户把任务卡路径投递至合格全新会话才启动执行。

## 引用的 L1 长期原则

- L1-1 数据主权：只读项目资产与固定非敏感夹具，不触碰真实数据或外部目标。
- L1-2 内容身份：用户方向、Source/Artifact、AI 派生、建议、Feedback、执行、结果和确认事实必须分离。
- L1-3 生命周期完整：来源、记忆、问题、建议、反馈、理解更新、撤销、过期和关闭重开语义一致。
- L1-4 失败关闭：信息不足、冲突、过期、失权或健康高风险时停止／降级，不伪装确定性。
- L1-5 用户控制：建议不自动执行；长期泛化、重大动作、删除和未来影响需要明确控制。
- L1-6／L1-7 审计可信与 Evidence 诚实：独立逐行反例和结构化 Evidence 支撑每个结论。
- L1-8 历史保全：P3-113 与历史 Frozen 资产只读，不用新结论改写旧事实。
- L1-9 授权不漂移：独立评审授权不扩展到实现、真实能力、冻结、风险或阶段。
- L1-10 可复核性：固定输入、独立设计、反例、hash、Manifest 与复跑入口可复核。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 全新会话与先设计后读取 | P0 | 会话与 P3-113 执行／PM 隔离；先冻结独立测试设计，再读取候选正文／Evidence | Blocked／Rework |
| ABF-I-02 | 人是一级主体 | P0 | 全局结果、首页、记忆和建议以人为主体；Project 仅为工作领域上下文 | Rework |
| ABF-I-03 | 历史资产影响诚实 | P0 | 历史 Frozen 状态不删除／不改写；继续有效、工作域限定、重新打开、候选替代和未来关卡可解释 | Rework |
| ABF-I-04 | 双领域七段闭环可测试 | P0 | 工作+健康／健身覆盖感知、记忆、理解、问题、建议、反馈、更新且无空标签 | Rework |
| ABF-I-05 | Source 与内容身份完整 | P0 | 至少两个清晰 Source 及 Artifact／Derivation／Advice／Feedback、授权、时间、范围、时效和失效链可追溯 | Rework |
| ABF-I-06 | 反馈到理解更新完整 | P0 | 认可、修改后接受、拒绝、忽略、延后、回答、执行、结果、理解和长期候选记忆分离；关闭重开不混淆 | Rework |
| ABF-I-07 | 首页合同克制且可控 | P1 | 1–3 建议、0–1 高价值问题；依据／不确定性／范围可见；可拒绝、修改、暂停且不自动行动 | Rework |
| ABF-I-08 | 健康与信息不足失败关闭 | P0 | 无诊断／治疗；未答、冲突、过期、失权或警示信号触发停止／保守降级／专业支持 | Rework |
| ABF-I-09 | 记忆与未来影响受控 | P0 | 推断不覆盖事实；候选偏好未经明确确认、范围和时效不得影响未来日期 | Rework |
| ABF-I-10 | 不提前实现、冻结或外推价值 | P0 | 产品语义不写成 Schema/API／页面冻结；不外推 P3-111 工程或合成场景为真实价值／Stage 4 | Rework |
| ABF-I-11 | Gate 与后续单线边界准确 | P1 | Gate 1–3 可评审，Gate 4 仅条件可行，Gate 5 仅假设；原型路线依赖与授权明确 | Rework |
| ABF-I-12 | Evidence、历史和清理可复核 | P1 | 输入／历史 hash、独立反例、逐行结果、Manifest、复跑和精确清理成立 | Rework |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | 任务启动 | 未读取 P3-113 候选 | 核验投递、全新会话、模型、ABF hash、授权与临时根不存在 | I-01 前置成立 | 全部候选 | IR-001 | `session_boundary.json` |
| ABF-M-002 | 独立设计 | 只读任务卡／ABF／L1 | 在候选读取前写独立问题、反例和判定法并封存 hash／时间 | 设计先于候选阅读且非复制 P3-113 测试 | P3-113 Evidence | IR-002 | `test_design.md`, `read_order.json` |
| ABF-M-003 | 固定输入 | 设计已冻结 | 复算 P3-113 初次／Rework／PM Manifest 与任务指定输入 | hash、数量和历史链一致，无遗漏或漂移 | 全部只读输入 | IR-003 | `input_integrity.json` |
| ABF-M-004 | 产品主体 | 组合候选 | 攻击 Person／Project、用户结果、范围和产品定位一致性 | I-02，非项目管理器／医疗产品／全能 AI | 历史定位 | IR-004 | `product_center_review.json` |
| ABF-M-005 | 历史资产 | 冻结影响矩阵 | 逐项验证旧状态、适用性和未来替代关卡 | I-03，无静默解冻／改写 | Frozen 记录 | IR-005 | `frozen_asset_impact_review.json` |
| ABF-M-006 | Source／记忆 | 固定双域输入 | 追踪 Source→Artifact→Derivation／Memory→Advice，注入缺失／冲突／过期／失权 | I-04/I-05/I-09；错误身份不得进入建议 | 候选原文 | IR-006 | `source_memory_counterexamples.json` |
| ABF-M-007 | 首页／问题／建议 | 多种信息状态 | 核对数量、问题阈值、basis、不确定性、用户控制和不自动执行 | I-07；不足时无伪确定性 | 健康边界 | IR-007 | `home_advice_contract_review.json` |
| ABF-M-008 | 反馈生命周期 | 建议各处置分支 | 独立走认可／修改／拒绝／忽略／延后／未执行／执行／结果／撤销／重开 | I-06/I-09；身份、时间、对象、范围和未来影响不混淆 | 原建议与 Source | IR-008 | `feedback_lifecycle_counterexamples.json` |
| ABF-M-009 | 健康安全 | 未答／警示／冲突等反例 | 核对停止、降级、非医疗边界及专业支持措辞 | I-08，无诊断／治疗／安全保证 | 用户权威 | IR-009 | `health_safety_review.json` |
| ABF-M-010 | 跨领域固定情境 | 合成 fixture | 独立重演完整闭环及关闭重开，比较初次与 Rework 候选 | 全链可追溯，P0 修复未制造新矛盾 | 无真实数据 | IR-010 | `cross_domain_replay.json` |
| ABF-M-011 | Gate／路线 | 全部语义结果 | 逐问 Gate 1–5，核对原型→复评→工程→Pilot 单线与授权 | I-10/I-11；不冻结、不创建后续任务 | Stage 4 | IR-011 | `gate_and_route_review.json` |
| ABF-M-012 | 独立攻击 | 已完成基础矩阵 | 执行预先冻结的反例并记录支持／反驳／Unknown | 反例逐项有证据，不由候选自报 PASS 推定 | 候选文件 | IR-012 | `independent_counterexamples.json` |
| ABF-M-013 | 收口 | 所有行完成 | 汇总计数、Review、Manifest、复跑与精确临时根清理 | I-12；P0/P1/P2/Unknown/NI 诚实 | 风险／冻结／账本 | IR-013 | `results.json`, `temporary_residue.json`, `MANIFEST.md` |

## Evidence 合同

- 独立测试设计：必须在读取候选正文和专项 Evidence 前写入并 hash；不得复制 P3-113 的问题清单作为独立性主证据。
- 逐行结构化结果：M-001～M-013 各自独立，不以总 Pass 或 PM Pass 推定。
- source／history hash：至少绑定 P3-113 任务卡、ABF、初次／Rework 交付物、初次／Rework专项 Manifest、PM Review、初次／Rework PM Manifest及任务卡列明直接输入。
- Manifest：非自指，列 SHA-256、bytes、文件和角色。
- 复跑命令：只解析文本／JSON、计算 hash、验证结构化反例和精确临时根；不运行应用、DB、模型或网络。
- 临时清理：只允许精确清理 `/private/tmp/lifeos-p3-114-product-review-v1`；不得扫描、读取或删除其他 `/private/tmp` 内容。

## 计数与 Pass 公式

- P0：任一 P0 不变量失败、独立性不足、历史改写、健康误导、身份混淆、越权或虚假冻结／阶段外推。
- P1：影响产品候选完整性、体验合同、路线或 Evidence 可复核性的实质缺口。
- P2：不影响唯一结果的清洁项，必须披露。
- Unknown：必要事实无法判断且未被安全关闭。
- Not Implemented：矩阵要求但没有实际独立评审动作／Evidence。
- Pass 公式：M-001～M-013 全部 PASS；P0=0、P1=0、Unknown=0、Not Implemented=0；P2 已披露且不影响完成定义；历史只读、无越权、临时残留为零；结论仅为 `Independent Product Review Pass / Awaiting PM Acceptance`。
- 允许 N/A：仅实现、真实使用或产品价值验证等明确非范围；不得对独立性、主体、双域闭环、Source、反馈、健康、历史资产影响或 Evidence 使用 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-114 自有测试设计、runner／Evidence／Review 问题，用户结果、候选输入、目录、授权和本 ABF 不变，且历史可保全。
- 必须新建任务：候选需修改；用户结果、领域、真实数据／模型、目录、入口、健康风险、实现、架构、Schema/API、冻结／风险／阶段边界变化；ABF 需实质修改；或两轮正式 Rework 后仍未通过。
- Blocked：全新独立性、模型、必要固定输入／hash、唯一临时根空基线或授权无法成立；不得用访问真实数据／外部来源解除。

## 候选基线与只读保全

- 候选输入：P3-113 初次／Rework 交付物及 `evidence/MANIFEST.md`、`evidence/rework-1/MANIFEST.md`；PM Review 与两轮 PM Evidence Manifest。
- 历史只读：P3-111/P3-112、P3-113 初次资产、历史 Frozen 产品／领域／信任／架构资产和全部账本。
- 允许发生变化的文件：仅 P3-114 交付物、Independent Review、Evidence 与精确临时根。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：尚无。
- 最终冻结版本：`ABF-P3-114-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
