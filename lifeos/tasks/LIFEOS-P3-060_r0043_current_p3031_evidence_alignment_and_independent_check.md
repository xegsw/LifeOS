# LIFEOS-P3-060｜R-0043 当前 P3-031 Evidence 对齐与隔离独立核对

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、候选 SQL、合同测试、Review、Evidence 和合成测试数据，用于防御性 Evidence 对齐、缺陷复现验证与本地回归测试；不涉及外部目标、真实数据或凭据、未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“旁路、反例、删除后复活、改绑”等术语仅指本地合成环境的负向验证，不授权扩大范围。既有只读资产、用户确认、独立性和停止条件继续有效。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-060`；优先级：P1；类型：当前 Evidence 对齐与隔离独立核对；建议篇幅：2000–4000 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离会话。
- 推荐理由：需将当前候选输入、可复现结构化结果、历史 Evidence 保留和独立反例核对绑定，不能复用 P3-031、P3-037/P3-039 或 P3-058 的执行／评审会话。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`xhigh`。
- 模型选择理由：需处理 hash 谱系、历史保留、独立性与合成 SQLite 反例矩阵；D-0242 后白名单内无等价低配替代。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：任何 hash/Evidence 冲突、历史保留失败、P0/P1、明确合同 P2 bypass、Unknown、Not Implemented、独立性不足，或拟形成 R-0043 风险决策输入时。
- 必须升级条件：当前配置无法形成可复核、可重跑的对齐结论时停止并回报 PM；仅可由 PM 新任务卡改为 `gpt-5.6-terra` + `max`。
- 是否需要后续独立评审：No；本任务本身是隔离独立核对。R-0043 风险关闭仍须 PM 验收和用户明确确认。
- 是否允许修改工程文件：No。候选 SQL、合同测试、既有 P3-031 Evidence、历史 Review/Evidence 和项目账本全部只读；仅可写本任务自身 deliverable、review、Evidence、临时副本和本地预检。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA / Evidence Reviewer；协审：技术架构、数据/领域模型、AI 信任与安全；关卡：Gate 2、Gate 3、Gate 4。
- 状态：Ready（等待 PM 派发至全新隔离 Codex 会话）。

## 会话隔离与读取

- 是否建议新建会话：Yes；执行方式：Create New Session；推荐会话类型：Codex 隔离独立 Evidence Review；推荐复用会话：None。
- 隔离原因：不得与 P3-031 工程执行、P3-037/P3-038 工程整改、P3-039 独立复评或 P3-058 风险决策会话相同；也不得复用其攻击函数或将其输出作为本任务唯一结论。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`INDEPENDENT_REVIEW_TEMPLATE.md`、`SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的会话隔离、Evidence／风险验收和上下文读取规则；`ROLE_MATRIX.md` 的独立 QA／技术架构／数据领域／AI 信任与安全检查点；`STAGE_GATES.md` 的 Gate 2、Gate 3、Gate 4；Codex 执行本任务时不必读取 `AGENT_BRIEFING_PACK.md`。
- 直接输入：P3-031 当前 SQL/合同入口与主 Evidence、P3-037/P3-038/P3-039 的任务／Review／Evidence、P3-058 task/independent review/PM Review/Evidence、R-0043 行及 D-0208–D-0214、D-0258–D-0262。
- 可复用既有读取结果：None；新会话必须建立自己的轻量读取账本。
- 任务完成后是否建议保留会话：No；该会话不得承担其成果的风险关闭判断。

## 背景与目标

P3-058 已证明当前候选 SQL/tests（SQL `bda3e8…9b1`、tests `45d19e…224a`）与 P3-031 旧主 Manifest/70 PASS 结构化快照不一致。隔离临时副本的 74 PASS 是正向信号，但不能替代可追溯的当前 Evidence。用户现授权仅补齐该 Evidence 链并作一次隔离独立核对。

