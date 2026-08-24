# LIFEOS-P3-111 Evidence Manifest

## 身份与边界

- 任务：`LIFEOS-P3-111`；ABF：`ABF-P3-111-v1`，SHA-256 `24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395`。
- 候选输入：P3-106 rework-1 Manifest，SHA-256 `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe`；允许变化仅限 P3-111 工程、Evidence 和交付物。
- Evidence payload 不含用户原文、client key、完整 DB 或 DB 内容。实际专用目录仅保留 metadata：目录为真实目录、`capture.sqlite` 为普通文件、无 sidecar；metadata 工具不读取 DB 内容，不执行 raw SQL／shell／process。
- 用户在 native app 内主动保存的 2 条低敏感记录按授权保留在 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2/capture.sqlite`。本任务不清理、删除、复制或读取该 DB。

## 可复跑命令

在仓库根目录执行。前四项只使用隔离 candidate 与固定非敏感夹具；不得以它们替换用户的实际输入。

```bash
python3 lifeos/engineering/LIFEOS-P3-111/tools/run_fixed_selfcheck.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/run_bundle.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/build_payload_manifest.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/run_disposable_mutations.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/final_cleanup.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/build_payload_manifest.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/write_semantic_result.py
python3 lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py
```

native UI 复跑只能在用户另行实际操作时进行，且不得捕获其原文。动态闭环逐项表见 `UI_DYNAMIC_EVIDENCE_CLOSURE.md`。

## 语义与篡改验证

- `PAYLOAD_MANIFEST.json` 对 payload 中每个文件给出 bytes 与 SHA-256；它自身、本文件和 `semantic-verifier-result.json` 排除在 payload 外，以避免自引用。
- `semantic_verifier.py` 对 missing、extra、bytes/hash drift、关键测试语义及动态闭环表重新判断。
- `run_disposable_mutations.py` 使用完整 Evidence 的实际 disposable 副本，分别变异缺文件、hash、清理残留、negative 退出码、DB 计数和 geometry；六类均须由同一 verifier 检出，并在结束时移除 disposable 副本。

最终 payload SHA-256：`0c8f1fcea3fb756c1974243d3d20315854ceada28fd73bd4c65652d3afd3bb7b`；最终 verifier SHA-256：`52a75c16a8b56d2fa03340d13b5a581d31d7982ce7263c4e02aaa7827546fb2a`；mutation 结果 SHA-256：`c5df02374827f1ca2dd21076fdeb4f5b8d123df43e45763a824e4c462003390c`。如 payload 文件变化，以重新生成的 `PAYLOAD_MANIFEST.json` 为准。
