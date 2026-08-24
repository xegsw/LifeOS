# LIFEOS-P3-085｜三张冻结今日页多页本地 UI 壳

这是一个无依赖、纯本地的三页演示壳。可分别直接以 `file:` 打开：

- `default-recovery.html`：默认恢复与仅当前页面会话的手动捕获演示。
- `no-reliable-suggestion.html`：尚未选择 Project 时的“暂无可靠建议”页。
- `restricted-offline.html`：权限受限／离线且 AI 关闭的降级页。

页面仅使用相对本地 CSS 与 JavaScript。不会访问网络、浏览器持久化、文件、数据库、Tauri/IPC、服务或第三方依赖；刷新和关闭会清除手动捕获内容。

## 静态复跑

从本目录运行：

```sh
node tests/static_check.mjs
```

动态 `file:` 演练、结果、视觉记录与 hash 见 `evidence/`。
