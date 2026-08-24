# LIFEOS-P3-045｜Authorization 生命周期证据与终态历史边界合同

## 1. 执行摘要与适用边界

- **推荐方案：B，DB 不变量 + 应用事务守卫。** DB 负责状态机、generation、DB 时钟、证据原子生成、不可变和受控清理门；应用负责身份/意图、幂等命令、用户确认、租约调度和清理编排。V1 用一个非核心、append-only 的生命周期命令记录承接事务意图，不升级为事件权威/投影架构。
- 退休证据不得再由 trigger 检查“预先存在的 audit/outbox”来放行；应由同一 Authorization 状态转换在 DB 内原子生成。预置同 correlation/idempotency 的行只能令事务冲突回滚，不能充当退休证据。
- `audit_entry` 是最小、append-only 的生命周期证据；`outbox_job` 是非权威投递队列，其业务载荷不可变，租约、重试和结果状态可按状态机改变。
- terminal Authorization 及 scope/action/policy 默认完全不可变；用户明确清理时采用“一向受控 redaction/tombstone + 最小审计摘要”，诚实标记历史已清理，不把清理伪装成完整历史仍可验证。
- 本文是后续工程合同，不修改或冻结 Schema/API，不关闭 R-0048/R-0049 或其他风险，不构成 P3-044 独立复评，也不外推到真实 DB/Tauri/IPC。
- 实际配置：`gpt-5.6-sol` + `xhigh`，未降级。

## 2. 已验证事实、推断、建议与待确认

**已验证事实**：当前候选 SQL 的退休 trigger 只检查 audit/outbox 匹配行存在；两表均无 UPDATE/DELETE 防线；generation 只防下降；`created_at_ms`、`revoked_at_ms` 可直接改写；terminal 父表和三类子表可变。P3-041/P3-043 已在合成 SQLite 中复现，维持 P2。当前 outbox 枚举为 `pending/leased/completed/cancelled/dead_letter`。

**推断**：单纯把 audit/outbox 全表锁死会破坏 outbox 合法执行；只依赖应用约定又不能阻止直接 SQL 制造相互一致但虚假的证据。SQLite 可用 BEFORE trigger 校验转换、AFTER trigger 派生 evidence；任一插入冲突会令同一语句/事务回滚。

**建议**：下一工程补丁以 trigger 原子生成退休 audit/outbox、字段级不可变、outbox 状态机、terminal 不可变和受控清理门为最小范围。新增一个内部控制记录 `authorization_lifecycle_command`（不是核心领域实体）：应用只追加经过确认的命令，DB trigger 以 DB 时钟完成转换并生成证据；`submission` 继续留幂等回执。DB 证据不信任日志、聊天或应用口头声明。

**需 PM 确认**：采纳本合同作为下一工程输入；允许候选 Schema 增加上述非核心命令记录，并将 `authorization` 纳入 tombstone/清理对象。两项都只是候选控制元数据，不是核心实体变更或 Schema 冻结。

## 3. 表、字段与操作责任矩阵

| 对象/字段 | 分类与权威性 | INSERT | UPDATE | DELETE / 清理 |
|---|---|---|---|---|
| `authorization` 身份、包络、status、generation、时间 | 权威业务事实 | 仅 proposed/granted 起步 | 仅合法状态转换；active/terminal 包络不可变 | active 禁止；terminal 仅受控清理 |
| scope/action/policy | 权威授权语义 | 仅非 active/terminal 配置 | active/terminal 禁止 | active/terminal 禁止；受控清理例外 |
| `audit_entry` 全字段及 correlation | 不可变最小证据 | 仅生命周期 trigger/受控审计入口 | 一律禁止 | 单对象清理保留最小行；整库用户销毁除外 |
| outbox：job/subject/generation/payload/idempotency | 不可变业务载荷 | 仅权威事务/trigger | 一律禁止 | terminal 且超过保留期后可清理 |
| outbox：status/attempts/available/lease*/last_error | 可变运行态 | 初始 pending | 仅状态机与 CAS | 随 job 受控清理 |
| `submission` idempotency/canonical hash/correlation | 幂等命令回执 | 应用事务守卫写入 | 不改请求身份或结果绑定 | 按明确保留策略清理，不充当退休证据 |
| lifecycle command：auth/expected generation/target/actor/idempotency/hash | append-only 一次性控制意图 | 应用守卫只追加 | 一律禁止；由 INSERT trigger 当步消费 | 不作业务历史权威；保留期后可清理 |
| tombstone/cleanup 状态 | 用户清理权威控制 | 用户确认后的 destruct 流程 | 只向前转换 | 不删除、不可 REPLACE |

