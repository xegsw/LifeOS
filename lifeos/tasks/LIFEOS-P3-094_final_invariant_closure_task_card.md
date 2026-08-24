# LIFEOS-P3-094｜真实本地闭环最终不变量收口任务卡

## 状态与授权

- 任务 ID：`LIFEOS-P3-094`；历史任务，已由 D-0401 收口。
- 优先级：P0。
- 状态：`Closed — Acceptance Not Met / Superseded by LIFEOS-P3-096 / Not Frozen`。
- D-0401 已采纳并应用两层验收治理。P3-094 已超过新的两轮正式 Rework 上限，不得再创建 attempt-10，也不得重新投递本卡启动工程。
- attempt-1 至 attempt-9、P3-095、全部 PM Review／Evidence／Manifest 和当前工程候选严格只读保全。
- D-0399 的三项缺口由新任务 `lifeos/tasks/LIFEOS-P3-096_post_commit_audit_evidence_closure.md` 接替，并使用冻结的 `ABF-P3-096-v1`。
- P3-094 未通过且不标记 Accepted；R-0051 保持 P0 / Open，不进入独立复评、冻结、风险关闭或 Stage 4。

> D-0401 后，本卡以下内容仅作为历史验收合同保留，不再构成执行授权或活动任务范围。

## 为什么改为最终不变量收口

此前整改按当轮已知症状收窄，执行侧测试又主要复现已知症状，导致“缺失 DB”“零字节 DB”“缺表／缺列”“缺约束／非法来源”等同一不变量的不同表现被分轮发现。本卡不再把下一轮定义成两个反例的局部补丁，而是一次覆盖下列四个完整不变量：

1. 所有生命周期入口共享同一 task-local 路径能力边界。
2. 所有读取、展示、清理与既有 DB 写入共享同一 SQLite 结构、约束、来源和审计完整性边界。
3. 每类失败的页面、DB、sidecar、哨兵和半成品后置状态都有唯一、可机器判定的合同。
4. 执行侧在提交 PM 前先完成完整变异矩阵和既有全回归；缺一行、失败一行或无法复核均不得提交。

本卡提高一次通过概率，但不承诺 PM 或独立评审必须忽略新发现的 P0/P1。任何真实缺陷仍必须如实判定。

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本卡仅用于防御性修复和本地回归：

- 只使用项目工作区及 `/private/tmp` 新建的固定非敏感测试夹具。
- 不访问真实个人文件、既有个人数据库、真实用户路径、网络、云、第三方系统、凭据或外部目标。
- 不启用 Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 不演示或扩大攻击能力；路径、链接、Schema 变异和失败注入只针对本任务新建夹具。
- 不关闭或重开 R-0051，不冻结资产或 Schema/API，不恢复工程基线，不进入 Stage 4。

## Agent、模型与会话路由

- 推荐 Agent：Codex 工程执行。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 允许降级模型：None。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用时使用并记录原因。
- 禁止降级条件：路径／删除、SQLite 完整性、来源标注、P0/P1、失败原子性、Evidence 或范围争议。
- 必须升级／停止：任何真实文件／DB 接触、外部访问、范围扩大、无法证明历史资产只读、无法清理临时夹具、Schema/API 实质变化。
- 推荐执行方式：复用已结束 attempt-8 且未承担 P3-095 独立评审的 Codex 工程会话，或新建隔离 Codex 工程会话。
- 禁止复用：P3-095 独立评审会话，以及任何仍有未完成任务或上下文边界不清的会话。
- 后续独立评审：PM Pass 且用户采纳后，必须另建全新隔离独立复评；执行会话不得自评。

## 最小启动包与定向补读

