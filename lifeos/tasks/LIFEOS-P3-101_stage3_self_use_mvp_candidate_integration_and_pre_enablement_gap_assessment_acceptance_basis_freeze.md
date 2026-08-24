# LIFEOS-P3-101 Acceptance Basis Freeze｜有限 Stage 3 自用 MVP 候选整合与真实启用前差距评估

## 冻结信息

- 任务 ID：`LIFEOS-P3-101`
- ABF ID／版本：`ABF-P3-101-v1`
- 生效决策：`D-0415`
- 冻结完成时间：2026-08-23 08:47:09 CST (+0800)
- 时间语义：以上时间是 PM 创建本 ABF 时取得的已发生本地时间；文件 SHA-256 由写入完成后计算并记录在任务卡和 D-0415，本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 只读建立当前有限 Stage 3 自用 MVP 候选的事实基线，复核 Stage 3→4 五项硬门槛及 Gate 1／3／4／5，并输出且只输出一个后续方向：
  1. `Recommend Separate Limited Real-Use Enablement Task`；
  2. `Recommend Separate R-0040 Tauri/IPC Validation Task`；
  3. `Hold Limited Stage 3 / Close One Named Gap First`；
  4. 必要输入或账本冲突无法安全消解时输出 `Blocked`。
- 本任务不批准或执行推荐方向。
- 不冻结：工程候选、工程基线、Schema/API、技术架构、真实本地能力或 Stage 4。
- 非范围：不修改工程、Review、Evidence、Manifest、风险、冻结状态或阶段；不访问真实个人数据／文件／DB／路径；不启用 Vault、Tauri/IPC、网络、云／第三方、导出、同步、多设备、L3 或外部用户。

## 授权与能力边界

- 允许写入：仅 P3-101 自身 deliverable、task-owned Evidence／local precheck；PM 验收前专项会话不得修改项目账本。
- 允许读取：任务卡列明的当前账本、Stage Gate、治理文件及固定 Review／Evidence 摘要。
- 允许入口：只读文本定位、hash／Manifest 复算和结构化差距矩阵；不得运行真实能力或使用真实数据。
- 严格只读：P3-079 至 P3-100 的任务、工程、deliverable、Review、Evidence、Manifest；全部项目账本由 PM 独占维护。
- 临时数据：如需结构化脚本，只能在新建 `/private/tmp/lifeos-p3-101-*` 使用固定非敏感元数据，不得复制或读取真实个人内容，结束时精确清理。
- 后续授权：真实个人数据／路径／DB、Tauri/IPC、R-0040 风险关闭、工程基线恢复、冻结或 Stage 4 均须另建任务并再次获得用户明确确认。

## 引用的 L1

- L1-1 数据主权；L1-2 内容身份；L1-3 生命周期完整；L1-4 失败关闭；L1-5 用户控制；L1-6 审计可信；L1-7 Evidence 诚实；L1-8 历史保全；L1-9 授权不漂移；L1-10 可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权、隔离与冻结先后 | P0 | 用户已授权创建；任务卡投递至未承担 P3-097/P3-098 实现或评审的新会话；ABF hash 匹配且冻结早于接收时间 | Blocked |
| ABF-I-02 | 当前账本事实一致 | P1 | CURRENT_STATUS、TASK_REGISTRY、FREEZE_STATUS、RISK_LOG 和 D-0414/D-0415 无无法解释冲突 | Blocked 或 Rework |
| ABF-I-03 | 候选能力地图完整 | P1 | P3-079/080、P3-085–092、P3-097/098 与 P3-100 当前结论、适用边界和未冻结状态逐项列明 | Rework |
| ABF-I-04 | Stage 3→4 硬门逐项判断 | P0 | 可真实使用 MVP、基础导出、基础权限设置、错误／数据恢复策略、Alpha 使用说明逐项标为 Met／Partial／Not Met／Unknown，并引用当前证据 | Rework |
| ABF-I-05 | Gate 判断诚实 | P0 | Gate 1、3、4、5 分别判断；受控合成或固定夹具证据不得外推为真实能力、真实用户价值或 Stage 4 Pass | Rework |
| ABF-I-06 | R-0040 边界独立 | P0 | 明确 R-0040 仍为 Open / Conditional；不得用 R-0051 的有限关闭或非 Tauri Evidence 抵消 | Rework |
| ABF-I-07 | 真实启用差距明确 | P0 | 区分“固定非敏感本地夹具可复核”和“本人真实使用已授权／可启用”，列明缺失确认、能力和 Evidence | Rework |
| ABF-I-08 | 单一方向公式 | P1 | 仅基于冻结矩阵选择一个方向；不得并行创建多个任务或把建议写成已授权 | Rework |
| ABF-I-09 | 无越权状态变化 | P0 | 不改工程、历史资产、风险、冻结、基线或阶段；不运行真实能力；临时残留为零 | Rework 或 Blocked |
| ABF-I-10 | Evidence 与结论可复核 | P1 | 事实、推断、建议、待确认分离；每项判断有路径／行号或 hash／Manifest 依据；计数完整 | Rework |

