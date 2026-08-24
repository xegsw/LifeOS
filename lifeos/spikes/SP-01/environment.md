# SP-01 运行环境

- 运行日期：2026-08-08（Asia/Shanghai）
- 主机：Apple arm64，10 个逻辑 CPU，24 GiB 内存
- 操作系统：macOS 26.5.2；Darwin 25.5.0
- Python：3.9.6（仅标准库）
- SQLite：3.51.0（Python `sqlite3`）
- 存储配置：`journal_mode=WAL`、`synchronous=FULL`、`foreign_keys=ON`、`busy_timeout=5000`
- 测试卷：APFS 数据卷；运行前约 838 GiB 可用
- 网络：脚本不访问网络；不调用云、第三方 API 或模型
- 数据：固定种子 `20260808` 生成的合成字符串，不读取真实文档、Vault 或敏感数据

资源口径：`results.json` 中 `ru_maxrss` 为 macOS 返回的字节数；本次主进程峰值约 20.0 MiB。子进程总峰值未汇总。延迟是本机单进程 Python 调用的墙钟时间，不是产品端到端 UX 指标或市场承诺。

