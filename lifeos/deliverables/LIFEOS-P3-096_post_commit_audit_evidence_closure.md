# LIFEOS-P3-096｜捕获完成点、审计语义与逐行 Evidence 收口

## 任务信息

- 任务 ID：`LIFEOS-P3-096`
- 任务名称：捕获完成点、审计语义与逐行 Evidence 收口
- 执行 Agent：Codex 工程执行
- 任务类型：P0 补丁／条件整改型受控能力包；不适用 P3 Engineering Fast Lane
- 更新时间：2026-08-22
- 当前状态：Execution-side `PASS — READY FOR PM`；不代表 PM Pass、独立 Pass、风险关闭、冻结、基线恢复或 Stage 4 准入
- 执行授权证据：用户向本新隔离专项会话投递 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-096_post_commit_audit_evidence_closure.md`；D-0404 授权继续 `Rework 1/2`；会话类型为 New isolated Codex engineering session；本次任务卡精确接收时间为 `2026-08-22 22:07:16 CST (+0800)`
- 实际模型：`gpt-5.6-terra` + `high`；未主动降级
- 验收依据：`lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md`
- ABF：`ABF-P3-096-v2`，PM 记录及实际 SHA-256 均为 `bc529ddaf2ed965e96047dc6681acdd9e17c892a4db2ddd850038cbbd239ea09`
- 规范性 V1：实际 SHA-256 `2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58`
- 启动前歧义：未发现；V2 仅替换只读候选输入，二十行矩阵与 Pass 公式继承 V1
- 当前正式 Rework 次数／上限：1／2

## Rework 1／2 收口

PM 初验以独立反例证明：既有 DB 的新 capture 已完成 commit 后，`conn.close()` 抛错会覆盖本应返回的 `saved`，造成调用结果与已持久化 DB／audit 状态矛盾。Rework 仅调整该 post-commit close 完成点：仅当事务尚未完成时继续传播 close 错误；commit 已完成后，close 错误不再把已持久化成功改报为失败。未改变 capture 内容、Schema/API、公开入口或其他完成点。

新增两条彼此独立的固定非敏感回归夹具，分别覆盖既有 DB 新 capture 与 idempotent repeat。两者各自使用独立 test ID／fixture ID、close 失败注入、before／after DB 与 audit 计数、页面合同、sentinel hash 及零 sidecar／staging／临时残留断言。新 Evidence 写入 `lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/`；初始 `lifeos/engineering/LIFEOS-P3-096/evidence/` 保持逐文件 SHA-256 不变。

## 修复／验证目标

1. 以 D-0400 晚到提交为只读候选，验证 capture 的返回状态与 DB、audit、页面、sidecar、staging 和临时对象后置状态一致。
2. 逐项验证 future capture／saved、saved 时间不一致、逆序或失效 repeat、审计时间倒退及 clear count 错误均全量 fail closed。
3. 以独立 fixture、test ID、实际执行、before／after 断言和结构化 Evidence 关闭 `ABF-M-001` 至 `ABF-M-020`，禁止由 unit suite 汇总结果批量映射 PASS。
4. 保全全部 P3-094／P3-095 历史资产，保持真实数据、外部能力、风险、冻结、基线和阶段边界不变。

## 事实与实际修改

启动门先复算晚到提交 Manifest 的 10 个候选文件，10/10 均与记录 hash 一致。随后从 Manifest 指定的当前 P3-094 路径机械复制候选 runtime、CLI、tests、runner 和 README 至新的 `lifeos/engineering/LIFEOS-P3-096/`；初次 PM Evidence `sources/` 仅作只读对照。

晚到 runtime 已包含 D-0399 三项实现修正：staging 清理被移到不可回滚完成点之前，失败时恢复页面并保持 DB 不变；capture 与 saved 使用同一时间；audit 按 ID／时间重放 active 集合并核对 repeat、clear count 和 future window。因此本任务未改变业务 Schema/API 或公开入口，只将源码任务标识改为 P3-096。

工程侧专用 `scripts/run_p3_096.py` 将 test fixture 前缀收口为 `/private/tmp/lifeos-p3-096-*`。Rework runner 在干净临时副本加载 runtime，逐一执行 30 个独立 test/fixture ID，再生成 20 行聚合结果；新增的两个 ID 均映射 `ABF-M-006`，但保留独立 fixture、结构化结果与失败注入断言。`M-005` 分别执行初始化、commit、发布失败；`M-012` 分别执行 unknown／cleared repeat；`M-014` 分别执行 count 过大／过小；`M-016` 分别执行大小写、空串、NULL、BLOB；`M-017` 分别执行重复 id／idem_key。`M-018` 与 `M-019` 直接自测缺字段和 suite-pass-but-row-missing 自动门，均确认 `NOT PASS — DO NOT SUBMIT` 与 Not Implemented 非零。

首次完整自检按设计阻断：`M-004` 的 DB、audit、页面 bytes/hash 和残留均满足合同，但 runner 把 rollback 后页面 inode 变化错误等同于可观察页面变化，导致 18/20。包内将该断言收敛为 ABF 要求的 exists/type/nlink/size/SHA-256 不变，同时仍在 `state_transitions.json` 保留完整 device/inode 供复核。第二次完整自检为 20/20；该包内修正不计正式 Rework。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-096/src/local_capture.py`
- `lifeos/engineering/LIFEOS-P3-096/tests/test_runtime.py`
- `lifeos/engineering/LIFEOS-P3-096/scripts/run_p3_096.py`
- `lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/`
- `lifeos/deliverables/LIFEOS-P3-096_post_commit_audit_evidence_closure.md`