执行前必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. `lifeos/reviews/LIFEOS-P3-094_pm_review.md` 的 Attempt-5 至 Attempt-8 章节
5. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/MANIFEST.md`
6. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/pm_schema_constraint_counterexamples.py`
7. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/pm_schema_constraint_counterexamples.json`
8. `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
9. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
10. `lifeos/PM_OPERATING_MODEL.md` 中 P0、真实本地数据、删除／失败关闭和受控能力包章节
11. `lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 中工程、数据／安全和 Gate 2–4 相关章节
12. `lifeos/DECISION_LOG.md` 中 D-0388 至 D-0397、`lifeos/RISK_LOG.md` 中 R-0051

仅在发现冲突时定向补读其他历史；不得全文翻读无关项目历史。

首份会话报告必须记录：本卡完整路径、会话类型、精确接收时间、实际模型配置、授权决策号、未承担 P3-095 独立评审，以及开始前工作区已有修改。

## 允许修改与只读资产

### 允许修改

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`
- `lifeos/engineering/LIFEOS-P3-094/scripts/operator_cli.py`
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`
- `lifeos/engineering/LIFEOS-P3-094/README.md`
- 新建 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/`
- 新交付物：`lifeos/deliverables/LIFEOS-P3-094_final_invariant_closure.md`

### 严格只读

- attempt-1 至 attempt-8 的全部工程、交付物、Evidence 和 Manifest。
- P3-095 的任务、交付物、Review 和 Evidence。
- 全部既有 PM Review／PM Evidence；不得把 PM 反例文件复制、移动或覆盖到工程 Evidence。
- 项目账本、冻结状态、风险日志和其他任务资产。

## 非范围

- 不读取、迁移或修复既有个人 DB；不建立生产迁移策略。
- 不改变产品定位、用户原文规则、SQLite 业务 Schema 或字段语义。
- 不冻结 Schema/API；允许为收紧 task-local 能力而做最小内部接口／CLI 参数收口，但必须保持现有业务行为，并在交付物逐项列明兼容影响。
- 不支持并发恶意路径替换、多进程并发写、WAL 恢复、崩溃恢复、网络文件系统或外部进程篡改；这些明确超出有限 Stage 3 单进程边界。发现相关状态时必须 fail closed，不得假装支持。
- 不新增导入、导出、分享、HTTP、浏览器自动化、云、同步或第三方能力。
- 不关闭 R-0051，不创建独立复评，不进入 Stage 4。

## 必须实现的四个不变量

### I-1：统一 task-local 路径能力

所有公开运行时入口 `capture()`、`list_today()`、`safe_snapshot()`、`render_today()`、`delete_all()` 及对应 CLI 必须复用同一条路径验证逻辑，不得各自形成宽窄不一的边界。

- DB 必须是绝对、词法规范化后严格等价的路径，文件名固定为 `capture.sqlite`；拒绝相对路径、`..`、规范化绕路、空组件语义差异和调用方页面目标。
- DB 父目录必须已存在；从根到父目录的每个现有组件均须通过 `dir_fd/openat` 与 `O_NOFOLLOW` 验证为真实目录。capture 不得以 `mkdir(parents=True)` 静默创建任意祖先目录。
- DB 最终对象若存在，必须是不跟随链接确认的普通文件，且 `st_nlink == 1`；拒绝符号链接、硬链接、目录、FIFO、socket、设备或类型无法确认。
- 内部页面只能是同目录精确 `today.html`；最终对象若存在必须为普通文件。符号链接、目录、FIFO、socket、设备及无法确认类型均拒绝。
- 页面写入、失效和临时文件操作只能通过已验证父目录 fd 与固定 basename 完成；不得重新拼接任意外部路径。
- 边界验证失败必须发生在任何 DB、页面、sidecar、哨兵或目录变更前；所有固定哨兵的存在、inode、大小和 SHA-256 均保持不变。
- 有限 Stage 3 不声明抵抗并发恶意替换；但单次操作前后必须核对关键 inode/device/link-count 未发生意外变化，异常即不得报告成功。

### I-2：唯一 canonical SQLite 合同

不得用“表名 + 列名／类型相同”代替完整 Schema 验证。实现须从当前未变更的 `SCHEMA` 建立一个 canonical reference contract，并由全部既有 DB 操作共享。

至少验证：

