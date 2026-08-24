# 环境与边界

- 执行日期：2026-08-09。
- 运行时：本机 Python 3、标准库 `sqlite3` / SQLite FTS5。
- 存储：进程内 SQLite；机器证据写入本 Spike 目录。
- 网络、真实模型、真实 embedding、真实 pgvector / ANN、云、第三方 API：均未使用。
- 数据：固定合成语料；未读取或扫描真实 Vault、真实用户文件或凭据。

因此所有延迟只代表 60 条内存合成样本，不是容量或生产 SLA。pgvector 未被生产级验证。

