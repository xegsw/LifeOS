# LIFEOS-P3-097｜不可逆提交完成点边界 Acceptance Basis Freeze

## 冻结信息

- 任务 ID：`LIFEOS-P3-097`
- ABF ID／版本：`ABF-P3-097-v1`
- 生效决策：D-0406
- 冻结时间：2026-08-22（专项会话启动前）
- ABF 文件 SHA-256：由 PM 冻结后记录在任务卡与 D-0406；本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 要完成的单一结果：把 live DB 原子发布确定为 capture 的唯一不可逆完成点，使所有失败路径在该点前 fail closed，且该点后的资源释放或状态检查错误不得把已经完成的成功错误报告为失败；新捕获与幂等重复都必须保持返回语义、持久化状态、页面状态和 task-local 残留一致。
- 明确不冻结的产品需求：不冻结业务 Schema/API、产品功能、生产部署方式、真实用户 DB 迁移、并发／崩溃恢复方案或后续风险处置。
- 明确非范围：不重新验收 P3-094/P3-095/P3-096 的历史结论；不新增公开状态、入口或业务字段；不处理真实个人文件、既有个人数据库、真实用户路径、Vault、Tauri/IPC、网络、云、第三方、同步、多设备、L3、外部用户、风险关闭、冻结、基线恢复或 Stage 4。

## 授权和能力边界

- 允许目录：只允许新建或修改 `lifeos/engineering/LIFEOS-P3-097/` 与 `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`。
- 允许数据与夹具：仅项目工作区只读候选，以及 `/private/tmp/lifeos-p3-097-*` 中新建的固定非敏感文本、task-local SQLite、HTML、哨兵和失败注入夹具。
- 允许入口／接口：候选已有 Python runtime 和 CLI；公开成功状态保持 `saved`／`idempotent_repeat`，公开失败合同保持既有 fail-closed 语义。
- 允许工具／环境：离线本地 shell、Python 标准库、SQLite、hash 工具及任务提交的 runner；不得联网。
- 严格只读资产：P3-094、P3-095、P3-096 的任务、工程、交付物、Review、PM Evidence、Engineering Evidence 和 Manifest；项目账本、风险与冻结记录。
- 禁止能力与外部目标：真实个人数据或既有 DB、工作区外既有文件、网络、云、第三方、凭据、Vault、Tauri/IPC、导出、同步、多设备、L3、外部用户，以及任何攻击能力扩展。
- 投递前额外用户确认：用户已于 D-0406 明确要求创建本任务；工程执行仍须由用户把本任务卡明确路径投递至一个全新隔离 Codex 工程会话。PM 主会话中的创建或提及不构成执行授权。

## 引用的 L1 长期原则

- L1-1 数据主权与边界：所有读写、临时文件、sidecar、页面和清理均限于本轮新建 task-local 目录；历史资产保持只读。
- L1-2 原文与来源真实性：固定夹具的 capture、source 与 audit 关系不得被静默伪造、错标或重排。
- L1-3 失败关闭与状态诚实：返回失败不得同时留下已发布 capture/audit 或页面变化；已完成的不可逆成功不得被后续资源释放错误错误报告为失败。
- L1-4 数据生命周期完整：DB、audit、页面、sidecar、staging 与临时产物必须形成一致终态，不允许半成品或不可解释残留。
- L1-5 可复核与证据真实性：每个冻结矩阵行必须由独立夹具和实际执行 ID 支撑，不得用 suite 总结果批量代替。
- L1-6 最小权限与默认关闭：不扩大目录、数据、入口、Schema/API、外部能力或风险权限。
- L1-7 阶段与治理诚实：本任务通过也只形成候选，不代表冻结、风险关闭、基线恢复、独立复评通过或 Stage 4 准入。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | live DB 原子发布是唯一不可逆完成点 | P1 | 发布前所有可能改变返回结果的写入、验证、页面失效和临时清理均完成；发布只有一次且可定位 | live DB、audit、页面和哨兵保持 before 状态，且无 sidecar／staging／temp 残留 |
| ABF-I-02 | 发布后的错误不得推翻准确成功 | P1 | live 发布完成后，连接／FD 释放或只读终态观察失败不得向调用方返回失败；返回状态与已持久化结果一致 | 不得出现“调用方收到失败但 capture/audit 已完成”的终态 |
| ABF-I-03 | 新捕获具有完整原子生命周期 | P1 | `saved` 时恰好新增一条 capture 与对应 audit，旧安全页面按合同失效，且无临时残留 | 任一发布前失败均保持 DB bytes/hash、audit、页面和哨兵不变 |
| ABF-I-04 | 幂等重复具有完整原子生命周期 | P1 | `idempotent_repeat` 不新增 capture，按既定合同追加或保持精确 audit，页面与残留状态一致 | 任一发布前失败均保持 live 状态不变，不得产生伪重复或半条 audit |
| ABF-I-05 | 页面失效与 DB 发布保持一致 | P1 | 会导致旧页面不再可信的 capture 在发布前完成安全失效准备；成功后不存在可展示旧状态的页面 | 页面操作失败时不得发布 DB；返回失败时页面与 live DB 同时保持 before 状态 |
| ABF-I-06 | shadow／sidecar／staging 永不成为权威数据 | P1 | 候选 DB、journal/WAL/SHM、页面 staging 和其他 temp 仅存在于 task-local 目录，成功及受支持失败终态均为零 | 可注入的暂态清理失败在发布前经有界恢复；仍无法清理则停止且不得发布 live DB |
| ABF-I-07 | 路径与历史边界持续关闭 | P0 | 所有生命周期文件均在同一 task-local 目录且完整目录链、规范化路径和文件类型检查通过；历史 hash 不变 | 越界、链接链或特殊文件在任何文件／DB 变化前拒绝 |
| ABF-I-08 | Evidence 逐行真实执行 | P1 | 每个矩阵行有唯一夹具、唯一测试 ID、独立 before/after 与结构化结果；缺行时 runner 非零退出 | 任一缺行、复用冒充或不可复核项计入 Not Implemented，不得提交 Pass |

