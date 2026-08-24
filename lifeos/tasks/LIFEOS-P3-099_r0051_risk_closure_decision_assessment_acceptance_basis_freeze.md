# LIFEOS-P3-099 Acceptance Basis Freeze｜R-0051 风险关闭决策评估

## 冻结信息

- 任务 ID：`LIFEOS-P3-099`
- ABF ID／版本：`ABF-P3-099-v1`
- 生效决策：`D-0410`
- 冻结时间：2026-08-22 23:35:00 CST (+0800)
- ABF 文件 SHA-256：由 PM 冻结后记录在任务卡与 D-0410；本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 要完成的单一结果：基于 P3-097 当前固定候选、P3-097 PM Pass、P3-098 全新隔离独立 Pass 与 PM 验证，形成一个独立、可复核、范围严格的 R-0051 风险关闭决策建议；结论只能是 `Recommend Limited Closure`、`Keep Open` 或 `Blocked`。
- 明确不冻结的产品需求：不冻结工程代码、Schema/API、技术架构、真实本地数据能力、产品 SLA 或 Stage 4 准入。
- 明确非范围：不修改工程；不关闭或重开 R-0051；不修改 PM 账本；不访问真实个人文件／DB／用户路径；不验证并发敌对替换、进程崩溃、网络文件系统、永久 OS 拒绝或生产部署；不启用网络、云、第三方、Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。

## 授权和能力边界

- 允许目录：只读项目工作区；只可新写 `lifeos/deliverables/LIFEOS-P3-099_r0051_risk_closure_decision_assessment.md`、`lifeos/reviews/LIFEOS-P3-099/`、`lifeos/local_prechecks/`，以及新建的 `/private/tmp/lifeos-p3-099-*` 固定非敏感临时目录。
- 允许数据与夹具：任务卡固定的项目文档、源码、Review、Evidence、Manifest 和新建固定非敏感 task-local SQLite／HTML／哨兵夹具；不得读取真实个人内容。
- 允许入口／接口：只读 hash／Manifest 复算、静态检查；可调用固定 P3-098 独立 runner 的公开复跑入口并把新输出写入 P3-099 自身 Evidence。
- 允许工具／环境：本地 shell、Python 标准库、SQLite、SHA-256；不联网。
- 严格只读资产：P3-094 至 P3-098 的任务卡、ABF、工程源码、测试、runner、交付物、Review、Evidence、Manifest；所有历史资产。
- 禁止能力与外部目标：真实文件／DB／路径、网络、云／第三方、凭据、Vault、Tauri/IPC、导出、同步、多设备、L3、外部用户及任何项目外目标。
- 投递前额外用户确认：本任务的创建已由用户明确要求；用户把任务卡路径投递到规定的新隔离会话才启动评估。真正关闭 R-0051 仍须任务完成后 PM 验收与用户再次明确确认。

## 引用的 L1 长期原则

