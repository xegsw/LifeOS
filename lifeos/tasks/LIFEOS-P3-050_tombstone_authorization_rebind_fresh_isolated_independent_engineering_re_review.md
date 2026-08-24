# LIFEOS-P3-050｜Tombstone 向 Authorization 改绑整改全新隔离独立工程复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定工作区、候选代码和合成测试数据，用于防御性代码审查、缺陷复现、修复验证与本地回归测试；不授权访问外部或第三方目标、真实用户数据或真实凭据，也不涉及未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避，不授权把测试能力用于本项目范围之外。文中“攻击、反例、旁路、改绑、权限提升”等术语仅指本地合成环境中的负向验证。任务卡既有目录权限、只读资产、用户确认、独立评审和停止条件继续完整有效；如实际操作需要超出这些边界，立即停止并回报 PM。

## 任务信息

- 任务 ID：LIFEOS-P3-050
- 任务名称：Tombstone 向 Authorization 改绑整改全新隔离独立工程复评
- 优先级：P0
- 任务类型：程序隔离 Rework 后的全新独立工程复评 / 防御性反例验证 / Evidence 核验
- 建议篇幅：2000-4000 字；完整日志、结构化结果、快照、环境和 hash 写入 Evidence
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：用户已采纳 P3-049 的 PM Rework，并明确授权创建全新隔离 Codex 复评任务。P3-049 技术矩阵通过，但因复用先前承载 P3-043 的 Codex 任务而未满足程序独立性；本任务必须在未承载任何其他 LifeOS 工作的全新 Codex 任务中重新形成独立验证链。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：本任务是 P0 整改链的独立复评，涉及 Authorization 撤回与 Tombstone 历史完整性、SQLite trigger 负向验证、Evidence 可信度和独立性证明；质量与可审计性优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务涉及 P0 整改独立复评、授权／撤回／删除历史与证据链核心边界，禁止改用 `gpt-5.6-terra`、`gpt-5.6-luna`、`gpt-5.5`、`gpt-5.4` 或其他配置；不得因 P3-049 技术结果已通过而降低模型、推理强度、攻击覆盖或 Evidence 要求。
- 必须升级条件：若 `xhigh` 无法独立形成攻击集合、无法判断 SQLite UPDATE OF/UPSERT/REPLACE/多行与事务语义，或 Evidence/hash/统计冲突，先在同一全新会话升级为 `gpt-5.6-sol` + `max`；若仍无法判断，停止并回报 PM，不扩大范围。
- 后备模型：`None`
- 是否需要后续独立评审：No；本任务本身即全新隔离独立复评。若结论 Rework 或 Blocked，后续只能由 PM 另行创建任务。
- 是否允许修改工程文件：No；P3-031、P3-046、P3-047、P3-048、P3-049 及全部历史工程／评审资产严格只读
- 是否允许修改项目账本：No
- 主责角色：独立 QA / Evidence Reviewer、技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：In Progress
- 实际派发：全新 Codex 任务 `01a02001-a5f2-7681-a2b8-e42f44a08efd`，host `local`，`gpt-5.6-sol` + `xhigh`，2026-08-21 00:29 CST；派发证明见 `lifeos/reviews/LIFEOS-P3-050/pm_dispatch_evidence/MANIFEST.md`

## 会话路由

