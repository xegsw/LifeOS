# LIFEOS-P3-044 Evidence Manifest

## 1. 授权范围与能力边界

- 任务：active Authorization 父记录 REPLACE/重建旁路 P1 整改与回归。
- 实际模型路由：`gpt-5.6-sol` + `xhigh`；首选配置可用，未触发后备模型或降级。
- 修改范围：P3-031 候选 SQL、合同测试及 evidence；新建 P3-044 runner、快照与 evidence。
- P3-040/P3-042 只在临时项目树中对当前 P3-031 SQL 复跑；P3-039 至 P3-043 原始交付物、评审、PM Review 和 evidence 均未修改。
- 仅使用合成空库、合成数据、内存 SQLite 和 `lifeos/engineering/LIFEOS-P3-044/work/` 文件库。
- 未连接/迁移真实 DB、Vault、用户文件、导出或 Tauri/IPC；未使用云/第三方模型、向量、同步、多设备、L3、外部用户或网络。
- 未修改 PM 账本，未关闭风险、冻结资产、恢复基线、进入下一阶段或创建/启动 P3-045。

## 2. 约束设计

| Trigger | 时机 | 条件 | 稳定错误 |
|---|---|---|---|
| `authorization_no_replace_while_active` | `BEFORE INSERT` | 已存在 active 行，且 `old.id=NEW.id` 或 `(old.logical_key,old.version_no)=(NEW.logical_key,NEW.version_no)` | `active_authorization_replace_forbidden` |
| `authorization_no_delete_while_active` | `BEFORE DELETE` | `OLD.status='active'` | `active_authorization_delete_forbidden` |

`BEFORE INSERT` 在 SQLite 执行 REPLACE conflict resolution 之前查询旧 active 行，因此不依赖隐式 DELETE trigger、FK 或 `recursive_triggers`。既有 direct-active INSERT trigger 排除上述 active 冲突，保证替换 active→active 也稳定返回 replacement 错误；无冲突 direct-active 仍返回 `authorization_must_start_inactive`。终态历史不可变保持 R-0049 非范围。

## 3. 环境、命令与退出合同

- 工作目录：`/Users/xxe/Documents/No.2`
- Python：3.9.6；SQLite：3.51.0；平台：macOS arm64。
- 主命令：`sh lifeos/engineering/LIFEOS-P3-044/scripts/run_validation.sh`
- 内含 P3-031：`sh lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- P3-040 current：临时树内 `python3 lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
- P3-042 current：临时树内 `python3 lifeos/engineering/LIFEOS-P3-042/scripts/run_validation.py`
- 退出码：P3-031=`0`；P3-040 current=`0`；P3-042 current=`0`；P3-044=`0`。
- 非零条件：任一回归非零、任一 P0/P1 非 PASS、任何 FAIL/NOT_IMPLEMENTED/UNKNOWN、文件库检查异常或 P3-043 preservation 失败。

## 4. 四组测试统计

| 测试集 | PASS | Known limitation | Observation | FAIL | Not Implemented | Unknown | 退出码 |
|---|---:|---:|---:|---:|---:|---:|---:|
| P3-031 current | 46 | 0 | 0 | 0 | 0 | 0 | 0 |
| P3-040 current | 128 | 0 | 0 | 0 | 0 | 0 | 0 |
| P3-042 current | 52 | 26 | 0 | 0 | 0 | 0 | 0 |
| P3-044 P1 | 160 | 0 | 0 | 0 | 0 | 0 | 0 |
| P3-044 P2 | 40 | 18 | 0 | 0 | 0 | 0 | 0 |
| P3-044 P3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |

P3-031 为 P0=18、P1=20、P2=8，46/46 PASS。P3-040 为 P1=126、P2=2，128/128 PASS。P3-042 仍为 52 PASS + 26 P2 Known Limitation，且 `p3_031_exit=0`、`p3_040_isolated_exit=0`。P3-044 共执行 220 个实例；110 个文件库的 integrity/quick/FK 检查全部通过。

## 5. 冲突键、写法、状态、PRAGMA、后端与事务矩阵

| 维度 | 覆盖 | 结果 |
|---|---|---|
| 冲突键 | 同 id；同 `(logical_key,version_no)` 不同 id；两者同时冲突；仅 id 冲突；无冲突 | active 冲突全部稳定拒绝；无冲突 proposed/granted 合法 |
| SQL 写法 | `INSERT OR REPLACE`、`REPLACE INTO`、UPSERT id/version DO UPDATE、DO NOTHING、普通重复 INSERT、DELETE、DELETE+INSERT | 目标 active 时全部 fail closed |
| 替换状态 | proposed、granted、active、revoked | 全部返回 replacement 错误 |
| 包络 | processor、purpose、location、policy_version、`expires_mode='at'` + `expires_at_ms` | 原 active 值完整保留 |
| 后端 | memory、task-local file | 全部通过 |
| FK | ON、OFF；runner 在 migration 后设置并读取回值确认 | 全部通过 |
| recursive | ON、OFF；runner读取回值确认 | 全部通过 |
| 事务 | autocommit、显式事务预期 commit、失败后 rollback | P3-043 P1 与 DELETE+INSERT 全组合通过 |

P3-043 的 `insert_or_replace_granted_fk_on` 在 2 后端 × 2 FK × 2 recursive × 3 transaction 共 24 个实例全部 PASS。显式事务中先写 fake audit 再 REPLACE 的 16 个实例全部回滚，证明父表、三类子表、generation、audit/outbox 无半状态。每个拒绝用例都对完整父行、三类子表和 evidence 快照做前后相等检查。

## 6. 合法路径与历史反例映射

