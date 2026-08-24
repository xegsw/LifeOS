# LIFEOS-P3-037｜受控文件型 SQLite migration / 残留 P2 验证执行报告

## 1. 任务信息

- 任务 ID：LIFEOS-P3-037
- 任务类型：P0 工程验证任务 / 受控执行 / Evidence 生成；不适用 P3 Engineering Fast Lane
- 执行 Agent：Codex（专项工程执行会话，不是 PM 或独立评审会话）
- 主责角色：技术架构负责人 / 工程验证负责人
- 协审角色：数据 / 领域模型、AI 信任与安全、QA / Evidence Reviewer、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 执行日期：2026-08-13
- 任务状态：**Completed / Validation FAIL**；执行与证据生成完成，但候选 SQL 未达到 P3-036 的残留项目标合同

## 2. 执行摘要

1. **[事实]** 已在 `lifeos/engineering/LIFEOS-P3-037/` 建立固定无参数入口、候选 SQL 输入快照、只读合成 source fixture、可丢弃工作副本、backup / restore 与 evidence。没有连接真实用户 DB、Vault、真实文件路径或 Tauri / IPC。
2. **[事实]** P3-031 三个稳定源文件 hash 全部与既有 MANIFEST 匹配；SQL 快照 SHA-256 为 `55f3e15b...01c4b1`，与只读源一致。P3-031 文件没有修改。
3. **[事实]** 总计 10 项：7 PASS / 3 FAIL；P0 0 FAIL，P1 3 FAIL，P2 0 FAIL，Not Implemented 0，Unknown 0。验证入口依合同返回退出码 `1`。
4. **[事实]** P2-2 为 **FAIL / P1**：普通 DELETE、`INSERT OR REPLACE`、显式事务 DELETE+INSERT 均可提交；tombstone 可消失或从 generation 5 降到 4，六类合成消费门模拟由 DENY 变 ALLOW。rollback 可恢复原行，但不能补偿 commit 旁路。
5. **[事实]** P2-3 为 **FAIL / P1**：`active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 四种非 `accepted` 初始状态均可直接 INSERT。合法 `accepted` 起点、合法转换和非法 `accepted → cleaned` 拒绝仍正常。
6. **[事实]** P2-4 为 **FAIL / P1**：active Authorization 的 scope/action/policy 均可直接 DELETE；等价消费门在事务中、提交后、缓存及队列重检时均 DENY / AMBIGUOUS，未发生权限放宽，但父状态仍 active、generation 不变且无新增 audit，未达到推荐审计完整性合同。
7. **[判断]** 当前结果不能进入“通过结果的独立工程复评”或更高层真实 DB / Schema / API 输入；应先由 PM 判断候选 SQL 整改与风险状态复核路线。本会话不修改 SQL、不改账本、不启动整改或评审任务。

## 3. 授权边界与实际修改范围

实际新增仅限：

- `lifeos/engineering/LIFEOS-P3-037/input/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-037/work/` 下的合成 SQLite 源、攻击副本、backup 和 restore 副本
- `lifeos/engineering/LIFEOS-P3-037/evidence/` 下的 manifest、日志和结构化证据
- 本报告及本任务本地预检输出

没有修改 P3-031 候选 SQL、合同测试、runner 或 evidence；没有修改 P3-009、Stitch、生产代码、PM 账本、风险记录或冻结状态；没有执行非空旧版本 upgrade 或真实 SQL migration；没有启用云、第三方模型、向量、同步、多设备、L3 或外部用户。

## 4. 输入 hash 与环境

| 输入 | 期望 SHA-256 | 实际结果 |
|---|---|---|
| P3-031 `001_candidate_schema.sql` | `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` | 匹配 |
| P3-031 `run_contract_tests.py` | `defdd87e1ee355a978ddb75352c1a8aeca9e33960a2ad2922b8385e9740b295c` | 匹配 |
| P3-031 `run_validation.sh` | `61f9d6a17dfd4eb455ffd0e768c5289d0e9b5d578235130aa212d6e0896e2769` | 匹配 |
| P3-037 SQL 快照 | 与源 SQL 相同 | 匹配 |

运行环境：Python 3.9.6、SQLite 3.51.0、macOS 26.6.1 arm64；SQLite 编译选项完整记录于 `evidence/environment.json`。source fixture 使用 `journal_mode=delete`、`foreign_keys=1`、`user_version=1`，文件权限为 `0444`。本次只验证 bootstrap candidate version 1 生成的合成文件库，不验证旧版本升级。

## 5. 目录与路径隔离证明

入口不接受任何 CLI 路径参数，DB 访问统一经过任务根校验。实际反例覆盖并拒绝：`~`、文件系统根、项目根、宽泛 `work/` 目录、UNC 网络路径、scheme 网络路径、用户 DB-like 名称、Vault-like 名称，以及指向隔离目录外的 symlink；合法探针只解析到 P3-037 的 `work/`。

fixture 只包含 `synthetic-*` ID、固定合成 Project/Source 名与 `SYNTHETIC_PAYLOAD_NO_USER_CONTENT`，无真实正文、URL、密钥、Vault 路径或可反识别标识。环境 evidence 记录 22 次 DB 打开，路径全部位于 P3-037 隔离根。此处证明的是本脚本固定入口和本次访问清单，不外推为操作系统级沙箱或真实 Tauri capability 证明。

## 6. P2-2 验证结果

结论：**FAIL / P1**。

- 基线为 artifact generation 5、tombstone generation 5、`active_blocked`，六类模拟门均 DENY。
- 普通 DELETE 成功提交，tombstone 消失，read/search/suggest/outbox/export/restore 六类模拟门均 ALLOW。
- `INSERT OR REPLACE` 成功以 generation 4、`accepted` 替换原行；显式 DELETE+INSERT commit 同样成功，六门均 ALLOW。
- 同一攻击走 rollback 后，原 generation 5 / `active_blocked` 行完整恢复，六门恢复 DENY；说明 SQLite rollback 正常，但 commit 旁路实际成立。

依据：`evidence/checks/p2_2_tombstone_delete_insert.json`。按 P3-036 标准，旁路在文件型 DB 中可执行即归 P1，不能继续按“残留 P2”弱化。

## 7. P2-3 验证结果

结论：**FAIL / P1**。

- 直接 INSERT `active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 均成功且各留 1 行。
- 合法 `accepted` 起点成功；`accepted → active_blocked → cleanup_pending → cleaned` 成功。
- 非法 `accepted → cleaned` 被 `tombstone_status_transition_invalid` 拒绝。

