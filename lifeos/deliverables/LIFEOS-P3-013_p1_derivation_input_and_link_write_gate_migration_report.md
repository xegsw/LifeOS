# LIFEOS-P3-013｜P1 派生输入与 important_link 写入口门迁移报告

- 任务类型：工程硬化 / P1 迁移 / 回归测试
- 主责角色：工程负责人
- 协审角色：数据与权限、AI 信任与安全、QA / 测试、技术架构负责人
- 日期：2026-08-11
- 结论：**Pass with Conditions**

## 1. 任务摘要

1. **[已验证事实]** P3-009 已新增归一化 `derivation_input`，一个 Derivation 可记录多个精确 evidence version，以及各输入的 Artifact、Source 和两级 generation 快照；不再只以 `derivation.evidence_version_id` 判断全部输入有效性。
2. **[已验证事实]** `revoke` 或 `delete` 任一派生输入（包括非主证据）会通过 `derivation_input` 将关联 Derivation 标为 `stale`。stale 后 feedback、内存测试包 export 和同一建议的再次返回均被阻断。
3. **[已验证事实]** 已新增最小 `createImportantLink()` 写入口、`important_link` 与 `important_link_evidence`。写入显式保存 Project、from/to Artifact 与精确 Version、两端 Source 身份、Link 身份、确认状态和证据输入快照。
4. **[已验证事实]** important_link 写前及事务内再次复用 `canConsume()`，对 Project、当前版本、Authorization、Artifact/Source generation、tombstone、purpose、location、processor 和 evidence 执行 fail-closed 重检。
5. **[已验证事实]** 最终验证为 **18 PASS / 0 FAIL，P0 FAIL=0**；原有 14 项全部继续通过，P1-3 / P1-5 新增 4 项全部通过。八类默认关闭能力矩阵无变化。
6. **[边界]** 本结果仅证明合成、单进程、受控内存测试包；不冻结生产 Schema、API 或模块边界，不启用真实 Tauri / IPC、Vault、文件导出或其他关闭能力。

## 2. 修改文件清单

工程实现与测试：

- `lifeos/engineering/LIFEOS-P3-009/src/types.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/store.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`

验证脚本刷新：

- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-009/evidence/invariant_migration_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/architecture_conformance.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/default_off_matrix.md`

本报告为 `lifeos/deliverables/` 下唯一新增文件。未修改 P3-001、项目账本、冻结资产、Stitch 或 PRD。

## 3. P1-3 多证据派生输入迁移

**[实现事实]** `suggest()` 首次创建 Derivation 时，在同一 SQLite 事务内写入全部可消费输入。每条 `derivation_input` 保存 `derivation_id`、`evidence_version_id`、`artifact_id`、`source_id`、`artifact_generation` 和 `source_generation`。重复建议仍保留既有 Derivation、确认状态和既有输入集合，继承 P1-1 修复。

**[消费门事实]** `feedback()` 和 `exportMemory()` 通过 `derivationInputsConsumable()` 要求全部已记录输入均存在精确匹配 context 且重新通过 `canConsume()`；缺少任一输入或任一输入失效即拒绝。`control()` 不再只按主证据列传播，而是按 `derivation_input.artifact_id` 将所有相关 Derivation stale。

**[AI 信任事实]** stale Derivation 不接受 feedback、不进入导出，也不被 `suggest()` 重新作为下一步候选返回。测试特意撤回 / 删除非主证据 `artifact-1`，而主证据 `artifact-2` 仍合法，以证明派生物不能仅凭主证据继续 active。

**[边界]** 为保持既有返回形状，`derivation.evidence_version_id` 暂保留为主证据兼容字段，但安全判断以 `derivation_input` 全集为准。本任务没有实现 P1-4 的独立 generation mismatch 自动 staling；generation mismatch 仍在消费时 fail closed。

## 4. P1-5 important_link 写入口迁移

**[实现事实]** `createImportantLink()` 只接受显式 `user_confirmed + confirmed` 的重要 Link，避免把 AI inference、外部引用或未确认关系冒充为用户确认事实。表中分别保存 Link 身份 / 确认状态和两端 Source 身份；证据表保存每个 evidence version 与 Artifact/Source generation 快照。

**[写入口门事实]** 写入要求：from、to 与全部 evidence 均属于调用 Project；每个 context 当前可消费；版本与权威 current version 一致；证据非空且版本不重复。事务建立后再次运行同一消费门，检查失败、唯一键冲突或并发状态变化均回滚并返回 `null`。

**[负测事实]** deny、missing Authorization、generation mismatch、cross Project 和 tombstone 五类场景均未产生 Link 行。合法路径同时核对 Project、from/to Source、确认身份和两条 evidence 记录。

## 5. 新增 / 修改测试清单

| 测试 | 覆盖 |
|---|---|
| `P1-3 derivation records every evidence version and generation` | 两个输入版本、Artifact/Source 身份及两级 generation 均落账 |
| `P1-3 non-primary revoke or delete...` | 非主证据 revoke/delete 传播；stale 后 feedback/export/suggest 阻断 |
| `P1-5 important_link writes...` | 合法确认 Link 的 Project、两端、Source、身份、确认和 evidence 绑定 |
| `P1-5 important_link fails closed...` | deny、missing auth、generation mismatch、cross Project、tombstone |

原有 14 项测试未删除或改名，并继续覆盖 H1-H9、P0 授权冲突、P1-1 / P1-2 与 T-ARCH。

## 6. 测试命令与结果摘要

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

- 环境：macOS arm64；Node v24.14.0；内建 `node:sqlite`。
- 最终结果：18 tests / 18 pass / 0 fail；P0 fail 0。
- 原有回归：14 / 14 PASS；P1-3 / P1-5 新增迁移：4 / 4 PASS。
- Evidence snapshot：`41c17e8474da4e8e841de29ea9ca897324af2c7081aeb32031799092b2634be0`。
- 非阻断提示：`node:sqlite` 仍有 experimental warning，不构成生产依赖冻结依据。

## 7. Evidence 更新

`validate.mjs` 已将任务标识更新为 P3-013，并在机器摘要中分别记录原有 14 项预期和 4 项 P1 迁移测试。MANIFEST、`test_results.json`、`test_run.log` 的 18/0、运行时间与 snapshot 一致；迁移矩阵和架构符合性已加入多证据输入、撤回传播及 important_link 写门；默认关闭矩阵内容未变化且 8 项负测继续通过。

## 8. 未启用真实能力与剩余迁移状态

**[已验证事实]** 本任务仅使用 `synthetic-disposable` 夹具和内存 SQLite。未接入或启用真实 Obsidian Vault、Tauri / IPC、文件系统导出、真实数据、云 / 第三方模型、向量、同步 / 多设备、L3 或外部用户。R-0040 保持 `Open / Conditional`。

- P1-4：未迁移；仅保留消费时 generation mismatch fail closed。
- P1-6：未迁移 restore_candidates、权威投影与旧包不复活。
- P1-7：未迁移 Authorization `expires_at` 与 `retract_feedback`。
- P1-8：未迁移 suggestion ID 的完整 generation 绑定，现有 fallback 边界不变。

**[建议｜需 PM 后续决定]** 上述项目继续保持关闭 / 未迁移状态；本会话不创建或启动后续任务。

## 9. 本地预检

已按项目规则调用本地预检，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`。该情况符合允许跳过场景，不阻塞工程交付。预检报告：`lifeos/local_prechecks/LIFEOS-P3-013_LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report_local_precheck.md`。本地预检不替代 PM Review 或后续独立评审。

## 10. 角色检查点与关卡

- **工程负责人：Pass。** 修改限于 P3-009、evidence 与指定报告；18 项可复跑。
- **数据与权限负责人：Pass（合成边界）。** 多证据完整落账；任一输入撤回 / 删除传播；Link 写门重检 Project、版本、授权、generation、tombstone 和证据。
- **AI 信任与安全负责人：Pass（本任务边界）。** stale 派生不能继续建议、导出或接受 feedback；Link 的用户确认身份与 AI inference / external reference 明确分离。
- **QA / 测试负责人：Pass。** 新增测试包含 revoke、delete、deny、missing auth、generation mismatch、cross Project、tombstone；原有 14 项未回退；evidence 同次生成。
- **技术架构负责人：Pass with Conditions。** 未冻结 Schema/API/模块边界，未启用真实能力；R-0040 不变，仍需不同 Agent 后续独立评审。
- **任务关卡：** P1-3、P1-5、H1-H9 回归、默认关闭能力回归和 evidence manifest 更新均通过；正式验收与后续独立评审由 PM 决定。

## 11. 结论与需 PM 确认

**Pass with Conditions。** P1-3 和 P1-5 已在 P3-009 的合成、单进程、受控测试包边界内完成迁移，18/18 PASS、P0=0。条件是：该结果不得外推为生产 Schema/API、真实 Tauri / IPC、真实数据或能力启用结论；P1-4 / P1-6 / P1-7 / P1-8 仍未迁移；按任务卡仍需后续独立评审。

**[需 PM 确认]** 是否验收 P3-013 并安排独立工程评审。专项会话不自行验收、不更新账本、不冻结资产、不关闭风险、不启动后续任务。
