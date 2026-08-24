# SP-03 运行环境与边界

- 运行入口：`python3 lifeos/spikes/SP-03/run_spike.py`
- 依赖：Python 标准库；无第三方包、数据库服务、网络或模型依赖。
- 数据：固定种子 `20260808` 的合成、可丢弃夹具。
- 隔离：脚本只在 `lifeos/spikes/SP-03/` 内改写证据输出。
- 明确未做：未连接真实 Obsidian Vault，未读取用户真实文档，未调用云、第三方 API 或真实模型，未修改 Stitch 或产品代码。
- 结论边界：脚本中的字典、JSON 包络、状态名、依赖查询与导出格式只服务 Spike；不冻结 Schema、API、事件流、图数据库、存储或技术架构。

实际 Python、操作系统、架构和运行时间由每次运行写入 `results.json`。
