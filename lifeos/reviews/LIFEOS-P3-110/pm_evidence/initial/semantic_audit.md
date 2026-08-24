# LIFEOS-P3-110 PM Semantic Evidence Audit

- 时间：2026-08-24（Asia/Shanghai）
- 范围：只读核对专项 Evidence；未修改候选、专项 Review 或专项 Evidence。
- Frozen ABF：`ABF-P3-110-v1`，SHA-256 `8324c9e847bafdfeebb022affffb372c0ce032a326009990bb3740e0310f1570`。

## Manifest 复算

- `PAYLOAD_MANIFEST.json`：110 项。
- PM 逐项复算全部 110 个文件的 SHA-256 与 bytes：110/110 匹配。
- Evidence 目录除顶层 `MANIFEST.md` 与 `PAYLOAD_MANIFEST.json` 外共有 110 个文件；missing=0，extra=0。
- `PAYLOAD_MANIFEST.json` SHA-256：`eda0616c1195a7f859522aced3ea6e1154f8e73efc90269ae89bf29583c9139d`。
- 顶层 `MANIFEST.md` SHA-256：`93fd48865a7f61438d2a26f1f945c66bc75428b7f6afb4825244c93b5e5556d8`。

## 只读复跑

PM 直接执行 `semantic_verifier.py`，未写入专项 Evidence：

| 入口 | exit |
|---|---:|
| baseline | 0 |
| `--mutation missing_file` | 1 |
| `--mutation hash_changed` | 1 |
| `--mutation cleanup_residue` | 1 |
| `--mutation negative_exit_zero` | 1 |
| `--mutation db_count_wrong` | 1 |
| `--mutation geometry_wrong` | 1 |

这只证明参数分支返回预期退出码，不证明 verifier 能发现真实 disposable Evidence 变异。

## Finding：PM-P3-110-EV-01

严重级别：P0；矩阵：ABF-I-12、ABF-I-13、ABF-M-016；L1：L1-7、L1-10。

1. `semantic_verifier.py` 没有读取 `PAYLOAD_MANIFEST.json`，没有复算任何 payload 文件 SHA-256／bytes，也没有比较 Manifest 的 missing／extra；因此真实 payload hash 即使漂移，baseline verifier 仍可能返回 0。
2. verifier 未解析 `authorization.json`、`read_order.json`、`copy-inventory.json`、`unit-path-ledger.json`、`visual/fixed-comparison.json`、`UI_DYNAMIC_EVIDENCE_CLOSURE.md`、a11y transcript、actual-app raw logs 或逐项 negative raw logs。对视觉、键盘、content/schema tamper 只检查四个路径是否为文件，不能从 raw Evidence 重算对应语义。
3. 六个 mutation 不是 disposable payload mutation。`hash_changed`、`missing_file`、`cleanup_residue` 直接把局部布尔值设为 false；其余三项只修改已载入对象。`mutation_runner.py` 仅传入参数，没有复制并实际改变一个 Evidence payload 后运行同一个无特殊分支的 verifier。

结论：专项文件完整性可复算，且已读取的结构化记录未显示候选缺陷；但 M-016 的语义 verifier／mutation 完成定义未实现，专项 Pass 不成立。ABF、候选、授权和目录均无需改变，可按同一 P3-110 记录正式 Rework 1/2。
