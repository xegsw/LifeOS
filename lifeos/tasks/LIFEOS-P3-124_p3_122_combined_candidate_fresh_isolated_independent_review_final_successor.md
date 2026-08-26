# LIFEOS-P3-124｜P3-122 组合候选全新隔离独立复评最终后继

## 任务信息

- 任务 ID：`LIFEOS-P3-124`
- 优先级：P0
- 类型：全新隔离独立复评；P3-123 的后继，不是原地 Rework，不得修改 P3-122 或 P3-123。
- 唯一结果：以格式可直接解析的固定输入重新独立验证 P3-122 的视觉直接继承、三档 native/WebView/DOM 视口、三 IPC 生命周期、失败关闭、禁止能力与 Evidence lineage，并给出 Pass、Rework 或 Blocked。
- 推荐 Agent：Codex 全新会话；不得复用 P3-122 工程执行、P3-123 评审或 PM 会话。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 选择理由：P0 actual-Tauri geometry、视觉 lineage、Runtime 生命周期和独立 mutation 需要高强度本地复核。
- 允许降级模型：`gpt-5.5 + xhigh`，仅在完整读取并保持 ABF 时允许。
- 禁止降级条件：不得使用 `gpt-5.6-luna`、`gpt-5.4` 或项目白名单外模型完成最终 P0 裁决。
- 必须升级条件：降级配置无法复核 native geometry、visual lineage 或 Manifest 时停止并改用推荐配置。
- 后备模型：`gpt-5.5`
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/2 / Not Frozen`
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-124_p3_122_combined_candidate_fresh_isolated_independent_review_final_successor_acceptance_basis_freeze.md`（`ABF-P3-124-v1`）
- 生效决策：D-0499。

## 当前授权状态

- 用户已采纳 P3-123 `Blocked / Closed — Acceptance Not Met`，授权创建本任务，并于 2026-08-26 在 PM 主会话完成 P3-124 精确边界确认。
- 允许根仅为：`lifeos/reviews/LIFEOS-P3-124/`、`/private/tmp/lifeos-p3-124-independent-review-v1`；PM 冻结时确认两根均不存在。
- 允许数据：全新固定非敏感合成 DB 与最多两条任务内固定短文本。
- 允许接口：仅 `capture_record`、`get_today`、`runtime_status` 三项既有 IPC，offline actual Tauri。
- 严格只读：P3-116～P3-123 的 task、ABF、candidate、delivery、Review、Evidence、Manifest 与账本，特别包括 P3-122 candidate/Evidence/Review 和 P3-123 全部历史资产。
- 禁止：Pilot、真实 DB／路径／文本、网络、产品模型、云／第三方、新 IPC/capability、clear/export/权限/恢复、系统设置、风险关闭、冻结或 Stage 4。
- 授权证据：`lifeos/tasks/LIFEOS-P3-124_authorization/user_confirmation.md`、`preflight.md`、`MANIFEST.md`、`FREEZE_MANIFEST.md`。

## P3-123 缺陷收口

- 新候选清单：`lifeos/tasks/LIFEOS-P3-124_candidate_source_allowlist.md`。
- 格式合同：UTF-8、真实 LF 物理换行、75 个 candidate 数据行、每个文件一行；禁止用字面 backslash-n 编码多行。
- 模型路由属于会话执行约束：专项首报必须声明实际 model/effort，并附平台可见元数据（若平台提供）。平台不提供底层元数据时，不得仅因此把产品矩阵记为 Unknown；声明配置与任务卡不符则立即 Blocked。
- P3-123 的 task、ABF、allowlist、两份输出、Review 与 Evidence 全部只读保全。

## 独立性与 Evidence 合同

1. 全新评审会话自写 runner；禁止 import、复制或调用 P3-122/P3-123 runner。
2. 在创建任何执行根、DB 或 App 前，直接解析并复算 Draft/Frozen ABF、新 allowlist、P3-122 PM Review、PM acceptance/adoption Manifest、Engineering Final Manifest。
3. 先执行纯读取 preflight；只有所有固定输入、75 行、tree hash、根不存在和授权状态匹配后才可启动 actual Tauri。
4. 每个矩阵行记录行号、冻结动作、测试 ID、实际 Evidence、hash 与结论；不得用汇总结果批量替代。
5. 精确清理唯一 temp root；保留 P3-124 Review Evidence；不得覆盖任何历史 Evidence。

## 最小启动包与定向补读

必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、Frozen ABF、`lifeos/ACCEPTANCE_GOVERNANCE.md`、独立评审与 UI Dynamic Evidence 模板；P3-122 task/ABF/delivery/PM Review/PM Evidence/Engineering Final Manifest；P3-123 task/ABF/allowlist/两份输出/PM Review/PM Evidence。

高风险定向补读：`PM_OPERATING_MODEL.md` 的独立评审/Tauri/IPC/P0/Evidence 章节；`ROLE_MATRIX.md` 的独立评审/体验/架构/QA；`STAGE_GATES.md` 的关键原型独立评审与 Stage 3→4 区分；`TASK_REGISTRY.md` P3-122～P3-124；`DECISION_LOG.md` D-0490～最新；`RISK_LOG.md` R-0024/R-0025/R-0040/R-0051/R-0052。

## 交付

- 独立 Review：`lifeos/reviews/LIFEOS-P3-124/independent_review.md`
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-124/evidence/`
- 专项交付摘要：`lifeos/deliverables/LIFEOS-P3-124_p3_122_combined_candidate_fresh_isolated_independent_review_final_successor.md`
- 结论仅限 Pass/Rework/Blocked；必须报告 P0/P1/P2/Unknown/Not Implemented。
- 不修改账本、不冻结资产、不关闭风险、不创建后续任务、不进入 Stage 4。

## 启动条件

启动前边界已由用户明确确认，PM 已复算 75 个物理 candidate 行及固定 hashes、确认两根不存在并冻结 `ABF-P3-124-v1`。只有本最终任务卡的绝对路径投递到全新隔离 Codex 会话才构成执行授权；投递前不得创建 review/temp root、DB 或 App。
