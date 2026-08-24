# LIFEOS-P3-110 Evidence Manifest

这是顶层非自指索引；它不对自身哈希，也不把 Markdown 结论当作通过输入。

| 顺序 | 产物 | SHA-256 | 作用 |
|---|---|---|---|
| 1 | `PAYLOAD_MANIFEST.json` | `eda0616c1195a7f859522aced3ea6e1154f8e73efc90269ae89bf29583c9139d` | 非自指 payload 文件清单与 hash |
| 2 | `semantic_verifier.py` → `semantic-verifier-result.json` | `cc411aa77802b5bc362eee960c2d939fff8f2913f0f3349abc71196a7e72eab0` | 从 raw JSON/log/geometry/cleanup 重算；真 payload exit 0 / `passed: true` |
| 3 | `mutation_runner.py` → `mutation-results.json` | `8ca5d7a6b92e8a37581ac480a8dcb8959d081596ff681d791c1ef47e00b3ebf4` | 六类 disposable mutation 均 exit 1 |
| 4 | `cleanup.json` | payload 内可复算 | work、副本、13 个授权 fixture、三条 unit regex 残留均为 0 |

复跑顺序（工作副本已清理，均为 Evidence 目录内只读输入）：

```bash
python3 lifeos/reviews/LIFEOS-P3-110/evidence/semantic_verifier.py
python3 lifeos/reviews/LIFEOS-P3-110/evidence/mutation_runner.py
```

`PAYLOAD_MANIFEST.json` 在 semantic verifier 前生成；本顶层索引最后生成，因此不存在 self-reference。
