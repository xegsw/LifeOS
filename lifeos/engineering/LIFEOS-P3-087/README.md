# LIFEOS-P3-087 受控本地 UI

三张仅可通过相对本地资源打开的静态页面。它们不包含网络、持久化、真实文件、数据库、Tauri/IPC、导出、同步、模型或第三方依赖。

静态复跑：

```sh
node tests/static_check.mjs . > evidence/static_results.json
```

动态／视觉复跑仅限 Google Chrome（`com.google.Chrome`）通过 Computer Use `@oai/sky`，在新的 Chrome 标签页直接打开干净 task-local 副本的 `file:` 入口。不得以 HTTP、网络、CDP、命令行浏览器或其他浏览器替代。
