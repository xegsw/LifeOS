# LIFEOS-P3-111 Rework 1/2 Evidence Manifest

## 范围与只读保全

- Rework 原因：PM finding `PM-CE-001`（L1-7、L1-10、ABF-I-11、ABF-M-011）。初次 verifier 在绝对路径包含 `/disposable/` 时会错误排除完整 payload，导致未篡改副本也失败。
- Frozen ABF 未变化：`ABF-P3-111-v1`，SHA-256 `24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395`。用户已在 D-0451 采纳同任务 Rework 1/2，并确认原执行路由为 `gpt-5.6-terra + xhigh`。
- 仅变更 `tools/semantic_verifier.py` 与 `tools/run_disposable_mutations.py`，并生成本 `evidence/rework-1/` 与 Rework 交付物；candidate/runtime/UI 未写入。
- 初次 Engineering Evidence 保持只读：初始 `PAYLOAD_MANIFEST.json` SHA-256 `0c8f1fcea3fb756c1974243d3d20315854ceada28fd73bd4c65652d3afd3bb7b`、初始 `semantic-verifier-result.json` SHA-256 `52a75c16a8b56d2fa03340d13b5a581d31d7982ce7263c4e02aaa7827546fb2a`、初始 `mutation-results.json` SHA-256 `c5df02374827f1ca2dd21076fdeb4f5b8d123df43e45763a824e4c462003390c` 均未变。
- 本轮未执行 capture，未打开、读取、hash、复制、覆盖或清理 Pilot-2／`capture.sqlite`，未联网。

## verifier 修复与负控制

- `semantic_verifier.py` 现在先将文件转为相对所传 Evidence root 的路径，再仅排除该 root 直接子目录 `disposable/`。故传入位于任意祖先 `/disposable/noop` 下的 Evidence root 时，payload 仍被完整枚举。
- 新的 rework runner 在空 `evidence/rework-1/` 中只读复制初次 `raw/`、`screenshots/` 与动态闭环表，生成新的 manifest；它不会写入初次 Evidence，若 `rework-1/` 已存在即 fail-closed，避免覆盖。
- `disposable/noop-final` 是相同、未篡改的最终 payload 副本：exit 0，`missing=[]`、`extra=[]`、`drift_paths=[]`、`semantic_errors=[]`。

## 六类实际 disposable mutation

所有 mutation 都在 `evidence/rework-1/disposable/<name>` 的实际副本中完成，随后立即精确移除。每项以同一 verifier 运行，均 exit 1，且结果仅匹配预期原因：

| Mutation | 精确预期／实际失败原因 |
|---|---|
| `missing_file` | `missing=[raw/geometry.json]`；`unreadable:raw/geometry.json:FileNotFoundError` |
| `hash_changed` | `drift_paths=[raw/static-results.json]` |
| `cleanup_residue` | `drift_paths=[raw/cleanup.json]`；`semantic_errors=[cleanup]` |
| `negative_exit_zero` | `drift_paths=[raw/negative-results.json]`；`semantic_errors=[negative]` |
| `db_count_wrong` | `drift_paths=[raw/fixed-lifecycle.json]`；`semantic_errors=[lifecycle]` |
| `geometry_wrong` | `drift_paths=[raw/geometry.json]`；`semantic_errors=[geometry]` |

完整逐项结构化输出在 `mutation-results.json`（source payload）及 `semantic-verifier-result.json`（final payload 的未篡改控制与六项复验）。临时 `disposable/` 最终不存在。

## 最终重算与复跑

- 最终 payload：38 个文件；`PAYLOAD_MANIFEST.json` SHA-256 `16dbe0f05d825bca4f7e08f723dd5c3b7b90606bad0a4af1d9feaaea34641d22`。
- 最终 semantic result SHA-256：`d3afbc9e13a1a3bfc3b81b83cc878dfa3a2f2bb228ec6a4088b3fa8f5443f011`；mutation contract SHA-256：`1d9594b50a9570bfb536009cabc332f6778d046295803e5031cd7ef0f0595d8c`。
- 最终 root verifier 为 PASS，`missing`、`extra`、`hash_or_bytes_drift` 和 `semantic_errors` 均为空。

```bash
python3 lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py \
  lifeos/engineering/LIFEOS-P3-111/evidence/rework-1
```

`run_disposable_mutations.py` 只在全新空的 `evidence/rework-1/` 上创建 Evidence；现有 Rework Evidence 必须保留，若要从零重建须在另一次明确授权的干净副本中执行，不得覆盖本目录。
