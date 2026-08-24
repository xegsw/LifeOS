# LIFEOS-P3-039 Evidence Manifest

## 评审信息

- 任务 ID：LIFEOS-P3-039
- 评审类型：隔离独立工程复评
- 评审会话：WorkBuddy 独立评审会话（与 P3-038 Codex 执行会话隔离）
- 评审日期：2026-08-17
- 评审结论：Pass with Conditions

## 授权与隔离范围

- 评审使用临时副本 `/tmp/p3-039-yWfgBq/` 复跑 P3-031 和 P3-038，未修改原始工程文件。
- 独立反例脚本使用内存合成 SQLite 空库，未连接真实用户 DB、Vault、Tauri / IPC。
- 未修改 P3-031 / P3-037 / P3-038 原始 SQL、测试、脚本、fixture 或 evidence。
- 未修改 PM 账本、风险状态或冻结状态。

## 文件清单

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `counter_example_attacks.py` | 独立反例攻击脚本（29 个攻击场景） | `16e493390a1eeb86cf076959ab2576e593c74f6fc5c98e7c647642c50179ce9d` |
| `counter_example_results.json` | 结构化反例结果（29 攻击 / 18 PASS / 11 FAIL） | `0630a27be39692a5e1b962feefacaec84bc8941a754069d0c51f25e04cdd6545` |
| `counter_example_results.txt` | 反例运行完整日志 | `0b95ea393a39655a81c0a34cb4281ff49a2858de1326906a1e74f479ed9c69fa` |
| `candidate_schema.sql` | 候选 SQL 输入快照（与 P3-031 原始匹配） | `008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2` |

## 复跑统计

| 套件 | 独立复跑结果 | 退出码 | 与报告一致 |
|---|---|---|---|
| P3-031 合成空库 | 38 PASS / 0 FAIL / 0 Not Implemented（P0=18, P1=12, P2=8） | 0 | Yes |
| P3-038 受控文件型 | 12 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown（P0=2, P1=10） | 0 | Yes |

## Hash 校验

### P3-031 稳定源文件

| 文件 | 期望 SHA-256 | 实际 SHA-256 | 匹配 |
|---|---|---|---|
| `migrations/001_candidate_schema.sql` | `008cd328...c4cf2` | `008cd328...c4cf2` | Yes |
| `tests/run_contract_tests.py` | `246f3675...39da` | `246f3675...39da` | Yes |
| `scripts/run_validation.sh` | `611a2714...6230d` | `611a2714...6230d` | Yes |

### P3-037 failure evidence 保留

| 文件 | 既有 SHA-256 | 当前 SHA-256 | 未变 |
|---|---|---|---|
| `evidence/MANIFEST.md` | `8aa519c0...72e3` | `8aa519c0...72e3` | Yes |
| `evidence/test_results.json` | `253a3ff4...e354` | `253a3ff4...e354` | Yes |
| `evidence/checks/p2_2_...json` | `374c0304...f603` | `374c0304...f603` | Yes |
| `evidence/checks/p2_3_...json` | `cf3d3b8d...df34` | `cf3d3b8d...df34` | Yes |
| `evidence/checks/p2_4_...json` | `68d3e1a1...8dda` | `68d3e1a1...8dda` | Yes |

### 运行输出 hash

| 文件 | 期望 SHA-256 | 实际 SHA-256 | 匹配 |
|---|---|---|---|
| P3-038 `evidence/test_results.json` | `bdf6f992...f816d` | `bdf6f992...f816d` | Yes |
| P3-031 `evidence/test_results.json` | `e5a18677...ba25c` | `e5a18677...ba25c` | Yes |

## 独立反例攻击统计

| 分组 | 攻击数 | PASS | FAIL | P1 bypass |
|---|---|---|---|---|
| P2-2（Tombstone DELETE/REPLACE/DELETE+INSERT） | 6 | 6 | 0 | 0 |
| P2-3（Tombstone 初始状态/转换/generation） | 8 | 8 | 0 | 0 |
| P2-4（Active Auth 子表 DELETE + inactive 清理） | 4 | 4 | 0 | 0 |
| ADJ（Active Auth 子表 INSERT/UPDATE/改绑/REPLACE） | 11 | 0 | 11 | 11 |
| **Total** | **29** | **18** | **11** | **11** |

## 环境

- Python：3.13.12（评审脚本）；P3-031/P3-038 复跑使用系统 Python 3.9.6（与原始环境一致）
- SQLite：3.51.0
- OS：macOS arm64
- 网络：未使用
- 真实 DB / Vault / Tauri / IPC：未触碰

## 不可外推声明

本 evidence 仅证明当前候选 SQL 快照在合成空库和本机内存 SQLite 中的行为。它不是生产 migration、真实用户 DB / Vault / Tauri / IPC 验证，不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线，不关闭 R-0040、R-0043 或 R-0046，不重新打开或关闭 R-0044 / R-0045（仅建议 PM 重新评估 R-0044），不构成正式 MVP 或下一阶段准入。