- `captures`、`audit` 的对象类型、列顺序、声明类型、`NOT NULL`、默认值和主键位置。
- `captures.id` 主键、`captures.idem_key` 唯一约束、`captures.source` 的 `CHECK(source = 'local_capture')`。
- `audit.id INTEGER PRIMARY KEY AUTOINCREMENT` 及 `sqlite_sequence` 语义。
- canonical reference 产生的全部必需 index／autoindex；缺失、替换、降级为非唯一或列顺序变化均拒绝。
- 不允许同名 view／trigger 冒充表；不允许改变核心语义的额外 trigger、index 或 shadow object。若决定允许无害额外对象，必须在代码中有精确 allowlist 和测试，不得默认接受。
- `PRAGMA quick_check` 必须返回 `ok`；无法执行、返回其他结果或出现 sidecar／WAL／journal 状态均 fail closed。
- 目标 DB 的读取验证必须严格只读，不得创建、初始化、补写或修复任何对象，不得创建 `journal`、`wal`、`shm` 或其他副文件。

建议实现方式：在内存 SQLite 用当前 `SCHEMA` 创建 reference，仅比较结构化 PRAGMA／`sqlite_master` 合同和规范化 SQL；不得只做脆弱字符串包含判断，也不得对目标 DB 试写探测约束。

### I-3：行级来源、类型和审计一致性

render、list 和 snapshot 发布任何记录前，必须一次性读取并验证完整结果集，任何一行无效都不得展示部分成功。

- `id`、`content`、`created_at`、`source`、`idem_key` 必须为预期 SQLite 类型且非 NULL；不得把 BLOB、INTEGER、REAL 或 NULL 当作合法文本。
- `source` 必须逐行严格等于 `local_capture`；页面来源标签必须来自已验证事实，不得无条件硬编码后发布未验证记录。
- `id` 必须符合当前 capture 生成的 UUID 形式；`created_at` 必须为当前合同允许的带时区 ISO-8601；`content` 和 `idem_key` 必须满足现有非空规则。
- captures 的 `id` 与 `idem_key` 必须唯一；即使异常 DB 绕过约束形成重复，也必须拒绝整个结果集。
- 每条 capture 必须存在与当前合同一致的 `capture_saved` 审计；审计 event、capture_id、created_at、detail 类型与允许值必须可验证。孤立、缺失、伪造或类型异常的关键审计不得被当作来源可信。
- 页面 HTML 必须转义固定测试文本；包含标记、引号、Unicode、换行和超长但受控文本的夹具不得产生脚本／标签注入、截断或部分页面。
- 任何 Schema、行级或审计完整性失败：list／snapshot 返回安全失败且 DB 不变；render／clear 先按安全页面合同使旧页面不可展示，再返回失败且 DB 不变；capture 对既有异常 DB 在任何写入前失败。

### I-4：全生命周期状态机与失败原子性

必须为每个入口定义并验证唯一的 before/operation/after 状态：

- **capture 新 DB**：只允许在已验证父目录中创建精确 `capture.sqlite`；Schema 初始化与首条 capture 必须形成可证明的完成状态。初始化或首写失败不得留下零字节 DB、部分 Schema、sidecar、临时文件或页面。
- **capture 既有 DB**：写前完成 canonical Schema 与关键状态验证；失败、幂等冲突或注入异常不得改变 captures/audit、DB hash 或页面。成功新增记录后，既有 `today.html` 必须先失效或以其他可证明方式不再被视为当前页面，不能继续展示旧快照。
- **幂等重复**：保持现有返回合同；若允许追加 repeat audit，必须明确验证只发生这一项预期变化。相同 key 不同内容必须失败且 DB／页面状态符合合同。
- **list／snapshot**：永不创建 DB／Schema／sidecar，永不写 audit；缺失、空、损坏、不完整或内容不可信时完整失败，不返回部分记录。
- **render**：先完成边界、canonical Schema、全量行／审计验证，再构造完整 HTML；合法发布使用同目录独占临时普通文件、flush/fsync、原子 replace。发布失败清理半成品并保留此前已验证有效页面；DB 始终只读不变。
- **render 无可信 DB 状态**：DB 缺失、零字节、损坏、无／部分／伪完整 Schema、约束缺失、非法来源、审计不一致、sidecar 或查询失败时，安全旧页面必须失效；DB bytes、inode、大小、hash、对象和 sidecar 清单不变。
- **clear**：确认字符串必须精确为 `DELETE`。先完成路径和 DB 完整性预检；随后必须先使安全页面失效并确认不可展示，再在一个 DB 事务中清空 captures 并追加合法 audit。页面失效失败时 DB 不变；DB 清理失败时事务回滚、不得报告成功，页面可保持已失效并须明确披露。
- **clear 缺失／不可信 DB**：不得创建或修复 DB；若路径边界安全且存在旧页面，先使页面失效再返回失败。边界本身不可信时不得触碰页面或 DB。
- **关闭重启／跨进程顺序**：首次、重复、重启读取、render、再 capture、再 render、clear、clear 后 render 失败均须在全新进程验证，不得用同一模块内存状态代替。

