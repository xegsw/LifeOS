# LIFEOS-P3-036｜PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-036
- 任务名称：真实 DB migration 前置验证清单
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-036_real_db_migration_preflight_checklist.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-036_pm_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-036_LIFEOS-P3-036_real_db_migration_preflight_checklist_local_precheck.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Planning Input
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-036 已按任务卡完成“真实 DB migration 前置验证清单”，覆盖 P2-2、P2-3、P2-4 的验证目的、输入前置、最小反例、PASS / FAIL、证据要求和停止规则。
- 交付物明确区分候选 SQL、合成空库、文件型临时测试 DB、结构化升级 fixture、真实用户 DB、真实 Vault / 文件能力，避免把“未来文件型验证”误写成真实用户数据库验证。
- 交付物明确本任务没有执行 SQL、没有创建或连接数据库、没有修改工程代码 / 候选 SQL / evidence / PM 账本，符合任务授权边界。
- 对 P2-2 / P2-3 / P2-4 的验证要求足够硬：包含事务、rollback、hash、消费门、audit、strict_intersection、缓存 / 队列重检与 fail-closed 口径，可作为后续受控执行任务输入。
- 对非空旧库 upgrade 的提醒是必要的：当前 `001_candidate_schema.sql` 只能视为 bootstrap / 空库候选，不能直接外推为任意旧版本升级 migration。
- P3-036 不关闭 R-0040，不改变 R-0043 / R-0044 / R-0045 的既有状态，不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 本地预检因本地模型连接重置跳过，不作为验收依据；PM 已按任务卡、交付物和相关账本独立验收。

## P3 快车道 Review（适用时）

- 是否适用 P3 快车道：No
- 验收结论：不适用。P3-036 是 P0 技术验证前置 / 决策输入任务，不是 P1 / P2 工程补丁。
- 测试复跑摘要：未复跑；本任务不授权执行真实 DB、SQL migration 或工程测试。
- 是否存在 P0：未发现。
- P1 / P2 是否可留在快车道：不适用。
- 风险状态是否变化：无。R-0040 保持 Open / Conditional；R-0043 / R-0044 / R-0045 保持 Closed 且关闭范围不扩大。
- 是否触发用户确认：Yes。是否采纳 P3-036，并是否启动后续受控文件型 SQLite 验证执行任务，需要用户确认。
- 是否允许继续下一工程补丁：No。本任务建议的是后续验证执行任务，不是快车道工程补丁。
- 修改文件：PM Review 和 PM 账本。
- evidence 路径：本任务无新工程 evidence；本地预检见上方路径。
- Agent 适配度记录：Codex 适合此类技术验证清单与 evidence 结构设计。
- 是否必须退出快车道：不适用。

## 角色与关卡验收

- 主责角色覆盖情况：通过。技术架构负责人视角下，交付物定义了真实 DB 验证前置边界、硬准入、命令边界、evidence 结构、停止规则和后续任务边界。
- 协审角色覆盖情况：通过。
  - 数据 / 领域模型：覆盖 tombstone、Authorization、source / identity、generation、audit、restore / recovery 相关语义。
  - AI 信任与安全：覆盖删除不复活、授权 fail-closed、真实数据 / Vault / Tauri / IPC 不触碰、不可外推边界。
  - QA / Evidence：覆盖 MANIFEST、hash、环境、before/after integrity、rollback、恢复演练、P0/P1/P2 判定。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass with Conditions（清单层）
  - Gate 3 AI 权限与信任评审：Pass with Conditions（清单层）
  - Gate 4 技术可行性评审：Pass with Conditions（规划层）
- 未通过或需后续确认关卡：
  - 真实文件型 SQLite 执行结果尚未产生。
  - 非空旧库 upgrade version matrix 尚未定义。
  - 真实 Tauri / IPC、真实 Vault、真实用户 DB 仍未验证。
- 是否属于关键冻结事项：No
- 是否需要独立评审：本任务本身不需要；后续若执行真实 DB migration、关闭 R-0040、冻结 Schema / API 或进入下一阶段，必须另行独立评审。
- 独立评审路径：不适用
- 独立评审结论：不适用
- 是否允许进入下一任务或下一阶段：允许进入下一任务需用户确认；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA、工程基线、真实 DB 验证结果、真实 Tauri / IPC、R-0040。
- 是否允许进入下一任务：Conditional。用户确认采纳后，可创建受控文件型 SQLite migration / 残留 P2 验证执行任务。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，更新 P3-036 为 Accepted but Not Frozen / Planning Input。

