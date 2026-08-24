# LIFEOS-P3-009 Target-stack minimum skeleton

这是隔离的 TypeScript + Node.js + SQLite 最小工程骨架，用于迁移 P3-001 的 H1-H9 / T-ARCH 不变量。它不是生产应用、正式 Schema/API 或真实 Tauri 集成。

## 边界

- 只使用 `fixtures/synthetic_v1.json` 中的可丢弃合成数据。
- SQLite 来自 Node 24 内建 `node:sqlite`；无网络安装依赖。
- 真实 Vault、Tauri/IPC、文件导出、云/第三方模型、向量、同步/多设备、L3、外部用户全部硬关闭。
- “导出”仅返回内存对象，不写文件。

## 复跑

本机 PATH 若已有 Node 24：

```bash
npm test
npm run validate
```

Codex 随附运行时：

```bash
NODE=/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
$NODE --experimental-strip-types --test tests/*.test.ts
$NODE scripts/validate.mjs
```

`validate` 会复跑全部测试并刷新 `evidence/`。退出码非零代表验证失败。
