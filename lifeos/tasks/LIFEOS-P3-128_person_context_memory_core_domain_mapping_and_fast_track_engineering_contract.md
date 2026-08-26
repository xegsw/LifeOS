# LIFEOS-P3-128｜Person / Context / Memory 核心映射与 Fast Track 工程合同

## 任务信息

- 任务 ID：`LIFEOS-P3-128`
- 风险等级：`L2`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / Awaiting Task-card Delivery / Not Started`
- 主责 Agent／会话类型：产品架构专项会话；不得复用刚完成 P3-127 的独立评审结论作为自证
- 所需执行能力：本地只读分析、产品／领域建模、结构化合同与一致性检查
- 是否需要独立评审：`Conditional`
- 独立评审触发理由：只有候选要求改变既有 Frozen 核心领域语义、成为关键冻结输入，或 PM 无法复核对象／权限／生命周期映射时触发；不得仅因任务编号或历史惯例自动独立评审。

本任务采用 D-0516 后 Governance V2，不另建 ABF，不填写推荐模型或推理强度。

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只在项目工作区内读取已列明的治理、产品、架构与候选源码，并只写任务自己的产品架构交付物。不得访问真实个人数据、Pilot、真实 DB、真实用户目录、网络、云、第三方、凭据或外部目标；不得执行 Tauri、IPC、migration、模型或产品 Runtime。

## Task Contract

### 1. 唯一用户结果

形成一份可直接约束下一张 4–5 小时 `MVP 1.0 Fast Track Vertical Slice #1` 工程任务的实现合同：明确 `Person / Domain / Context / Memory / Global AI Context` 如何兼容映射到既有 Frozen 核心领域语义与当前 P3-126 Runtime，避免第二套 Domain Model，并明确下一任务可实现和不可实现的边界。

本任务不写产品代码，不冻结领域模型、Schema/API、IA、Runtime 或架构。

### 2. 允许范围

- 允许写入：
  - `lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md`
  - `lifeos/architecture/LIFEOS-P3-128/`
- 允许只读输入：
  - 根目录 `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/PROJECT_CONTEXT.md`
  - `lifeos/FREEZE_STATUS.md`
  - `lifeos/STAGE_GATES.md` 的 Stage 3→4 与 Gate 1–4 相关章节
  - `lifeos/architecture/LifeOS架构基线V1.0.md`
  - `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
  - `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
  - `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md`
  - `lifeos/reviews/LIFEOS-P3-114_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-126/candidate/`（只读，用于核对当前实现接口和模块事实）
  - `lifeos/reviews/LIFEOS-P3-127_pm_review.md`
- 允许数据：仓库内既有合成 fixture 与文档中的固定非敏感示例；不得创建或读取真实个人内容。
- 允许工具：本地只读文本／源码检查、结构化 JSON／Markdown 校验、hash 与静态一致性检查。

### 3. 禁止范围

- 不实现产品代码、UI、migration、DB、Repository、IPC、Tauri、模型或 Agent。
- 不增加或启用真实能力；不访问 Pilot、真实 DB／路径／文件／文本、Vault、网络、云、第三方或产品模型。
- 不重新设计 P3-116/P3-126 视觉，不扩大一级 IA，不加入通知中心、宽 Sidebar、领域 Dashboard 或独立 AI 一级页面。
- 不把 `Person / Domain / Context / Memory` 简单改名为数据库表，也不把旧 `Project` 静默提升为所有生活 Context。
- 不让 Domain／Context／Link 产生权限扩张；不允许 LifeOS 静默创建 Context 或 AI 替用户确认事实、Action、Decision、长期记忆。
- 不修改历史任务、候选、Review、Evidence、Manifest、PM 账本、风险或冻结状态。
- 不冻结核心领域模型、Schema/API、架构、IA 或 Runtime；不恢复工程基线，不进入 Stage 4，不自动创建 P3-129。

### 4. 必须继承的映射约束

交付物必须在以下约束内作出一个明确、可实现的推荐，不得把选择留给下一工程会话：

1. `Person` 是一级主体与本地所有者上下文，不得与 `Source`、账户 Profile 或 AI 画像混为一体。
2. `Domain` 是长期生活视角和受控分类／读取视图，不是一级 App，也不得成为授权捷径。
3. `Context` 是 Person 正在经历、推进或持续关注的上下文容器；`Project` 只能作为其中一种，不得覆盖健康 Program、Life Event 或 Observed Context。
4. `Memory` 是基于 `Source / Artifact / Assertion / Decision / Derivation / Feedback / Link` 的长期记忆与 Evidence Browser，不得成为第二份权威原文库。
5. 用户原文、用户确认事实、AI Observation、AI Inference、Decision、Derivation、External Source 必须保持身份分离。
6. Global AI Context 固定由 `Person Context + Page Context + Selection Context` 组装；每一输入类别必须可见、可移除并经 Authorization 检查。
7. 既有核心对象 `Project / Artifact / Source / Assertion / Decision / Action / Event / Derivation / Feedback / Authorization / AuditEntry / Link` 的 Frozen 身份、来源、确认、失效和不复活语义不得被削弱。
8. 新工程仍遵守 `UI → Application → Domain → Ports → Adapters`；业务代码不得直接依赖 SQL，Model 与 Agent 保持分离。

