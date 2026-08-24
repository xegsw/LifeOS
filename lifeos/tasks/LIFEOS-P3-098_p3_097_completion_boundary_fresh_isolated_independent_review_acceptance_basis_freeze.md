# LIFEOS-P3-098｜P3-097 完成点边界全新隔离独立复评 Acceptance Basis Freeze

## 冻结信息

- 任务 ID：`LIFEOS-P3-098`
- ABF ID／版本：`ABF-P3-098-v1`
- 生效决策：D-0408
- 冻结时间：2026-08-22（独立评审会话启动前）
- ABF 文件 SHA-256：由 PM 冻结后记录在任务卡与 D-0408；本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 要完成的单一结果：由未参与 P3-097 工程执行或 PM 验收的全新隔离评审会话，独立判断当前固定 hash 是否满足 live DB 唯一不可逆完成点、失败关闭、task-local 路径和 Evidence 诚实边界。
- 明确不冻结的产品需求：不冻结 P3-097 资产、Schema/API、生产部署、真实用户 DB、风险状态或阶段。
- 明确非范围：不修改 P3-097；不复用／复制／调用其 runner、tests 或 PM 反例作为独立测试；不访问真实个人数据、外部系统或网络；不作风险关闭、冻结、基线恢复或 Stage 4 判断。

## 授权和能力边界

- 允许目录：仅 `lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md`、`lifeos/reviews/LIFEOS-P3-098/independent_review.md` 与 `lifeos/reviews/LIFEOS-P3-098/evidence/`。
- 允许数据与夹具：只读 P3-097 固定候选；`/private/tmp/lifeos-p3-098-*` 新建固定非敏感文本、task-local SQLite、HTML、sidecar、链接和哨兵。
- 允许入口／接口：仅直接调用被评审候选的公开 runtime／CLI；不得调用 P3-097 runner 或 tests。
- 允许工具／环境：离线本地 Python 标准库、SQLite、shell、hash；不使用浏览器或网络。
- 严格只读资产：P3-094 至 P3-097 的任务、ABF、工程、交付物、Review、PM/Engineering Evidence 与 Manifest；全部项目账本。
- 禁止能力与外部目标：真实个人文件／DB／路径、网络、云、第三方、凭据、Vault、Tauri/IPC、导出、同步、多设备、L3、外部用户及攻击能力扩展。
- 投递前额外用户确认：用户已于 D-0408 采纳 P3-097 PM Pass 并授权 PM 创建本任务；只有用户把本任务卡路径投递到全新隔离独立评审会话时才启动执行。

## 引用的 L1 长期原则