这说明 UPDATE 转换矩阵有效，但没有覆盖初始 INSERT 声明；候选 SQL 可以直接伪造“已阻断 / 已清理 / 供应商受限”等状态。依据：`evidence/checks/p2_3_tombstone_status_insert.json`。

## 8. P2-4 验证结果

结论：**FAIL / P1**，同时保留“运行时 fail closed”事实。

- scope allow、read action、policy 三类子行均能直接 DELETE 并提交。
- 删除后父 Authorization 仍 `active`、generation 仍为 1、audit 行数仍为 1，没有受控降级、代际递增或追加审计。
- 在事务内查询和提交后查询均为 DENY / AMBIGUOUS；旧缓存中的 ALLOW 决定在重检后变为 DENY / AMBIGUOUS，队列重检相同。
- rollback 后子行与 baseline ALLOW 恢复。

因此最低消费安全合同在等价模拟中 fail closed，未观察到不完整授权放宽；但 P3-036 的推荐审计完整性合同明确要求 DB 拒绝，或父授权同事务降级/撤销、generation 递增并写 audit。当前三类均不满足，归 P1。依据：`evidence/checks/p2_4_authorization_child_delete.json`。

## 9. 统计与基础设施验证

| 严重级别 | PASS | FAIL | Not Implemented | Unknown |
|---|---:|---:|---:|---:|
| P0 | 2 | 0 | 0 | 0 |
| P1 | 5 | 3 | 0 | 0 |
| P2 | 0 | 0 | 0 | 0 |
| **Total** | **7** | **3** | **0** | **0** |

