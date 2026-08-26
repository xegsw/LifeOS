# LIFEOS-P3-120 Rework-1 实际 App Evidence 测试设计

## 目的与边界

本设计只关闭 PM-P0-001 与 PM-P1-001 的 Evidence 缺口，并把用户已确认的模型配置写入结构化 Evidence。它不修改 candidate、ABF、三项 IPC、Schema/API、初次 Evidence、项目账本、风险、冻结或阶段。

所有动态动作须由用户在前台 packaged `.app` 中手动完成。执行侧只负责启动／关闭 task-local app、读取合成 SQLite、保存进程 stdout、截取辅助窗口图、生成 hash 与运行 verifier。禁止使用 P3-119 helper、Computer Use、AppleScript、AX、CDP、HTTP、WebDriver、浏览器控制、源码状态合同或 Rust unit test 替代任何实际动作。

## 固定环境

- Runtime 根：`/private/tmp/lifeos-p3-120-runtime-mvp-v1`
- DB：`/private/tmp/lifeos-p3-120-runtime-mvp-v1/capture.sqlite`
- 允许原文：`P3-120 synthetic capture one`、`P3-120 synthetic capture two`
- IPC：`capture_record`、`get_today`、`runtime_status`
- 初次 Evidence：只读；其 PM 核验 hash 必须在 `preflight.json` 中复算。

## 动态闭环表

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence | 状态 |
|---|---|---|---|---|---|
| M-001 | 空临时根，复算初次资产与用户确认模型 | hash 不漂移；模型为 terra+xhigh | R1-PREFLIGHT | `preflight.json` | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-01 | 空 DB 的 Today | Today 空态、Runtime status | R1-today-empty | screenshot + app log | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-02 | 手动导航 Me | Me fixture 页面可见 | R1-me | screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-03 | 手动导航 Contexts 并打开 Context Detail | 列表与详情分别可见 | R1-contexts / R1-context-detail | screenshots | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-04 | 手动导航 Memory 并打开 Memory Detail | 列表与详情分别可见 | R1-memory / R1-memory-detail | screenshots | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-05 | 打开 Global AI，再展开 AI Workspace | Panel 与 Workspace 分别可见且模型未启用 | R1-global-ai / R1-ai-workspace | screenshots | PASS — `DYNAMIC_CLOSURE.json` |
| M-004-06 | 手动导航 Settings | 弱化 Settings 可见 | R1-settings | screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-005 | App 已运行 | stdout 记录 runtime_status restricted_offline | R1-today-empty | app log + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-006 | 空 DB，手动点击 synthetic one | `saved`；DB 1 capture/1 audit；Today 可见 | R1-capture-one | app log + DB + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-007 | 1 capture，重复点击 synthetic one | `idempotent_repeat`；DB 仍 1 capture/2 audit；Today 可见 | R1-repeat-one | app log + DB + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-008 | 1 capture，手动点击 synthetic two | `saved`；DB 2 capture/3 audit，顺序正确 | R1-capture-two | app log + DB + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-009 | 2 captures，手动点击 Refresh Today | 2 条不变；DB SHA 与 refresh 前相同 | R1-refresh | app log + DB + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-010-01 | 2 captures，用户从窗口关闭 app | 原 app process 已退出；DB 2 条保持 | R1-closed | process + DB + log | PASS — `DYNAMIC_CLOSURE.json` |
| M-010-02 | 同一 DB 重开 app | stdout get_today=loaded；Today 2 条保持 | R1-reopen-today | process + DB + screenshot | PASS — `DYNAMIC_CLOSURE.json` |
| M-015 | 完成后关闭 app、复算并清理根 | 初次资产不变；唯一根不存在 | R1-final | verifier + cleanup | PASS — `DYNAMIC_CLOSURE.json` |

刷新与关闭重开是独立动作。每个 `PASS` 必须有用户手动操作、相应结构化结果、截图或进程／stdout 日志、以及 SHA-256；任何缺项由 verifier 置为 `NOT IMPLEMENTED`，不得从相邻步骤推定。
