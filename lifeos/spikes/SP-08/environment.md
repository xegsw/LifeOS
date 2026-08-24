# 环境

- 运行时：本机 `python3`，仅标准库。
- 数据：确定性合成 JSON / Markdown，无真实敏感数据。
- 外部依赖：无网络、无 Vault、无模型、无云、无第三方 API、无付费资源。
- 执行模型：单进程、本地文件系统；未验证并发、崩溃一致性、附件、压缩、签名、加密、容量或 SLA。

精确 Python / OS 版本可由 `python3 --version` 与 `uname` 复核；机器结论记录在 `raw_logs/run_summary.json`。

