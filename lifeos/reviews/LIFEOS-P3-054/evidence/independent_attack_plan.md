# LIFEOS-P3-054 独立攻击计划（封存版）

## 封存信息

- 任务：LIFEOS-P3-054，P3-053 整改后的全新隔离独立复评。
- 封存时点：2026-08-21 CST；在读取 P3-053 的具体反例脚本、测试结果或评审前形成。
- 制定依据（封存前允许输入）：当前任务卡、`lifeos/reviews/LIFEOS-P3-052_pm_review.md`、候选 SQL `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`。
- 候选 SQL SHA-256：`bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`。
- 运行边界：仅在临时 SQLite 数据库和合成记录中执行；候选 SQL、历史工程、历史评审与历史 Evidence 均只读。

## 独立性承诺

- 自建 runner 只使用 Python 标准库；不会 import、调用、复制 P3-052 或 P3-053 的 runner、helper、测试场景表或结果断言。
- 在本计划封存后，P3-053 历史 runner 仅可用于等价回归；历史脚本、结果和评审不会定义本 runner 的案例或预期结果。
- 每个反例独立从当前候选 SQL 建库，并记录执行环境、输入 SQL SHA-256、结果和文件完整性散列。
- 任何 P1、明确 P2 bypass、Not Implemented、Unknown、候选 SQL 散列变更或只读资产变更都会停止“Pass”判断并按任务卡报告 Rework 或 Blocked。

## 预先定义的测试矩阵

### A. 生命周期 Outbox 的伪造与状态机

1. 针对 `authorization_state_change`，尝试直接 `INSERT` 与 `INSERT OR REPLACE` 伪造 job；分别改变 subject、job/idempotency、correlation、generation、payload、available time 和 canonical ID。
2. 构造真实 lifecycle command 后，核对同一事务中的 Authorization terminal 状态、generation、AuditEntry、Submission、Outbox 的 ID/idempotency/correlation/payload/audit action 与时间关系；对 revoked、expired、superseded 三终态分别验证。
3. 对真实 lifecycle job 尝试直接 UPDATE 以及伪造/错配 CAS 的 claim、renew、retry、cancel、dead-letter、complete；仅允许由匹配 `outbox_runtime_command` 驱动的合法转移。
4. 对 complete 条件验证 Authorization generation 必须与 job.subject_generation 匹配，且 command 追加记录不可篡改、不可重放。

### B. Retention、删除与重放围栏

1. 验证 lifecycle job 在非终态、缺审计、缺 retention binding、未满足 retention 时间时均不可删除。
2. 在满足终态、匹配 AuditEntry、binding、runtime command 和零时长 retention 后，验证合法删除成立。
3. 删除后分别用原 job ID、idempotency/correlation、以及替换 payload 尝试重新插入，验证 retention binding 仍构成 replay fence。
4. 用 non-authorization generic terminal job 验证原有的合法清理路径未被错误收紧或放开。

### C. Authorization 初始值与生命周期契约

1. 对 proposed/granted 初始 INSERT 和 `INSERT OR REPLACE` 验证 generation 必为 1，所有 non-revoked 状态的 `revoked_at_ms` 必为 NULL。
2. 覆盖主键及 `(logical_key, version_no)` 冲突；确保 active/terminal 不可被 REPLACE，且失败不会留下部分写入。
3. 对 proposed/granted -> active 验证 generation=1、`revoked_at_ms=NULL` 和完整 scope/action/policy 前置条件。
4. 对 revoked、expired、superseded 逐一验证只由匹配 lifecycle command 进入终态；revoked 的时间等于处理时间，expired/superseded 的 `revoked_at_ms` 为 NULL。

### D. 执行模式、原子性与回归

1. 在 memory/file × `foreign_keys` ON/OFF × `recursive_triggers` ON/OFF 的 8 个配置运行 A-C；当 SQLite 行为限制使测试不适用时，必须明确标记并说明，不能静默跳过。
2. 为关键拒绝路径加入显式事务、多行语句和 rollback 案例，检查失败语句或事务不留下 orphan Authorization/Audit/Outbox/binding/command。
3. 对 file 数据库执行 `PRAGMA integrity_check` 与 `foreign_key_check`，并记录文件散列。
4. 独立执行 P3-031 既有回归及 PM-CE-01 至 PM-CE-05 等价回归；其结果只证明不回归，不取代 A-C 的独立结论。

## 结论口径

- Pass 仅在全部预定义案例完成，且 P0/P1/明确 P2 bypass/Not Implemented/Unknown 均为 0、独立性与散列校验成立、回归成立时使用。
- 本复评即使通过，也只提供 R-0048 后续风险决策输入；不关闭 R-0048，不影响 R-0049，不冻结任何资产，不恢复基线，也不进入下一阶段。
