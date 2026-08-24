# LIFEOS-P3-069 Independent Evidence Manifest

本 Evidence 由全新隔离独立复评产生。P3-067 工程、测试与既有 Evidence 全程只读；runner 仅复制候选 `src/recovery.py` 与 `scripts/recovery_cli.py` 到一次性临时副本，未导入、调用或复制 P3-067 测试文件。

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `independent_runner.py` | `9be4a159930f660e0cf6239a6c09fca854c708abbb85c50182028177fd8cea5c` | 全新独立 runner |
| `independent_results.json` | `ade88bf979157bbb519655f066d04b2a7ae6a8afefc7643d3bacec6ed38078e5` | 15 PASS / 0 FAIL 的结构化结果 |
| `lifeos/engineering/LIFEOS-P3-067/src/recovery.py` | `5329d725b271b340b403edfeffc2d37605c7029a9b5ae365c40031455b45f389` | 被评审当前候选源 |
| `lifeos/engineering/LIFEOS-P3-067/scripts/recovery_cli.py` | `02b7f5166d4f19503623dd9d596b698e8fa4cbf31693c3444880d2c34558b537` | 被评审当前候选 CLI |
| `lifeos/engineering/LIFEOS-P3-067/evidence/MANIFEST.md` | `660de57d3d398aec2981b0b5f37ee4acabd6897054d9ee7b2c3f637cc0746567` | 当前 P3-067 Rework Evidence 清单 |

## 核验摘要

- 当前 P3-067 Manifest 列出的 7 个主 Evidence 文件均与其 SHA-256 一致。
- P3-068 历史 `independent_runner.py` 与 `independent_results.json` 的 hash 仍分别匹配其历史 Manifest；其旧候选源 hash `b0a15c…e78bc` 与当前源 hash 不同，符合第二轮 Rework 后“历史 Rework Evidence 不覆盖当前 hash”的预期。
- 独立 runner 在 `/private/tmp/lifeos-p3069-independent/` 的一次性候选副本中验证：提交前故障／非法输入不伪称 `saved`、黑盒 CLI 的 ready preview → 首次 CONFIRM（非幂等）→ 二次 CONFIRM（幂等）链、`recovery_not_confirmed` 与 `recovery_blocked` 的跨重启耐久及顺序，以及 source/version/revocation/tombstone fail-closed。
- 静态检查未发现候选源／CLI 的网络、HTTP、socket、目录扫描或任意数据库路径入口；代码声明 network、Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、L3 与外部用户均关闭／未使用。

本 Evidence 仅覆盖合成 SQLite、单进程、任务目录和关闭态外部能力，不构成真实恢复、备份、真实路径、Tauri/IPC、风险关闭、工程基线恢复、冻结或 Stage 4 的证据。
