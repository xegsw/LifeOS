# LIFEOS-P3-038｜候选 SQL 残留 P1 整改与回归报告

## 1. 任务信息

- 任务 ID：LIFEOS-P3-038
- 任务类型：P0 工程整改 / 候选 SQL 补丁 / 回归验证 / Evidence 生成；不适用 P3 Engineering Fast Lane
- 执行 Agent：Codex（专项工程整改会话，不是 PM 或独立评审会话）
- 主责角色：技术架构负责人 / 工程整改负责人
- 协审角色：数据 / 领域模型、AI 信任与安全、QA / Evidence Reviewer、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 执行日期：2026-08-13
- 执行状态：**Completed / Remediation Regression PASS**；是否采纳与风险处置仍需 PM 及后续隔离独立复评

## 2. 执行摘要

1. **[事实]** 已在 P3-031 候选 SQL 增加 Tombstone 初始 INSERT、DELETE/重插及 active Authorization 子表 DELETE 的 DB trigger；没有用“正常代码不会这样写”替代 DB 约束。
2. **[事实]** P3-031 合成空库回归为 38 PASS / 0 FAIL / 0 Not Implemented：P0 18、P1 12、P2 8；新增 CT-P1-10/11/12 分别覆盖 P2-2/3/4，退出码 0。
3. **[事实]** P3-038 受控文件型回归为 12 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown：P0 2、P1 10，退出码 0。P2-2 三类攻击、P2-3 四类非法初态、P2-4 三类 active 子表 DELETE 全部被 SQLite trigger 拒绝。
4. **[事实]** source fixture 权限为 `0444`，before/after hash 相同；integrity、quick check、FK、backup/restore、rollback 全部通过。P3-037 五个 failure evidence 文件 hash 全部未变。
5. **[判断]** 三个 P1 在“当前候选 SQL + 合成空库 + 受控文件型 SQLite”边界内已形成整改通过证据，可以作为后续隔离独立工程复评输入；本结论不等于风险关闭、Schema/API 冻结或真实 migration 通过。

## 3. 授权边界与实际修改文件

实际修改：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`

P3-031 `scripts/run_validation.sh` 已按任务卡修正退出码透传：先保存 Python 状态，再输出日志并以原状态退出，避免 `tee` 掩盖失败。另新增 `lifeos/engineering/LIFEOS-P3-038/` 下的 SQL 快照、固定无参数 runner、合成工作库、backup/restore 与 evidence，以及本交付物和本地预检。

没有修改 P3-037 failure evidence、交付物或 PM Review；没有修改 P3-009、生产代码、Stitch 或 PM 账本；没有执行真实用户 DB migration、非空旧库 upgrade，也没有访问真实 Vault、真实用户文件、真实导出路径或真实敏感数据；没有启动 Tauri / IPC、云、第三方模型、向量、同步、多设备、L3 或外部用户。

## 4. P2-2 整改与回归

失败原因是原 SQL 只用 `tombstone_generation_monotonic` 阻止 UPDATE 降代，却允许 DELETE 后重插；`INSERT OR REPLACE` 也能绕过 UPDATE trigger。

整改采用两个 DB trigger：

- `tombstone_no_delete`：无条件拒绝 Tombstone 直接 DELETE，错误码 `tombstone_delete_forbidden`。
- `tombstone_insert_contract`：若同一 `(subject_type, subject_id)` 已存在，则在 INSERT 冲突处理前拒绝，错误码 `tombstone_reinsert_forbidden`，从而同时阻断 `INSERT OR REPLACE` 和 DELETE+INSERT 重建路径。

CT-P1-10 与文件回归证明：普通 DELETE、`INSERT OR REPLACE generation=4`、显式 DELETE+INSERT commit/rollback 攻击均被拒绝；原 generation 5 / `active_blocked` 行完整不变，read/search/suggest/outbox/export/restore 六类合成门持续 DENY。P2-2：**PASS**。

## 5. P2-3 整改与回归

失败原因是既有 `tombstone_status_transition` 只约束 UPDATE，未约束初始 INSERT。

`tombstone_insert_contract` 现在要求 `NEW.cleanup_status='accepted'`，否则以 `tombstone_must_start_accepted` 拒绝。原状态转换矩阵保留不变；进入 `active_blocked` 前的消费门证明仍属于应用事务 guard，SQL trigger 不伪装成该证明。

CT-P1-11 与文件回归证明：直接 INSERT `active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 全部拒绝且零残留；合法 `accepted → active_blocked → cleanup_pending → cleaned` 通过，非法 `accepted → cleaned` 仍拒绝。P2-3：**PASS**。

## 6. P2-4 整改与回归

失败原因是 Authorization 只在激活时检查 completeness，激活后 scope/action/policy 可以被删除，导致父状态与 generation 不变、audit 不追加。

本任务选择任务卡允许的“DB 直接拒绝”分支，新增：

- `authorization_scope_no_delete_while_active`
- `authorization_action_no_delete_while_active`
- `authorization_policy_no_delete_while_active`

三个 trigger 只在父 Authorization 为 `active` 时拒绝删除；父授权处于非 active 状态时，子行仍可清理，避免把所有维护路径永久锁死。

CT-P1-12 与文件回归证明：三类 active 子表 DELETE 均被对应错误码拒绝；父状态仍 active、generation 仍 1、子行数与 audit 行数不变，未创建不完整授权状态。缓存与队列重检保持 ALLOW，是因为攻击失败后完整授权本身完全未变；这不应误写为旁路。若未来允许受控修改，仍需先让父授权退出 active 并按正式合同处理 generation/audit/outbox。P2-4：**PASS**。

