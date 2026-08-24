# LIFEOS-P3-094｜真实本地闭环最终不变量收口

## 任务信息

- 任务 ID：LIFEOS-P3-094（同一能力包 attempt-9）
- 执行 Agent：Codex 工程执行
- 任务类型：P0 真实本地能力包最终不变量收口；不适用 P3 Engineering Fast Lane
- 状态：Execution-side PASS — Ready for PM Review；不代表 PM Pass、独立 Pass、风险关闭、冻结或 Stage 4 准入
- 任务卡：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-094_final_invariant_closure_task_card.md`
- 会话类型：New isolated Codex engineering session
- 接收时间：2026-08-22 20:20:51 CST (+0800)（以当前 Codex task 目录创建时间记录）
- 实际模型：`gpt-5.6-terra` + `high`；未降级
- 执行授权：D-0398；用户明确投递任务卡路径即启动
- 独立性：本会话未承担 P3-095 独立评审；不得自评后续独立复评
- 开始前工作区：仓库整体为未跟踪状态；既有 `.DS_Store`、`generate_depr_sql.py`、`generate_simple_depr_sql.py`、`update_IDecDeprMonths_from_excel.sql`、`update_IDecDeprMonths_simple.sql` 与 LifeOS 既有资产均视为用户已有内容并保持不动

## 修复与验证目标

1. 五个公开入口与 CLI 共用唯一 task-local 路径能力，不再由 capture/list/snapshot 隐式创建目录或绕过页面／DB 对象边界。
2. 从未变更的 `SCHEMA` 生成 canonical SQLite 合同，统一验证完整结构、约束、index、对象类型、`quick_check` 和 sidecar 关闭态。
3. 在发布 list、snapshot 或 HTML 前一次性验证全部记录与审计链；来源、SQLite 类型、UUID、带时区时间、唯一性或审计任一不可信即整体失败。
4. 将新 DB、既有 DB、幂等、render、clear 与跨进程顺序收束为明确状态机，并用自动阻断 runner、结构化状态和历史 hash 证明。

## 实际修改

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`
- `lifeos/engineering/LIFEOS-P3-094/scripts/operator_cli.py`
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`
- `lifeos/engineering/LIFEOS-P3-094/README.md`
- 新建 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/scripts/run_attempt_9.py`
- 新建 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/evidence/`
- 新建本交付物

未修改任务卡、PM Review、PM Evidence、项目账本、风险日志、冻结状态、attempt-1 至 attempt-8 或 P3-095 资产。

## 四个不变量实现

### I-1：统一路径能力

`local_capture.py:115` 的 `_open_path_gate()` 是五个入口唯一的路径 gate。它保留 CLI 原始词法字符串，要求绝对路径、规范化严格等价与固定 `capture.sqlite` basename；从 `/` 开始以 `openat`/`O_NOFOLLOW` 打开每级父目录；父目录必须预先存在。DB 与 `today.html` 都只接受普通、单链接文件；symlink、祖先链接、硬链接、目录、FIFO、socket 模式、错误 basename、调用方输出目标与 sidecar 状态均在操作合同规定的阶段拒绝。页面 unlink、rename、临时创建与 replace 只使用稳定 parent fd 和固定 basename。

入口位置：capture `:395`、list `:434`、snapshot `:439`、render `:446`、clear `:481`；CLI 保留 `--db` 原始字符串后直接调用这些入口。单次操作前后核对 parent 与 DB device/inode/nlink；有限 Stage 3 不声明抵抗并发恶意替换。

### I-2：canonical SQLite 合同

`canonical_schema_contract()`（`:183`）在内存 SQLite 执行当前未变更 `SCHEMA`，生成 `sqlite_master` 规范化 SQL、`table_xinfo`、`index_list` 和 `index_xinfo` 结构合同。`_open_read_only()`（`:196`）使用 `mode=ro&immutable=1`，先拒绝 journal/WAL/SHM，再要求 `PRAGMA quick_check == ok` 与完整合同精确相等。

该比较覆盖 captures/audit 对象类型、列顺序／声明类型／NOT NULL／默认值／PK、`idem_key UNIQUE` autoindex、`source CHECK`、audit AUTOINCREMENT 与 `sqlite_sequence`，并默认拒绝额外 table/view/index/trigger/shadow object。目标 DB 验证不试写、不初始化、不补 Schema。

### I-3：行级来源、类型与审计

`_validated_records()`（`:236`）用 `typeof()` 一次读取完整 captures/audit 结果集。它验证 UUID4、带时区 ISO-8601、非空 content/idem_key、逐行精确 `source=local_capture`、ID/幂等键唯一，以及审计 ID、事件、类型、时间和 detail。每条当前 capture 必须恰有一个位于最近 clear 之后的 `capture_saved`；repeat 与历史 clear 之前审计有明确状态语义；伪造、缺失、孤立或未知事件全部拒绝。

HTML 只由已验证记录构造，来源标签只有在来源事实已通过验证后才写入；content 与时间均 HTML escape。固定标记、引号、Unicode、换行与 20,000 字符夹具已验证无脚本／标签注入或截断。

### I-4：生命周期与失败原子性

- 新 DB：`_create_new_capture()`（`:362`）在已验证 parent fd 下独占创建随机临时普通文件，完成 Schema、首条 capture、capture_saved、合同与行级复核、commit 和文件 fsync 后原子 replace 为固定 DB；失败清理 DB temp/sidecar/page staging。
- 既有 DB capture：写前只读完整验证；冲突不写；幂等重复只追加 repeat audit；新记录事务失败会 rollback 并恢复旧页面，成功后旧页面不可展示。
- list/snapshot：只读 gate + canonical/row/audit 验证；缺失或不可信 DB 不创建 DB、Schema、audit 或 sidecar。
- render：全量验证后才构造 HTML；同目录 O_EXCL 临时普通文件经 flush/fsync 后原子 replace。构造、写入、fsync 或 replace 失败保留此前可信页面并清理 temp；缺失／空／损坏／伪完整 DB、sidecar 或不可信数据先失效安全旧页面再失败，DB 不变。
- clear：精确确认 `DELETE`；完整预检后先失效页面，再以单事务 DELETE captures + 合法 clear audit；事务失败 rollback，页面保持失效并披露。缺失／不可信 DB 在路径边界安全时先失效页面且不创建／修复 DB；路径边界不可信时不触碰任何对象。
- 重试清理：`_cleanup_temp()`（`:336`）对瞬时 unlink 失败作有限重试；持续文件系统失败不会被报告为成功。

## 代码审查强制项映射

1. 五入口/CLI 统一 gate：`_open_path_gate()`；测试 `test_all_public_entries_share_exact_path_gate` 与 PATH 系列结构化结果。
2. 仅 capture 可创建新 DB：`_create_new_capture()`；list/snapshot/render/clear 均先 `_open_read_only()`；测试 `test_read_entries_never_create_missing_db_or_sidecar`。
3. canonical 合同：`canonical_schema_contract()` + `_schema_contract_from_connection()` + `_open_read_only()`；88 条 Schema 独立变异结果见 `schema_mutation_results.json`。
4. 非法来源无法到 HTML：`_validated_records()` 在 `render_today()` 构造 cards 前完成；测试 `test_source_and_row_type_mutations_fail_whole_result`、`test_audit_mutations_fail_closed`。
5. 失败前后状态：`state_transitions.json`、`fresh_process_lifecycle.log` 与 failure results 记录 DB/page/sidecar 的 before-after；clear 事务失败页面可保持失效，其余失败按合同保持或失效。
6. 稳定 parent fd 文件操作：path gate、`_stage_page()`、`_invalidate_today()`、render O_EXCL/fsync/replace 和 `_cleanup_temp()`。
7. 硬链接／sidecar／半成品：单链接检查、sidecar tuple、临时 basename 清理；相关 unittest 与 PATH/LIFE 结果均 PASS。
8. 明确不支持：并发恶意替换、多进程并发写、崩溃/WAL 恢复、网络文件系统和外部进程篡改；sidecar 或单次操作关键身份变化 fail closed，不外推为生产恢复保证。

## 测试与 Evidence

- 运行时 unittest：41 PASS / 0 FAIL。
- attempt-9 自动阻断矩阵：107 PASS / 0 FAIL；Schema 88、Path 6、Row/Audit 6、Lifecycle/Failure 7。
- attempt-6 行为回归：19 PASS / 0 FAIL。
- attempt-7 行为回归：13 PASS / 0 FAIL。
- attempt-8 行为回归：18 PASS / 0 FAIL。
- PM attempt-8 已知反例：2 PASS / 0 FAIL；两个伪完整 Schema 均被拒绝、旧页面失效、DB 不变。
- 全新进程链：首次 capture → repeat → restart read → render → 再 capture → 再 render → clear → clear 后 render 失败，全部退出码与状态匹配。
- 历史严格只读：185 个文件 before/after SHA-256 相等。
- 临时残留：`/private/tmp/lifeos-p3-094-*` 为 0；工程与 Evidence 无 pyc/__pycache__/SQLite/HTML。
- 禁止能力：网络、HTTP、Tauri/IPC、Vault、导出、同步、第三方、真实外部目标均未触发。
- Manifest：attempt-9 Evidence 非自指 Manifest 已逐项复算一致。

复跑命令：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/scripts/run_attempt_9.py
```

