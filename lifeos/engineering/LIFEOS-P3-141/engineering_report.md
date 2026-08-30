# LIFEOS-P3-141 Attempt-7 Closure engineering report

## 工程门结论

**Phase A Ready for Independent Review**。本 Closure 关闭了 attempt-6 的 P0/P1：最终 receipt-enabled P3-141 bundle 现在在原生 Tauri/Wry `WKWebView` 上显式设置 Accessibility element 与 `AXWebArea` role；current `source_lineage.json` 已以最终 candidate 的 79-file framed tree 重建。结论仅覆盖唯一临时根中的固定合成夹具，不是独立评审 Pass、真实使用、PM 验收、风险关闭、冻结或 Stage 推进。Phase B/C/D/E 继续 Pending。

## 已实现与复跑事实

- 继承的 P3-140 tree 79/79 和固定输入 12/12 均匹配；current P3-141 candidate 为 79 文件、恰好 20 IPC、framed tree SHA-256 `7034edd14b9f99dbd85f8ba6a4b58f993c61a738d870fb9067b994ed6ca404c2`。旧 `6a45…a87e1` 仅为 attempt-6 失败历史。
- Provider 保持 OpenAI、Anthropic、Ollama、LM Studio 四选一；验证只走合成 loopback，零 Custom、第二 Provider、fallback、后台发送或网络。首次真实发送锁定、root receipt gate、strict fresh/owned lifecycle、Work 7–14 day 上限、Memory ≤3、五字段 Health、Today/feedback、Resolver/预算与失败关闭均保留。
- 离线 Rust 完整回放为 **48/48**；另编译的 AX helper self-test 确认：window-only 与 `AXHTMLContent`-only 均拒绝，而 `AXWebArea`／`AXWebView` 才可通过。
- 以同一 receipt-enabled final bundle、固定合成夹具和全新 direct PID 进行 actual-Tauri：desktop PID 37686、compact PID 37890、narrow PID 38060。每一行只向 native helper 传入该 PID；helper 从该 PID 的 exact-title 唯一 `AXWindow` 递归找到原生 `AXWebArea`，不把截图、Computer Use app-level HTML 或全局窗口搜索当作身份证据。
- startup receipt 仅在 `set_size`、220ms delay 和三次相等有效样本后写出。desktop 的同 PID receipt/AXWindow 均为 host-clamped 1280×949；compact 均为 700×760，narrow 均为 560×640。三张无敏感 supporting screenshot 的 native top bar 均肉眼显示 `LifeOS · P3-141 Controlled Pilot Candidate`。

## Evidence、历史与清理

- 当前 native AX / receipt / screenshot 总索引：[actual_tauri_viewports.json](evidence/actual_tauri_viewports.json)；原始 PID 链和 strict helper controls 在 [attempt-7-rework](evidence/attempt-7-rework/)；三张截图在 [evidence/screenshots](evidence/screenshots/)。
- 逐行 Frozen ABF 状态：[ABF_PHASE_A_MATRIX.md](evidence/ABF_PHASE_A_MATRIX.md)。attempt-6 及本轮所有失败或排除尝试保留在 [failure_history.md](evidence/failure_history.md)，未被重写为正 Evidence。
- 可移植的离线回放入口为 [replay_phase_a.sh](tools/replay_phase_a.sh)，须显式传入 `--input-root`；其只调用 [cleanup_temp.sh](tools/cleanup_temp.sh) 精确清理唯一临时根。最终 cleanup receipt、非自引用 Manifest 与 current source lineage 在 Evidence 根。

## 五类计数与 PM 下一步

- P0：0
- P1：0
- P2：1（本机 Rust toolchain 未安装 rustfmt，`cargo fmt --check` 无法执行；不影响编译、测试或动态 Evidence）
- Unknown：0（仅 Phase A 合成离线合同）
- Not Implemented：0（仅 Phase A 合同；Phase B/C/D/E 是明确 Pending，非本轮已实现结论）

需要一轮全新隔离的独立评审。工程会话不得自行启动 Phase C 或任何真实 Pilot。
