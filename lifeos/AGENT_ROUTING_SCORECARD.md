# LifeOS Agent Routing Scorecard

更新时间：2026-08-11

用途：帮助 PM 根据 Codex、WorkBuddy 及未来 Agent 的实际交付物质量，持续判断“哪类任务更适合交给哪个 Agent”。本文件只记录分派经验，不替代 PM 验收、独立评审、冻结状态或风险登记。

## 使用原则

- PM 主会话在验收专项交付物后，可追加一条 Agent 适配度记录。
- 评分服务于后续任务分派，不影响任务本身的 Accepted / Rework / Blocked 结论。
- 不因单次表现永久定性 Agent；至少观察 3 次同类任务后再调整默认分派。
- 若任务结果涉及 P0 / 高风险边界，仍以 PM Review、独立评审和 evidence 为准。

## 评分维度

每项 1-5 分，允许写 `N/A`。

| 维度 | 说明 |
|---|---|
| 范围纪律 | 是否严格按任务卡执行，未自行扩展或越权 |
| 证据质量 | 结论是否有文件、测试、截图、日志、引用或明确推理支撑 |
| 反例能力 | 是否主动发现边界、漏洞、自证循环或隐藏风险 |
| 工程执行力 | 是否能稳定修改 / 运行 / 复测 / 整理 evidence |
| 文档清晰度 | 交付物结构、术语、结论、风险和待确认问题是否清楚 |
| 上下文成本 | 是否按降耗规则读取材料，聊天输出是否简洁 |
| PM 可验收性 | PM 是否能快速判断结论、风险、路径和下一步 |

## 默认适配画像

| Agent | 当前推荐任务 | 谨慎任务 | 禁止事项 |
|---|---|---|---|
| Codex | 工程实现、技术 Spike、P0 修复、回归测试、evidence 整理、流程文件落地 | 高风险独立复评时应避免评审自己刚完成的实现 | 不得自行改 PM 账本、冻结资产、关闭风险或启动后续任务 |
| WorkBuddy | 独立评审、反例攻击、风险复核、产品 / 体验 / 证据链审查、文档一致性检查 | 大规模工程修改、需要复杂本地环境复跑的任务需先确认能力 | 不得自行改 PM 账本、冻结资产、关闭风险或启动后续任务 |
| TBD | 待观察 | 待观察 | 同上 |

## PM 分派判断规则

| 任务类型 | 默认推荐 Agent | 需要交叉验证时 |
|---|---|---|
| 工程实现 / 修复 | Codex | WorkBuddy 做独立评审或反例攻击 |
| 技术 Spike / 性能验证 | Codex | WorkBuddy 复核报告与证据链 |
| 独立评审 / 复评 | WorkBuddy | Codex 可仅作测试复跑辅助，不给最终评审结论 |
| 产品 / PRD / IA 初稿 | Codex 或 WorkBuddy，按任务重心决定 | 另一个 Agent 做范围和用户价值复核 |
| 条件整改 / 补丁 | 原执行 Agent 或 Codex | 另一个 Agent 复核是否关闭条件 |
| 决策准备 | PM 主会话主导，可让任一 Agent 准备选项 | 高风险决策需独立评审输入 |

## 适配度记录模板

PM 每次验收后按需追加：

| 日期 | 任务 ID | Agent | 任务类型 | PM 验收结论 | 主要强项 | 主要问题 | 建议后续更适合任务 | 是否调整默认分派 |
|---|---|---|---|---|---|---|---|---|

## 历史记录