Evidence 入口：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/evidence/MANIFEST.md`。

### 历史 runner 兼容说明

attempt-6/7/8 历史 runner 原件保持只读。其旧夹具依赖 capture 自动创建 case 父目录，并在页面为非法对象时绕过统一 gate 调用 list；两者与本卡的新不变量冲突。attempt-9 runner 只在 `/private/tmp` 临时副本中加入夹具前置 mkdir、把非法页面状态后的 DB 数量断言改为直接只读计数，并将已重命名的内部读失败注入点对齐；工程行为断言未放宽。适配后 19/13/18 全通过，详细变更原因和结果已结构化披露。

## 兼容影响

- 有意收紧：DB basename 必须为 `capture.sqlite`，父目录须调用方预先创建；`runtime.sqlite`、相对／绕路路径及自动建祖先目录不再兼容。
- 有意收紧：list/snapshot 也验证同目录页面对象；非法页面链接、硬链接或特殊对象会阻断读取，而不是绕过统一能力边界。
- 有意收紧：同列形状但非 canonical 的旧 SQLite、未知额外对象、非法来源或不一致审计不再被读取、展示、清理或追加写入；本任务不迁移或修复它们。
- 保持：业务 `SCHEMA` 与字段语义未改变；合法 capture/list/snapshot/render/clear 成功结果结构和精确 `DELETE` 合同保持。
- CLI 不接受任意 output 参数；`--db` 改为保留原始词法字符串后交由统一 gate 验证。

## 非范围与剩余边界

- 未读取、迁移或修复既有个人 DB；未制定生产 migration。
- 未改变产品定位、V1、核心领域模型、AI 权限、业务 Schema/API；未冻结任何资产。
- 未启用网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3、第三方或外部用户。
- R-0051 保持 P0 / Open；本交付物不关闭／重开风险、不恢复工程基线、不进入 Stage 4。
- 不支持的并发／恢复边界保持明确；若未来要支持，需独立任务、独立评审和用户确认。

## 角色与关卡

- 主责角色：技术架构负责人 / Codex 工程执行。
- 协审检查点：数据／领域模型负责人（来源、审计、原文、生命周期）；AI 信任与安全负责人（本地处理、来源身份、禁止外部能力）；PM（授权、范围、Evidence、后续关卡）。
- 执行侧 Gate 2：PASS candidate；来源、类型、审计、删除后置状态和原文展示均有行为与结构化 Evidence。
- 执行侧 Gate 3：PASS candidate；无 AI/网络/第三方处理，来源标签不可绕过验证。
- 执行侧 Gate 4：PASS candidate；四项不变量、失败状态机、全量变异、回归与跨进程链均通过自动阻断门。
- 仍需：正式 PM 验收；用户采纳；之后另建全新隔离独立复评。风险关闭、冻结、基线恢复和 Stage 4 不在本卡授权内。

## 自评与本地预检

- Execution-side：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0。
- 自动阻断结论：`PASS — READY FOR PM`。
- 本地模型预检：跳过。原因是本轮涉及删除、真实本地 DB、来源完整性与失败关闭的高风险最终判断；任务卡明确允许执行侧跳过，局域网模型不得替代人工代码审查、反例矩阵或 PM 验收。
- 需要 PM 决策：No（仅需按既定流程进行 PM 验收；不得由专项会话自行启动后续任务）。