目标是生成一个可审计的 **P3-031 当前候选后继 Evidence 包**：明确它与旧 P3-031 Evidence 的谱系关系，不覆盖旧文件，并将当前 SQL/tests/runner 的 hash、当前受控复跑、独立 R-0043 相邻反例、结果和只读保留绑定。它只提供后续 PM 风险决定输入，不直接关闭 R-0043。

## 必须完成的范围

1. 在读取历史攻击实现前，写入并封存本任务自己的独立性声明与反例计划；新 runner 不得 import、调用或复制 P3-039/P3-058 的攻击函数、场景表或结构化结果。
2. 为本任务直接输入建立 before/after SHA-256 清单；至少覆盖当前 SQL、合同 tests、validation runner、P3-031 既有 Manifest/result/log、P3-037/P3-038/P3-039/P3-058 直接 Evidence 和 R-0043/相关决策。证明既有资产未被覆盖。
3. 仅在隔离临时副本复跑当前 P3-031 合同入口，记录命令、退出码、环境、当前 hash、结构化结果 hash、P0/P1/P2/Unknown/Not Implemented 计数；不得在原 P3-031 工作树写入任何 Evidence。
4. 自建、最小但充分的独立 R-0043 反例集合，覆盖 Tombstone generation 降级、DELETE/reinsert、普通 Tombstone 向 Authorization 改绑、伪造 generation/command/reason/time、合法单调 successor，以及事务回滚／保存点语义。
5. 反例矩阵至少覆盖 memory/file、`foreign_keys` ON/OFF、`recursive_triggers` ON/OFF；记录各配置及事务结果。任何无法运行的维度必须标为 Unknown 或 Not Implemented，不得静默省略。
6. 新增并保存以下**仅属于 P3-060**的输出：
   - `lifeos/deliverables/LIFEOS-P3-060_r0043_current_p3031_evidence_alignment_and_independent_check.md`
   - `lifeos/reviews/LIFEOS-P3-060/independent_review.md`
   - `lifeos/reviews/LIFEOS-P3-060/evidence/MANIFEST.md`
   - 任务专属结构化结果、日志、独立计划和当前候选快照；该包必须明确声明为 P3-031 的 current successor Evidence，**不得覆写** `lifeos/engineering/LIFEOS-P3-031/evidence/` 中的历史文件。
7. 本地预检默认运行；若本地模型不可用、超时或空输出，记录允许跳过原因。

## 非范围与停止条件

- 不改 SQL、合同测试、runner、工程代码、P3-031 历史 Evidence、历史交付物、风险日志、冻结状态或其他 PM 账本。
- 不关闭或重开 R-0043 或任何其他风险；不恢复或冻结工程基线；不冻结 Schema/API；不进入下一阶段；不创建后续任务。
- 不使用真实 DB、真实用户数据、Vault、Tauri/IPC、文件导出、网络、云／第三方模型、同步、多设备、并发/WAL、恢复能力、L3 或外部用户。
- 若发现 P0/P1、明确合同 P2 bypass、Unknown、Not Implemented、hash/Evidence 冲突、历史保留失败或独立性不足，停止扩大结论并判为 Rework 或 Blocked；不得以 74 PASS 或测试数量抵消。

## 验收标准与回复

- 当前候选的 hash、可复现结构化结果与 P3-060 Evidence Manifest 一致，且旧 P3-031 Evidence 的历史属性与 hash 保留被证明。
- 独立性、隔离临时副本、反例矩阵、合法路径和事务语义均有可复核证据。
- 明确 P0/P1/P2/Unknown/Not Implemented 数量、退出码和是否存在 bypass。
- 结论只能是 Pass / Pass with Conditions / Rework / Blocked 之一，并严格按上述停止条件；即使 Pass，也只构成 PM 对 R-0043 的后续决策输入。
- 交付物区分事实、推断、建议、风险与需 PM 决定事项；会话回复按 `SESSION_REPORT_TEMPLATE.md` 简短回报。