## 7. 两套回归结果

### P3-031 合成空库

命令：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 12 | 0 | 0 |
| P2 | 8 | 0 | 0 |
| **Total** | **38** | **0** | **0** |

退出码 0；旧有 35 项未回退，新增 CT-P1-10/11/12 通过。该 harness 没有 Unknown 状态分支，执行列表全部产生 PASS，无缺失用例。

### P3-038 受控文件型 SQLite

命令：`lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh`

| 严重级别 | PASS | FAIL | Not Implemented | Unknown |
|---|---:|---:|---:|---:|
| P0 | 2 | 0 | 0 | 0 |
| P1 | 10 | 0 | 0 | 0 |
| P2 | 0 | 0 | 0 | 0 |
| **Total** | **12** | **0** | **0** | **0** |

退出码 0。路径隔离、合成声明、稳定 hash、只读 source、integrity/FK、backup/restore、rollback、P3-037 证据保留、P3-031 快照以及三项攻击面全部通过。

## 8. 输入 / 输出 hash

| P3-031 稳定文件 | 整改前 | 整改后 |
|---|---|---|
| 候选 SQL | `55f3e15b...01c4b1` | `008cd328...c4cf2` |
| 合同测试 | `defdd87e...b295c` | `246f3675...39da` |
| runner | `61f9d6a1...e2769` | `611a2714...6230d` |

关键运行输出：P3-031 `test_results.json` 为 `e5a18677...ba25c`，`test_run.log` 为 `f3c88495...03a9b`；P3-038 `test_results.json` 为 `bdf6f992...f816d`。完整 64 位 hash 见两个 MANIFEST。

P3-037 原始 MANIFEST、test_results 及三个失败 JSON 的当前 hash 与整改前记录逐项相同；保留证明见 `lifeos/engineering/LIFEOS-P3-038/evidence/input/p3_037_failure_preservation.json`。

## 9. 文件型完整性、恢复与隔离

- source fixture before/after SHA-256 均为 `5723953c...de7deec`，权限 `0444`。
- before/after `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`、`foreign_keys=1`。
- backup 与独立 restore SHA-256 均为 `4d11324d...bb0ca8`；11 张关键表行数、Tombstone、消费门和 Authorization gate 匹配。
- runner 无路径参数，拒绝 `~`、根/项目/宽泛目录、网络路径、用户 DB/Vault-like 名称和越界 symlink；DB 访问日志全部位于 P3-038 隔离根。
- 以上仅证明本脚本固定入口与本次合成访问清单，不是操作系统级沙箱、真实 Tauri capability 或真实文件能力证明。

## 10. Evidence 入口

- P3-038 Evidence manifest：`lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
- P3-038 机器结果：`lifeos/engineering/LIFEOS-P3-038/evidence/test_results.json`
- P3-038 摘要 / 日志：`lifeos/engineering/LIFEOS-P3-038/evidence/summary.md`、`test_run.log`
- 三项回归：`lifeos/engineering/LIFEOS-P3-038/evidence/checks/`
- P3-031 Evidence manifest：`lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`

## 11. 角色、关卡、风险与待确认

- Gate 2：**执行自检 Pass with Conditions**。删除不复活、初始状态诚实性和授权子表完整性在当前候选层通过；仍待独立复评。
- Gate 3：**执行自检 Pass with Conditions**。三项 DB 旁路被拒绝；`active_blocked` 前全消费门证明仍属于应用 guard，未被本 SQL 扩权；仍待独立复评。
- Gate 4：**执行自检 Pass with Conditions**。两套回归、hash、恢复与非零退出合同通过；未验证非空旧库、真实 DB、跨平台或真实 IPC。
- R-0040 保持 Open / Conditional；R-0043 保持 Reopened；R-0046 保持 Open；R-0044 / R-0045 保持 Closed。本会话不改变任何风险状态。
- **[需 PM 决策]** 是否接受本整改为隔离独立工程复评输入；风险是否关闭必须等待独立复评和 PM/用户后续决策，本任务不得自行判断。

## 12. 后续独立评审建议与不可外推声明

**[建议]** 可进入与本执行会话隔离的独立工程复评，重点复核 trigger 的 SQLite 行为、REPLACE 前置触发、active/non-active Authorization DELETE 边界、两套结果、P3-037 证据保留和 hash。专项会话不启动该任务。

本整改只在当前候选 SQL、合成空库、macOS arm64 / SQLite 3.51.0 受控文件 fixture 和单进程范围内成立。不得外推为生产 migration、非空旧库 upgrade、真实用户 DB、真实 Vault/文件、真实 Tauri/IPC、跨平台、并发进程、WAL/断电、生产 backup SLA 或法律删除能力通过；不得外推为 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线冻结；不得作为 R-0040/R-0043/R-0046 关闭、正式 MVP 准入或下一阶段准入。

本地预检：**Completed / 适合进入 PM 验收**，路径为 `lifeos/local_prechecks/LIFEOS-P3-038_LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression_local_precheck.md`。预检认为任务卡覆盖完整、未发现越界或 Frozen/Accepted/MVP 准入误写，并要求 PM 重点复核独立复评输入与风险处置；预检只做覆盖和措辞检查，不作为技术结论、PM Review、独立评审或风险关闭依据。
