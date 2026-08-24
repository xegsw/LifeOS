# LIFEOS-P3-020 P3-009 P1 迁移完成独立工程覆盖复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-020
- 对应交付物路径：P3-013 至 P3-019 交付物 + P3-009 当前工程状态
- 独立评审角色：独立工程评审负责人 / 反例攻击负责人
- 协审视角：数据与权限、AI 信任与安全、QA / 测试、技术架构
- 评审关卡：P1-3 / P1-4 / P1-5 / P1-6 / P1-7 / P1-8 覆盖完整性、H1-H9 / T-ARCH 回归、P0 消费门回归、evidence 一致性、默认关闭能力、R-0040 边界不误关
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-020_p1_migration_completion_independent_engineering_review.md`
- 评审结论：**Pass with Conditions**
- 更新时间：2026-08-11

## 评审摘要

1. **独立只读复跑 P3-009 测试套件（34 PASS / 0 FAIL）**，evidence 快照 SHA-256 `332e9e47...` 经独立重算确认一致，9 个文件逐文件 SHA-256 全部匹配。MANIFEST ↔ test_results.json ↔ test_run.log 三方一致（34/0/0）。P3-001 文件经 `snapshot_manifest.json` 比对确认 7/7 全部匹配未被修改。
2. **评审结论：Pass with Conditions。** P1-3 至 P1-8 均已在合成、单进程、受控测试包边界内完成迁移，独立反例攻击未发现 P0 或 P1 缺口。
3. **独立构造 63 条反例攻击，63 PASS / 0 FAIL**，覆盖 P1-3 多证据记录与撤回传播、P1-4 generation mismatch 主动 staling（artifact + source × suggest/feedback/export/restore）、P1-5 important_link 写入口门全维度 fail closed、P1-6 restore candidates 只读与旧包不复活、P1-7 expires_at 八入口阻断与 retractFeedback 幂等/不复活、P1-8 suggestion ID 完整绑定与稳定性、10 条组合场景（restore+expired、restore+feedback_retracted、suggestion ID+source gen change、important_link+expired/revoked/stale、feedback retract+confirmed/edited_confirmed/invalid/stale/expired、exportMemory+staling+inputsConsumable）、P0 回归、默认关闭能力回归、跨项目隔离。
4. **Evidence 一致性全部通过**：task 字段为 `LIFEOS-P3-019`（最后刷新任务），P1 分类计数（P1-3/5=4, P3-015=1, P1-4=2, P1-8=4, P1-6=5, P1-7=4）与测试文件实际匹配，总和 50（含 existing 30）= 34 PASS。
5. **八类默认关闭能力全部保持关闭**，`CAPABILITIES` 对象使用 `Object.freeze()`，所有能力调用均 throw `DisabledCapability`。
6. **R-0040 建议保持 Open / Conditional**：当前结果仅限合成、单进程、受控测试包，不构成生产 Schema / API / Tauri 配置 / 导出格式 / SLA 冻结依据。建议 PM 后续在确认本复评后，可考虑启动 R-0040 关闭条件评估任务。
7. 本评审未修改 P3-009 / P3-001 工程文件、evidence、项目账本或冻结资产；只运行只读测试和临时反例脚本（`/tmp/p3-020-adversarial.ts`）；未启用任何真实能力。

## 复跑能力说明

- 实际复跑：Yes。使用 WorkBuddy 管理的 Node v22.22.2 运行时，在原工程目录只读执行 `node --experimental-strip-types --test tests/invariants.test.ts`。
- 未运行 `validate.mjs`（该脚本会覆写 evidence 文件，超出只读复核授权范围），改为手动重算 snapshot 和逐文件 SHA-256 进行交叉验证。
- 反例攻击脚本位于 `/tmp/p3-020-adversarial.ts`，使用独立内存 SQLite 实例，不修改原工程目录。

## Evidence 一致性检查

| 检查项 | 结果 |
|---|---|
| Snapshot SHA-256 独立重算 | `332e9e47382f8c403a89695398779b6e9d6f682d37f867d850390aece0e00f6c` — 匹配 |
| 9 个文件逐文件 SHA-256 | 全部匹配 |
| MANIFEST.md PASS/FAIL/Snapshot | 34/0/`332e9e47...` — 与 test_results.json 一致 |
| test_run.log PASS/FAIL/tests | 34/0/34 — 与 test_results.json 一致 |
| test_results.json task 字段 | `LIFEOS-P3-019`（最后刷新任务，正确） |
| P1 分类计数 | P1-3/5=4, P3-015=1, P1-4=2, P1-8=4, P1-6=5, P1-7=4 — 与测试文件实际匹配 |
| P3-001 snapshot_manifest | 7/7 文件 SHA-256 匹配，未被修改 |

## P1-3 覆盖复核：多证据派生输入

**结论：Pass。**

- `suggest()` 在创建 Derivation 时，在同一 SQLite 事务内为每个可消费输入写入 `derivation_input` 行，记录 `derivation_id`、`evidence_version_id`、`artifact_id`、`source_id`、`artifact_generation`、`source_generation`。（反例 P1-3-01 验证）
- 非主证据 `revoke` 或 `delete` 通过 `control()` → `derivation_input.artifact_id` 将关联 Derivation 标为 `stale`。stale 后 `feedback()` 返回 null、`exportMemory()` 排除、`suggest()` 返回 null。（反例 P1-3-02, P1-3-03 验证）
- 零 `derivation_input` 的 Derivation 不会被 `suggest()` 返回，因为 `derivationInputsConsumable()` 要求 `inputs.length > 0`。（反例 P1-3-04 验证）

## P1-4 覆盖复核：Generation mismatch 主动 staling

**结论：Pass。**

- `staleGenerationMismatches()` 在 `suggest()`、`feedback()`、`exportMemory()` 入口均被调用，通过 `derivation_input` 关联当前 `artifact` 和 `source` 的 generation，发现不一致即更新为 `stale`。（反例 P1-4-01~03 验证）
- Artifact generation mismatch 和 Source generation mismatch 两个方向均覆盖。
- Stale 后 `restoreCandidates()` 不会将旧 Derivation 标为 restorable。（反例 P1-4-04 验证）
- 失效不依赖 `control()`、tombstone 或 Authorization deny 副作用——反例确认触发前后 tombstone 数和 deny 数均为 0。

## P1-5 覆盖复核：important_link 写入口门

**结论：Pass。**

- `createImportantLink()` 只接受 `user_confirmed + confirmed`；`ai_inference`、`unconfirmed`、空 evidence 均被拒绝。（反例 P1-5-01~04 验证）
- 写前和事务内均执行 `canConsume()` 重检；deny、missing authorization、artifact generation mismatch、cross project、tombstone、duplicate evidence versions 全维度 fail closed。（反例 P1-5-05~10 验证）
- `source_id` 来自数据库读取而非 context 传入，避免伪造。

## P1-6 覆盖复核：restore candidates 与旧包不复活

**结论：Pass。**

- `exportMemory()` 输出独立 `authorityProjection`，包含 Artifact 和 Derivation 的完整权威投影（Project、version、Source、generation、tombstone、authorization、content hash/kind、完整排序 derivation_input）。
- `restoreCandidates()` 只返回诊断结果，不执行导入或写回。13 类权威表行数在评估前后完全一致。（反例 P1-6-01 验证）
- Revoke / delete 后旧包不可恢复受影响 Artifact 和 Derivation。（反例 P1-6-02, P1-6-03 验证）
- Stale / invalid Derivation 不进入新导出，也不被旧包评估为 restorable。（反例 P1-6-04, P1-6-05 验证）
- 篡改包内容（original_text / output_text）会被 content hash 或 identity 检查阻断。（反例 P1-6-06, P1-6-07 验证）
- Artifact generation 变化标记为 `stale` 而非 `blocked`，区分了版本漂移与权限失效。（反例 P1-6-08 验证）

## P1-7 覆盖复核：expires_at 与 retract_feedback

**结论：Pass。**

- Authorization 可空 `expires_at_ms`：`NULL` 延续非过期行为，未来时间放行，到期时 fail closed。（反例 P1-7-01~03 验证）
- 过期授权一致阻断 `read`、`search`、`suggest`、`feedback`、`exportMemory`、`restoreCandidates`、`createImportantLink` 全部已实现入口。（反例 P1-7-04~08, P1-7-14 验证）
- `retractFeedback()` 拒绝非 user actor。（反例 P1-7-09 验证）
- 首次撤回把 feedback 状态改为 `retracted`，重复撤回返回同一状态且不新增/删除记录。（反例 P1-7-10 验证）
- 撤回 confirmed Derivation 改为 `feedback_retracted`，撤回 edited_confirmed 同理，`suggest()` 和 `exportMemory()` 均排除。（反例 P1-7-11, COMBO-07 验证）
- 撤回不复活 invalid / stale / expired Derivation。（反例 P1-7-12, P1-7-13, COMBO-08 验证）

## P1-8 覆盖复核：suggestion ID 完整 generation 绑定

**结论：Pass。**

- Suggestion ID 格式为 `suggestion:v2:<SHA-256>`，payload 包含 `projectId` 和稳定排序的完整输入集合，每个输入绑定 `evidenceVersionId`、`artifactId`、`sourceId`（数据库读取）、`artifactGeneration`、`sourceGeneration`。（反例 P1-8-01 验证）
- 顺序变化时 ID 不变（确定性排序）。（反例 P1-8-01 验证）
- 非主输入 Artifact generation 变化 → 新 ID，旧 Derivation stale。（反例 P1-8-02 验证）
- 非主输入 Source generation 变化 → 新 ID，旧 Derivation stale。（反例 P1-8-03 验证）
- 输入集合变化（缩减为仅主输入）→ 新 ID。（反例 P1-8-04 验证）
- 已确认 suggestion 重复调用复用同一 ID，保持 `confirmed` 状态。（反例 P1-8-05 验证）

## 组合反例攻击清单与结论

| 组合方向 | 反例数 | 结果 |
|---|---|---|
| restore candidates + 过期授权 | 1 | PASS |
| restore candidates + feedback_retracted | 1 | PASS |
| suggestion ID + 非主 Source generation 变化 | 1 | PASS |
| important_link + 过期/revoked/stale evidence | 3 | PASS |
| feedback retract + edited_confirmed/invalid/stale/expired | 2 | PASS |
| exportMemory + staleGenerationMismatches + derivationInputsConsumable | 2 | PASS |
| **总计** | **10** | **10 PASS / 0 FAIL** |

**组合结论：** P1-3 至 P1-8 之间未发现互相打架的场景。restore candidates 与过期授权、feedback 撤回与各种 Derivation 状态、suggestion ID 与 generation staling、important_link 与失效证据之间的组合行为均正确 fail closed。

## P0 / P1 / P2 问题清单

### P0 问题

无。

### P1 问题

无。

### P2 问题（不阻塞 Pass，记录为后续清洁项）

| ID | 描述 | 影响 |
|---|---|---|
| P2-1 | `feedback()` 仍使用 `INSERT OR REPLACE`，理论上重复 feedback kind 会静默覆盖（但当前测试未暴露问题，因为同一 derivation+kind 只调用一次） | 低：当前语义下 `INSERT` 即可，但不影响安全 |
| P2-2 | `validate.mjs` 的 `p0_fail` 字段直接等于 `fail`（所有失败计为 P0），未区分 P0/P1 测试失败 | 低：统计精度问题，不影响实际测试结果 |
| P2-3 | `suggest()` 中 `INSERT INTO derivation` 未使用 `INSERT OR IGNORE`，若并发同一 ID 可能 throw（但单进程合成测试包不暴露） | 低：单进程边界内不触发 |
| P2-4 | `derivation.evidence_version_id` 兼容字段仍保留，安全判断已以 `derivation_input` 全集为准，但兼容字段可能在后续迁移中引起混淆 | 低：已在 P3-013 报告中声明 |

## 是否建议 PM 后续考虑关闭 R-0040

**Conditional。**

当前 P3-009 在合成、单进程、受控测试包边界内已覆盖 P1-3 至 P1-8 全部迁移项，34 项测试 + 63 条独立反例攻击全部通过，evidence 一致，默认关闭能力未变。从工程覆盖角度，R-0040 的"P1 迁移完成"条件已满足。

但 R-0040 的关闭还应考虑：
- 真实 Tauri / IPC 验证仍未执行。
- 真实 Vault、文件导出、云 / 第三方模型、向量、同步、多设备、L3、外部用户均未启用。
- 生产 Schema / API / 模块边界 / 导出格式 / SLA 均未冻结。
- 本独立复评不替代 PM / 用户的风险关闭决策。

建议 PM 在确认本复评后，可启动 R-0040 关闭条件评估任务，但最终关闭仍需用户确认。

## 是否建议 PM 后续考虑恢复 / 冻结工程基线扩展

**Conditional。**

P3-009 在受控边界内已达到 P1 迁移完成候选标准。但工程基线扩展恢复 / 冻结涉及技术架构边界变化，应由 PM 另行走决策流程，本复评不自行执行。

## 必须整改项

无。当前无 P0 或 P1 问题阻塞。

## 条件通过项

| 条件 | 适用范围 | 失效条件 |
|---|---|---|
| 结论仅限合成、单进程、受控测试包 | P3-009 当前全部测试和 evidence | 启用真实 Tauri / IPC / Vault / 文件导出 / 云模型 / 向量 / 同步 / 多设备 / L3 / 外部用户后失效 |
| R-0040 保持 Open / Conditional | 风险登记 | PM / 用户另行关闭流程后变更 |
| 不构成生产 Schema / API / Tauri 配置 / 导出格式 / SLA 冻结 | 技术架构边界 | PM 另行冻结流程后变更 |
| P2 清洁项不阻塞当前结论 | feedback INSERT OR REPLACE、validate.mjs P0 统计、derivation 兼容字段 | 后续迁移中应逐步清理 |

## 关卡检查

- **Gate 1 产品一致性评审：Pass。** P3-009 覆盖 LifeOS 核心不变量（H1-H9 / T-ARCH），用户原文不可变、五类内容身份、消费前重检、撤回/删除不复活、默认关闭能力均成立。
- **Gate 2 数据与来源评审：Pass。** Source / Artifact / Derivation / Feedback / Authorization / Link 的身份、来源、generation、权限和状态未混淆。删除、撤回、过期、generation mismatch 均不能被旧包、旧 suggestion、旧 feedback 或 link 绕过。
- **Gate 3 AI 权限与信任评审：Pass。** AI suggestion 始终是候选，不绕过证据、授权、用户撤回或反馈撤回。用户确认、纠正、撤回可区分，不被 AI 静默改写。旧 AI 建议不通过导出 / 恢复 / ID 复用重新变成可信建议。
- **Gate 4 技术可行性评审：Pass with Conditions。** 结论仍限定于合成、单进程、受控测试包。未把真实 Tauri / IPC、真实 Vault、真实导出、生产 Schema / API 或 SLA 偷渡为已通过。R-0040 保持 Open / Conditional。
- **Gate 5 用户价值验证评审：** Not Applicable（合成测试包，无真实用户验证）。

## 风险

- R-0040 保持 Open / Conditional。本复评建议 PM 后续可考虑启动关闭条件评估，但不自行关闭。
- P2 清洁项（feedback INSERT OR REPLACE、validate.mjs P0 统计、derivation 兼容字段）应在后续工程任务中逐步清理，但不阻塞当前结论。
- 真实 Tauri / IPC、真实 Vault、真实文件导出、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户均未验证，后续启用前需另行独立评审。

## 需要 PM 决策

1. 是否接受 **Pass with Conditions** 结论，认定 P1-3 至 P1-8 在受控边界内完成迁移。
2. 是否启动 R-0040 关闭条件评估任务（建议保持 Open / Conditional，最终关闭需用户确认）。
3. 是否启动工程基线扩展恢复 / 冻结评估任务（本复评不自行执行）。
4. P2 清洁项是否纳入后续工程任务清单。

## 最终建议

建议 PM 接受 Pass with Conditions 结论，认定 P3-009 在合成、单进程、受控测试包边界内已完成 P1-3 至 P1-8 全部迁移。R-0040 建议保持 Open / Conditional，后续可由 PM 启动关闭条件评估任务。工程基线扩展恢复 / 冻结应由 PM 另行决策。P2 清洁项建议纳入后续工程任务清单，但不阻塞当前结论。

## 本地预检

已调用本地预检，状态为 Skipped / Local Model Unavailable（局域网模型连接不可用），符合允许跳过场景，不阻塞评审交付。
