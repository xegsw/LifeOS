# LIFEOS-P3-089 Evidence Manifest

## 授权、隔离与关闭态

- 授权证据：用户于 2026-08-21 将 `lifeos/tasks/LIFEOS-P3-089_three_frozen_today_pages_synthetic_lifecycle_ui_integration_controlled_capability_package.md` 投递至新建隔离 Codex 工程会话。
- 写入范围：仅 `lifeos/engineering/LIFEOS-P3-089/` 与任务指定交付物；P3-079、P3-087、P3-088、冻结设计与项目账本未改写。
- 干净副本：`/private/tmp/lifeos-p3-089.rcH3wY/app`；预检入口：`file:///private/tmp/lifeos-p3-089.rcH3wY/app/default-recovery.html`。
- 动态验证：Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 的新标签页预检通过后执行。无 HTTP、网络、CDP、命令行浏览器、浏览器持久化或安全策略绕过。

## 结果

- 当前工程静态 runner：87 PASS / 0 FAIL。
- 干净 task-local 副本静态 runner：87 PASS / 0 FAIL。
- Chrome 动态／视觉矩阵：15 PASS / 0 FAIL。
- P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。

## 可复跑入口

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  lifeos/engineering/LIFEOS-P3-089/tests/static_check.mjs \
  lifeos/engineering/LIFEOS-P3-089
```

动态复跑仅可由 Google Chrome（`com.google.Chrome`）通过 Computer Use `@oai/sky` 在新的 task-local `file:` 副本中执行。

## 关键文件 hash

| 文件 | SHA-256 |
|---|---|
| `default-recovery.html` | `c8e6e130bdb26962f6663afc56529fecf2c3501f643633655837daa433ee16b4` |
| `no-reliable-suggestion.html` | `c38a3d8fe35bb00d5d13ca1fa1967daa813c1b8af083e75de3fb9cb593d0520d` |
| `restricted-offline.html` | `0965726629e105087b94680476f18e5a35f361f046be23ccbc468850ac84085f` |
| `styles.css` | `052600b12672a7d9bf255c130edbb4eb5d6d3d3bfee3a64be403e24e74dfe94a` |
| `app.js` | `88dc10ffa945d12baf42b771e4c6fddef791a5f1305e9f1d349161977684fe1a` |
| `tests/static_check.mjs` | `0477a2fe96d1e19a6b10468c73d1cd1db93f296f92d521e48729aa7d21e9b725` |
| `evidence/static_results.json` | `c155e7cd7094060d5e2d2bcc987cf7dfc880a66da1452d81103c433cd1b78684` |
| `evidence/dynamic_results.json` | `0eb78497f3263d4a5ff637dbbe9c376c27a32ec5ddb76f278bfa85cb6f82cf60` |

`historical_input_hashes.txt` 保存 P3-079、P3-087 与 P3-088 指定只读输入的 SHA-256；它们仅被读取和哈希，未被覆盖。逐项标准对应关系见 `acceptance_matrix.md`，动态步骤见 `operation_log.md`。
