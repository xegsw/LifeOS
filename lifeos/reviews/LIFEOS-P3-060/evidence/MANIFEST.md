# LIFEOS-P3-060 Current Successor Evidence Manifest

## 范围与谱系

本包是 `LIFEOS-P3-031` 的 **current successor Evidence**，只绑定当前候选 SQL、合同 tests 与 runner；它不替换、重写或宣称等同于 `lifeos/engineering/LIFEOS-P3-031/evidence/` 的历史 P3-031 Evidence。历史包仍保留其 70 PASS 与早期 hash 的事实；此次包明确记录差异并提供当前 74 PASS 的可复核后继快照。

所有工作仅在合成 SQLite、单进程、本地临时副本和本目录中进行。未连接真实 DB、Vault、用户文件、Tauri/IPC、网络、云或外部用户；不改变任何风险、冻结、工程基线或阶段状态。

## 独立性与写入边界

- 独立计划在读取 P3-039/P3-058 攻击实现前封存：[INDEPENDENCE_PLAN.md](INDEPENDENCE_PLAN.md)。
- 自建 runner 为 [independent_r0043_matrix.py](independent_r0043_matrix.py)，未 import、调用或复制 P3-039/P3-058 的攻击函数、场景表或结果。
- 工程与历史 Evidence 全程只读；仅新增 P3-060 deliverable、review、manifest、计划、快照、结果、日志和本地预检。

## Before/after 只读保留核验

开始时对任务直接输入与历史 Evidence 逐文件计算 SHA-256；结束时重新计算。受保护集合（P3-031/037/038 Evidence、P3-039/058 Evidence、历史任务/Review、RISK_LOG、DECISION_LOG）共 60 个文件，结束集合哈希为 `cacbaaedc73c36525f5bc3f4182bbbcb1d93c1e99bd13b6df0022f62d5635a80`；逐项对照开始清单均一致，未发现覆盖或改写。

| 关键输入 | Before SHA-256 | After |
|---|---|---|
| 当前 SQL | `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` | Same |
| 当前 contract tests | `45d19e56fc3aaf75ccd12c5de678dec770c425fec9e8d570e3783f4a7bb8224a` | Same |
| 当前 runner | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | Same |
| P3-031 历史 manifest / result | `479ca2c82bbdc85a3ae41d53c1aa1fb6fc58a3bc1f2259345efd335007e7fb96` / `59fc105b4a4e49330271299a4f881d9a59bf97c6b77fce4eb313f8f88943c2a7` | Same / Same |
| P3-037 Evidence manifest / results | `8aa519c023e846f88de7a3d0d0b48e8bb9372f50251db7be8c9b38dd3a2072e3` / `253a3ff4ba33137e90ef3ead0f8cdbeddeb1a507e927fa1f97c8a90b0ee4e354` | Same / Same |
| P3-038 Evidence manifest / results | `ab0cb881aa4ae1513ad134fd54a392d6bbb4dd07a0317c7d39ee948f7f3e724f` / `bdf6f9925994f84736776069742e8404591205a56c4673859455c0f7bc0f816d` | Same / Same |
| P3-039 manifest / structured attacks | `a5603682e1b60af5947200f5b7c9954fb3825857cda74a37ac686b4365f8c7f7` / `0630a27be39692a5e1b962feefacaec84bc8941a754069d0c51f25e04cdd6545` | Same / Same |
| P3-058 manifest / review | `f22f7510abbc0ca72cb6b3a3bae3fa4030c06888de9594fce94f020b83185773` / `dc91ea889c71b42417cd22f245aaa3b05d27630ae0498f357248c600288c3ada` | Same / Same |
| RISK_LOG / DECISION_LOG | `6fc9566f616a769f221396e0a89eb39992528cff323cc5f5fa4f5c65d2f42931` / `65e09edb16a65e28d6f08caae80c4c1ef447bbf2d4226e762f8fea54e1e5785e` | Same / Same |

## 当前候选快照与受控复跑

快照位于 [current_candidate_snapshot](current_candidate_snapshot)：SQL、tests、runner hash 分别与上表当前值一致。复制 `lifeos/engineering/LIFEOS-P3-031` 至 `/private/tmp/lifeos-p3-060.6IPdcB/LIFEOS-P3-031` 后运行其 `scripts/run_validation.sh`；原工程目录未运行会写 Evidence 的入口。

| 项目 | 结果 |
|---|---|
| exit code | 0 |
| P0 / P1 / P2 | 18 / 29 / 27 PASS |
| FAIL / Unknown / Not Implemented | 0 / 0 / 0 |
| total | 74 PASS |
| structured result hash | `024a60fcda8e1802789a64c99c6e9081ea2b39dd342200d37cd3a4538d8c6b64` |
| log hash | `15c5957ee0599a3a7f21824ea9f809aae7ad96459a7024174f2f18a687bf9e03` |

输出：[current_p3031_contract_results.json](current_p3031_contract_results.json)、[current_p3031_contract_run.log](current_p3031_contract_run.log)。

## 独立 R-0043 相邻矩阵

矩阵覆盖 memory/file × `foreign_keys` ON/OFF × `recursive_triggers` ON/OFF，共 8 个配置。每个配置覆盖 tombstone generation 降级、DELETE/reinsert、普通 Tombstone 向 Authorization 改绑并伪造 generation/command/reason/time、伪造 Authorization Tombstone INSERT、合法单调 successor、事务 savepoint 回滚后合法写入。

- 48 PASS / 0 FAIL / 0 Unknown / 0 Not Implemented；runner exit 0。
- 结果：[independent_r0043_matrix_results.json](independent_r0043_matrix_results.json)，SHA-256 `f26614f243edc653e59ef6ac889c51d1c3ba43bfd7a907a9f176da8abb28df46`。
- runner SHA-256：`2bd542f667a83db41fcfe2092472ae20d1dbb1606336b265955407d440b0cb9f`。

## 历史差异的明确处理

历史 P3-031 manifest 当前仍声明 SQL `56f3c77f…ac6d`、tests `6729d48e…b3b5` 与 70 PASS；其结构化结果文件也仍为 70 PASS。这些历史资产的 hash 已保留，且不应被覆写。本 P3-060 包将当前 SQL `bda3e8…9b1`、tests `45d19e…224a`、runner `611a…6230d`、74 PASS 与本次独立矩阵明确绑定，因此消除了“将旧主 Evidence 冒充为当前候选 Evidence”的问题，而非抹除历史谱系。

## 不可外推与结论边界

本 Manifest 仅为 PM 对 R-0043 的后续决策输入。它不关闭或重开 R-0043，不冻结 Schema/API 或工程基线，也不证明真实 DB/非空升级、并发/WAL/恢复、真实 Vault/文件、Tauri/IPC、生产 SLA 或阶段准入。

## 本地预检

已按规则调用 `lifeos/tools/local_precheck.py`。本地模型不可用（`Operation not permitted`），因此允许跳过；记录见 `lifeos/local_prechecks/LIFEOS-P3-060_LIFEOS-P3-060_r0043_current_p3031_evidence_alignment_and_independent_check_local_precheck.md`。该预检不影响本次人工核对结论。
