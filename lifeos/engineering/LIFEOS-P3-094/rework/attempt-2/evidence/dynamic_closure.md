# P3-094 attempt-2 动态 Evidence 闭环

| ID | 动作 | 结果 | Evidence | SHA-256 | 状态 |
|---|---|---|---|---|---|
| D-01 | 新 Chrome 标签页输入完整 `file:` URL | 本地今日页加载，地址栏为 `file:` | `visual/02-today-page.png` | `5cf1b570850c85a1f4520f870f13b6d54e74825be50a1de0faf654a441413c66` | PASS |
| D-02 | 查看首次捕获／重启后的今日页 | 固定非敏感文本、时间、用户原文与本地捕获来源可见 | `visual/02-today-page.png` | 同上 | PASS |
| D-03 | 打开固定拒绝页 | 空输入被拒绝，未显示成功或部分记录 | `visual/03-rejected.png` | `c70f68a10a1fc314f7c740b431906fe525d5a6ea0f3ed0ccd2f1b0299458a53a` | PASS |
| D-04 | 关闭 Chrome 标签并删除 task-local 目录 | DB 与 HTML 已不存在 | `self_check_results.json`、操作日志 | 见 Manifest | PASS |

离线 runner 覆盖重复幂等、原子失败、清理和关闭态；其结果为 13 PASS / 0 FAIL。所有动态页面仅包含固定非敏感测试文本。
