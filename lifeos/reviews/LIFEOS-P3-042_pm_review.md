# LIFEOS-P3-042 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-042
- 任务名称：Active Authorization 父表安全包络字段不可变 P1 整改与回归
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
- Evidence 路径：`lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-042_LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-042_pm_review.md`
- 任务验收状态：Accepted / Remediation Regression Passed
- 资产冻结状态：Accepted but Not Frozen / Pending Independent Re-review
- 是否允许进入下一任务：Conditional；用户确认采纳后只允许创建 P3-043 隔离独立工程复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-20

## PM 总结

- P3-042 在候选 SQLite Schema 中新增 `authorization_security_envelope_immutable_while_active`，用 NULL 安全的 `IS NOT` 比较保护 `grantor_ref`、`processor`、`purpose`、`location`、`valid_from_ms`、`expires_mode`、`expires_at_ms`、`policy_version` 八个字段。
- P3-041 的七个父 Authorization P1 已在 memory/file 双后端定向重放并全部 fail closed；有效期 NULL/配对、复合更新、多行原子回滚也通过，稳定错误码为 `active_authorization_security_envelope_immutable`。
- 合法 proposed/granted 配置、激活、active 退休、新版本 supersede/激活、no-op 与仅 `updated_at_ms` 更新未回退；更改授权含义必须创建新版本。
- PM 在隔离临时副本复跑 P3-042 总入口，退出码 0：P3-031 为 44 PASS / 0 FAIL，P3-040 为 128 PASS / 0 FAIL，P3-042 为 52 PASS / 26 个 P2 Known Limitation / 0 FAIL / 0 Not Implemented / 0 Unknown。
- 26 个 Known Limitation 是 13 个逻辑用例的 memory/file 双实例：R-0048 既有 7 个、R-0049 既有 4 个、新发现相邻元数据 2 个。历史 P3-041 的 `update_valid_from_active` 已被本任务纳入整改，因此原 12 个 P2 中当前仍属于 R-0048/R-0049 并可复现的是 11 个。
- `created_at_ms`、`revoked_at_ms` 在 active 状态仍可改写。当前证据只支持定为 P2 证据/生命周期元数据完整性问题，尚未证明可直接扩大 active 权限；PM 将其并入 R-0048 扩展范围，并要求 P3-043 攻击组合路径，若能升级为权限旁路则必须改判 Rework。
- P3-041 五个原始 evidence 文件哈希与既有期望完全一致；候选 SQL、测试、runner、结果和日志哈希与 P3-042 manifest 一致。
- 本地预检因局域网模型超时跳过，符合允许降级规则；不影响 PM 人工复核和隔离复跑。

## P3 快车道 Review

- 是否适用 P3 快车道：No。
- 原因：P0 优先级权限边界整改，必须用户确认并经隔离独立复评。
- 是否存在新增 P0：No。
- 是否存在未关闭的本任务 P1：当前执行证据中 No；最终仍待 P3-043 独立复评。
- 风险状态是否变化：R-0044、R-0047 可进入 Remediation Candidate / Pending Independent Re-review，但不得关闭；R-0048 扩展记录相邻元数据 P2；其他风险不关闭。
- 是否触发用户确认：Yes；P0 修复结论采纳必须用户确认。
- 是否允许继续下一工程补丁：No；只允许在用户确认后创建 P3-043 隔离独立复评。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖真实 SQLite trigger、八字段、NULL、复合/多行、合法路径、三套回归、hash 与 evidence。
- 协审角色覆盖情况：已覆盖授权含义、来源/有效期/策略版本、R-0048/R-0049 非范围、真实能力禁用与证据保留。
- Gate 2：Pass with Conditions；数据与来源证据一致，但 created/revoked 时间元数据及 R-0048/R-0049 仍开放。
- Gate 3：Pending Independent Re-review；执行证据显示八字段 P1 关闭，必须由 P3-043 独立反例攻击确认。
- Gate 4：Pending Independent Re-review；三套回归可复现，仍需隔离复评验证 trigger 顺序、相邻字段组合和合法生命周期。
- 是否属于关键冻结事项：No；但结果是 Schema 风险处理输入，不能直接冻结。
- 是否需要独立评审：Yes，P3-043。
- 独立评审路径：尚未创建。
- 是否允许进入下一任务或下一阶段：只允许用户确认后进入 P3-043；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：候选 Schema/API、SQL migration、Authorization 权限包络、工程基线及所有真实能力。
- 是否允许进入下一任务：Conditional；仅 P3-043。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：No；无冻结状态变化。

