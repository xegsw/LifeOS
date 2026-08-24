# LIFEOS-P3-058｜R-0043 风险关闭决策评估

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限本地代码、Review、Evidence 与合成测试数据的只读核验，用于防御性风险决策；不涉及外部目标、真实数据或凭据、未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“旁路、反例、删除后复活”等术语仅指本地合成负向验证，不授权扩大范围。既有用户确认、独立性与停止条件继续有效。

## 任务信息与路由

- 任务 ID：LIFEOS-P3-058；优先级：P1；类型：独立风险关闭决策评估；建议篇幅：1000-2000 字；P3 快车道：No。
- 推荐 Agent：Codex 新建隔离会话；理由：R-0043 关闭涉及历史失败、整改、独立复评、当前候选 hash 与严格适用范围的跨证据裁决。
- 推荐模型 / 推理强度：`gpt-5.6-terra` + `xhigh`。
- 模型选择理由：风险关闭需要高保真跨文件证据链和边界判断。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：任何 hash/Evidence 冲突、P0/P1/明确 P2 bypass、未知/未实现，或需要提出关闭建议时。
- 必须升级条件：当前配置无法形成可复核结论时，停止并回报 PM；仅在 PM 新任务卡明确授权时可升级为 `gpt-5.6-terra` + `max`。
- 是否需要后续独立评审：No；本任务本身为独立风险决策。实际关闭仍须 PM 和用户确认。
- 工程与账本：全部只读；仅可写 P3-058 自身 deliverable、review、evidence 和 local precheck。
- 主责角色：独立 QA / Evidence Reviewer；协审：技术架构、数据/领域模型、AI 信任与安全；关卡：Gate 2、Gate 3、Gate 4。
- 会话：必须新建、不得复用 P3-038/P3-039 或其执行/评审会话；新会话需完整重读 `AGENTS.md`、基础规则、任务卡、模板、P3-037/P3-038/P3-039 直接材料、R-0043、D-0208 至 D-0214 与当前 P3-031 SQL/合同入口。
- 实际派发会话：新隔离 Codex 会话 `01a0226d-b147-7da0-b507-0504659e242e`（local，`gpt-5.6-terra` + `xhigh`）。
- 状态：In Progress。

## 目标、范围与限制

1. 建立任务专属输入清单与 SHA-256、before/after 只读保留核验，并证明新会话与 P3-038/P3-039 隔离。
2. 独立核查 P3-037 的 R-0043 失败、P3-038 窄整改、P3-039 隔离反例/PM Evidence，以及当前候选 SQL 与 P3-031 合同入口；不得用叙述性交付物替代结构化 Evidence。
3. 只形成“建议关闭 / 保持 Open / Blocked”及严格范围、非范围和重开条件。P3-039 后续任务造成的 current SQL 演进必须显式处理，不能假定旧结论自动延续。
4. 交付 `lifeos/deliverables/LIFEOS-P3-058_r0043_risk_closure_decision_assessment.md`、`lifeos/reviews/LIFEOS-P3-058/independent_review.md`、`lifeos/reviews/LIFEOS-P3-058/evidence/MANIFEST.md` 与本地预检记录。
5. 不修改工程或历史资产；不关闭 R-0043，不影响其他风险，不冻结 Schema/API 或工程基线，不启用真实能力，不进入下一阶段，不创建后续任务。

任何 P0/P1、明确合同 P2、Unknown、Not Implemented、hash/证据冲突或独立性不足，必须结论 Rework 或 Blocked。完成后按 `SESSION_REPORT_TEMPLATE.md` 简短回报；Pass 仅是 PM/用户风险决定输入。