- 是否建议新建会话：Yes，硬性条件
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 全新隔离独立工程复评
- 推荐复用的会话：None
- 禁止复用：P3-049 实际执行任务 `01a01dc5-4a0a-7820-b7fd-bb180be333e5`、任何 P3-046/P3-047/P3-048 工程执行任务、PM 主会话，以及任何曾承载其他 LifeOS 任务的 Codex 会话
- 会话判断理由：P3-049 已因复用旧任务被 PM 校正为 Rework。P3-050 的首要目的之一就是补足程序独立性；全新任务、全量重读、独立攻击设计、只读源资产和独立临时副本缺一不可。
- 是否需要独立性隔离：Yes，强制
- PM 派发证明：`lifeos/reviews/LIFEOS-P3-050/pm_dispatch_evidence/MANIFEST.md`
- 必须重新读取：
  - 根目录 `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/AGENT_BRIEFING_PACK.md`
  - `lifeos/PM_OPERATING_MODEL.md`
  - `lifeos/ROLE_MATRIX.md`
  - `lifeos/STAGE_GATES.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 可复用既有读取结果：None；这是全新会话，不继承任何 LifeOS 读取状态、计划、授权或未完成操作
- 必须因变化或不确定性重读：上述全部文件及本任务“输入材料”中的直接依赖
- 任务完成后是否建议保留会话：Yes，仅供 P3-050 的 PM 追问与 Evidence 澄清；不得在该会话执行工程整改、风险关闭或后续任务

## 背景

P3-048 对普通 Tombstone 经 UPDATE 改绑为 Authorization Tombstone 的路径进行了窄整改。P3-049 的技术验证记录了 P3-048 552 PASS、P3-047 等价回归 297 PASS、P3-031 70 PASS、原 PM-CE-06 8 PASS / 0 BYPASS，以及独立攻击 488 PASS / 0 BYPASS；PM 复跑可复现这些结果。

但 P3-049 实际复用了此前承载 P3-043 的 Codex 任务，不满足任务卡、D-0233 和用户要求的“全新隔离会话”硬条件。用户已于 2026-08-21 采纳该 Rework，并授权创建本任务。P3-050 不修改 P3-048 补丁；它必须在新的上下文中从合同和候选 SQL 出发，重新形成可审计的独立结论。

## 目标

在真正全新的 Codex 隔离会话中，独立判断 P3-048 是否关闭 PM-CE-06 及直接相邻 Tombstone→Authorization 改绑路径，同时证明回归、Evidence、历史失败资产、合法路径和事务原子性均可信。最终严格给出 Pass / Pass with Conditions / Rework / Blocked，不把技术通过自动外推为风险关闭、冻结、工程基线恢复或阶段切换。

## 范围

本任务必须覆盖：

- 核对 PM 派发证明，确认当前 Codex 任务为新建任务、使用 `gpt-5.6-sol` + `xhigh`，且未承载其他 LifeOS 任务；无法确认时判 Blocked 并回报 PM。
- 在读取 P3-049 的独立攻击脚本、结构化结果和详细攻击日志之前，先根据任务卡、P3-047 PM-CE-06、P3-048 补丁和当前候选 SQL 独立形成攻击计划，并保存为 `lifeos/reviews/LIFEOS-P3-050/evidence/independent_attack_plan.md`；记录 hash 后再进入交叉比较阶段。
- 独立创建 P3-050 的反例脚本和夹具；不得 import、调用、复制或机械改写 P3-048/P3-049 的攻击生成函数、场景表或 runner helper。历史 runner 只允许用于等价回归复跑。
- 在隔离临时副本复跑 P3-048 总入口，核对 P3-048 552、P3-047 等价 297、P3-031 70、退出码、只读保留和文件完整性；不得覆盖源 Evidence。
- 直接复跑原 P3-047 PM-CE-06 对当前候选 SQL 的八配置攻击，核对 8 PASS / 0 BYPASS。
- 独立攻击至少覆盖：
  - generic→Authorization、Authorization→generic、Authorization A→B；
  - `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 六字段的单独与复合变异；
  - accepted、active_blocked、cleanup_pending、cleanup_failed、vendor_limited、cleaned；
  - NULL、cleanup_status/updated_at 组合、no-op 与合法 cleanup retry/cleaned 路径；
  - UPSERT、INSERT OR REPLACE、UPDATE OR REPLACE、冲突 INSERT、DELETE/reinsert；
  - 单行、多行、显式事务、失败语句原子性和调用方 rollback 边界；
  - memory/file、foreign_keys ON/OFF、recursive_triggers ON/OFF 的八配置矩阵；
  - 文件型 SQLite 的 integrity_check、quick_check 和 foreign_key_check。
- 在独立攻击计划和首轮结果封存后，只读查看 P3-049 Review、脚本、结果和 Evidence，比较覆盖差异与统计，不将 P3-049 自述当作本任务证据替代品。
- 核对 P3-046/P3-047/P3-048/P3-049 历史失败 Evidence、Review 和只读基线没有被覆盖；核对 P3-048 关键 Evidence hash 与当前文件一致。
- 明确列出 P0、P1、P2 bypass、新增 P2、P3 Observation、Not Implemented、Unknown 数量和退出码。

## 非范围

- 不修改 P3-031 候选 SQL、合同测试、runner 或 Evidence。
- 不修改 P3-046/P3-047/P3-048/P3-049 的任务卡、交付物、Review、PM Review、反例或任何原 Evidence。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`FREEZE_STATUS.md` 或其他 PM 账本。
- 不关闭 R-0048、R-0049 或其他风险，不冻结 Schema/API/migration/工程基线，不恢复工程基线，不进入下一阶段。
- 不执行真实 migration，不连接或写入真实用户 DB、真实 Vault、真实用户文件、真实 Tauri/IPC、云或第三方模型，不启用向量、同步、多设备、L3 或外部用户。
- 不把本任务扩展为工程整改、生产架构、身份认证、删除 SLA 或风险关闭决策任务。
- 不因 Cyber safeguards 提示删减准确术语、拆分隐蔽步骤、降低模型或测试强度；若外部安全机制阻塞，保留边界并回报 PM。

## 输入材料

按以下顺序读取：

1. 本任务“会话路由”列出的基础文件和模板。
2. `lifeos/reviews/LIFEOS-P3-050/pm_dispatch_evidence/MANIFEST.md`。
3. `lifeos/reviews/LIFEOS-P3-049_pm_review.md`，只用于理解 Rework 原因、技术统计和不可外推边界。
4. `lifeos/reviews/LIFEOS-P3-048_pm_review.md`。
5. `lifeos/reviews/LIFEOS-P3-048/evidence/MANIFEST.md`。
6. `lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`。
7. `lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`。
8. `lifeos/reviews/LIFEOS-P3-047_pm_review.md`。
9. `lifeos/reviews/LIFEOS-P3-047/evidence/MANIFEST.md`。
10. `lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py` 与 `counterexample_results.json`。
11. 当前 P3-031 候选 SQL、合同测试和验证入口。

