# LIFEOS-P3-040 Evidence Manifest

## 1. 授权、隔离与结论边界

- 任务：`LIFEOS-P3-040`，仅整改 P3-039 指出的 active Authorization 子表变异旁路及其状态翻转逃逸。
- 修改范围：P3-031 候选 SQL、合同测试与 evidence；新增 P3-040 隔离回归包及本任务交付物。
- 数据：只使用内存 SQLite 与 `lifeos/engineering/LIFEOS-P3-040/work/` 下 64 个可丢弃合成文件库。
- 未连接真实 DB、真实 Vault、真实用户文件、真实 Tauri / IPC；未使用网络、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 本 evidence 不冻结 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线；不关闭 R-0040、R-0043、R-0044、R-0046，不改变 R-0045。

## 2. 文件清单

- `input/001_candidate_schema.sql`：本次实际执行的候选 SQL 快照。
- `scripts/run_validation.py`：29 个 P3-039 等价攻击及状态翻转、双向改绑、合法路径的双模式 runner。
- `scripts/run_validation.sh`：固定无参数入口，保留 Python 非零退出码。
- `evidence/test_results.json`：128 项机器可读结果。
- `evidence/test_run.log`：完整运行日志。
- `evidence/environment.json`：环境、能力关闭声明与 DB 访问清单。
- `evidence/checks/integrity_and_fk.json`：64 个文件库 integrity / quick / FK 结果。
- `evidence/input/source_hashes.json`：候选源、快照与 runner hash。
- `evidence/input/p3_039_evidence_preservation.json`：P3-039 原始 evidence 保留证明。
- `work/*.db`：固定任务目录内的合成文件库。

## 3. 稳定输入与修改前后 hash

| 文件 | P3-040 前 SHA-256 | P3-040 后 SHA-256 |
|---|---|---|
| P3-031 `migrations/001_candidate_schema.sql` | `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` | `50d25371865b6a153267042c68290bbb00baca12a9b43d2821bd8c3a2a93cf7c` |
| P3-031 `tests/run_contract_tests.py` | `246f3675b69207cf574f0aa9da919adb5b3b435996160dfe658e77f61f9339da` | `074e93884ec77946021ede4e13a0f1d56614d63012b59b698eed3a3d5274072e` |
| P3-031 `scripts/run_validation.sh` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |

P3-040 快照 hash 与 P3-031 当前候选 SQL 均为 `50d25371865b6a153267042c68290bbb00baca12a9b43d2821bd8c3a2a93cf7c`。

## 4. 准确命令、环境与退出合同