允许主体不是数据库账号名，而是代码责任：DB trigger 独占证据派生和不变量；应用生命周期服务独占合法命令、actor、确认、幂等与事务；worker 只可改变 outbox 运行态；cleanup worker 只在 tombstone 门成立时执行。失败必须返回稳定错误并保持父、子、audit、outbox、submission 全部原样。

## 4. AuditEntry append-only 与防预置/防回放合同

1. audit 首次 INSERT 后所有字段不可 UPDATE，正常运行不可 DELETE/REPLACE；`correlation_id` 唯一，且绑定 `authorization-state:{id}:{new_generation}:{terminal_status}`。
2. active→terminal 的 BEFORE trigger 校验：状态合法、`generation=OLD+1`、时间配对正确；不得再以 audit/outbox “存在”作为放行条件。
3. 应用追加生命周期命令后，其 INSERT trigger 在同一 `sqlite3_step` 内用 DB 时钟完成 Authorization UPDATE，并插入 audit 与 outbox。subject、version、action、result、correlation、generation 和时间由命令与 OLD 行共同确定；actor 来自经应用守卫核验且不可变的命令字段，expired 仅允许受控本地 system actor。直接对 active 行执行 terminal UPDATE 一律拒绝。
4. 预置相同 correlation 的 audit、重复 outbox idempotency 或回放同一 transition 会触发唯一冲突并整体回滚；错误 generation/version/status 不能匹配由 trigger 派生的值。
5. audit 插入失败、outbox 插入失败、应用事务后续失败均回滚 Authorization 转换；不得留下“已退休但无证据”或“有证据但未退休”。日志和聊天不参与权威判断。
6. 本合同防的是正常应用与任何直接 SQL 路径的静默伪造；拥有操作系统/数据库文件完全控制权的用户仍可销毁或离线篡改本地库，V1 不声称提供密码学不可否认性。

## 5. OutboxJob 不可变载荷与可变运行态合同

- 兼容映射：`pending` 同时表达初次待执行与可重试；`leased` 为租约中；`completed` 为 succeeded；`dead_letter` 为达到策略上限的 failed/abandoned；`cancelled` 为因 subject generation 失效或用户清理而 abandoned。
- 合法转换：pending→leased；leased→completed；leased→pending（失败且可重试/租约恢复）；pending或leased→cancelled；leased→dead_letter。completed/cancelled/dead_letter 均 terminal，不得返回 pending。
- 领取必须按 status、available time、旧 `lease_generation` 做 CAS；成功时 `lease_generation+1`、设置 owner/expiry，并只在领取或实际执行失败时按约定增加 attempts。续租只允许同 owner+generation 延长有限 expiry。
- 重试可改 available time、last error 和运行态；不得改 job_type、subject、subject_generation、payload_ref、idempotency。完成前再次校验租约和当前 Authorization generation；旧 generation 只能取消，不能发布。
- outbox 不是历史权威。只有 terminal job、对应 audit 已耐久存在、无活跃 lease 且超过保留窗口时才可批量清理；清理失败不得改变 Authorization 状态或 audit。

## 6. Generation、时间、状态与 evidence 原子合同

- 新 Authorization 从 generation=1 开始；proposed/granted 配置和首次激活不递增。active→revoked/expired/superseded 必须恰好 +1。active→active 维护、outbox 重试、租约或补偿不得改变 generation；terminal 不可再激活。
- `created_at_ms` 从 INSERT 起永久不可变。非 revoked 状态 `revoked_at_ms` 必须 NULL；active→revoked 时由命令 trigger 使用同一 DB 时间一次性写入，并等于 `updated_at_ms` 与 audit `occurred_at_ms`；之后不可变。expired/superseded 的权威终态时间同样是 audit `occurred_at_ms`，且等于转换时 `updated_at_ms`；V1 不必新增两个重复时间列。
- 单一事务顺序：应用校验 actor/确认/idempotency/expected generation → 写幂等 submission → INSERT lifecycle command → DB 在该语句内校验并写状态+generation+DB 时间、audit、outbox → 应用检查结果 → COMMIT。任何一步失败 ROLLBACK。
- 若未来需要 active→active 政策变更，应创建并激活 successor，而不是“维护事件”升 generation。若确需补偿性反向转换或新增终态时间字段，必须回 PM 重新评估。

## 7. Terminal 历史与用户清理方案

