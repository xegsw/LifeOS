# LIFEOS-P3-057｜Active Authorization 整改全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、候选 SQL、历史 Evidence 和合成测试数据，用于防御性代码审查、缺陷复现、修复验证与本地回归测试；不涉及外部目标、真实数据或凭据、未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“攻击、反例、旁路、替换、重建、权限边界”等术语仅指本地合成环境的负向验证，不授权扩大范围。既有只读资产、用户确认、独立性和停止条件继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-057
- 优先级：P0
- 类型：P3-044 整改后的全新隔离独立工程复评
- 建议篇幅：2000-4000 字
- 是否适用 P3 Engineering Fast Lane：No（独立复评与开放 P1 风险输入）
- 推荐执行 Agent：Codex，新建隔离会话
- 推荐理由：需在不复用 P3-044 执行上下文或攻击函数的前提下，自建反例并核验 P0/P1 权限边界与只读保留。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：跨历史整改、当前候选 SQL、反例设计、事务/PRAGMA 矩阵和 Evidence 保留的高风险独立复核。
- 允许降级模型：None
- 禁止降级条件：任何 P0/P1、测试/Evidence 冲突、独立性不足、hash 变化、或涉及 R-0044/R-0047/R-0050 关闭建议时。
- 必须升级条件：若当前配置无法形成可复核的独立结论，停止并回报 PM；仅在 PM 明确新任务卡授权时可升级为 `gpt-5.6-terra` + `max`。
- 后备模型：None
- 是否需要后续独立评审：No；本任务自身为独立复评。风险关闭仍须 PM 与用户确认。
- 是否允许修改工程文件：No；仅允许在隔离临时副本执行，且只写 P3-057 自身 review、deliverable、evidence 与 local precheck。
- 是否允许修改项目账本：No
- 主责角色：独立 QA / Evidence Reviewer
- 协审角色：技术架构、数据/领域模型、AI 信任与安全
- 必须通过的评审关卡：Gate 2、Gate 3、Gate 4
- 实际派发会话：新隔离 Codex 会话 `01a0225d-59d4-7071-8509-823c20dbe27e`（local，`gpt-5.6-terra` + `xhigh`）。
- 状态：In Progress

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 独立工程复评
- 推荐复用的会话：None
- 会话判断理由：P3-044 原独立复评被用户例外跳过；本任务必须避免执行侧自证及既有会话污染。
- 是否需要独立性隔离：Yes
- 必须重新读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`AGENT_BRIEFING_PACK.md`、`PM_OPERATING_MODEL.md`、`ROLE_MATRIX.md`、`STAGE_GATES.md`、`INDEPENDENT_REVIEW_TEMPLATE.md`、`SESSION_REPORT_TEMPLATE.md`、P3-044 任务/交付物/PM Review/Evidence Manifest、P3-043 独立 Review/Evidence、当前 P3-031 候选 SQL 与合同入口、R-0044/R-0046/R-0047/R-0050 行、D-0222 至 D-0225 与 D-0253。
- 可复用既有读取结果：None（新隔离会话）。
- 任务完成后是否建议保留会话：No；该会话不得承担自身成果后的风险关闭判断。

## 目标与范围

核验当前候选 SQL 是否在合成 SQLite、memory/file、FK ON/OFF、recursive triggers ON/OFF、事务/保存点和多行语义下，对 active Authorization 的替换、重建、父/子安全包络写入与关联旁路 fail closed；同时核验合法 successor / terminal 路径不回归。

必须：

1. 在读取 P3-044 攻击资产前，先封存自己的攻击计划与独立性声明；新 runner 不得 import、调用或复制 P3-044 的攻击函数/场景表。
2. 核验 P3-043 历史失败 Evidence 与 P3-044 当前整改/PM Evidence 的 hash 保留；工程与历史 Review/Evidence 均只读。
3. 自建反例至少覆盖：id 与 `(logical_key, version_no)` 冲突的 INSERT/REPLACE、UPSERT/冲突目标变体、DELETE+INSERT 重建、active 子表 INSERT/UPDATE/DELETE/改绑、父安全包络字段改写、PRAGMA 八配置、事务回滚/保存点、多行语义与合法 successor/terminal 路径。
4. 输出 P0/P1/P2、Not Implemented、Unknown 的明确计数；任何 P0/P1、违反明确合同的 P2、Evidence 冲突、hash 保留失败或独立性不足，结论必须为 Rework 或 Blocked。
5. 创建任务专属独立 Review、交付物、Evidence Manifest、结构化结果/日志/快照、输入 before/after hash 与本地预检记录。

## 非范围与停止条件

- 不修改候选 SQL、合同测试、历史 Evidence 或项目账本；不关闭 R-0044/R-0046/R-0047/R-0050，不影响已关闭的 R-0048/R-0049。
- 不使用真实数据库、真实用户数据、真实 Vault/Tauri/IPC/文件、网络、云/第三方模型、同步、多设备、L3、外部用户、并发/WAL 或恢复能力。
- 不冻结 Schema/API 或工程基线，不进入下一阶段，不创建后续任务。
- 若发现当前候选已与 P3-044 Evidence 不兼容或任务输入无法一致核验，停止扩大测试并记录 Blocked/冲突。

## 任务输出

- 交付物：`lifeos/deliverables/LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-057/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-057/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/` 下本任务报告；若不可用，记录允许跳过原因。

## 验收与回复

交付物必须区分已验证事实、合理推断、建议、风险和需 PM 决策；按 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 简短回报。P3-057 的 Pass 仅可作为 PM 后续风险决策输入，不构成风险关闭、冻结、基线恢复或阶段切换。
