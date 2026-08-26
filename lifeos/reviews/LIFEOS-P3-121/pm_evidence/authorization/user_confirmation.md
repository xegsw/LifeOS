# LIFEOS-P3-121 启动前执行边界确认

- 日期：2026-08-25
- 用户确认：P3-121 仅在 `lifeos/engineering/LIFEOS-P3-121/` 与 `/private/tmp/lifeos-p3-121-combined-v1` 使用全新合成 DB 和既有 `capture_record`、`get_today`、`runtime_status` 三项 Tauri/IPC。
- 明确禁止：Pilot、真实 DB、真实路径、真实文本、网络、模型。
- PM 解释：本确认只授权正式 Frozen ABF 范围内的 P3-121 工程执行；不授权新 IPC、Schema/API、clear/export/权限/恢复、Vault、网络／模型、风险关闭／重开、资产冻结、工程基线恢复、独立复评或 Stage 4。
- 执行启动：PM 完成 fixed-input 复算、positive allowlist 和 ABF 冻结后，用户将最终任务卡绝对路径投递至全新合格 Codex 工程会话才启动。
