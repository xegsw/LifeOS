# SP-09 证据入口

本目录仅包含确定性合成数据、可复跑基准、结构化结果和可删除工作库。它不是产品实现，也不冻结 Schema、数据库、索引、向量或架构。

## 一条命令复跑

```bash
python3 lifeos/spikes/SP-09/run_spike.py --tiers 10000,100000 --full --keep-work
```

预计要求：SQLite 3.51+（含 FTS5）、约 4 GiB 可用磁盘；本机整轮约 78 秒。`--keep-work` 保留数据库、备份和恢复副本；去掉该参数仅保留轻量证据。100 万档并发维护断言按本次证据预期为 FAIL，进程因此返回非零；这代表已知条件，不代表脚本故障。

## 文件索引

- `run_spike.py`：合成数据生成器、SQLite/FTS5 基准、删除/恢复/并发探针与证据生成器。
- `evidence/results.json`：三档原始结构化结果、查询计划、环境和向量成本模型。
- `evidence/test_matrix.csv`：逐档机器断言（共 45 项）。
- `evidence/vector_costs.csv`：300 万向量、384/768/1536 维、100%/25%/10% 覆盖、float32/float16 原始成本估算。
- `evidence/privacy_scan.json`：合成与日志隐私检查。
- `evidence/failure_samples.json`：机器失败样例；当前仅 100 万档“全量 FTS 重建期间捕获超过 1 秒”。
- `environment.md`：实际本机与未验证组件边界。
- `fixtures.md`：数据模型、状态分布和查询集。
- `resource_summary.md`：三档容量、性能和资源摘要。
- `failure_samples.md`：失败解释与允许/禁止的处置。
- `execution_log.txt`：最终整轮控制台与 `/usr/bin/time -l` 摘要。
- `cleanup.md`：精确清理说明。
- `work/`：可重建 SQLite 主库、删除前备份和恢复副本；不属于长期权威资产。

## 结论边界

- 1 万/3 万、10 万/30 万、100 万/300 万均为实际装载和实测，不是外推。
- PostgreSQL、PostgreSQL FTS、pgvector、ANN、真实 embedding、真实附件、真实 Vault、真实并发和冷缓存未实测。
- 向量数字是存储算术估算，不含 ANN、表、MVCC、WAL、备份和构建峰值。
- 查询均在单机热缓存、单进程候选映射上执行；不得外推为生产 SLA。

