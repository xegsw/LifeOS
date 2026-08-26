# LIFEOS-P3-125 User Boundary Confirmation

- Date: 2026-08-26
- Decision: D-0504

> 确认 P3-125 仅使用 `lifeos/engineering/LIFEOS-P3-125/` 与 `/private/tmp/lifeos-p3-125-runtime-root-config-v1`，使用全新合成 DB；P3-122/P3-124 全部只读；仅允许构建时 `LIFEOS_RUNTIME_ROOT` 和既有 `capture_record`、`get_today`、`runtime_status` 三项 IPC；不访问旧 P3-122 临时根、Pilot、真实 DB、真实路径、真实文本、网络或产品模型。

This confirmation authorizes PM to freeze the task boundary. Execution starts only when the final task-card absolute path is delivered to a qualified Codex engineering session.
