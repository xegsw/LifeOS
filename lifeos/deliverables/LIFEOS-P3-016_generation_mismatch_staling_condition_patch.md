# LIFEOS-P3-016｜独立 generation mismatch staling 条件补丁报告

## 任务信息

- 任务 ID：LIFEOS-P3-016
- 执行 Agent：Codex
- 任务类型：P3 Engineering Fast Lane / P1 条件补丁 / 工程硬化 / 回归测试
- 更新时间：2026-08-11
- 专项结论：**Pass（需 PM 验收）**

## 修复 / 验证目标

- 让任一 `derivation_input` 的 Artifact 或 Source generation 与当前权威行错配时，旧 Derivation 主动变为 `stale`。
- 保证 `suggest()`、`feedback()`、`exportMemory()` 均先触发此机制并阻断旧派生物。
- 证明失效不依赖 `control()`、tombstone 或 Authorization deny 副作用。
- 保持原有 19 项、P1-3 / P1-5、P3-015、H1-H9 / T-ARCH 与默认关闭能力回归。

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

未修改 `src/store.ts` 或 `src/types.ts`：现有归一化输入表及 generation 字段足以完成补丁，无需扩展 Schema 或类型。

## P1-4 条件关闭说明

**[已验证事实]** 新增私有 `staleGenerationMismatches()`：以完整 `derivation_input` 集合关联当前 `artifact` 与 `source`，发现任一输入缺失或 Artifact / Source generation 不一致时，将关联 Derivation 更新为 `stale`。`suggest()`、`feedback()`、`exportMemory()` 均在读取或返回派生物前调用该方法，因此即使上下文已因错配无法消费，状态仍会先完成失效。

**[已验证事实]** 测试直接递增非主输入 `artifact-1` 或其 Source 的 generation，未调用 `control()`；触发前 Derivation 保持 `candidate`，触发后为 `stale`，同时 tombstone 数与 deny Authorization 数均为 0。三个消费入口分别在独立实例中触发并通过，随后三者均持续阻断旧 Derivation。

**[推断]** 该实现补齐了“消费时拒绝”与“权威状态主动呈现失效”之间的差距，并继续以所有已记录输入为准，而非兼容性的主证据字段。结论仅适用于当前合成、单进程、受控 SQLite 骨架。

## 新增 / 修改测试

- `P1-4 artifact generation mismatch independently stales derivation at every consumption entry`
- `P1-4 source generation mismatch independently stales derivation at every consumption entry`

两项测试各自遍历 suggest / feedback / export 三个触发入口，并断言：直接 generation 变更、触发前 candidate、触发后 stale、三入口阻断、无 tombstone、无 deny。原有 19 项未删除或改名。

## 测试摘要

- 基线：19 PASS / 0 FAIL。
- 复跑命令：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts`
- Evidence 命令：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs`
- 最终结果：**21 PASS / 0 FAIL；P0 FAIL=0**。
- 原有回归：19/19；P1-3 / P1-5：4/4；P3-015：1/1；P1-4：2/2。
- Snapshot：`a371643a8580faed4ac1ae6d5240b5fabf50c7b757917e43b1683ba56c7bcd41`。
- 异常：仅有 `node:sqlite` experimental warning，不作为生产依赖冻结依据。

## Evidence

- Manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- 原始日志：`lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- 矩阵：`invariant_migration_matrix.md`、`architecture_conformance.md`、`default_off_matrix.md`

Manifest、JSON、日志和矩阵均来自同次验证，21/0、分类统计与 snapshot 一致；八类默认关闭能力未被破坏。

## 非范围与剩余风险

- 不改变产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界。
- 未启用真实数据、真实 Vault、真实 Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 未修改 P3-001 或项目账本；不关闭 R-0040，不恢复工程基线，不进入下一阶段。
- P1-6 restore candidates、P1-7 `expires_at` / `retract_feedback`、P1-8 suggestion ID 完整 generation 绑定仍未迁移。
- 未处理 `feedback()` 的 `INSERT OR REPLACE`、自引用 Link、夹具多样性或其他 P2 清洁项。

## 角色与关卡

- 工程负责人：**Pass**；仅在 `lifeos.ts` 增加最小方法与三处调用，19 项原回归全通过。
- 数据与权限负责人：**Pass（受控边界）**；以完整输入集合对比当前 Artifact / Source generation，两级均覆盖。
- AI 信任与安全负责人：**Pass（受控边界）**；旧建议状态变为 stale，不能继续建议、反馈或导出，内容身份分离未改变。
- QA / 测试负责人：**Pass**；真实制造 generation mismatch，断言状态变化且排除 control / tombstone / deny 假阳性，evidence 一致。
- 技术架构负责人：**Pass with Conditions**；无 Schema/API/模块边界冻结或真实能力启用，R-0040 保持 Open / Conditional。
- 已覆盖关卡：P1-4、suggest / feedback / export、P1-3 / P1-5 / P3-015、H1-H9 / T-ARCH、evidence manifest、默认关闭能力回归。

## 本地预检

已按规则调用本地预检，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景，不阻塞工程交付。报告：`lifeos/local_prechecks/LIFEOS-P3-016_LIFEOS-P3-016_generation_mismatch_staling_condition_patch_local_precheck.md`。该结果不替代 PM Review。

## 结论

**Pass（需 PM 验收）。** P1-4 已在授权边界内以最小补丁实现，Artifact 与 Source generation mismatch 均会由任一派生消费入口主动置 stale，且三入口全部阻断旧派生物；21 PASS / 0 FAIL、P0=0。无需用户确认或独立复评；是否正式接受由 PM 主会话决定。
