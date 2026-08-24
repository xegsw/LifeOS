# LIFEOS-P3-111 本地自用受控运行时

本候选只允许 renderer 调用 `capture_record`、`get_today`、`runtime_status`。正式运行时不接收任何路径参数，只能在用户通过 UI 主动提交简短、非敏感原文时创建并原子发布到唯一获授权的 `LifeOS-Self-Use-Pilot-2/capture.sqlite`。

冻结关闭态：网络、AI、外部来源、Vault、导出、同步、Shell、进程、直接文件/数据库/通用路径 API 均未启用。P3-111 仍不是 Stage 4 准入、风险关闭或完整自用 MVP 宣称。

包内夹具仅位于 `evidence/test-fixtures/`，用于固定非敏感的失败关闭、幂等、篡改和链接边界测试；它们不会读取或写入正式 Pilot-2 数据库。
