# P3-133 Closure-1｜保全的 actual Tauri 合成动态 Evidence

本表只复算仍保全的 `ui-observations.json`、截图和其 SHA-256；不读取、写入或依赖已清理的合成 DB。原 `verification.json` 与 `FINAL_MANIFEST.json` 因 PM 事故被隔离，且不作为正 Evidence。真实根与真实输入均未访问。

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| D-133-C01 | 合成 actual Tauri：明确接受 Candidate | Today Focus 对应用户确认 Action | `positive-lifecycle:accept_candidate` | `actual-tauri/screenshots/synthetic-confirmed-action.jpeg`；`actual-tauri/ui-observations.json` | `b7c53d40707c5094a42be94c324199fe9ecaefce9c54643b14748d461a04e27b` | PASS |  |
| D-133-C02 | 合成 actual Tauri：关闭并重开 | Capture／Context／Action／Today Focus 仍可见 | `positive-lifecycle:reopen` | `actual-tauri/screenshots/synthetic-reopen-focus.jpeg`；`actual-tauri/ui-observations.json` | `c48b2bf0d7a233d3b89625e4a99130b73bedfe6f4e773fa19f6feff6bd5494a3` | PASS |  |
| D-133-C03 | 合成 actual Tauri：拒绝 Context link | Candidate／Action 为零，Today 为空 | `link-rejection:capture_then_reject_link` | `actual-tauri/screenshots/synthetic-link-rejected.jpeg`；`actual-tauri/ui-observations.json` | `edd6f867aa6da61f97b9c2f4ca0ecbd70fc24f28eb1b1eb7a0979f3b5de23e5f` | PASS |  |
| D-133-C04 | 合成 actual Tauri：拒绝 Candidate | Action 为零，Today 为空 | `candidate-rejection:confirm_context_then_reject_candidate` | `actual-tauri/screenshots/synthetic-candidate-rejected.jpeg`；`actual-tauri/ui-observations.json` | `6846d2c66acaf714b77bda3a6bdf68a1842050c783619a4b0f75b23e3820e6fe` | PASS |  |

这些行仅恢复工程侧已保全的合成动态资产的可复算性；AC-11 独立评审与 AC-12 真实自用仍为 `NOT IMPLEMENTED`，不得由本表推导 Pass。
