# LIFEOS-P3-010 PM Review｜目标技术栈最小工程骨架独立工程评审

## 验收信息

- 任务 ID：LIFEOS-P3-010
- 任务名称：目标技术栈最小工程骨架独立工程评审
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-010_pm_review.md`
- 任务验收状态：Accepted
- 独立评审结论：Rework
- 资产冻结状态：Not Applicable；P3-009 更新为 Rework
- 是否允许进入下一任务：Conditional，需用户确认是否采纳 Rework 并启动 P3-011
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High
- 更新时间：2026-08-11

## PM 总结

1. P3-010 按任务卡完成独立工程评审，未修改 P3-009 / P3-001 工程文件、项目账本、Stitch 或冻结资产。
2. 独立评审只读复跑 P3-009 测试为 10 PASS / 0 FAIL，并核对 evidence manifest、test results、test log 与文件 hash 一致。
3. 独立评审发现 1 项 P0：P3-009 的 `canConsume()` 只检查 `allow` 数量，不检查 `deny`；allow+deny 冲突时仍放行。
4. PM 复现该 P0：插入 deny 授权后，`read()` 仍返回用户原文，确认问题真实存在。
5. P3-010 另识别 8 项 P1，其中 `suggest()` 的 `INSERT OR REPLACE` 丢失确认状态与 feedback / derivation / generation / restore / link 等历史测试迁移缺口需要后续处理。
6. 本地预检已调用，但局域网模型连接重置，状态为 Skipped / Local Model Unavailable；不作为 PM 验收依据。
7. PM 结论：P3-010 任务 Accepted；P3-009 回退为 Rework，不能作为后续工程基线候选；R-0040 保持 Open / Conditional；新增 R-0042。

## 角色与关卡验收

- 主责角色覆盖情况：独立工程评审负责人覆盖充分；完成只读复跑、P3-001→P3-009 覆盖差异检查、反例攻击和 Rework 判断。
- 协审角色覆盖情况：
  - 技术架构负责人：覆盖；指出 `node:sqlite` experimental warning 不构成生产依赖冻结依据，R-0040 必须保持 Open / Conditional。
  - 数据与权限负责人：覆盖；发现 deny 授权未进入消费门判定，违反 H4 fail closed。
  - QA / 测试负责人：覆盖；指出 P3-009 10 个聚合测试覆盖不足，不能替代 P3-001 的 23 项历史测试 / 136 条断言。
  - AI 信任与安全负责人：覆盖；指出 `INSERT OR REPLACE` 会静默重置候选确认状态。
- 已通过关卡：只读复跑 / evidence 一致性检查、默认关闭能力检查、边界纪律检查。
- 未通过或需后续确认关卡：P0 反例攻击未通过；Gate 2 数据与来源、Gate 3 AI 信任与安全为 Rework。
- 是否属于关键冻结事项：否；但影响 P3-009 是否可作为工程基线候选。
- 是否需要独立评审：本任务自身为独立评审，已完成。
- 是否允许进入下一任务或下一阶段：仅允许用户确认后进入 P3-011 P0 返工；不允许进入下一阶段。

## PM 复核记录

### PM 复现 P0

PM 使用 bundled Node v24.14.0 在 P3-009 内存库中复现：

1. 创建 artifact 与默认 allow 授权。
2. 插入同 subject / purpose / location / processor / generation 的 deny 授权。
3. 调用 `read(ctx)`。
4. 实际结果：返回用户原文；期望结果：fail closed 返回 `null`。

该行为确认 P3-010 的 AD-1 P0 成立。

### 本地预检

- 预检路径：`lifeos/local_prechecks/LIFEOS-P3-010_LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review_local_precheck.md`
- 预检状态：Skipped / Local Model Unavailable
- 错误：`[Errno 54] Connection reset by peer`
- PM 判断：允许跳过；不影响 PM 复核。

## 验收与冻结区分

- 任务是否验收通过：Yes，P3-010 作为独立评审任务 Accepted。
- 对应资产是否冻结：No。
- P3-009 是否仍可作为工程基线候选：No，回退 Rework。
- 冻结范围：无。
- 未冻结内容：P3-009 工程基线、生产 Schema、API、模块边界、Tauri 配置、真实数据、真实 Vault、真实 IPC、导出格式、同步、多设备、云 / 第三方模型、L3、生产 SLA。
- 是否允许进入下一任务：Conditional；用户确认采纳 Rework 后，可启动 P3-011 P0 返工。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-010 的 Rework 结论，并启动 P3-011？
   - PM 建议：采纳，并启动 P3-011。
   - 可选方向：A. 采纳并启动 P3-011；B. 要求重新评审 P3-010；C. 暂停工程线。
   - 不确认的影响：P3-009 保持 Rework，不能继续作为工程基线候选；工程线暂停在当前节点。
2. 问题：P3-011 是否只修 P0，还是顺手纳入 P1-1 / P1-2？
   - PM 建议：P3-011 以 P0 为必须项，同时允许修复 P1-1 / P1-2，因为它们同属消费门 / 写入口状态保持，范围仍可控。
   - 可选方向：A. 只修 P0；B. 修 P0 + P1-1 / P1-2；C. 扩展修复全部 P1。
   - 不确认的影响：范围不清会导致 P3-011 过窄或过大。

## 整改建议

P3-011 建议范围：

- 修复 `canConsume()` 中 deny 授权未检查的问题。
- 新增 allow+deny 冲突反例测试，P0 必须失败转 PASS。
- 回归 P3-009 现有 10 项测试，保持 0 FAIL。
- 建议同时修复：
  - `suggest()` 使用 `INSERT OR REPLACE` 导致确认状态丢失。
  - `feedback()` 不显式检查 derivation status。
- P1-3 至 P1-8 暂登记为后续迁移清单，不在 P3-011 中一次性扩散。

## 可接受内容

- P3-010 的独立评审方法有效，能发现 P3-009 自测未覆盖的关键 P0。
- P3-009 的模块化方向、默认关闭能力和 evidence 自动生成机制仍可保留为返工基础。
- P3-001 仍保持此前恢复的合成工程基线候选地位；P3-009 不得替代它。

## 不接受或需谨慎内容

- 不接受 P3-009 继续作为后续工程基线候选。
- 不接受关闭 R-0040。
- 不接受把 P3-009 的 10 PASS 外推为 P3-001 历史 136 条断言已迁移完成。
- 不接受在 P3-011 前继续扩展真实 Tauri / IPC、真实 Vault、真实数据或外部能力。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：P3-010 更新为 Accepted；P3-009 更新为 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-009 更新为 Rework；P3-010 更新为 Accepted / Rework conclusion。
- `lifeos/DECISION_LOG.md`：新增 D-0152。
- `lifeos/RISK_LOG.md`：新增 R-0042。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-010 Rework 并启动 P3-011。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：反例攻击有效；能够识别 P3-009 自测中的关键消费门漏洞和覆盖弱化。
- 主要问题：本地预检未成功，但不影响任务质量。
- 以后更适合分派给该 Agent 的任务类型：独立评审、反例攻击、工程复评、风险复核。
- 不建议分派给该 Agent 的任务类型：大规模工程修复。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要。

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-011`：P3-009 P0 消费门返工与回归补测
- 推荐执行 Agent：Codex
- 任务类型：工程返工 / P0 修复 / 回归测试
- 是否允许修改工程文件：Yes，仅限 P3-009 返工范围
- 是否允许修改项目账本：No

P3-011 完成后仍需独立复评；复评通过前，P3-009 不得恢复为工程基线候选。
