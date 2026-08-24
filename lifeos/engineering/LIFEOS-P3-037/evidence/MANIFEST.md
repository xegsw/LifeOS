# LIFEOS-P3-037 Evidence Manifest

## 授权与隔离范围

- 任务：`LIFEOS-P3-037`，仅受控文件型 SQLite + 合成 fixture 验证。
- 唯一写入工程根：`lifeos/engineering/LIFEOS-P3-037/`。
- 固定无参数入口拒绝 `~`、宽泛目录、UNC / scheme 网络路径、用户 DB / Vault-like 名称、隔离目录外路径与 symlink。
- 未连接或修改真实用户 DB、真实 Vault、真实文件；未启动 Tauri / IPC；未启用网络、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- P3-031 源文件只读核对；候选 SQL 只复制为输入快照，没有修改原文件。

## 创建 / 修改文件

- `input/001_candidate_schema.sql`：P3-031 候选 SQL 输入快照。
- `scripts/run_validation.py`、`scripts/run_validation.sh`：固定路径验证入口。
- `work/`：合成只读源 fixture、可丢弃攻击副本、backup 与 restore 文件。
- `evidence/`：环境、hash、逐项结果、日志与本 manifest。

## 稳定输入 hash

| 稳定源文件 | 期望 SHA-256 | 实际 SHA-256 | 匹配 |
|---|---|---|---|
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` | `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` | Yes |
| `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py` | `defdd87e1ee355a978ddb75352c1a8aeca9e33960a2ad2922b8385e9740b295c` | `defdd87e1ee355a978ddb75352c1a8aeca9e33960a2ad2922b8385e9740b295c` | Yes |
| `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` | `61f9d6a17dfd4eb455ffd0e768c5289d0e9b5d578235130aa212d6e0896e2769` | `61f9d6a17dfd4eb455ffd0e768c5289d0e9b5d578235130aa212d6e0896e2769` | Yes |

- 输入快照：`lifeos/engineering/LIFEOS-P3-037/input/001_candidate_schema.sql` / `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` / 与 P3-031 原始 SQL 匹配：`True`。
- 稳定输入 hash 与下方运行输出 hash 分开记录。

## 环境

- Python：`3.9.6`（CPython）
- SQLite：`3.51.0`
- OS：`macOS-26.6.1-arm64-arm-64bit` / `arm64`
- 源 fixture：只读 `0444`；`foreign_keys=1`；journal mode 与编译选项详见 `evidence/environment.json`。
- 源 / 目标 schema version：bootstrap candidate version 1 → synthetic file fixture user_version 1；不做非空旧库 upgrade。

## 准确命令与退出合同

- 工作目录：项目根 `/Users/xxe/Documents/No.2`
- 命令：`lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh`
- 本次退出码：`1`
- 退出合同：任何 P0 / P1 FAIL、Unknown 或 Not Implemented 均非零；当前退出码与统计一致。

## 测试统计与失败项

- P0：PASS 2 / FAIL 0 / Not Implemented 0 / Unknown 0
- P1：PASS 5 / FAIL 3 / Not Implemented 0 / Unknown 0
- P2：PASS 0 / FAIL 0 / Not Implemented 0 / Unknown 0
- Total：PASS 7 / FAIL 3 / Not Implemented 0 / Unknown 0

- `FILE-P1-P2-2` / P1 / FAIL：DELETE/INSERT and OR REPLACE can lower/remove tombstone and six simulated gates ALLOW
- `FILE-P1-P2-3` / P1 / FAIL：four non-accepted initial states are directly insertable
- `FILE-P1-P2-4` / P1 / FAIL：runtime/cache/queue rechecks DENY, but child DELETE commits without parent generation/status change or audit

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
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/consumption_gate_results.json` | `d18e28e837c3630c0acd48296fc936e53935743b36781463c2844d6727eda034` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/integrity_and_fk.json` | `93500ce93f809f13c17df5c53dd5e24ecd2053737d036712bcce62dda05caaeb` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json` | `374c0304e6557c4a9561609820ce741a49108d4731a98fad3a3ceb4dbd0ff603` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json` | `cf3d3b8da7d8a837010e2fc883102a516e6018bad7454431933867aeae80df34` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json` | `68d3e1a16bb9493e552f5ea0ec3918fe5576be6e26943cacb7fd2ff33f4d8dda` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/checks/path_isolation.json` | `37f5d1d6fda03d4db6143c6ac7c50054d73d60693245c0463515aeae8fea3505` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/environment.json` | `036db8d4ff1d0332201452cad25e6903da1de9c417813bb81eaea08e68d4771b` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/input/fixture_declaration.json` | `d58057ac970c745e3ab81712f2140e89d0ed1d08fa0ef9b10874731fc7d79f0e` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/input/source_hashes.txt` | `d52366dcf9f0899ba6d5735c877f307c74031201b4f11cdb223df0b7d8c85ed5` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/input/source_manifest.json` | `e247ac600b2522d3efe2733cde00b269f48196693b6b269155b642af7a6ede9c` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/input/source_schema.sql` | `cdd4c286dbbff8b772efd2dfedbb7a2a928c1cc4aacd84d0cbcd43739227c2ac` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/migration/apply.log` | `cd7cdaf0fd3f192dbe3034877b8cd5e6d7d126e2b7e4287aad16d51972bdce2d` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/migration/candidate_hashes.json` | `e247ac600b2522d3efe2733cde00b269f48196693b6b269155b642af7a6ede9c` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/migration/restore_rehearsal.log` | `7cfa6394cff2c8fe458a97f6d417f0c393a3deef0c55b4e1c866e716e881a5f3` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/migration/rollback.log` | `300c2ed8ba452161c49eacd713af93a23b3e4f6f3985108d3fa32006ed2c5386` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/summary.md` | `09d665b8098174cb902eb592e3cb361bf6d1768a094f6dc63373bc31df7f9bce` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json` | `253a3ff4ba33137e90ef3ead0f8cdbeddeb1a507e927fa1f97c8a90b0ee4e354` |
| `lifeos/engineering/LIFEOS-P3-037/evidence/test_run.log` | `8c5098ce2a4b1a1792e625a0a3cfc4bafb30441031d8a33ffe64b788330deefd` |
| `lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.py` | `fb6fff24726bf188db6edfce89d4a6b52d1ae23c11a5e275e420d101193c5ea5` |
| `lifeos/engineering/LIFEOS-P3-037/scripts/run_validation.sh` | `454c8fe0c4bcf788e4eb2a6a32a748ffba56451cd2e1755e54c5ca8ee9b1c227` |
| `lifeos/engineering/LIFEOS-P3-037/input/001_candidate_schema.sql` | `55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1` |

## 不可外推声明

本 evidence 仅证明当前候选 SQL 快照在本机文件型 SQLite、合成 fixture、单进程隔离副本中的行为。它不是生产 migration、真实用户 DB / Vault / Tauri / IPC 验证，不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线，不关闭 R-0040，不重新打开或关闭 R-0043 / R-0044 / R-0045，不构成正式 MVP 或下一阶段准入。
