# LIFEOS-P3-052｜R-0048 生命周期证据全范围隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定工作区、候选代码和合成测试数据，用于防御性代码审查、缺陷验证和本地回归测试；不授权访问外部或第三方目标、真实用户数据或真实凭据，也不涉及未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“攻击、反例、旁路、权限”等术语仅指本地合成环境中的负向验证。既有只读、用户确认、独立性和停止条件继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-052
- 任务名称：R-0048 生命周期证据全范围隔离独立复评
- 优先级：P1
- 任务类型：全范围独立 Evidence 复评 / 风险关闭前置判断
- 是否适用 P3 Engineering Fast Lane：No；涉及风险关闭前置证据
- 推荐执行 Agent：Codex 新建隔离会话
- 推荐模型 / 推理强度：`gpt-5.6-sol` + `xhigh`
- 选择理由：需独立审查 Authorization lifecycle、AuditEntry、Outbox、generation/time、幂等命令、事务回滚与证据链；WorkBuddy 无额度。
- 允许降级模型 / 后备模型：None / None
- 禁止降级条件：风险关闭前置、撤回/权限/证据链边界、独立反例和完整 Evidence 均在范围内。
- 必须升级条件：如无法独立判断事务、SQLite trigger、hash 或 Evidence 冲突，在同一新会话升级 `gpt-5.6-sol` + `max`；仍无法判断则 Blocked 并回报 PM。
- 是否需要后续独立评审：No；本任务本身即独立复评，任何风险关闭仍需 PM 与用户确认。
- 允许修改工程 / 账本：No / No
- 主责角色：独立 QA / Evidence Reviewer、AI 信任与安全负责人
- 协审角色：技术架构负责人、数据 / 领域模型负责人、风险关闭评估负责人
- 必须通过关卡：Gate 2、Gate 3、Gate 4
- 状态：In Progress

## 会话、资产与范围

- 实际派发：全新 Codex 任务 `01a021e5-6dbb-71f2-8621-330ac075a32f`，host `local`，`gpt-5.6-sol` + `xhigh`，2026-08-21 CST。
- 必须为未承载任何 LifeOS 工作的新会话；禁止复用 P3-046/P3-047/P3-048/P3-049/P3-050/P3-051 及 PM 会话。
- 只允许写 P3-052 自身 deliverable/review/evidence/local precheck；所有工程、历史 Evidence 和主账本严格只读。
- 不关闭 R-0048，不修改 SQL/tests，不冻结资产、不恢复基线、不启用真实能力、不进入下一阶段。

## 目标与必测范围

对 R-0048 的全范围，而非 P3-050 的 Tombstone 子路径，形成独立结论。至少覆盖：

1. Submission/canonical hash/idempotency 与 lifecycle command 绑定、冲突和重放；
2. AuditEntry 同事务生成、append-only、correlation 唯一、预置和回滚；
3. Outbox payload 不可变、available/lease、owner/generation CAS、retry、complete/cancel/dead-letter、retention 和 generic job 清理作用域；
4. active→terminal generation/time 配对、audit/outbox/submission 的事务原子性、失败语句与调用方 rollback；
5. memory/file、FK ON/OFF、recursive triggers ON/OFF 八配置，文件型完整性检查；
6. P3-047 既有 PM-CE-01 至 PM-CE-05、P3-031 当前合同回归、P3-046/P3-047 历史失败 Evidence preservation；
7. 独立计划先封存，独立脚本不得 import/call P3-047 执行侧 runner 或攻击 helper；再延迟比较历史攻击资产。

## 结论规则

- Pass：所有范围形成独立主证据，0 P0/P1/明确 P2 bypass、0 Not Implemented/Unknown，回归/hash/独立性成立；只可作为 R-0048 风险决策输入。
- Rework：任一 P0/P1、明确 P2 合同 bypass、Evidence 冲突或只读保留失败。
- Blocked：会话非全新、关键资产不可访问、无法独立形成攻击集合或外部 safeguards 持续阻断关键工作。
- 无论结论如何，不得关闭 R-0048 或连带影响已关闭的 R-0049。

## 交付物

- `lifeos/deliverables/LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review.md`
- `lifeos/reviews/LIFEOS-P3-052/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-052/evidence/MANIFEST.md`
- 按规则运行本地预检；不可用时记录后继续人工评审。
