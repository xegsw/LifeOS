# P3-084 Rework Chrome `file:` 动态操作日志

- 环境：本机 Google Chrome，新标签页；仅加载 `file:///private/tmp/lifeos-p3-084-rerun/index.html`。
- 输入：仅固定非敏感测试文本；未访问网络、未启动服务、未使用 CDP／命令行浏览器，也未触达持久化、文件 API、Tauri/IPC、Vault、导出、同步或模型。

| 步骤 | 操作与可观察结果 | 结论／视觉记录 |
|---|---|---|
| 1 | 新标签页输入 `file:` URL，页面成功加载，显示默认恢复态与“仅当前浏览器页面会话／AI 未启用”。 | PASS；`visual_default.png` |
| 2 | 空文本点击确认，状态变为“未保存：请输入原文后再显式确认”。 | PASS |
| 3 | 输入固定文本后点击确认，显示“已确认”与“你的记录／原文”。 | PASS；`visual_confirmed.png` |
| 4 | 点击模拟保存失败，记录隐藏，状态为“保存失败：本次会话未保留原文”。 | PASS |
| 5 | 切换“暂无可靠建议”，依次点击“选择 Project”“先记录当前停点”；两条受控说明均显示，未读取资料。 | PASS；`visual_no_suggestion.png` |
| 6 | 切换“权限受限 · 离线”，显示网络未使用、不联网不同步、AI 未启用及已确认行动非 AI 确认。 | PASS；`visual_restricted.png` |
| 7 | 对同一固定文本连续两次显式确认；页面只保留一个 saved-record 区域（文本在输入框和单一显示区各出现一次）。 | PASS |
| 8 | 先确认“刷新清除复测”文本，再以 Chrome 刷新快捷键刷新；回到默认恢复态，文本、记录、确认回执均已清除，状态为“尚未确认保存”。 | PASS；`visual_after_refresh.png` |
| 9 | 先确认“关闭后必须清除”文本，关闭该临时 `file:` 标签页；再新开标签页并打开同一干净副本。页面为初始态，无该文本或记录。 | PASS；`visual_reopened.png` |

Chrome 的本地文件提示曾在一次状态切换后出现；仅关闭该非绑定提示后继续。未接受安全警告、未调整任何 Chrome 设置，且未采用替代路径。
