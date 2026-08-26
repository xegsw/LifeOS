# LIFEOS-P3-128｜Person / Context / Memory 核心映射与 Fast Track 工程合同

## 结论

**[候选决定]** 采用一个不增加第二套 Core Domain 的实现方向：`Person` 是本地所有者上下文，`Domain` 是受控长期读取视角，`Context` 是由既有核心对象组成且拥有稳定应用级 ID 的容器投影，`Memory` 是证据／理解读取模型，`Global AI Context` 是一次请求内可见、可移除、逐项重检授权的 Resolver 结果。

**[事实]** Frozen 核心领域模型仍只有 11 个对象加 `Link`；Frozen 技术架构仍要求 `UI → Application → Domain → Ports → Adapters`。P3-113/P3-114 的人本候选、P3-126 Runtime 与其 UI 都是 Accepted / Not Frozen 输入，不能覆盖这些 Frozen 约束。

**[事实]** P3-126 当前 Runtime 已验证的实现事实是：构建期 task-local root、`capture_record`／`get_today`／`runtime_status` 三个 IPC、固定合成输入、SQLite/audit、离线 fail-closed 和零 renderer plugin permission。它并未实现持久 Person、Context、Memory 或 Global AI 的领域合同。

**[候选决定]** 下一张任务应当只做一个 4–5 小时的 L2 垂直切片：在全新合成工程根中，把一次固定原文捕获通过用户显式确认关联到一个预置的 Work / Project-backed Context；重开后从 Today／Context 查看关联和 Memory provenance。Context Inspector 仅预览 Person + Page + Selection，不调用模型或 Agent。

**[后置项]** 非 Project Context、Domain 深度激活、真实 AI／Agent、健康推断、搜索／FTS、外部来源、导出／删除／恢复、同步、真实数据和 Schema/API 冻结均不进入下一切片。

**[需 PM 确认]** 本合同不要求新的产品、Frozen 语义或权限决策。PM 如认可本任务通过，只需按下文 handoff 创建一个新的 L2 Fast Track Task Contract，并在创建时明确新工程根、唯一临时根、物理多行 source allowlist、合成 fixture、实际 App 是否纳入动态 Evidence 和精确清理规则；创建不授权执行。

## 一、映射推荐

| 概念 | 推荐定位 | 不能是什么 | Frozen 兼容点 |
|---|---|---|---|
| Person | 本地所有者、用户权威与最小 Context scope | Source、账户 Profile、AI 画像、隐式授权 | User-confirmed/AI-inference 身份保持分离；Authorization 仍六维判定 |
| Domain | 长期生活视角与受控读取／分类视图 | 一级 App、权限捷径、Project 替代物 | Link/Derivation 可表达视图，但 Source/Artifact/Authorization 仍是权威 |
| Context | Person 正在经历、推进或关注之事的应用级容器投影 | 第 12 个 Core object、通用 Project 容器、静默创建的记录 | Project 是其一种 canonical backing；其他类型以后由既有对象与 Link 组合 |
| Memory | 从核心对象和 Evidence 构成的长期读取模型 | 第二份原文库、不可解释的个人画像 | 回溯 Derivation、Source/Artifact/version、Feedback、Link 与 Authorization |
| Global AI Context | Person + Page + Selection 的短生命周期 Resolver envelope | 持久 profile、全局检索授权、Agent execution plan | 每个 ref 在消费前重检，用户可移除，输出必须记录 Derivation 输入集 |

完整的 5×12 双向映射、身份权威和生命周期在 [object_mapping.json](../architecture/LIFEOS-P3-128/object_mapping.json)；Frozen/Not Frozen 优先级和冲突裁决在 [frozen_input_impact.json](../architecture/LIFEOS-P3-128/frozen_input_impact.json)。

## 二、Context 与 Memory 的可实现边界

**[候选决定] Context 稳定 ID：** Project-backed Context 使用 `ctx:project:<project-id>`；这是 Context Projection 的稳定 ID，不改变 Project ID。非 Project Context 只有在用户确认名称、类型、范围和 backing refs 后才分配独立 ID。状态为 `candidate → confirmed → active|watching → closed`；关闭保存历史，重新打开必须重新核验当前有效依据。

**[候选决定] Memory：** 每个 MemoryItem 只保存／返回对象引用、身份、状态与 provenance，而非成为正文权威。理解链为 `Source → Artifact/version → Assertion/Decision/Action/Event/Link → Derivation → Feedback → MemoryItem`。任一版本、来源、授权、证据或 tombstone 条件失效时，读取模型必须变为 `stale`、`evidence_unavailable` 或 `review_required`，不能继续产生可靠建议。

状态机与反例见 [context_lifecycle.json](../architecture/LIFEOS-P3-128/context_lifecycle.json)；两条可回溯 Memory trace 及失效规则见 [memory_provenance.json](../architecture/LIFEOS-P3-128/memory_provenance.json)。

