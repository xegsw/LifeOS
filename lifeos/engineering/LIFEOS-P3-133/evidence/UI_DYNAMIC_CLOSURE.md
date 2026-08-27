# P3-133｜actual Tauri UI 动态 Evidence 闭环

所有 PASS 动作均在任务临时根的 native Tauri 合成运行中完成；没有真实自用根访问，也没有真实文本。每行的结构化结果在 `actual-tauri/ui-observations.json`，其中只含合成状态或非内容型计数。

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| D-133-01 | 新鲜 native Tauri 合成窗口，保存充分 Evidence Capture | Capture 保存；Context 为 candidate；Today 仍为空 | `positive-lifecycle:fresh_start/capture` | `actual-tauri/ui-observations.json`; `actual-tauri/synthetic-run-noncontent.json` | `656baa3d3fd398dd84e592cad793daa1cec793c8dc48c059f0b5b78f024fff83` | PASS |  |
| D-133-02 | 在同一窗口点击“重试同一 Capture” | receipt 为 `idempotent_repeat`，记录数仍为 1 | `positive-lifecycle:repeat_capture` | `actual-tauri/ui-observations.json`; `actual-tauri/synthetic-run-noncontent.json` | `656baa3d3fd398dd84e592cad793daa1cec793c8dc48c059f0b5b78f024fff83` | PASS |  |
| D-133-03 | 明确确认 Context 后点击刷新 | Candidate 可见；刷新不自动创建 Today Focus | `positive-lifecycle:confirm_context/refresh` | `actual-tauri/ui-observations.json`; `actual-tauri/screenshots/synthetic-confirmed-action.jpeg` | `b7c53d40707c5094a42be94c324199fe9ecaefce9c54643b14748d461a04e27b` | PASS |  |
| D-133-04 | 用户明确接受 Candidate | 只创建 1 个开放 Action，Today Focus 可见 | `positive-lifecycle:accept_candidate` | `actual-tauri/screenshots/synthetic-confirmed-action.jpeg`; `actual-tauri/synthetic-run-noncontent.json` | `b7c53d40707c5094a42be94c324199fe9ecaefce9c54643b14748d461a04e27b` | PASS |  |
| D-133-05 | 切换 Global AI Context 与 Memory provenance | 两个页面可见；Memory 仅显示引用身份 | `positive-lifecycle:global_and_memory` | `actual-tauri/ui-observations.json` | `656baa3d3fd398dd84e592cad793daa1cec793c8dc48c059f0b5b78f024fff83` | PASS |  |
| D-133-06 | 关闭并重开同一 native App | Capture／confirmed Context／开放 Action／Today Focus 保持 | `positive-lifecycle:reopen` | `actual-tauri/screenshots/synthetic-reopen-focus.jpeg`; `actual-tauri/synthetic-run-noncontent.json` | `c48b2bf0d7a233d3b89625e4a99130b73bedfe6f4e773fa19f6feff6bd5494a3` | PASS |  |
| D-133-07 | 新鲜合成根保存后拒绝 Context link | Context 为 rejected；Candidate／Action 均为 0；Today 为空 | `link-rejection:capture_then_reject_link` | `actual-tauri/screenshots/synthetic-link-rejected.jpeg`; `actual-tauri/synthetic-link-rejected-noncontent.json` | `edd6f867aa6da61f97b9c2f4ca0ecbd70fc24f28eb1b1eb7a0979f3b5de23e5f` | PASS |  |
| D-133-08 | 新鲜合成根确认 Context 后拒绝 Candidate | Action 为 0；Today 为空 | `candidate-rejection:confirm_context_then_reject_candidate` | `actual-tauri/screenshots/synthetic-candidate-rejected.jpeg`; `actual-tauri/synthetic-candidate-rejected-noncontent.json` | `6846d2c66acaf714b77bda3a6bdf68a1842050c783619a4b0f75b23e3820e6fe` | PASS |  |
| D-133-09 | 键盘路径 | N/A | `ui-observations:not_run.keyboard_path` | `actual-tauri/ui-observations.json` | N/A | Task Contract 未把键盘操作列为验收动作。 |
| D-133-10 | 宽／窄视口 | N/A | `ui-observations:not_run.viewport_resize` | `actual-tauri/ui-observations.json` | N/A | Task Contract 未把窗口尺寸／窄视口列为验收动作。 |

`tools/verify_engineering.py` 读取同一 actual Tauri 截图、非内容状态和测试日志，不能从本表中的 PASS 文本推导工程结论。
