# LIFEOS-P3-011 PM Review｜P3-009 P0 消费门返工与回归补测

## 验收信息

- 任务 ID：LIFEOS-P3-011
- 任务名称：P3-009 P0 消费门返工与回归补测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`
- Evidence Manifest 路径：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-011_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen；P3-009 保持 Rework pending independent re-review
- 是否允许进入下一任务：Conditional，用户确认采纳后启动 P3-012 独立复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-11

## PM 总结

1. P3-011 按任务卡在 `lifeos/engineering/LIFEOS-P3-009/` 内完成窄范围返工，未修改 P3-001、项目账本、Stitch 或冻结资产。
2. P0 `allow+deny` 授权冲突放行已修复：消费门现在要求完整授权上下文内 `total === 1 && allow_count === 1` 才放行。
3. PM 复跑 P3-009 测试，结果为 14 PASS / 0 FAIL；PM 复跑 `scripts/validate.mjs` 成功，并刷新 evidence。
4. PM 复现 P3-010 的 AD-1 历史反例，当前 read / search / recovery / suggest / export 均 fail closed，确认 P0 关闭。
5. P1-1 / P1-2 已在同范围内修复：重复 suggestion 不再静默重置 confirmed 状态；feedback 对非 candidate derivation 显式拒绝。
6. P1-3 至 P1-8 未在本任务扩散实现，已列入后续迁移清单，范围纪律合格。
7. P3-001 snapshot 校验 7 / 7 文件一致，未被本任务修改。
8. 本地预检已调用，但局域网模型连接重置，状态为 Skipped / Local Model Unavailable；不作为 PM 验收依据。

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人覆盖充分；修复范围、测试、evidence、报告均完整。
- 协审角色覆盖情况：
  - 数据与权限负责人：覆盖；deny / conflict / duplicate allow / missing / unknown 均 fail closed。
  - AI 信任与安全负责人：覆盖；候选确认状态保持和非 candidate feedback 拒绝已补测。
  - QA / 测试负责人：覆盖；新增 4 项测试，原 10 项回归通过，evidence 一致。
  - 技术架构负责人：覆盖；未冻结 Schema / API / 模块边界，未启用真实能力。
- 已通过关卡：P0 修复验证、回归测试、P1 同范围修复评估、evidence manifest 更新、默认关闭能力回归。
- 未通过或需后续确认关卡：P3-009 是否恢复工程基线候选仍需独立复评；R-0042 是否关闭仍需独立复评和 PM / 用户确认。
- 是否属于关键冻结事项：否；但影响 P3-009 工程基线候选恢复。
- 是否需要独立评审：Yes，建议 P3-012。
- 独立评审路径：待创建。
- 独立评审结论：未开始。
- 是否允许进入下一任务或下一阶段：允许用户确认后进入 P3-012 独立复评；不允许进入下一阶段。

## PM 复核记录

### 复跑命令

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

结果：

- 测试：14 PASS / 0 FAIL
- P0 失败：0
- P1 Open：0
- Evidence snapshot：`26eae1f16ffb4bf61c824ecf59552066fb063fcb7b981a0f0694f7b85bf62881`

### PM 抽样复核

PM 复现 P3-010 AD-1 历史反例：

- read：PASS，返回 null
- search：PASS，返回空
- recovery：PASS，返回空
- suggest：PASS，返回 null
- exportMemory：PASS，artifacts 为空

### P3-001 完整性

PM 重算 P3-001 snapshot manifest：

- checked：7
- missing：0
- mismatch：0
- snapshot：`ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`

### 本地预检

- 预检路径：`lifeos/local_prechecks/LIFEOS-P3-011_LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report_local_precheck.md`
- 预检状态：Skipped / Local Model Unavailable
- 错误：`[Errno 54] Connection reset by peer`
- PM 判断：允许跳过；不影响 PM 复核。

## 验收与冻结区分

- 任务是否验收通过：Yes，P3-011 Accepted。
- 对应资产是否冻结：No。
- P3-009 是否恢复工程基线候选：No，需 P3-012 独立复评通过后再判断。
- R-0042 是否关闭：No，保持 Open。
- 冻结范围：无。
- 未冻结内容：P3-009 工程基线、生产 Schema、API、模块边界、Tauri 配置、真实数据、真实 Vault、真实 IPC、导出格式、同步、多设备、云 / 第三方模型、L3、生产 SLA。
- 是否允许进入下一任务：Conditional；用户确认采纳 P3-011 后，可启动 P3-012 独立复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-011，并启动 P3-012 独立复评？
   - PM 建议：采纳，并启动 P3-012。
   - 可选方向：A. 采纳并启动 P3-012；B. 要求 P3-011 继续返工；C. 暂停工程线。
   - 不确认的影响：P3-009 保持 Rework，不能恢复工程基线候选；R-0042 保持 Open。

## 整改建议

本任务不要求继续返工。P3-012 独立复评应重点验证：

- P3-010 AD-1 是否彻底关闭，所有消费入口均 fail closed。
- duplicate allow / unknown / missing auth 是否继续 fail closed。
- P1-1 / P1-2 是否真实关闭，且没有引入新的状态写入绕路。
- P1-3 至 P1-8 是否仍被清楚保留为未迁移项，没有被误报完成。
- Evidence 是否与实际代码和测试一致。

## 可接受内容

- P0 修复方案可接受。
- P1-1 / P1-2 的窄范围修复可接受。
- Evidence 自动刷新与报告口径可接受。
- 未启用真实能力、未冻结实现细节、未修改 P3-001 的边界纪律可接受。

## 不接受或需谨慎内容

- 不接受直接恢复 P3-009 工程基线候选。
- 不接受关闭 R-0042。
- 不接受把 14 PASS 外推为 P3-001 全部 23 项测试 / 136 条断言已迁移完成。
- 不接受在 P3-012 前扩展真实 Tauri / IPC、真实 Vault、真实数据或外部能力。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：P3-011 更新为 Accepted；P3-009 保持 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-011 更新为 Accepted；P3-009 标记为返工完成待独立复评。
- `lifeos/DECISION_LOG.md`：新增 D-0154。
- `lifeos/RISK_LOG.md`：R-0042 保持 Open，但记录 P3-011 已完成 PM 验收。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-011 并启动 P3-012。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：工程修复、回归测试、evidence 更新完整；范围纪律较好。
- 主要问题：无阻塞问题；仍需独立复评防自证。
- 以后更适合分派给该 Agent 的任务类型：工程返工、P0 修复、回归测试、技术 Spike。
- 不建议分派给该 Agent 的任务类型：对自己刚完成工程的独立复评。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要。

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-012`：P3-011 P0 消费门返工独立工程复评
- 推荐执行 Agent：WorkBuddy
- 任务类型：独立工程复评 / 反例攻击
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No

P3-012 通过前，不得恢复 P3-009 工程基线候选，不得关闭 R-0042。
