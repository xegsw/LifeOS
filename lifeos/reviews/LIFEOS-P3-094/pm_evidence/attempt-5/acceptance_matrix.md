# Attempt-5 验收追溯矩阵

| 任务卡标准 | 测试 ID | Evidence |
|---|---|---|
| 首次、幂等、跨进程复读 | A5-01..03 | results.json |
| 合法精确 today 页面失效、DB 清空、重渲染失败 | A5-04 | results.json |
| API／CLI DB 外哨兵拒绝且 hash、DB 不变 | A5-05, A5-07 | results.json, sentinel_hashes.json |
| 非标准名、相对／规范化／.. 绕路拒绝 | A5-06 | results.json |
| 链接、目录、特殊文件与 DB 链接边界 | A5-08..11 | results.json, sentinel_hashes.json |
| 页面失效失败 DB 不变 | A5-12 | results.json |
| 原子失败、损坏 DB、禁止能力关闭 | A5-13..15 | results.json, source_hashes.json |
| 干净副本单元回归、零残留、历史保全 | A5-16..18 | results.json, historical_read_only_hashes.json |
