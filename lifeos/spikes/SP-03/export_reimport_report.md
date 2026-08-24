# SP-03 导出 / 重导入报告

## 结论

- 当前导出状态：`partial`；成功 1、排除 2、失败 1。
- 导出条目保留 Artifact 身份、精确版本、Source；业务对象保留 AI/用户确认身份、原候选、Feedback 与证据状态。
- 使用删除前旧包重导入时，先合并并应用当前墓碑与 Feedback 撤回，再接纳内容；复活数 **0**。
- 这是 SP-03 的基础包络验证，不是 SP-08 正式迁移格式或完整导出协议。

## 部分结果

- 排除原因：source_policy_non_exportable, tombstoned
- 失败原因：authorization_revoked
- 被控制阶段阻断的 Artifact：artifact-user-note
- 被控制阶段阻断的 Feedback：feedback-action-edit