| 方案 | 安全/恢复 | 数据主权与成本 | 结论 |
|---|---|---|---|
| A 原行永久完全不可变 | 历史最直观，恢复简单 | 无法满足选择性清理；敏感引用长期保留 | 不采用 |
| B 生命周期事件权威、Authorization 仅投影 | 最强事件追踪与重建 | 引入新权威模型、迁移/查询复杂，超出 V1 | 暂不采用；多设备/同步再评估 |
| C terminal 默认不可变；用户确认后 tombstone + 单向受控 redaction/清理 | 正常历史可信；清理后诚实显示“已清理”，不伪造旧语义 | 保留最小审计元数据，有有限隐私残留 | **V1 推荐** |

方案 C 下，revoked/expired/superseded 的父包络、身份、generation、时间以及三类子表默认全部不可变。选择性清理必须先写 Authorization tombstone、达到 active_blocked、追加 cleanup audit，再由专用作业删除敏感 scope/policy 引用或最终父/子投影；保留的 audit 仅含随机作用域引用、版本、终态、generation、时间和 `redacted_by_user` 结果，不含正文、路径、URL、自由错误或可猜 hash。系统必须明确显示该历史已按用户请求清理，不能再宣称原授权语义完整可验证。整库删除由用户直接销毁本地库，优先于项目内审计保留。

## 8. 技术方案比较与单一 V1 推荐

| 维度 | A 纯 DB trigger | B DB + 应用事务守卫 | C 事件权威 + 投影 |
|---|---|---|---|
| 安全/崩溃恢复 | 强 DB 原子性；难表达用户确认/actor | DB fail-closed + 应用意图，单事务可恢复 | 最强回放，但新复杂面最大 |
| V1 可实现/测试 | 中；易把 outbox 误锁 | **高；与当前 SQLite/服务层一致** | 低；需要新权威语义和迁移 |
| 数据主权 | 需另加清理门 | 可编排 tombstone/redaction | 事件清理与重放更难 |
| 未来扩展 | 中 | 中高，可逐步迁移 | 高，但当前过重 |

因此推荐 B：应用守卫只追加一次性 lifecycle command；trigger 守不可绕过的不变量、使用 DB 时钟完成转换并原子生成 evidence；应用继续处理 actor、preview、idempotency、worker/cleanup；outbox 保持非权威。出现多设备同步、跨进程多 writer、监管级不可否认审计、需要从事件完整重建 Authorization，或受控 redaction 无法满足恢复/导出时，才重新评估 C。

## 9. R-0048 / R-0049 条目级处置

| 风险条目 | 下一补丁必须处理 | 可条件保留及失效条件 |
|---|---|---|
| R-0048 audit 预置/改删 | trigger 原子生成、correlation 唯一、append-only | 不保留；若仍靠存在性放行则失败 |
| R-0048 outbox 改删 | 载荷不可变、运行态状态机、terminal 清理 | 运行态可变可保留；任意 payload/subject 改写即失败 |
| R-0048 generation climb | 只允许 active→terminal +1 | 不保留；active→active 升高即失败 |
| R-0048 created/revoked 时间 | created 永久不可变；NULL/状态/转换时间配对 | expired/superseded 不增列可保留，前提是 audit 时间权威且不可变 |
| R-0049 terminal 父/子 | 默认不可变，受控清理为唯一例外 | 用户确认清理后语义缺失可保留，必须有 tombstone/audit 且 UI/导出诚实标记 |

风险状态建议仅为“完成工程与独立核验后进入关闭候选”；本任务不关闭任何风险。

## 10. 后续工程验收测试（不含代码）