## 冻结验收矩阵

| 行 ID | 独立动作 | 通过条件 | Evidence |
|---|---|---|---|
| ABF-M-001 | 核验任务投递、会话隔离、接收时间和 ABF hash | I-01 成立 | `session_start.json` |
| ABF-M-002 | 定向对账五份当前账本及 D-0414/D-0415 | 无无法解释冲突 | `ledger_reconciliation.json` |
| ABF-M-003 | 建立当前候选能力与边界地图 | 指定任务线逐项覆盖 | `candidate_capability_map.json` |
| ABF-M-004 | 逐项评估 Stage 3→4 五项硬门槛 | 五项均有状态、依据和缺口 | `stage_gate_matrix.json` |
| ABF-M-005 | 逐项评估 Gate 1／3／4／5 | 四 Gate 均有诚实结论 | `stage_gate_matrix.json` |
| ABF-M-006 | 独立核对 R-0040 与 R-0051 边界 | 无风险外推或混并 | `risk_boundary_matrix.json` |
| ABF-M-007 | 建立真实启用前授权／能力／Evidence 差距表 | 无 Unknown 被写成满足 | `pre_enablement_gap_matrix.json` |
| ABF-M-008 | 应用单一后续方向决策公式 | 只选择一个允许结果 | `next_direction_decision.json` |
| ABF-M-009 | 核对全部输入 before/after 状态及临时清理 | 只读资产未变、残留为零 | `input_integrity.json`, `temporary_residue.json` |
| ABF-M-010 | 生成交付物、计数与非自指 Manifest | 10/10 行可复核，计数齐全 | deliverable, `MANIFEST.md` |

## 方向选择公式

- 若五项硬门槛中的下一最小缺口是“有限本人真实使用的授权／运行边界”，且 R-0040 不被该入口触发：选择 `Recommend Separate Limited Real-Use Enablement Task`。
- 若下一最小且不可绕过的缺口明确是 Tauri capability、IPC、WebView/CSP 或平台路径行为：选择 `Recommend Separate R-0040 Tauri/IPC Validation Task`。
- 若存在更小、仍处于有限 Stage 3 且不需要真实启用／Tauri 的单一产品或 Evidence 缺口：选择 `Hold Limited Stage 3 / Close One Named Gap First`，只能命名一个缺口。
- 若必要输入、账本一致性、隔离性或授权不可得：选择 `Blocked`。
- 不得选择 Stage 4 Pass、风险关闭、资产冻结、基线恢复或多个并行方向。

## Evidence 与 Pass 公式

- 必须提供 P3-101 自身 Evidence：上述 10 行结构化结果、引用路径／行号、必要 hash／Manifest 结果、输入完整性、临时残留、复核命令和非自指 Manifest。
- 任务完成：10/10 行实际核对；P0/P1/P2/Unknown/Not Implemented 计数明确；结论符合四分方向公式；历史只读和范围关闭成立。
- `Blocked` 是必要输入或授权不可得时的有效结果，不得伪造事实填补。
- 本任务是高风险阶段／真实启用前治理判断；可跳过本地模型预检，但必须在交付物注明本地模型不得决定阶段、风险或真实能力边界。

## Rework、退出与新任务

- 正式 Rework：0/2；仅同一结果、同一只读输入、同一授权与本 ABF 不变时允许 Rework。
- 任一真实能力、数据、路径、Tauri/IPC、风险关闭／重开、工程变更、Schema/API、冻结、基线恢复或阶段切换必须停止，并另建任务、新授权、新 ABF。
- 两轮正式 Rework 后仍未通过，P3-101 以 `Closed — Acceptance Not Met` 收口，不得继续 attempt-3。
- 专项会话不得创建或启动其推荐的后续任务。

## 启动前质疑窗口

- 专项会话在任何 Evidence 动作前核对本 ABF、任务卡、投递时间、允许读取范围和四分结果公式。
- 歧义必须在执行前回报 PM；启动后不得修改本 ABF。
