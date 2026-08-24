# LIFEOS-P3-096｜PM 验收 Review

## 验收信息

- 任务 ID：`LIFEOS-P3-096`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md`，规范性继承 V1
- ABF ID／版本／SHA-256：`ABF-P3-096-v2` / `bc529ddaf2ed965e96047dc6681acdd9e17c892a4db2ddd850038cbbd239ea09`
- V1 SHA-256：`2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58`
- ABF 是否在专项会话开始前 Frozen：Yes
- 本次反例是否全部映射到既有 L1/L2：Yes；L1-3、L1-4、ABF-I-01、ABF-I-02
- 正式 Rework 次数／上限：2／2；已达到上限且仍未通过
- 是否为受控能力包：Yes
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-096_post_commit_audit_evidence_closure.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-096/pm_evidence/initial/`；`lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/`
- 执行授权证据：D-0404 用户明确允许 Rework 1/2；交付物记录任务卡完整路径、新隔离 Codex 工程会话、`gpt-5.6-terra + high` 及精确接收时间 `2026-08-22 22:07:16 CST (+0800)`。路径、会话、模型、时间和范围成立。
- 任务验收状态：`Closed — Acceptance Not Met / Formal Rework Limit Reached`
- 资产冻结状态：`Not Frozen`
- 是否允许进入下一任务：Conditional；只有用户确认后才可创建具有新授权和新 ABF 的后继任务，P3-096 不得继续整改
- 是否允许进入下一阶段：No
- 更新时间：2026-08-22

## 首次 PM 总结（D-0403）

1. ABF V1/V2、治理文件和晚到候选 hash 均与冻结记录一致；P3-096 Engineering Evidence Manifest 17/17、晚到候选 10/10、P3-094/P3-095 历史只读资产 253/253 可复算且无漂移。
2. PM 在全新、非冲突命名的 `/private/tmp` 隔离目录复跑提交 runner：20/20 ABF 行 PASS，28 个唯一 test ID、28 个唯一 fixture、110 个断言、51 项 unit、候选 baseline 117 PASS、旧 PM 六反例 6 PASS，退出码 0，临时夹具残留 0。
3. 逐行 Evidence 自动门已实质改善：M-001 至 M-020 均有实际执行，M-005／012／014／016／017 的子变体分别独立记录；M-018／019 能阻断缺字段和 suite 总通过但缺行的情形。本轮 `Not Implemented=0`。
4. PM 独立 `PM-P3-096-CE-01` 仍稳定复现完成点 P1：既有 DB 的真实 commit 完成后，固定注入连接 close 失败，调用返回 `OperationalError`，但 captures／audit 从 1／1 变为 2／2，页面由存在变为不存在；哨兵不变。失败回执与持久化事实矛盾。
5. 该反例不是新增验收标准，直接映射 L1-3、L1-4、ABF-I-01 与 ABF-I-02。ABF、用户结果、目录、数据、入口、能力和授权均无需变化，因此继续同一 P3-096 Rework；不新建任务。
6. 计数：P0=0、P1=1、P2=1、Unknown=0、Not Implemented=0。P2 是交付物只记录接收日期而未记录任务卡要求的精确接收时间，不与 P1 重复计数。
7. 本地模型预检跳过：本轮是删除／真实本地数据生命周期、失败原子性、审计可信和 Evidence 诚实的高风险最终判断；本地模型不得替代 PM 裁决。

## 两层验收治理核对

- 满足的 L1：L1-1、L1-6、L1-7、L1-8、L1-10 的提交 Evidence 与本次复跑部分成立。
- 未满足的 L1：L1-3 生命周期完整、L1-4 失败关闭；L1-9 的执行授权本身成立，但精确接收时间记录存在 P2 清洁缺口。
- 满足的 L2：ABF-M-001 至 ABF-M-020 的提交 runner 与 PM 复跑均为 PASS；历史保全、禁止能力关闭和临时清理成立。
- 未满足的 L2：ABF-I-01、ABF-I-02。既有 DB capture 在 commit 后 close 失败时仍以失败退出并留下新持久化。
- PM 是否在提交后新增无法映射到 L1/L2 的标准：No
- 新发现问题分类：当前任务失败；同边界正式 Rework
- 是否需要实质修改 ABF：No
- 是否仍满足同任务 Rework 全部条件：Yes
- 是否达到两轮正式 Rework 上限：No；当前 1／2
- 终止状态：N/A

