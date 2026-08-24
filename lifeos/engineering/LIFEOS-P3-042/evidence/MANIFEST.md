# LIFEOS-P3-042 Evidence Manifest

## 1. 授权范围与执行边界

- 任务：active Authorization 父表安全包络不可变 P1 整改与回归。
- 实际模型路由：`gpt-5.6-sol` + `xhigh`；首选路由可用，未触发后备模型或降级。
- 修改范围：P3-031 候选 SQL、合同测试及其 evidence；新建 P3-042 runner、快照与 evidence。
- P3-040 仅在一次性临时项目树中隔离复跑；P3-039/P3-040/P3-041 原始文件未修改。
- 仅使用合成空库、代码内合成数据、内存 SQLite 和 `lifeos/engineering/LIFEOS-P3-042/work/` 下任务文件库。
- 未连接真实 DB/Vault/用户文件/Tauri/IPC；未执行真实 migration；未使用网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 未修改 PM 账本、未冻结资产、未关闭任何风险、未启动 P3-043。

## 2. 环境与准确复跑命令

- 工作目录：`/Users/xxe/Documents/No.2`
- Python：3.9.6
- SQLite：3.51.0
- 平台：macOS arm64
- 主命令：`sh lifeos/engineering/LIFEOS-P3-042/scripts/run_validation.sh`
- 内含 P3-031 命令：`sh lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- 内含 P3-040 隔离命令：临时树内 `python3 lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
- 三套退出码：P3-031=`0`；P3-040 isolated=`0`；P3-042=`0`。
- P3-042 非零退出合同：P3-031/P3-040 非零、任一 P0/P1 非 PASS、任一 FAIL/NOT_IMPLEMENTED/UNKNOWN、文件库 integrity/FK 异常、P3-041 hash 不一致，均返回非零。`KNOWN_LIMITATION` 只允许用于明确的 P2 非范围复现。

## 3. 测试统计

| 测试集 | 执行实例 | PASS | FAIL | Known limitation | Not Implemented | Unknown | 退出码 |
|---|---:|---:|---:|---:|---:|---:|---:|
| P3-031 全量 | 44 | 44 | 0 | 0 | 0 | 0 | 0 |
| P3-040 当前完整集合（隔离复跑） | 128 | 128 | 0 | 0 | 0 | 0 | 0 |
| P3-042 P1 | 26 | 26 | 0 | 0 | 0 | 0 | 0 |
| P3-042 P2 合法/既有保护 | 26 | 26 | 0 | 0 | 0 | 0 | 0 |
| P3-042 P2 非范围观察 | 26 | 0 | 0 | 26 | 0 | 0 | 0 |

P3-042 每个逻辑用例均在 memory/file 两种后端执行。39 个文件库实例的 `integrity_check`、`quick_check`、`foreign_key_check` 全部通过。这里的 P0/P1/P2 是测试严重级别；缺陷统计为新增 P0=`0`、新增 P1=`0`、FAIL=`0`、Not Implemented=`0`、Unknown=`0`。

## 4. 八字段整改与测试映射

统一 DB trigger：`authorization_security_envelope_immutable_while_active`；统一错误：`active_authorization_security_envelope_immutable`；条件使用 `OLD.status = 'active'` 与逐字段 `NEW.field IS NOT OLD.field`。

| 字段 | 单字段/配对测试 | 补充覆盖 | 结果（memory/file） |
|---|---|---|---|
| `grantor_ref` | `update_grantor_active` | 复合、多行 | PASS/PASS |
| `processor` | `update_processor_active` | compound、退休复合、多行 | PASS/PASS |
| `purpose` | `update_purpose_active` | compound | PASS/PASS |
| `location` | `update_location_active` | 单字段 | PASS/PASS |
| `valid_from_ms` | `update_valid_from_active` | 历史 P3-041 P2 定向纳入本任务 | PASS/PASS |
| `expires_mode` | `update_expiry_to_indefinite_active`、`expires_indefinite_to_at_active` | at↔indefinite 配对 | PASS/PASS |
| `expires_at_ms` | `update_expires_at_active`、`expires_null_to_value_active` | 时间单改、NULL→值、值→NULL | PASS/PASS |
| `policy_version` | `update_policy_version_active` | 单字段 | PASS/PASS |

P3-041 七个 P1 原名 `update_processor_active`、`update_purpose_active`、`update_location_active`、`update_grantor_active`、`update_expiry_to_indefinite_active`、`update_policy_version_active`、`compound_field_update_active` 均为 PASS/PASS，共 14/14 实例。

## 5. 文件清单与 SHA-256

### 5.1 稳定输入与实现

