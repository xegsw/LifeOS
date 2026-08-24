# LIFEOS-P3-094 Rework attempt-7

本轮只修复 render 无法确认 DB 内容有效时的旧页面生命周期：空、损坏、不可读或查询失败 DB 必须先让唯一 task-local `today.html` 不可展示，再返回失败；render 不修改 SQLite 状态。合法 render、原子发布失败保留当前有效页面和 clear 先失效后清理语义保持不变。

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/scripts/run_attempt_7.py
```

runner 仅在 `/private/tmp` 创建固定非敏感夹具，使用 `-B`，不写用户缓存目录；提交 Evidence 位于本目录 `evidence/`。PM 复跑应使用 `--evidence-dir` 指向新的 `/private/tmp` 目录，避免覆盖提交 Evidence。
