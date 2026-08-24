# LIFEOS-P3-094 Rework attempt-4

本轮只修复清理后旧 `today.html` 仍可展示的 P1。运行时现在先精确失效内部展示工件，再清空 SQLite；页面失效失败时数据库保持不变。

复跑（只使用固定非敏感测试文本）：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/scripts/run_attempt_4.py
```

如需避免覆盖本轮提交 Evidence，可把复跑结果写入另一个 task-local 目录：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/scripts/run_attempt_4.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-4-review-evidence
```

runner 在干净临时副本执行并用 `finally` 精确移除本轮 SQLite、HTML、复制源码和缓存。不得将 Evidence 中固定测试文本替换为真实用户文本。
