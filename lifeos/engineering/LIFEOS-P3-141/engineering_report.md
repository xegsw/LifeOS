# LIFEOS-P3-141 Attempt-4 Rework Closure engineering report

## 工程门结论

**Phase A Ready for Independent Review**。本 Closure 修复了 attempt-4 指出的启动回执时序、多档尺寸复用风险、Today Health 受控来源和前端入口遗漏，并重新完成受控 real-mode actual-Tauri Evidence。结论仅覆盖唯一临时根中的固定合成夹具；不是 Phase B 独立评审 Pass、Phase C 真实使用、PM 验收、风险关闭、冻结或 Stage 推进。Phase B/C/D/E 均为 Pending。

## 已实现与复跑事实

- candidate 仍为 79 文件、恰好 20 IPC；固定输入 12/12 与 P3-140 candidate 79/79 tree 均匹配。Provider 仅 OpenAI、Anthropic、Ollama、LM Studio；验证仅使用 loopback，零 Custom、第二 Provider、fallback、后台发送或网络。
- Work real-contract 为 7–14 天、每日最多 1 条、总数最多 14。第 2 条同日和第 15 条总量均在任何业务写前拒绝，并由 restart-safe ledger 审计。
- `update_current_state` 承载 Health/Fitness 五个封闭字段：sleep duration range、energy 1–5、soreness/pain boolean、training load L/M/H、available time。没有自由文本或医疗诊断路径；非法值和自由文本在写前拒绝，Today/feedback 仍复用现有闭环。
- receipt-enabled real-contract 限制 confirmed Durable Memory 至 3；第 4 条写前拒绝并在重启后保持。candidate 的 real-flow 标识、source/artifact、request key 和文案均为 P3-141；静态扫描无 P3-133/P3-131 残留。
- 最终 synthetic replay 为 Rust 48/48。新增反例覆盖 stale 首样本/跨档复用、受控 source 的唯一闭集、完整 UI Health DTO 和 `runtime-adapter.js` 必须在 P3-140 前加载。既有 root、Work、Memory、五字段非法/自由文本、重启、DB/哨兵、Provider lock、budget 与 feedback 覆盖均未回退。
- actual-Tauri 仅在 receipt-enabled real-mode、固定合成夹具中启动：desktop PID 21459、compact PID 21709、narrow PID 21840。每次直接 PID 均定位同一 bundle；原生 AX 对该 PID 返回 1 个 exact-title Window 和 1 个 HTML WebView。回执在 `set_size` 后等待 220ms 并采集 3 个稳定样本。desktop 主机实际外框为 1280×949（而非声称请求值 1280×1024），与同 PID AX frame 一致；compact 700×760、narrow 560×640 均精确一致。
- desktop Today 的合成五字段 UI 已实际保存：受控 source ref、SQLite 五字段行、Today 更新和 candidate-only `confirm` feedback 均可复核；无自由文本、诊断、Provider 或网络派发。

## Evidence、清理与保留

- 最终 actual-Tauri 数据与截图 hash：[`actual_tauri_viewports_final.json`](evidence/attempt-4-rework/actual_tauri_viewports_final.json)；人工视觉声明：[`manual_screenshot_review.md`](evidence/attempt-4-rework/manual_screenshot_review.md)；Health UI route：[`health_ui_route.json`](evidence/attempt-4-rework/health_ui_route.json)。仅该目录内三张 `*_final.png` 是本次正 Evidence。
- 逐行状态在 [`ABF_PHASE_A_MATRIX.md`](evidence/ABF_PHASE_A_MATRIX.md)。旧标题冲突、初始 compact 尺寸不符、fixture schema 失败和所有中间截图均保留在 [`failure_history.md`](evidence/failure_history.md)，不作正 Evidence。
- 回放入口为 [`replay_phase_a.sh`](tools/replay_phase_a.sh)（显式 `--input-root`）；它以 trap 调用唯一 [`cleanup_temp.sh`](tools/cleanup_temp.sh)。最终 cleanup receipt 确认唯一临时根已不存在。
- 本包 P0=0、P1=0、P2=1（环境缺少 rustfmt，`cargo fmt --check` 未能执行）、Unknown=0、Not Implemented=0（仅 Phase A 范围）。全任务层面：Phase B/C/D/E 均 Pending，不能宣称完成。

## PM 下一步

需要一轮新的隔离独立评审。不得由本工程会话自行启动任何真实 Pilot 或 Phase C。
