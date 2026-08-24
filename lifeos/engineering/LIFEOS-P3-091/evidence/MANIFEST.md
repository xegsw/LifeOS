# LIFEOS-P3-091 Evidence Manifest

## 授权、隔离与预检

- 授权证据：用户于 2026-08-21 投递 `lifeos/tasks/LIFEOS-P3-091_three_frozen_today_pages_content_identity_and_boundary_clarity_controlled_ui_capability_package.md` 至新建隔离 Codex 工程会话。
- 写入范围：仅 `lifeos/engineering/LIFEOS-P3-091/` 与指定交付物；P3-089、P3-090、冻结设计与项目账本未改写。
- 干净副本：`/private/tmp/lifeos-p3-091-clean-app`；Chrome 预检入口：`file:///private/tmp/lifeos-p3-091-clean-app/default-recovery.html`。
- 预检：Google Chrome (`com.google.Chrome`) 由 Computer Use `@oai/sky` 在新标签页直接加载成功；未使用 HTTP、网络、CDP、命令行浏览器、浏览器持久化或策略绕过。

## 结果与复跑

- 当前工程静态 runner：97 PASS / 0 FAIL。
- 干净副本静态 runner：97 PASS / 0 FAIL。
- Chrome 动态／视觉矩阵：15 PASS / 0 FAIL。
- P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  lifeos/engineering/LIFEOS-P3-091/tests/static_check.mjs \
  lifeos/engineering/LIFEOS-P3-091
```

动态复跑仅可由 Google Chrome (`com.google.Chrome`) 通过 Computer Use `@oai/sky` 在新的 task-local `file:` 副本中执行。

## 非自指 SHA-256

| 文件 | SHA-256 |
|---|---|
| `default-recovery.html` | `e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b` |
| `no-reliable-suggestion.html` | `e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793` |
| `restricted-offline.html` | `b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e` |
| `styles.css` | `35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91` |
| `app.js` | `a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac` |
| `tests/static_check.mjs` | `93bd7f0fbdcfb76a605ed3f6f22e3955a866b034a2f374c082dcd4bd2ad3f755` |
| `evidence/static_results.json` | `ddd909fac748781be8b739644cbc009fa0e547723dbafa6b6c54b1a251b09f67` |
| `evidence/dynamic_results.json` | `3e5c59e08a5c16386dc961a43205b51a7444ae9aef87d0aa819d6d4f10aee74e` |
| `evidence/operation_log.md` | `ff7b3a53f03ad267a95927a98fc04ce8a282b76749fd1a0d0fee45fde2ef3644` |
| `evidence/acceptance_matrix.md` | `57354a6af16b376f6cc619fa4d63f4e0887e50a24ec3c2a4686a079653aee299` |
| `evidence/historical_input_hashes.txt` | `35a383529fbede77214d086c4e896fdfe43589da245d5a94b0731f8bf55f4fee` |
| `evidence/01-preflight-default.jpeg` | `ad7bb860324db8f30093130e2b62631400856e39d7a7d4e33f7da68d44bc5be6` |
| `evidence/02-confirmed-recovery.jpeg` | `c19cbb26e0477f11cf7b03226915272fa4d864baccf2a85b34b3d64af78c3559` |
| `evidence/03-failure-cleared.jpeg` | `2cc414c63d080f1339b6dee4506a98dcc93dbbb6ff4912defb02134af65d2701` |
| `evidence/04-restricted-offline.jpeg` | `954b13c978d6e62af2ff5257a1eb01dea8b21f95db96cf9208e160b8138d6649` |
| `evidence/05-narrow-responsive.jpeg` | `27a021a9eb5c795934e4b6270380da130b9514b1a5e101ec065e240ec0e3baa6` |

`MANIFEST.md` 自身不产生自指 hash。P3-089 与 P3-090 attempt-2 只读输入的复算 hash 见 `historical_input_hashes.txt`。
