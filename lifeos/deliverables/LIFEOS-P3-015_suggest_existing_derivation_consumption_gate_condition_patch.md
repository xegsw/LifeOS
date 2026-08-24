# LIFEOS-P3-015｜suggest 已有 Derivation 输入消费门条件补丁报告

- 任务类型：补丁 / 条件整改 / 工程硬化 / 回归测试
- 主责角色：工程负责人
- 协审角色：数据与权限、AI 信任与安全、QA / 测试、技术架构负责人
- 日期：2026-08-11
- 专项结论：**Pass（需 PM 验收确认）**

## 1. 任务摘要

1. **[已验证事实]** `suggest()` 返回已有 Derivation 前，已从仅判断 `status === "stale"` 改为同时调用 `derivationInputsConsumable(id, evidence)`；任一已记录输入不可消费即返回 `null`。
2. **[已验证事实]** 新增 direct-deny 反例：创建包含 `artifact-1` 与 `artifact-2` 的 suggestion 后，直接把非主证据 `artifact-1` 的 Authorization 改为 `deny`，不调用 `control()`。Derivation 仍为 `candidate`，但 `suggest()`、`feedback()` 和 `exportMemory()` 均阻断旧候选。
3. **[已验证事实]** 最终为 **19 PASS / 0 FAIL，P0 FAIL=0**；原有 18 项回归 18/18 PASS，P1-3 / P1-5 为 4/4 PASS，新增测试 1/1 PASS。
4. **[边界]** 仅关闭 P3-014 指定条件；未迁移其他 P1，未修改 P3-001 或项目账本，未启用真实能力。

## 2. 修改文件清单

实现与测试：

- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`

Evidence 更新：

- `evidence/MANIFEST.md`
- `evidence/test_results.json`
- `evidence/test_run.log`
- `evidence/invariant_migration_matrix.md`
- `evidence/architecture_conformance.md`
- `evidence/default_off_matrix.md`（重生成，内容与关闭状态无变化）

以上 evidence 路径均相对于 `lifeos/engineering/LIFEOS-P3-009/`。除此报告外未创建其他 deliverable；未修改 P3-001、Stitch、PRD、冻结资产或项目账本。

## 3. P3-014 条件关闭说明

**[实现事实]** `suggest()` 仍先通过 `recovery()` 选择可用主输入并定位 suggestion ID；对应 Derivation 存在时，返回其任何状态前都要求 `derivationInputsConsumable(id, evidence)` 为真。

该门逐条读取 `derivation_input`，要求 context 精确匹配 `artifact_id`、`evidence_version_id`、Artifact generation 与 Source generation，并再次通过 `canConsume()`。因此输入缺失或伪造、两级 generation mismatch、Authorization deny / missing / conflict / unknown、tombstone、版本或 Project 不匹配均 fail closed；零输入也拒绝。

**[推断]** 该改动统一了已有 suggestion 复用与 `feedback()`、`exportMemory()` 的派生输入判断，关闭 PM 复现的 direct-deny 非主证据旁路。结论仅适用于合成、单进程、受控测试包。

## 4. 新增测试与原有回归

新增 `P3-015 direct deny of non-primary input blocks existing suggestion feedback and export`：先创建双输入 suggestion，再直接 deny `artifact-1` 且不调用 `control()`；断言 Derivation 仍为 `candidate`，排除 stale 假阳性，并验证 suggest 返回 `null`、feedback 返回 `null`、export 不含旧 Derivation。

原有 P1-3 撤回 / 删除传播、P1-5 important_link 写门、P3-011 P0 消费门、H1-H9、T-ARCH 和八项默认关闭能力测试均保留且通过。

## 5. 测试命令与结果

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

- 修改前基线：18 PASS / 0 FAIL。
- 补丁后与验证脚本：19 PASS / 0 FAIL；P0 FAIL=0；退出码 0。
- 原有回归：18/18；P1-3 / P1-5：4/4；P3-015：1/1。
- Snapshot：`7abf6dec41f5b17bcfd9579f0f50a25bdc27cded3982cc60e1576de7c195d11e`。
- `node:sqlite` experimental warning 仍存在，不作为生产依赖冻结依据。

## 6. Evidence 一致性

`validate.mjs` 仅作必要统计更新：任务标识为 P3-015，并区分原有 18 项、P1-3 / P1-5 四项与条件补丁一项。Manifest、JSON、原始日志的运行时间、19/0 与 snapshot 一致；矩阵及架构符合性补充“已有 suggestion 返回前重检全部输入”。默认关闭矩阵八项能力仍全部关闭。

## 7. 角色与关卡

- **工程：通过。** `lifeos.ts` 仅新增一个门条件；未顺手处理其他清洁项。
- **数据与权限：通过。** suggest / feedback / export 均重检全部输入；不确定态与 context 错配 fail closed。
- **AI 信任与安全：通过。** 不可消费证据不再支撑旧 AI 建议；内容与来源身份分离未改变。
- **QA：通过。** 定向测试复现 PM 条件并排除 stale 假阳性；evidence 一致。
- **技术架构：有限边界内通过。** 未冻结生产 Schema / API / 模块边界，未启用真实 Tauri / IPC；R-0040 保持 Open / Conditional。
- **Gate 2 / 3 / 4：** 在受控测试包内通过；Gate 5 不适用。条件是否正式关闭仍需 PM 验收。

## 8. 未启用能力与未迁移项

**[已验证事实]** 仅使用 `synthetic-disposable` 与内存 SQLite。真实 Vault、Tauri / IPC、文件导出、真实数据、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户均未启用；R-0040 未关闭。

- P1-4：未迁移独立 generation mismatch staling。
- P1-6：未迁移 restore_candidates、权威投影与旧包不复活。
- P1-7：未迁移 `expires_at` 与 `retract_feedback`。
- P1-8：未迁移 suggestion ID 完整 generation 绑定。

## 9. 本地预检

已调用本地预检，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景。报告：`lifeos/local_prechecks/LIFEOS-P3-015_LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch_local_precheck.md`。它不替代 PM Review。

## 10. 结论与待确认

**专项结论：Pass。** 指定消费门条件已以最小补丁关闭，回归与 evidence 一致，无范围扩张。

**[需 PM 确认]** 是否接受本专项 Pass 并认定 P3-014 条件已关闭。本会话不更新账本、不扩展工程基线、不关闭 R-0040、不启动后续任务。

**[后续建议]** 无新增；P1-4 / P1-6 / P1-7 / P1-8 保持未迁移，由 PM 另行决定。
