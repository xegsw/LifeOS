# LIFEOS-P3-057 Evidence Manifest

## 1. 授权范围与独立性

- 任务：`LIFEOS-P3-057` Active Authorization 整改全新隔离独立复评。
- 执行会话：任务卡指定的新隔离 Codex 会话 `01a0225d-59d4-7071-8509-823c20dbe27e`，`gpt-5.6-terra` + `xhigh`。
- 封存顺序：先创建 `00_attack_plan_and_independence.md`，再读取 P3-044 攻击资产。该文件的预注册计划和本 manifest 的 runner 证明本评审不 import、调用或复制 P3-044 的攻击函数 / 场景表。
- 工程、历史 Review、历史 Evidence 与项目账本均只读；本任务只写入本目录、P3-057 review/deliverable 和本地预检报告。
- 仅使用合成 memory/file SQLite、系统临时目录和本地脚本；未使用真实数据库、真实用户数据、Vault、文件导出、Tauri/IPC、网络、云/第三方模型、同步、多设备、L3 或外部用户。

## 2. 输入 before / after SHA-256

| 输入 | Before | After | 判定 |
|---|---|---|---|
| 当前 P3-031 candidate SQL | `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` | `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` | 未改变 |
| 当前 P3-031 contract runner | `45d19e56fc3aaf75ccd12c5de678dec770c425fec9e8d570e3783f4a7bb8224a` | `45d19e56fc3aaf75ccd12c5de678dec770c425fec9e8d570e3783f4a7bb8224a` | 只读 |
| P3-044 SQL 历史 snapshot | `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376` | `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376` | 与 P3-044 Manifest 一致 |

当前候选 hash 与 P3-044 snapshot 不同，是后续已登记工程整改的当前输入演进；P3-057 所运行的当前 SQL hash 同 R-0048 已记录的有限受控边界 hash。它不是 P3-044 Evidence 的 hash 冲突，也不改变 R-0048 状态。

## 3. 历史 evidence 保留复核

| 资产组 | 已核验项 | 结果 |
|---|---|---|
| P3-043 原始失败 evidence | candidate snapshot、攻击脚本、JSON 结果、文本结果 | 4/4 与 `reviews/LIFEOS-P3-043/evidence/MANIFEST.md` 匹配 |
| P3-044 整改 evidence | SQL snapshot、runner、结果、日志、环境、integrity/FK、source hashes、P3-043 preservation | 8/8 与 `engineering/LIFEOS-P3-044/evidence/MANIFEST.md` 匹配 |
| P3-044 PM Review | 当前观测 SHA-256 `18e7d0966c0c5f9c87fb74560b644033cfd398d01872487d21f258ae0ed82787` | 只读记录；P3-044 manifest 未提供该文件的历史期望 hash，未将其伪称为历史 hash 保留证明 |

历史 hash 的逐项 expected / actual 比较在 `fresh_independent_results.json` 的 `hash_checks.historical_assets` 中保留。

## 4. 测试命令、环境与退出合同

| 测试 | 隔离方式 | 退出码 | 结果 |
|---|---|---:|---|
| P3-057 新 runner | 每案例新建系统临时 SQLite；memory/file × FK ON/OFF × recursive trigger ON/OFF | 0 | P1 312 PASS、P2 2 PASS、0 FAIL |
| P3-031 合同入口 | 将 P3-031 目录复制到 `mktemp` 临时树后运行复制品 | 0 | P0 18、P1 29、P2 27，74/74 PASS |

环境：Python `3.9.6`，SQLite `3.51.0`，macOS 本地合成执行。任何 P0/P1、明确合同 P2、Not Implemented、Unknown、hash 冲突或独立性不足都应使此独立评审为 Rework 或 Blocked；本次均未发生。

独立矩阵覆盖：id / version 唯一键冲突、REPLACE、UPSERT、DELETE+INSERT、父八字段与子表变异 / 改绑、八 PRAGMA 配置、事务 rollback、保存点、multi-row UPDATE/INSERT…SELECT、合法 proposed/granted/active、terminal/successor 路径。文件库案例均通过 `integrity_check`、`quick_check` 与 `foreign_key_check`。

## 5. P0/P1/P2 与未实现统计

| 范围 | P0 | P1 | P2 | Not Implemented | Unknown |
|---|---:|---:|---:|---:|---:|
| P3-057 新发现 | 0 | 0 | 0 | 0 | 0 |
| P3-057 runner PASS | 0 | 312 | 2 | 0 | 0 |
| 隔离 P3-031 合同 PASS | 18 | 29 | 27 | 0 | 0 |

P3-057 的两个 P2 PASS 是历史 evidence 保留和当前 R-0048 边界 hash 的只读核验，不是新的 P2 风险结论。

## 6. P3-057 输出 SHA-256

| 文件 | SHA-256 |
|---|---|
| `00_attack_plan_and_independence.md` | `dd19e8dfe43892405f736ed74de3a18e192c989dd51b133edb7dedb10e21128d` |
| `fresh_independent_runner.py` | `8089e5c1f7d3c8f50a2abbe08fe9f8bc5139a94bc924bdbdcfc6387421a1c604` |
| `fresh_independent_results.json` | `74a7e05ccfceac06e55a78c701439485df617ba063dd2bbeff6c0cf4134f9e44` |
| `p3_031_contract_isolated_results.json` | `a71bf9c9b1127af2e02f1ef356bd978f9e83c38a76bb74d71eb00831d5b8a3a2` |
| `execution_log.md` | `c5b9a2129bb4d5d7122665b363c689b85eafe3120a58b6003ed5ca7c070fe494` |
| `../independent_review.md` | `d9f0280ea0c6e75fc5c6f8842d88f9afe38ee89fd07b0ae4c3daebb26b71c76b` |
| `../../../deliverables/LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review.md` | `0a5527e995233bcdb540f8db318d0ebfc179ca7db206acc580cb547e95827b13` |

## 7. 非范围与不可外推

- 不关闭、调整或重新打开 R-0044、R-0046、R-0047、R-0050；不触及 R-0048/R-0049 的状态、重开条件或冻结含义。
- 不冻结 SQL/Schema/API/工程基线，不恢复工程基线，不启用真实能力，不进入下一阶段。
- 结果不能外推到真实 DB 或非空 migration、并发/WAL、崩溃恢复、真实 actor/确认、Vault、Tauri/IPC、导出、云/同步、性能或生产 SLA。

## 8. Local Precheck / 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review.md`
- 报告：`lifeos/local_prechecks/LIFEOS-P3-057_LIFEOS-P3-057_active_authorization_remediation_fresh_isolated_independent_re_review_local_precheck.md`
- SHA-256：`420afc2380bdb0dc46ddfaa0021c21f78402be653914a576aeda08ce73647a3a`
- 结果：`Skipped / Local Model Unavailable`；本地模型调用返回 `Errno 1 Operation not permitted`。符合项目允许跳过规则，未用于形成 Pass 或 PM 决策。
