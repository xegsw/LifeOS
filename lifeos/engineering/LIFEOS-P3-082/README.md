# LIFEOS-P3-082 最小本地 UI

仅可通过本地浏览器的 `file:` 地址打开 `index.html`。无需安装依赖、无需启动服务、不会联网。

- 手动输入仅存在于当前页面会话；刷新或关闭页面即丢弃。
- 页面不访问文件、数据库、浏览器持久存储、Tauri/IPC 或外部服务。
- 这不是生产、Alpha、真实耐久、真实导出、真实 AI、风险关闭、冻结或 Stage 4 证据。

静态检查：`node tests/static_check.mjs`
