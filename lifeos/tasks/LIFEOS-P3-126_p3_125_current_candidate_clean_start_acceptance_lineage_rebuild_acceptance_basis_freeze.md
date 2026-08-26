# ABF-P3-126-v1｜P3-125 当前技术候选清洁启动与验收链重建

## 冻结信息

- 任务 ID：`LIFEOS-P3-126`
- ABF ID／版本：`ABF-P3-126-v1`
- 生效决策：`D-0511`
- 冻结时间：2026-08-26
- ABF 文件 SHA-256：由最终任务卡、D-0511 与 Freeze Manifest 记录；本文件不自指。
- 状态：Frozen
- 是否在专项会话开始前冻结：Yes；P3-126 engineering root 与唯一 temp root 在冻结时均不存在。
- 正式 Rework 上限：1；当前 0/1

## 本轮唯一用户结果

- Byte-exact P3-125 Rework-1 candidate 在全新 P3-126 task-local 根中重建从 clean preflight 到 exact cleanup 的完整验收链，且没有任何旧 P3-122 Runtime-root access/stat。
- 不冻结产品、UI、Runtime 架构、Schema/API、capability、风险或阶段。
- 不包含 production source修改、独立复评、真实能力、产品合同或 Fast Track。

## 授权与能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-126/`、P3-126 deliverable/local precheck、`/private/tmp/lifeos-p3-126-clean-closure-v1`。
- 允许数据：唯一 temp root 内全新合成 SQLite、固定非敏感短文本、sentinel、负向夹具与 task-local cache。
- 允许入口：构建时 `LIFEOS_RUNTIME_ROOT`；既有 `capture_record`、`get_today`、`runtime_status`。
- 严格只读：P3-125 Rework-1 candidate、Final Manifest、delivery、PM Review、PM Evidence/final adoption及最终 P3-126 allowlist。
- 禁止：旧 P3-122 Runtime root 的 access/stat/hash/create/cleanup；P3-122/P3-124 主动补读；P3-125 修改；Pilot、真实 DB／路径／文本、网络、产品模型、新 IPC／UI／Schema/API／capability、风险／冻结／Stage 4。
- 投递前额外用户确认：Completed；用户已精确确认新 engineering/temp root、全新合成 DB、P3-125 Rework-1 全部只读、仅构建时 root与三 IPC、旧 P3-122 Runtime root零 access/stat/hash/create/cleanup，以及 Pilot、真实边界、网络和产品模型全部禁止。

## 引用 L1

- L1-1 数据主权：只写新 P3-126 task-local root。
- L1-3 生命周期完整：首次、重复、刷新、关闭重开一致。
- L1-4 失败关闭：所有启动／路径／DB失败先于变更。
- L1-6 审计可信：source、build、IPC、DB、geometry、动作有对应关系。
- L1-7 Evidence 诚实：每行实际执行，不批量映射。
- L1-8 历史保全：P3-125 及更早资产只读。
- L1-9 授权不漂移：不继承 P3-125 会话或访问旧 root。
- L1-10 可复核性：byte-exact source、固定夹具、runner、Manifest 可复跑。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | Clean startup | P0 | candidate read/root create 前完成身份、hash、命令计划；无禁止 root操作 | 立即停止，零新写入 |
| ABF-I-02 | Byte-exact candidate | P0 | 75/75 与 Frozen allowlist一致，production changes=0 | 停止，不提交 |
| ABF-I-03 | 单根与双根可移植 | P0 | 同一 source 在 run-a/run-b只由构建变量绑定 | 无串写 |
| ABF-I-04 | 生命周期不退化 | P0 | 三 IPC first/repeat/refresh/reopen 与 UI/DB/audit/geometry一致 | 原子失败 |
| ABF-I-05 | 失败关闭 | P0 | config/path/storage negatives 全部 before-after不变 | 无半成品 |
| ABF-I-06 | 产品／接口零漂移 | P0 | UI、IPC、Schema/API、capability与输入一致 | 停止 |
| ABF-I-07 | 历史与授权保全 | P0 | P3-125 hashes一致；旧 root零操作 | Not Pass |
| ABF-I-08 | Evidence/Manifest/cleanup | P0 | 12行、mutation、非自指 Manifest、精确 cleanup完整 | Not Pass |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | clean preflight | 新会话、两根 absent | 核对身份／模型／任务／ABF／allowlist／命令计划 | 全匹配且禁止 root零操作后才继续 | candidate/history/root | P126-M001 | preflight.json |
| ABF-M-002 | source copy | Frozen 75-row allowlist | 建立 candidate | 75/75 byte-exact、production delta=0 | P3-125 input | P126-M002 | source-lineage.json |
| ABF-M-003 | static contract | candidate ready | 单根、派生、UI/IPC/API/capability核对 | 全部不漂移 | candidate | P126-M003 | static-contract.json |
| ABF-M-004 | config negatives | root absent/sentinel | missing/empty/relative/traversal/link/file | build前拒绝 | sentinel/root/DB | P126-M004 | config-negatives.json |
| ABF-M-005 | run-a | fresh run-a | build＋actual Tauri | 仅 run-a写入 | run-b/history | P126-M005 | run-a-results.json |
| ABF-M-006 | run-b | fresh run-b、同 source | 只改变 build root | 仅 run-b写入 | run-a/history | P126-M006 | run-b-results.json |
| ABF-M-007 | three IPC | fresh DB | status/first/repeat/today/refresh/reopen | UI/DB/audit/geometry一致 | other root/history | P126-M007 | ipc-lifecycle.json |
| ABF-M-008 | failure closure | disposable roots | path/DB/sidecar/geometry/atomic/unwritable failures | 全部 before-change拒绝 | sentinel/DB | P126-M008 | failure-closure.json |
| ABF-M-009 | prohibited boundary | completed runs | source/bundle/log/write inventory＋命令审计 | 禁止能力与旧 root操作零命中 | behavior/history | P126-M009 | boundary.json |
| ABF-M-010 | history | before snapshot | after hash复算 | P3-125 inputs全一致 | history | P126-M010 | history-integrity.json |
| ABF-M-011 | mutation | pristine verifier PASS | root/fallback/derive/order/history/extra/path/omission | 每类拒绝 | pristine | P126-M011 | mutation-results.json |
| ABF-M-012 | cleanup/final | App closed | 精确删除唯一 temp root并生成 Manifest | root absent、Manifest完整非自指 | Evidence/history | P126-M012 | cleanup.json/FINAL_MANIFEST.json |

