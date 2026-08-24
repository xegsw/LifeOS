# LIFEOS-P3-094 Rework attempt-5

本轮仅收紧 task-local 删除目标边界。运行时只可删除数据库同目录的精确普通文件 `today.html`；CLI 已移除 `clear --output`，API 任何调用方目标参数均在变更前拒绝。符号链接、目录、特殊文件和无法确认的目标同样 fail closed。

复跑（只使用固定非敏感测试文本和哨兵）：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/scripts/run_attempt_5.py
```

外置复跑 Evidence：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/scripts/run_attempt_5.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-5-review-evidence
```

runner 在 `/private/tmp` 干净副本运行，并在 `finally` 精确清理本轮 DB、HTML、哨兵、FIFO、链接、源码副本和缓存。