P0 两项为路径隔离和合成数据边界。P1 的五项通过为稳定 hash、只读 source、integrity/FK、backup/restore、rollback；三个失败即 P2-2/3/4。原问题编号虽为 P2，文件型 DB 已证明可利用后按 P3-036 升级为 P1。准确命令为：

```bash
lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh
```

本次退出码 `1`，符合“任一 P0/P1 FAIL、Unknown、Not Implemented 均非零”的合同。

## 10. backup / restore / rollback / integrity / FK

- source fixture before/after SHA-256 均为 `ed471d53...aea49`，未变化，权限 `0444`。
- before/after `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。
- SQLite backup API 生成 backup，并在独立 restore 副本恢复；11 张关键表行数、tombstone、六类消费门和 Authorization gate 均与 source 匹配；restore 后 integrity/FK 通过。
- P2-2 和 P2-4 rollback 均恢复基线关系及 gate 结果。

## 11. Evidence 入口

- Evidence manifest：`lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json`
- 摘要：`lifeos/engineering/LIFEOS-P3-037/evidence/summary.md`
- 日志：`lifeos/engineering/LIFEOS-P3-037/evidence/test_run.log`
- 环境：`lifeos/engineering/LIFEOS-P3-037/evidence/environment.json`
- 逐项反例、消费门、完整性/FK：`lifeos/engineering/LIFEOS-P3-037/evidence/checks/`
- backup/restore/rollback：`lifeos/engineering/LIFEOS-P3-037/evidence/migration/`

## 12. 角色、关卡、风险与 PM 待确认

- Gate 2：**Not Passed / Rework input**。Tombstone generation 与初始状态可被直接 SQL 旁路；Authorization 审计语义不完整。
- Gate 3：**Pass with Conditions（仅 P2-4 等价消费门）/ Overall Not Passed**。不完整 Authorization 在事务、commit、缓存和队列重检中 DENY，但 P2-2 模拟消费出现 ALLOW，且 P2-3 可伪造状态。
- Gate 4：**Not Passed / Rework input**。隔离、hash、恢复和证据可复跑，但 3 个 P1 使候选 SQL 不满足后续输入条件。
- R-0040 继续 Open / Conditional；本任务不提供关闭证据。
- R-0043 / R-0044 / R-0045 保持账本中的既有状态，本会话不重新打开或关闭。**[需 PM 决策]** P2-2/3 和 P2-4 已满足 P3-036 所列“残留项被证明可利用 / 审计 fencing 缺失”的条件，PM 应判断是否重评 R-0043 / R-0044 的状态、如何建立候选 SQL 整改任务，以及整改后的隔离独立评审安排；P2-4 运行时 fail-closed 不应被忽略。R-0045 本次未发现新旁路。

## 13. 后续独立评审建议与不可外推声明

**[建议]** 当前不建议把本结果送入“通过结果确认型”的独立工程评审，也不建议进入更高层真实 DB 验证。PM 应先验收本 evidence 和三个 P1，决定是否另立窄范围候选 SQL 整改；整改执行与本会话隔离后的成果，再由独立评审会话复核 P2-2/3/4、hash、路径、rollback 与 evidence。本会话不启动这些任务。

本报告仅描述当前 P3-031 SQL 快照在 macOS arm64 / SQLite 3.51.0、合成文件型 fixture、单进程隔离副本中的行为。不得外推为生产 migration、非空旧库 upgrade、真实用户 DB、真实 Vault / 文件、真实 Tauri / IPC、跨平台、并发进程、WAL/断电、生产 backup SLA 或法律删除能力通过；不得外推为 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线冻结；不得作为 R-0040 关闭、正式 MVP 准入或下一阶段准入。

本地预检：**Completed / 需要人工复核**，路径为 `lifeos/local_prechecks/LIFEOS-P3-037_LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation_local_precheck.md`。预检未发现 Frozen、Accepted、MVP 准入或“已实现”误写；其要求 PM 重点复核三个 P1、风险失效条件、SQL 整改与独立评审安排，与本报告第 12–13 节一致。预检仅用于覆盖与措辞检查，不作为本任务技术结论、PM Review 或独立评审依据。