| 日期 | 任务 ID | Agent | 任务类型 | PM 验收结论 | 主要强项 | 主要问题 | 建议后续更适合任务 | 是否调整默认分派 |
|---|---|---|---|---|---|---|---|---|
| 2026-08-11 | 初始化 | Codex | 项目流程落地 | N/A | 工程 / 文件操作 / 规则落地适配度高 | 独立复评自己刚完成的工程时需回避 | 工程实现、技术 Spike、规则文件维护、evidence 验证 | No |
| 2026-08-11 | 初始化 | WorkBuddy | 独立评审候选 | N/A | 适合作为外部评审、反例攻击和第二视角 | 工程复跑能力需通过实际任务观察 | 独立评审、风险复核、产品 / 体验 / 证据链挑错 | No |
| 2026-08-11 | LIFEOS-P3-012 | WorkBuddy | 独立工程复评 / P0 反例攻击 | Accepted | 只读复跑、39 条反例攻击、P0/P1/P2 分类、evidence 一致性检查清楚，未越权改文件或账本 | 本地预检不可用；Node 版本与 PM 复跑版本不同但结论被 PM 复核支持 | 独立评审、P0 复评、证据链复核、反例攻击 | No |
| 2026-08-11 | LIFEOS-P3-013 | Codex | 工程迁移 / P1 安全不变量补强 | Accepted / Pass with Conditions | 范围纪律好，集中在 P3-009 受控目录；工程实现、测试补充、evidence 更新和交付物路径清楚 | 本地预检不可用；新增写入口和证据依赖仍需交给独立评审会话做反例攻击 | 工程实现、受控迁移、测试与 evidence 整理；独立复评仍建议交给 WorkBuddy | No |
| 2026-08-11 | LIFEOS-P3-014 | WorkBuddy | 独立工程复评 / P1 反例攻击 | Accepted / PM adjusted to Pass with Conditions | 只读边界清楚，78 条反例攻击和 evidence 一致性检查扎实，发现了 `suggest()` 旧候选返回路径缺口 | 将该缺口定为 P2，PM 判断应上调为 P1 条件补丁 | 独立评审、反例攻击、证据链复核；风险分级仍由 PM 最终裁定 | No |
| 2026-08-11 | LIFEOS-P3-015 | Codex | P3 快车道 / P1 条件补丁 | Accepted | 范围纪律好，最小代码补丁、回归测试和 evidence 更新一致；PM 复跑与定向反例均通过 | 本地预检不可用；仍不适合作为自己后续高风险独立复评者 | P3 快车道工程补丁、受控测试迁移、evidence 更新、回归测试 | No |
| 2026-08-11 | LIFEOS-P3-016 | Codex | P3 快车道 / P1 条件补丁 | Accepted | 范围纪律好，覆盖 artifact/source generation mismatch 与三个消费入口；报告、测试、evidence 一致 | 本地预检不可用；仍不适合作为自己后续高风险独立复评者 | P3 快车道工程补丁、受控测试迁移、evidence 更新、回归测试 | No |
| 2026-08-11 | LIFEOS-P3-017 | Codex | P3 快车道 / P1 条件补丁 | Accepted | 范围纪律好，覆盖完整输入集合 ID 绑定、顺序稳定、非主 generation 变化与 evidence 一致性；PM 复跑和定向复现均通过 | 本地预检不可用；仍不适合作为自己后续高风险独立复评者 | P3 快车道工程补丁、受控测试迁移、evidence 更新、回归测试 | No |
| 2026-08-11 | LIFEOS-P3-018 | Codex | P3 快车道 / P1 条件补丁 | Accepted | 范围纪律好，覆盖只读 restore candidates、最小权威投影、旧包不复活与 evidence 一致性；PM 复跑和定向复现均通过 | 本地预检不可用；仍不适合作为自己后续高风险独立复评者 | P3 快车道工程补丁、受控测试迁移、evidence 更新、回归测试 | No |
| 2026-08-17 | LIFEOS-P3-038 | Codex | P0 候选 SQL 整改 / SQLite 回归 | Accepted / Remediation Regression Passed | DB 层补丁、两套回归、退出合同、hash 与 failure evidence 保留清楚；PM 临时副本复跑全部通过 | 不能独立复评自己的高风险整改；已知 DELETE 攻击面之外仍需独立反例扩展 | 工程整改、SQLite 合同测试、回归入口和 evidence 整理 | No |
| 2026-08-18 | LIFEOS-P3-039 | WorkBuddy | P0 整改隔离独立工程复评 / 反例攻击 | Accepted / Pass with Conditions | 独立复跑与 hash 核对完整；在已知用例外扩展 11 条 Authorization 子表变异反例并全部提供可复现 evidence | “Pass with Conditions”容易弱化 11 个 P1 的阻断性，PM 需明确只能进入整改、不允许风险关闭 | 权限 / 删除边界独立复评、反例攻击、evidence 复核 | No |
| 2026-08-20 | LIFEOS-P3-040 | Codex | P0 候选 SQL 权限边界整改 / 双模式回归 | Accepted / Remediation Regression Passed | SQLite trigger、状态转换与版本约束补丁集中；P3-031 42 项、P3-040 128 项回归、退出合同、hash 和 P3-039 evidence 保留完整，PM 临时副本复跑一致 | 不能独立复评自己的高风险权限整改；真实事务原子性、证据重放和 terminal 历史完整性仍需外部反例攻击 | 候选 SQL 工程整改、合同测试、受控回归和 evidence 整理 | No |
| 2026-08-20 | LIFEOS-P3-041 | WorkBuddy | P0 权限整改隔离独立复评 / 反例攻击 | Accepted / PM Adjusted to Rework | 独立确认既有 11 个 P1 关闭，并新增 38 个反例，稳定发现 7 个父 Authorization 字段 P1 与 12 个证据 / 历史 P2；evidence 可复现 | 将存在 7 个 P1 的结果写成 Pass with Conditions；R-0040 / R-0043 风险映射错误；评审日期和文件路径规范性不足 | 权限、删除、证据链独立评审和反例攻击；最终严重级别与风险归属由 PM 校正 | No |
| 2026-08-20 | LIFEOS-P3-042 | Codex | P0 候选 SQL 父 Authorization 安全包络整改 / 双模式回归 | Accepted / Remediation Regression Passed | 严格执行 `gpt-5.6-sol` + `xhigh` 与授权边界；八字段 NULL 安全 trigger、44/128/专项回归、hash 和原 evidence 保留完整；主动披露 created/revoked 元数据 P2 与历史 P2 数量口径变化 | 不能独立复评自己的高风险整改；相邻元数据组合攻击与最终严重级别需外部复评 | 候选 SQL 权限整改、SQLite 合同测试、隔离回归和 evidence 整理 | No |
| 2026-08-20 | LIFEOS-P3-043 | WorkBuddy | P0 权限整改隔离独立复评 / SQLite 替换写反例攻击 | Accepted / PM Adjusted to Rework | 独立发现 FK ON 下 `INSERT OR REPLACE(granted)` 可绕过 UPDATE trigger、保留子表并重新激活；R-0048 组合与合法路径覆盖有价值 | 再次在存在 P1 时写成 Pass with Conditions；三套回归日志/退出证据未落盘；P3-031 tests hash 映射错误，基础脚本未直接覆盖正文所述 policy_version 变体 | 权限/删除/证据链反例攻击；最终严重级别、hash归属和风险裁定必须由 PM复核 | No |
| 2026-08-20 | LIFEOS-P3-044 | Codex | P0 候选 SQL active 父记录替换／重建旁路整改与矩阵回归 | Accepted / Remediation Regression Passed | 严格使用 `gpt-5.6-sol` + `xhigh`；冲突 INSERT 与直接 DELETE trigger 集中，覆盖 id/版本键、REPLACE/UPSERT、FK/recursive、后端/事务原子性，四套 current 回归、hash 和 P3-043 preservation 完整，PM 临时树复跑一致 | 不能独立复评自己的高风险权限整改；真实 migration、并发/WAL、崩溃恢复与最终风险关闭仍需隔离复评和后续验证 | 候选 SQL 权限整改、SQLite 合同测试、组合矩阵回归和 evidence 整理 | No |
| 2026-08-20 | LIFEOS-P3-045 | Codex | P1 权限生命周期／证据链工程合同设计 | Accepted / Pass with Conditions | 方案比较、DB／应用／投影职责、AuditEntry/OutboxJob 边界、generation/时间原子性、terminal 清理和 18 条工程测试合同形成闭环，范围纪律清楚 | lifecycle command 的操作者身份含义与 audit 只追加／清理冲突仍需 PM 加护栏；不适合作为自身后续高风险实现的风险关闭评审者 | 候选 Schema 合同、数据库不变量、权限生命周期和受控测试设计 | No |
| 2026-08-20 | LIFEOS-P3-046 | Codex | P0 候选 SQL 权限生命周期／证据链实现与矩阵回归 | Accepted / PM Adjusted to Rework | lifecycle command、原子 retirement evidence、audit append-only、terminal 不可变与 248 项矩阵均可运行，原入口和 hash 可由 PM 复现，范围纪律与 evidence 组织较好 | 测试过度贴合自身 helper；漏测 future availability、无 owner/generation CAS completion、hash/Submission 绑定、tombstone 控制包络和通用 outbox cleanup，PM 新增反例为 2 P1 + 3 P2 | 复杂候选 SQL整改、矩阵回归、evidence 整理；高风险反例覆盖需 PM/隔离评审补强 | No |