## 冻结验收矩阵

每行必须独立创建夹具、执行动作、断言结果并生成 Evidence；不得由总测试结果批量映射。失败注入只针对确定、有限、可复现的本地异常；永久 OS 拒绝不伪装为可恢复成功。

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | runtime capture | 合法 existing DB、无 sidecar、存在安全旧页 | 新内容正常捕获 | 返回 `saved`；恰好一条 capture/audit；旧页失效；零残留 | 哨兵及目录边界 | P3-097-M001 | before/after、结果、日志 |
| ABF-M-002 | CLI capture | 与 M-001 独立夹具 | 新内容正常捕获 | 与 runtime 同一终态合同 | 哨兵及目录边界 | P3-097-M002 | before/after、结果、日志 |
| ABF-M-003 | runtime capture | 已有相同 active capture | 正常幂等重复 | 返回 `idempotent_repeat`；capture 不增加；audit 精确符合既有合同；零残留 | 原 capture、哨兵 | P3-097-M003 | before/after、audit diff |
| ABF-M-004 | runtime capture | 合法 existing DB | 候选写入／commit 在 live 发布前失败 | 明确失败且无 live 变化、无残留 | DB bytes/hash、audit、页面、哨兵 | P3-097-M004 | 注入点、before/after |
| ABF-M-005 | runtime capture | 候选已 commit、live 未发布 | 候选连接 close 抛错 | 明确失败且不发布 live DB；零残留 | live DB、audit、页面、哨兵 | P3-097-M005 | 注入点、before/after |
| ABF-M-006 | runtime capture | 候选已 commit、live 未发布 | 候选 close 留下 journal/WAL/SHM | 在发布前识别并安全清理；若受支持恢复成功则继续，否则失败且不发布 | live DB、audit、页面、哨兵 | P3-097-M006 | sidecar 快照、结果 |
| ABF-M-007 | runtime capture | 候选 sidecar 待清理 | 第一次清理固定失败、随后允许重试 | 有界恢复后按真实结果成功或失败；绝不半发布；终态零残留 | 失败分支的 live 状态、哨兵 | P3-097-M007 | 尝试次数、终态快照 |
| ABF-M-008 | runtime capture | 合法 existing DB、存在安全旧页 | 页面失效／staging 操作在发布前失败 | 明确失败且不发布 DB；页面保持 before 可解释状态；零残留 | DB bytes/hash、audit、哨兵 | P3-097-M008 | 页面与 DB before/after |
| ABF-M-009 | runtime capture | 合法 existing DB | task-local 父目录稳定性／路径检查失败 | 在任何变化前拒绝 | DB、audit、页面、哨兵 | P3-097-M009 | 路径检查日志、hash |
| ABF-M-010 | runtime capture | 候选准备完成 | 候选 Schema／audit／完整性验证失败 | 明确失败且不发布；零残留 | live DB、audit、页面、哨兵 | P3-097-M010 | 验证结果、before/after |
| ABF-M-011 | runtime capture | 所有发布前条件完成 | live DB 原子发布固定失败 | 明确失败；live 权威状态保持 before；页面不产生与 DB 不一致终态；零残留 | audit、哨兵、目录边界 | P3-097-M011 | 发布注入、终态快照 |
| ABF-M-012 | runtime capture | live DB 原子发布已成功 | 发布后的连接 close 固定抛错 | 仍准确返回成功；DB/audit/page 与成功一致；零残留 | 哨兵、目录边界 | P3-097-M012 | 返回值与持久化核对 |
| ABF-M-013 | runtime capture | live DB 原子发布已成功 | 发布后的路径 gate FD close 固定抛错 | 仍准确返回成功，不生成第二完成点或假失败 | 已发布 DB/audit/page、哨兵 | P3-097-M013 | 返回值、调用顺序、hash |
| ABF-M-014 | runtime capture | live 发布前、需要最终 sidecar/temp 扫描 | 扫描固定失败 | 明确失败且不发布；零任务产物残留 | live DB、audit、页面、哨兵 | P3-097-M014 | 扫描注入、before/after |
| ABF-M-015 | runtime capture | 已有相同 active capture | 在 M-004 至 M-014 适用失败点执行幂等重复子矩阵 | 每个失败点均满足 I-02/I-04/I-06，不得新增 capture 或不完整 audit | live DB、页面、哨兵 | P3-097-M015-* | 每子行独立 ID 与状态 |
| ABF-M-016 | runner | 故意缺少矩阵行、fixture 断言或唯一执行 ID | 运行 Evidence 门 | Not Implemented 非零且 runner 非零退出 | 已生成 Evidence 不得冒充全通过 | P3-097-M016 | negative-gate result |
| ABF-M-017 | runner | 全部矩阵行独立具备 | 运行完整验收 runner | 行数、唯一测试 ID、实际执行记录完全匹配且退出 0 | history hash、临时清理为零 | P3-097-M017 | results、executed IDs、Manifest |

