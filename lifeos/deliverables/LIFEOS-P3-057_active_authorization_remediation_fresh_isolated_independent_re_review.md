# LIFEOS-P3-057｜Active Authorization 整改全新隔离独立复评交付物

## 1. 任务与授权边界

- 任务状态：**Completed — 独立复评 Pass（受控范围）**。
- 主责角色：独立 QA / Evidence Reviewer；协审：技术架构、数据 / 领域模型、AI 信任与安全。
- 评审关卡：Gate 2、Gate 3、Gate 4；均仅在当前候选 SQL、合成 SQLite 和本任务 Evidence 的范围内通过。
- 实际执行配置：任务卡指定的 `gpt-5.6-terra` + `xhigh`；没有降级或后备配置。
- 操作范围：工程、历史 Review、账本和历史 Evidence 全部只读；只写入 P3-057 的 review、deliverable、evidence 与本地预检。没有修改 SQL、合同测试、风险账本、冻结状态或历史资产。
- 能力边界：只使用合成 SQLite 内存/临时文件库；没有访问真实数据库、用户数据、Vault、Tauri/IPC、用户文件、导出、网络、云/第三方模型、同步、多设备、L3 或外部用户。

## 2. 已验证事实

### 2.1 新隔离与独立性

在读取 P3-044 攻击资产前，本会话先封存了 `evidence/00_attack_plan_and_independence.md`。该文件预注册了冲突写入、DELETE+INSERT、父/子包络、八配置、事务/保存点、多行语义和合法路径的测试计划，并声明本 runner 不能使用 P3-044 的攻击函数或场景表。

之后创建的 `evidence/fresh_independent_runner.py` 为独立实现：它不 import、不调用、不复制 P3-044 攻击 runner 或场景表，仅读取当前 P3-031 候选 SQL。结构化结果中记录了 `imports_p3_044=false`、`calls_p3_044=false` 和 `copies_p3_044_attack_functions_or_scenario_table=false`。所有案例在 `TemporaryDirectory` 的新建合成数据库运行；没有在原工程目录执行写测试。

### 2.2 当前候选与历史 hash

当前候选 SQL 的运行前/后 SHA-256 均为：

`bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`

它与 R-0048 已记录的有限受控边界 hash 相同。P3-044 历史 SQL 快照仍为：

`0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376`

两者不同，不是证据冲突：当前候选在 P3-044 之后继续经历了生命周期与终态边界的已登记整改；P3-044 快照本身没有被改写。P3-043 失败 evidence 的 candidate、攻击脚本、JSON、文本共 4 项，以及 P3-044 的 SQL snapshot、runner、结果、日志、环境、检查与 source/preservation 文件共 8 项，均逐项匹配其 Manifest 的期望 SHA-256。这些历史核验只证明输入可追溯和未被篡改，**不作为本任务技术 Pass 的证据**。

### 2.3 独立反例矩阵

`fresh_independent_runner.py` 在八个配置中执行：

| 维度 | 覆盖 |
|---|---|
| 存储 | memory、临时 file |
| FK | `foreign_keys` ON、OFF |
| trigger 递归 | `recursive_triggers` ON、OFF |
| 冲突写法 | `INSERT OR REPLACE`、`REPLACE INTO`、普通 INSERT、id/version-key `DO UPDATE` UPSERT、`DO NOTHING` |
| 冲突身份 | 相同 id、相同 `(logical_key, version_no)` 不同 id、双冲突 |
| 重建 | active 父 DELETE 及其后续 INSERT 重建不可达 |
| 父包络 | grantor、processor、purpose、location、valid-from、expires mode/time、policy version 的单字段与多行变异 |
| 子包络 | scope/action/policy 的 INSERT、UPDATE、DELETE、REPLACE、从 active 改绑出及改绑入 active |
| 原子性 | 事务 rollback、保存点 rollback/release、多行 UPDATE 与 `INSERT … SELECT` |
| 合法路径 | proposed→granted→active、active→superseded 受控命令、v2 successor 激活 |

