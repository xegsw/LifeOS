# LIFEOS-P3-091 内容身份与处理边界可见性 UI

三张可独立以 `file:` 打开的今日页。固定非敏感演示文本、用户明确确认动作、合成系统状态和 AI 未启用状态均在页面内可见。所有交互状态只存在于当前页面内存；没有网络、浏览器持久化、文件、数据库、Tauri/IPC、模型或第三方依赖。

静态复跑：

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  lifeos/engineering/LIFEOS-P3-091/tests/static_check.mjs \
  lifeos/engineering/LIFEOS-P3-091
```

动态核查只能通过 Google Chrome（`com.google.Chrome`）与 Computer Use `@oai/sky`，在新建 task-local 临时副本的 `file:` 页面完成；不得以 HTTP、网络、CDP、命令行浏览器或浏览器持久化替代。
