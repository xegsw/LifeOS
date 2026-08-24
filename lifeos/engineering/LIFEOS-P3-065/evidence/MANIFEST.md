# LIFEOS-P3-065 Rework Evidence Manifest

本 Manifest 覆盖 D-0280 授权的窄 Rework。初版执行 Evidence 已完整保留于 `evidence/initial/`，未被覆盖；该目录内的原 `MANIFEST.md` 保留初版文件 hash 和 14 PASS 结果。本 Rework 未修改任何 PM P1 Evidence。

生成方式：在本目录执行 `./scripts/run_tests.sh`。输入均为代码内受控合成枚举、合成 Project 和固定合成时间；没有读取个人数据、路径或网络资源。

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `src/permissions.py` | `29e33624b7988e3b18b9ec6451d1e76c97f43ae2189f65636e51d66460dca57a` | deny 优先、歧义拒绝、撤回命令幂等与审计消费门 |
| `scripts/permission_cli.py` | `342ef7bc918cb062090ad8d03866d4798822d83440818cfce14fd04f8ecb47d1` | 操作者 CLI |
| `tests/test_permissions.py` | `fb25ba02488d3ba6f686a89f7352341c853b90db4ae5a4c01baa94d73ab0619c` | 23 项回归及顺序／冲突矩阵 |
| `evidence/test_results.json` | `33dead70755c262e3529abb9c2cf207515cb092bafd51b3e784e0bcdd234b7cf` | 结构化统计与用例清单 |
| `evidence/snapshot.json` | `cda5d13fdbc474550221317a29cb8c9593f45c5be118f71a969d1da6afbdacf8` | 基础设置、审计、版本、确认快照 |
| `evidence/conflict_matrix_snapshot.json` | `daa6347de0c0b933ce79a7fbf0fe76558b9b474298e8d8d7d04f5d58d49b6ed2` | 九项顺序／冲突矩阵的返回、审计、版本与持久化快照 |
| `evidence/test_run.log` | `41326d6a8b1e084cd7e7d5695b981dc9ff4b01d2d949a4fdad5502de23d83ff7` | 复跑原始输出 |

结果：23 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0，退出码 0。

冲突规则：对同一精确 Project、类别、目的、位置、处理者绑定，任何当前有效 `denied` 均返回 `explicit_deny_current`；没有 deny 时仅恰好一项当前有效 `granted` 可以返回 allow；多项 grant 返回 `ambiguous_multiple_current_grants`。所有拒绝均为 fail-closed，且固定 `external_action: none`、`ai_consumption: none`。

边界：仅限单进程、合成 SQLite、本目录运行。`allowed=true` 只表示本地合成决定，不代表真实 AI、网络、Tauri/IPC、Vault、真实路径、导出、同步或其他能力获授权。
