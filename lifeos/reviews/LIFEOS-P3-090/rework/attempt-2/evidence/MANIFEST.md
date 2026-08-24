# LIFEOS-P3-090 attempt-2 Independent Evidence Manifest

## 隔离、预检与结果

- 原 P3-090 `evidence/` 与 `independent_review.md` 仅只读保留；本轮新增目录为 `rework/attempt-2/`。
- task-local 副本：`/private/tmp/lifeos-p3-090-attempt-2/app`。P3-089 五项 source before／after SHA-256 一致；P3-079、P3-087、P3-088 指定历史 hash 未变，逐项结果见 `independent_static_results.json`。
- Chrome：Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 新标签页直接加载 task-local `file:`；预检通过后才执行动态矩阵。未使用 HTTP、网络、CDP、命令行浏览器、持久化或策略绕过。
- 独立静态：48 PASS / 0 FAIL。Chrome 动态／视觉：15 PASS / 0 FAIL。P0/P1/P2/Unknown/Not Implemented：0/0/0/0/0。

## 复跑

```sh
python3 lifeos/reviews/LIFEOS-P3-090/rework/attempt-2/evidence/independent_static_runner.py \
  /private/tmp/lifeos-p3-090-attempt-2/app \
  lifeos/reviews/LIFEOS-P3-090/rework/attempt-2/evidence/independent_static_results.json
```

动态复跑只可用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 新标签页打开新的 task-local `file:` 副本。

## Evidence 文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `01-preflight-wide.jpeg` | `4d21cf0252f387fb0da38bd9b6fd73847e650629466dfa0ad1a92d4db2fcc60b` |
| `02-keyboard-focus.jpeg` | `5e90dde54c0b5ebf015b5292253fea361fd4e3b356672d40c90ca0461be7aef0` |
| `03-confirmed-recovery.jpeg` | `80bb6a2bc16e0e2dc70cbce2f863e53a0d53e8a40071293c9d812929f84525e2` |
| `04-revoked-cleared.jpeg` | `366c562c9e0a1293523a8899570425bff21931eb266bdcd4d2110002753de712` |
| `05-failure-cleared.jpeg` | `a0537135a7798c586e8c3b94aa22369ebf3529b5a45e6b6ba2d6b1530031676e` |
| `06-no-suggestion.jpeg` | `7c30c77de0ed9a5a548660ea7f330ffa6e5148d81639bfed7bf990b838bf61a4` |
| `07-restricted-offline.jpeg` | `3c02e7cc70d0fa5225359fa61e63effdc551e4a28d6e32c970547838f4ddc4f8` |
| `08-refresh-cleared.jpeg` | `5cc0c501db5b18ec7601d1886d9e706e1aba3674ed0d286f35da053d50d3aa85` |
| `09-zoom-responsive.jpeg` | `9c6fd353f698fced359a79ec9c74950666049ea8e9edcecf97a0cb6c24aae570` |
| `10-close-reopen-cleared.jpeg` | `4d21cf0252f387fb0da38bd9b6fd73847e650629466dfa0ad1a92d4db2fcc60b` |
| `11-repeat-confirmation.jpeg` | `b4dcb4ec668a571bae83e9f30bc3db82a4e840a09540c6bef7ca9c4d5b578604` |
| `independent_static_runner.py` | `072532d3109f9921b2b61becc927b85f25aece018f00fceff6f00915ee45c74a` |
| `independent_static_results.json` | `d533fe4bbe04829f236e304378710062ce11b1ece2116021672538df9ed50f4c` |
| `dynamic_results.json` | `b22eeee087511e38f0038a9df1a703f0475c19e078f365213010487faa8b99a7` |
| `operation_log.md` | `7a6cb5c3385fb89133597e04a5b748e58560d211f32b7a6964e39253d3636ec1` |
| `acceptance_matrix.md` | `687c736751a6a9eb20ad0cc51b75c4645b8e2af2da4eeb43f6912476db292d8d` |

`MANIFEST.md` 为 hash 清单本身，故不对自身生成不可稳定的自指 hash；其当前 SHA-256 由提交前的复算命令单独记录在本轮交付验证输出中。