初始 `lifeos/engineering/LIFEOS-P3-096/evidence/` 未被覆盖。未修改 ABF、任何 P3-094／P3-095 工程／交付物／Review／Evidence／Manifest、PM Evidence、任务卡或项目账本。

## 非范围

- 不重新设计已通过的路径、文件类型、canonical Schema、来源、render／clear 页面合同。
- 不新增产品功能、公开入口、业务 Schema、migration、并发／崩溃恢复或生产能力。
- 不访问、迁移或修复既有个人文件／DB；不使用真实个人内容。
- 不启用网络、云、第三方、Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。
- 不关闭／重开 R-0051，不冻结资产或 Schema/API，不恢复工程基线，不进入 Stage 4，不创建独立复评。

## 测试摘要

- 复跑命令：`PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/engineering/LIFEOS-P3-096/scripts/run_p3_096.py`
- P3-094 晚到候选 baseline：117 PASS / 0 FAIL；旧 PM 六反例：6 PASS / 0 FAIL。
- P3-096 unit：53 tests，退出码 0；新增既有 DB capture 与 idempotent repeat 的 post-commit close 独立回归均通过。
- ABF 矩阵：20 PASS / 0 FAIL；实际独立执行 ID：30；runner 退出码 0。
- P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。
- ABF V1/V2 hash：一致；晚到 Manifest 候选：10/10 一致；P3-094／P3-095 历史 before/after hash：一致；初始 P3-096 Evidence 与 P3-096 PM Evidence before/after 逐文件 hash：一致。
- 禁止能力扫描：关闭；Evidence 中 SQLite／HTML／pyc／cache：0；`/private/tmp/lifeos-p3-096-*` 残留：0。

## Evidence

- Rework 1 Manifest：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/MANIFEST.md`
- 汇总：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/summary.json`
- 验收矩阵：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/acceptance_matrix.json`
- 实际执行 ID：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/executed_test_ids.json`
- 状态转换：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/state_transitions.json`
- 失败注入：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/failure_injection_results.json`
- 审计语义：`lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/audit_semantics_results.json`
- unit／baseline 日志：`unit_test.log`、`baseline_candidate.log`
- source／history hash：`source_history_hashes.json`
- 临时残留：`temporary_residue.json`
- 复跑说明：`rerun.md`

## 角色与关卡

- 主责角色：技术架构负责人／Codex 工程执行；完成 capture 完成点、失败原子性、可复跑 runner 与 Evidence 自动门。
- 数据／领域模型协审检查点：来源、capture/saved 时间、repeat active 关系、clear count 与生命周期重放均有独立负向夹具；Gate 2 为 execution-side PASS candidate。
- AI 信任与安全协审检查点：仅固定非敏感本地夹具；无 AI、网络、第三方或外部处理；Gate 3 的禁止能力关闭态通过。
- 技术可行性检查点：20 行矩阵、30 个实际执行 ID、53 个 unit、baseline、历史 hash 与初始 Evidence 不可覆盖检查均通过自动阻断门；Gate 4 为 execution-side PASS candidate。
- 仍需关卡：正式 PM 验收；用户采纳；采纳后才可另建全新隔离独立复评。本执行会话不得评审自身 P0 成果。

## 剩余风险与建议

事实：本结果严格限于当前候选 hash、固定非敏感 task-local SQLite／HTML 夹具、单进程和有限 Stage 3。R-0051 仍为 P0 / Open。

推断：当前 Evidence 支持 P3-096 按冻结 ABF 提交 PM，但不能外推为真实个人文件、并发／崩溃恢复、生产环境或风险关闭已通过。

建议：PM 复算 Rework 1 Manifest、历史及初始 Evidence hash，并复跑唯一 runner和既有独立反例。PM Pass 与用户采纳后，再依任务卡创建全新隔离独立复评。

## 用户确认与本地预检

- 本轮是否触发新的用户确认：No；没有扩大目录、数据、入口、能力、Schema/API、风险、冻结或阶段边界。
- 是否需要独立复评：Yes，Conditional on PM Pass and user adoption；不得由本会话启动。
- 本地模型预检：跳过。原因是本轮属于 P0、真实本地 DB 边界候选、失败原子性、删除／审计可信与 Evidence 诚实的高风险最终判断；任务卡明确允许跳过，本地模型不得替代人工复核或 PM 验收。
- 需要 PM 决策：No；仅需按既定 L1 + Frozen L2 流程验收。
