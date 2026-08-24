# SP-05 propagation state machine

## Stage A — synchronous commit

`accepted → active_blocked → physical_cleanup_pending | completed_no_physical_cleanup_required`

同一事务写入命令、Authorization 版本或墓碑、受影响对象不可消费状态、最小 AuditEntry 与 cleanup outbox。事务一旦提交，所有读取、搜索、恢复、今日、候选、队列、模型网关、跨 Project、再派生、导出与重导入路径都必须重检；任何未知状态默认拒绝。

## Stage B — asynchronous cleanup

`physical_cleanup_pending ↔ physical_cleanup_failed → physically_cleaned`

第三方不能即时或完全删除时进入 `vendor_limited`；唯一证据失效的用户确认对象进入 `review_required`。租约、幂等键和验证允许 kill、重复、乱序及租约过期后重试。死信只说明物理清理未收敛，绝不解除 `active_blocked`。

这些状态是验证语义，不是正式持久化枚举、API 或 UI 冻结。