## 测试与 Evidence

- 提交 Manifest：17/17，0 mismatch。
- D-0400 晚到候选 Manifest：10/10，0 mismatch。
- ABF hash：V1/V2 均一致；治理文件 hash `86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c` 一致。
- P3-096 source hash：6/6 一致；runner 与 Evidence `runner_source.py` hash 相同。
- P3-094/P3-095 历史：253/253 before/after 一致；PM 验收未修改历史工程、Review 或 Evidence。
- 提交 runner PM 复跑：20 PASS / 0 FAIL；28 个唯一实际执行 ID；51 unit；exit 0。
- PM 独立反例：0 PASS / 1 FAIL；exit 1；P1=1。
- 第一次 PM 复跑曾把 PM 输出目录误命名为 runner 保留的 `lifeos-p3-096-*` 夹具前缀，runner 因检测到该输出目录而按设计以 P2=1／exit 1 阻断；改用新的非冲突 PM 外层目录后 exit 0。该项属于 PM 编排命名冲突，不计候选缺陷，事实与首轮 summary hash 已记录于 PM Evidence。
- PM 临时目录将在 PM Evidence 固化后精确清理；Engineering Evidence 未被覆盖。

## 角色与关卡验收

- 主责角色：技术架构检查未通过；完成点仍可在 commit 后 close 失败时产生矛盾状态。
- 数据／领域模型：Gate 2 未通过；失败回执与实际 capture/audit 生命周期不一致。
- AI 信任与安全：Gate 3 的网络、云、第三方、Tauri/IPC、Vault、导出和真实个人数据关闭态通过；不代表整体任务通过。
- 技术可行性：Gate 4 未通过；既有矩阵未覆盖并未阻断 post-commit close 失败。
- 是否需要独立评审：当前不允许；仅在同一 P3-096 重新 PM Pass、用户采纳后创建全新隔离独立复评。
- 是否属于关键冻结事项：No；不得冻结任何资产。

## 受控能力包关卡

- 执行侧完成包内自检并报告首次 18/20 后修正为 20/20；该提交前修正不计正式 Rework。
- runner、逐项结果、日志、状态快照、hash、Manifest 与复跑入口可复核；逐行 Evidence 不再由 suite 总结果批量映射。
- 历史只读资产和禁止能力关闭态成立。
- PM 首次正式验收发现实质 P1，记录正式 Rework 1／2。
- 不触发新用户授权：整改仍是同一结果、同一 ABF、同一目录、同一固定非敏感数据和同一授权边界。

## 整改要求

1. 对既有 DB capture 建立明确的不可回退完成点：commit 成功后，连接 close 或其他完成后清理／检查失败不得再把已持久化结果返回为失败；或在仍可回滚的边界内完成所有可能失败步骤。返回值必须始终与 DB、audit、页面事实一致。
2. 为“真实 commit 完成后 close 失败”增加独立 fixture、test ID、before/after、哨兵与零残留断言，并纳入 ABF-I-01/I-02 的自动阻断 Evidence；同时覆盖 idempotent repeat 的同类完成点。
3. 交付物补记任务卡投递的精确接收时间；不修改 ABF 或历史 P3-094/P3-095 资产。
4. 新提交写入 P3-096 自身新 Evidence，保全本次 Engineering Evidence 与 PM Evidence；PM 复验时正式 Rework 计数仍为 1／2，只有再次正式失败才增加到 2／2。

## 资产、风险与下一步

- P3-096：Rework 1／2；Not Frozen。
- P3-094：继续 Closed — Acceptance Not Met / Superseded；全部历史只读。
- P3-095：历史状态不变；全部资产只读。
- R-0051：P0 / Open；不得关闭。
- 允许下一步：仅同一 P3-096 在 Frozen ABF v2 下整改并重新提交 PM；现有授权继续有效，无需用户重复授权。
- 不允许：独立复评、新任务、风险关闭、资产或 Schema/API 冻结、工程基线恢复、真实个人文件／既有 DB、网络／云／第三方、Tauri/IPC、导出、Stage 4 或下一阶段。

## 需要用户确认的事项

无。依据 D-0401，两层治理下同一 ABF、同一边界且未达到 Rework 上限的修正无需重复授权。用户如希望停止本任务或改变 ABF／范围，才需要另行确认。

## 用户明确允许（D-0404）