### 5. 关键不变量与 Pass 条件

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | 列出所有适用 Frozen 与 Not Frozen 输入，并明确优先级、冲突和不可覆盖项 | 固定资产影响矩阵 | `frozen_input_impact.json` |
| AC-02 | 对 `Person / Domain / Context / Memory / Global AI Context` 与既有 11 对象 + `Link` 给出逐项映射、权威来源、身份和生命周期 | 双向映射矩阵；不得有未解释空白 | `object_mapping.json` |
| AC-03 | 明确 Context 的稳定 ID、类型、状态、创建／确认／关闭语义，以及 Project 与非 Project Context 的兼容关系 | 状态机和反例检查 | `context_lifecycle.json` |
| AC-04 | 明确 Memory 只是证据／记忆读取模型；可从 AI Understanding 追溯到 Derivation、Evidence、Source/Artifact | 追溯链示例与身份检查 | `memory_provenance.json` |
| AC-05 | 明确 Person／Page／Selection Context Resolver 与 Context Inspector 的输入、输出、移除、授权重检和证据不足语义 | Resolver 合同矩阵 | `context_resolver_contract.json` |
| AC-06 | 明确 Application Service、Repository Port、SQLite Adapter、read model、transaction 与 event 边界；不得让 UI 或 Orchestrator 直连 SQL | 分层依赖图和接口草案 | `application_port_contract.json` |
| AC-07 | 对 P3-126 当前三 IPC、Runtime root、UI DOM/CSS 与数据结构给出保留／适配／后置清单 | 只读源码事实矩阵 | `p3_126_compatibility.json` |
| AC-08 | 给出下一张 Fast Track 的唯一 Vertical Slice、允许修改目录、候选 IPC／数据变化、测试矩阵、Evidence 等级和 Stop Rule | 工程 handoff 合同 | `fast_track_handoff.json` |
| AC-09 | 至少覆盖 silent Context creation、Domain 扩权、AI 画像冒充 Person、Memory 复制原文、失效证据继续消费、UI/Orchestrator 直连 SQL 六类反例 | 反例矩阵 | `negative_cases.json` |
| AC-10 | 交付物明确：哪些是事实、候选决定、后置项与需 PM 决策项；不得声称 Frozen、Stage 4 Ready 或真实 MVP 已实现 | 术语／状态扫描 | 主交付物 |

Pass 公式：AC-01～AC-10 全部通过；P0=0、P1=0、Unknown=0、Not Implemented=0。允许 P2 仅限不会改变下一工程任务语义或验收终点的实现细节，并须逐项说明。

### 6. Evidence 等级

- 本任务采用：`L2（产品／架构合同）`。
- 必须提供结构化逐项矩阵、双向映射、反例、固定输入影响分析和可复核 Manifest。
- 不需要动态 GUI、actual-Tauri、真实 DB 或独立评审；若输出要求改变 Frozen 核心语义，必须停止并回 PM，不能自行将任务升级或继续实现。

### 7. 新任务触发器

仅当完成映射必须改变 Frozen 核心领域语义、V1 范围、AI 权限边界、Person-centered IA、技术架构，或必须冻结 Schema/API 时，关闭当前合同并新建 L3/Gate 任务。测试、Evidence、Manifest、措辞和同范围映射缺口留在 P3-128 内完成。

## 一次性授权方式

- 本任务卡已完整展示全部 Task Contract。用户将本任务卡绝对路径投递到产品架构专项会话，即构成创建后的唯一执行授权，覆盖分析、交付、结构化 Evidence、包内修正和 PM 验收，不再要求额外边界确认。
- 执行中若新增真实数据、不可逆动作、网络／第三方、权限／导出、风险／冻结／Stage 或核心语义变更，必须停止并回 PM。

## 输入与最小启动包

专项会话必须先读取：

1. 根目录 `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. 上述“允许只读输入”中列出的直接输入

大型文件按项目分页规则读取；只定向读取历史 Review／Evidence。不得因任务为合同型工作跳过 Frozen 冲突检查。

## 执行要求

1. 开始前记录任务卡绝对路径投递、会话类型和接收时间，并检查工作区已有修改。
2. 只写允许目录；历史输入全部只读。
3. 先完成结构化 Evidence，再从同一事实生成主交付物，避免 Markdown 与机器可读矩阵漂移。
4. 提交前运行自写 verifier：验证 AC-01～AC-10 全部存在、引用路径有效、映射无空白、反例齐全、Manifest hash一致。
5. 同范围缺口在包内修正，不拆任务、不要求重复授权。
6. 不修改 PM 账本，不自动创建 Fast Track 工程任务。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md`
- Evidence：`lifeos/architecture/LIFEOS-P3-128/`
- 必须包含：上述 7 个 JSON、`verify_contract.py`、`verification.json`、`MANIFEST.md`
- 聊天回复：结论、映射摘要、冲突、测试／Evidence、P0/P1/P2/Unknown/Not Implemented、下一 Fast Track 是否具备创建条件、需 PM 决策事项。

## PM 验收

- PM 只按长期质量原则和本 Task Contract 验收，不新增完成定义。
- 若不触发 Frozen 语义变化且 PM Pass，本 L2 任务按 Governance V2 自动 `Accepted / Complete`，无需用户逐任务采纳。
- PM Pass 仅允许创建下一张结果级 Fast Track 工程 Task Contract；不自动授权工程执行、不冻结资产、不改变风险、不进入 Stage 4。
