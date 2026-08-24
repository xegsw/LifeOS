# P3-091 attempt-2｜动态 Evidence 闭环表

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| D-REOPEN | 在新 Chrome task-local `file:` 标签页输入固定非敏感文本、确认、grant、准备预览、精确 `CONFIRM`，关闭该已确认标签页；再用新标签页打开相同副本。 | 新标签页恢复默认拒绝；输入为空、无已确认记录、无恢复预览／回执，页面未回退到真实能力。 | `RW-D-01` | `01-confirmed-before-close.jpeg`、`02-reopened-cleared.jpeg`、`operation_log.md` | `c19cbb26e0477f11cf7b03226915272fa4d864baccf2a85b34b3d64af78c3559`（确认前）／`ad7bb860324db8f30093130e2b62631400856e39d7a7d4e33f7da68d44bc5be6`（重开后） | PASS |  |
| D-TAB-ENTER | 从重开后的页面起点实际按一次 `Tab` 至 skip link，再按 `Enter`。 | 可见焦点落在“跳到主要内容”；Enter 后 URL 变为 `#main-content`，默认拒绝与空输入关闭态保持。 | `RW-D-02` | `03-tab-skip-link-focus.jpeg`、`04-enter-skip-link.jpeg`、`operation_log.md` | `848f2b056488b74e65c05d22f676ccbd591875b52214379e63ac9b1074761282`（Tab）／`8194ae6a9b6de108d14f3f95a651b79d8b8380bbf6a95eaf774f9255ac01b47c`（Enter） | PASS |  |

本表仅覆盖 D-0370 明确授权补齐的两项初始动态 Evidence 缺口；初始 attempt-1 Evidence 保持只读且未被覆盖。
