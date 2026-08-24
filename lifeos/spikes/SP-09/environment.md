# SP-09 环境说明

- 执行日期：2026-08-09（Asia/Shanghai）
- 操作系统：macOS 26.5.2，arm64
- CPU：Apple M5，10 核
- 内存：25,769,803,776 bytes（24 GiB）
- 文件系统：本轮开始时工作盘约 838 GiB 可用
- Python：3.9.6
- SQLite：3.51.0，FTS5 可用，WAL 可用；`PRAGMA secure_delete` 实测返回 `2`（FAST）
- 候选参数：WAL、`synchronous=FULL`、外键开启、60 秒 busy timeout、128 MiB SQLite page cache 上限、临时数据落文件
- 最终整轮 `/usr/bin/time -l`：77.65 秒；maximum resident set size 312,475,648 bytes；0 swaps

本机达到任务的 16 GiB RAM / 足够本地磁盘最低候选条件。测试不包含真实用户数据、真实路径、真实 Vault、真实 Project 名、真实 prompt/输出、真实向量或真实模型调用。

Docker、`psql` 和本地 PostgreSQL 服务均不可用，因此 PostgreSQL/FTS/pgvector/ANN 未实测；未创建外部账号、容器、云服务或付费资源。该缺口必须保留到技术架构候选评审，不得用 SQLite 结果替代。