## 强制变异与反例矩阵

runner 必须从 canonical 固定 DB 派生“一次只改变一个不变量”的夹具，并为每行记录预期、实际、DB／页面／哨兵 before-after 状态和 Evidence ID。至少包含：

### 路径与文件对象

- API 与 CLI：相对路径、含 `..`、规范化不等价、错误 DB basename、调用方 output 参数。
- DB 的直接符号链接、祖先任一级符号链接、硬链接、目录、FIFO、socket／可安全创建的特殊文件。
- today.html 的直接符号链接、祖先链接、硬链接、目录、FIFO、socket／特殊文件。
- DB 外固定哨兵、页面外固定哨兵、链接真实目标哨兵；所有拒绝后 hash／inode／存在状态不变。
- 父目录缺失、父目录不可读／不可写、页面不可删除、临时文件创建失败、fsync 失败、replace 失败。

### SQLite 结构

- DB 缺失、零字节、随机损坏、合法 SQLite 但无 Schema、仅一张表、每张表分别缺一列。
- 每个列分别变异名称、顺序、类型、NOT NULL、默认值、PK 位置。
- 分别缺 `id` 主键、`idem_key UNIQUE`、`source CHECK`、audit AUTOINCREMENT；唯一 index 变非唯一、错列或缺失。
- captures／audit 被 view 替代；额外 trigger 改写 source／audit；同名或 shadow object；Schema SQL 语义变更但列形状相同。
- quick_check 非 `ok`、存在 `-journal`／`-wal`／`-shm`、查询异常、权限不可读。

### 行与审计

- source 为其他字符串、大小写变体、空串、NULL、BLOB。
- id/content/created_at/idem_key 分别为 NULL、空值、错误 SQLite 类型；无效 UUID、无时区／无效时间。
- 重复 id、重复 idem_key、乱序／重复记录；一条合法加一条非法，必须整体失败而非部分 render。
- 缺 capture_saved audit、错误 capture_id、错误 event/detail、孤立 audit、NULL／BLOB 审计字段。
- 固定 HTML 标记、引号、Unicode、换行夹具，确认转义且 Evidence 不保存真实用户原文。

### 生命周期与失败注入

- 新 DB 初始化的每个可注入失败点；失败后 DB／sidecar／页面／临时目录零半成品。
- 既有 DB capture 写入、audit 写入、commit 失败；幂等重复与冲突。
- render 读取、全量验证、临时文件写、flush、fsync、replace、临时清理失败。
- clear 页面失效、失效确认、DELETE、audit、commit、rollback 失败。
- capture 后旧页面新鲜度、clear 后旧页面、DB 缺失／异常时旧页面、失效失败披露。
- 全新进程首次→重启→render→再 capture→再 render→clear→失败重渲染完整链。

## 架构与代码审查强制项

提交前必须由执行侧逐项给出代码位置和测试 ID：

1. 五个公开运行时入口和 CLI 是否全部经过统一路径 gate。
2. 哪个入口被允许创建新 DB；其余入口如何机器证明永不创建／建表／补写。
3. canonical Schema 合同由何处生成，如何覆盖约束、index、对象类型和 quick_check。
4. 为什么非法来源、类型和审计不一致无法到达 HTML 构造。
5. 每类失败是在页面失效前还是后停止，DB／页面后置状态为何符合状态机。
6. 哪些文件操作使用稳定 parent fd、固定 basename、O_NOFOLLOW／O_EXCL 和原子 replace。
7. 如何处理 DB／页面硬链接、SQLite sidecar 和半成品。
8. 哪些并发／恢复能力明确不支持，遇到相关状态如何 fail closed。

