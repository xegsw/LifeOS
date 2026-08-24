# LIFEOS-P3-114｜P3-113 人本双领域产品重基线全新隔离独立评审

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。用户已采纳 P3-113 PM Pass，并授权创建本任务。本任务仅以只读方式评审项目工作区中的产品／治理文件和脱敏结构化 Evidence，只写 P3-114 自身交付物、Independent Review 与 Evidence，并只在 `/private/tmp/lifeos-p3-114-product-review-v1` 使用固定非敏感夹具。不访问真实个人／健康／工作数据、真实 DB／路径／外部文件、retained Pilot、网络、云、第三方、凭据或外部目标；不运行应用、数据库或模型，不修改工程、候选、账本、风险、冻结或阶段状态。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-114`
- 任务名称：P3-113 人本双领域产品重基线全新隔离独立评审
- 优先级：P0
- 任务类型：全新隔离、只读、产品／数据来源／AI 信任／健康安全／Evidence 独立评审；非工程能力包。
- 唯一结果：独立判断 P3-113 初次候选 + Rework 1 的组合产品候选是否满足 `ABF-P3-114-v1`，给出 Pass／Rework／Blocked 和逐项 Evidence。
- 是否为受控能力包：No。
- 建议篇幅：2000–4000 字；完整反例和日志写入 Evidence。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 全新独立产品评审会话。
- 推荐理由：需要在本地只读文件边界内完成独立反例设计、跨产品／数据／健康／冻结语义复核和 Manifest 可复核性；必须避免 P3-113 执行与 PM 自证循环。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 产品中心、健康安全、Source／反馈身份、关键冻结候选和独立 Evidence 判断需要高强度综合推理。
- 允许降级模型：None
- 禁止降级条件：本任务全部范围；不得降低独立性或健康／产品判断强度。
- 必须升级条件：N/A；首选已为规定范围内高质量配置。首选不可用则停止，不得静默换模。
- 后备模型：`gpt-5.5` / `xhigh`，仅首选不可用且用户／PM明确同意后使用。
- 是否需要后续独立评审：No；本任务自身即独立评审，仍需 PM 验收和用户采纳。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No；仅 PM 主会话维护。
- 主责角色：独立产品架构／数据来源／AI 信任与健康安全评审。
- 协审角色：领域模型、体验设计、用户研究、技术架构、Evidence QA。
- 必须通过：Gate 1、Gate 2、Gate 3；Gate 4 只审查条件可实现性与不提前冻结；Gate 5 只核对可证伪假设，不得判真实价值通过。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-114-v1`
- ABF SHA-256：`22d1b5f89ce608e72cdf42d3e08fe3adf11f57b10f23a64d2cf7b1273f27b96d`
- ABF 状态：Frozen
- 本任务正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0461`
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话即授权执行；仅创建本任务卡不启动执行。
- 投递授权的会话类型与隔离要求：必须是未参与 P3-113 产品定义、Rework、独立评审或 PM 验收的全新 Codex 独立评审会话；不得复用 P3-113 产品定义会话、当前 PM 主会话或任何自证上下文。
- 投递前额外用户确认：None；任务严格只读且无真实能力。任何真实数据／模型／外部来源、工程、原型、冻结、风险或阶段动作立即停止并回 PM。
- 授权证据记录：首份会话报告记录收到的任务卡绝对路径、会话类型、接收时间、实际模型／推理强度、ABF hash 与独立性声明。

## 独立性与强制读序

在读取 P3-113 初次／Rework 交付物正文、专项 Evidence JSON 或 PM Review 结论前，必须：

1. 只读 `AGENTS.md`、`CURRENT_STATUS.md`、本任务卡、`ABF-P3-114-v1`、验收治理和独立评审模板。
2. 核对全新会话、模型、授权、ABF hash 和唯一临时根不存在；若临时根已存在，Blocked，不删除。
3. 创建并封存 `lifeos/reviews/LIFEOS-P3-114/evidence/test_design.md`，写明独立问题、反例、严重级别和判定法；另写 `read_order.json` 记录 hash 与时间。
4. 设计至少覆盖：Project 重新夺回全局中心、Source 身份混合、过期／冲突／失权仍建议、问题未答、健康警示、接受与执行混淆、一次结果泛化偏好、撤销／关闭重开复活、历史 Frozen 静默改写、合成证据外推真实价值。

独立设计冻结后才能读取候选及其 verifier／Evidence。不得复制 P3-113 自检问题作为本任务独立主证据；可以在独立测试完成后只读交叉比较。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 `ABF-P3-114-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
7. `lifeos/PROJECT_CONTEXT.md`（涉及产品定位、V1、领域语义和关键冻结候选）

