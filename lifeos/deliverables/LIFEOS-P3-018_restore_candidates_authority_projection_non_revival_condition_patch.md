# LIFEOS-P3-018｜restore candidates、权威投影与旧包不复活条件补丁报告

## 任务信息

- 任务 ID：LIFEOS-P3-018
- 任务名称：P1-6 条件补丁：restore candidates、权威投影与旧包不复活
- 执行 Agent：Codex
- 任务类型：P3 Engineering Fast Lane / P1 条件补丁 / 工程硬化 / 回归测试
- 更新时间：2026-08-11
- 专项结论：**Pass（需 PM 验收）**

## 修复 / 验证目标

- 为受控内存导出包增加可独立核对的最小权威投影。
- 新增只读 `restoreCandidates()`，始终以当前 SQLite 权威状态重检旧包。
- 阻断 revoke / delete、授权变化、Artifact / Source generation 变化及 stale / invalid Derivation 的复活路径。
- 保持原有 25 项回归、H1-H9 / T-ARCH 与默认关闭能力不变。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-009/evidence/invariant_migration_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/architecture_conformance.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/default_off_matrix.md`（验证脚本重生成，关闭状态无变化）

未修改 `src/types.ts` 或 `src/store.ts`：现有表结构足以生成只读投影和候选诊断，无需变更 Schema。

## P1-6 条件关闭与设计说明

**[已验证事实]** `exportMemory()` 现输出独立 `authorityProjection`。Artifact 投影包含 Project、Artifact、当前 version、Source、标题/类别、内容哈希与内容身份、Artifact / Source generation、双方 tombstone，以及 Authorization 的 purpose / location / processor / decision / generation；Derivation 投影包含 Project、kind、output、status、evidence version 与完整排序 `derivation_input` 集合。

**[已验证事实]** `restoreCandidates()` 只返回 `restorable / blocked / stale / excluded` 候选及原因，不执行导入或写回。它不信任包内结论，而是重新查询当前 Artifact、version、Source、Authorization、tombstone、generation、Derivation status 与完整 inputs；同时核对包内容哈希和 Derivation 输出身份，包内容替换也会阻断。

**[已验证事实]** 旧包在 revoke / delete 或 direct-deny 后不可恢复受影响 Artifact 和 Derivation；Artifact / Source generation 独立变化后均标为 stale；stale / invalid Derivation 不进入新导出，也不会被旧包评估为可恢复建议。候选评估前后 13 类权威表、FTS 与 outbox 行数完全一致，且 generation 用例证明该方法不会顺手把当前 candidate 写成 stale。

**[合理推断]** P1-6 已在合成、单进程、内存包边界内满足主动恢复前诊断与不复活条件；该结论不代表正式恢复协议、真实文件格式或生产并发语义已完成。

## 测试摘要

- 直接复跑：`node --experimental-strip-types --test tests/invariants.test.ts`
- Evidence 生成：`node scripts/validate.mjs`
- 最终结果：**30 PASS / 0 FAIL；P0 FAIL=0**。
- 原有回归：25/25；新增 P1-6：5/5；P1-8：4/4；P1-4：2/2；P3-015：1/1；P1-3 / P1-5：4/4；H1-H9 / T-ARCH 全部通过。
- Snapshot：`741549734ce972a2e772c8505a6f8d8c5118549d73ef7630685cb018fa6b4be6`。
- 异常：仅有 `node:sqlite` experimental warning，不作为生产依赖冻结依据。

## Evidence

- Manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- 原始日志：`lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- 矩阵：`invariant_migration_matrix.md`、`architecture_conformance.md`、`default_off_matrix.md`

同次验证的 Manifest、JSON、日志和矩阵均为 30/0、P1-6 5/5；八类默认关闭能力未被破坏。

## 非范围、剩余风险与角色关卡

- 未实现真实文件导出、真实导入、真实备份恢复、路径选择、自动合并或权威写回；未冻结正式导出 / 恢复格式、Schema、API 或工程基线。
- 未启用真实数据、Vault、Tauri / IPC、云 / 第三方模型、向量、同步、多设备、L3 或外部用户；未修改 P3-001 或项目账本。
- P1-7 `expires_at` / `retract_feedback` 仍未迁移；R-0040 保持 Open / Conditional。
- 工程、数据与权限、AI 信任、QA 关卡：**Pass（受控边界）**；技术架构：**Pass with Conditions**，真实恢复与 R-0040 仍在边界外。无需独立复评。

## 本地预检

已按规则调用，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景，不阻塞工程交付。报告：`lifeos/local_prechecks/LIFEOS-P3-018_LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch_local_precheck.md`。该结果不替代 PM Review。

## 是否触发用户确认与结论

- 是否触发用户级确认：**No**。未涉及 P0、风险关闭、工程基线恢复、真实能力启用、阶段切换或关键冻结边界变化。
- 最终结论：**Pass（需 PM 验收）**。P1-6 已在任务授权的合成、单进程、受控内存包范围内完成；专项会话不关闭 R-0040、不更新账本、不启动后续任务。