用户已明确回复“允许”，确认 P3-096 可继续 Rework 1/2。该确认与 D-0401 的既有授权连续性一致，不改变 `ABF-P3-096-v2`，不扩大用户结果、目录、数据、入口、能力、风险、冻结或阶段边界；不得创建新任务或独立复评。

## Rework 1/2 正式复验与任务终止（D-0405）

### 验收结论

`Closed — Acceptance Not Met / Formal Rework 2 of 2 / Awaiting User Decision on Successor Task`。

### Evidence 与复跑

- Rework-1 提交 Manifest 17/17、初始 Engineering Evidence 18/18、初始 PM Evidence 25/25、晚到候选 10/10、P3-094/P3-095 历史资产 253/253 hash 全部一致；PM 未修改工程代码或工程 Evidence。
- PM 在全新 `/private/tmp` 固定非敏感夹具复跑提交 runner：20/20 ABF 行 PASS、30 个唯一 test／fixture ID、53 unit、baseline 117 PASS、旧 PM 六反例 6 PASS，退出码 0，临时残留 0。
- D-0403 的 `PM-P3-096-CE-01` 已由当前候选关闭：commit 后 close 抛错不再覆盖 `saved`，反例复跑 PASS、退出码 0；idempotent repeat 的相同 close 路径也有独立回归。
- 新独立反例 `PM-P3-096-R1-CE-02` 仍为 FAIL、退出码 1：既有 DB 的真实 commit 完成后，固定模拟 close 留下 task-local `capture.sqlite-journal`；随后现有 post-commit sidecar 检查返回 `CaptureError`，但 captures/audit 已从 1/1 变为 2/2、旧页消失且 sidecar 存在，哨兵保持不变。
- 新反例只使用本任务固定非敏感 task-local 夹具，不接触真实个人文件／既有 DB，不联网；它直接映射 L1-3、L1-4、ABF-I-01、ABF-I-02，不是提交后新增标准。
- 本地模型预检因删除／真实本地数据生命周期、失败原子性、审计与 Evidence 诚实的高风险最终判断继续跳过。

### 计数与两层治理

- P0=0；P1=1；P2=0；Unknown=0；Not Implemented=0。
- L1-3／L1-4：未通过；失败回执仍与不可回退的持久化事实冲突。
- ABF-I-01／I-02：未通过；完成点之后仍有可把已提交成功改报为失败的 sidecar 检查。
- ABF-M-001 至 M-020 的提交 Evidence：全部实际 PASS；这不能覆盖 PM 已复现的不变量反例。
- 是否修改 ABF：No。
- 是否达到两轮正式 Rework 上限：Yes。D-0403 为第 1 轮，本次 D-0405 为第 2 轮；任务仍未通过。
- 依 D-0401 与 `ACCEPTANCE_GOVERNANCE.md`，P3-096 必须终止为 `Closed — Acceptance Not Met`，不得继续 Rework 3、attempt 或同任务补丁。

### 角色与关卡

- Gate 2：未通过；capture/audit 生命周期与失败回执不一致。
- Gate 3：禁止的网络、云、第三方、Vault、Tauri/IPC、导出和真实个人数据仍保持关闭。
- Gate 4：未通过；完成点不变量仍有可复现失败分支。
- 不允许进入全新隔离独立复评、风险关闭、冻结、工程基线恢复或 Stage 4。

### 资产、风险与下一步

- P3-096：`Closed — Acceptance Not Met`；全部工程、两轮 Engineering Evidence、PM Evidence、Review、交付物与 Manifest 转为只读历史。
- P3-094／P3-095：状态不变并继续只读。
- R-0051：保持 P0 / Open，不关闭。
- 资产：Not Frozen；不冻结 Schema/API，不恢复工程基线。
- 若继续，只能由 PM 创建新的后继任务、新 ABF 和新授权；不得把 P3-096 重新打开或增加 Rework 3。
- 本轮不自动创建后继任务，等待用户确认是否创建单一后继任务以完整消除所有 post-commit 可失败检查，而不是再做单点补丁。

### 需要用户确认

请确认是否创建新的后继任务。PM 建议创建一个新的单一任务，冻结“不可回退 commit 后不得存在任何能把成功改报为失败的清理、close、路径稳定或 sidecar 检查”这一完整结果，并一次覆盖新 capture 与 idempotent repeat；新任务不会关闭 R-0051、冻结资产或进入 Stage 4。
