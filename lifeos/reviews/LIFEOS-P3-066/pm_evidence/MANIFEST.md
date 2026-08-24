# LIFEOS-P3-066 PM Evidence Manifest

## PM 隔离复跑

- PM 将 `lifeos/engineering/LIFEOS-P3-065/` 复制到一次性临时副本 `/private/tmp/lifeos-p3066-pm.l0PAU4/LIFEOS-P3-065/`；原工程、初版 Evidence、Rework Evidence 与 P3-066 执行侧 Evidence 均未写入。
- 在该副本运行 P3-066 的独立 runner：退出码 `0`，`14 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0`。
- 在同一副本运行候选既有回归 `./scripts/run_tests.sh`：退出码 `0`，`23 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0`。
- PM 复跑的独立 runner 与 P3-065 `tests/test_permissions.py` 分离；其结果再次覆盖历史 P1 的 `grant→deny` 与 `deny→grant`、默认拒绝、绑定不匹配、到期、撤回、多 grant 歧义、决定／撤回幂等冲突、CLI 明确确认、审计状态和关闭态边界。

## Hash 与保留核对

| 产物 | SHA-256 | PM 判断 |
|---|---|---|
| `src/permissions.py` | `29e33624b7988e3b18b9ec6451d1e76c97f43ae2189f65636e51d66460dca57a` | 与 P3-065 Rework、P3-065 PM Evidence、P3-066 Evidence 一致 |
| `scripts/permission_cli.py` | `342ef7bc918cb062090ad8d03866d4798822d83440818cfce14fd04f8ecb47d1` | 一致 |
| `tests/test_permissions.py` | `fb25ba02488d3ba6f686a89f7352341c853b90db4ae5a4c01baa94d73ab0619c` | 一致 |
| Rework `evidence/test_results.json` | `33dead70755c262e3529abb9c2cf207515cb092bafd51b3e784e0bcdd234b7cf` | 23 PASS Evidence 保留 |
| Rework `conflict_matrix_snapshot.json` | `daa6347de0c0b933ce79a7fbf0fe76558b9b474298e8d8d7d04f5d58d49b6ed2` | 冲突修复 Evidence 保留 |
| 初版 `evidence/initial/MANIFEST.md` | `fd7546e1c69f78d075ea7804820b860ae0fcd3b30a24162cf06fad395effd00b` | 初版 14 PASS Evidence 仍独立保留 |
| P3-065 PM Evidence Manifest | `1fd724b227dfac4e1166cc0a9fce3a4d4ddd3d51648210c6d5480073bb035e6e` | 历史 P1 与 Rework 记录未覆盖 |

## 边界

本 Evidence 仅支持当前 hash、单进程、合成 SQLite、受控 Project 与无外部动作。未验证真实身份／数据／路径／Vault、Tauri/IPC、网络／云、导出、同步、多设备、L3、并发／WAL、风险关闭、工程基线恢复、冻结或 Stage 4。
