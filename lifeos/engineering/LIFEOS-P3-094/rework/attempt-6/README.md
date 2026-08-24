# LIFEOS-P3-094 Rework attempt-6

本轮仅修复 render／clear 的 task-local 路径边界：唯一内部 `today.html`、完整无链接目录组件链、DB 与最终页面普通文件类型、失败前零变更。固定非敏感夹具在 `/private/tmp` 干净副本中运行，并在 `finally` 精确清理。

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/scripts/run_attempt_6.py
```

提交 Evidence 位于 `evidence/`；PM 复跑应使用 `--evidence-dir` 指向新的 `/private/tmp` 目录，避免覆盖提交 Evidence。