高风险定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：独立评审、会话隔离、关键冻结、健康／真实能力、两层验收与用户确认章节。
- `lifeos/ROLE_MATRIX.md`：产品、数据／领域、AI 信任、体验、技术、用户研究和独立评审职责。
- `lifeos/STAGE_GATES.md`：Gate 1–5 与 Stage 3→4；正式 Gate 名称不得改写。
- `lifeos/FREEZE_STATUS.md`：核心资产和当前阶段判断。
- `lifeos/TASK_REGISTRY.md`：P3-111 至 P3-114。
- `lifeos/DECISION_LOG.md`：D-0401、D-0457 至 D-0461。
- `lifeos/RISK_LOG.md`：R-0001～R-0018、R-0040、R-0051、R-0052。

独立设计冻结后读取的直接候选输入：

- P3-113 任务卡与 `ABF-P3-113-v1`
- `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline.md`
- `lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md`
- `lifeos/reviews/LIFEOS-P3-113/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/MANIFEST.md`
- P3-113 两轮 Manifest 列出的结构化 Evidence
- `lifeos/reviews/LIFEOS-P3-113_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-113/pm_evidence/initial/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-113/pm_evidence/rework-1/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-112_post_adoption_human_centered_product_rebaseline_activation.md`

历史适用性核对输入：

- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-111_pm_review.md`、`lifeos/reviews/LIFEOS-P3-112_pm_review.md`（只核对工程证明边界，不运行或访问 Pilot）

如路径不存在、hash 漂移、读序无法证明或账本冲突，停止并形成 Blocked Evidence；只在冲突处定向补读，不全文重读无关历史。

## 必须工作

1. 完整执行 ABF-M-001 至 M-013；每行独立 Evidence，不以 P3-113 或 PM 自报 Pass 推定。
2. 独立判断 Person 是否真正为一级主体，Project 是否只保留工作领域语境；攻击企业后台、项目管理器、医疗产品或全能 AI 漂移。
3. 独立复核历史 Frozen 资产影响：历史事实不删除、不解冻，新候选何时才可能替代全局基线。
4. 攻击七段闭环、至少两个 Source、Artifact／Derivation／Advice／Feedback 身份、长期记忆确认与时效。
5. 对首页／问题／建议／反馈合同执行缺失、冲突、过期、失权、未答、拒绝、忽略、延后、未执行、执行、结果、撤销和关闭重开反例。
6. 独立核对健康／健身仅为低风险非医疗辅助；警示信号必须停止并建议适当专业支持，不提供诊断／治疗／安全保证。
7. 复演固定非敏感跨领域场景，验证原建议、修改处置、实际执行、结果、当前理解和待确认长期记忆不混淆。
8. 逐问 Gate 1–5；Gate 4 只审查条件可行，Gate 5 只允许假设。不得把合成场景、P3-111 工程或本任务 Pass 外推为真实价值、冻结或 Stage 4。
9. 复算全部指定 Manifest／hash，核对 P3-113 初次与 Rework 历史保全、禁止能力关闭和精确临时清理。
10. 报告 P0/P1/P2/Unknown/Not Implemented；明确 Pass／Rework／Blocked，并区分事实、推断、建议和需 PM 决定事项。

## 允许修改与交付

仅允许写入：

- `lifeos/deliverables/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-114/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-114/evidence/`
- `/private/tmp/lifeos-p3-114-product-review-v1`（结束时精确清理）

Evidence 至少包含：`test_design.md`、`read_order.json`、`session_boundary.json`、`input_integrity.json`、`product_center_review.json`、`frozen_asset_impact_review.json`、`source_memory_counterexamples.json`、`home_advice_contract_review.json`、`feedback_lifecycle_counterexamples.json`、`health_safety_review.json`、`cross_domain_replay.json`、`gate_and_route_review.json`、`independent_counterexamples.json`、`results.json`、`temporary_residue.json`、`rerun.md`、非自指 `MANIFEST.md`。

完整交付物：`lifeos/deliverables/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review.md`

独立 Review：`lifeos/reviews/LIFEOS-P3-114/independent_review.md`

## 结论与退出

- 专项结论：Pass / Rework / Blocked；PM 最终裁决。
- Pass：I-01～I-12、M-001～M-013 全部通过；P0=0、P1=0、Unknown=0、Not Implemented=0；P2 已披露且不影响唯一结果；历史只读、禁止能力关闭、临时残留为零。
- 同任务 Rework：只允许 P3-114 自有 Review／Evidence／独立测试问题，ABF 和候选输入不变且未达两轮上限。
- 候选 P0/P1 或需改 P3-113：评审不得修改候选，交 PM 按治理流程判断同任务 Rework 或新任务。
- Blocked：独立性、模型、必要输入／hash、账本或唯一临时根空基线不成立；不得访问真实或外部目标解除。
- 即使 Pass，也不冻结新产品资产、不创建高保真原型任务、不关闭／重开 R-0040/R-0051/R-0052 或其他风险、不恢复工程基线、不进入 Stage 4。

## 本地预检与聊天回复

- 可跳过本地模型预检：本任务涉及产品中心、健康安全、数据来源、独立性和关键冻结候选的 P0 最终判断；Review 必须注明，预检不得决定结论。
- 聊天严格使用 `SESSION_REPORT_TEMPLATE.md`，只输出结论、Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、资产／风险、下一步、Review／Evidence 路径及需 PM 确认事项。
