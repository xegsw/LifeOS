# LIFEOS-P3-118 会话报告：P3-116 当前候选的 PID 范围 Native GUI 动态 Evidence 后继

## 任务信息

- 任务：`LIFEOS-P3-118`
- Frozen Acceptance Basis：`ABF-P3-118-v1`，SHA-256 `d6f12523683beea42ecd9d9db586b41c489991286e0ee41e2eb4afeab5e5c18c`
- 任务卡 SHA-256：`3172457dc2c60080100d367acb979f92fbb060f4c4bd6383f60e9d7cfe76ec1b`
- 执行授权证据：用户于 2026-08-25 在本专项会话投递了任务卡和 Frozen ABF 的绝对路径；本会话类型为专项执行会话。
- 状态：`Blocked — Acceptance Not Met`。这不是 P3-116 候选的失败结论，也不是 PM 验收、独立复评、用户采纳、风险关闭、冻结或 Stage 4 结论。
- 模型路由：任务卡要求 `gpt-5.6-terra + xhigh`；当前执行接口未提供可写入 Evidence 的独立实际模型／推理强度标签，故该项如实记为 `Unknown`，未以任务卡要求替代实际证明。

## 执行摘要

本任务的先决目标是：仅以 P3-118 直接启动的 Chrome PID 为边界，先由 native helper 从窗口列表中按 PID 过滤，再证明唯一 layer-0、onscreen 的窗口，并让 Computer Use 只对该已 attested 的窗口执行 46 项 GUI 动作。ABF 同时禁止按 `com.google.Chrome`、Chrome bundle、窗口标题或现有应用实例进行选择；因为这种 app-selector 路径无法证明所操作的面是 runner 新建的 PID/window。

冻结输入预检完成且通过。`evidence/preflight/fixed_inputs.json` 重新计算了 17 个只读固定输入、P3-118 任务卡、Frozen ABF 和直接 Chrome 可执行文件的 SHA-256；全部与冻结值一致。精确路径 `/private/tmp/lifeos-p3-118-native-capture-v1` 在任何浏览器或 GUI 行为前不存在。P3-116/P3-117 的候选、历史任务、交付物、Review、Manifest、账本、风险和冻结资产均只读，未被修改。

在不选择、不查询、不启动 Chrome 的前提下，已新增并编译 P3-118 自有的 `tools/pid_window_attest.swift`。该 helper 仅接受 `--pid`；先过滤 `CGWindowListCopyWindowInfo` 的目标 PID，再从该集合抽取 layer-0、onscreen 窗口；只允许序列化 PID、window ID、bounds、layer、onscreen、frontmost、可执行文件 SHA-256 和布尔条件。它不接受或输出窗口标题、owner 名称、URL、DOM、AX、浏览器 profile 或其他环境元数据。静态审计确认这些 PID-first 约束存在，且没有 app selector、窗口标题字段、AppleScript、DevTools、浏览器自动化或全桌面截图 API。

阻塞点发生在下一步所需的 Computer Use 绑定：本机可用的 Computer Use 操作表面是 app-scoped，GUI 状态和输入操作需要 `app` 目标；没有 PID 参数、没有 native window-ID 参数，也没有能接收 helper `{pid, window_id}` attestation 的调用。若继续把 `com.google.Chrome` 传给该表面，就会使用 ABF 明确禁止的 app selector，且无法证明动作发生在所 attested 的 P3-118 窗口。该路径会重现 P3-117 所识别的绑定歧义，因此在任何 Chrome launch、窗口查询、PID 获取、native capture、`screencapture` 或 46 项 GUI 操作之前停止。

本会话没有以浏览器控制、AX、CDP、DevTools、WebDriver、headless、现有 Chrome、应用选择器、窗口标题、OCR、全屏／全桌面截图或其他替代途径绕过该限制。未创建临时 profile、候选副本、Chrome PID、截图或 capture 文件；精确清理检查为 `NONE_REQUIRED`。本地模型预检未调用：任务卡禁止网络，而该预检依赖局域网模型；这不影响本次基于本地可复算 JSON 和 SHA-256 的 fail-closed 结论。

## Evidence 与验收矩阵

