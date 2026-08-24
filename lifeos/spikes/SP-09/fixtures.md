# SP-09 合成夹具

固定种子为 `20260809`。三档分别生成 10,000 / 100,000 / 1,000,000 个内容单元，每单元 3 个分块。全量档含 128 个合成 Project、2,000 个 Source，并按确定性比例生成 Link（20%）、Derivation（约 14.3%）、Feedback（约 9.1%）、AuditEntry（5%）。

内容单元保留稳定合成 ID、Project、Source、版本、时间、类型、用户原文候选、hash、Authorization、证据状态、active、generation 与 tombstone。正文只使用受控通用词与序号，不来自任何真实资料。

每 200 条的控制分布：2 条预置删除/旧 generation、1 条撤回、4 条拒绝授权、1 条证据不可用，其余允许；每 100 个 Source 有 1 个断开。Project、Source、状态和时间彼此可组合过滤，避免无过滤纯随机压测。

查询集每类预热 10 次后采样：关键词+Project+权限/状态 120 次、Project+时间元数据 120 次、高/低选择性授权查询各 120 次、Project 恢复包组装 80 次。捕获增量采样 100 次。删除测试含单条、单 Source 和恰好 1% ID 模式；先提交 tombstone/active block，再抹除 inactive 原文和派生分块、重建 FTS。恢复从新控制事件之前的数据库感知备份开始，并在开放读取前重放 tombstone。

并发维护探针在隔离恢复副本上用 `BEGIN IMMEDIATE` 获取写者锁后执行 FTS 全量 rebuild，同时测一次前台权威捕获等待。该探针刻意暴露 SQLite 单写者长事务风险。