- L1-1：所有独立夹具与文件操作必须留在新建 task-local 目录，历史资产只读。
- L1-2：固定 capture/source/audit 关系必须真实可追溯。
- L1-3：失败不得留下已发布状态；已发布成功不得被后置释放错误改报失败。
- L1-4：DB、page、sidecar、shadow、temp 与哨兵终态必须一致。
- L1-5：独立 runner、逐行 Evidence、hash 和 Manifest 必须可复核，不能自证循环。
- L1-6：禁止能力默认关闭，不扩大目录、数据、入口或授权。
- L1-7：独立 Pass 也不自动冻结、关闭风险或推进阶段。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 评审独立性成立 | P1 | 新写 runner／fixture／断言，不导入、复制或执行 P3-097 runner/tests/PM 反例；评审会话与执行、PM 会话隔离 | 独立性不足则 Blocked 或 Rework，不得写 Pass |
| ABF-I-02 | 固定候选与历史完整 | P1 | 任务卡列出的 current hash、Engineering/PM Manifest 前后一致 | 任一不明漂移立即停止，不在评审侧修复 |
| ABF-I-03 | live DB 发布是唯一不可逆完成点 | P1 | saved 与 repeat 各自只有一次实际发布；发布前所有可失败检查完成 | 发布前失败保持 live DB/audit/page/sentinel 不变且零残留 |
| ABF-I-04 | 实际发布失败原子关闭 | P1 | 对真实 `os.replace` syscall 失败而非仅 pre-hook，existing saved、repeat、missing DB 均失败关闭 | 不存在 DB/page 半变化、sidecar/shadow/temp 或假成功 |
| ABF-I-05 | 发布后释放错误保持状态诚实 | P1 | saved/repeat 在 post-publish FD close 错误下仍返回准确成功且状态一致 | 不得出现失败返回但 DB/audit 已发布 |
| ABF-I-06 | 候选 close／sidecar／清理均在发布前收口 | P1 | close 抛错、sidecar 产生、暂态重试和持续失败均不造成 live 半状态 | 失败分支 live 状态不变；支持范围内终态零残留 |
| ABF-I-07 | 页面与 DB 完成点一致 | P1 | saved 成功使旧页失效；repeat 保持可信页；页面失效或发布失败不产生 DB/page 不一致终态 | 失败后 DB/page 同时保持 before，哨兵不变 |
| ABF-I-08 | task-local 路径与文件类型关闭 | P0 | 祖先目录链接、最终 DB/page 链接、特殊文件、非规范路径及 render/clear 外部目标均在变更前拒绝 | 外部哨兵、live DB、页面和目录均不变 |
| ABF-I-09 | Schema／source／audit 语义无回退 | P1 | canonical Schema、来源、时间、saved/repeat/clear 审计与重启复读满足既有合同 | 不可信 DB fail closed，不生成误标页面 |
| ABF-I-10 | 独立 Evidence 完整诚实 | P1 | 每行唯一 test/fixture/execution ID、before/after、日志、源码、hash、非自指 Manifest；缺项时非零退出 | P0/P1/Unknown/Not Implemented 任一非零不得 Pass |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 独立操作／失败点 | 预期结果 | 必须保持不变 | 独立测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | runtime + CLI | 新 task-local 目录 | 首次 saved 与关闭重开复读 | 精确一条 capture/audit；返回与复读一致 | 哨兵、目录边界 | IR-P3-098-001 | before/after、reopen |
| ABF-M-002 | runtime | 已有 active capture/page | repeat 与同键异文拒绝 | repeat 只增精确 audit；冲突零变化 | capture、page、哨兵 | IR-P3-098-002 | DB/audit/page diff |
| ABF-M-003 | runtime | existing DB/page | 实际 live `os.replace` saved 失败 | 明确失败、完整回滚、零残留 | DB/audit/page/sentinel | IR-P3-098-003 | syscall trace、hash |
| ABF-M-004 | runtime | existing repeat/page | 实际 live `os.replace` repeat 失败 | 明确失败、完整回滚、零残留 | DB/audit/page/sentinel | IR-P3-098-004 | syscall trace、hash |
| ABF-M-005 | runtime | DB 缺失 | 初次 live `os.replace` 失败 | 返回失败且 DB 仍缺失、零残留 | 哨兵、目录 | IR-P3-098-005 | existence/hash |
| ABF-M-006 | runtime | candidate committed, live 未发布 | candidate close 抛错 | 不发布，live 状态不变、零残留 | DB/audit/page/sentinel | IR-P3-098-006 | trace、before/after |
| ABF-M-007 | runtime | candidate sidecar | 首次清理失败后恢复；持续清理失败 | 暂态可恢复成功；持续失败不发布且零残留 | 失败分支 live 状态 | IR-P3-098-007 | attempts、residue |
| ABF-M-008 | runtime | existing DB/page | page invalidation 失败与实际发布失败 | 两分支均无 DB/page 不一致 | DB/audit/page/sentinel | IR-P3-098-008 | page/DB hashes |
| ABF-M-009 | runtime | saved 发布完成 | post-publish gate FD close 错误 | 准确 `saved`，DB/audit/page 成功终态 | 哨兵、边界 | IR-P3-098-009 | return/state/trace |
| ABF-M-010 | runtime | repeat 发布完成 | post-publish gate FD close 错误 | 准确 `idempotent_repeat`，页面保持可信 | capture/page/哨兵 | IR-P3-098-010 | return/state/trace |
| ABF-M-011 | public entries | 链接／特殊文件／非规范路径夹具 | ancestor、final DB/page、FIFO/dir/hardlink | 全部变更前拒绝 | 目标、live DB/page/sentinel | IR-P3-098-011-* | 每类独立 ID |
| ABF-M-012 | render/clear | DB 父目录外固定哨兵 | 调用方指定外部 output | 两入口均拒绝且无变化 | 外部哨兵、DB/page | IR-P3-098-012 | before/after |
| ABF-M-013 | read/render/capture | Schema/source/audit 变异 | 缺约束、错来源、未来/逆序审计 | 全部 fail closed；旧页按合同失效 | DB bytes、外部状态 | IR-P3-098-013-* | 每变异独立 ID |
| ABF-M-014 | 独立 runner | 故意缺行／重复 ID／缺断言 | 运行 Evidence 负门 | Not Implemented 非零、退出非零 | 不得冒充完整 Pass | IR-P3-098-014 | negative gate |
| ABF-M-015 | 静态／hash | 固定候选与禁止能力 | 前后 hash、依赖和字符串扫描 | hash 全一致；禁止能力无入口 | 全部只读资产 | IR-P3-098-015 | hash/scan |

