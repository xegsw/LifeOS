# LIFEOS-P3-100｜R-0051 风险关闭决策评估后继

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅对任务卡固定的本地源码、Review、Evidence、Manifest 和固定非敏感 task-local 夹具进行防御性只读风险评估；不访问真实个人文件、既有个人数据库、网络、云、第三方系统、凭据或外部目标，不授权未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“反例、旁路、删除、失败注入”等术语仅指本地固定非敏感夹具。超出范围立即停止并回报 PM。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-100`
- 任务名称：R-0051 风险关闭决策评估后继
- 优先级：P0
- 类型：全新隔离独立风险关闭决策评估；非受控能力包；不适用 P3 Fast Lane。
- 唯一结果：输出 `Recommend Limited Closure`、`Keep Open` 或 `Blocked`，不直接修改风险状态。
- 推荐 Agent：Codex 新建隔离独立评审会话。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 理由：P0 风险关闭需跨文件 hash、Manifest、隔离复跑和严格范围裁决。
- 允许降级：None；后备模型：None。
- 禁止降级：本任务全部范围；若界面明确显示配置不符，停止回报 PM。
- 配置可观察性：界面不暴露精确内部标签时诚实记录 `not exposed`，不构成 Blocked；不得猜测或虚构。
- 是否需后续独立评审：No，本任务自身即独立风险判断；真正关闭仍须 PM 验收与用户确认。
- 工程／账本修改：均不允许。
- 主责：独立 QA / Evidence Reviewer；协审：技术架构、数据／领域、AI 信任与安全。
- 关卡：Gate 2、Gate 3、Gate 4。
- 状态：Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery。
- ABF：`lifeos/tasks/LIFEOS-P3-100_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-100-v1`
- ABF SHA-256：`a0049da75feca4b0f9cc9ac21c15c94719eedb28b3d095ee47aa47eefed48ce6`
- Rework：0/2。

## 会话、授权与独立性

- 必须新建会话，不得复用 P3-094 至 P3-099 的工程、独立评审或 PM 验收会话。
- 用户把本任务卡绝对路径投递至符合条件的新会话即授权本任务只读评估；仅创建任务卡不执行。
- 首份 Evidence 必须记录任务卡路径、会话类型、精确接收时间和界面实际可观察的运行配置。
- 专项会话无权关闭 R-0051、冻结资产、恢复基线、进入 Stage 4 或创建后续任务。

## P3-099 治理修正

- P3-099 已因 ABF 正文冻结时间晚于会话启动、并把不可观察模型内部标签设为硬门而 Blocked。
- 本任务使用已发生的真实冻结完成时间；新会话只需证明其接收时间更晚。
- 模型路由继续由 PM 指定，但不再要求专项会话证明接口未暴露的内部标签；只有明确可见冲突才阻断。
- P3-099 全部资产只读，不原地更改其 ABF 或历史结论。

## 最小启动包与高风险补读

完整读取：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡与 `ABF-P3-100-v1`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

定向补读：

- `lifeos/PM_OPERATING_MODEL.md` 的会话路由、用户确认、独立评审、两层验收治理和风险管理章节。
- `lifeos/ROLE_MATRIX.md` 的 PM／Codex／独立评审及技术架构、数据／领域、AI 信任安全职责。
- `lifeos/STAGE_GATES.md` 的独立评审要求及 Gate 2、Gate 3、Gate 4。
- `lifeos/RISK_LOG.md` 中 R-0051；`lifeos/DECISION_LOG.md` 中 D-0379 至 D-0412。

直接输入：P3-099 任务卡列出的 P3-094 至 P3-098 直接材料，以及：

- `lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md`
- `lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md`
- `lifeos/deliverables/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md`
- `lifeos/reviews/LIFEOS-P3-099/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-099/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-099_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-099/pm_evidence/initial/MANIFEST.md`

只在 Manifest 冲突时定向打开引用的具体 Evidence；不得全文重读无关历史。

## 固定 P3-099 历史根资产

| 路径 | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md` | `ca418978b4879492537bd0441fa0ac92a23c0721432ce1a7e3ff101922b63085` |
| `lifeos/tasks/LIFEOS-P3-099_r0051_risk_closure_decision_assessment_acceptance_basis_freeze.md` | `e318ba97fcacf16646e7545da7bb16ab3eadda7cc32a238643bf030cc95213ca` |
| `lifeos/deliverables/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md` | `28a56fcdbc500dedf089ead4d0b0660fd5951d60a8eaf65cdb0a7b18f92b065d` |
| `lifeos/reviews/LIFEOS-P3-099/independent_review.md` | `03a93085d883d1e34045ffad468652c40e7b266f9a49b4a775f83f34e4897f11` |
| `lifeos/reviews/LIFEOS-P3-099/evidence/MANIFEST.md` | `ee0153534afc0c157fa6d3ed78e83914dc64df21b1821353795344cd0d5d515f` |
| `lifeos/reviews/LIFEOS-P3-099_pm_review.md` | `1dc23031615eac02262ae29de12c890f569e70ca48afd3ab4deaf9d32e5387b6` |
| `lifeos/reviews/LIFEOS-P3-099/pm_evidence/initial/MANIFEST.md` | `cc9014b1c2a33bf2f3a0bdf219f2d0ee9b51447d9c5ffcdfebe96bc57e47dcfb` |

另须逐项复算 P3-099 任务卡中 13 个 P3-097/P3-098 技术根资产；总计 20/20。

## 必须工作与 Evidence

1. 执行 ABF-M-001 至 M-012，每行独立 action/test/execution ID 和 Evidence，不得批量推定。
2. 复算 20 个固定根资产、四层 Manifest 16/16、23/23、14/14、18/18，以及 P3-098 45 个唯一 ID。
3. 在全新 `/private/tmp/lifeos-p3-100-*` 固定非敏感目录复跑 P3-098 独立 runner，要求 45/45 PASS、退出 0、计数全零。
4. 把 P3-094/095/096 每类失败逐项映射到当前 P3-097/098 Evidence。
5. 核对完成点、失败回执、页面／SQLite／staging／sidecar、路径链接／文件类型、Schema/source/audit 与禁止能力关闭态。
6. 输出三分风险建议、风险基础计数和任务自身交付质量计数；如建议关闭，列明有限范围、非范围和重开条件。
7. before/after hash 一致并精确清理本任务临时目录。

交付路径：

- `lifeos/deliverables/LIFEOS-P3-100_r0051_risk_closure_decision_assessment.md`
- `lifeos/reviews/LIFEOS-P3-100/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-100/evidence/`

Evidence 至少包含：`session_start.json`、`runner_source.py`、`decision_matrix.json`、`input_hashes.json`、`manifest_results.json`、`risk_coverage_matrix.json`、`risk_decision.json`、`static_scope_scan.json`、`temporary_residue.json`、复跑输出／日志、`rerun.md` 和非自指 `MANIFEST.md`。

## 结论与限制

- `Recommend Limited Closure` 只是 PM／用户输入，不改变风险状态。
- `Keep Open` 是有效任务结果，不因风险未关闭自动记 Rework。
- `Blocked` 仅用于必要输入、授权、独立性或安全本地环境不可得。
- 不修改任何工程、历史 Evidence 或 PM 账本；不关闭／重开任何风险，不冻结、不恢复基线、不进入 Stage 4。
- 不使用真实个人数据、既有个人 DB、网络、云、第三方、凭据或外部目标。
- 本任务为 P0 风险关闭最终判断，可跳过本地模型预检，但须注明理由；本地模型不得决定结论。
- 会话回复严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只报告结论、计数、路径与 PM 决策请求。
