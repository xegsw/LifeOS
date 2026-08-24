# Attempt-6 验收追溯矩阵

| 任务卡标准 | 测试 ID | Evidence |
|---|---|---|
| 唯一内部 render 路径与 CLI 移除输出能力 | A6-01, A6-03..04 | results.json, sentinel_hashes.json |
| render 最终链接／目录／FIFO fail closed | A6-05..06 | results.json, sentinel_hashes.json |
| render／clear 完整祖先链接链拒绝 | A6-07..08 | results.json, sentinel_hashes.json |
| 相对／`..`／规范化绕路拒绝 | A6-09 | results.json |
| 合法 render→clear→重渲染失败 | A6-10 | results.json |
| 页面失效失败 DB 不变、DB 最终链接拒绝 | A6-11..12 | results.json |
| render 发布失败无半成品、capture 原子失败、损坏 DB、关闭态 | A6-13..16 | results.json, source_hashes.json |
| 干净副本、零残留、历史只读 hash | A6-17..19 | results.json, historical_read_only_hashes.json |
