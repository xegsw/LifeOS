# LIFEOS-P3-110 PM Evidence Manifest｜initial

本索引不自指；PM 未覆盖专项 Evidence。

| 产物 | SHA-256 | 用途 |
|---|---|---|
| `semantic_audit.md` | `4f2e8745014226579658ee2c9d3724317702c0f582abde449221106d2e5fcc86` | 110 项 payload 独立复算、只读 verifier 复跑与 M-016 语义审计 |
| 专项 `evidence/PAYLOAD_MANIFEST.json` | `eda0616c1195a7f859522aced3ea6e1154f8e73efc90269ae89bf29583c9139d` | 专项 payload 索引 |
| 专项 `evidence/semantic_verifier.py` | `c6dcd4cf659b574b22eeff2c6fc9c430912849e82486ce164c0c8840aedf2c0b` | 被审计 verifier 源码 |
| 专项 `evidence/semantic-verifier-result.json` | `cc411aa77802b5bc362eee960c2d939fff8f2913f0f3349abc71196a7e72eab0` | 专项 baseline 结果 |
| 专项 `evidence/mutation_runner.py` | `73668ca191613ced52fc28b8035358be606c589578b31973678ce146e8c0218b` | 被审计 mutation 入口 |
| 专项 `evidence/mutation-results.json` | `8ca5d7a6b92e8a37581ac480a8dcb8959d081596ff681d791c1ef47e00b3ebf4` | 专项 mutation 结果 |
| 专项 `evidence/MANIFEST.md` | `93fd48865a7f61438d2a26f1f945c66bc75428b7f6afb4825244c93b5e5556d8` | 专项顶层非自指索引 |

结论：专项 payload 的当前文件完整性 110/110 匹配，但 semantic verifier 与 mutation 的 Frozen M-016 完成定义不成立。
