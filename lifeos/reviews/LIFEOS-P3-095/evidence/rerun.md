# LIFEOS-P3-095 独立复跑说明

在仓库根目录运行：

```bash
python3 -B lifeos/reviews/LIFEOS-P3-095/evidence/scripts/independent_runner.py prepare
```

当前 hash 的预期结果为退出码 `1`，`offline_results.json` 中 `O-10-exact-cleanup-and-no-display` 为 `FAIL / P1`。runner 会在 `finally` 中精确删除其 `lifeos-p3-095-review-*` SQLite／HTML 与父目录。

不要运行 Chrome 动态步骤：当前离线 P1 已触发任务卡停止条件。修复必须回到 P3-094 同一能力包；修复并经 PM 验收后，应在另一全新隔离独立会话重新执行完整离线与 Chrome `file:` 动态矩阵。

