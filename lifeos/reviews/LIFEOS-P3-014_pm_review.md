# LIFEOS-P3-014 PM Review

更新时间：2026-08-11

## 验收信息

- 任务 ID：LIFEOS-P3-014
- 任务名称：P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口独立工程复评
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-014_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High

## PM 总结

1. P3-014 按任务卡完成独立只读复评，未修改 P3-009 / P3-001 工程文件、项目账本或冻结资产。
2. 独立复评复跑 P3-009 测试为 18 PASS / 0 FAIL，并报告 42 组 / 78 条反例攻击全部通过；PM 使用 bundled Node v24.14.0 复跑测试，同样为 18 PASS / 0 FAIL。
3. P1-3 多证据 `derivation_input` 与非主证据 `revoke/delete` 传播，在任务卡定义范围内成立。
4. P1-5 `important_link` 写入口门，在任务卡定义范围内成立：用户确认关系、Project、版本、授权、generation、tombstone 和 evidence 均有门禁。
5. PM 接受 P3-014 作为独立复评任务，但不接受其“纯 Pass”作为无条件结论；PM 将结论调整为 Pass with Conditions。
6. 条件原因：P3-014 自身发现 `suggest()` 在已有 Derivation 返回路径上未调用 `derivationInputsConsumable()`；PM 定向复现确认，直接 deny 非主证据但未通过 `control()` 时，旧 suggestion 仍会返回。
7. 该问题当前不构成 P0：feedback 与 export 已阻断，且没有启用真实能力；但它违反“AI 建议消费也应重检所有派生输入”的一致性，PM 将其定为 P1 条件补丁。
8. R-0040 必须继续保持 Open / Conditional；本任务不构成真实 Tauri / IPC 风险关闭依据。

## PM 定向复核

PM 复跑命令：

```bash
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
```

结果：

- 18 PASS
- 0 FAIL
- P0 FAIL = 0

PM 定向复现 P3-014 P2 观察：

- 先创建基于 `artifact-1` 与 `artifact-2` 的 suggestion。
- 直接将非主证据 `artifact-1` 的 authorization 改为 `deny`，不调用 `control()`。
- 再次调用 `suggest("project-orbit", evidence)`。
- 结果：旧 suggestion 仍返回；但 `feedback()` 返回 null，`exportMemory()` 不包含该 derivation。

PM 判断：

- 这说明 `feedback()` 与 `exportMemory()` 的派生输入消费门已经生效。
- 但 `suggest()` 作为 AI 建议消费入口，已有 Derivation 返回路径也应执行 `derivationInputsConsumable()`。
- 因此该问题不是纯代码清洁度，而是 P1 级一致性补丁。

## 角色与关卡验收

- 主责角色覆盖情况：通过。独立工程评审已完成只读复跑、反例攻击和 evidence 一致性检查。
- 协审角色覆盖情况：条件通过。技术、数据与权限、AI 信任、QA 视角均覆盖；但 PM 上调一项问题级别。
- 已通过关卡：Gate 2 数据与来源、Gate 3 AI 权限与信任、Gate 4 技术可行性在有限工程边界内条件通过。
- 未通过或需后续确认关卡：Gate 5 用户价值不适用；真实 Tauri / IPC 仍未验证。
- 是否属于关键冻结事项：否。
- 是否需要独立评审：本任务自身就是独立复评。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- 独立评审结论：专项结论为 Pass；PM 调整为 Pass with Conditions。
- 是否允许进入下一任务或下一阶段：允许进入窄范围条件补丁；不允许进入下一阶段或启用真实能力。

## 验收与冻结区分

- 任务是否验收通过：是，P3-014 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-009 工程基线扩展、生产 Schema / API、真实 Tauri / IPC、真实 Vault、真实数据、导出格式、同步 / 多设备、L3、生产 SLA。
- 是否允许进入下一任务：Conditional，建议启动 P3-015 窄范围条件补丁。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是。

## 需要用户确认的事项

1. 是否采纳 P3-014 的 PM 验收结论：Accepted / Pass with Conditions。
   - PM 建议：采纳。
   - 不确认的影响：无法启动 P3-015 条件补丁。
2. 是否启动 P3-015 窄范围条件补丁。
   - PM 建议：启动。
   - 任务边界：只修复 `suggest()` 已有 Derivation 返回路径未重检全部 `derivation_input` 的问题，并新增 direct-deny 非主证据反例测试；可顺手把 P3-014 的 P2 观察登记为后续清洁项，但不要扩大实现。
3. 是否保持 R-0040 Open / Conditional。
   - PM 建议：保持。
   - 不确认的影响：可能误把合成后端测试外推为真实 Tauri / IPC 安全通过。

## 整改建议

建议创建 `LIFEOS-P3-015`：

- 类型：补丁 / 条件整改型任务。
- 推荐 Agent：Codex。
- 核心修复：`suggest()` 在返回已有 Derivation 前，必须调用 `derivationInputsConsumable()`；若任一输入证据不可消费，则不得返回旧候选。
- 必须新增测试：直接 deny 非主证据但不调用 `control()` 后，`suggest()` 不得返回旧候选。
- 回归要求：现有 18 项测试继续通过；P0 FAIL=0。
- 不允许范围：不迁移 P1-4 / P1-6 / P1-7 / P1-8，不启用真实能力，不改项目账本。

## 可接受内容

- P3-014 的只读复跑、反例攻击、evidence 一致性检查和 R-0040 保留判断可作为后续输入。
- P3-013 的 P1-3 / P1-5 主体迁移可继续保留。
- P3-013 未冒充完成 P1-4 / P1-6 / P1-7 / P1-8，边界清楚。

## 不接受或需谨慎内容

- 不接受将 P3-014 的最终结论作为无条件 Pass。
- 不接受将 P3-013 直接视为工程基线扩展完成。
- 不接受关闭 R-0040。
- 不接受启用真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型、向量、同步 / 多设备或 L3。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：P3-014 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：P3-013 / P3-014 状态更新为 Pass with Conditions / Accepted，下一动作指向 P3-015 条件补丁。
- `lifeos/DECISION_LOG.md`：新增 D-0160。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-014 并启动 P3-015。
- `lifeos/RISK_LOG.md`：暂不新增风险；R-0040 继续 Open / Conditional。
- `lifeos/AGENT_ROUTING_SCORECARD.md`：追加 WorkBuddy 适配度记录。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy
- 是否符合推荐：是
- Agent 与任务类型匹配度：High
- 主要优势：只读边界清楚，反例攻击覆盖广，evidence 一致性核对细。
- 主要问题：将 `suggest()` 旧候选返回路径的输入消费门缺口定为 P2，PM 判断应上调为 P1 条件补丁。
- 以后更适合分派给该 Agent 的任务类型：独立工程复评、反例攻击、证据链复核、风险分级审查。
- 不建议分派给该 Agent 的任务类型：需要直接修改代码并维护 evidence 的工程实现任务。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：是。

## 下一步任务建议

建议用户确认后启动：

`LIFEOS-P3-015`：P3-014 条件补丁：`suggest()` 已有 Derivation 输入消费门补强。

该任务完成后，再决定是否需要独立复评，或继续迁移 P1-4 / P1-6 / P1-7 / P1-8。

