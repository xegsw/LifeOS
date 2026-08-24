# LIFEOS-P3-022 PM Review：P2 工程清洁项 Batch Patch

评审日期：2026-08-13  
评审角色：PM 主会话  
任务类型：P3 Engineering Fast Lane / P2 Batch Patch  
验收结论：Accepted  
资产状态：Not Frozen / 不恢复工程基线 / 不关闭 R-0040  

## 1. 验收对象

- 任务卡：`lifeos/tasks/LIFEOS-P3-022_p2_engineering_cleanup_batch_patch.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-022_p2_engineering_cleanup_batch_patch.md`
- Evidence manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-022_LIFEOS-P3-022_p2_engineering_cleanup_batch_patch_local_precheck.md`

## 2. P3 快车道适用性

本任务适用 P3 Engineering Fast Lane：范围仅限 `lifeos/engineering/LIFEOS-P3-009/` 内合成数据、单进程、受控测试包和本地 evidence；未改变产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界；未启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。

本次 PM Review 未触发退出快车道条件：未发现 P0，未关闭风险，未恢复或冻结工程基线，未进入下一阶段，未启用真实能力。

## 3. 覆盖检查

P3-022 要求处理三个 P2 清洁项：

1. `feedback()` 不得通过重复 ID 静默覆盖原用户反馈。实际补丁将 feedback 写入改为 insert-once，重复、冲突和撤回后重复写入均 fail closed，不改写 `user_text` 或 `status`。
2. `validate.mjs` 需要区分 `total_fail`、`p0_fail`、`p1_fail`、`p2_fail`。实际输出已包含四类计数，且任何失败仍会非零退出。
3. `derivation.evidence_version_id` 不能被误读为唯一主证据权威。实际导出 / 恢复候选中标明其仅为 `legacy_compatibility_display_only`，完整权威输入集仍为 `derivation_input` / exported `inputs`。

上述三项均有测试或 evidence 表达；未发现任务范围遗漏。

## 4. 测试复跑摘要

PM 使用项目指定 Node runtime 复跑：

`cd lifeos/engineering/LIFEOS-P3-009 && /Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs`

复跑结果：

- Total：37 PASS / 0 FAIL
- P0 FAIL：0
- P1 FAIL：0
- P2 FAIL：0
- 既有 34 项回归：34/34 PASS
- P2 cleanup：3/3 PASS
- Evidence snapshot：`4d28b22d29c412fa335e30919d552c294405d313c1314a9d4837e88afe269159`

本地预检因本地模型连接重置跳过：`[Errno 54] Connection reset by peer`。按项目规则，本地预检不可用不阻塞 PM 验收，PM 已按任务卡、交付物、源码抽查和验证结果完成独立复核。

## 5. 风险状态

- R-0040：保持 Open / Conditional。
- 本次不关闭、不拆分任何风险。
- 本次不恢复、不冻结新的工程基线。
- 本次不改变 P3-001 / P3-009 的“后续工程基线候选”边界。

## 6. 修改文件核对

专项交付物声明修改范围为：

- `lifeos/engineering/LIFEOS-P3-009/src/store.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`
- `lifeos/engineering/LIFEOS-P3-009/evidence/*`
- `lifeos/deliverables/LIFEOS-P3-022_p2_engineering_cleanup_batch_patch.md`

PM 抽查未发现越权修改产品账本、P3-001 工程基线、Stitch 或真实能力配置。

## 7. PM 结论

LIFEOS-P3-022 验收通过，结论为 Accepted。P2 工程清洁项已在 P3-009 合成、单进程、受控测试包边界内完成：feedback 写入不再静默覆盖，validate 失败统计粒度已拆分，Derivation 主证据字段语义已降级为兼容 / 展示指针。

本结论允许继续下一项受控 P3 工程 / 评估任务；不允许关闭 R-0040、恢复或冻结工程基线、进入下一阶段或启用真实能力。