## 三、Global AI Context Resolver

**[候选决定]** Resolver 只接受 Person Context、当前 Page Context、显式 Selection 和用户主动选择的 Domain/Context。它先展示包含原因、来源／证据状态与移除控件，应用用户移除后才逐项重检主体、范围、动作、目的、位置、时效、Source、版本、generation、tombstone 与 Evidence。未知／冲突即拒绝并显示安全的证据或权限缺口；不搜索或补充隐藏的相邻 Context。

这个 Resolver 不确认任何事实、Decision、Action 或长期记忆。若未来调用模型，必须把 exact ResolverResult 写入新的 Derivation；本 Fast Track 仅实现 preview，不调用 ModelPort 或 AgentPort。完整合同见 [context_resolver_contract.json](../architecture/LIFEOS-P3-128/context_resolver_contract.json)。

## 四、架构与 P3-126 兼容策略

**[事实]** P3-126 的 UI 是人本 IA／合成演示与 Runtime 的组合候选；其中 Context／Memory／Global AI 大多是 browser-memory fixture。P3-128 不把 UI 文案或 fixture 当作持久域模型事实。

**[候选决定]** 后继在一个新任务根中保留 P3-126 三 IPC 的兼容字段和 root/SQLite fail-closed 底座；将业务逻辑下沉到 Capture、Context Recovery、Context Association、Memory Query 和 Resolver Application Services。Repository Port、AuthorizationPort、FeedbackRepository、AuditPort 和 DomainEventPort 约束业务层；UI／Orchestrator 不触碰 SQL。

P3-126 逐项 `retain / adapt / defer` 事实表在 [p3_126_compatibility.json](../architecture/LIFEOS-P3-128/p3_126_compatibility.json)，分层、Port、事务与 event 边界在 [application_port_contract.json](../architecture/LIFEOS-P3-128/application_port_contract.json)。

## 五、唯一 Fast Track 工程合同

唯一结果是“Project-backed Context Recovery”：固定合成 Person 通过一个 Work 视图，捕获不可变原文，用户明确确认与预置 Project-backed Context 的关联，重开后能在 Today／Context／Memory detail 查看经 Source、Artifact/version、Link、Feedback、Audit 支撑的链路。它不创建通用 Context、Person 或 Memory 表；不启用模型、网络、Agent、真实数据或新一级 IA。

后继候选只新增 `confirm_capture_context` 与 `get_context_recovery` 两个窄 IPC；`capture_record`、`get_today`、`runtime_status` 保持兼容。最少验收包括：显式确认、禁止静默创建、重启恢复、provenance、临时移除不持久化、证据／授权失败关闭、严格 DTO、无 UI/Orchestrator 直连 SQL、精确 cleanup。完整写入范围、候选数据与 IPC、11 条验收矩阵、L2 Evidence 和 Stop Rule 在 [fast_track_handoff.json](../architecture/LIFEOS-P3-128/fast_track_handoff.json)。

## 六、反例与关卡

覆盖了静默 Context 创建、Domain 扩权、AI 画像冒充 Person、Memory 复制原文、失效 Evidence 消费、UI/Orchestrator 直连 SQL，以及 Project 泛化、Feedback 覆盖历史与未确认 Context 扩展等反例；详见 [negative_cases.json](../architecture/LIFEOS-P3-128/negative_cases.json)。

| 关卡 | 本任务结论 | 边界 |
|---|---|---|
| Gate 1 产品一致性 | Pass（L2 合同层） | Person-first，不变成企业后台／领域 Dashboard／独立 AI App |
| Gate 2 数据与来源 | Pass（L2 合同层） | 所有 Memory 与 Context 读取回链 Source/Artifact/version/Link/Feedback |
| Gate 3 AI 权限与信任 | Pass（L2 合同层） | Resolver 可见、可移除、逐项授权；本轮没有模型消费 |
| Gate 4 技术可行性 | 条件成立 | Port／事务／Runtime 兼容合同完备；未来任务仍须以 L2 实现 Evidence 验证 |
| Gate 5 用户价值 | 未判 Pass | 未做真实用户或真实数据价值外推 |

未触发独立评审：本交付物没有改变 Frozen 核心语义、V1 范围、AI 权限边界、关键 IA、技术架构，也不构成冻结输入。若 PM 判断下一任务需要这些变化，必须停止本路线并新建 L3/Gate 合同。

## 七、自检与状态

`verify_contract.py` 已验证 AC-01 至 AC-10、所有 JSON、路径、映射完整性、反例、handoff、主交付物术语和 Manifest hash。结果见 [verification.json](../architecture/LIFEOS-P3-128/verification.json)，稳定资产 hash 清单见 [MANIFEST.md](../architecture/LIFEOS-P3-128/MANIFEST.md)。

本任务计数：P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0。结论是 **Completed candidate contract / Not Frozen / Not Stage 4 / no engineering execution performed**。
