# LIFEOS-P3-127｜P3-126 清洁启动候选全新隔离独立复评

## 任务信息

- 任务 ID：`LIFEOS-P3-127`
- 优先级：P0
- 类型：全新隔离独立复评；不是 P3-126 原地 Rework，不得修改 P3-126。
- 唯一结果：在全新 review/temp 根与全新合成 DB 中，独立复核 P3-126 已获 PM Pass 的 clean-start candidate、三 IPC actual-Tauri 生命周期、失败关闭、历史保全、Evidence lineage 与精确清理，并给出 Pass、Rework 或 Blocked。
- 推荐 Agent：Codex 全新独立评审会话；不得复用 P3-125/P3-126 工程执行会话或 PM 主会话。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 选择理由：P0 actual-Tauri、路径失败关闭、DB 生命周期、Evidence lineage 与独立 mutation 需要高强度本地复核。
- 允许降级模型：`gpt-5.5 + xhigh`，仅在推荐配置不可用且 PM 明确确认后允许。
- 禁止降级条件：不得使用 `gpt-5.6-luna`、`gpt-5.4` 或项目白名单外模型完成最终 P0 裁决。
- 必须升级条件：备用配置无法完整复核 native App、lineage、mutation 或 cleanup 时停止并回报 PM。
- 后备模型：`gpt-5.5`
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/1 / Not Frozen`
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md`（`ABF-P3-127-v1`）
- 生效决策：D-0515。

## 当前授权状态

- 用户已采纳 P3-126 PM Pass、授权创建本任务，并于 2026-08-26 明确确认精确 synthetic-only actual-Tauri/IPC 边界。
- 允许根仅为：`lifeos/reviews/LIFEOS-P3-127/`、`/private/tmp/lifeos-p3-127-independent-review-v1`；PM 冻结时确认两根均不存在。
- 允许数据：全新固定非敏感合成 DB 与任务内固定短文本。
- 允许入口：仅构建时 `LIFEOS_RUNTIME_ROOT` 与既有 `capture_record`、`get_today`、`runtime_status` 三项 IPC，offline actual Tauri。
- 严格只读：P3-126 task、Frozen ABF、source allowlist、candidate、Evidence、delivery、PM Review 与 PM Evidence，以及所有上游历史资产。
- 额外禁止：对旧 P3-122 Runtime root 进行任何 access、stat、hash、create 或 cleanup；禁止 Pilot、真实 DB／路径／文本、网络、产品模型、新 IPC/capability、clear/export/权限/恢复。
- 授权与冻结证据：`lifeos/tasks/LIFEOS-P3-127_authorization/user_confirmation.md`、`preflight.md`、`FREEZE_MANIFEST.md`。

## 独立性与 Evidence 合同

1. 全新评审会话自写 task-local runner；禁止 import、复制或调用 P3-126 runner。
2. 在 candidate read、review/temp root 创建、DB 或 App 启动前，先核对实际 model/effort、Frozen hashes、物理 allowlist 语义和授权。
3. 固定输入或授权冲突必须 action-before stop；不得以历史 PM Pass 替代独立复核。
4. 每个矩阵行记录“行号→冻结动作→测试 ID→实际 Evidence→hash→结论”；汇总结果不得批量替代逐行证据。
5. actual-Tauri 动作必须绑定 UI/截图、IPC 返回、DB/process/log 与 attestation；静态扫描或 unit test 不替代动态证据。
6. 精确清理唯一 temp root；保留 P3-127 review Evidence；不得覆盖或更改 P3-126 与上游历史资产。

## 最小启动包与定向补读

必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、Frozen ABF、`lifeos/ACCEPTANCE_GOVERNANCE.md`、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、UI Dynamic Evidence 模板；P3-126 task/ABF/allowlist/delivery、两份 PM Review、PM Evidence closure Manifest 与 Engineering Final Manifest。

高风险定向补读：`PM_OPERATING_MODEL.md` 的独立评审/Tauri/IPC/P0/Evidence 章节；`ROLE_MATRIX.md` 的独立评审/架构/QA；`STAGE_GATES.md` 的 Stage 3→4 区分；`TASK_REGISTRY.md` P3-125～P3-127；`DECISION_LOG.md` D-0508～最新；`RISK_LOG.md` R-0040/R-0051/R-0052。

## 交付

- 独立 Review：`lifeos/reviews/LIFEOS-P3-127/independent_review.md`
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-127/evidence/`
- 专项交付摘要：`lifeos/deliverables/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review.md`
- 结论仅限 Pass/Rework/Blocked；必须报告 P0/P1/P2/Unknown/Not Implemented。
- 不修改账本、不冻结资产、不关闭风险、不创建后续任务、不进入 Stage 4。

## 启动条件

启动前精确边界已由用户确认，PM 已复算 75 个物理 candidate 行及固定 hashes、确认两根不存在并冻结 `ABF-P3-127-v1`。只有本最终任务卡的绝对路径投递到全新隔离 Codex 独立评审会话才构成执行授权；投递前不得创建 review/temp root、DB 或 App。
