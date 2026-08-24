# LIFEOS-P3-087 Evidence Manifest

## 授权、隔离与范围

- 执行授权：用户于 2026-08-21 将 `lifeos/tasks/LIFEOS-P3-087_three_frozen_today_pages_responsive_accessibility_controlled_ui_capability_package.md` 投递至本新建隔离 Codex 工程会话。
- 仅写入 `lifeos/engineering/LIFEOS-P3-087/` 与任务指定交付物；P3-085、P3-086、冻结设计输入与项目账本未修改。
- task-local 副本：`/private/tmp/lifeos-p3-087.Yvv65U/app`；Chrome 入口：`file:///private/tmp/lifeos-p3-087.Yvv65U/app/default-recovery.html`。
- 动态／视觉操作只使用 Google Chrome（`com.google.Chrome`）和 Computer Use `@oai/sky`；无 HTTP、网络、CDP、命令行浏览器、浏览器持久化或策略绕过。

## 工程 hash

| 文件 | SHA-256 |
|---|---|
| `default-recovery.html` | `eaea4933dc6166590129331734f3d947483e1a6ded39c28df28597692492b95d` |
| `no-reliable-suggestion.html` | `f9c47ca754b91f1d924b3f5b7fb4e9b5d4ba1b4ba98693d5cd7d2358af43f643` |
| `restricted-offline.html` | `f246e2607cfc85bc01a14274358bb917f25cf800fcad6d67f17dbd0d79a58a0b` |
| `app.js` | `fa50eb0e7bfa177a3ba2c6e97ec1185370506e84cc2f1d01434ac9d5ea090d0c` |
| `styles.css` | `3313d07eff663e74f95897d7d05130ac7a25dee3455c38e4b772cc79f68a855c` |
| `tests/static_check.mjs` | `beffb4e75bbafe2a97bab1448bd48d7f7d28a2070d798f27a270f7b319aa0ed5` |
| `evidence/static_results.json` | `b850d18937cc7b9846205300c348f5d5c7fe0150f9117f6c72470e06cbfaf296` |
| `evidence/dynamic_results.json` | `1dc205c95c111030df52e9fbdd546409413f9ae4bd19a01920b9bcdd3cb0c464` |

## 动态快照 hash

| 文件 | SHA-256 |
|---|---|
| `01-preflight-wide.png` | `bd8a768219de1fd101b001e21abcedae621217df5dc5a156a4163a488c7a84c1` |
| `02-keyboard-no-suggestion.png` | `fabff0bd32b290cb4e6f9847758cf42c83d1dee0f04f891774f684f3228baea3` |
| `03-keyboard-controlled-path.png` | `32937661637ca4ec64ac82fc1e4621f66aed53ad9bcc59b7b92c9b3539bebafd` |
| `04-confirmed.png` | `74372ba40f505f2896cdd7b09f8dda371e25ce7ec9d1b0aa669ae243c25a40ab` |
| `05-failure-cleared.png` | `67b627f5e08cb482e5f3f11ac45f74af83db022469abc6a341bbf5735f78464f` |
| `06-narrow-responsive.png` | `5f48e17c4946d1be78e718e55844d1ef401ee8753871272d45b2d2e60041f0ae` |
| `07-extra-narrow-responsive.png` | `43dfdd2dd6d7360520daafcda59cfb60c1fe489f42d9a85e2da25351d3b79db0` |
| `08-refresh-cleared.png` | `f59091446fd1047a939a2e9bf6c9e194989415bcb73764821388979c335431a6` |
| `09-close-reopen-cleared.png` | `1a781b27aba8a9e926cbed6ab6fb3ac9639f5edb47d9832e360f3ab88e0ee3cc` |

## 结果

- 静态 runner：61 PASS / 0 FAIL。
- Chrome 动态／视觉：12 PASS / 0 FAIL。
- 自检计数：P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。
- 历史只读 P3-085 五项 hash 均与 P3-086 attempt-3 Manifest 一致：`98241ff3…`、`2d50aa2f…`、`036d061f…`、`f1e05252…`、`e6e91c2c…`。

## 可复跑入口

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node lifeos/engineering/LIFEOS-P3-087/tests/static_check.mjs lifeos/engineering/LIFEOS-P3-087
```

动态复跑只可由 Google Chrome（`com.google.Chrome`）通过 Computer Use `@oai/sky` 在新标签页直接打开新的 task-local `file:` 副本；不得使用 HTTP、网络、CDP、命令行浏览器或其他浏览器。
