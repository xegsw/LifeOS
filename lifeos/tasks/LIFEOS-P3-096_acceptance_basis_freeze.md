# LIFEOS-P3-096 Acceptance Basis Freeze

## 冻结信息

- 任务 ID：`LIFEOS-P3-096`
- ABF ID／版本：`ABF-P3-096-v1`
- 生效决策：D-0401
- 冻结时间：2026-08-22
- SHA-256：由 PM 在冻结后记录于任务卡校验区与 D-0401；本文件不使用自指 hash。
- 状态：Frozen
- 本文件在专项会话开始前冻结：Yes

## 本轮唯一用户结果

以 P3-094 attempt-9 的只读候选为输入，仅关闭 D-0399 三项缺口：capture 完成点与返回状态一致、审计时间／顺序／clear count 语义可信、每个强制矩阵行由实际独立执行决定 PASS。

本 ABF 不冻结未来产品需求，不冻结 Schema/API，不代表风险关闭、资产冻结或 Stage 4 准入。

## 授权和能力边界

- 允许目录：新建 `lifeos/engineering/LIFEOS-P3-096/`、新交付物及 `/private/tmp/lifeos-p3-096-*`。
- 允许数据：固定非敏感测试文本和本任务新建 SQLite／HTML 夹具。
- 允许入口：候选 `capture()`、`list_today()`、`safe_snapshot()`、`render_today()`、`delete_all()` 及既有 CLI；不得新增公开入口。
- 严格只读：全部 P3-094、P3-095 资产及项目账本。
- 禁止：真实个人文件／DB／路径、网络、云、第三方、Vault、Tauri/IPC、导出、同步、多设备、L3、外部用户、风险关闭／重开、冻结、基线恢复和 Stage 4。
- 投递前额外用户确认：None；D-0401 已授权建立本任务，任务卡路径投递即执行授权。

## 适用的 L1 原则

- L1-1 数据主权：所有运行和清理仅限新 task-local 目录。
- L1-3 生命周期完整：capture 成功／失败与 DB、页面、audit、临时对象的后置状态一致。
- L1-4 失败关闭：返回失败时不得留下新增持久化或半成品。
- L1-6 审计可信：时间、事件顺序、active 集合和 clear count 可重放一致。
- L1-7 Evidence 诚实：每行 PASS 来自独立实际执行。
- L1-8 历史保全：P3-094／095 全部只读。
- L1-9 授权不漂移：不得利用新任务触及真实或外部能力。
- L1-10 可复核性：固定候选 hash、夹具和 runner 可重复得到相同结果。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | capture 返回与持久化事实一致 | P1 | success 恰有预期持久化且零残留；failure 的受保护状态完全不变且零残留 | 不得出现失败但新增 DB／capture／audit／页面变化或 staging |
| ABF-I-02 | capture 完成点之后不存在可导致矛盾失败的清理步骤 | P1 | 每个清理／commit／publish 失败点均产生唯一合同状态 | 无法证明原子性时必须在 commit 前停止并回滚 |
| ABF-I-03 | capture 与 audit 时间语义一致 | P1 | capture_saved 时间与对应 capture 时间相等且不位于允许时钟窗口之外 | 全量读取失败；render 使旧页面失效；DB 不变 |
| ABF-I-04 | audit 可按 id／时间顺序重放 | P1 | repeat 不早于 saved、只引用 active capture；clear count 等于清理前 active 数 | 全量失败，不发布部分记录 |
| ABF-I-05 | 每个冻结矩阵行独立实际执行 | P1 | 每行存在唯一 fixture、测试 ID、执行记录、断言和 Evidence | 缺一项即 Not Implemented，runner 非零退出 |
| ABF-I-06 | 历史资产和 task-local 边界不变 | P0 | P3-094／095 hash 一致，外部哨兵不变，临时残留为 0 | 任何越界／覆盖立即停止并报告 P0 |

## 冻结验收矩阵

每一行必须独立创建夹具、执行动作并决定 PASS；允许一个测试函数通过参数化产生多行，但 `executed_test_ids.json` 必须分别记录每个行 ID 和实际 fixture，不得由 suite 总结果批量映射。