## Evidence 合同

- 可运行 runner／测试源码：提交 task-local runner、unit tests 和全部失败注入 fixture；PM 可在全新 `/private/tmp` 目录复跑。
- 逐行结构化结果：`acceptance_matrix.json` 逐行记录行 ID、测试 ID、fixture ID、实际动作、断言和 PASS/FAIL；M-015 每个子失败点具有独立执行 ID。
- before／after 状态：记录 DB 文件存在性、bytes/hash、captures、audit、页面、sidecar、staging、temp、哨兵和目录边界；只读取本任务固定测试内容。
- 日志／快照：记录完成点调用顺序、失败注入点、返回状态、清理尝试及终态；不得包含真实数据。
- source／history hash：复算候选源码和全部指定历史 Manifest；P3-094/P3-095/P3-096 历史不得漂移。
- Manifest：列出所有提交 Evidence 的相对路径、SHA-256、用途和生成方式，不得自指，不得覆盖工程或 PM 历史 Evidence。
- 复跑命令：给出离线、确定性、从全新 `/private/tmp` 夹具开始的完整命令和预期退出码。
- 临时清理：成功、失败、runner 自检和 PM 复跑结束后精确清理本轮目录；提交残留报告必须为零。

## 计数与 Pass 公式

- P0：0
- P1：0
- P2：0
- Unknown：0
- Not Implemented：0
- Pass 公式：全部 ABF-I-01 至 I-08 与 ABF-M-001 至 M-017（含 M-015 每个适用子行）独立 PASS；runner 退出 0；source/history hash 一致；task-local 临时残留为 0；不存在范围、授权或 Evidence 冲突。
- 允许的 N/A：无。若实现证明某个已冻结失败点在当前结构中不可达，仍须用结构断言和独立 Evidence 证明其不可达，不得静默标 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：PM 或后续独立评审发现的问题仍可直接映射到本 ABF，且不改变用户结果、目录、数据、入口、公开语义、能力、授权、Schema/API 或风险边界。
- 必须新建任务条件：达到两次正式 Rework 后仍未通过；需要修改本 ABF；需要新增公开状态／入口、改变 `saved`／`idempotent_repeat` 语义、Schema/API、目录、数据、外部能力、架构承诺、风险处置、冻结或阶段边界；或实现只能通过允许持久残留、假成功、假失败来满足当前标准。
- Blocked 条件：候选／历史 hash 冲突且无法在只读范围解释；固定夹具无法在授权环境复现；需要访问真实数据／外部系统；或需要永久 OS 拒绝下保证物理上不可能的零残留。Blocked 不等于 Pass，也不得扩大授权绕过。

## 候选基线与只读保全

- 候选输入 hash／Manifest：以 `lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/MANIFEST.md`、`lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/MANIFEST.md` 及其中固定源码快照为只读输入；任务卡记录 live candidate 的已复算 hash。
- 历史只读 hash／Manifest：P3-094/P3-095/P3-096 各 Engineering/PM Manifest 及 D-0405 记录的历史集合；执行前后均须复算。
- 允许发生变化的文件：仅 `lifeos/engineering/LIFEOS-P3-097/` 与 `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未启动；等待新隔离专项会话核对。
- PM 处理：若专项会话在任何工程动作前指出真实歧义，PM 只可解释文字而不得实质改变冻结标准；实质变化必须关闭 P3-097 并新建任务。
- 最终冻结版本：`ABF-P3-097-v1`
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
