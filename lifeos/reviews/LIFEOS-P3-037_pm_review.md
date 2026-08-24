# LIFEOS-P3-037｜PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-037
- 任务名称：受控文件型 SQLite migration / 残留 P2 验证执行任务
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`
- Evidence Manifest 路径：`lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-037_pm_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-037_LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation_local_precheck.md`
- 任务验收状态：Accepted
- 验证结果状态：Validation Failed / Rework Required
- 资产冻结状态：Accepted but Not Frozen / Rework Input
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-037 按任务卡完成受控文件型 SQLite + 合成 fixture 验证，交付物、evidence manifest、结构化结果、脚本和本地预检路径齐全。
- PM 在临时副本复跑 `lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh`，稳定复现退出码 `1`，统计为 7 PASS / 3 FAIL / 0 Not Implemented / 0 Unknown；P0 0 FAIL，P1 3 FAIL。
- P3-037 的任务本身可验收，因为它准确揭示了候选 SQL 的失败证据；但验证结果不通过，不能进入“通过结果确认型”的独立评审，也不能作为真实 DB / Schema / API 更高层输入。
- P2-2 已升级为 P1 失败：普通 DELETE、`INSERT OR REPLACE`、显式 DELETE+INSERT commit 均可让 tombstone 消失或 generation 从 5 降到 4，六类合成消费门由 DENY 变为 ALLOW。
- P2-3 已升级为 P1 失败：`active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 四种非 `accepted` 初始 tombstone 状态均可直接 INSERT。
- P2-4 已升级为 P1 失败：active Authorization 的 scope/action/policy 子行可直接 DELETE；运行时重检仍 DENY / AMBIGUOUS，没有观察到权限放宽，但父状态仍 active、generation 不变、无新增 audit，不满足 P3-036 的审计 / generation fencing 合同。
- R-0043 的关闭失效条件已触发，应由 PM 重新打开；R-0044 暂不重新打开，因为 P2-4 没有破坏 runtime fail-closed，但必须新增单独风险跟踪 Authorization 子表 DELETE 的 audit / generation fencing 缺口；R-0045 不受本任务新增影响。
- 本任务未触碰真实用户 DB、真实 Vault、真实用户文件、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户；不冻结任何资产，不关闭 R-0040。

## P3 快车道 Review（适用时）

