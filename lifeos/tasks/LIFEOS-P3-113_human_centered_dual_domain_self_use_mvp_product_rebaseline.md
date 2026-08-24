# LIFEOS-P3-113｜人本双领域自用 MVP 产品重新基线与冻结资产影响收口

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只读分析项目工作区中的产品、治理、Review 与脱敏 Evidence 摘要，只写 P3-113 自身交付物和 Evidence。任务不访问真实健康数据、真实敏感工作数据、真实 DB／用户路径／外部文件、网络、云、第三方、凭据或外部目标，不运行候选应用，不修改工程代码，不关闭或重开风险，不冻结资产，不进入 Stage 4。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-113`
- 任务名称：人本双领域自用 MVP 产品重新基线与冻结资产影响收口
- 优先级：P0
- 类型：产品定义／关键资产重新基线候选；非工程能力包；不适用 P3 Engineering Fast Lane。
- 唯一结果：形成一个可被独立评审的人本双领域自用 MVP 产品重新基线候选，明确 P3-111 能力边界、受影响冻结资产、产品语义、首页／主动提问／建议／反馈合同、非范围与后续路线。
- 推荐 Agent：Codex 产品定义专项会话。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 选择理由：任务同时影响产品定位适用范围、V1 场景／范围、领域语义、首页合同和高风险健康建议边界，需要跨资产深度一致性判断。
- 允许降级模型：`None`。
- 禁止降级条件：本任务全部范围均属于产品中心、V1 和关键冻结候选变化，不允许降级。
- 必须升级条件：N/A；首选已为规定范围内高质量配置。
- 后备模型：`gpt-5.5` / `xhigh`，仅首选不可用且用户／PM明确同意后使用；不得静默切换。
- 是否需要后续独立评审：Yes；必须由全新隔离会话执行 P3-114，且在其 Pass、PM 验收和用户确认前不得形成新 Frozen 基线。
- 是否允许修改工程：No。
- 是否允许修改项目账本：No；仅 PM 主会话维护。
- 主责：产品架构负责人。
- 协审：数据／领域模型、AI 信任与安全、体验设计、技术架构、用户研究。
- 必须通过：Gate 1、Gate 2、Gate 3；Gate 4 只验证可实现性与不提前冻结；Gate 5 只形成验证假设，不得宣称价值已证实。
- 状态：Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery。
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-113-v1`
- ABF SHA-256：`a64c87840b4526aab816a3186b3e63a43f33afcad183a4b4cfec2531f22b7d6d`
- 正式 Rework：0/2。

## 会话、授权与隔离

- 必须新建产品定义专项会话；不得复用 P3-111 工程、P3-112 独立评审或当前 PM 主会话，避免把旧 Project 中心、工程实现或 PM 结论当成新产品定义的自证。
- 用户将本任务卡绝对路径投递至符合条件的新会话，即授权本任务卡范围内的只读分析和 P3-113 自身文件写入，无需重复授权。
- 首份会话报告必须记录任务卡路径、会话类型、接收时间、ABF hash、实际模型与推理强度。
- 投递前仍需单独确认的例外：真实个人／健康／敏感工作数据、真实 DB／用户路径／外部文件、真实模型、网络／云／第三方、连接器、Tauri/IPC 新能力、同步、多设备、L3、外部用户、风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、Stage 4。当前均未授权。

## 最小启动包与定向补读

完整读取：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡与 `ABF-P3-113-v1`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/PROJECT_CONTEXT.md`（本任务涉及产品定位、V1 范围和领域语义变化）

高风险定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：会话隔离、用户确认、模型路由、关键冻结、阶段状态、两层验收章节。
- `lifeos/ROLE_MATRIX.md`：产品、数据／领域、AI 信任、体验、技术、用户研究职责。
- `lifeos/STAGE_GATES.md`：独立评审、Gate 1–5、Stage 3→4。
- `lifeos/FREEZE_STATUS.md`：核心资产看板和当前阶段判断。
- `lifeos/TASK_REGISTRY.md`：P3-101 至 P3-113。
- `lifeos/DECISION_LOG.md`：D-0414 至 D-0457。
- `lifeos/RISK_LOG.md`：R-0001～R-0018、R-0040、R-0051、R-0052。

直接输入：

- `lifeos/reviews/LIFEOS-P3-112_post_adoption_human_centered_product_rebaseline_activation.md`
- `lifeos/reviews/LIFEOS-P3-111_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-112_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`

如路径不存在或账本冲突，停止并形成 Blocked 证据；不得自行替换输入。

## 必须工作

1. 逐条执行 ABF-M-001 至 M-012，并生成独立结构化 Evidence。
2. 明确 P3-111“证明／未证明／可复用／仅历史参考”的边界，不外推产品价值。
3. 对产品定位、目标用户、第一场景、价值排序、V1 范围、领域模型、首页 PRD／原型、IA、自用 MVP 路线和技术／信任基础逐项分类：继续有效、仅工作领域有效、需重新打开、被候选替代、保留输入。
4. 输出人本双领域 MVP 的一句话定义、用户结果、七段闭环、Must／Should／Not Now 和完成定义。
5. 定义“人／人生领域／目标／状态／约束／偏好／记忆”的产品语义及其与现有对象的最小映射；不得把语义误写成数据库表、API 或页面模块冻结。
6. 冻结候选合同内容：首页、主动提问、建议依据、用户反馈、记忆确认／纠正／失效／删除、安全降级与健康边界。
7. 设计一个固定非敏感跨领域验收场景，覆盖工作负荷、睡眠、疲劳、膝盖约束、可用时间、信息缺失、主动补问、保守建议、反馈和关闭重开；不得包含医疗诊断。
8. 给出 P3-114 至受控 N=1 Pilot 的单线任务路线、依赖、隔离、Evidence 和额外授权触发器，不创建后续任务。
9. 逐项说明 Gate 1–5；Gate 5 只能形成可证伪假设和未来验证方法。
10. 核对历史输入只读、禁止能力关闭、临时残留为零，并报告 P0/P1/P2/Unknown/Not Implemented。

## 交付物与 Evidence

- 交付物：`lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-113/evidence/`
- Evidence 至少包含：`session_start.json`、`ledger_reconciliation.json`、`p3_111_boundary.json`、`frozen_asset_impact_matrix.json`、`product_definition_matrix.json`、`memory_semantics_matrix.json`、`home_question_advice_feedback_contract.json`、`cross_domain_scenario.json`、`safety_degradation_matrix.json`、`route_and_authorization_matrix.json`、`input_integrity.json`、`temporary_residue.json`、`rerun.md`、非自指 `MANIFEST.md`。
- 每个结论必须区分事实、用户方向、候选定义、推断和待独立评审项。
- 会话回复严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出结论、计数、路径和需 PM 确认事项。

## 验收与停止

- Pass 只表示 P3-113 候选完整、可复核，可进入 P3-114；不表示新产品资产 Frozen。
- 不得修改 P3-111/P3-112 或任何历史任务、工程、Review、Evidence、Manifest、风险、冻结和阶段账本。
- 不得运行应用、数据库、模型、网络或外部来源；只允许文本读取、hash／Manifest 核对和 task-local 结构化 Evidence。
- 临时文件仅允许 `/private/tmp/lifeos-p3-113-product-rebaseline-v1`，使用固定非敏感元数据，结束时精确清理。
- 发现账本冲突、必要输入不存在、ABF hash 不匹配或实际模型不符合路由，停止并报告 Blocked。
- 本任务涉及产品定位、V1、领域语义、关键冻结适用性和健康建议边界，可跳过本地模型预检，但交付物必须注明理由。
