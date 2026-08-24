# LIFEOS-P3-086 独立复评 Evidence Manifest

## 授权、隔离与范围

- 授权证据：用户于 2026-08-21 CST 将 `lifeos/tasks/LIFEOS-P3-086_three_frozen_today_pages_multipage_local_ui_shell_fresh_isolated_independent_re_review.md` 投递至本新建 Codex 独立安全／体验评审会话。
- 只读对象：`lifeos/engineering/LIFEOS-P3-085/`、P3-085 交付物／PM Review／PM Evidence 与 P3-082／084 Manifest。未修改被评审工程、历史 Evidence／Review 或项目账本。
- task-local 干净副本：`/private/tmp/lifeos-p3-086.amAXQ3/app`；仅含三页、`app.js` 与 `styles.css`。
- 未启动 HTTP 服务、未访问网络、未使用 CDP、命令行浏览器、其他浏览器、持久化或安全策略绕过；仅尝试任务指定的 Google Chrome 新标签页直接 `file:` 预检。

## 被评审工程与历史只读 hash

| 文件 | SHA-256 | 结论 |
|---|---|---|
| `P3-085/default-recovery.html` | `98241ff3ae39bd0d9b562f72700a6b7cee66dd28fb252827558182b5a6f18616` | 与工程 Manifest 一致，副本 before／after 一致 |
| `P3-085/no-reliable-suggestion.html` | `2d50aa2f26a0c66647d385d9426386e01081d3f964919bc1588707611cae0577` | 与工程 Manifest 一致，副本 before／after 一致 |
| `P3-085/restricted-offline.html` | `036d061f605367ef4087ee3ea49f2ace1bd69203370b0e4a8135160f6689ecef` | 与工程 Manifest 一致，副本 before／after 一致 |
| `P3-085/app.js` | `f1e0525285da80001fcc9e3ac305c3577c169bd5216b305666e90be3bc4f89e2` | 与工程 Manifest 一致，副本 before／after 一致 |
| `P3-085/styles.css` | `e6e91c2ca590299a1307118f8f5fff467254ecb2c0bfa36acb623b25f6bd9774` | 与工程 Manifest 一致，副本 before／after 一致 |
| `P3-082/index.html` | `eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722` | 与 P3-082／085 Manifest 一致 |
| `P3-082/app.js` | `784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d` | 与 P3-082／085 Manifest 一致 |
| `P3-082/styles.css` | `7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2` | 与 P3-082／085 Manifest 一致 |

## 独立 Evidence 文件

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `independent_static_runner.mjs` | `745ff2dcc8b4bdd7c4b7821ed10f55aba7091e302eb585af28ddff96cd5083ff` | 新写的 29 项独立静态验证入口 |
| `independent_results.json` | `70443446be385e3f2879795c2f77714da0db638c64438c3d4da4bcf7f7694dee` | 逐项结构化结果，29 PASS / 0 FAIL |
| `operation_log.md` | `b15663905c7b2d9831591ae2510dc922aea51f116134b3d27361559e9c1a3a56` | 隔离、Chrome 预检与动态缺口记录 |
| `acceptance_matrix.md` | `eba03b7bd01ecb5c1bd10e7e7f1aefc4b1393f0d36e4c40724a22f5ee5470d99` | 任务验收映射 |

## 结果、复跑与缺口

- 静态：29 PASS / 0 FAIL。runner 不导入、调用或复制任何执行侧或 P3-082／084 runner。
- Chrome `file:` 预检：Not Implemented。当前浏览器控制安全策略在正常导航前阻止指定 `file:` URL，且明确禁止任何替代或绕过。未发生两次 Chrome 正常加载失败，故本 Evidence 不将其写为已满足任务卡的候选 Blocked 双次条件。
- 动态／视觉：Not Implemented（默认页、两个独立页、导航、确认、失败披露、刷新、关闭重开及视觉记录）。不得由静态结果或 P3-085 PM 动态 Evidence 替代。
- 计数：P0=0；P1=0；P2=0；Unknown=0；Not Implemented=1（影响完成定义的独立动态／视觉矩阵）。
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-086_LIFEOS-P3-086_three_frozen_today_pages_multipage_local_ui_shell_fresh_isolated_independent_re_review_local_precheck.md`，结果为 Skipped / Local Model Unavailable；未参与独立评审结论。

复跑静态入口：

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node lifeos/reviews/LIFEOS-P3-086/evidence/independent_static_runner.mjs /private/tmp/lifeos-p3-086.amAXQ3/app
```

动态复跑仅可由 Google Chrome（`com.google.Chrome`）新标签页直接打开一个新的 task-local `file:` 副本；不得使用 HTTP、网络、CDP、命令行浏览器、其他浏览器或策略绕过。
