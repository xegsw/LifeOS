# LIFEOS-P3-049｜Tombstone 向 Authorization 改绑整改隔离独立工程复评

## 任务信息

- 任务 ID：LIFEOS-P3-049
- 任务名称：Tombstone 向 Authorization 改绑整改隔离独立工程复评
- 优先级：P0
- 任务类型：隔离独立工程复评 / 反例攻击 / Evidence 核验
- 建议篇幅：2000-4000 字；完整日志、结构化攻击结果、快照、环境和 hash 写入 evidence
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：用户明确说明 WorkBuddy 额度不可用并要求复评任务交给 Codex。Codex 可在新建隔离会话中只读复跑、构造独立 SQLite 反例和核验 Evidence；必须与 P3-048 工程执行会话隔离，避免同会话自证。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：本任务是 P0 整改链的独立复评，涉及权限撤回、删除历史、Tombstone 控制包络、替换写语义和 evidence 可信度；需要主动寻找执行侧矩阵之外的反例，质量与独立性优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：独立评审 Rework 处理、权限／撤回／删除／证据链核心边界、风险关闭前置判断均禁止降级；不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置，不得因已知补丁仅一行 trigger 条件而降级。
- 必须升级条件：若 `xhigh` 无法形成独立于 P3-048 runner 的攻击集合，无法判断 SQLite UPDATE OF/UPSERT/REPLACE/多行语义，或 evidence、hash、统计互相冲突，先升级为 `gpt-5.6-sol` + `max`；若发现新增 P0/P1、数据不可恢复风险、真实能力触达、核心领域模型／技术架构／AI 权限边界必须变化，停止扩大范围并回报 PM。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选不可用时使用 `gpt-5.5` + `xhigh`，记录原因、实际配置和影响；不能满足禁止降级条件时停止，不得静默换模。
- 是否需要后续独立评审：No；本任务本身即隔离独立复评。若结论 Rework/Blocked，后续整改和复评仍由 PM 另行创建任务。
- 是否允许修改工程文件：No；工程资产严格只读
- 是否允许修改项目账本：No
- 主责角色：独立 QA / Evidence Reviewer、技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 隔离独立工程复评
- 推荐复用的会话：不复用任何 P3-046、P3-047、P3-048 工程执行或 PM 验收会话
- 会话判断理由：P3-049 必须独立复评 P3-048 的 P0 整改链成果。虽然执行 Agent 与复评 Agent 都是 Codex，但必须通过全新会话、只读工程资产、隔离临时副本和独立攻击集合保持上下文与证据隔离；WorkBuddy 额度不可用只改变 Agent 路由，不降低独立评审标准。
- 是否需要独立性隔离：Yes，强制
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/AGENT_BRIEFING_PACK.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/tasks/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`
  - `lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.sh`
  - `lifeos/reviews/LIFEOS-P3-048_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-048/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-047_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-047/evidence/counterexample_results.json`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/RISK_LOG.md` 中 R-0048、R-0049
  - `lifeos/DECISION_LOG.md` 中 D-0230 至 D-0233
- 可复用既有读取结果：None；必须使用新建隔离会话，不继承 P3-048 执行会话读取状态
- 必须因变化或不确定性重读：上述全部直接输入；若发生上下文压缩、输出截断或文件版本不明，按 AGENTS.md 规则补读到 EOF
- 任务完成后是否建议保留会话：Yes，仅供同一独立复评线的 PM 追问或证据澄清；不得在该会话修改工程或执行后续整改

## 背景

P3-047 因 PM-CE-06 发现 generic Tombstone 可经 UPDATE 改绑为 Authorization Tombstone，被 PM 校正为 Rework。P3-048 将不可变 trigger 从仅检查 OLD 为 Authorization，补强为 OLD 或 NEW 任一侧涉及 Authorization时冻结六字段控制包络。

P3-048 执行侧声称 552 PASS；PM 隔离复跑得到 P3-048 552 PASS、P3-047 当前协议等价 297 PASS、P3-031 70 PASS、40/40 只读文件保持一致，并直接运行原 PM-CE-06 得到 8 PASS / 0 BYPASS。用户已采纳该 PM 验收结论，并因 WorkBuddy 无额度明确要求复评任务交给 Codex。

本任务不是重复运行执行侧测试，而是由全新 Codex 隔离会话主动攻击补丁、核查证据链并判断是否 Pass / Pass with Conditions / Rework / Blocked。

## 范围

本任务必须覆盖：

- 在隔离临时副本只读复跑 P3-048 总入口，核对 552/297/70、退出码、40 文件保留与文件完整性统计。
- 直接运行原 P3-047 PM-CE-06 脚本攻击新候选 SQL，确认 8 配置实际结果。
- 不复用 P3-048 runner 的攻击生成逻辑，独立实现新的反例脚本并至少覆盖：
  - generic→Authorization、Authorization→generic、Authorization A→B；
  - OLD/NEW subject 类型组合与 `UPDATE OF` 触发语义；
  - 六控制字段单独、复合、NULL/非 NULL（若 Schema 允许）与 no-op 语义；
  - cleanup_status / updated_at_ms 与身份字段同语句组合；
  - `UPDATE OR REPLACE`、`INSERT OR REPLACE`、UPSERT、冲突 INSERT、DELETE/reinsert 及多行 UPDATE；
  - memory/file、FK ON/OFF、recursive triggers ON/OFF、autocommit/transaction/rollback；
  - 六 cleanup 状态与合法 retry/cleaned/generic 更新路径；
  - 触发失败后的整句／事务原子性、行身份、Authorization、AuditEntry、OutboxJob、Submission 与 Tombstone 快照无半状态。