| ID / 级别 | 场景与预期 | 必备证据 | 阻塞后续 Schema/API 判断 |
|---|---|---|---|
| AC-01 P2 | 预置正确 correlation audit 后退休：唯一冲突、全事务回滚 | 前后五表快照/错误码 | Yes |
| AC-02 P2 | UPDATE/DELETE/REPLACE audit：全部拒绝 | 原行 hash/错误码 | Yes |
| AC-03 P2 | generation/version/action 不匹配证据：不能退休 | rollback 快照 | Yes |
| AC-04 P2 | 重放相同退休命令：原回执或冲突，不增证据 | submission/audit 计数 | Yes |
| AC-05 P2 | 修改 outbox subject/payload/idempotency：拒绝 | 原 job 快照 | Yes |
| AC-06 P1 | 合法 lease→完成，owner/generation CAS 正确 | 状态序列/受影响行数 | Yes |
| AC-07 P1 | 旧租约、旧 subject generation 完成：拒绝/取消，不发布 | CAS 与发布计数 | Yes |
| AC-08 P2 | retry 增 attempts、available/error，不改载荷 | 逐步快照 | No |
| AC-09 P2 | active generation 单独 +1/+N：拒绝 | generation 前后值 | Yes |
| AC-10 P2 | 改写 created_at 或预写 active revoked_at：拒绝 | 错误码/快照 | Yes |
| AC-11 P2 | revoked/expired/superseded 时间配对错误：拒绝 | audit/parent 零半状态 | Yes |
| AC-12 P2 | terminal 父包络 UPDATE/REPLACE/DELETE：拒绝 | 完整父行快照 | Yes |
| AC-13 P2 | terminal scope/action/policy INSERT/UPDATE/DELETE/改绑：拒绝 | 三子表快照 | Yes |
| AC-14 P1 | 合法 revoke/expire/supersede：parent+1、audit+outbox 原子提交 | correlation/事务日志 | Yes |
| AC-15 P1 | 合法 supersede 后完整 successor 激活，旧历史不变 | 版本链与两代快照 | Yes |
| AC-16 P1 | audit 或 outbox 插入故障：状态/generation/submission 全回滚 | 故障注入日志 | Yes |
| AC-17 P2 | 无 tombstone/未 active_blocked 的清理：拒绝 | cleanup 错误/零删除 | Yes |
| AC-18 P2 | 用户确认清理：单向 tombstone/redaction、最小 audit 保留、旧包不复活 | 清理前后/restore 结果 | Yes |

## 11. 后续工程边界、evidence 与停止条件

**允许范围建议**：仅修改 P3-031 候选 SQL/合同测试/evidence，并新建一个窄回归包；实现本合同中的 audit/outbox/generation/time/terminal/controlled-cleanup 约束，只用合成空库、内存和任务目录文件 SQLite。

**非范围**：真实 migration/旧库、真实 DB/Vault/Tauri/IPC/文件、云/第三方模型、同步、多设备、L3、事件溯源重构、核心领域模型或权限边界变化、风险关闭、冻结和 PM 账本。

**Evidence manifest 最少包含**：输入/输出 hash、SQLite/Python/PRAGMA、memory/file 与 FK/recursive/事务矩阵、18 项逐例结果、原子快照、状态机轨迹、故障注入、文件库 integrity/FK 检查、既有 P3-044 evidence 未变证明、0 FAIL/Not Implemented/Unknown 的退出合同。

**停止条件**：发现 P0/P1 active 权限旁路；必须新增核心实体或改变冻结模型/架构/AI 权限；无法区分合法 outbox 运行态与载荷篡改；清理会复活或泄露用户数据；候选与 evidence hash 不一致；触及任何真实能力。命中即停止并回 PM，不自行扩卡。

## 12. 角色、关卡、剩余风险与不可外推

- 数据/领域模型主责：权威事实、证据、运行态和清理对象已分层；不把数据库表设计宣称为核心模型冻结。
- 技术架构主责：推荐可在当前 SQLite + 本地应用服务中落地；未依赖云、事件平台或真实 IPC。
- AI 信任与安全/QA 协审：generation、policy 历史和退休 evidence 不再允许静默伪造；用户清理优先且必须诚实降级历史可信度。
- Gate 2、Gate 3、Gate 4：**Pass with Conditions（合同设计层）**；条件是后续工程实现、合成回归、PM 验收。不是独立评审、冻结或真实能力准入。
- 剩余风险：完全控制本地文件的主体可离线篡改；并发/WAL/断电/升级旧库未验证；选择性清理会有意降低历史可验证性；outbox 保留窗口和整库销毁 UX 尚未冻结。
- 不可外推：本文不关闭 R-0040/R-0043/R-0044/R-0046/R-0047/R-0048/R-0049/R-0050，不改变 R-0045，不冻结 Schema/API/SQL migration/工程基线，不创建后续任务，不代表 P3-044 独立通过或允许进入下一阶段。

## 13. Local Precheck / 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py --timeout 20 lifeos/deliverables/LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract.md`
- 报告：`lifeos/local_prechecks/LIFEOS-P3-045_LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract_local_precheck.md`
- 状态：`Skipped / Local Model Unavailable`；局域网模型请求超时，脚本退出码 0，符合允许跳过规则，PM 需按原流程人工复核。
- 本地预检仅作覆盖与措辞辅助，不作 PM、独立评审、冻结、风险关闭或准入结论。