| 行 ID | 入口／前置状态 | 操作或失败点 | 预期结果 | 必须保持不变 | Evidence |
|---|---|---|---|---|---|
| ABF-M-001 | capture／既有 canonical DB＋有效页面 | staging 创建后首次 unlink 失败、重试后成功 | capture 成功或在 commit 前失败；不得失败后提交 | success 零 staging；failure 时 DB／audit／页面 hash 不变 | 独立状态转换 |
| ABF-M-002 | capture／既有 canonical DB＋有效页面 | staging unlink 持续失败 | `CaptureError`；DB／audit／页面不变；零 staging | 外部哨兵和历史 hash | 独立失败注入 |
| ABF-M-003 | capture／新 DB | staging unlink 持续失败 | `CaptureError`；不得留下 DB、Schema、audit、sidecar、页面或 temp | 父目录哨兵 | 独立失败注入 |
| ABF-M-004 | capture／既有 canonical DB | capture commit 失败 | `CaptureError`；新增 capture／audit 为 0；页面不变；零 sidecar/temp | DB bytes／inode／size/hash | 独立 commit 注入 |
| ABF-M-005 | capture／新 DB | 初始化／commit／发布各失败点 | 每个失败均无 DB、部分 Schema、audit、sidecar、页面或 temp | 父目录哨兵 | 每个失败点独立行结果 |
| ABF-M-006 | capture／既有 canonical DB | 正常新增记录 | 返回 saved；capture_saved 与 capture 同时间；页面按既有合同失效；零残留 | 既有记录和历史 audit 不变 | before／after 状态 |
| ABF-M-007 | capture／新 DB | 正常首次记录 | 返回 saved；精确一条 capture／saved audit；canonical DB；零残留 | 父目录外不变 | before／after 状态 |
| ABF-M-008 | list／snapshot／render | capture.created_at 位于允许窗口之外的未来 | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 独立审计语义夹具 |
| ABF-M-009 | list／snapshot／render | capture_saved 时间位于未来 | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 独立审计语义夹具 |
| ABF-M-010 | list／snapshot／render | capture_saved 时间与 capture.created_at 不相等 | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 独立审计语义夹具 |
| ABF-M-011 | list／snapshot／render | capture_repeat 早于对应 capture_saved | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 独立审计语义夹具 |
| ABF-M-012 | list／snapshot／render | repeat 引用未知或已 clear 的 capture | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 两个独立夹具 |
| ABF-M-013 | list／snapshot／render | audit id 顺序中的时间倒退 | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 独立审计语义夹具 |
| ABF-M-014 | list／snapshot／render | captures_cleared detail count 与清理前 active 集合不一致 | 全量拒绝；render 旧页面失效 | DB bytes／hash 不变 | 至少 count 过大、过小各一夹具 |
| ABF-M-015 | clear／两条 active capture | 正常 DELETE | 返回 count=2；audit detail count=2；当前 active 集合为空 | 无 page、sidecar、temp | 独立生命周期夹具 |
| ABF-M-016 | 全读取入口 | source 大小写变体、空串、NULL、BLOB | 四个变体分别实际执行并全量拒绝 | DB 不变；render 旧页失效 | 四个独立结果 ID |
| ABF-M-017 | 全读取入口 | 重复 id、重复 idem_key | 两个变体分别实际执行并全量拒绝 | DB 不变；render 旧页失效 | 两个独立结果 ID |
| ABF-M-018 | runner | 缺少任一必填测试 ID／fixture／断言／Evidence | `NOT PASS — DO NOT SUBMIT`，Not Implemented>0，退出非零 | 不得生成该行 PASS | runner 自测 |
| ABF-M-019 | runner | unit suite 整体通过但一项冻结行未执行 | 缺失行保持 Not Implemented，整体非零 | 不得批量映射 PASS | runner 自测 |
| ABF-M-020 | runner／完整执行 | 所有冻结行实际执行 | 每行唯一记录实际 test ID、fixture ID、断言和 Evidence；汇总与逐行一致 | Manifest 完整、临时残留 0 | 完整复跑 |

## Evidence 合同

- 每个 ABF-M 行必须出现在 `acceptance_matrix.json` 与 `results.json`。
- `executed_test_ids.json` 必须记录行 ID、测试 ID、fixture ID、开始／结束时间、实际结果和对应 Evidence。
- `state_transitions.json` 只记录 exists、type、device、inode、nlink、size、SHA-256 和计数，不保存 DB 内容。
- `audit_semantics_results.json` 逐项记录 M-008 至 M-015。
- `failure_injection_results.json` 逐项记录 M-001 至 M-005。
- 需保存 runner／测试源码、unit／regression 日志、source／history hash、临时残留、复跑命令和非自指 Manifest。
- Evidence 不得包含 SQLite、HTML、pyc、缓存或固定夹具明文之外的数据。

## 计数与 Pass 公式

- P0：越权、越界、历史覆盖或真实／外部能力触达。
- P1：任一冻结不变量失败、矩阵行失败、Evidence 虚假映射或无法证明失败原子性／审计语义。
- P2：不影响安全、生命周期、审计或 Evidence 完整性的清洁问题；本轮仍必须为 0 才可 Pass。
- Unknown：无法判断预期或实际状态。
- Not Implemented：必填行、fixture、实际执行、断言或 Evidence 任一缺失。
- Pass：全部 ABF-M 行 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；历史 hash 一致；禁止能力关闭；临时残留为 0；runner 退出 0。
- 允许 N/A：无。若实际不可执行，必须报告 Blocked 候选或 Not Implemented，不得自行标 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework：仅限修复上述六个不变量和二十行矩阵，ABF 不变。
- 必须新建任务：达到两轮 Rework、需要改变本 ABF、扩大目录／数据／入口／能力／授权、改变 Schema/API／架构／领域语义、风险关闭／冻结／阶段切换，或历史资产无法只读保全。
- Blocked：所需本地工具或输入真实不可用且无法在冻结边界内安全继续；不得用替代网络／外部能力解除。

## 候选基线与只读保全

- 代码候选入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/sources/`
- 候选及 PM Evidence Manifest：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/MANIFEST.md`
- 工程提交 Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/evidence/MANIFEST.md`
- PM 六个反例：`pm_final_invariant_counterexamples.py`／`.json`
- 允许变化：仅 P3-096 新工程目录、新交付物和其新 Evidence。

## 启动前质疑窗口

- 执行方发现歧义时必须在任何复制、修改或测试前停止。
- PM 只可在专项会话开始前发布新的 ABF 版本。
- 专项会话开始后不得实质修改本 ABF；如需修改，P3-096 关闭并新建任务。