- L1-1 数据主权：只读项目资产和固定非敏感 task-local 夹具，不触达真实个人数据或外部目标。
- L1-3 生命周期完整、L1-4 失败关闭：关闭建议必须覆盖 capture／render／clear、页面、SQLite、staging／sidecar、失败回执和不可逆完成点。
- L1-6 审计可信：source、时间、顺序、数量与结果须由实际 Evidence 支持。
- L1-7 Evidence 诚实：不得把 P3-097 自测或 PM Pass 单独替代 P3-098 独立结果，不得用汇总行批量推定未执行动作。
- L1-8 历史保全：全部输入与历史 Evidence 只读，before/after hash 一致。
- L1-9 授权不漂移：风险评估不等于风险关闭、资产冻结、真实能力启用或阶段授权。
- L1-10 可复核性：固定 hash、Manifest 和复跑入口须给出一致、可解释结果。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 会话与授权独立 | P0 | 新隔离会话未参与 P3-097 工程／PM 和 P3-098 独立／PM 验收；记录任务卡路径、会话类型、模型和精确接收时间 | `Blocked` 或 `Keep Open`，不得建议关闭 |
| ABF-I-02 | 固定输入身份 | P0 | 13 个固定根资产 hash 及其 Manifest 引用全部一致 | `Keep Open` 或 `Blocked` |
| ABF-I-03 | 历史失败链完整 | P0 | D-0379 至 D-0409 与 P3-094/095/096 已知页面、路径、Schema/source/audit、post-commit close/sidecar 事实逐项映射至当前关闭证据 | `Keep Open` |
| ABF-I-04 | 完成点与失败关闭 | P0 | live DB 原子发布唯一完成点；发布前失败零公开变化，发布后资源释放错误不把成功误报为失败 | `Keep Open` |
| ABF-I-05 | task-local 生命周期边界 | P0 | capture/list/snapshot/render/clear 与 CLI 的规范化、祖先链、最终链接、hardlink、特殊文件、页面和临时资产边界均有当前证据 | `Keep Open` |
| ABF-I-06 | Schema、来源与审计诚实 | P0 | canonical Schema 约束、固定 `local_capture` 来源、audit 数量／时间／顺序变异均 fail closed | `Keep Open` |
| ABF-I-07 | Evidence 独立且可复核 | P1 | P3-098 独立设计、runner、逐行结果、负门、Manifest 与 PM 复跑均可复算；无自证替代 | `Keep Open` 或 `Blocked` |
| ABF-I-08 | 决策语义准确 | P0 | 技术缺口得出 `Keep Open`，输入不可得得出 `Blocked`；只有全部有限关闭门满足才可 `Recommend Limited Closure` | 任务 Rework；不得关闭风险 |
| ABF-I-09 | 有限关闭范围与重开条件 | P0 | 建议逐项列明固定 hash、单进程／离线／task-local／固定非敏感夹具范围，以及实质 hash、并发、崩溃、真实 DB／路径、外部能力等重开触发器 | `Keep Open` |
| ABF-I-10 | 无状态越权 | P0 | 不修改代码、历史 Evidence、PM 账本、风险／冻结／基线／阶段状态；临时产物精确清理 | 任务 Rework 或 `Blocked` |

## 冻结验收矩阵

每行必须独立记录动作、结果与 Evidence；不得由总 PASS 数批量映射。

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | 会话／授权 | 新会话 | 核验独立性、投递和模型记录 | 全部满足 I-01 | 所有输入 | P3-099-AUTH-001 | `session_start.json`, `decision_matrix.json` |
| ABF-M-002 | 固定根资产 | 13 个任务／ABF／交付物／Review／Manifest | 逐文件 SHA-256 | 13/13 一致 | 文件 bytes | P3-099-HASH-002 | `input_hashes.json` |
| ABF-M-003 | P3-097 Engineering | 固定 Manifest | 非自指复算 | 16/16 一致 | 工程与 Evidence | P3-099-MAN-003 | `manifest_results.json` |
| ABF-M-004 | P3-097 PM Evidence | 固定 Manifest | 非自指复算 | 23/23 一致 | PM Evidence | P3-099-MAN-004 | `manifest_results.json` |
| ABF-M-005 | P3-098 Independent Evidence | 固定 Manifest | 非自指复算并核对逐行唯一 ID | 14/14、45 个 ID 唯一 | 独立 Evidence | P3-099-IND-005 | `manifest_results.json`, `decision_matrix.json` |
| ABF-M-006 | P3-098 PM Evidence | 固定 Manifest | 非自指复算 | 18/18 一致 | PM Evidence | P3-099-MAN-006 | `manifest_results.json` |
| ABF-M-007 | P3-098 独立 runner | 全新 `/private/tmp/lifeos-p3-099-*` | 复跑固定入口 | 45/45 PASS、退出 0、计数全零 | 固定输入 | P3-099-RUN-007 | `rerun/results.json`, `rerun.log` |
| ABF-M-008 | 已知风险链 | D-0379 至 D-0409、P3-094/095/096 | 逐项映射失败事实到 P3-097/098 当前证据 | 无未映射的完成定义缺口 | 历史资产 | P3-099-RISK-008 | `risk_coverage_matrix.json` |
| ABF-M-009 | 禁止能力／范围 | current runtime/CLI 和 Evidence | 静态核对关闭态及外推限制 | 禁止能力仍关闭 | 源码 bytes | P3-099-SCOPE-009 | `static_scope_scan.json` |
| ABF-M-010 | 决策门 | 前述独立结果 | 应用三分结论公式 | 结论与证据一致 | R-0051 仍 Open | P3-099-DEC-010 | `risk_decision.json` |
| ABF-M-011 | 关闭范围／重开条件 | 若推荐关闭 | 核对有限范围和触发器完备性 | 不作生产或真实能力外推 | 风险与冻结状态 | P3-099-BOUND-011 | `risk_decision.json` |
| ABF-M-012 | 历史保全／清理 | 完成评估后 | before/after hash 与临时残留扫描 | 输入无变化、残留为零 | 全部只读资产 | P3-099-CLEAN-012 | `input_hashes.json`, `temporary_residue.json` |