| 冻结动作／检查 | 测试 ID | 实际 Evidence | 结论 |
|---|---|---|---|
| 17 个固定输入、任务卡、ABF、Chrome 可执行文件哈希复算 | `P118-M001` | `evidence/preflight/fixed_inputs.json` | 输入完整性通过；实际模型／推理标签不可独立记录，M001 为 `Unknown` |
| PID-first native helper 的静态约束 | `P118-PREFLIGHT-STATIC` | `evidence/preflight/static_audit.json`；`tools/pid_window_attest.swift` | 通过；只是 source/compile 预检，不构成窗口 attestation |
| Computer Use 与 PID/window 绑定可用性 | `P118-BLOCKER-001` | `evidence/results/computer_use_pid_binding_assessment.md`；同名 JSON | `Blocked`；禁止 app selector 且无 PID/window 目标参数 |
| 46 项动态动作的闭环表 | `P118-A-001` 至 `P118-A-046` | `evidence/results/dynamic_closure.json` | 0/46 执行，46/46 `NOT_IMPLEMENTED`，没有伪造视觉或日志 Evidence |
| ABF-M-002 至 ABF-M-014 | `P118-M002` 至 `P118-M014` | `evidence/results/results.json` | 13 项 `NOT_IMPLEMENTED`，原因均为 `BLOCKED_COMPUTER_USE_PID_BINDING_UNAVAILABLE` |
| 未创建资源的精确清理 | `P118-M015` | `evidence/preflight/cleanup_prelaunch.json` | 通过；精确 P3-118 临时根不存在，未检查或影响任何其他 Chrome 状态 |
| Blocked 包的完整性 | `P118-PACKAGE-VERIFY` | `evidence/results/blocked_package_verification.json` | 通过；15 行矩阵、46 行闭环、零 GUI 行为和非 Pass 状态一致 |

本任务的数值为：P0=0、P1=0、P2=0、Unknown=1、Not Implemented=13。这里的零 P0/P1/P2 只表示在未执行候选 GUI 的前提下未观察或引入相应缺陷，不能推断为候选质量已被验证。由于 `Unknown` 与 `Not Implemented` 非零，且 46 个动态动作均未实际完成，Frozen ABF 的 Pass 公式不成立；候选质量未评估。

## 角色检查点与评审关卡

- 专项执行／Evidence 工程检查点：完成了固定输入防漂移、PID helper 静态边界、Computer Use 能力预检、无替代路径停止、46 项闭环的显式未执行记录和精确清理检查；结果为 `Blocked`，不提交为 Candidate Ready。
- 安全与证据诚实检查点：通过。未读取或操控既有 Chrome，未以 app selector 代替 PID/window binding，未补写任何截图、AX、日志或动态通过结论。
- PM 验收：尚未发生，且当前产物不具备验收为 Pass 的条件。
- 全新隔离独立复评／用户采纳：均未发生；在 PM 处理本阻塞并按治理规则决定后才可能适用。

## 交付物

- 本报告：`lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md`
- P3-118 自有工具、计划和 Evidence：`lifeos/prototypes/LIFEOS-P3-118/`
- 非自指 SHA-256 Manifest：`lifeos/prototypes/LIFEOS-P3-118/MANIFEST.md`

## 需要 PM 决策

需要。请 PM 依据现有 L1/L2 与 Rework／新任务边界决定如何处理“Computer Use 无 PID/window target，但 ABF 禁止 app selector”的环境能力缺口。当前专项会话无权修改 ABF、放宽 I03/I04、替换 GUI 工具、重新授权 app selector，或自行创建后继任务。任何后续尝试都必须在新的明确授权和适用 ABF 下进行；本任务历史及 P3-116/P3-117 资产应保持只读保全。

## 后续任务建议

无自动后续任务。仅等待 PM 对上述阻塞边界的治理决定。

## 阻塞或异常

唯一实质阻塞是 `BLOCKED_COMPUTER_USE_PID_BINDING_UNAVAILABLE`。Swift 编译曾因受限环境默认模块缓存不可写而首次停止；缓存随后仅定向至 P3-118 允许目录完成编译，并已按精确路径删除。该编译环境限制不改变主阻塞结论，且未创建任务指定的 native capture 临时根。
