# ABF-P3-125-v1｜Runtime 根可配置化与失败关闭收口

## 冻结信息

- 任务 ID：`LIFEOS-P3-125`
- ABF ID／版本：`ABF-P3-125-v1`
- 生效决策：`D-0504`
- 冻结时间：2026-08-26
- ABF 文件 SHA-256：由任务卡、D-0504 与 Freeze Manifest 记录；本文件不自指。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes；工程与临时根在冻结时均不存在。
- 正式 Rework 上限：1；当前 0/1。

## 本轮唯一用户结果

- 要完成的单一结果：P3-122 Runtime 路径合同变为单一构建时 task-local root 配置；同一 source 可在两个授权子根构建／运行，所有 Runtime 文件从该根派生，非法配置在任何变更前失败关闭。
- 明确不冻结的产品需求：不冻结产品、UI、Runtime 架构、Schema/API、Tauri capability、风险或阶段。
- 明确非范围：运行时任意目录选择、设置页、CLI flag、新 IPC、UI 重设计、真实数据／路径、网络／模型、风险关闭、基线恢复、P3-126 独立复评和后续 Fast Track。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-125/`、指定 P3-125 deliverable/local precheck、`/private/tmp/lifeos-p3-125-runtime-root-config-v1`。
- 允许数据与夹具：唯一 temp root 内的全新非敏感合成 SQLite、固定短文本、sentinel、symlink／文件类型负向夹具；`run-a/` 与 `run-b/` 仅作为该根子目录。
- 允许入口／接口：既有 `capture_record`、`get_today`、`runtime_status` 三项 IPC；构建时 `LIFEOS_RUNTIME_ROOT`。
- 允许工具／环境：离线 Rust/Cargo/Tauri、task-local runner、SQLite 只针对新合成 DB、macOS native App 取证；全部 cache 位于允许根。
- 严格只读资产：P3-122 candidate/Evidence/Review；P3-123/P3-124 全部历史；任务卡正式冻结时生成的 P3-125 source allowlist。
- 禁止能力与外部目标：旧 P3-122 temp root、Pilot、真实 DB／路径／文本、网络、产品模型、云／第三方、Vault、clear/export/权限/恢复、同步、多设备、L3、外部用户、新 IPC／capability／Schema/API。
- 投递前额外用户确认：Completed；用户明确确认两个根、全新合成 DB、P3-122/P3-124 全部只读、构建时唯一 `LIFEOS_RUNTIME_ROOT`、仅三项既有 IPC，并禁止旧 P3-122 temp root、Pilot、真实 DB／路径／文本、网络与产品模型。

## 引用的 L1 长期原则

- L1-1 数据主权：所有写入必须属于唯一配置且授权的 task-local root。
- L1-3 生命周期完整：首次、重复、刷新、关闭重开与失败后的 DB/UI/audit/geometry 一致。
- L1-4 失败关闭：非法配置、路径／类型／DB 失败必须先于任何变更。
- L1-6 审计可信：配置根、source/build hash、动作、DB 与 geometry 可追溯。
- L1-7 Evidence 诚实：actual-App 和逐项负向 Evidence，不以静态扫描代替动态结果。
- L1-8 历史保全：P3-122～P3-124 资产只读。
- L1-9 授权不漂移：构建配置只能使用本轮授权的两个子根；不得访问旧根。
- L1-10 可复核性：同一 source 在两个根得到一致语义，Manifest 与 runner 可复跑。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 单一配置源 | P0 | production source 无旧根／fallback；DB、viewport、geometry 全由 `LIFEOS_RUNTIME_ROOT` 派生 | 构建或启动停止，无写入 |
| ABF-I-02 | 配置可移植 | P0 | 同一 source hash 在 run-a/run-b 分别构建运行，根内 inventory 完整且互不串写 | 无跨根文件 |
| ABF-I-03 | 规范化与链接链关闭 | P0 | 相对、非规范、symlink ancestor、错误文件类型全部拒绝 | sentinel/DB 不变 |
| ABF-I-04 | 生命周期不退化 | P0 | 三 IPC 的 first/repeat/refresh/reopen 与 DB/audit/UI 一致 | 原子失败，无半成品 |
| ABF-I-05 | 产品与接口不漂移 | P0 | UI source、三 IPC、Schema/API、capability 与 P3-122 固定基线一致 | 停止，不提交候选 |
| ABF-I-06 | 历史与授权保全 | P0 | 历史 hashes before/after 一致；旧根零访问 | 停止并披露 |
| ABF-I-07 | Evidence/Manifest 可复核 | P0 | 逐行结果、actual-App、mutation、history、cleanup 与非自指 Final Manifest 完整 | Not Pass |
| ABF-I-08 | 精确清理 | P0 | 唯一 P3-125 temp root absent；无宽删除 | 保留 Evidence，停止 |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | 两根 absent | 复算任务／ABF／allowlist／历史 hash 与 model | 全匹配后才创建根 | 所有只读资产 | P125-M001 | preflight.json |
| ABF-M-002 | source copy | Frozen allowlist | 逐文件建立 candidate并仅改路径合同 | lineage 完整、UI/IPC/API不变 | P3-122 source | P125-M002 | source-lineage.json |
| ABF-M-003 | build config | config missing/invalid | 构建或启动 | 在任何文件创建前拒绝 | sentinel/root/DB | P125-M003 | config-negatives.json |
| ABF-M-004 | run-a | fresh run-a | 构建并启动 actual Tauri | 仅 run-a 内产生派生文件 | run-b/历史/旧根 | P125-M004 | run-a-results.json |
| ABF-M-005 | run-b | fresh run-b、同 source | 仅改变构建 root后构建启动 | 仅 run-b 内产生派生文件 | run-a/历史/旧根 | P125-M005 | run-b-results.json |
| ABF-M-006 | three IPC | fresh DB | status、first、repeat、today、refresh、reopen | UI/DB/audit/geometry 一致 | 另一根/历史 | P125-M006 | ipc-lifecycle.json |
| ABF-M-007 | path negatives | sentinel + disposable roots | 相对/`.`/`..`/symlink ancestor/root file | fail before change | sentinels/DB | P125-M007 | path-negatives.json |
| ABF-M-008 | DB/sidecar types | disposable DB/geometry | DB symlink/dir/non-SQLite、geometry type conflict | fail before change | DB bytes/schema/rows/audit | P125-M008 | storage-negatives.json |
| ABF-M-009 | prohibited scan | completed candidate/app | source/bundle/log/write inventory | 旧根与禁止能力零命中；夹具字面值分栏 | candidate behavior | P125-M009 | boundary.json |
| ABF-M-010 | history | completed Evidence | before/after hash | 全匹配 | P3-122～P3-124 | P125-M010 | history-integrity.json |
| ABF-M-011 | mutations | pristine verifier PASS | root/fallback/derive/order/history/extra-file 变异 | 每类 fail closed | pristine control | P125-M011 | mutation-results.json |
| ABF-M-012 | cleanup/final | App closed | 精确删除 temp root、生成 Review inputs/Manifest | root absent、Final Manifest 非自指完整 | 工程 Evidence/历史 | P125-M012 | cleanup.json/FINAL_MANIFEST.json |

## Evidence 合同

- 可运行 runner／测试源码：P3-125 自有，不 import/copy/call P3-122/P3-124 runner。
- 逐行结构化结果：M-001～M-012 每行独立结果，不用总数批量映射。
- before／after 状态：sentinel、root inventory、DB bytes/hash/schema/rows/audit、geometry 与历史 hash。
- 日志／快照：offline test/build、actual-App 三 IPC 动作、失败日志；不采集 ambient 应用资料。
- source／history hash：P3-122 75-file source allowlist、P3-124 final PM inputs、P3-125 candidate/build。
- Manifest：非自指 Final Manifest 覆盖 current、history、authorization、Evidence、delivery、cleanup。
- 复跑命令：必须使用明确 cwd、task-local cache 与固定构建 root；不含网络。
- 临时清理：只精确清理 `/private/tmp/lifeos-p3-125-runtime-root-config-v1`。

## 计数与 Pass 公式

- P0：授权根、路径派生、失败前置、三 IPC／Schema/API、历史或 cleanup 失败。
- P1：不改变核心边界但影响完成定义的实际 Tauri 生命周期退化。
- P2：不影响完成定义的轻微 Evidence／文案差异；Pass 仍要求 0。
- Unknown：任一 root、写入 inventory、actual-App、DB before/after、history 或 cleanup 无法复核。
- Not Implemented：任一不变量、矩阵行、runner、Evidence、mutation 或 Manifest 缺失。
- Pass 公式：I-01～I-08、M-001～M-012 全 PASS；P0/P1/P2/Unknown/Not Implemented 全零；silent N/A 为零。
- 允许的 N/A：仅 Gate 1/3/5 的非任务结论可注明 N/A；矩阵无 silent N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：1。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：仅 P3-125 自有实现、测试、Evidence、Manifest，在本 ABF、目录、数据、三 IPC、单一构建时 root 合同不变时允许一次。
- 必须新建任务条件：需运行时任意路径选择、设置页/CLI、新 IPC/capability、Schema/API、架构、真实边界、额外目录，或一次正式 Rework 后仍未通过。
- Blocked 条件：固定输入、授权或离线 actual Tauri 在确认边界内确实不可用且无授权替代；不得回退浏览器或访问旧根。

## 候选基线与只读保全

- 候选输入 hash／Manifest：P3-122 Final Manifest `b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c`；P3-125 physical multiline source allowlist `lifeos/tasks/LIFEOS-P3-125_source_allowlist.md`，87 physical lines、75 candidate rows、75/75 bytes/hash 匹配，SHA-256 `807ff8e1dd565eed4fec4c1b6bf5c6bca133861a9dffdbae1ca2bac60293dc4b`，candidate tree hash沿用 P3-122 Final Manifest 的 `ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742`。
- 历史只读 hash／Manifest：P3-124 Rework-1 PM Review `1dc006967cfe248db03ae3c557504e77c5ac04e9321fcbd1cd6a7a0cec3734b3`；PM Evidence Manifest `196a1ef87cf7bea449e4d1eb1269cd00199f1e5ea337ac667ab69630fca44ea1`。
- 允许发生变化的文件：仅正式任务卡允许的 P3-125 engineering/deliverable/local-precheck 与唯一 temp root。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递；正式工程动作前仍有一次标准质疑窗口。
- PM 处理：PM 已生成物理多行 source allowlist、复算 75/75 bytes/hash、验证两根不存在并按用户确认冻结边界。专项如发现构建时配置语义歧义，必须在任何工程动作前停止回报。
- 最终冻结版本：`ABF-P3-125-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
