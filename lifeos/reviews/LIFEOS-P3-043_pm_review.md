# LIFEOS-P3-043 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-043
- 任务名称：Active Authorization 父表安全包络整改隔离独立工程复评
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-043/independent_review.md`
- Evidence 路径：`lifeos/reviews/LIFEOS-P3-043/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-043_independent_review_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-043_pm_review.md`
- 任务验收状态：Accepted / PM Adjusted to Rework
- 资产冻结状态：Rework / Not Frozen
- 是否允许进入下一任务：Conditional；用户确认采纳 Rework 后，只允许创建 P3-044 窄范围整改
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High（反例发现）/ Medium（最终判定与 evidence 完整性）
- 更新时间：2026-08-20

## PM 总结

- 独立评审确认 P3-031 44 PASS、P3-040 128 PASS、P3-042 52 PASS + 26 个 P2 Known Limitation，既有整改和 P3-041 七个父表 P1均能复现为已关闭。
- 新增 46 个攻击：34 PASS、12 BYPASS，其中 1 个 P1、10 个 P2、1 个 P3 观察。结构化结果、反例脚本和 manifest 统计一致。
- 新 P1 为 FK ON 下的 `INSERT OR REPLACE ... status='granted'`：SQLite 通过替换写路径绕过只覆盖 UPDATE 的安全包络 trigger，使 active 授权变为 granted 且改写 processor/其他父字段，三类子表仍保留，随后可无 audit/outbox 地重新激活。
- PM 在隔离临时副本独立复现：替换后状态为 `granted`、processor 为 `evil-replace`、scope/action/policy 子行均保留；再次 `UPDATE status='active'` 成功，generation 仍为 1，audit=0、outbox=0。PM 另行变体确认 `policy_version='policy-evil'` 同样可被替换并重新激活。
- 根据 P3-043 任务卡，发现任何可复现 P0/P1 必须判定 `Rework`。因此 PM 不接受评审正文与 manifest 的 `Pass with Conditions`，统一校正为 `Rework`。
- R-0048 的 created/revoked/generation/audit/outbox 组合目前未证明升级为直接 active 权限旁路，维持 P2；terminal 父表包络可变并入 R-0049 历史语义风险。
- 独立 evidence 未保存三套回归的完整日志/退出码文件，且正文把 P3-031 contract tests hash 写成 `b8ee...4d78`，实际该值属于 P3-040 runner，P3-031 tests 当前 hash 为 `e934...d275`。这些是 P2 evidence/文档缺口，不影响 PM 对新 P1 的复现，但后续 P3-045 必须补齐。
- P1 基础反例脚本实际直接证明 processor 改写；正文中的 policy_version 示例属于扩展描述。PM 已用最小变体独立确认 policy_version 同样可替换，因此核心 P1 结论成立。
- 本地预检因 HTTP 502 跳过，符合允许跳过规则；不影响 PM 人工复核和反例复现。

## P3 快车道 Review

- 是否适用 P3 快车道：No。
- 原因：P0 权限整改独立复评，发现新的 P1。
- 是否存在 P0：No。
- 是否存在 P1：Yes，1 个可复现父记录替换旁路。
- 是否触发用户确认：Yes；独立评审 Rework 结论必须用户确认。
- 是否允许继续下一工程补丁：仅在用户确认后允许创建 P3-044。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖隔离复跑声明、八字段、SQL 写法、PRAGMA/trigger、R-0048 组合和合法路径；新 P1 有可运行反例。
- 协审角色覆盖情况：已覆盖 active 权限扩写、历史包络、证据链、generation、合法生命周期和不可外推边界。
- Gate 2：Pass with Conditions；核心 hash 与攻击 evidence 可核对，但三套回归独立日志缺失、contract tests hash 表述错误，R-0048/R-0049 仍开放。
- Gate 3：Rework；`INSERT OR REPLACE` 可无审计替换 active 授权包络并重新激活。
- Gate 4：Rework；候选 trigger 只覆盖 UPDATE，未覆盖 SQLite 替换写语义。
- 是否属于关键冻结事项：No；但本结论阻止 Schema/API 冻结。
- 是否需要后续独立复评：Yes；P3-044 整改后必须创建 P3-045 隔离独立复评。
- 是否允许进入下一任务或下一阶段：用户确认后仅允许 P3-044；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否完成：Yes，独立评审任务本身可验收。
- 评审最终结论：Rework。
- P3-042 对应候选资产是否冻结：No。
- 是否允许进入下一任务：Conditional；仅 P3-044。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：No；无可冻结状态变化。

## PM 对发现的裁定

### 接受为 P1

- FK ON、全部当前 trigger 生效时，`INSERT OR REPLACE` 可把已有 active Authorization 替换为 granted，改变父表安全包络，保留既有 scope/action/policy，再重新激活。
- 该路径不需要先关闭 foreign_keys，不产生 retirement audit/outbox，不提升 generation，属于真实候选 DB 权限边界旁路。
- 新增 R-0050 专项跟踪父 Authorization 替换/重建写路径绕过。

### 接受为 P2

- active `created_at_ms`、`revoked_at_ms`、generation 和预置/可变 audit/outbox 的组合路径继续归 R-0048；当前反例未证明直接改变 active 权限消费结果。
- revoked/expired/superseded 状态的父包络字段可变，扩展归入 R-0049 历史授权语义完整性风险。
- FK OFF 的父记录重建路径依赖违反当前候选连接合同，暂按 P2 配置/写者边界记录；P3-044 仍应尽可能 fail closed，P3-045 必须复核。

## 风险状态裁定

- R-0040：保持 Open / Conditional。
- R-0043：保持 Reopened / Closure Candidate。
- R-0044：从 Remediation Candidate 退回 Reopened / Rework；新父记录替换 P1 触发失效条件。
- R-0045：保持 Closed。
- R-0046：保持 Open / Closure Candidate。
- R-0047：从 Remediation Candidate 退回 Open / Rework；八字段 UPDATE 旁路已关闭，但替换写路径仍能改变同一安全包络。
- R-0048：保持 P2 Open / Known Limitation；组合攻击目前不升级。
- R-0049：保持 P2 Open / Known Limitation，并扩展纳入 terminal 父表包络可变。
- R-0050：新增 P1 Open，跟踪 `INSERT OR REPLACE`/父记录替换重建绕过 active 包络保护。

## 需要用户确认的事项

### 是否采纳 PM 校正后的 Rework 并创建 P3-044

- PM 建议：采纳。
- P3-044 建议范围：只关闭已有 active Authorization 的 `INSERT OR REPLACE`、替换式 INSERT 和直接 DELETE/重建旁路；覆盖 FK ON/OFF、recursive_triggers、granted/proposed/active 替换、子表保留、重新激活和合法退休/新版本路径。
- P3-044 非范围：不同时修复 R-0048 的证据/generation/时间元数据 P2，也不处理 R-0049 的 terminal 父子历史不可变；避免 P0 修复与尚未完成设计决策的 P2 混杂。
- P3-044 完成后：必须创建 P3-045 隔离独立复评，并补齐三套回归日志、退出码和准确 hash。
- 不确认的影响：P3-043 保持待确认 Rework，R-0044/R-0047/R-0050 保持阻塞，Schema/API 不得冻结。

## 对独立评审质量的判断

### 可接受

- 主动覆盖 REPLACE/UPSERT/DELETE+INSERT/PRAGMA/trigger 和 R-0048 组合攻击。
- 新 P1 可稳定复现，直接命中任务目标之外的 SQLite 写语义缺口。
- P2 组合路径未被无依据升级，合法路径与不可外推边界清楚。

### 需要 PM 校正

- 存在 P1 却给出 `Pass with Conditions`，违反任务卡硬判定规则；最终必须为 Rework。
- 独立 evidence 缺少三套回归原始日志、退出码和 preservation 文件，只在正文/manifest 声明结果。
- P3-031 contract tests hash 映射错误；P3-040 runner hash 被写到 contract tests 行。
- 基础 P1 脚本只直接改写 processor，正文描述 policy_version 同时被改写缺少同一原始用例支撑；PM 变体已补证，但 P3-045 应直接纳入攻击脚本。

## Agent 分派与适配度评估

- 推荐 Agent：WorkBuddy。
- 实际 Agent：WorkBuddy。
- 匹配度：High（反例能力）/ Medium（最终分级与 evidence 规范）。
- 主要优势：连续发现现有测试之外的 SQLite 权限旁路，攻击面扩展能力强。
- 主要问题：再次将存在 P1 的结果写成 Pass with Conditions；hash 映射和独立回归 evidence 完整性不足。
- 后续适合：隔离反例攻击、权限/删除/证据链复评。
- 不建议：由其独立决定最终严重级别、风险关闭或冻结结论；PM 必须按任务卡硬门校正。
- 是否调整默认分派：No；保留其反例发现角色，但后续任务卡继续使用明确的硬判定标准。

## 下一步任务建议

用户确认采纳后创建 P3-044：Active Authorization 父记录替换/重建旁路 P1 整改与回归。推荐交给 Codex 工程整改会话，按模型路由规则使用高风险配置；本轮不创建、不启动 P3-044。
