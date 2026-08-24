# LIFEOS-P3-104 PM Review｜三页 UI→本地 Runtime 与受控 Tauri/IPC 整合能力包

## 验收信息

- 任务 ID：`LIFEOS-P3-104`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-104-v1` / `2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b`
- ABF 是否在专项会话开始前 Frozen：Yes；冻结时间 `2026-08-23 12:16:34 CST`，首次专项接收时间 `2026-08-23T12:28:01+0800`。
- 本次复验是否沿用原 L1/L2：Yes；仅复验 D-0425 已映射的 L1-1/L1-4/L1-7/L1-10 与 ABF-I-05/I-07/I-11、M-002/M-008/M-012。
- 正式 Rework 次数／上限：`1/2`，本次复验通过；不增加第二轮 Rework。
- 是否为受控能力包：Yes。
- 能力包边界：同一三页 Tauri candidate、固定非敏感 task-local DB、三项窄 IPC、同一工具链与 Frozen ABF；未扩大数据、路径、依赖、风险、冻结或阶段边界。
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
- PM Review：`lifeos/reviews/LIFEOS-P3-104_pm_review.md`
- 执行授权证据：首次任务卡投递、D-0423/D-0424 真实 Tauri/IPC 与官方 bootstrap 授权继续成立；用户随后把首轮 PM Review 投递回原工程会话，构成同一 ABF 下 Rework 1/2 授权。
- 任务验收状态：`Accepted / PM Pass / Awaiting User Adoption`。
- 资产冻结状态：`Accepted but Not Frozen`。
- 是否允许进入下一任务：Conditional；先等待用户采纳。采纳后，现行任务卡要求全新隔离独立复评；高保真 Stitch UI 必须另建任务和新 ABF。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：No；它是已通过 PM 验收的技术候选，但不是最终高保真产品 UI。
- 实际执行 Agent：Codex；内部模型 SKU／推理标签未由接口暴露，不把不可观察元数据记为 Unknown。
- Agent 与任务匹配度：High。
- 更新时间：2026-08-23 16:38:31 CST (+0800)。
- 本地模型预检：跳过；本轮为真实 Tauri/IPC、路径和本地数据失败关闭的 P0 高风险最终复验，PM 直接执行 Frozen ABF 全量核对。

## PM 总结

1. Rework Manifest 在 PM 更新 Review 前 16/16 匹配；Frozen 历史输入 14/14、初始 Engineering Manifest、初始 PM Evidence、ABF 与 Cargo.lock 均未漂移。
2. PM 在全新 `/private/tmp` 副本完成离线复跑：Rework 检查 19/19、原静态 44/44、Rust unit 7/7、locked debug build、实际 `.app` bundle/replay、动态 Evidence 17/17、lock inventory 438/438 全部通过。
3. `PM-P3-104-CE-01` 已关闭：最终 DB 与 journal/wal/shm 使用 error-aware `symlink_metadata`；PM 对四类 dangling 对象做实际二进制黑盒反例，均在变更前 fail-closed，链接、缺失目标、哨兵和残留状态不变。
4. `PM-P3-104-EV-01` 已关闭：提交了可执行离线实际 `.app` runner，包含 clean、精确 locked bundle、启动／停止／重开、dangling 实际拒绝、hash 与精确清理；PM 从无 target 副本成功复跑。
5. 最终计数：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0。结论为 PM Pass，等待用户采纳；资产 Not Frozen，不关闭风险、不恢复基线、不进入 Stage 4。
6. 用户指出的视觉差异属实：当前候选实现的是 P3-091 的语义基线，不是原冻结 Stitch 的高保真实现。该事项不在 `ABF-P3-104-v1` 内，不能追溯阻断本轮 Pass，必须作为新任务候选明确治理。

## 两层验收治理核对（D-0401 起）

- 满足的 L1：L1-1 至 L1-10 在本 ABF 的固定非敏感、task-local、离线候选边界内均成立。
- 满足的 L2：ABF-I-01 至 I-12、ABF-M-001 至 M-012 全部 PASS。
- PM 是否在提交后新增无法映射到 L1/L2 的阻断标准：No。
- 新发现视觉问题分类：不阻断的“必须新建任务”候选；若要求高保真 Stitch 结果，将改变本轮用户结果、UI 基线和验收矩阵，不能并入 P3-104。
- 是否需要实质修改当前 ABF：No；本轮保持原 ABF 并通过。
- 是否达到 Rework 上限：No；仅使用 1/2。
- 终止状态：N/A。
- 新任务触发理由：高保真布局、组件、信息结构和视觉相似度未在本 ABF 冻结；实现该用户结果需要新任务、新 ABF 与明确视觉 Evidence。

## P3 快车道 Review

不适用。本任务为 P0 真实 Tauri/IPC 受控能力包。

## 角色与关卡验收

- 主责角色覆盖：桌面 UI 语义基线、本地 runtime、三项 IPC、SQLite 生命周期和失败关闭在 Frozen 边界内完成。
- 协审角色覆盖：技术架构、AI 信任安全、数据／领域、体验与可访问性均有可复核 Evidence；独立 QA 尚未启动。
- 已通过关卡：Gate 1；Gate 2/3/4 在本任务固定非敏感候选边界内通过。
- 未通过或需后续确认：Gate 5 只完成内部固定夹具可用性，不构成用户价值 Pass；高保真原型实现未在本任务验收。
- 是否属于关键冻结事项：No；不冻结架构、Schema/API、UI 或其他资产。
- 是否需要独立评审：Yes；任务卡规定 PM Pass 与用户采纳后必须全新隔离独立复评。
- 独立评审路径／结论：N/A，尚未创建。
- 是否允许进入下一任务或阶段：等待用户采纳后才可创建独立复评；Stage 4 不允许。

## 验收与冻结区分

- 任务是否验收通过：Yes，PM Pass，等待用户采纳。
- 对应资产是否冻结：No。
- 冻结范围：仅 `ABF-P3-104-v1` 作为本轮历史验收依据保持 Frozen。
- 未冻结内容：P3-104 工程、UI、Tauri 配置、IPC、Schema/API、Evidence 与 build 资产。
- 是否允许进入下一阶段：No。
- 是否需要更新 `FREEZE_STATUS.md`：Yes，仅更新状态，不冻结资产。

## 受控能力包关卡

- 交付前包内自检：完成；44/44、19/19、7/7、实际 `.app` replay PASS。
- PM 干净副本复跑：完成；无 target 副本离线重建和实际 bundle 成功。
- 原子失败／清理／拒绝与审计追溯：PASS；四类 dangling 外置反例 4/4 PASS。
- 验收标准→测试→Evidence：完整；首轮动态闭环 17/17 继续可复核，Rework Evidence 独立追加。
- runner、结果、日志、hash、Manifest 与复跑入口：可复核。
- 历史只读资产及禁止能力关闭态：已核对；14/14 不变，retained pilot 未访问，三项 IPC 外能力关闭。
- 执行侧计数是否如实：Yes；PM 复验计数一致。
- 是否需要新的正式 Rework：No。
- 是否触发新的用户确认：Yes；需要用户决定是否采纳 PM Pass，以及采纳后如何安排独立复评与高保真 UI 新任务的先后关系。

## 需要用户确认的事项

1. 是否采纳 P3-104 作为“真实 Tauri/IPC 与本地 runtime 技术候选”的 PM Pass。
2. 若采纳，PM 建议不要把当前 UI 表述为原始设计已实现。用户需选择：按原流程先做 P3-104 全新隔离独立复评，再创建高保真 UI 任务；或明确调整治理顺序，把当前候选作为只读技术输入，先创建高保真 UI 新任务，并对最终组合候选做新的独立复评。未确认前不自动创建任何任务。

## 整改建议

无当前 ABF 内整改项。高保真 Stitch 还原不属于 P3-104 Rework，不能在本任务继续膨胀。

## 可接受内容

- error-aware lstat 与 DB／sidecar dangling 对象关闭态。
- 锁定离线工具链、真实 `.app` clean bundle/replay。
- 三项窄 IPC、renderer 零直接 capability、固定非敏感 capture/today 生命周期。
- 当前三页仅作为 P3-091 语义基线和工程测试界面，不外推为最终视觉实现。

## 不接受或需谨慎内容

- 不得声称 P3-104 高保真还原了原始冻结 Stitch 三页。
- 不得接入 retained pilot、真实个人输入或扩大 IPC。
- 不得据本轮关闭 R-0040/R-0052、扩大 R-0051、冻结资产、恢复基线或进入 Stage 4。

## 项目文件更新

- `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`：更新为 PM Pass／等待用户采纳，并记录高保真 UI 为 ABF 外新任务候选。
- `RISK_LOG.md`：不更新；风险事实未变化。
- `PROJECT_CONTEXT.md`、`PM_OPERATING_MODEL.md`、`OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度

- 推荐／实际 Agent：Codex / Codex；匹配度 High。
- 优势：真实 Tauri、Rust/SQLite 失败关闭、离线供应链和可执行 Evidence 整改完整。
- 本轮改善：首轮遗漏的 dangling link 状态矩阵和 actual-app replay 均已补齐。
- 不建议：不得由同一执行会话独立复评自己的 P0 成果。
- 是否更新路由评分：No。

## 下一步建议

- 当前停止在用户采纳决定，不自动创建后续任务。
- 若按原流程：用户采纳后创建 P3-104 全新隔离独立复评。
- 高保真原始 Stitch 三页必须使用新任务与启动前 Frozen ABF，直接锁定三张原始截图、布局／组件／信息结构、宽窄屏规则和实际 Tauri 对照 Evidence。
- 不进入 Stage 4。

## PM Evidence

- 初次验收：`lifeos/reviews/LIFEOS-P3-104/pm_evidence/initial/MANIFEST.md`
- Rework 复验：`lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md`