延迟读取：只有在 P3-050 的 `independent_attack_plan.md` 与首轮独立结果已保存并记录 hash 后，才读取：

- `lifeos/reviews/LIFEOS-P3-049/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-049/evidence/MANIFEST.md`
- P3-049 独立攻击脚本、结构化结果、详细日志与快照

## Evidence 与交付物

独立评审：

`lifeos/reviews/LIFEOS-P3-050/independent_review.md`

独立 Evidence Manifest：

`lifeos/reviews/LIFEOS-P3-050/evidence/MANIFEST.md`

Evidence 至少包括：

- `independent_attack_plan.md` 及封存 hash
- P3-050 自建独立反例脚本
- 结构化结果 JSON
- 回归、PM-CE-06、独立攻击与文件完整性日志
- before/after hash、历史 Evidence 保留清单与环境快照
- 临时副本路径、测试配置矩阵、退出码和命令清单

本地预检：

`python3 lifeos/tools/local_precheck.py lifeos/reviews/LIFEOS-P3-050/independent_review.md`

本地模型不可用、超时或输出为空时，按项目规则记录并继续人工评审，不得阻塞任务。

## 判定标准

- `Pass`：全新任务与程序隔离证明成立；独立计划在查看 P3-049 攻击资产前已封存；原 PM-CE-06 和独立相邻攻击全部 fail closed；合法路径无回退；P3-048/P3-047/P3-031 回归与 hash 可复现；0 P0 / 0 P1 / 0 P2 bypass；无 Not Implemented/Unknown。
- `Pass with Conditions`：程序独立性成立且无 P0/P1，只有不影响明确合同的 P2 清洁项；必须列出条件、范围和失效条件。不得把会话隔离缺口降级为条件通过。
- `Rework`：发现任一 P0/P1，或发现违反 PM-CE-06／Tombstone 自 INSERT 起不可改绑合同的 P2 bypass，或 Evidence/统计/只读保留不可信。
- `Blocked`：当前任务并非全新会话、无法证明程序隔离、关键文件不可访问、环境无法执行且无等价只读验证方案、外部安全机制持续阻塞，或证据冲突无法判断。
- 不得因 P3-049 已有 488 PASS 或 PM 复跑通过而默认 Pass；P3-050 必须形成自己的独立攻击计划、脚本、结果和 Evidence。

## 角色检查点

- 独立 QA / Evidence Reviewer：证明新任务、延迟读取、独立计划、脚本来源、hash、退出码、失败原子性和覆盖矩阵可信。
- 技术架构负责人：检查 SQLite trigger 的 OLD/NEW、UPDATE OF、NULL 安全比较、UPSERT/REPLACE、多行、跨 trigger 首错误与事务 rollback 语义。
- AI 信任与安全负责人：检查 Authorization cleanup 历史、撤回证据和控制包络是否仍可伪造、改绑或形成半状态。
- 数据 / 领域模型负责人：检查 generic Tombstone 合法语义是否被意外全局冻结，并确认候选 SQL 不变量没有被误写为核心领域模型冻结。

## 验收标准

- 使用 `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md` 形成完整独立评审。
- 当前 Codex 任务确为新建任务，PM 派发证明和专项 Review 对会话状态的陈述一致。
- P3-050 独立攻击不是 P3-048/P3-049 runner 或攻击函数的重复调用／机械复制；攻击计划在延迟输入揭示前已封存。
- 脚本、结构化结果、日志、快照、hash 与 MANIFEST 保存到 P3-050 Evidence，且不覆盖任何历史资产。
- 结论严格使用 Pass / Pass with Conditions / Rework / Blocked，并明确 Gate 2、Gate 3、Gate 4、P0/P1/P2/P3/Not Implemented/Unknown。
- 完成本地预检，或按规则记录允许跳过原因。
- 聊天回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、Review/Evidence/预检路径、实际模型配置和是否需要 PM 决策。

## 限制与停止条件

- 工程和历史资产严格只读；所有复跑在隔离临时副本进行。
- 只允许写入 P3-050 自身 Review、Evidence 和本地预检目录。
- 命中 P0/P1、违反明确合同的 P2、数据损坏、真实能力触达、Evidence 冲突、会话隔离不成立或 safeguards 阻塞时，不扩大为修复任务；完成可得证据记录后停止并回报 PM。
- 不自行创建、启动或分派后续任务，不自行更新 PM 账本、关闭风险、冻结资产、恢复基线或进入下一阶段。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中只输出任务状态、3-8 条摘要、独立 Review 路径、Evidence Manifest 路径、本地预检路径、实际模型配置和是否需要 PM 决策；不要粘贴完整日志或报告正文。
