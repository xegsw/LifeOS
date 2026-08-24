# P3-094 attempt-3 验收矩阵

| 任务卡验收标准 | 测试／动作 | Evidence |
|---|---|---|
| 离线前置、首次、幂等、重启、失败拒绝 | O-01..O-07 | `offline_results.json` |
| Chrome 完整 file: 预检与成功今日页 | D-01..D-02 | `dynamic_results.json`, `dynamic_closure.md`, `visual/` |
| 空输入拒绝／fail-closed | D-03 | `dynamic_results.json`, `visual/03-empty-fail-closed.png` |
| 关闭标签 | D-04 | `dynamic_results.json`, `visual/04-after-close.png` |
| DB／HTML 与系统临时残留清理 | D-05 | `cleanup_results.json` |
| source hash 与历史只读保全 | source-hash | `source_hashes.json`, `MANIFEST.md` |
