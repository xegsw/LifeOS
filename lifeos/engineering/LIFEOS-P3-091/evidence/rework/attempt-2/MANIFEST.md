# LIFEOS-P3-091 attempt-2 Rework Evidence Manifest

## 范围与预检

- D-0370 授权范围：只补关闭重开与实际 Tab／Enter 的 Chrome 动态 Evidence；未修改 UI、初始 Evidence、P3-089／P3-090 或项目账本。
- Chrome：`com.google.Chrome` 由 Computer Use `@oai/sky` 控制；新标签页直接打开 `file:///private/tmp/lifeos-p3-091-rework-attempt-2-app/default-recovery.html`。
- 干净副本静态 runner：97 PASS / 0 FAIL；attempt-2 闭环 runner：2 PASS / 0 FAIL。
- 计数：P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0。

## 复跑

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  lifeos/engineering/LIFEOS-P3-091/tests/rework_closure_check.mjs \
  lifeos/engineering/LIFEOS-P3-091
```

## 非自指 SHA-256

| 文件 | SHA-256 |
|---|---|
| `tests/rework_closure_check.mjs` | `9104bfc60f5c779fccac9a285206b294952f4cb0c14da69000f12ef285bb3661` |
| `dynamic_evidence_closure.md` | `8ca8a37a69726ecfa6f7e2c7ad221b67491a836ee77bd9e59074c7e64d0d4975` |
| `structured_results.json` | `a5e69273f6b42508fdca1cbf5386598c40d0223437d9488a1726c21c1ed6d4bc` |
| `operation_log.md` | `9a820a585948fa7252f4d4459e31344168f03968d5095442f262d79bb5676c88` |
| `01-confirmed-before-close.jpeg` | `c19cbb26e0477f11cf7b03226915272fa4d864baccf2a85b34b3d64af78c3559` |
| `02-reopened-cleared.jpeg` | `ad7bb860324db8f30093130e2b62631400856e39d7a7d4e33f7da68d44bc5be6` |
| `03-tab-skip-link-focus.jpeg` | `848f2b056488b74e65c05d22f676ccbd591875b52214379e63ac9b1074761282` |
| `04-enter-skip-link.jpeg` | `8194ae6a9b6de108d14f3f95a651b79d8b8380bbf6a95eaf774f9255ac01b47c` |

此 Manifest 不为自身生成自指 hash。初始 `evidence/MANIFEST.md` 与初始 Evidence 保持只读。