## 需要用户确认的事项

1. 是否采纳 P3-036？
   - PM 建议：采纳。
   - 可选方向：采纳 / 要求返工。
   - 不确认的影响：无法把 P3-036 作为后续真实 DB 验证执行任务输入。

2. 是否启动下一任务：受控文件型 SQLite migration / 残留 P2 验证执行任务？
   - PM 建议：启动，但边界必须限定为新建隔离目录、合成无敏感 fixture、只读 source、可丢弃工作副本、P2-2 / P2-3 / P2-4 反例、backup / restore、integrity / FK、完整 evidence；仍不得触碰真实用户 DB / Vault / Tauri / IPC。
   - 可选方向：A. 直接启动受控文件型 SQLite 验证；B. 若想验证非空旧库 upgrade，先创建 upgrade version matrix / 转换设计任务；C. 暂停 DB 线，转去 Tauri / IPC 前置线。
   - 不确认的影响：P3-036 停留为 planning input，不进入可执行验证。

3. 是否接受 P3-036 的推荐目标合同？
   - PM 建议：接受其方向作为后续任务输入，即 P2-2 / P2-3 优先 DB 直接拒绝；P2-4 优先 DB 拒绝，若允许受控变更，必须父授权降级 / 撤销 + generation + audit + 消费门 fail-closed。
   - 可选方向：接受 / 要求下一任务同时比较“DB 直接拒绝”与“受控维护例外”两种方案。
   - 不确认的影响：后续执行任务的 PASS / FAIL 口径会不够硬。

## 整改建议

无必须返工项。

可选增强项：如果用户选择后续验证“非空旧库 upgrade”，应先创建单独的 version matrix / 转换设计任务，避免把 bootstrap 候选 SQL 当成升级 migration。

## 可接受内容

- P2-2 / P2-3 / P2-4 的验证清单、最小反例、PASS / FAIL、证据要求和停止规则。
- 文件型 SQLite 验证的隔离边界：合成 fixture、只读 source、临时工作副本、无真实用户数据。
- evidence 结构：MANIFEST、environment、input、migration、checks、results。
- P0 / P1 / P2 严重级别判定。
- “bootstrap 不等于 upgrade migration”的约束。
- 不可外推声明。

## 不接受或需谨慎内容

- 不得把 P3-036 解释为真实 DB migration 已执行。
- 不得把未来文件型 SQLite 验证解释为真实用户 DB 验证。
- 不得把 P3-036 解释为 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线冻结。
- 不得把 P3-036 解释为 R-0040 关闭依据。
- 不得直接进入下一阶段或正式 MVP 准入。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不需要。
- `lifeos/PM_OPERATING_MODEL.md`：不需要。
- `lifeos/TASK_REGISTRY.md`：需要将 P3-036 更新为 Accepted。
- `lifeos/DECISION_LOG.md`：需要新增 PM 验收决策。
- `lifeos/RISK_LOG.md`：不需要。
- `lifeos/FREEZE_STATUS.md`：需要更新 P3-036 状态。
- `lifeos/CURRENT_STATUS.md`：需要更新当前等待用户确认和下一步建议。
- `lifeos/OPEN_QUESTIONS.md`：不需要。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：技术边界、验证清单、evidence 结构、失败停止规则表达清晰，且没有越权执行真实 DB 或修改工程。
- 主要问题：无必须整改问题。
- 以后更适合分派给该 Agent 的任务类型：技术验证规划、工程前置清单、受控测试任务、evidence 结构设计。
- 不建议分派给该 Agent 的任务类型：独立评审自己刚执行的真实 DB 验证结果。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要。

## 下一步任务建议

PM 建议用户确认后启动：

- `LIFEOS-P3-037`：受控文件型 SQLite migration / 残留 P2 验证执行任务。

建议边界：

- 仅新建隔离目录。
- 仅使用合成无敏感 fixture。
- 不触碰真实用户 DB、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 验证 P2-2 / P2-3 / P2-4。
- 产出 evidence manifest、测试摘要、hash、恢复演练和 PASS / FAIL 结果。
- 不关闭 R-0040，不冻结 Schema / API，不进入下一阶段。

若用户明确想验证非空旧版本 upgrade，则应先创建：

- `LIFEOS-P3-037`：upgrade version matrix / 转换设计任务。

再创建文件型 SQLite 执行任务。
