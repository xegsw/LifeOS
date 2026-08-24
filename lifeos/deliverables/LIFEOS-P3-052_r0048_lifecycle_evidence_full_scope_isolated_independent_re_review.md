# LIFEOS-P3-052｜R-0048 生命周期证据全范围隔离独立复评交付物

## 任务与边界

- 任务类型：全范围独立 Evidence 复评 / R-0048 风险关闭前置判断。
- 执行方式：全新隔离 Codex 会话；任务派发 ID 与任务卡一致。未复用 P3-046、P3-047、P3-048、P3-049、P3-050、P3-051 或 PM 会话。
- 主责角色：独立 QA / Evidence Reviewer、AI 信任与安全负责人。
- 协审角色：技术架构负责人、数据 / 领域模型负责人、风险关闭评估负责人。
- 授权与数据边界：只读候选工程和历史资产；所有动态验证仅在内存或临时文件型合成 SQLite 中执行。未使用真实用户数据、真实 DB/Vault、Tauri/IPC、网络、云或第三方系统。
- 未执行事项：未修改候选 SQL/tests、未修改账本、未关闭 R-0048、未影响 R-0049、未冻结资产、未恢复工程基线、未进入下一阶段。

## 独立性与证据方法

### 已验证事实

1. 在读取 P3-046/P3-047/P3-048/P3-049/P3-050 的攻击脚本、结果或 Review 前，已独立创建攻击计划并封存 SHA-256：`28c02a3cad630f119e4e2a877ddf93421f785f76b3c1c701f24ee354c450fee7`。
2. 自建 `independent_lifecycle_review.py` 直接读取 P3-048 candidate SQL（SHA-256：`56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d`）；未 import/call P3-047 runner 或历史 attack helper。
3. 自建 23 个逻辑用例覆盖 Submission/canonical hash/idempotency、AuditEntry、Outbox 状态机和 retention、generation/time、事务 rollback/savepoint、多行原子性、P3-047 PM-CE-01 至 PM-CE-05 语义、八配置与文件检查。
4. 运行结果为 184 个实例：152 PASS、32 BYPASS、0 FAIL、0 Unknown；32 个 bypass 是下列四类各在八配置中复现。所有文件型实例的 integrity/quick/FK 检查通过。
5. P3-031 在隔离临时副本复跑 70 PASS（P0 18、P1 27、P2 25），退出码 0；当前合同回归未失败。
6. P3-046/P3-047 旧执行 Evidence、旧 PM 反例、当前 P3-048 candidate/Manifest 共 14 个只读文件 before/after SHA-256 一致，历史 BYPASS/Rework 证据没有被覆盖。

### 独立发现

| 发现 | 级别 | 复现事实 | 合同影响 |
|---|---|---|---|
| 伪造 lifecycle Outbox | P1 | 直接插入 `authorization_state_change` OutboxJob 后，可在 Authorization 仍 active/generation=1 时 claim 并 complete；不需要 lifecycle command 或 AuditEntry。 | Outbox lifecycle evidence/delivery 不再能证明其由权威状态转换派生。 |
| retention 后 job 重放 | P1 | 合法 retention DELETE 后，可复用已删除 job 的 ID/idempotency/correlation 重插不同 payload；保留 binding 不阻止插入。 | 清理后失去 lifecycle identity/replay fence，可重复或改写投递。 |
| 初始 generation 非 1 | P2 | `generation=7` 的 proposed Authorization 可完成配置并激活。 | 违反“新 Authorization 从 generation=1 开始”的 generation fencing 合同。 |
| active 前预写 revoked 时间 | P2 | proposed 行可写 `revoked_at_ms`，然后激活而字段保持非 NULL。 | 违反非 revoked 状态为 NULL、转换时间配对的生命周期时间合同。 |

### 已通过的关键边界

- malformed/unbound Submission—command 绑定、同 key replay、预置同 correlation 的 Audit/Outbox 导致状态转换回滚。
- Audit/Submission/lifecycle command append-only；Outbox 既存 payload/subject/idempotency 不可原位改写。
- future availability claim、错误 owner/generation CAS、过期租约 complete/renew、retry、complete/cancel/dead-letter 单向转移均按预期受限。
- direct active→terminal、generation climb、created/revoked 时间直接 UPDATE、多行失败语句、显式事务/后续失败/savepoint rollback 均未留下半状态。
- 历史 PM-CE-01 至 PM-CE-05 的语义在独立 fixture 和 P3-031 隔离回归均通过；Tombstone 回归只是对已关闭 R-0049 的非决策性回归检查。

## 结论

### 已验证事实

任务卡的 Pass 条件要求 0 P0/P1/明确 P2 bypass、0 Not Implemented/Unknown、回归/hash/独立性均成立。本轮虽然满足独立性、历史保留、P3-031 回归、文件完整性及 152 个实例通过，但存在 2 个稳定 P1 与 2 个稳定 P2 bypass。

### 合理推断

P1-01 与 P1-02 分别使 Outbox 产生不由权威 lifecycle 事务派生的状态变更投递，或在清理后重用同一 lifecycle 投递身份。Outbox 虽不应成为权威业务事实，但 R-0048 的合同要求其与 Audit/Submission/Authorization 生命周期一致且可追溯；因此不能作为风险关闭输入通过。P2-01/P2-02 进一步说明 generation/time 的初始状态约束并未完整落地。

### 评审结论

**Rework。** 本结论只作为 R-0048 的后续 PM 决策输入；不关闭风险、不改变 R-0049、不冻结或推进任何资产。

## 关卡与角色检查

- Gate 2 数据与来源：Rework。Outbox provenance/replay 和 lifecycle generation/time 的证据语义不完整。
- Gate 3 AI 权限与信任：Rework。撤回/失效投递可与权威 Authorization 状态不一致，不满足风险关闭前 fail-closed 要求。
- Gate 4 技术可行性：Rework。候选可稳定运行且文件库完整，但没有满足完整 Outbox/idempotency/retention 合同。
- Gate 1 / Gate 5：不适用；没有产品范围或用户价值变更。

## 建议与待 PM 决策

### 建议

1. 新建窄范围工程整改任务，优先限制 lifecycle Outbox 只能由匹配 command + terminal Authorization + Audit 在同一事务派生，并在 retention 删除后保留不可重用的 lifecycle replay fence。
2. 同一任务补齐 Authorization 初始 `generation=1` 及 non-revoked `revoked_at_ms IS NULL` 的 INSERT/activation 合同与负测。
3. 修复后依次复跑 P3-031、PM-CE-01 至 PM-CE-05、四项本轮反例、八配置文件完整性；由新的隔离会话做独立复评。

### 需要 PM 决策

- 是否采纳 P3-052 的 Rework 结论并创建上述窄范围整改任务。
- 在整改和新的独立复评完成前，R-0048 是否继续维持 Open / Remediation Candidate（本评审建议：是）。

## Evidence

- 独立评审：[independent_review.md](/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-052/independent_review.md)
- Evidence 入口：[MANIFEST.md](/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-052/evidence/MANIFEST.md)
- 结构化主结果：[independent_attack_results.json](/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-052/evidence/independent_attack_results.json)
- 隔离 P3-031 回归：[p3_031_isolated_results.json](/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-052/evidence/p3_031_isolated_results.json)
- 本地预检：[LIFEOS-P3-052_local_precheck.md](/Users/xxe/Documents/No.2/lifeos/local_prechecks/LIFEOS-P3-052_LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review_local_precheck.md)（Skipped / Local Model Unavailable；不影响人工独立评审）
