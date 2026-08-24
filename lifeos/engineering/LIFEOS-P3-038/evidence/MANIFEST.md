# LIFEOS-P3-038 Evidence Manifest

## 授权与隔离范围

- 任务：`LIFEOS-P3-038`，仅受控文件型 SQLite + 合成 fixture 验证。
- 唯一新增回归包根：`lifeos/engineering/LIFEOS-P3-038/`；另按任务卡修改 P3-031 候选 SQL、合同测试与其 evidence。
- 固定无参数入口拒绝 `~`、宽泛目录、UNC / scheme 网络路径、用户 DB / Vault-like 名称、隔离目录外路径与 symlink。
- 未连接或修改真实用户 DB、真实 Vault、真实文件；未启动 Tauri / IPC；未启用网络、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- P3-031 候选 SQL与合同测试已按 P2-2 / P2-3 / P2-4 窄范围整改；P3-037 failure evidence 只读核对且保持不变。

## 创建 / 修改文件

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`：三项 DB trigger 整改。
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`：CT-P1-10 至 CT-P1-12 与必要旧夹具调整。
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`、`test_results.json`、`test_run.log`：最新 38 项合成空库回归证据。
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`：保留 Python 测试非零退出码，避免 `tee` 掩盖失败。
- `input/001_candidate_schema.sql`：P3-031 候选 SQL 输入快照。
- `scripts/run_validation.py`、`scripts/run_validation.sh`：固定路径验证入口。
- `work/`：合成只读源 fixture、可丢弃攻击副本、backup 与 restore 文件。
- `evidence/`：环境、hash、逐项结果、日志与本 manifest。

## 稳定输入 hash

### 整改前

| P3-031 稳定源文件 | 整改前 SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` |
| `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py` | `defdd87e1ee355a978ddb75352c1a8aeca9e33960a2ad2922b8385e9740b295c` |
| `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` | `61f9d6a17dfd4eb455ffd0e768c5289d0e9b5d578235130aa212d6e0896e2769` |

### 整改后

| 稳定源文件 | 期望 SHA-256 | 实际 SHA-256 | 匹配 |
|---|---|---|---|
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` | `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` | Yes |
| `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py` | `246f3675b69207cf574f0aa9da919adb5b3b435996160dfe658e77f61f9339da` | `246f3675b69207cf574f0aa9da919adb5b3b435996160dfe658e77f61f9339da` | Yes |
| `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | Yes |

- 输入快照：`lifeos/engineering/LIFEOS-P3-038/input/001_candidate_schema.sql` / `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` / 与 P3-031 原始 SQL 匹配：`True`。
- 稳定输入 hash 与下方运行输出 hash 分开记录。

## P3-037 failure evidence 保留

| P3-037 文件 | 既有 SHA-256 | 当前 SHA-256 | 未变 |
|---|---|---|---|
| `lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md` | `8aa519c023e846f88de7a3d0d0b48e8bb9372f50251db7be8c9b38dd3a2072e3` | `8aa519c023e846f88de7a3d0d0b48e8bb9372f50251db7be8c9b38dd3a2072e3` | Yes |
| `lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json` | `253a3ff4ba33137e90ef3ead0f8cdbeddeb1a507e927fa1f97c8a90b0ee4e354` | `253a3ff4ba33137e90ef3ead0f8cdbeddeb1a507e927fa1f97c8a90b0ee4e354` | Yes |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json` | `374c0304e6557c4a9561609820ce741a49108d4731a98fad3a3ceb4dbd0ff603` | `374c0304e6557c4a9561609820ce741a49108d4731a98fad3a3ceb4dbd0ff603` | Yes |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json` | `cf3d3b8da7d8a837010e2fc883102a516e6018bad7454431933867aeae80df34` | `cf3d3b8da7d8a837010e2fc883102a516e6018bad7454431933867aeae80df34` | Yes |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json` | `68d3e1a16bb9493e552f5ea0ec3918fe5576be6e26943cacb7fd2ff33f4d8dda` | `68d3e1a16bb9493e552f5ea0ec3918fe5576be6e26943cacb7fd2ff33f4d8dda` | Yes |

## 环境

- Python：`3.9.6`（CPython）
- SQLite：`3.51.0`
- OS：`macOS-26.6.1-arm64-arm-64bit` / `arm64`
- 源 fixture：只读 `0444`；`foreign_keys=1`；journal mode 与编译选项详见 `evidence/environment.json`。
- 源 / 目标 schema version：bootstrap candidate version 1 → synthetic file fixture user_version 1；不做非空旧库 upgrade。

## 准确命令与退出合同

