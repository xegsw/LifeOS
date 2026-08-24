# LIFEOS-P3-085 Evidence Manifest

## 授权与边界

- 任务卡：`lifeos/tasks/LIFEOS-P3-085_three_frozen_today_pages_multipage_local_ui_shell_controlled_capability_package.md`。
- 授权证据：用户于 2026-08-21 20:53:40 CST 将该任务卡路径投递至新建隔离 Codex 工程执行会话。
- 写入范围：仅 `lifeos/engineering/LIFEOS-P3-085/`、本任务交付物与本地预检报告；未修改项目账本、冻结原型、P3-082／084 工程、历史 Review 或 Evidence。
- 能力边界：无依赖静态页面，使用相对本地 CSS／JS；没有服务、网络、浏览器持久化、真实文件、DB、Vault、Tauri/IPC、导出、同步、模型或第三方。

## 当前工程 SHA-256

| 文件 | SHA-256 |
|---|---|
| `default-recovery.html` | `98241ff3ae39bd0d9b562f72700a6b7cee66dd28fb252827558182b5a6f18616` |
| `no-reliable-suggestion.html` | `2d50aa2f26a0c66647d385d9426386e01081d3f964919bc1588707611cae0577` |
| `restricted-offline.html` | `036d061f605367ef4087ee3ea49f2ace1bd69203370b0e4a8135160f6689ecef` |
| `app.js` | `f1e0525285da80001fcc9e3ac305c3577c169bd5216b305666e90be3bc4f89e2` |
| `styles.css` | `e6e91c2ca590299a1307118f8f5fff467254ecb2c0bfa36acb623b25f6bd9774` |
| `tests/static_check.mjs` | `8e0d972c26ed0a00ee2ab99c6b1b2a67e88be7853ffcad1f87ad68b012904b51` |
| `README.md` | `d51be763b8567d3a4b5be2cd7d2ace13652c5d2f79f0c33e8d9e9db77c8f6b56` |
| `evidence/static_check_results.json` | `88e91cf533adef872a53f213f70a9ac676d3f0d5b3f22b7ba8bdf0984051d561` |

## 历史只读资产核对

| 历史文件 | 本次复算 SHA-256 | 期望值／结论 |
|---|---|---|
| `lifeos/engineering/LIFEOS-P3-082/index.html` | `eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722` | 与 P3-082／P3-084 Manifest 一致，Pass |
| `lifeos/engineering/LIFEOS-P3-082/app.js` | `784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d` | 与 P3-082／P3-084 Manifest 一致，Pass |
| `lifeos/engineering/LIFEOS-P3-082/styles.css` | `7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2` | 与 P3-082／P3-084 Manifest 一致，Pass |

## 自检与复跑

- 静态 runner：37 PASS / 0 FAIL；`tests/static_check.mjs` 不导入、调用或复制 P3-082／084 runner。
- 干净副本静态复跑：37 PASS / 0 FAIL；副本位置见 `temp_copy_path.txt`。
- 浏览器 `file:` 动态演练：Not Implemented。受控浏览器的 URL 策略在首次导航前阻断，且禁止切换或规避；完整记录在 `browser_blocker.md`。
- 本地预检：Skipped / Local Model Unavailable；`lifeos/local_prechecks/LIFEOS-P3-085_LIFEOS-P3-085_three_frozen_today_pages_multipage_local_ui_shell_controlled_capability_package_local_precheck.md`。错误为本地模型地址调用被运行环境拒绝；该报告未参与任何通过结论。
- 包内自检结论：**Not Pass**。P0=0；P1=0；P2=0；Unknown=0；Not Implemented=1（任务卡要求的动态 `file:` 演练、刷新／关闭重开和视觉记录）。

从工程目录复跑静态核验：

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tests/static_check.mjs
```

动态复跑只可在任务允许、可直接访问 `file:` 的合规图形浏览器中执行；不得启动 HTTP 服务、使用网络、CDP、命令行浏览器或绕过浏览器策略。