- 新 granted/proposed 唯一记录、配置 scope/action/policy 后激活：各 8/8 PASS。
- active→superseded（generation+1 + audit/outbox）后同事务创建完整 v2 successor 并激活：8/8 PASS。
- active no-op 包络更新与仅 `updated_at_ms` 维护：8/8 PASS。
- P3-042 八字段/NULL/复合/多行及 P3-040 active 子表当前候选回归无回退。

P3-043 原始 1 个 P1 已转为当前 fail-closed。原 10 个 P2 均保留映射：`fk_off_replace_rebuild_then_activate` 与本次同根因且任务明确要求覆盖，当前 8/8 PASS；其余 terminal 父包络 2 个与 R-0048 7 个仍以 18 个双后端 `KNOWN_LIMITATION` 实例保留。原 1 个 granted 可变 P3 观察仍以 2 个双后端 `OBSERVATION` 保留。历史 34 PASS/12 BYPASS evidence 本身未被改写。

## 7. 输入与输出 SHA-256

### 稳定实现输入

| 文件 | 修改前 | 修改后 |
|---|---|---|
| P3-031 candidate SQL | `ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b` | `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376` |
| P3-031 contract tests | `e934dff9b9502d5e5c4f46c96a1471e9d581e08a7fe448e8a6754e86b7ecd275` | `58a4cb9781c88dc899e647ff9f95b851aba67c863dc1ddd48c6d8c7e20760ba9` |
| P3-031 shell | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | unchanged |
| P3-044 runner | N/A | `1e297a9eaf031776b33ee978656e9aa62e477d1b05875a6c1aa9627b532774c3` |
| P3-044 shell | N/A | `5a1cb65ea030b1fd13d7be19e7cb2774cf36ceee0752587728abc07b60647dd0` |
| P3-044 SQL snapshot | N/A | `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376` |

### 生成 evidence

| 文件 | SHA-256 |
|---|---|
| `evidence/test_results.json` | `857c86c8212a09f35f5fdd129acda82ca4b532269158c0c4b5c9e08a8dbe439f` |
| `evidence/test_run.log` | `b0e4f76ce3af1cd447e1dfac53823fb73894f6959dd14f1afe8bdf949adc6848` |
| `evidence/environment.json` | `4e851b2cb375b6049fdcda2dc301207b43f9eb6926ded83d5c1f4ddc4eca2e45` |
| `evidence/checks/integrity_and_fk.json` | `46c7cb980ee3e47e7594726ef0196d45cadcdb50231a1461d814394da954fdb5` |
| `evidence/input/source_hashes.json` | `cbaf6545c616892b14798255c3b818b382e566b2ae7c88d1a16ecd53ca2b5138` |
| `evidence/input/p3_043_preservation.json` | `5a57b71e4d182beb2671ad141822fddea998b74d9be95f90bf4f8212e32ccaa0` |
| `evidence/regressions/p3_031_test_results.json` | `ba798af5c679f162949e65e25d2603252dce89f39ae46152f64a8bef343b482b` |
| `evidence/regressions/p3_031_test_run.log` | `0c866c40157ac11d958ee33723db9a20a815202dcbe4584456db9e4f89fa13d0` |
| `evidence/regressions/p3_040_test_results.json` | `23f3700d020f80e9a88e4c8242efea5a4b6c5b23efb31547f25a1e3c7a5298aa` |
| `evidence/regressions/p3_040_test_run.log` | `2043fbf2a2da27595514e960e547a94658f2d2e4df0a81029f6475fdce08a400` |
| `evidence/regressions/p3_042_test_results.json` | `2e60c22289971d96662e2777497abe33439531c4458fff5cd3dc6ce8835d70f6` |
| `evidence/regressions/p3_042_test_run.log` | `27e267a441a244ecc7908fafa7bfe165333e9d9994d1bc2d995e4d58ef298acd` |

隔离 source_hashes 明确记录 current candidate=`0b7f...d376`，避免把旧 snapshot 回归冒充当前候选回归。

## 8. P3-043 保留证明

P3-043 PM Review、独立评审、manifest、candidate snapshot、攻击脚本、JSON/TXT 结果共 7 个文件执行前后 hash 一致；详见 `evidence/input/p3_043_preservation.json`。关键原始 hash：PM Review=`1d35...bd39`，independent review=`4018...fc61`，attack script=`400c...e40a`，results JSON=`a5d2...6d7b`。P3-040/P3-042 原目录也未作为输出目标，所有当前候选复跑均在临时树完成。

## 9. 非范围与不可外推

- R-0048 的 audit/outbox 预置/修改/删除、generation 独立升高、active created/revoked 元数据可变未修复。
- R-0049 的 terminal 父表/子表历史不可变及受控清理未修复。
- 本结果不关闭 R-0040/R-0043/R-0044/R-0046/R-0047/R-0048/R-0049/R-0050，不改变 R-0045。
- 合成 SQLite 结果不可外推到真实非空旧库 upgrade、真实用户数据/Vault/文件/导出/Tauri/IPC、并发进程、WAL/断电、跨平台、性能或生产 SLA。
- 本 evidence 仅供 PM 验收及决定是否另行创建 P3-045 隔离复评；不构成 Accepted、风险关闭、Schema/API/SQL migration/工程基线冻结或阶段准入。

## 10. 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`
- 脚本退出码：0；报告正常落盘。
- 报告：`lifeos/local_prechecks/LIFEOS-P3-044_LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression_local_precheck.md`
- 状态：`Skipped / Local Model Unavailable`；局域网本地模型连接超时，按项目规则允许跳过，不替代 PM/独立复评。
