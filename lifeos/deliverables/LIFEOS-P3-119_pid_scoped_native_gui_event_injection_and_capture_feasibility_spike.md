# LIFEOS-P3-119｜PID 限定原生 GUI 事件注入与截图可行性 Spike

## 结论

**专项自检结论：Not Pass。** 本 Spike 只验证 task-local synthetic fixture 的工具链，不对 P3-116 候选、产品质量、风险状态、冻结、runtime 或 Stage 4 作任何结论。

在 `execution-8` 的干净临时根中，10 项冻结输入和 Chrome executable 均匹配；Swift helper 通过 PID-only 静态审计并编译；直接启动的 Chrome 主 PID `2399` 在 profile 合同和 `file:` fixture 合同均通过后，取得唯一 layer-0 onscreen window `48976`（1200×905）。`screencapture -l 48976` 产生 S0 原生图，目标 PID/window 和 S0 红色色块均可复核。

随后 helper 以 Swift 对 C API `CGEventPostToPid` 的正式绑定 `CGEvent.postToPid(_:)` 向该精确 PID/window 投递首次 click `P119-E001`。投递记录为 `PID_CLICK_POSTED`，但重新 attestation 后的 S1 原生图与 S0 的 SHA-256 同为 `16a34016e9682493595e9cc9a2f9e29b0b83e4a15c0330b6f9100055c7d77ddf`；S1 绿色像素断言为 0/81。即：事件的目标归属可复核，但没有可观察的 S0→S1 GUI 状态转换。

这违反 L1-4、L1-6、L1-7 与冻结 ABF-I-04 / ABF-M-004，记 **P0=1**。按照 Frozen “任一失配即停止”的合同，未发送第二次 click、Tab 或 Enter；未执行 restart 或 10 类 mutation。精确关闭专用 PID 后，唯一临时根 `/private/tmp/lifeos-p3-119-pid-gui-spike-v1` 已不存在。

## 事实与待确认

源码审计拒绝 global event、AppleScript、AX、selector、CDP/DevTools、headless、HTTP/网络、storage 与 DOM 旁路；每次执行后的 root 都不存在，且 P3-116～P3-118 未被修改。当前证据不能区分 macOS 输入权限、`postToPid` 语义或其他环境条件，故结论是 **Not Pass**，不擅自外推为权限 `Blocked`。当前执行界面未暴露实际模型/推理配置，记 **Unknown=1**。

## 冻结矩阵

| 行 | 结果 | 实际 Evidence | 结论 |
|---|---|---|---|
| M-001 | Pass with model Unknown | `execution-8/fixed-inputs.jsonl` | 10/10 输入匹配；模型配置不可观察 |
| M-002 | Pass | `raw/static_audit.json`、`helper_compile.log` | 静态 PID-only 工具链成立 |
| M-003 | Pass | `raw/P119-M003-attest.json`、`images/S0.png` | 专用 PID/唯一窗口/S0 成立 |
| M-004 | Not Pass / P0 | `raw/P119-E001-click.json`、`raw/S1-*.json`、`images/S1.png` | 已投递但 S1 未发生 |
| M-005–M-008 | Not Implemented | `evidence/final_assessment.json` | M-004 后冻结 fail-closed 停止 |
| M-009 | Pass | `execution-8/cleanup.jsonl` | 本次专用 PID 精确关闭；root 不存在 |

自检计数：**P0=1、P1=0、P2=0、Unknown=1、Not Implemented=4**。Pass 公式不成立。

## 角色与关卡

- 主责“本地 GUI 技术 Spike”：Gate 4 技术可行性未通过，原因仅为 M-004 的实际状态转换缺失。
- Evidence QA：通过边界、固定输入、PID/window 归属、原生截图、fail-closed 与清理检查；未将 helper 编译或 event 返回冒充 GUI Pass。
- 隐私/安全：通过受控范围检查；未访问既有 Chrome、P3-116 候选、真实数据、其他 PID/window 或网络。
- 本任务不要求独立评审；仍须 PM 验收与用户采纳，且本结论不创建后续任务。

## Evidence 与本地预检

Evidence 入口为 [MANIFEST.md](/Users/xxe/Documents/No.2/lifeos/spikes/LIFEOS-P3-119/MANIFEST.md) 与 [README.md](/Users/xxe/Documents/No.2/lifeos/spikes/LIFEOS-P3-119/README.md)。机器可读结论见 [final_assessment.json](/Users/xxe/Documents/No.2/lifeos/spikes/LIFEOS-P3-119/evidence/final_assessment.json)。

按任务卡的网络禁止边界，本地模型预检跳过；它也不得决定此 P0 GUI 隔离/可行性结论。

## PM 需要确认

1. 验收本 Spike 的 `Not Pass` 事实：PID-target event 未形成可观察 GUI 转换。
2. 是否将该现象归类为工具/权限环境 `Blocked`，或在用户授权后创建新任务与新 ABF；在此之前不得创建最终 46 动作 Evidence 任务。