| 文件 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | `ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b` |
| `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py` | `e934dff9b9502d5e5c4f46c96a1471e9d581e08a7fe448e8a6754e86b7ecd275` |
| `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |
| `scripts/run_validation.py` | `f76d78ccb9b724675070198966fe048f62356af5a68cbe4f8ad927aaa0628c42` |
| `scripts/run_validation.sh` | `5a1cb65ea030b1fd13d7be19e7cb2774cf36ceee0752587728abc07b60647dd0` |
| `input/001_candidate_schema.sql` | `ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b` |

修改前稳定 hash：候选 SQL=`50d25371865b6a153267042c68290bbb00baca12a9b43d2821bd8c3a2a93cf7c`；P3-031 tests=`074e93884ec77946021ede4e13a0f1d56614d63012b59b698eed3a3d5274072e`。P3-040 runner/shell 修改前后分别保持 `b8ee1db6c65ff098a11e9501948848eaa8773846fd4ad75b28ed5e102b764d78` / `5a1cb65ea030b1fd13d7be19e7cb2774cf36ceee0752587728abc07b60647dd0`。

### 5.2 生成证据

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `evidence/test_results.json` | P3-042 结构化结果 | `2e60c22289971d96662e2777497abe33439531c4458fff5cd3dc6ce8835d70f6` |
| `evidence/test_run.log` | P3-042 完整日志 | `27e267a441a244ecc7908fafa7bfe165333e9d9994d1bc2d995e4d58ef298acd` |
| `evidence/environment.json` | 环境/能力边界 | `72749591e5c4298219066ae67fe073462d92215451acc6d107d0202598e03a22` |
| `evidence/checks/integrity_and_fk.json` | 文件库健康检查 | `f878353211f157d3dd561422c9643816b7d388b79c0c467b9fc72119eaad4153` |
| `evidence/input/source_hashes.json` | 稳定源 hash | `89a11ecca3d968a36a71b4322c8322e0172b507b934e47d60fe62434f1fc7982` |
| `evidence/input/p3_041_evidence_preservation.json` | P3-041 保留证明 | `9018c22db8ee339a2446390ef9d4bdc0882a1dccfb7c5647bcafde837524dd5b` |
| `evidence/regressions/p3_031_test_results.json` | P3-031 快照 | `89c9c65ee5f367d59a214700e86b14852dde8ae58cd25f3f5998bdd2b32e3e9e` |
| `evidence/regressions/p3_031_test_run.log` | P3-031 日志 | `bebfcb21601af1549bf539d80ac950eb9b9f869c5812a3ae2a247b7f94d8da9c` |
| `evidence/regressions/p3_040_test_results.json` | P3-040 隔离结果 | `23f3700d020f80e9a88e4c8242efea5a4b6c5b23efb31547f25a1e3c7a5298aa` |
| `evidence/regressions/p3_040_test_run.log` | P3-040 隔离日志 | `2043fbf2a2da27595514e960e547a94658f2d2e4df0a81029f6475fdce08a400` |

同目录另含 P3-040 隔离复跑的 environment、integrity、source hash 与 P3-039 preservation JSON；它们均列在本 manifest 所在 evidence 目录中，可直接复核。

## 6. P3-041 原始 evidence 保留证明

P3-041 的 `MANIFEST.md`、反例脚本、JSON/TXT 结果、候选 SQL 快照共 5 个文件在执行前后 hash 完全一致；明细见 `evidence/input/p3_041_evidence_preservation.json`。原始 19 个 bypass（P1=7、P2=12）的历史证据未被覆盖或改写。

P3-041 历史 P2 中 `update_valid_from_active` 被本任务明确要求纳入八字段保护，当前已作为 P3-042 P1 回归 PASS；剩余 11 个 R-0048/R-0049 行为继续复现。另记录 `created_at_ms`、`revoked_at_ms` 两个相邻字段可变观察，未纳入本 trigger，等待 PM 分类。不得将“历史 12 条记录仍保留”误写为“12 条当前仍可复现且全部属于 R-0048/R-0049”。

## 7. 非范围与不可外推

- R-0048：audit/outbox 预置、UPDATE、DELETE 与 generation 独立升高未修复；7 个逻辑用例、14 个双后端实例标记 `KNOWN_LIMITATION`。
- R-0049：terminal 子表 INSERT/UPDATE 未修复；4 个逻辑用例、8 个双后端实例标记 `KNOWN_LIMITATION`。
- 相邻观察：active 时 `created_at_ms`、`revoked_at_ms` 仍可改，2 个逻辑用例、4 个双后端实例保留为 P2 `KNOWN_LIMITATION`，不在本任务擅自扩展生命周期合同。
- 合成空库/合成数据结果不能外推到真实非空旧库升级、真实用户数据、Vault、文件、Tauri/IPC、性能、并发、跨平台或生产 SLA。
- 本 evidence 仅支持 PM 判断是否送交 P3-043；不构成 Accepted、风险关闭、Schema/API/SQL migration/工程基线冻结或真实能力准入。

## 8. 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
- 退出码：0（预检脚本正常落盘）。
- 报告：`lifeos/local_prechecks/LIFEOS-P3-042_LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression_local_precheck.md`
- 状态：`Skipped / Local Model Unavailable`；局域网本地模型连接超时，依项目规则允许跳过，不能替代 PM 复核。