## 风险状态裁定

- R-0040：保持 Open / Conditional。
- R-0043：保持 Reopened / Closure Candidate。
- R-0044：保持 Reopened，更新为 Remediation Candidate / Pending Independent Re-review；P3-043 通过前不得关闭。
- R-0045：保持 Closed。
- R-0046：保持 Open / Closure Candidate。
- R-0047：保持 Open，更新为 Remediation Candidate / Pending Independent Re-review；P3-043 通过前不得关闭。
- R-0048：保持 P2 Open / Known Limitation，并扩展纳入 active `created_at_ms` / `revoked_at_ms` 可改写；P3-043 必须判断其与预置 evidence、generation、退休状态组合后是否仍只是 P2。
- R-0049：保持 P2 Open / Known Limitation。

## 需要用户确认的事项

### 是否采纳 P3-042 并创建 P3-043 隔离独立工程复评

- PM 建议：采纳。
- 理由：任务范围、模型路由、SQL 补丁、三套回归、hash 与 evidence 均满足任务卡；当前未发现新增 P0/P1，但 P0 权限整改不能由执行 Agent 自证结束。
- P3-043 重点：独立复跑 44/128/P3-042；重放八字段、NULL/复合/多行攻击；扩展 active→terminal、同事务、trigger 顺序、`created_at_ms`/`revoked_at_ms` 与 R-0048 组合攻击；确认无 P0/P1 后才可讨论后续风险关闭评估。
- 不确认的影响：P3-042 保持 Accepted but Not Frozen，P3-043 不创建，R-0044/R-0047 不得关闭，Schema/API 不得冻结。

## 可接受内容

- 八字段安全包络不可变 trigger 与稳定错误码。
- P3-041 七个 P1 的双后端关闭证据。
- P3-031 44/44、P3-040 128/128、P3-042 52 PASS 的隔离可复跑结果。
- 对 P3-041 历史 P2 数量与当前行为数量的事实校正。
- 对 R-0048/R-0049 及相邻 P2 的诚实保留和不可外推声明。

## 不接受或需谨慎内容

- 不把执行回归通过解释为 P3-042 已独立通过、风险关闭或 Schema/API 冻结。
- 不把 26 个 Known Limitation 解释为 26 个不同风险；它们是 13 个逻辑用例的双后端实例。
- 不把 `created_at_ms`/`revoked_at_ms` 直接降格为无影响元数据；P3-043 必须验证组合攻击，Schema 冻结前必须有明确处置。
- 不外推到真实 DB、真实旧库、真实 Vault/文件、Tauri/IPC、并发、性能、跨平台或生产 SLA。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex。
- 是否符合推荐：Yes。
- 匹配度：High。
- 主要优势：严格遵守 `gpt-5.6-sol` + `xhigh`；SQL trigger、回归、隔离复跑、hash 与 evidence 完整；主动披露相邻 P2，没有用全绿掩盖非范围风险。
- 主要问题：无阻塞性问题；相邻元数据最终严重级别仍需独立复评，不由执行 Agent 决定。
- 后续适合：P0/P1 SQLite 权限整改、合同测试、evidence 整理。
- 不建议：独立复评自己的 P3-042 结果或自行关闭风险。
- 是否调整默认分派：No。

## 下一步任务建议

用户确认采纳后创建 P3-043：Active Authorization 父表安全包络整改隔离独立工程复评。推荐交给 WorkBuddy 新建隔离会话；模型路由字段按外部 Agent 规则全部填写 `N/A`。本轮不创建、不启动 P3-043。
