# LIFEOS-P3-051｜R-0049 风险关闭决策与 R-0048 边界复核

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定工作区、候选代码和合成测试数据，用于防御性代码审查、Evidence 核验与本地回归结论复核；不授权访问外部或第三方目标、真实用户数据或真实凭据，也不涉及未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“攻击、反例、旁路、改绑、权限提升”等术语仅指本地合成环境中的负向验证。所有既有只读、用户确认、独立性和停止条件继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-051
- 任务名称：R-0049 风险关闭决策与 R-0048 边界复核
- 优先级：P1
- 任务类型：独立风险决策评估 / Evidence 收口；不属于工程整改
- 是否适用 P3 Engineering Fast Lane：No；涉及风险关闭判断
- 推荐执行 Agent：Codex 新建隔离会话
- 推荐理由：WorkBuddy 无可用额度；风险关闭不得由 P3-048 工程执行、P3-049 或 P3-050 复评会话自证，须使用未承载任何 LifeOS 工作的新 Codex 会话。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：R-0049 涉及 Authorization terminal 历史、Tombstone 控制包络、Evidence 可信度和风险关闭边界；需要保守判断与完整证据链。
- 允许降级模型：`None`
- 禁止降级条件：风险关闭、删除／撤回／权限／证据链边界、用户确认与阶段关卡均在范围内；不得降低模型、推理强度或独立性。
- 必须升级条件：证据、hash、任务结论或风险范围冲突时，在同一新会话升级为 `gpt-5.6-sol` + `max`；仍无法判定则 Blocked 并回报 PM。
- 后备模型：`None`
- 是否需要后续独立评审：No；本任务本身为独立风险评估，最终关闭仍需 PM 验收与用户明确确认。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：风险关闭评估负责人、独立 QA / Evidence Reviewer
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、技术架构负责人
- 必须通过的关卡：Gate 2、Gate 3、Gate 4
- 状态：In Progress
- 实际派发：全新 Codex 任务 `01a021d6-6ef6-7d22-baa6-7cd695befcd0`，host `local`，`gpt-5.6-sol` + `xhigh`，2026-08-21 CST。

## 会话路由与边界

- 是否建议新建会话：Yes，硬性条件。
- 禁止复用：P3-048 工程执行会话、P3-049、P3-050、PM 主会话和所有已承载 LifeOS 工作的会话。
- 允许写入：仅 `lifeos/deliverables/LIFEOS-P3-051_r0049_risk_closure_decision_and_r0048_boundary_review.md`、P3-051 专属 review/evidence 目录和本地预检目录。
- 必须只读：P3-031、P3-046、P3-047、P3-048、P3-049、P3-050 全部工程、任务、Review 与 Evidence；所有主账本。
- 禁止：修改 SQL、测试、历史 Evidence、风险状态、冻结状态或工程基线；连接真实 DB/Vault/Tauri/IPC/云/第三方模型；创建或启动后续任务。

## 背景与目标

P3-048 已针对 Tombstone generic→Authorization 改绑完成窄整改；P3-050 在全新隔离 Codex 会话中，以先封存独立计划、再延迟读取 P3-049 资产的方式，形成 832 PASS / 0 BYPASS 的独立矩阵。PM 复跑确认 P3-048 552 PASS、P3-047 等价 297 PASS、P3-031 exit 0，以及 40/40 历史 preservation hash 一致。

用户已采纳 P3-050 Pass 并要求继续。本任务必须严格判断：R-0049 是否可建议在“候选 SQL + 合成 SQLite + 当前 Evidence + 有限 Stage 3”范围内关闭；同时确认 R-0048 的 lifecycle/audit/outbox 其余风险不被 P3-050 覆盖，必须保持 Open。

## 必读输入

1. `AGENTS.md`、`lifeos/CURRENT_STATUS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`。
2. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
3. `lifeos/RISK_LOG.md` 中 R-0048、R-0049；`lifeos/DECISION_LOG.md` 中 D-0226 至 D-0237；`lifeos/FREEZE_STATUS.md`。
4. P3-045 合同、P3-046/P3-047/P3-048 交付物及 PM Review，P3-047 PM-CE-06 Evidence。
5. `lifeos/reviews/LIFEOS-P3-050/independent_review.md`、`lifeos/reviews/LIFEOS-P3-050_pm_review.md`、P3-050 Evidence 与 PM Evidence Manifest。

## 必须完成的核查

1. 逐项映射 R-0049 风险描述中的 terminal 父／子历史与 cleanup 控制包络，确认每项都有对应合同、测试和独立证据；不得用测试总数替代映射。
2. 核对 P3-050 的新建会话证明、独立计划封存、脚本独立性、832 PASS、PM 复跑、历史 preservation 与 P3-048/P3-047/P3-031 回归。
3. 明确 R-0049 的关闭建议只能覆盖候选 SQL 与合成 SQLite 边界；列出失效条件及任何仍需后续真实 DB / 真实能力验证的内容。
4. 明确 R-0048 不得因 R-0049 关闭而连带关闭；列出仍开放的 lifecycle/audit/outbox/generation/time/幂等命令范围。
5. 明确不冻结 Schema/API、SQL migration、工程基线或阶段；不恢复基线、不启用真实能力。
6. 结论只可为“建议关闭 R-0049”“保持 R-0049 Open”“Blocked”；R-0048 必须为“保持 Open”。出现证据冲突、P0/P1、明确 P2 bypass 或独立性不足时不得建议关闭。

## 交付与验收

- 决策包：`lifeos/deliverables/LIFEOS-P3-051_r0049_risk_closure_decision_and_r0048_boundary_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-051/independent_review.md`
- Evidence Manifest：`lifeos/reviews/LIFEOS-P3-051/evidence/MANIFEST.md`
- 本地预检：按项目规则运行；不可用时记录后继续人工评审。
- 验收通过不等于关闭风险。仅当独立评估建议关闭、PM 验收且用户再次明确授权关闭 R-0049 后，PM 才可更新风险账本；R-0048 始终保持 Open。
