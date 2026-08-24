# LIFEOS-P3-065 Evidence Manifest

生成方式：在本目录执行 `./scripts/run_tests.sh`。所有输入为代码内受控枚举与合成时间戳；未读取个人数据、路径或网络资源。

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `src/permissions.py` | `d86e5e1920889bd51765b38178d24258b6c955d2750a12757be4319b91459ad7` | SQLite 适配、授权决策、审计与消费门 |
| `scripts/permission_cli.py` | `342ef7bc918cb062090ad8d03866d4798822d83440818cfce14fd04f8ecb47d1` | 操作者 CLI |
| `tests/test_permissions.py` | `7aced9708725a628d97541ff58c75a774cfb05f75ca630f61cc1c1eb59158bd9` | 14 项受控回归（含 CLI 路径） |
| `evidence/test_results.json` | `d94c054657ae7189d11518d42154b3bab24e0027709a836032b76f01cce5d442` | 结构化测试统计 |
| `evidence/snapshot.json` | `ee749ae856f08be397da5cca436970284d2c6c237842adc90990301c1e0df1cd` | 授权、版本、确认和审计快照 |
| `evidence/test_run.log` | `5dae0ddb026d498bff7dd17a819690371cef2d6269cdfad5c5cbb51b2abfe6b1` | 原始复跑输出 |

结果：14 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0，退出码 0。

边界：仅限合成 SQLite、单进程、本地目录。`allowed=true` 只表示返回本地合成决定；没有外部动作、网络、AI 内容消费、Tauri/IPC、Vault、真实路径或导出。
