# LIFEOS-P3-099｜R-0051 风险关闭决策评估

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅对任务卡固定的本地源码、Review、Evidence、Manifest 和固定非敏感 task-local 测试夹具进行防御性只读风险评估；不访问真实个人文件、既有个人数据库、网络、云、第三方系统、凭据或外部目标，不授权未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“反例、旁路、删除、失败注入”等术语仅指本地固定非敏感夹具。超出范围立即停止并回报 PM。

## 任务信息

- 任务 ID：`LIFEOS-P3-099`
- 任务名称：R-0051 风险关闭决策评估
- 优先级：P0
- 任务类型：全新隔离独立风险关闭决策评估
- 是否为受控能力包：No；风险关闭必须保持独立任务。
- 唯一风险边界：只判断 R-0051 是否可在当前固定 P3-097 candidate、单进程、离线、task-local、固定非敏感夹具范围内建议有限关闭。
- 建议篇幅：1500–2500 字。
- P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 新建隔离独立评审会话。
- 推荐理由：需本地复算多层 Manifest、复跑固定 runner，并跨 P3-094 至 P3-098 形成高风险证据裁决；必须与工程和既有验收上下文隔离。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 模型选择理由：P0 风险关闭需要高保真跨文件证据链、失败语义和范围／重开条件判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围，尤其是提出关闭建议、hash/Evidence 冲突、P0/P1/P2、Unknown 或 Not Implemented 判断。
- 必须升级条件：当前配置无法形成可复核结论时停止并回报 PM；不得静默换模或扩大范围。
- 后备模型：None。
- 是否需要后续独立评审：No；本任务本身是全新隔离独立风险判断。真正关闭仍须 PM 验收和用户最终确认。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA / Evidence Reviewer。
- 协审角色：技术架构负责人、数据／领域模型负责人、AI 信任与安全负责人。
- 必须通过关卡：Gate 2、Gate 3、Gate 4；不涉及 Gate 5 或阶段切换。
- 状态：Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery。
- 验收治理文件：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-099-v1`
- ABF SHA-256：`e318ba97fcacf16646e7545da7bb16ab3eadda7cc32a238643bf030cc95213ca`
- ABF 状态：Frozen
- 本任务正式 Rework 上限／当前次数：2／0

## 执行授权与会话路由

- 执行授权方式：用户将本任务卡完整路径投递至符合隔离条件的新 Codex 会话即启动本评估；仅在 PM 主会话提及路径不构成执行。
- 投递前额外用户确认：本任务创建已由用户明确要求；专项评估不直接关闭风险。真正关闭 R-0051 必须在 PM 验收后取得用户再次明确确认。
- 必须新建会话：Yes。
- 推荐会话类型：Codex 独立评审。
- 独立性硬条件：不得复用或继承 P3-094/096/097 工程会话、P3-095/098 独立评审会话、P3-097/098 PM 验收上下文；不得由参与上述工作的 Agent 会话执行。
- 授权证据：首份报告记录收到的绝对任务卡路径、新会话类型、实际模型／推理强度及精确接收时间。
- 任务完成后建议保留会话：Yes，作为风险决策审计记录；不得继续执行后续任务。

## 背景与唯一目标

P3-097 已获 PM Pass 并由用户采纳；P3-098 的全新隔离独立复评已经 PM 验证并由用户在 D-0410 采纳。R-0051 仍为 P0/Open，因为独立技术 Pass 不自动等于风险关闭。

本任务只回答：当前固定证据是否足以建议在严格有限范围内关闭 R-0051；若不足，应准确给出 `Keep Open` 或 `Blocked` 及证据原因。专项会话不得自行修改风险状态。

## 启动前验收依据冻结

- 在任何评估、hash 或复跑动作前，完整读取并复算 `ABF-P3-099-v1`。
- ABF 只冻结本轮裁决依据，不冻结产品需求或资产。
- 若 ABF、固定输入或独立性存在歧义，立即停止并回报 PM；不得自行修改或解释 ABF。
- 启动后新增检查必须映射到既有 L1/L2；需要改变输入、风险边界、关闭范围或权限时，本任务必须停止并触发新任务。

## 最小启动包与定向补读

必须完整读取：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`

高风险定向规则补读：

- `lifeos/PM_OPERATING_MODEL.md` 中“会话路由”“用户确认降频规则”“独立评审规则”“两层验收治理”“风险管理规则”相关章节；理由：风险关闭、独立性和用户最终决定边界。
- `lifeos/ROLE_MATRIX.md` 中 PM、Codex、独立评审、技术架构、数据／领域、AI 信任安全职责与任务分派表；理由：专项会话不得代替 PM 或用户关闭风险。
- `lifeos/STAGE_GATES.md` 中“独立评审要求”及 Gate 2、Gate 3、Gate 4；理由：核验数据来源、关闭态权限与技术 Evidence。

直接输入材料：