- 是否适用 P3 快车道：No
- 验收结论：不适用。P3-037 是 P0 工程验证执行任务，不是 P1 / P2 快车道工程补丁。
- 测试复跑摘要：PM 临时副本复跑通过复现任务结果：退出码 `1`；P0 2 PASS / 0 FAIL；P1 5 PASS / 3 FAIL；P2 0；总计 7 PASS / 3 FAIL。
- 是否存在 P0：未发现。
- P1 / P2 是否可留在快车道：No。三个 P1 必须走整改与后续独立评审。
- 风险状态是否变化：Yes。R-0043 应重新打开；新增 R-0046 跟踪 Authorization active 子表 DELETE 的 audit / generation fencing 缺口。R-0040 保持 Open / Conditional；R-0044 / R-0045 保持 Closed。
- 是否触发用户确认：Yes。是否采纳 P3-037 验收结论并启动 P3-038 候选 SQL 整改任务，需要用户确认。
- 是否允许继续下一工程补丁：Conditional。只能在用户确认后创建窄范围候选 SQL 整改任务。
- 修改文件：PM Review 与 PM 账本；不修改 P3-031 / P3-037 工程 evidence。
- evidence 路径：`lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
- Agent 适配度记录：Codex 适合此类验证执行；失败发现被准确报告，没有掩盖成通过。
- 是否必须退出快车道：Yes，本任务本身不适用快车道，且发现 P1。

## PM 复核证据

- 本地预检：Completed / 需要人工复核。预检要求 PM 重点复核三个 P1、风险失效条件、SQL 整改与独立评审安排；PM 已完成定向复核。
- PM 临时副本复跑：
  - 复跑方式：复制 `LIFEOS-P3-031` 与 `LIFEOS-P3-037` 到 `/tmp/lifeos-p3-037-pm-*` 后运行 P3-037 验证脚本。
  - 复跑命令：`lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh`
  - 复跑结果：退出码 `1`；7 PASS / 3 FAIL；P0=0 FAIL，P1=3 FAIL。
- 关键 evidence：
  - `lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/path_isolation.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/integrity_and_fk.json`

## 角色与关卡验收

- 主责角色覆盖情况：通过。交付物覆盖文件型 SQLite 隔离、hash、合成 fixture、P2-2 / P2-3 / P2-4 逐项验证、退出码合同、evidence 和后续建议。
- 协审角色覆盖情况：通过。
  - 数据 / 领域模型：明确 tombstone generation、tombstone 状态、Authorization 子表、audit、generation 与消费门语义。
  - AI 信任与安全：明确删除不复活、授权 fail-closed、真实数据 / Vault / Tauri / IPC 不触碰。
  - QA / Evidence：提供结构化 JSON、MANIFEST、hash、环境、rollback、restore、integrity / FK 和复跑入口。
- 已通过关卡：
  - Gate 4 技术可行性评审：验证执行能力、路径隔离和 evidence 结构通过。
- 未通过或需后续确认关卡：
  - Gate 2 数据与来源评审：Not Passed / Rework Required。Tombstone 删除 / 降代与伪终态 INSERT 旁路成立。
  - Gate 3 AI 权限与信任评审：Not Passed / Rework Required。删除 / 撤回消费门在 P2-2 反例中放行；P2-4 runtime fail-closed 但审计 / generation fencing 不完整。
- 是否属于关键冻结事项：No
- 是否需要独立评审：后续整改通过后需要；当前失败结果不建议做“通过确认型”独立评审。
- 独立评审路径：不适用
- 独立评审结论：不适用
- 是否允许进入下一任务或下一阶段：允许进入整改任务需用户确认；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted；这是对“验证任务完成且证据可信”的验收。
- 验证结果是否通过：No，Validation Failed。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA、工程基线、真实 DB 验证结果、真实 Tauri / IPC、R-0040。
- 是否允许进入下一任务：Conditional。用户确认后，可创建 `LIFEOS-P3-038` 候选 SQL 残留 P1 整改任务。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes，作为整改输入。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 是否采纳 P3-037？
   - PM 建议：采纳。这里的“采纳”不是采纳验证通过，而是采纳 P3-037 的失败证据和 PM 的风险判断。
   - 可选方向：采纳 / 要求复跑或返工 P3-037。
   - 不确认的影响：无法进入候选 SQL 整改。

2. 是否启动 P3-038 候选 SQL 残留 P1 整改任务？
   - PM 建议：启动。
   - 建议边界：仅允许修改 P3-031 候选 SQL 的 P3-038 隔离副本或明确授权的候选 SQL 文件、补充 P2-2 / P2-3 / P2-4 对应合同测试、更新 P3-037 类验证脚本 / evidence；不得触碰真实用户 DB / Vault / Tauri / IPC。
   - 不确认的影响：R-0043 保持 Reopened，R-0046 保持 Open，SQL migration 线不能继续向真实 DB / Schema / API 后续推进。

3. 是否接受 PM 对风险状态的处理？
   - PM 建议：R-0043 重新打开；R-0044 暂不重开但新增 R-0046；R-0045 保持 Closed；R-0040 保持 Open / Conditional。
   - 不确认的影响：风险账本与验证事实会产生滞后。

## 整改建议

建议启动 `LIFEOS-P3-038`，整改范围最小包括：

- Tombstone 表禁止直接 DELETE / `INSERT OR REPLACE` / 降代重建，或实现受控维护事务的等价强不变量。
- Tombstone 初始 INSERT 仅允许 `accepted`；`active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 等终态 / 中间态必须经合法转换和证明进入。
- Authorization active 子表 DELETE 必须 DB 拒绝，或受控事务内父授权降级 / 撤销、generation 递增、audit / outbox 追加、消费门 fail-closed。
- 补充对应合成空库合同测试与文件型 SQLite 验证。
- 整改完成后必须由隔离独立工程评审会话复核。

## 可接受内容

- P3-037 的验证框架、路径隔离、合成 fixture、hash 口径、backup / restore、rollback、integrity / FK 证据。
- 7 PASS / 3 FAIL 的结果统计和非零退出合同。
- P2-2 / P2-3 / P2-4 从残留 P2 升级为当前文件型 DB P1 失败的判定。
- “bootstrap candidate 不等于真实用户 DB migration / 非空旧库 upgrade”的不可外推声明。

## 不接受或需谨慎内容

- 不得把 P3-037 解释为验证通过。
- 不得进入真实用户 DB、真实 Vault、真实 Tauri / IPC 或更高层 Schema / API 推进。
- 不得关闭 R-0040。
- 不得冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不得把 R-0043 继续视为稳定关闭。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不需要。
- `lifeos/PM_OPERATING_MODEL.md`：不需要。
- `lifeos/TASK_REGISTRY.md`：更新 P3-037 为 Accepted / Validation Failed。
- `lifeos/DECISION_LOG.md`：新增 PM 验收决策。
- `lifeos/RISK_LOG.md`：R-0043 重新打开；新增 R-0046。
- `lifeos/FREEZE_STATUS.md`：更新 P3-037 状态。
- `lifeos/CURRENT_STATUS.md`：更新当前等待用户确认和下一步建议。
- `lifeos/OPEN_QUESTIONS.md`：不需要。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：能完成受控脚本、复跑、evidence 和失败归因；没有把失败包装成通过。
- 主要问题：无必须返工问题。
- 以后更适合分派给该 Agent 的任务类型：候选 SQL 整改、受控 SQLite 验证、evidence 生成、回归测试。
- 不建议分派给该 Agent 的任务类型：独立评审自己刚完成的整改或验证。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要。

## 下一步任务建议

PM 建议用户确认后启动：

- `LIFEOS-P3-038`：候选 SQL 残留 P1 整改与回归任务。

推荐执行 Agent：Codex 工程整改会话。  
后续必须再启动隔离独立工程复评会话，不能由 P3-038 执行会话自评通过。
