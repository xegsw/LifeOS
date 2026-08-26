# LIFEOS-P3-123｜P3-122 组合候选全新隔离独立复评

## 任务信息

- 任务 ID：`LIFEOS-P3-123`
- 优先级：P0
- 类型：全新隔离独立复评；不是工程实现，不得修改 P3-122。
- 唯一结果：独立验证 P3-122 的 P3-116 视觉直接继承、三档 native/WebView/DOM 视口、三 IPC 生命周期、失败关闭、禁止能力与 Evidence lineage，给出 Pass/Rework/Blocked。
- 推荐 Agent：Codex，全新会话；不得复用 P3-122 工程执行或当前 PM 会话。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 理由：P0 原生 Tauri geometry、视觉 lineage 与独立 mutation 需要高强度推理和本地工具能力。
- 允许降级：`gpt-5.5 + xhigh`；仅在完整读取并保持 ABF 时允许。
- 禁止降级：不得使用 `gpt-5.6-luna` 或 `gpt-5.4` 完成最终 P0 独立裁决；不得使用项目白名单外模型。
- 必须升级：降级配置无法独立复核 native geometry、visual source 或 Manifest 时须停止并改用推荐配置。
- 后备模型：`gpt-5.5`
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/2 / Not Frozen`
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID／SHA-256：`ABF-P3-123-v1` / `7b5f67152c9c50187999d11900d2efc44efe79d2b87e2e33173be0a13dc2302b`
- 生效决策：`D-0495`
- 正式 Rework：0/2。

## 当前授权状态

- 用户已采纳 P3-122 PM Pass，并授权 PM 创建本任务与新 ABF。
- 用户已明确确认新的 Tauri/IPC 独立复评边界；授权 Manifest：`lifeos/reviews/LIFEOS-P3-122/pm_evidence/p3-123-authorization/MANIFEST.md`，SHA-256 `c8c804de0c596e2ca210a46a81618716a8b9589ec99b46d0ab0e75a3519f3b21`。
- 允许根：`lifeos/reviews/LIFEOS-P3-123/`、`/private/tmp/lifeos-p3-123-independent-review-v1`。两根在冻结时均不存在。
- 执行授权方式：用户将本最终任务卡绝对路径投递至全新隔离 Codex 评审会话即启动；仅在 PM 主会话查看路径不启动。

## 拟允许与禁止范围

- 允许：P3-123 自有独立 runner/Evidence/Review；固定 temp root；全新合成 DB；P3-122 final candidate/build、Engineering Evidence、PM Review 只读；仅三项 IPC；离线 actual Tauri App、native/renderer geometry、截图、SQLite、hash 和 disposable mutation。
- 禁止：修改 P3-122 或上游资产；导入、复制或调用 P3-122 runner；访问 Pilot、真实 DB／路径／文本；网络、产品模型、云、第三方、新 IPC/capability、clear/export/权限/恢复、系统设置、风险关闭、冻结或 Stage 4。
- 清理：只能精确清理唯一 P3-123 temp root；Review Evidence 保留。
- Frozen candidate allowlist：`lifeos/tasks/LIFEOS-P3-123_candidate_source_allowlist.md`，75/75，SHA-256 `a5b8bd56114fd1091996b2fb0094ebb7a7f5c9ee4f9e3ddbfbe11780f9e437b7`；candidate tree hash `ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742`。

## 独立性合同

1. 评审会话与 P3-122 工程执行及 PM 验收会话隔离。
2. 在任何执行前复算 Frozen ABF、P3-122 PM Review、PM acceptance Manifest 与 Engineering Final Manifest。
3. 自写独立 runner；禁止 import、复制、调用 P3-122 `tools/build_evidence.py` 或信任其汇总结论。
4. 可读取 P3-122 Evidence 作为被评审对象，但关键结论必须由独立 runner、全新 DB、actual App 动作和独立 mutation 产生。
5. 每个矩阵行必须记录行号、冻结动作、测试 ID、实际 Evidence、hash 与结论。

## 最小启动包与定向补读

必须读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 Frozen `ABF-P3-123-v1`
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. P3-122 task/ABF/delivery、PM Review、PM acceptance Manifest、Engineering Final Manifest 与双 source allowlist

高风险补读：`PM_OPERATING_MODEL.md` 的独立评审/Tauri/IPC/P0/Evidence 章节；`ROLE_MATRIX.md` 的独立评审/体验/架构/QA；`STAGE_GATES.md` 的关键原型独立评审与 Stage 3→4 区分；`TASK_REGISTRY.md` P3-122/P3-123；`DECISION_LOG.md` D-0490～D-0494；`RISK_LOG.md` R-0024/R-0025/R-0040/R-0051/R-0052。

## 交付

- 独立 Review：`lifeos/reviews/LIFEOS-P3-123/independent_review.md`
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-123/evidence/`
- 专项交付摘要：`lifeos/deliverables/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review.md`
- 结论仅限 Pass/Rework/Blocked；必须报告 P0/P1/P2/Unknown/Not Implemented。
- 不修改账本、不冻结资产、不关闭风险、不创建后续任务、不进入 Stage 4。

## 启动条件

用户已完成精确确认；PM 已生成候选 75/75 allowlist 与授权 Evidence、确认两根不存在并冻结 `ABF-P3-123-v1`。用户现在可将本任务卡绝对路径投递至全新隔离 Codex 独立评审会话；专项仍须先完成启动前质疑窗口，且不得越出 Frozen 边界。