- `lifeos/RISK_LOG.md` 中 R-0051。
- `lifeos/DECISION_LOG.md` 中 D-0379 至 D-0410；仅定向读取，不全文读取其他历史。
- `lifeos/reviews/LIFEOS-P3-094_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-095_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-096_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`
- `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md`
- `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`
- `lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-097_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md`
- `lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md`
- `lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- `lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-098/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-098/evidence/results.json`
- `lifeos/reviews/LIFEOS-P3-098/evidence/source_history_hashes.json`
- `lifeos/reviews/LIFEOS-P3-098_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md`

仅在 Manifest 或结论冲突时定向打开其引用的具体 Evidence；不要全文重读无关历史。

## 固定根资产

专项会话必须在任何复跑前后复算以下 13 项：

| 路径 | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md` | `3355c7f3e744abfd3be392902217f8abfa02bb783a492d87e88d8a63ddb2a09f` |
| `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md` | `0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048` |
| `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md` | `a214e681ebf9449af9097edde42cd04b02dc83be2a09eec472e1a3b67c386ee1` |
| `lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md` | `63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311` |
| `lifeos/reviews/LIFEOS-P3-097_pm_review.md` | `057cbf047f412c38cc606ef033604a9e7591de83272ad2523ab0e02d86a58fee` |
| `lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md` | `90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183` |
| `lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md` | `89909b6ebea2cf669da3d7934976d08417b2fbb3097265ff7cde2320e734931e` |
| `lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review_acceptance_basis_freeze.md` | `249239ef03a84576d7cec01bd0c9eb0a21bccf032b032348a1665e7f8ca36fff` |
| `lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md` | `6c87b447b5f295bcaf257d8403a4deff58b6ef63d899ba04b675f78ff6136175` |
| `lifeos/reviews/LIFEOS-P3-098/independent_review.md` | `5a9d1681dbe0a6c08e487581b1efb0e779e0ec720992abfe390df2097f1ee28a` |
| `lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md` | `4f74f685d2ba5857c7fb9a469ae3397ddf06349bd9f9a34193b933773dfb6958` |
| `lifeos/reviews/LIFEOS-P3-098_pm_review.md` | `232c144f103d877d35d86572a13efac132773528345e9e81b9725b37927cd668` |
| `lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md` | `4ddf1158c63bbeecb0b2dd83fea44d19aa24d52b4bd2c33e25df966ba412c266` |

## 必须完成的工作

1. 建立任务专属 session、input hash、Manifest、风险覆盖和决策矩阵 Evidence；所有输入 before/after 只读一致。
2. 递归复算 P3-097 Engineering Manifest 16/16、P3-097 PM Manifest 23/23、P3-098 Independent Manifest 14/14、P3-098 PM Manifest 18/18。
3. 在全新 `/private/tmp/lifeos-p3-099-*` 固定非敏感目录复跑固定 P3-098 独立 runner，要求 45/45 PASS、45 个唯一 test/fixture/execution ID、退出 0、计数全零。
4. 把 R-0051 从 P3-094/095/096 暴露的每类事实逐项映射到 P3-097/098 当前 Evidence，不得只写“已有测试覆盖”。
5. 核对 task-local 路径、链接链、文件类型、页面生命周期、Schema/source/audit、不可逆完成点、失败回执、sidecar/staging 和禁止能力关闭态。
6. 输出严格三分结论：`Recommend Limited Closure`、`Keep Open` 或 `Blocked`。若建议关闭，必须写明精确关闭范围、所有非范围和可执行重开条件。
7. 报告 P0/P1/P2/Unknown/Not Implemented 数量；区分“风险基础中的发现”和“P3-099 自身交付质量缺口”。
8. 精确清理本任务创建的临时目录；不得覆盖 P3-097/P3-098 或历史 Evidence。

## 交付物与 Evidence

- 交付物：`lifeos/deliverables/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-099/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-099/evidence/`
- Evidence 至少包含：`session_start.json`、`runner_source.py`、`decision_matrix.json`、`input_hashes.json`、`manifest_results.json`、`risk_coverage_matrix.json`、`risk_decision.json`、`static_scope_scan.json`、`temporary_residue.json`、复跑输出／日志、`rerun.md` 和非自指 `MANIFEST.md`。
- 会话回复：严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只给摘要、结论、计数、交付物／Review／Evidence 路径和需 PM 决策事项。

## 结论与停止规则

- `Recommend Limited Closure`：仅是 PM／用户决策输入，不改变 R-0051。
- `Keep Open`：发现实质风险或关闭门未满足；这是诚实完成任务，不因结论本身记为 Rework。
- `Blocked`：必要输入、独立性或安全可运行环境不可得。
- P3-099 自身若违反 Frozen ABF、Evidence 不完整或结论与证据不一致，才进入同任务 Rework；最多两轮。
- 发现需要工程修改、新能力、新输入基线、真实数据／路径、并发／崩溃、架构、Schema/API、风险边界、冻结、基线或阶段变化时，立即停止；不得塞入本任务。

## 禁止事项

- 不修改任何工程代码、测试、runner 或 P3-094 至 P3-098 资产。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`FREEZE_STATUS.md` 或其他 PM 账本。
- 不关闭／重开 R-0051，不关闭 R-0040，不冻结资产，不恢复工程基线，不进入 Stage 4。
- 不访问真实个人数据、既有个人数据库、真实路径、网络、云、第三方、凭据或外部目标。
- 不自行创建、分派或执行后续任务。

## 本地预检

本任务属于 P0 风险关闭最终判断，可跳过局域网本地模型预检，但必须在交付物和 Review 中注明：本地模型不得决定风险关闭结论；已由确定性 hash、Manifest、隔离复跑和人工证据裁决替代。若使用本地预检，其结果仅可作格式／覆盖辅助，不得作为关闭依据。