结果为 P1 312 PASS / 0 FAIL，P2 2 PASS / 0 FAIL；所有 file 库均额外通过 `integrity_check`、`quick_check` 和 `foreign_key_check`。每个拒绝路径都比较父、三类子表、audit 与 outbox 的前后快照，未出现父/子孤儿、半写入、generation 改变或伪 evidence 残留。

### 2.4 当前合同入口隔离复跑

为避免原工程目录被测试输出写入，本任务将完整 P3-031 工程目录复制到 `mktemp` 创建的 `/private/tmp` 隔离目录后，运行复制品的 `tests/run_contract_tests.py`。退出码为 0；结果为 P0 18 PASS、P1 29 PASS、P2 27 PASS，共 74/74 PASS，0 FAIL / 0 Not Implemented。完整逐项数据位于 `evidence/p3_031_contract_isolated_results.json`。

## 3. 缺陷分类与结论

| 项目 | P0 | P1 | P2 | Not Implemented | Unknown |
|---|---:|---:|---:|---:|---:|
| 本次发现 | 0 | 0 | 0 | 0 | 0 |
| P3-057 独立测试通过项 | 0 | 312 | 2 | 0 | 0 |
| 隔离 P3-031 合同入口通过项 | 18 | 29 | 27 | 0 | 0 |

未出现任务卡规定必须导致 Rework/Blocked 的条件：没有 P0/P1、没有违反明确合同的 P2、没有 hash 保留失败、没有 Evidence 冲突，也没有独立性不足。

## 4. 合理推断

- 当前候选中的 active-conflict `BEFORE INSERT` 保护在所测 SQLite 语义下早于替换式冲突解析生效，因而覆盖 P3-043 所揭示的“绕过 UPDATE trigger”的根因，而不是只让单一 SQL 文本失败。
- active 父 DELETE 禁止与子表 OLD/NEW 双侧检测结合后，在本任务的合成写入模型下防止 active Authorization 被替换、重建或通过子记录变异静默扩大。
- “整改候选在受控范围内通过独立复评”的技术结论仅由本任务的新 runner 与隔离 P3-031 合同入口复跑支撑。P3-044 历史 evidence 保留只支撑来源完整性，不能单独或共同替代本次独立技术证据，也不能证明真实系统中的操作者身份、用户确认、迁移兼容性或运行时消费门。

## 5. 风险、非范围与不可外推

- 本任务没有关闭、调整或重新打开 R-0044、R-0046、R-0047、R-0050；它们仍由 PM 按账本和用户确认流程处理。
- R-0048/R-0049 未被处理。对 R-0048 hash 的确认是只读一致性核验，不能再次关闭、扩大关闭范围或改变其重开条件。
- 没有测试真实 DB / 非空升级、并发/WAL、多进程、崩溃恢复、性能/容量、真实 Vault/Tauri/IPC/文件导出、云服务或外部用户；因此结果不构成生产安全承诺、Schema/API 冻结、工程基线恢复、真实能力启用或阶段切换。

## 6. 建议与需 PM 决策

**建议：** PM 可将本任务的 Pass 作为 R-0044、R-0046、R-0047、R-0050 后续风险决策所需的独立复评输入。

**需 PM 决策：** 是否采纳该独立输入，并在不越过现有风险关闭、用户确认和冻结关卡的条件下决定后续处理。采纳本交付物不等于关闭风险、冻结资产、恢复基线、启用真实能力或进入下一阶段。

## 7. Evidence 与本地预检

- 独立 Review：`lifeos/reviews/LIFEOS-P3-057/independent_review.md`
- Evidence manifest：`lifeos/reviews/LIFEOS-P3-057/evidence/MANIFEST.md`
- 攻击计划与独立性声明：`lifeos/reviews/LIFEOS-P3-057/evidence/00_attack_plan_and_independence.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-057_LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review_local_precheck.md`。已实际调用；因本地模型地址返回 `Errno 1 Operation not permitted`，报告为 `Skipped / Local Model Unavailable`。这符合允许跳过规则，不替代独立评审或 PM 决策。
