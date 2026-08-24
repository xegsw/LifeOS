# LIFEOS-P3-101 resume-1｜有限 Stage 3 自用 MVP 候选整合与真实启用前差距评估

## 唯一方向

**`Recommend Separate Limited Real-Use Enablement Task`**

这只是一个尚未授权执行的后续方向。本任务不创建、不启动该任务，不启用真实数据／路径／DB，不改变风险、冻结、工程基线或阶段状态。

## 恢复依据

- D-0416 已验证上一轮 `Blocked` 正确，并由 PM 修正 `FREEZE_STATUS.md` 的陈旧当前摘要。
- 最新 `CURRENT_STATUS.md`、`FREEZE_STATUS.md`、`TASK_REGISTRY.md` 与 D-0416 一致允许同一 P3-101 在未变化的 `ABF-P3-101-v1` 下恢复。
- Blocked 不计 Rework；当前仍为 0/2。
- 初次 Blocked 交付物、Evidence、PM Review 与 PM Evidence 均保持只读；本轮只写入 `resume-1` 隔离目录。

## 未变化的事实基线

- 当前仍为有限 Stage 3；Stage 4 未准入。
- 五项硬门仍为 Partial：可真实使用 MVP、基础导出、基础权限设置、错误和数据恢复策略、Alpha 用户使用说明均没有真实启用 Evidence。
- Gate 1／3／4 实体状态仍为 Partial；Gate 5 仍为 Not Met。
- P3-079/080、P3-085–092、P3-097/098 的 Pass 只在各自合成／固定非敏感／task-local 边界成立；候选均 Not Frozen。
- R-0040 保持 `P0 / Open / Conditional`。
- R-0051 保持 `P0 / Closed / Limited Controlled Boundary`，且真实数据／路径／DB、行为或 hash 变化会触发重开或等价风险处理。

这些事实继续由初次提交的 `candidate_capability_map.json`、`stage_gate_matrix.json` 和 `risk_boundary_matrix.json` 支撑；本轮已复算其 hash 未变。

## 为什么选择有限真实使用启用

当前最小且不可绕过的缺口，是把“固定非敏感 task-local 候选”推进到“用户明确授权的有限本人真实使用边界”，并取得一次真实运行 Evidence。P3-097/P3-098 已为 CLI／本地完成点提供受控技术候选，但没有授权使用个人输入、真实路径或真实 DB，也没有真实使用结果。

这一最小入口可以保持 CLI-only：只允许用户明确输入的低敏感文本、一个新建专用自用目录和新建本地 DB；继续关闭 Tauri/IPC、Vault、真实文件导出、网络、云／第三方、同步、多设备、L3 与外部用户。因此 R-0040 虽继续开放，却不是此最小入口的前置触发项。

不存在更小的非真实能力缺口：

- 真实权限设置和恢复 Evidence 依赖先有一个获授权的真实数据流与 DB／路径边界。
- Alpha 使用说明必须与实际启用行为一致，不能先把受控候选写成已可真实使用。
- Gate 5 的本人自用价值、反证和退出 Evidence 也必须从真实使用开始。
- 基础真实文件导出涉及另一条文件／路径授权，并可能触发 R-0040，不应混入首个 CLI-only 切片。

## 推荐任务的严格边界

未来若由 PM 创建该任务，必须重新取得用户明确确认并冻结新 ABF，至少写明：

- 精确的低敏感用户输入类别；
- 一个全新、专用的自用目录和全新本地 DB；不得读取或迁移既有个人 DB；
- 仅允许的 CLI 入口；
- 首次、重复／幂等、关闭重启、失败、清理、审计和用户可见状态 Evidence；
- 触达真实数据／路径／DB 时，R-0051 重开或等价风险的独立治理方式；
- 全新隔离独立复评、停止条件和退出／清理方式。

该任务不得混入 Tauri/IPC、Vault、文件导出、网络、云／第三方、同步、多设备、L3、外部用户、Schema/API 冻结、工程基线恢复或 Stage 4 准入。

## 计数

- 指定风险事实：P0=6、P1=1、P2=0、Unknown=0、Not Implemented=0；R-0040 开放，R-0051 仅有限关闭。
- 本轮决策基础：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0。
- P3-101 resume-1 交付质量：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0。
- 方向数量：1；创建任务数量：0；执行任务数量：0。

## 角色与关卡

- 主责：产品 PM／Stage Governance Analyst；已完成单一方向公式。
- 协审：技术架构、AI 信任与安全、数据／领域、独立 QA；已核对 CLI/Tauri 分界、真实数据授权、风险重开条件和历史保全。
- Gate 1／3／4：评估完整性通过，实体仍 Partial。
- Gate 5：评估完整性通过，实体仍 Not Met。
- 仍需 PM／用户确认：是否采纳本方向；如采纳，必须由 PM 另建任务并取得真实数据／路径／DB 的单独明确用户确认。

## 本地预检

Skipped。本轮仍是阶段和真实启用前的高风险治理判断；本地模型不得决定阶段、风险或授权边界。