## Evidence 合同

- 可运行 runner／测试源码：必须全新编写；不得包含来自 P3-097 runner/tests/PM 反例的复制片段。
- 逐行结构化结果：15 个父行及所有 `-*` 子行均具唯一 test、fixture、execution ID。
- before／after 状态：DB bytes/hash、captures/audit、page、sidecar/shadow/temp、sentinel、路径对象类型。
- 日志／快照：实际 syscall 失败、调用顺序、返回结果和终态；只含固定非敏感内容。
- source／history hash：执行前后复算任务卡固定 hash 与两个 Manifest 全量条目。
- Manifest：列出所有独立 Evidence 相对路径、SHA-256 与用途；非自指，不覆盖 P3-097。
- 复跑命令：离线、确定性、全新 `/private/tmp/lifeos-p3-098-*` 夹具；记录预期退出码。
- 临时清理：所有评审临时目录精确清理，系统残留为零。

## 计数与 Pass 公式

- P0：0
- P1：0
- P2：0
- Unknown：0
- Not Implemented：0
- Pass 公式：独立性成立；ABF-I-01 至 I-10、M-001 至 M-015 及全部子行独立 PASS；固定 hash 与 Manifest 一致；runner 退出 0；残留为 0；五项计数均为 0。
- 允许的 N/A：无；不可达分支须用独立结构证据证明，不得静默 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：仅限独立评审交付／Evidence 自身仍可在不改变 ABF、候选 hash、目录、数据、入口和授权的前提下补正。
- 必须新建任务条件：需要修改 ABF、候选 hash 或评审边界；达到两轮仍不完整；或独立性已被污染无法恢复。
- 被评审候选失败规则：发现映射 L1/本 ABF 的实质 P0/P1、Evidence 冲突或完成定义缺口时，P3-098 结论为 Rework，并把 P3-097 返回其同一 Frozen ABF 的 Rework 1/2；不得由评审会话修改候选。
- Blocked 条件：独立性不足、hash 不明漂移、环境无法完成固定夹具、需要真实数据／外部能力或连续不可恢复的本地执行阻断。

## 候选基线与只读保全

- 候选输入 hash／Manifest：任务卡列出 P3-097 task/ABF/deliverable、5 个 source、Engineering Manifest、PM Review 与 PM Evidence Manifest 的固定 SHA-256。
- 历史只读 hash／Manifest：P3-097 Engineering Manifest 16 项与 PM Evidence Manifest 23 项，以及其引用的 310 项历史集合。
- 允许发生变化的文件：仅 P3-098 交付物、独立 Review 与独立 Evidence。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未启动。
- PM 处理：启动前可解释文字，不得实质修改冻结标准；需实质修改则关闭并新建任务。
- 最终冻结版本：`ABF-P3-098-v1`
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
