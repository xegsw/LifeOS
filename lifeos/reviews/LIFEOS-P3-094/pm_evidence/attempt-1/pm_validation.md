# LIFEOS-P3-094 PM 独立复核记录（attempt-1）

## 方法与边界

- 在 PM 隔离临时副本中运行执行侧 `scripts/run_self_check.py`；未改写原工程或其 Evidence。
- 该复跑仅使用脚本内固定非敏感文本、临时 SQLite 与临时内部 HTML；退出码为 0，结构化结果为 14 PASS / 0 FAIL。
- PM 未重试 Chrome 或任何浏览器导航，避免再次触及任务禁止的外部访问边界。
- 本地模型预检未调用：本次是涉及真实本地数据边界与 P1 事件的最终 PM 判断，且其局域网调用不应替代或干扰该判断。

## 可复核发现

1. 执行侧 Manifest 中 12 个条目的 SHA-256 与当前工程文件逐项一致。
2. 执行侧离线自检的 14 项结果可在隔离副本重放；源码静态检查未发现 HTTP、socket、云、Tauri/IPC、导出或第三方客户端路径。
3. `tests/test_runtime.py` 的 `setUp()` 使用 `tempfile.mkdtemp()` 创建 `lifeos-p3-094-test-*`，但没有 `tearDown()` 清理。PM 复跑后在系统临时目录观测到 15 个同名前缀目录，每个含 `runtime.sqlite`，其中 4 个还含 task-local `today.html`。这些产物来自固定非敏感测试文本，但仍违反任务卡对全部 task-local DB／页面清理和可复核的完成定义。
4. 执行侧已报告 Chrome 地址输入被解析为 Google 搜索 URL。即使未取得网络传输日志，这一外部 URL 导航尝试已触发任务卡的“外部访问立即停止”规则；不得以离线测试通过抵消。

## PM 结论

- P0：0；P1：2（外部 URL 导航尝试；task-local 测试残留）；P2：0；Unknown：0；Not Implemented：1（合规 Chrome `file:` 动态验证）。
- 结论：`Rework / Awaiting User Confirmation`。不得进入独立复评、采纳、冻结、风险关闭、基线恢复或 Stage 4。