## Evidence 合同

- 独立 P3-126 runner，不 import/copy/call P3-125 runner；production candidate仅 byte-exact copy。
- M-001～M-012 每行独立结构化结果；actual App动作绑定 UI/screenshot、IPC、DB、process/log和 hash。
- 所有负向有 sentinel/DB/inventory before-after。
- model/effort按平台暴露值写入 preflight与首报；无法记录则 action-before stop。
- Final Manifest以 repository root解析，覆盖 task/ABF/allowlist/authorization/P3-125 inputs/current candidate/Evidence/delivery/mutation/cleanup，排除自身。
- 只精确清理 `/private/tmp/lifeos-p3-126-clean-closure-v1`。

## 计数与 Pass 公式

- P0：任一授权、clean startup、candidate byte、根、失败前置、IPC/Schema、history、Manifest或cleanup失败。
- P1：不改变核心边界但影响 actual-App完成定义的退化。
- P2：轻微 Evidence／文案差异；Pass仍要求0。
- Unknown：任一 identity/root/write inventory/App/DB/history/cleanup无法复核。
- Not Implemented：任一不变量、矩阵行、runner、mutation或Manifest缺失。
- Pass：I-01～I-08与M-001～M-012全 PASS；五类计数全零；silent N/A=0。
- 允许 N/A：仅 Gate 1/3/5非任务结论；矩阵无 N/A。

## Rework 与退出

- 正式 Rework上限：1。
- 同任务 Rework：仅 P3-126 task-owned runner/Evidence/Manifest，production candidate、ABF和边界不变。
- 新任务触发：production source需要修改、ABF／目录／数据／入口／IPC／Schema/API／授权变化，或 Rework 1/1后仍不通过。
- Blocked：Frozen inputs、授权或离线 actual Tauri确实不可用且无授权替代。

## 候选与历史

- 候选：P3-125 Rework-1 75-file candidate；Frozen physical multiline allowlist SHA-256 `2c4a1a40310adb833f42d935a017fe3fdc8fe5c26c9a2c21b30ba94f7b4a06b9`，75/75 bytes/hash匹配。
- 历史：P3-125 Rework-1 Final Manifest、delivery、PM Review、PM Evidence与 final adoption Manifest。
- 允许变化：仅最终任务卡允许的 P3-126 engineering/delivery/local-precheck/temp root。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递；正式工程动作前仍有一次标准质疑窗口。
- PM 处理：已复算 allowlist 75/75、核对新根 absent，并按用户精确确认冻结边界。
- 最终冻结版本：`ABF-P3-126-v1`。
- 专项开始后不得修改 Frozen ABF；需修改则关闭并新建。
