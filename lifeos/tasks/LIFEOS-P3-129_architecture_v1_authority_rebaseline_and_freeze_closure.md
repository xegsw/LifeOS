# LIFEOS-P3-129｜架构 V1.0 权威重基线与冻结收口

## 任务信息

- 任务 ID：`LIFEOS-P3-129`
- 标题：架构 V1.0 权威重基线与冻结收口
- 风险等级：`Gate`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 主责 Agent／会话类型：全新技术架构专项会话；完成候选包后由另一个全新隔离独立评审会话只读复核
- 所需执行能力：本地文件只读、Markdown／JSON、hash、静态 verifier；不运行产品 Runtime
- 是否需要独立评审：`Mandatory`
- 独立评审触发理由：正式技术架构冻结替换；V1.0 将成为长期权威并 supersede V0.1
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-129_architecture_v1_authority_rebaseline_and_freeze_closure_acceptance_basis_freeze.md`
- Frozen ABF SHA-256：`df3c4e9879a624e05ef8f7eb5b71d1a5835422db0eea278e2fc88404032b40fb`

## 用户决策与目的

用户于 2026-08-26 明确确认：`确认以架构 V1.0 正式取代 V0.1`。

本任务不再讨论是否回到 V0.1；它负责把这项方向决策收敛为可冻结、可继承、无账本歧义的精确架构合同，并通过强制独立评审验证其与产品宪法、核心领域、AI 信任、P3-126 Runtime 事实及 P3-128 映射合同的兼容性。

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务仅处理工作区内的架构文档、冻结历史和结构化 Evidence；不访问真实个人数据、真实 DB／路径／文件、Pilot、网络、云、第三方、凭据、模型或外部系统，不运行产品 Runtime，不扩大产品能力。

## Task Contract

### 1. 唯一用户结果

形成一个经过独立评审、可由 PM 在最终用户关卡后精确执行的冻结包：以当前 `lifeos/architecture/LifeOS架构基线V1.0.md` 的固定内容为技术架构 V1.0 权威，正式 supersede 技术架构 V0.1 的后续规范效力，同时保留 V0.1 全部历史事实与 Evidence；明确冻结范围、非冻结实现细节、兼容／改变／废止矩阵及唯一 canonical promotion patch。

### 2. 允许范围

- 允许写入：
  - `lifeos/architecture/LIFEOS-P3-129/`
  - `lifeos/deliverables/LIFEOS-P3-129_architecture_v1_authority_rebaseline_and_freeze_closure.md`
  - 独立评审会话仅写 `lifeos/reviews/LIFEOS-P3-129/`
- 允许只读输入：本任务卡、Frozen ABF、当前 V1.0 架构文件、FREEZE_STATUS 的技术架构记录、P2-016 冻结决策包／PM Review、P0-003/P0-009 核心领域、PROJECT_CONTEXT 的产品／信任／技术方向、P3-113/P3-114 人本产品候选、P3-126/P3-127 当前 Runtime 事实、P3-128 交付物／PM Review及任务卡定向列出的账本片段。
- 允许工具：`rg`、`wc`、`sed`、`shasum`、只读 JSON/Markdown parser、task-local verifier。
- PM 最终用户关卡后唯一允许的 canonical promotion：把 V1.0 文件状态行从 `Architecture Baseline Draft` 精确替换为经评审确认的 Frozen/supersession 状态，并同步 PM 账本；专项 Agent 不执行该 promotion。

### 3. 禁止范围

- 不修改当前 `lifeos/architecture/LifeOS架构基线V1.0.md`、任何 V0.1 历史交付物／Review/Evidence、P3-126/P3-128 资产或工程代码。
- 不运行 Tauri、IPC、DB、测试 App、浏览器、模型或网络；不访问 Pilot、真实数据、真实路径、旧临时根或外部目标。
- 不冻结 Schema/API、IPC 签名、Tauri capability、SQLite 表／PRAGMA、具体 Adapter API、模型／Agent 供应商、云／同步栈、生产 SLA、工程基线、产品 IA、风险或 Stage 4。
- 不把“V1.0 目标结构”解释为本任务内立即迁移代码；不删除或改写 V0.1 历史。
- 不自动创建 Fast Track 工程任务。

### 4. 关键不变量与 Pass 条件

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | 固定输入与 hash 完整，当前 V1.0 候选唯一绑定 | 逐文件复算 | `fixed_inputs.json` |
| AC-02 | 给出 V0.1→V1.0 的逐项 `retained / changed / superseded / deferred` 矩阵 | 逐行检查，无未分类规范 | `v0_to_v1_reconciliation.json` |
| AC-03 | V1.0 与产品宪法、11 核心对象+Link、AI 权限／确认／Evidence 语义无冲突 | 语义矩阵及反例 | `cross_baseline_compatibility.json` |
| AC-04 | 明确 V1.0 冻结范围与仍不冻结的实现细节 | 正负清单、无隐式 Schema/API 冻结 | `freeze_scope.json` |
| AC-05 | 明确 P3-126/P3-128 的保留、过渡和后继工程继承规则 | 只读事实核对 | `runtime_transition.json` |
| AC-06 | 形成 canonical promotion patch，除状态／supersession 元数据外不改 V1.0 正文 | pre/post hash、逐字节 diff | `canonical_promotion_patch.json` |
| AC-07 | verifier 对正确包通过，并拒绝候选 hash 替换、遗漏 V0.1 行、越界冻结和非授权正文变化 | pristine + 至少 4 类 mutation | runner、results、mutation results |
| AC-08 | 独立评审从固定输入自建核对，明确 Gate 1～4 与 Gate 5 N/A/适用性 | 独立 runner／Review／Manifest | `lifeos/reviews/LIFEOS-P3-129/` |
| AC-09 | 历史资产全部只读，最终 Manifest 非自指且可复算 | before/after hash 与 Manifest | history verification、Final Manifest |
| AC-10 | 结论诚实：评审前不宣称 Frozen，PM／用户关卡前不执行 canonical promotion | 声明扫描与账本核对 | 主交付物与 Review |

Pass 公式：AC-01～AC-10 全部 PASS；P0/P1/P2/Unknown/Not Implemented 均为 0；独立评审为 Pass；无越权、无历史漂移、无未解释的 V0.1→V1.0 规范差异。

### 5. Evidence 等级

- 本任务采用：`Gate`。
- 必须包含逐行矩阵、固定输入 hash、可运行 verifier、至少四类 mutation、历史保全、非自指 Manifest 和全新隔离独立评审。
- 纯文案自述、总数、PM 推断或用户方向确认不能替代兼容矩阵与独立评审。

### 6. 新任务触发器

若收口需要改变当前 V1.0 正文中的实质架构语义、扩大冻结范围、改变核心领域／AI 权限／V1 产品范围、冻结 Schema/API、访问真实数据或运行产品能力，则停止并返回 PM；不得在本任务中静默改写。Task Contract 不变的矩阵、Evidence、verifier和非实质元数据修正留在本任务 Closure Cycle。

## 顺序与独立性

1. 技术架构专项会话只创建冻结候选包、矩阵、verifier、Evidence和主交付物。
2. PM 接收候选后，必须使用另一个全新隔离会话完成只读独立评审；执行会话不得自评。
3. PM 同时核对主交付物与独立评审；Pass 后仍等待一次最终用户关卡确认。
4. 最终用户确认后，PM 才能执行已经独立评审的 exact canonical promotion 和账本更新。

## 一次性授权方式

用户已明确确认“以架构 V1.0 正式取代 V0.1”，该确认覆盖本完整收口链的创建、候选包编制、Evidence、同范围修正、独立评审与 PM 验收；不需要重复确认合同内目录或只读边界。最终 exact freeze promotion 仍按 Gate 规则在独立评审与 PM Pass 后由用户确认一次。

将本最终任务卡绝对路径投递到全新技术架构专项会话即启动第一阶段。候选完成后，不复用该会话做独立评审。

## 输入与最小启动包

必须完整读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡与 Frozen ABF
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/FREEZE_STATUS.md` 技术架构行与当前适用性摘要
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/reviews/LIFEOS-P2-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md`
- `lifeos/reviews/LIFEOS-P3-128_pm_review.md`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`
- `lifeos/PM_OPERATING_MODEL.md` 的风险分级、独立评审和冻结章节
- `lifeos/ROLE_MATRIX.md` 的技术架构与独立评审章节
- `lifeos/STAGE_GATES.md` Gate 1～5
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`

如发现与 P3-113/P3-114、P3-126/P3-127 或 PROJECT_CONTEXT 的具体冲突，再定向补读对应文件；不得无目标全文扫描无关历史。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-129_architecture_v1_authority_rebaseline_and_freeze_closure.md`
- 候选／Evidence：`lifeos/architecture/LIFEOS-P3-129/`
- 独立评审：`lifeos/reviews/LIFEOS-P3-129/independent_review.md` 及其独立 Evidence／Manifest
- 复跑：候选与独立评审各自提供一条 task-local 命令

## PM 验收与最终关卡

- PM 必须同时验收候选包与独立 Review，不能仅凭用户方向确认直接冻结。
- PM Pass 后状态为 `Awaiting Final User Freeze Confirmation`。
- 用户最终确认后才将 V1.0 标为 Frozen／权威、将 V0.1 标为 Superseded for forward architecture authority，并更新 FREEZE_STATUS、CURRENT_STATUS、TASK_REGISTRY、DECISION_LOG；历史 V0.1 资产继续只读保全。
- 本任务不关闭任何风险，不进入 Stage 4，不自动创建 Fast Track 工程任务。