- 工作目录：项目根 `/Users/xxe/Documents/No.2`
- P3-031 合成空库命令：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`；快照退出码：`0`；结果 hash：`e5a18677a851d4eed6d025aaddf9deeda14c1bc49c925c47e9a6a8dab2fba25c`。
- P3-038 文件型命令：`lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh`
- 本次退出码：`0`
- 退出合同：任何 P0 / P1 FAIL、Unknown 或 Not Implemented 均非零；当前退出码与统计一致。

## 测试统计与失败项

- P0：PASS 2 / FAIL 0 / Not Implemented 0 / Unknown 0
- P1：PASS 10 / FAIL 0 / Not Implemented 0 / Unknown 0
- P2：PASS 0 / FAIL 0 / Not Implemented 0 / Unknown 0
- Total：PASS 12 / FAIL 0 / Not Implemented 0 / Unknown 0

- 无。

## P2-2 / P2-3 / P2-4 证据

- P2-2：`evidence/checks/p2_2_tombstone_delete_insert.json`
- P2-3：`evidence/checks/p2_3_tombstone_status_insert.json`
- P2-4：`evidence/checks/p2_4_authorization_child_delete.json`
- 消费门汇总：`evidence/checks/consumption_gate_results.json`
- 机器结果：`evidence/test_results.json`
- 摘要：`evidence/summary.md`
- 完整运行日志：`evidence/test_run.log`

## backup / restore / rollback / integrity / FK

- backup / restore 演练：`PASS`；详见 `evidence/migration/restore_rehearsal.log`。
- P2-2 rollback：详见 P2-2 JSON 与 `evidence/migration/rollback.log`。
- 源 fixture before/after hash、schema dump、integrity / quick / FK：见 `evidence/input/` 与 `evidence/checks/integrity_and_fk.json`。

## 运行输出 hash

| 文件 | 本次运行 SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/consumption_gate_results.json` | `a358e6bf75ea0dacefc78a710ae226d7393be0dc7abdfe4513e7d5d796fa59cc` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/integrity_and_fk.json` | `653a055934ffe3e7e5ae1f4d8b4d2bbb244014a705d5466479140e08136ee7a4` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_2_tombstone_delete_insert.json` | `073e82dc454c5bd29d91bbea6401f25024092220b84886f110f6d17ebfa5f350` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_3_tombstone_status_insert.json` | `a0a2f53109e8405af7f4dd77d05e09118890db615239c525623984bbb3af30b2` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_4_authorization_child_delete.json` | `b86108e452f0c36ba16250b986bfe6d21f332dfe327683b986e6049d9d1fb674` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/checks/path_isolation.json` | `d426566f2b4d1f6aeb5c3ffb62af18f12b34f7a481906294877e3603c5863b58` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/environment.json` | `1d60c36eb5b8474b2dac40299971db9f60f99656cd6150c1ca18cb814aed2caf` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/input/fixture_declaration.json` | `d58057ac970c745e3ab81712f2140e89d0ed1d08fa0ef9b10874731fc7d79f0e` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/input/p3_037_failure_preservation.json` | `261027f3e213ae559817e5c52c2df45c6a829c8a952aa6f50e3baaf1f30b5823` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/input/source_hashes.txt` | `803e6bd3c605057cd46afba9aff113c154047240cc50f926865799b939fb803f` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/input/source_manifest.json` | `0f2b41fe1495fc746022c0b537435ce4f59ba4c8d5cd11c68d8b434cb5057154` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/input/source_schema.sql` | `da7936b81a27e36f63944f2b9dd0197b073208aa63d9e3e2643962fcda82b9ac` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/migration/apply.log` | `cd7cdaf0fd3f192dbe3034877b8cd5e6d7d126e2b7e4287aad16d51972bdce2d` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/migration/candidate_hashes.json` | `0f2b41fe1495fc746022c0b537435ce4f59ba4c8d5cd11c68d8b434cb5057154` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/migration/restore_rehearsal.log` | `6144b781b8ce2bec1e09643df27ec027c3225082e7478609c77da8659e1118f9` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/migration/rollback.log` | `3867bc53440621da676efaa5120d70cfd9fc5acb34a713fd495fe8a96f49d2d9` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/p3_031_regression_snapshot.json` | `d745aa17046d7856bd813e77c2143fb6fe864574d8692a4304cae4d3eb4c996d` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/summary.md` | `c00e6036e130696bfe9a30359fbec0a19cd68e278fbdbc8c3fc6c6ead846b000` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/test_results.json` | `bdf6f9925994f84736776069742e8404591205a56c4673859455c0f7bc0f816d` |
| `lifeos/engineering/LIFEOS-P3-038/evidence/test_run.log` | `64d109ca37d643676d126900828ba4b474cb07e1553e6b31eed942215503ab2f` |
| `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.py` | `377a53c1735e2ef845275e469b1bcc537cf2d80df6a7b1a0d71a3f4ee6929a85` |
| `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh` | `454c8fe0c4bcf788e4eb2a6a32a748ffba56451cd2e1755e54c5ca8ee9b1c227` |
| `lifeos/engineering/LIFEOS-P3-038/input/001_candidate_schema.sql` | `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` |

## 不可外推声明

本 evidence 仅证明当前候选 SQL 快照在合成空库和本机文件型 SQLite、合成 fixture、单进程隔离副本中的行为。它不是生产 migration、真实用户 DB / Vault / Tauri / IPC 验证，不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线，不关闭 R-0040、R-0043 或 R-0046，不重新打开或关闭 R-0044 / R-0045，不构成正式 MVP 或下一阶段准入。
