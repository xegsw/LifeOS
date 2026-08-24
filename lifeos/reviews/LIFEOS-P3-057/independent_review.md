# LIFEOS-P3-057 独立评审｜Active Authorization 整改全新隔离复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-057
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review.md`
- 独立评审角色：独立 QA / Evidence Reviewer（新建隔离 Codex 会话）
- 协审视角：技术架构、数据 / 领域模型、AI 信任与安全
- 评审关卡：Gate 2、Gate 3、Gate 4
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-057/independent_review.md`
- 评审结论：**Pass**（仅限当前候选 SQL + 合成 SQLite + 本任务证据的独立复评输入）
- 更新时间：2026-08-21

## 评审摘要

1. **独立性成立。** 在读取 P3-044 攻击资产前已先封存本任务攻击计划和独立性声明；新建 runner 不 import、调用或复制 P3-044 的攻击函数或场景表。它仅以当前 P3-031 候选 SQL 为输入，在系统临时目录的全新合成 SQLite 库运行。
2. **替换 / 重建边界通过。** 在 memory/file × FK ON/OFF × recursive trigger ON/OFF 的八种配置中，对主键冲突、`(logical_key, version_no)` 冲突、双冲突、`INSERT OR REPLACE`、`REPLACE INTO`、两类 `DO UPDATE` UPSERT、`DO NOTHING`、普通重复 INSERT 与 DELETE→INSERT 重建均得到 fail-closed 结果；312 项 P1 断言全部通过。
3. **父 / 子安全包络通过。** 八个 active 父包络字段的单字段和多行改写均被拒绝；scope/action/policy 三个子表的 INSERT、UPDATE、DELETE、REPLACE 及从 active 改绑出 / 改绑入 active 都被拒绝，失败后父行、子行、audit/outbox 快照保持不变。
4. **事务、保存点与合法路径没有回归。** 故意在事务中预写合成 audit 后执行 REPLACE 并 rollback，未留下半状态；保存点回滚后连接仍可安全执行新 proposed 写入。合法 proposed→granted→active、active→superseded 的受控命令路径及 v2 successor 激活均通过。
5. **合同入口与历史证据一致。** 复制 P3-031 工程目录到隔离临时副本后，其合同入口获得 P0 18、P1 29、P2 27，均为 PASS（74/74，退出码 0）。P3-043 历史失败 evidence 4 项与 P3-044 快照/runner/7 项 evidence 的记录 SHA-256 均匹配。
6. **没有发现新增 P0/P1/P2、Not Implemented 或 Unknown。** 独立 runner 的发现计数为 P0=0、P1=0、P2=0、Not Implemented=0、Unknown=0；P2 的两项执行断言均为 hash / 当前受控边界核验通过，不是风险发现。

## 已通过内容

- 当前 SQL 的 `BEFORE INSERT` active-conflict 防线在 SQLite 执行替换式冲突解析前就拒绝写入，因此既不依赖 foreign key 开关，也不依赖 implicit DELETE 是否触发 trigger。
- active 父记录直接 DELETE 被拒绝；因而在本测试模型中无法把已激活父记录移除后再重建。
- active 子表的父键改绑检查同时覆盖 OLD 与 NEW 所属父记录，未发现从 active 移出或移入的旁路。
- 拒绝的语句在各自隔离库中均恢复到操作前安全快照；文件库额外完成 `integrity_check`、`quick_check` 与 `foreign_key_check`，没有发现结构或引用异常。
- 当前候选 SQL SHA-256 为 `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`，与 R-0048 已关闭受控边界所记录 hash 相同。P3-044 的历史 SQL 快照 `0b7f…d376` 仍完整保留；当前候选不同是后续已登记整改的输入演进，不构成 P3-044 historical evidence 冲突。

## 关键问题

- 未发现阻止本次独立复评 Pass 的 P0、P1、明确合同 P2、hash 冲突、不可复核输入或独立性不足。
- 本结论不重新裁决 P3-044 当时的过程例外；它只补回当前候选在明确范围内的全新独立测试证据。

## 必须整改项

无。本次受控范围内没有触发 Rework 或 Blocked 条件。

## 条件通过项

| 条件 | 适用范围 | 失效条件 |
|---|---|---|
| 本评审 Pass | 当前 SQL hash、合成 memory/file SQLite、八种 PRAGMA 配置、单进程本地测试 | 候选 SQL/runner/合同实质变化、出现 P0/P1/明确合同 P2、hash 或独立性失效、或测试扩展到任务非范围 |
| 历史证据保留成立 | 已核验的 P3-043 与 P3-044 文件集合 | 任一文件 hash 变化、manifest 期望值冲突或证据来源不可追溯 |

## 关卡检查

- Gate 1 产品一致性评审：N/A；未改变产品定位、V1 范围或体验。
- Gate 2 数据与来源评审：**Pass（受控范围）**；active 父/子写入的身份、版本、来源性关联和失败原子性在当前候选及合成测试中保持；历史 evidence hash 完整。
- Gate 3 AI 权限与信任评审：**Pass（受控范围）**；active Authorization 的处理器、用途、位置、有效期和策略版本不能经所测替换、重建或直接变异静默扩大；不把数据库合成结果外推为真实确认或真实 actor 验证。
- Gate 4 技术可行性评审：**Pass（受控范围）**；八种 SQLite 配置、事务、保存点、多行语义与隔离 P3-031 合同入口均可复跑。
- Gate 5 用户价值验证评审：N/A；未涉及用户研究或外部用户验证。

## 风险

- 本评审不关闭、调整或重新打开 R-0044、R-0046、R-0047、R-0050；它只为 PM 后续风险判断提供独立证据。
- R-0048/R-0049 不在本任务的风险处理范围内。当前 SQL hash 与 R-0048 已记录的受控边界一致，只是只读核验，不能解释为再次关闭、冻结或扩大该风险边界。
- 未验证真实数据库 / 非空迁移、真实身份与用户确认、并发或 WAL、崩溃恢复、Vault、Tauri/IPC、文件导出、云/同步或外部用户。因此不能外推为生产安全、Schema/API 冻结、工程基线恢复或阶段准入。

## 需要 PM 决策

- 是否采纳本任务的 **Pass** 为 R-0044、R-0046、R-0047、R-0050 后续 PM 风险决策的独立输入。采纳不等于关闭任何风险。

## 最终建议

建议 PM 将 P3-057 作为“全新隔离独立复评已完成且技术范围通过”的任务输入，并在主会话按既定风险关闭和用户确认流程自行判断下一步。本评审不建议冻结资产、恢复工程基线、启用真实能力或进入下一阶段。

证据入口：`lifeos/reviews/LIFEOS-P3-057/evidence/MANIFEST.md`。
