# LIFEOS-P3-089 合成生命周期 UI

三张可独立以 `file:` 打开的今日页。所有输入、权限、恢复预览和回执仅保存在当前页面 DOM；没有浏览器持久化、网络、文件、数据库、Tauri/IPC、模型或第三方依赖。

静态复跑：

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  lifeos/engineering/LIFEOS-P3-089/tests/static_check.mjs \
  lifeos/engineering/LIFEOS-P3-089
```

动态核查只能通过 Google Chrome（`com.google.Chrome`）与 Computer Use `@oai/sky`，在新建 task-local 临时副本的 `file:` 页面完成；不得以 HTTP、网络、CDP、命令行浏览器或浏览器持久化替代。