- 静态核查 trigger 顺序、WHEN 条件、UPDATE OF 列表、INSERT/DELETE/REPLACE 相邻 guard，寻找执行侧可能因其他 trigger 先失败而掩盖的目标 guard 缺口。
- 核对执行 Evidence 中所有关键 hash、统计、只读保留与当前文件一致；不得仅信任 MANIFEST 声明。
- 明确区分：已知 PM-CE-06 是否关闭、是否发现新增 P0/P1/P2、资产是否仍需保持未冻结、R-0048/R-0049 是否只能作为风险决策输入。

## 非范围

- 不修改 P3-031 候选 SQL、测试、runner 或 evidence。
- 不修改 P3-046/P3-047/P3-048 任务卡、报告、Review、PM 反例或任何原 Evidence。
- 不修改 PM 账本，不关闭风险，不冻结资产，不恢复工程基线，不进入下一阶段。
- 不执行真实 migration，不连接真实 DB/Vault/用户文件/Tauri/IPC，不启用网络、云／第三方模型、向量、同步、多设备、L3 或外部用户。
- 不把独立复评扩展为生产架构、身份认证、删除 SLA 或风险关闭决策任务。
- 不自行要求工程执行会话立即修复；若发现问题，只在独立 Review 中分级并回报 PM。

## Evidence 与交付物

独立评审：

`lifeos/reviews/LIFEOS-P3-049/independent_review.md`

独立 Evidence Manifest：

`lifeos/reviews/LIFEOS-P3-049/evidence/MANIFEST.md`

独立反例脚本与结构化结果建议：

- `lifeos/reviews/LIFEOS-P3-049/evidence/independent_counterexample_attacks.py`
- `lifeos/reviews/LIFEOS-P3-049/evidence/counterexample_results.json`

完整日志、环境、hash、快照和隔离复跑结果全部写入 P3-049 evidence 目录。不得覆盖任何工程或历史评审 Evidence。

## 判定标准

- `Pass`：原 PM-CE-06 和独立相邻攻击全部 fail closed；合法路径无回退；P3-048/P3-047/P3-031 回归与 hash 可复现；0 P0 / 0 P1 / 0 P2 bypass；无 Not Implemented/Unknown。
- `Pass with Conditions`：无 P0/P1，只有不影响已知安全合同的明确 P2 清洁项，且任务卡允许保留；必须列出条件、范围和失效条件。
- `Rework`：发现任一 P0/P1，或发现违反 PM-CE-06／Tombstone 自 INSERT 起不可改绑明确合同的 P2 bypass，或 evidence/统计/只读保留不可信。
- `Blocked`：关键文件不可访问、环境无法执行且无等价只读验证方案、证据冲突无法判断，或无法保持与执行会话隔离。
- 不得因执行侧 552 条和 PM 复跑通过而默认 Pass；必须有独立攻击集合和结构化结果。

## 角色检查点

- 独立 QA / Evidence Reviewer：证明测试不是执行侧 helper 的重复自证，核对实际文件、hash、退出码、失败原子性和覆盖矩阵。
- 技术架构负责人：检查 SQLite trigger 的 OLD/NEW、UPDATE OF、UPSERT/REPLACE、多行与事务语义是否形成最小且可验证的不变量。
- AI 信任与安全负责人：检查 Authorization cleanup 历史、撤回证据和控制包络是否仍可伪造或改绑。
- 数据 / 领域模型负责人：检查 generic Tombstone 合法语义是否被意外全局冻结，以及候选 SQL 不变量是否被误写成核心领域模型冻结。

## 验收标准

- 使用 `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md` 形成完整独立评审。
- 独立反例不是简单调用 P3-048 runner 的同一函数；脚本、结果、日志和快照保存到 P3-049 evidence。
- 评审结论严格使用 Pass / Pass with Conditions / Rework / Blocked，并按上述标准分级。
- 明确 Gate 2、Gate 3、Gate 4 结论，列出 P0/P1/P2 数量和风险影响。
- 完成本地预检，或按规则记录本地模型不可用／超时等允许跳过原因。
- 聊天回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、Review/Evidence/预检路径、实际模型和是否需要 PM 决策。

## 限制与停止条件

- 工程与历史资产严格只读；所有复跑在隔离临时副本进行。
- 不修改 PM 账本、风险状态、冻结状态或任务状态。
- 命中 P0/P1、违反明确合同的 P2、数据损坏、真实能力触达或 evidence 冲突时，不扩大为修复任务；完成证据记录后停止并回报 PM。
- 不自行创建、启动或分派后续任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中只输出任务状态、3-8 条摘要、独立 Review 路径、Evidence Manifest 路径、本地预检路径、实际模型配置和是否需要 PM 决策；不要粘贴完整日志或报告正文。
