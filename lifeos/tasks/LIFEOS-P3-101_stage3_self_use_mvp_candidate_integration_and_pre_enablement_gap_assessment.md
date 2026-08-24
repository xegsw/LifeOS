# LIFEOS-P3-101｜有限 Stage 3 自用 MVP 候选整合与真实启用前差距评估

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务只读评估项目工作区内当前账本、固定 Review／Evidence 摘要及固定非敏感测试边界，用于建立有限 Stage 3 候选事实基线和下一任务方向；不访问真实个人文件、既有个人数据库、真实用户路径、网络、云、第三方系统、凭据或外部目标，不运行或启用 Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户能力。超出范围立即停止并回报 PM。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-101`
- 任务名称：有限 Stage 3 自用 MVP 候选整合与真实启用前差距评估
- 优先级：P1
- 类型：产品／阶段治理只读决策任务；非受控工程能力包；不适用 P3 Engineering Fast Lane。
- 唯一结果：建立当前事实基线，并只推荐一个尚未授权执行的后续方向。
- 推荐 Agent：Codex 新建产品／阶段治理专项会话。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 模型选择理由：需跨多条已完成能力线、风险边界和 Stage Gate 做严格事实／外推分离。
- 允许降级模型：`gpt-5.5` / `xhigh`。
- 禁止降级条件：发现账本冲突、Stage Gate 证据冲突、R-0040 边界不清或需要判断真实启用范围时不得降级。
- 必须升级条件：使用允许降级模型时命中上述任一条件，停止并改用首选配置；不可用则 Blocked。
- 后备模型：`gpt-5.5` / `xhigh`。
- 是否需要后续独立评审：Conditional；本任务若仅输出保持 Stage 3 的准备建议，不强制独立复评；若未来任务涉及真实启用、R-0040、冻结或 Stage 4，必须另行独立评审。
- 工程／项目账本修改：专项会话均不允许。
- 主责：产品 PM／Stage Governance Analyst；协审：技术架构、AI 信任与安全、数据／领域、独立 QA。
- 必须通过：Gate 1、Gate 3、Gate 4 的评估完整性；Gate 5 只判断现有证据，不得虚构用户价值验证。
- 状态：Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery。
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-101_stage3_self_use_mvp_candidate_integration_and_pre_enablement_gap_assessment_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-101-v1`
- ABF SHA-256：`c12f81c7510cde59f108143446863cf291d9e75e335461f8b0bc80a82fad17cf`
- 正式 Rework：0/2。

## 会话、授权与隔离

- 建议新建会话；不得复用 P3-097 工程、P3-098 独立评审或 P3-100 风险判断会话，避免把实现／风险关闭上下文直接当成阶段结论。
- 用户把本任务卡绝对路径投递至符合条件的新会话即授权本任务只读执行；仅在 PM 主会话创建或提及任务卡不启动专项执行。
- 首份会话报告必须记录任务卡路径、会话类型、精确接收时间、ABF hash 和实际可观察模型配置；内部标签不可观察时如实写 `not exposed`。
- 投递前仍需单独用户确认的例外：任何真实个人数据／DB／路径／文件、Vault、Tauri/IPC、网络、云／第三方、同步、多设备、L3、外部用户、风险关闭／重开、工程基线恢复、Schema/API 或关键冻结、Stage 4。当前任务均未授权。

## 最小启动包与定向补读

完整读取：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡与 `ABF-P3-101-v1`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

高风险定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：阶段推进、用户确认、独立评审、两层验收治理与风险管理章节。
- `lifeos/ROLE_MATRIX.md`：PM、产品、技术架构、AI 信任安全、数据／领域、独立 QA 职责。
- `lifeos/STAGE_GATES.md`：Stage 3→4 和 Gate 1／3／4／5。
- `lifeos/FREEZE_STATUS.md`：当前阶段与冻结摘要。
- `lifeos/TASK_REGISTRY.md`：P3-079 至 P3-101。
- `lifeos/RISK_LOG.md`：R-0013、R-0014、R-0015、R-0019、R-0021、R-0040、R-0051。
- `lifeos/DECISION_LOG.md`：D-0332 至 D-0415，只定向读取相关行。

直接输入：

- `lifeos/reviews/LIFEOS-P3-080_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-081_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-086_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-088_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-090_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-092_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-093_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-097_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-098_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-100_pm_review.md`
- 以上 Review 直接引用的 Manifest；只在 hash／结论冲突时打开具体 Evidence，不全文重读无关历史。

## 必须工作

1. 执行 ABF-M-001 至 M-010，每行生成独立结构化 Evidence。
2. 对账当前阶段、任务、风险和冻结事实；冲突必须显式列出，不得自行覆盖账本。
3. 建立当前候选能力地图，区分受控合成、固定非敏感本地夹具、独立复评、真实启用和冻结状态。
4. 逐项评估 Stage 3→4 五项硬门槛及 Gate 1／3／4／5；不得把 Accepted／Independent Pass 外推为真实能力或阶段准入。
5. 单独核对 R-0040 与 R-0051：R-0051 的有限关闭不得抵消 R-0040 的真实 Tauri/IPC 条件。
6. 建立真实启用前差距矩阵，并严格应用 ABF 的四分方向公式，只推荐一个后续方向。
7. 报告 P0/P1/P2/Unknown/Not Implemented 数量，区分风险事实计数与交付质量计数。
8. 核对输入只读保全并精确清理 P3-101 自身临时产物。

## 交付物与 Evidence

- 交付物：`lifeos/deliverables/LIFEOS-P3-101_stage3_self_use_mvp_candidate_integration_and_pre_enablement_gap_assessment.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-101/evidence/`
- Evidence 至少包含：`session_start.json`、`ledger_reconciliation.json`、`candidate_capability_map.json`、`stage_gate_matrix.json`、`risk_boundary_matrix.json`、`pre_enablement_gap_matrix.json`、`next_direction_decision.json`、`input_integrity.json`、`temporary_residue.json`、`rerun.md` 和非自指 `MANIFEST.md`。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出结论、计数、路径和需要 PM 确认的问题。

## 验收、停止与限制

- 只有 ABF 10/10 行可复核、计数完整、历史只读成立且只输出一个允许方向时才可提交 PM。
- 本任务不允许修改工程代码、项目账本、历史 Review／Evidence／Manifest，不允许创建或执行后续任务。
- 不允许关闭／重开 R-0040 或 R-0051，不允许冻结、恢复基线、启用真实能力或进入 Stage 4。
- 若需要扩大到真实数据／路径、Tauri/IPC、工程、风险、Schema/API、冻结或阶段，立即停止；由 PM 关闭当前边界并另建任务。
- 本任务涉及阶段和真实启用前的高风险治理判断，可跳过本地模型预检，但必须注明理由；本地模型不得决定阶段或授权边界。
