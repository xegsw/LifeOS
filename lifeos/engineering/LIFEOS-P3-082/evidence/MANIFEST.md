# LIFEOS-P3-082 Evidence Manifest

## 执行信息

- 任务卡：`lifeos/tasks/LIFEOS-P3-082_three_frozen_today_pages_minimal_local_ui_preflight_capability_package.md`
- 授权证据：用户于 2026-08-21 CST 将任务卡路径投递至新建隔离 Codex 工程执行会话；接收时间 2026-08-21 18:02:34 CST。
- 工程范围：仅本 `LIFEOS-P3-082/` 目录；未改项目账本、冻结 Stitch 原型或历史资产。
- 运行方式：仅用户本机 `file:` 打开 `index.html`；无需依赖或服务。

## 文件与 SHA-256

| 文件 | SHA-256 |
|---|---|
| `index.html` | `eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722` |
| `styles.css` | `7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2` |
| `app.js` | `784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d` |
| `tests/static_check.mjs` | `08b8b22aa3d6c9fc7397863fe1e4e5bf202793dd8f2f69c0ae084e153e019778` |
| `README.md` | `2b5562b3d2b14e024bcd47cc74e86f1ffbf1076d6a2560686d7f428caae8ce12` |

## 自检结果

- 静态 runner：24 PASS / 0 FAIL；结果在 `static_check_results.json`。
- 本地预检：Skipped / Local Model Unavailable；详见 `lifeos/local_prechecks/LIFEOS-P3-082_LIFEOS-P3-082_three_frozen_today_pages_minimal_local_ui_preflight_capability_package_local_precheck.md`。该报告未参与自检结论。
- 动态 `file:` 浏览器演练：Not Implemented；浏览器安全策略拒绝本地 file URL。详见 `browser_blocker.md`。
- P0=0；P1=0；P2=0；Unknown=0；Not Implemented=1（浏览器端到端与截图）。
- 总体包内自检：**Not Pass**。原因是任务卡强制的干净浏览器会话、刷新清除和截图 Evidence 尚未完成。

## 复跑命令

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tests/static_check.mjs
```

从工程目录运行。浏览器步骤见 `manual_browser_runbook.md`。
