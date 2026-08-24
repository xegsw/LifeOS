# LIFEOS-P3-041 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-041
- 任务名称：Active Authorization 子表变异整改隔离独立工程复评
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-041/independent_review.md`
- Evidence 路径：`lifeos/reviews/LIFEOS-P3-041/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-041_pm_review.md`
- 任务验收状态：Accepted / PM Adjusted to Rework
- 资产冻结状态：Rework / Not Frozen
- 是否允许进入下一任务：Conditional；用户确认采纳 Rework 后，只允许进入 P3-042 窄范围整改
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High，但结论分级和风险映射需 PM 校正
- 更新时间：2026-08-20

## PM 总结

- 独立评审确认 P3-031 为 42 PASS / 0 FAIL、P3-040 为 128 PASS / 0 FAIL；P3-039 五个原始 evidence hash 保持一致，已知 11 个 active 子表 P1 确实关闭。
- 评审新增 38 个相邻反例：19 PASS、19 个 bypass，其中 7 个 P1、12 个 P2。PM 在隔离临时副本复跑同一反例脚本，得到相同统计和预期退出码 1。
- 7 个 P1 证明 active Authorization 父表的 processor、purpose、location、grantor_ref、expires_mode、policy_version 及复合字段可被静默改写，generation 不变且无 audit；这直接削弱权限包络、缓存键和授权来源可信度。
- 依据 P3-041 任务卡判定标准，只要发现任何可复现 P0 / P1，最终结论必须为 Rework。因此 PM 不接受评审文件中的 `Pass with Conditions`，校正为 `Rework`。
- 评审对 R-0040 / R-0043 的映射不准确：R-0040 是真实 Tauri / IPC 能力风险，R-0043 是 Tombstone generation 风险，均不应因本次父 Authorization 字段旁路改变定义或关闭候选判断。
- R-0044 保持 Reopened；R-0046 的子表范围可进入 Closure Candidate 但不得关闭；新增 R-0047、R-0048、R-0049 分别跟踪父授权包络、证据 fence 和终态历史完整性。
- 本地预检再次调用但返回 502，按规则跳过；不影响 PM 人工复核和反例复跑。

## P3 快车道 Review

- 是否适用 P3 快车道：No。
- 原因：P0 优先级独立复评，涉及权限、证据链、风险状态和后续 P0 整改。
- 是否存在 P0：No。
- 是否存在 P1：Yes，7 个可复现 P1。
- 是否触发用户确认：Yes；独立评审 Rework 结论采纳必须用户确认。
- 是否允许继续下一工程补丁：仅在用户确认后允许创建 P3-042。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖隔离复跑、hash、已知 P1、相邻反例、版本链、合法路径和 evidence。
- 协审角色覆盖情况：已覆盖权限包络、audit / outbox、generation、terminal 历史和版本链。
- Gate 2：Pass with Conditions；hash 和回归一致，但历史证据可修改的 P2 未处置。
- Gate 3：Rework；发现 7 个 active Authorization 父表字段 P1。
- Gate 4：Rework；反例脚本稳定复现 P1，候选 SQL 尚不能作为完整权限边界输入。
- 是否属于关键冻结事项：No；但本结论明确阻止 Schema / API 冻结。
- 是否需要后续独立复评：Yes；P3-042 整改后必须创建 P3-043 隔离独立复评。

## 验收与冻结区分

- 任务是否完成：Yes，独立评审任务本身可验收。
- 评审最终结论：Rework。
- P3-040 对应候选资产是否冻结：No。
- 是否允许进入下一任务：Conditional；仅允许 P3-042 窄范围整改。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：No；当前不存在可冻结状态变化。

## PM 对发现的裁定

### 接受为 P1

- active 状态下直接修改 processor、purpose、location、grantor_ref、expires_mode、policy_version。
- 单次复合 UPDATE 同时修改多个安全字段。
- P3-042 不应只覆盖已经演示的 6 个单字段，还必须覆盖 `expires_at_ms`、`valid_from_ms` 等会改变有效期或授权解释的父表包络字段，并明确允许修改的非安全字段白名单。

### 接受为 P2 / 待设计处置

- audit_entry / outbox_job 可被删除或修改，以及预置证据可满足存在性检查。
- active generation 可脱离状态转换单独升高，并可与预置 evidence 组合。
- terminal Authorization 子表可继续 INSERT / UPDATE / DELETE，改变历史授权语义。

这些 P2 不应被直接表述为“Schema 冻结后由应用层补偿”。在 Schema 冻结前，必须明确责任归属、允许变更状态、审计合同和验证任务；否则不能冻结相关 Schema。

## 风险状态裁定

- R-0040：保持 Open / Conditional，原因仍是未验证真实 Tauri / IPC capability；本次 Authorization 父字段 P1 与其不直接对应。
- R-0043：保持 Reopened / Closure Candidate；本次未发现新的 Tombstone P1。
- R-0044：保持 Reopened，并将 active 父表安全字段可改写纳入关闭阻塞条件。
- R-0045：保持 Closed。
- R-0046：更新为 Open / Closure Candidate；P3-041 已独立确认已知 active 子表 11 个 P1 关闭，但关闭仍需单独风险决策和用户确认。
- R-0047：新增 P1 / Open，跟踪 active Authorization 父表安全字段静默改写。
- R-0048：新增 P2 / Open / Known Limitation，跟踪 audit / outbox 可变、预置证据和 generation 独立升高组合风险。
- R-0049：新增 P2 / Open / Known Limitation，跟踪 terminal Authorization 子表历史语义可被改写。

## 需要用户确认的事项

### 是否采纳 PM 校正后的 Rework 结论并启动 P3-042

- PM 建议：采纳。
- P3-042 范围：只修复 active Authorization 父表安全包络字段不可静默修改，补充必要负测、合法退休 / 新版本路径和 evidence；不要把 R-0048 / R-0049 的设计问题混入同一补丁。
- P3-042 完成后：必须启动 P3-043 隔离独立复评。
- 不确认的影响：P3-041 保持待确认 Rework，不能继续整改、风险关闭或 Schema 冻结。

## 对独立评审文件的质量判断

### 可接受

- 独立复跑、hash 核对和 P3-039 evidence 保留判断清楚。
- 反例攻击超出既有测试并稳定发现 7 个 P1、12 个 P2。
- 父表字段、证据 fence、generation 和 terminal 历史问题均提供了复现入口。

### 需要 PM 校正

- `Pass with Conditions` 与任务卡“出现任何 P0/P1 即 Rework”冲突。
- R-0040 / R-0043 与 Authorization 父字段风险的映射错误。
- 评审日期写为 2026-08-13，与实际任务日期 2026-08-20 不一致。
- 独立评审文件使用 `lifeos/reviews/LIFEOS-P3-041/independent_review.md`，与任务卡建议文件名不同；路径仍清晰可引用，本轮不要求重写。
- Manifest 未保存两套既有回归的完整独立日志，但 PM 已独立复跑并核对原 evidence；后续 P3-043 必须补齐独立复跑日志和退出码文件。

## Agent 分派与适配度评估

- 推荐 Agent：WorkBuddy。
- 实际 Agent：WorkBuddy。
- 匹配度：High。
- 主要优势：反例扩展能力强，连续发现执行测试之外的高风险攻击面，evidence 可复现。
- 主要问题：结论分级连续偏宽松；风险 ID 与原风险定义映射不严谨；日期与文件路径规范性不足。
- 后续适合：独立反例攻击、权限 / 删除 / 证据链复评。
- 不建议：由其直接决定最终严重级别、风险归属、风险关闭或冻结状态。
- 是否调整默认分派：No；继续由 PM 校正最终口径。

## 下一步任务建议

用户确认采纳后创建 P3-042：Active Authorization 父表安全包络字段不可变 P1 整改与回归。P3-042 应交给 Codex 工程整改会话，并按 D-0215 完整填写模型路由；本轮不创建、不启动。
