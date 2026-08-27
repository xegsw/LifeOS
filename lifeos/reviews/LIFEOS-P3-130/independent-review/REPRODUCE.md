# P3-130 独立复评复跑

当前结果可只读复核：

```bash
cd /Users/xxe/Documents/No.2
python3 -B lifeos/reviews/LIFEOS-P3-130/independent-review/review_p3_130.py
python3 -B lifeos/reviews/LIFEOS-P3-130/independent-review/verify_review.py
```

第二条命令要求唯一临时根保持 absent，并从本目录原始 Evidence 重算 22 个检查。

要从零重新取得 actual‑Tauri Evidence，先确认 `/private/tmp/lifeos-p3-130-context-recovery-v1` 不存在，再仅创建该确切根及 task-local cache/runtime 子目录，使用：

```bash
cd /Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-130/candidate
LIFEOS_RUNTIME_ROOT=/private/tmp/lifeos-p3-130-context-recovery-v1/runtime-confirm \
CARGO_NET_OFFLINE=true \
CARGO_TARGET_DIR=/private/tmp/lifeos-p3-130-context-recovery-v1/build-cache \
TMPDIR=/private/tmp/lifeos-p3-130-context-recovery-v1/tmp \
CLANG_MODULE_CACHE_PATH=/private/tmp/lifeos-p3-130-context-recovery-v1/clang-cache \
SWIFT_MODULECACHE_PATH=/private/tmp/lifeos-p3-130-context-recovery-v1/swift-cache \
/Users/xxe/.cargo/bin/cargo tauri build --debug --bundles app --no-sign
```

随后通过 macOS 正常 App 启动路径和 Computer Use 操作固定 UI（empty → capture → repeat → confirm → close/reopen；另根 reject、三类 mutation、三档视口）。不得使用 Engineering runner、历史 runtime root、网络或第六 IPC。完成后仅删除确切临时根并验证 absent。