不得仅用源码字符串扫描或 mock 调用次数替代行为测试；行为测试、静态审查和结构化 Evidence 三者都要有。

## Evidence 与自动阻断提交门

新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/evidence/`，不得覆盖任何历史目录。必须包含：

- 可运行的最终 runner 和全部测试源码。
- `results.json`：每个矩阵行独立 ID、预期／实际、PASS／FAIL、失败阶段。
- `state_transitions.json`：DB、page、sidecar、temp、sentinel 的 exists/type/device/inode/nlink/size/SHA-256 before-after；不得包含 DB 内容或原文。
- `schema_contract.json`：canonical reference 的结构化合同与 hash；不得包含目标 DB 数据。
- `schema_mutation_results.json`、`row_audit_mutation_results.json`、`path_boundary_results.json`、`failure_injection_results.json`。
- 全新进程端到端日志、单元测试日志、禁止能力静态关闭态、源码 hash、历史只读 hash、复跑命令、验收矩阵和 Manifest。
- “任务卡每一条强制矩阵 → 测试 ID → 结构化结果 → Evidence 文件”的机器可校验映射。

runner 必须内置提交阻断：以下任一成立时退出非零，并把执行侧结论写为 `NOT PASS — DO NOT SUBMIT`：

- 任一强制矩阵行缺失、FAIL、Unknown 或 Not Implemented。
- P0、P1、Unknown 或 Not Implemented 非零。
- PM attempt-8 两个已知反例未被明确拒绝，或旧页面／DB 后置状态不符合本卡。
- 任一失败路径出现未授权文件／DB 变化、sidecar、半成品、缓存或 `/private/tmp/lifeos-p3-094-*` 残留。
- 历史只读 hash 不一致、Manifest 漏项、Evidence 含 SQLite／HTML／pyc／缓存／固定夹具明文之外的数据。
- 禁止能力、网络、真实文件／DB、外部路径或范围扩大被触发。

执行侧不得把 `NOT PASS` 结果提交 PM；必须留在同一工程会话、同一 attempt-9 目录内继续修复和重跑，直到上述门全部为 PASS。不得通过删除测试、放宽预期、标 N/A 或改写历史 Evidence 消除失败。

## 完成定义

只有同时满足以下条件才允许提交 PM：

- 全部四个不变量实现并由统一代码路径承担，不是为单个夹具硬编码。
- 全部强制矩阵和现有 attempt-6／7／8 回归通过；执行侧 P0=0、P1=0、Unknown=0、Not Implemented=0。
- P2 只能是与安全、数据、生命周期、Evidence 完成性无关的非阻断项，且必须逐项说明；否则不得提交。
- 新 DB／既有 DB、合法／非法、API／CLI、成功／失败、首次／重启／清理均有结构化状态证据。
- 所有失败关闭都证明未越出 task-local；所有临时夹具精确清理。
- attempt-1 至 attempt-8、P3-095、PM Review 和全部 PM Evidence hash 保持只读；PM 后续授权更新造成的精确差异必须单列，不得笼统忽略。
- 交付物明确报告实际模型、会话授权、修改文件、兼容影响、未支持并发边界、本地模型预检是否跳过及原因。

## PM 验收与后续关卡

- 本轮涉及删除、真实本地 DB、来源完整性和失败关闭的高风险最终判断，执行侧与 PM 均可跳过本地模型预检，但必须记录理由。
- PM 将使用新的 `/private/tmp` 固定非敏感夹具复算 hash、复跑 runner，并从四个不变量各抽取反例；不会只重复执行侧 happy path。
- PM Pass 后仍须用户采纳，随后才可创建一次全新隔离独立复评。
- 独立复评、风险关闭、冻结、基线恢复和 Stage 4 均不由本卡自动授权。

## 专项会话回复

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，聊天只输出：执行结论、测试与 Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、修改文件、交付物路径、Evidence 路径、临时残留、是否需要 PM 决策。完整内容写入交付物，不在聊天粘贴任务卡或日志。
