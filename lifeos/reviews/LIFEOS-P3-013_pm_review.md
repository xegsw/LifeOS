# LIFEOS-P3-013 PM Review

更新时间：2026-08-11

## 1. 验收结论

- PM 验收结论：Accepted / Pass with Conditions。
- 任务是否通过：通过。
- 对应资产是否冻结：不冻结。
- 是否允许进入下一步：允许在用户确认采纳后，启动 `LIFEOS-P3-014` 独立工程复评。
- 是否允许进入真实能力：不允许。

## 2. 本次验收对象

- 任务卡：`lifeos/tasks/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- 证据清单：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-013_LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report_local_precheck.md`

## 3. PM 复核摘要

P3-013 按任务卡完成了 P3-009 受控工程目录内的 P1-3 / P1-5 迁移，没有修改 P3-001、Stitch、项目方向、技术架构冻结合同或真实能力边界。

本次迁移的有效范围为：

- 在合成、单进程、受控测试包边界内，为 `derivation` 增加多证据 `derivation_input` 输入快照。
- 非主证据被 `revoke` 或 `delete` 后，相关派生变为 `stale`，并阻断 feedback、export、suggest 等消费路径。
- 增加 `important_link` / `important_link_evidence` 写入口与证据快照。
- `important_link` 只允许 `user_confirmed + confirmed` 的关系写入。
- `important_link` 写入前和事务内均执行消费门禁，覆盖项目、版本、授权、generation、tombstone、来源证据等失败场景。

本次未覆盖、也不得外推为已完成：

- P1-4 恢复包 checksum / 载荷自证迁移。
- P1-6 Project state 闭包防混入迁移。
- P1-7 更细粒度 generation / source mutation 反例迁移。
- P1-8 capability / IPC 真实矩阵扩展。
- 真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型、向量、同步 / 多设备或 L3 自动动作。

## 4. 验证结果

PM 使用 bundled Node v24.14.0 复跑：

```bash
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
```

结果：

- 18 PASS
- 0 FAIL
- P0 FAIL = 0

证据包摘要与 PM 复跑一致：

- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md` 记录 18 PASS / 0 FAIL / P0 FAIL=0。
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json` 记录 original regression expected = 14，P1 migration expected = 4，P1 migration pass = 4。
- evidence snapshot：`41c17e8474da4e8e841de29ea9ca897324af2c7081aeb32031799092b2634be0`。

PM 抽查实现与测试：

- `src/store.ts` 已新增 `derivation_input`、`important_link`、`important_link_evidence` 表。
- `src/lifeos.ts` 中 `suggest()` 会记录每个可用输入证据版本、artifact/source generation；`derivationInputsConsumable()` 要求所有派生输入都仍可消费。
- `control()` 会基于 `derivation_input` 将依赖该 artifact 的 derivation 标记为 `stale`。
- `feedback()` 和 `exportMemory()` 均会重检派生输入是否仍可消费。
- `createImportantLink()` 要求用户确认关系、项目一致、证据非空、版本匹配，并在事务内再次重检 `canConsume()`。
- 测试已覆盖 P1-3 两组、P1-5 两组新增回归。

本地预检结果：

- 本地模型不可用，预检状态为 Skipped / Local Model Unavailable。
- 错误：`[Errno 54] Connection reset by peer`。
- 本地预检不作为 PM 验收依据。

## 5. 角色检查点

- PM / 项目负责人：通过。P3-013 范围收敛，没有扩大产品方向或真实能力。
- 工程负责人：通过。实现与测试集中在 `lifeos/engineering/LIFEOS-P3-009/`，复跑结果稳定。
- AI 权限与信任负责人：条件通过。P1-3 / P1-5 的证据与消费门要求已迁移，但真实 Tauri / IPC 与真实数据路径仍未启用。
- 数据治理 / 证据链负责人：条件通过。多证据输入与 Link 证据快照已建立，但仍限合成测试包。
- 风险负责人：条件通过。R-0040 继续 Open / Conditional；本任务不构成真实 Tauri capability 风险关闭依据。

## 6. PM 判断

P3-013 可以作为 P3-009 工程基线候选的 P1 安全不变量补强输入，但不能直接等同于工程基线扩展完成。原因是：

- 本任务是工程迁移任务，不是独立复评任务。
- P3-010 曾证明 P3-009 自测可能漏掉关键消费门反例。
- P3-013 新增了写入口和证据依赖路径，应由独立工程评审会话做反例攻击。

因此 PM 建议：

- 用户确认采纳 P3-013 后，启动 `LIFEOS-P3-014` 独立工程复评。
- P3-014 应重点攻击多证据撤回 / 删除传播、Link 写入口门、项目闭包、generation 漏绑、证据快照伪造和 evidence 一致性。

## 7. 待用户确认

请用户确认：

- 是否采纳 `LIFEOS-P3-013` 的 PM 验收结论。
- 是否启动 `LIFEOS-P3-014` P3-013 独立工程复评。