## Evidence 合同

- 可运行 runner／测试源码：P3-099 自身只读核验 runner；允许以 subprocess 调用固定 P3-098 runner，但不得复制或修改该 runner。
- 逐行结构化结果：`decision_matrix.json`，12 行均有唯一 test/execution ID。
- before／after 状态：固定输入 hash、Manifest 结果、R-0051 仍 Open 的账本快照。
- 日志／快照：复跑日志、风险覆盖矩阵、静态关闭态扫描。
- source／history hash：`input_hashes.json`，含 13 个根资产与 Manifest 递归结果。
- Manifest：`lifeos/reviews/LIFEOS-P3-099/evidence/MANIFEST.md`，非自指、逐文件 SHA-256。
- 复跑命令：必须给出从项目根目录可运行的精确命令。
- 临时清理：只删除本任务新建且精确核验的 `/private/tmp/lifeos-p3-099-*`；最终残留为零。

## 计数与 Pass 公式

- P0：越权状态变化、关闭建议缺少关键生命周期／路径／完成点证据、hash 冲突被忽略、真实能力外推。
- P1：独立性／Evidence 可复核性不足、历史失败链漏映射、重开条件实质缺失。
- P2：不改变结论但影响精确复核的文档或 Evidence 清洁问题。
- Unknown：必要事实无法确定。
- Not Implemented：冻结矩阵行没有实际执行或 Evidence。
- 任务完成公式：12/12 矩阵行有独立实际 Evidence；结论准确；自身 P0/P1/P2/Unknown/Not Implemented 均为 0；Manifest 一致；只读保全和清理成立。
- `Recommend Limited Closure` 额外公式：关闭依据的 P0/P1/P2/Unknown/Not Implemented 均为 0，所有 current/hash/independence/复跑/范围/重开门满足。
- `Keep Open`：发现任何实质技术缺口、合同失败或有限关闭门不满足；这是有效风险决策结果，不自动等于任务 Rework。
- `Blocked`：必要输入、授权、独立性或可运行环境不可得，无法诚实完成裁决。
- 允许的 N/A：仅当明确不适用且不削弱风险关闭依据；必须逐行说明，M-001 至 M-012 不允许整行 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：仅修正 P3-099 自身的同范围方法、Evidence、文案或遗漏；ABF、输入、风险边界和权限均不变。
- 必须新建任务条件：引用 `lifeos/ACCEPTANCE_GOVERNANCE.md`；任何工程整改、新能力、新输入基线、真实数据／路径、并发／崩溃／网络文件系统、风险边界、关闭范围、授权、架构、Schema/API、冻结、基线或阶段变化；两轮 Rework 后仍不满足。
- Blocked 条件：固定输入缺失／冲突、独立性无法成立、允许的本地复跑环境不可用且无安全替代。

## 候选基线与只读保全

- 候选输入 hash／Manifest：任务卡列出的 13 个固定根资产；P3-097 Engineering Manifest、P3-097 PM Manifest、P3-098 Independent Manifest、P3-098 PM Manifest 为递归完整性入口。
- 历史只读 hash／Manifest：P3-098 `source_history_hashes.json` 中 310 项历史集合，以及 P3-094/P3-095/P3-096 指定 Review/Evidence。
- 允许发生变化的文件：仅 P3-099 自身 deliverable、independent review、Evidence 和 local precheck；专项会话不得修改任何项目账本。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递；新会话在任何评估动作前有一次质疑窗口。
- PM 处理：如存在歧义，执行前停止；PM 可在未启动时更正并重新冻结。启动后不得改本 ABF。
- 最终冻结版本：`ABF-P3-099-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
