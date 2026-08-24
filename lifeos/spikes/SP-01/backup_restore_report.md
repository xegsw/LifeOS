# SP-01 一致备份与恢复报告

## 方法

使用 Python `sqlite3.Connection.backup()`（SQLite Online Backup API）从开启 WAL 的活跃数据库创建一致快照；备份期间后台线程完成 50 次耐久提交。没有把活跃数据库文件裸拷贝作为合格备份。随后将快照复制为独立恢复库，重新连接并执行完整性、计数、hash、墓碑、Feedback 撤回和待同步检查。

## 已验证事实

- 快照发生前最低计数：Artifact 1491、Version/Submission 1591。
- 快照计数：Artifact 1492、Version/Submission 1592；恢复计数完全相同。
- 备份结束后活库计数：Artifact 1541、Version/Submission 1641，证明写线程确实与快照过程交叠；快照是一个一致时点，不承诺包含快照后的写入。
- `PRAGMA integrity_check`：`ok`；恢复库原文 SHA-256 不一致：0。
- Tombstone 3 条、Feedback event 2 条、Authorization 4 条均保留。
- 恢复后待同步 Version 400 条，状态未被误改成已同步。
- 三个已删 Artifact 的活跃命中为 0；再次重放旧 Artifact 包后活跃命中仍为 0。
- 已撤回 Feedback 的活跃命中为 0。

## 推断与限制

- 结果支持“数据库感知快照 + 恢复时先加载用户权威状态”满足本 Spike 的最低一致恢复语义。
- 本次没有定义生产备份 SLA、加密、异地副本、保留周期、跨版本迁移或物理介质损坏恢复；不得据此宣称生产备份方案已冻结。

