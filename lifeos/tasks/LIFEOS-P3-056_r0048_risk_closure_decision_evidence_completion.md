# LIFEOS-P3-056｜R-0048 风险关闭决策 Evidence 补全

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限本地代码、Review、Evidence 和合成测试数据的只读核验，用于防御性风险决策证据收口；不涉及外部目标、真实数据/凭据、未授权访问、扫描、攻击、持久化、数据获取或安全控制规避。既有用户确认、独立性与停止条件继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-056
- 优先级：P1
- 类型：P3-055 Rework 的全新隔离 Evidence 补全风险决策评估
- 推荐 Agent / 模型：Codex 新建隔离会话，`gpt-5.6-terra` + `xhigh`
- 模型选择理由：需独立核验跨任务 Evidence、输入 hash、只读资产保留和风险关闭边界，避免把历史结论直接当作本任务证据。
- 允许降级模型：None
- 禁止降级条件：输入 Evidence 缺失、hash 不一致、只读资产变化、P0/P1/P2 合同冲突，或需要形成风险关闭建议时。
- 必须升级条件：若出现上述冲突且当前配置无法形成可复核结论，停止并回报 PM；仅在 PM 新任务卡明确授权时可升级为 `gpt-5.6-terra` + `max`。
- 后备模型：None
- 是否需要后续独立评审：不需要额外评审；本任务本身即为与 P3-055 隔离的独立风险决策补全。实际风险关闭仍须 PM 和用户确认。
- 实际派发会话：新隔离 Codex 会话 `01a02251-614d-7c00-ac79-62f1261e97c8`（local，`gpt-5.6-terra` + `xhigh`）。
- 工程与账本：严格只读；仅可写 P3-056 自身 deliverable、review、evidence 和 local precheck。
- 状态：In Progress

## 必须交付与判定

1. 新建任务证明、实际模型、完整输入清单、每项输入 SHA-256 与 before/after 只读保留核验。
2. 任务专属 `independent_review.md` 与 `evidence/MANIFEST.md`，并运行/记录本地预检或允许跳过原因。
3. 逐项引用并独立核对 P3-045 合同、P3-052 失败、P3-053 整改、P3-054 独立 Pass 与 PM Evidence；不得把 P3-055 草案直接视为证据替代品。
4. 仅形成“建议关闭 / 保持 Open / Blocked”判断，列出严格关闭范围、非范围、重开条件，特别排除真实 actor/确认、真实 DB、并发、恢复和真实能力。
5. 不关闭 R-0048、不影响 R-0049、不冻结资产、不恢复基线、不进入下一阶段。最终关闭仍需 PM 验收与用户明确授权。

## 任务输出

- 决策补全交付物：`lifeos/deliverables/LIFEOS-P3-056_r0048_risk_closure_decision_evidence_completion.md`
- 独立评审：`lifeos/reviews/LIFEOS-P3-056/independent_review.md`
- Evidence 清单：`lifeos/reviews/LIFEOS-P3-056/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/` 下由统一脚本生成的本任务报告；如超时或不可用，须在 Review 与 Manifest 中记录。
