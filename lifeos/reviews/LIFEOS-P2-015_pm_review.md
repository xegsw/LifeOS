# LIFEOS-P2-015｜Tauri / IPC 最小安全边界窄测 PM Review

## 验收信息

- 任务 ID：LIFEOS-P2-015
- 任务名称：Tauri / IPC 最小安全边界窄测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-015_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P2-015 完成了任务卡要求的等价可执行 harness 验证，交付物、证据入口、测试矩阵和隐私扫描完整。
2. PM 复跑 `python3 lifeos/spikes/P2-015-tauri-ipc-boundary/run_harness.py`，结果为 `42/42 PASS`、`P0 failed 0`。
3. Renderer 零直接 capability、IPC 白名单 / 默认拒绝、路径规范化、scope 校验、Vault 零写、导出隔离、执行前重检和内容身份保留均在 harness 中通过。
4. 由于本机未验证真实 Tauri capability、插件、WebView / CSP、debug / release bundle、invoke 注册、updater / sidecar 和目标平台配置，项目级结论只能是 `Pass with Conditions`。
5. P2-015 可以作为技术架构冻结输入，但不能证明真实 Tauri 包已经安全。
6. 本任务不冻结 Tauri、IPC 命令、capability 名称、API、Schema、文件布局、桌面壳或技术架构，也不允许进入 Stage 3。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖。技术架构负责人视角下，最小安全边界、默认拒绝、后端授权门和失败降级均明确。
- 协审角色覆盖情况：已覆盖。AI 信任与安全、数据 / 领域模型、体验设计和 PM 边界均有说明。
- 已通过关卡：Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；Gate 4 技术可行性评审（等价 harness 层）。
- 未通过或需后续确认关卡：真实 Tauri / 打包 / 平台层 Gate 4 仍需在实际实现引入时复测。
- 是否属于关键冻结事项：属于技术架构冻结前硬条件，但本任务自身不是冻结决策。
- 是否需要独立评审：不需要新增独立评审；P2-012 已完成技术架构独立评审，本任务是其条件验证。
- 独立评审路径：`lifeos/reviews/LIFEOS-P2-012_technical_architecture_independent_review.md`
- 独立评审结论：Pass with Conditions，要求 FTS 与 Tauri / IPC 两项窄测。
- 是否允许进入下一任务或下一阶段：允许进入技术架构冻结补充 / 决策准备；不允许进入 Stage 3。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否；当前为 Pass with Conditions。
- 冻结范围：无。
- 未冻结内容：真实 Tauri capability、插件、WebView / CSP、debug / release 包、OS 路径行为、updater / sidecar、IPC 命令签名、API、Schema、文件布局、桌面壳、技术架构整体。
- 是否允许进入下一任务：Conditional。条件是后续冻结决策必须明确：真实 Tauri 集成首次引入或能力变更时，本矩阵必须迁移复测；复测前相关能力关闭。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是。

## 需要用户确认的事项

1. 是否采纳 P2-015 的 `Accepted / Pass with Conditions` 结论。
   - PM 建议：采纳，但不得视为真实 Tauri 包安全通过。
   - 可选方向：采纳等价 harness 条件通过；或要求先做真实 Tauri 包复测再进入冻结决策。
   - 不确认的影响：技术架构冻结继续无法收口。

2. R-0040 风险状态如何处理。
   - PM 建议：保持 Open / Conditional，不完全关闭；在真实 Tauri debug / release / 平台矩阵通过前，相关能力必须关闭。
   - 可选方向：条件接受并记录复测触发器；或保持完全 Open 并新增实际 Tauri 包窄测任务。
   - 不确认的影响：后续可能误把等价 harness 通过当成真实桌面壳安全通过。

## 整改建议

无强制返工。若用户要求“真实 Tauri 包通过后再冻结”，需新增一个实际 Tauri 集成窄测任务；否则可把本结果作为冻结条件输入，并在冻结决策中写明后续复测触发器和能力关闭规则。

## 可接受内容

- Renderer 零通用 OS 能力。
- IPC 白名单与未知命令默认拒绝。
- 后端路径 / scope / 授权 / generation / lease 重检。
- Vault 零写、零删、零改名。
- 导出只写授权目标，覆盖 / 合并需确认。
- IPC 响应保留用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认等内容身份。
- 日志最小化和禁止正文 / 真实路径泄漏。

## 不接受或需谨慎内容

- 不得把等价 harness 通过外推为真实 Tauri capability 安全。
- 不得冻结 Tauri、IPC 签名、capability 名称、插件策略、CSP、路径库或打包配置。
- 不得启用真实 Vault、真实导出、真实文件系统广泛 scope 或正式桌面端能力，除非迁移矩阵复测通过。

## 对项目文件的更新建议

- `TASK_REGISTRY.md`：P2-015 更新为 Accepted。
- `FREEZE_STATUS.md`：P2-015 更新为 Pass with Conditions；技术架构仍未冻结。
- `DECISION_LOG.md`：新增 PM 接受 P2-015 的决策记录。
- `RISK_LOG.md`：R-0040 保持 Open / Conditional，并记录实际 Tauri 复测触发器。
- `CURRENT_STATUS.md`：更新等待用户确认事项。

## 下一步任务建议

等待用户确认是否采纳 P2-014 与 P2-015。若采纳，可启动技术架构冻结补充 / 决策准备；仍不得进入 Stage 3。

## 聊天回复边界

聊天中只输出验收结论、资产状态、下一步 / 下一阶段状态、修改文件和需要用户确认的问题。