- 工作目录：项目根 `/Users/xxe/Documents/No.2`
- P3-031：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`；退出码 `0`。
- P3-040：`lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.sh`；退出码 `0`。
- Python：`3.9.6`；SQLite：`3.51.0`；OS：`macOS-26.6.2-arm64-arm-64bit`。
- P3-031：任一 FAIL 非零。
- P3-040：任一 P0/P1 FAIL、Not Implemented、Unknown、文件库完整性/FK 失败或 P3-039 hash 变化均非零。

## 5. 测试统计

### P3-031 合成空库

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 16 | 0 | 0 |
| P2 | 8 | 0 | 0 |
| **Total** | **42** | **0** | **0** |

### P3-040 内存 + 文件型 SQLite

| 严重级别 | PASS | FAIL | Not Implemented | Unknown |
|---|---:|---:|---:|---:|
| P0 | 0 | 0 | 0 | 0 |
| P1 | 126 | 0 | 0 | 0 |
| P2 | 2 | 0 | 0 | 0 |
| **Total** | **128** | **0** | **0** | **0** |

- 每种模式 64 项：memory 64 PASS；file 64 PASS。
- P3-039 等价 29 项每种模式均通过：P2-2 6、P2-3 8、P2-4 4、ADJ 11。
- 扩展每种模式 35 项：active child 5、policy 遗漏字段 7、OLD/NEW 双向改绑 9、状态/generation/audit/outbox/version 10、合法终态清理/新版本 4。
- 64 个文件库 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

## 6. 11 个 P1 与新增测试路径

P3-039 的 11 个 P1 保留原名称在 `test_results.json` 的 `ADJ` 分组：新增 scope/action、scope effect/target、scope rebind、policy training/sensitivity/external send、action value、scope/policy REPLACE。它们现在均由 BEFORE INSERT/UPDATE trigger 在 DB 层拒绝。

新增分组：

- `EXT-CHILD` / `EXT-POLICY`：deny scope、source/artifact target、action REPLACE、policy direct INSERT 及 retention/recipients/regions/disclosure/license/quantity/frequency。
- `EXT-REBIND`：scope/action/policy 的 active→inactive、inactive→active、active→active，trigger 同时检查 OLD 与 NEW 父状态。
- `EXT-STATE`：active→proposed/granted、缺 generation/audit/outbox 的退出、revoked/expired/superseded 修改后复活、version identity 原地改写、无 supersedes 的新版本。
- `EXT-LEGAL`：revoked/expired/superseded 子表清理及合法 supersede→新 version complete→active。

## 7. 运行输出 hash

| 文件 | SHA-256 |
|---|---|
| P3-031 `evidence/test_results.json` | `dcd6e50d7cd47b83583930646454c08d0d64ff992b9b1cb9327ac6d5574f266b` |
| P3-031 `evidence/test_run.log` | `afcd1872838b91186d0005840e3288c6cec89e6e55c30f6fc76b460d5d324b57` |
| P3-040 `scripts/run_validation.py` | `b8ee1db6c65ff098a11e9501948848eaa8773846fd4ad75b28ed5e102b764d78` |
| P3-040 `scripts/run_validation.sh` | `5a1cb65ea030b1fd13d7be19e7cb2774cf36ceee0752587728abc07b60647dd0` |
| P3-040 `evidence/test_results.json` | `23f3700d020f80e9a88e4c8242efea5a4b6c5b23efb31547f25a1e3c7a5298aa` |
| P3-040 `evidence/test_run.log` | `2043fbf2a2da27595514e960e547a94658f2d2e4df0a81029f6475fdce08a400` |
| P3-040 `evidence/environment.json` | `e2ef8fd513664224d8f3618b9836ae1fa571b6c4a9db4ce85b19b4d8178b10b1` |
| P3-040 `evidence/checks/integrity_and_fk.json` | `2e8616e3be94ef29d4ca797935fe8f8b349527963c7710c3854a51df52c83f9f` |
| P3-040 `evidence/input/source_hashes.json` | `7d0675ed92c30da3d1ffbe8c11909f6e78a267f14ddc046a98dbb511879abfb8` |
| P3-040 `evidence/input/p3_039_evidence_preservation.json` | `cc6c7b6f721e04d9b81c0026e5fa046cba40410f90a88c0e1da555ed4a0fc676` |

## 8. P3-039 原始 evidence 保留

P3-039 的 MANIFEST、反例脚本、JSON、日志与旧候选 SQL 快照的当前 hash 均与 P3-040 启动时记录一致；逐项 64 位 hash 见 `evidence/input/p3_039_evidence_preservation.json`。本任务未修改 P3-037、P3-038 或 P3-039 原始交付物、评审、PM Review 或 evidence。

## 9. 风险与不可外推声明

本结果只证明候选 SQL 在合成空库、单进程、内存及任务专属文件型 SQLite 中的行为。audit/outbox 前置顺序是候选 DB 合同，不是生产事务 API 或真实并发/崩溃恢复证明。未验证非空旧库 upgrade、真实用户 DB/Vault/文件、真实 Tauri/IPC、跨平台、并发进程、WAL/断电、生产 backup SLA。是否采纳、是否进入隔离独立复评及任何风险状态变化均由 PM 决定。
