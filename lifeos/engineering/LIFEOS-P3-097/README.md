# LIFEOS-P3-097

有限 Stage 3、单进程、离线、task-local SQLite 完成点收口。公开 Python runtime、CLI、`saved`／`idempotent_repeat`、Schema 和业务审计语义保持不变；不接触真实个人文件、既有个人 DB、网络、Tauri/IPC、Vault、云、同步或外部用户。

```bash
mkdir -p /private/tmp/lifeos-p3-097-runtime
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-097-runtime/capture.sqlite capture --text '固定非敏感测试文本' --key first
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-097-runtime/capture.sqlite render
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-097-runtime/capture.sqlite clear --confirmation DELETE
```

capture 不再直接写 live DB。每次新捕获或幂等重复都在同目录独占 shadow DB 中完成写入、commit、候选连接 close、journal/WAL/SHM 有界清理、`quick_check`、canonical Schema、来源与完整 audit 重放验证、fsync、最终残留扫描和路径稳定性检查。新增记录还会在发布前完成旧 `today.html` 的安全失效准备。只有这些步骤全部成功后，才以固定 basename 和稳定 parent fd 执行一次 `os.replace`；这次 live DB 原子替换是唯一不可逆完成点。

原子替换失败时 live DB 保持原 bytes/hash，旧页面按固定夹具恢复，shadow 与 sidecar 被精确清理。所有 SQLite 连接在发布前关闭，因此“发布后连接 close”由结构断言证明不可达；替换完成后的路径 gate FD 释放异常只作为非权威资源释放观察，不得推翻准确的成功回执。幂等重复只在 shadow 中追加既有 `capture_repeat` 审计，页面因 capture 集合未变化而保持不变。

五个公开入口继续共用 descriptor-backed path gate：绝对且词法规范化严格等价的 `capture.sqlite`；从 `/` 逐级 `openat`/`O_NOFOLLOW`；数据库与页面只接受普通单链接文件；sidecar、链接链、特殊文件和身份漂移均 fail closed。不支持并发恶意路径替换、多进程写、崩溃恢复、网络文件系统或永久 OS 拒绝下的物理零残留承诺。

提交前自检：

```bash
python3 -B scripts/run_p3_097.py --output evidence
python3 -B scripts/run_p3_097.py --verify-only evidence
```

runner 对 ABF-M-001 至 M-017（含 M-015 的 11 个独立子测试）分别创建固定非敏感 `/private/tmp/lifeos-p3-097-*` 夹具、实际执行并记录唯一 test／fixture／execution ID、before/after、完成点 trace、失败注入、历史 hash 和非自指 Manifest；缺行、重复执行 ID、断言缺失、未列文件或 hash 漂移均非零退出。
