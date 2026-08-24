# LIFEOS-P3-022 P2 工程清洁项 Batch Patch

## 任务信息

- 任务 ID：LIFEOS-P3-022
- 任务名称：P2 工程清洁项 Batch Patch：feedback 覆盖语义、validate 分级统计、Derivation 主证据字段去混淆
- 执行 Agent：Codex
- 任务类型：P3 Engineering Fast Lane / P2 工程补丁 / Batch Patch
- 更新时间：2026-08-13

## 修复 / 验证目标

- P2-CLEAN-1：反馈 ID 改为仅首次插入，重复、冲突及撤回后的同 ID 写入均 fail closed，不覆盖 `user_text` 或 `status`。
- P2-CLEAN-2：验证结果同时输出 `fail`、`total_fail`、`p0_fail`、`p1_fail`、`p2_fail` 与 `unclassified_fail`；任意测试失败仍非零退出。
- P2-CLEAN-3：保留数据库兼容字段 `derivation.evidence_version_id`，但明确其仅为 primary / legacy compatibility display 元数据；完整 `derivation_input` / `inputs` 继续作为权威输入集合。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-009/src/store.ts`：注明兼容字段语义。
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`：反馈冲突拒绝；建议返回和 authority projection 去混淆；导出及恢复判定继续依赖完整 inputs。
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`：新增 3 项反馈覆盖测试，并加强多输入导出 / 恢复权威性测试。
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`：任务号、失败分级、P2 统计、evidence 文案及 snapshot 哈希更新。
- `lifeos/engineering/LIFEOS-P3-009/evidence/`：刷新测试日志、机器结果、矩阵、架构说明和 manifest。

## 非范围

- 未改变产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界。
- 未修改 P3-001、Stitch 或项目账本；未关闭或拆分 R-0040。
- 未恢复 / 冻结工程基线，未进入下一阶段，未启用真实数据、Vault、Tauri / IPC、文件导出、云模型、向量、同步、多设备、L3 或外部用户。

## 测试摘要

- 任务指定命令：`node scripts/validate.mjs`；当前 shell 因 `node` 不在 PATH 无法直接启动。
- 实际等价复跑：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs`（Node v24.19.0）。
- 结果：37 PASS / 0 FAIL；`total_fail=0`，P0 / P1 / P2 FAIL 均为 0；原 34 项回归 34/34 PASS；新增 P2 清洁测试 3/3 PASS。
- 新增测试：同 ID 重复反馈保留原记录；冲突文本不替换；撤回反馈不复活。既有 P1-6 测试同时确认：修改 primary display 元数据不改变恢复结论，缺失完整 inputs 则不可恢复。
- 关键失败或异常：首次复跑发现两项测试对 SQLite null-prototype 行对象使用了不合适的深相等断言，并发现失败标题在日志中重复计数；修正断言与标题去重后最终全通过，最终 evidence 已覆盖中间结果。

## P0 / P1 / P2 状态

- P0：0；未触发退出快车道条件。
- P1：0。
- P2：P2-CLEAN-1 / 2 / 3 均已实现并有可执行证据。

## Evidence

- Evidence manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- test_results：`lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- test_run：`lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- 其它证据：`architecture_conformance.md`、`invariant_migration_matrix.md`、`default_off_matrix.md`，均位于同一 evidence 目录。

## 角色与关卡

- 已验证事实：Technical Architect / QA Engineer 检查最小实现与完整复跑；Data Trust Reviewer 确认用户反馈历史不被同 ID 写入覆盖或复活；AI Trust Reviewer 确认完整 inputs 仍控制消费、导出与恢复，兼容主证据字段不降格多输入判断。
- 关卡结论：Gate 2、Gate 3、Gate 4 均在“合成数据、单进程、受控测试包”范围内通过；不外推到真实集成、生产格式或能力准入。
- 合理推断：三项修改未改变核心权限、删除、导出或 AI 建议可信度边界，仅降低既有实现和 evidence 的误读风险。

## 剩余风险

- R-0040 继续保持 Open / Conditional；真实 Tauri / IPC 与真实能力链路未被本任务验证。
- 当前仅验证内存导出 / 只读恢复候选，不代表生产 Schema、API、真实导出格式、平台打包或 SLA 通过。

## 是否触发用户确认

- 是否触发：No。
- 原因：无 P0、风险关闭、工程基线恢复、真实能力启用、阶段切换或关键边界变化。

## 是否需要独立复评

- 是否需要：No。
- 原因：任务卡明确无需独立复评，且最终复跑未发现 P0 或核心边界变化。

## 下一步建议

- 建议 PM 按快车道流程复核本报告、evidence manifest 与测试结果；专项会话不更新账本、不启动后续任务。

