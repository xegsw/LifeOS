# LIFEOS-P3-141 Phase B — 独立评审 Attempt 3

## 评审信息

- 对应任务 ID：LIFEOS-P3-141
- 是否为受控能力包：Yes
- 被评审候选：commit `51be094af913b8850d57a32774c83f72cc254dce`；tree `79 / 6a45b656a7bd1203485818872242d4ce2b9db572f197bec869356a6d807a87e1`
- 独立评审角色：隔离 Independent Review
- 协审视角：Provider/安全、路径所有权、Health 边界、Memory/State、Evidence 谱系、实际 Tauri 可观测性
- 评审关卡：L3 Phase B
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-3/`
- 结论：**Rework**（并有 actual-Tauri `Blocked / Unknown` 子项）
- 风险等级：L3 / P0
- 触发事实：任务合同要求全新隔离独立复评；候选只读。

## 独立性与边界

- 本轮在接触候选前已写入 `test_design.md`、`write_allowlist.md` 和 `precontact_seal.md`；固定输入 12/12、P3-139/P3-140 谱系与候选前后 tree hash 均由 review-owned verifier 复算。
- 候选、其 Evidence 与历史评审均保持只读。875e 历史评审为失败历史；0976 attempt-2 仅作为已被当前固定候选和本次合同取代的历史记录，未复用其设计、PID、DB、窗口、截图或结论。
- 本轮只写入本 attempt 根及唯一合成临时根。没有访问、探测、hash、创建或清理 Pilot-6 或其 `capture.sqlite`；没有读取真实文本、真实 Provider、凭据或发起网络。
- `tools/independent_verifier.py`、结构化结果、变异脚本与非自引用 Manifest 均在本根保留。候选的 43 条测试仅列为辅助信息，不构成独立通过证据。

## 评审摘要

1. 固定输入 12/12、P3-139 `77/63e2…cc9e`、P3-140 `79/6d56…9940` 与候选前后 `79/6a45…87e1` 全部一致；候选未被本评审修改。
2. 候选静态表面保留精确 20 IPC、四选一 Provider、首发锁定、receipt 先于 root、ownership/sidecar 与 Context Resolver/feedback 的部分失败关闭 seams。
3. 独立验证明确发现 5 项 P0：真实 Work 总额度为 3 而非 14；没有每日最多 1 条；没有所需五项结构化非医疗 Health 字段；没有已确认 Durable Memory ≤3；真实流仍保留 P3-133 标识。
4. 5/5 review-owned 语义变异（receipt、root ownership、Provider lock、Health boundary、feedback/budget）均可检测；它们证明的是已有静态 guard，并不能修复上述 P0。
5. receipt-enabled actual-Tauri 仅尝试一次离线构建即在 linker 停止，未形成 PID→AXWindow→AXWebView 绑定或三档截图。该项为 `Blocked / Unknown`，未以静态扫描、网页 fixture 或候选测试代替。
6. 因 P0 不为零且存在 Unknown/Blocked，Phase B 不通过；Phase C、Phase D、Phase E 均保持 Pending / Not Implemented。

## 已通过内容

- 固定输入、谱系和候选树的复算，以及本次候选只读边界。
- 20 IPC 与 Provider 枚举/锁定的静态合同表面。
- receipt-before-root、root ownership/sidecar、budget 失败、Health request-local removal、feedback stale-path 的静态 seams。
- 5/5 独立语义变异检出。
- 临时根按 marker 精确清理（见 `evidence/cleanup_receipt.json`）。

## 关键问题与 Closure List

| 优先级 | 必须回到同一 P3-141 Closure Cycle 的修正 |
|---|---|
| P0 | 将 Work 建模改为 7–14 天、每日最多 1 条、总数最多 14 的可审计且重启安全的额度规则；删除旧的 real limit=3 语义。 |
| P0 | 定义并实现结构化、最小、非诊断的 Health/Fitness 输入：sleep duration range、energy 1–5、soreness/pain boolean、training load L/M/H、available time；在 UI/IPC/SQLite/Today/feedback/失败关闭中保持一致。 |
| P0 | 在真实合同路径上实施用户确认的 Durable Memory 上限 3，并提供第 4 条写前拒绝和重启验证。 |
| P0 | 消除 real-flow 中 P3-133/P3-131 旧 ID、request key、source/artifact 与错误文案；替换为 P3-141 当前合同身份。 |
| P0 | 修正后使用全新隔离评审重新执行至少 43 条 review-owned 正/负动态路径，包括 root mutation 和 restart 的 pre/post 计数。 |
| P0 | 重新取得 receipt-enabled actual-Tauri 三档的本次 PID→AXWindow→AXWebView 直接绑定与固定合成脱敏截图；不得以辅助测试替代。 |

## ABF 逐行结果

| ABF 行 | 状态 | 依据 |
|---|---|---|
| M-001 | PASS | 12/12 固定输入与 P3-139/P3-140 谱系复算。 |
| M-002 | UNKNOWN | 仅静态 ownership seams；未完成独立动态 path mutation matrix。 |
| M-003 | PASS | Phase C 未启动；无 Pilot 根触达。 |
| M-004 | PASS (static) | 四选一、显式步骤和首发锁 static seams；无真实 Provider。 |
| M-005 | UNKNOWN | 无合格的 actual-Tauri/dispatch 动态证据。 |
| M-006 | PASS | 本轮合成、零真实内容/凭据/Provider/网络。 |
| M-007 | FAIL / P0 | Memory≤3 与结构化 Health 合同未实现。 |
| M-008 | Pending / Not Implemented | Phase C 用户 7–14 日使用未开始。 |
| M-009 | UNKNOWN | 缺少合格 P3-141 Health/Today 动态结果。 |
| M-010 | UNKNOWN | 缺少合格 request/receipt 动态审计。 |
| M-011 | UNKNOWN | 仅 stale seam，未有 P3-141 feedback-adaptation 动态证明。 |
| M-012 | PASS (static) | request-local Health removal seam。 |
| M-013 | FAIL / P0 | 结构化 Health 风险信号合同尚不存在。 |
| M-014 | UNKNOWN | 未完成 review-owned runtime failure matrix。 |
| M-015 | UNKNOWN | 未完成 P3-141 owned restart 动态验证。 |
| M-016 | BLOCKED / UNKNOWN | 无 PID/AXWindow/AXWebView 三档实际 Tauri Evidence。 |
| M-017 | Pending / Not Implemented | Phase C 真实非内容收据未开始。 |
| M-018 | REWORK | 本独立评审已完成，但候选有 5 项 P0，故不构成独立 Pass。 |
| M-019 | PASS | 唯一 marker-gated temporary root 已精确清理。 |
| M-020 | PASS | 本 review 根的 Manifest 为非自引用且逐文件 hash 可复算。 |

## 关卡、风险与 PM 决策

- Gate 1 产品一致性：**Rework**（核心 7–14 日 Work/Health 合同未实现）。
- Gate 2 数据与来源：**Rework**（Memory 上限/真实路径语义未闭合）。
- Gate 3 AI 权限与信任：**Rework**（实际 Tauri 与最小披露动态证据不足）。
- Gate 4 技术可行性：**Rework**（actual-Tauri three-viewport 证据 Blocked/Unknown）。
- Gate 5 用户价值验证：**Pending / Not Implemented**（Phase C 未启动）。
- 需 PM 决策：无需为本结论新增产品/权限/风险决定；候选应在同一 P3-141 Closure Cycle 完成上述 P0 修正后，再派发全新隔离独立复评。

## 最终建议

不建议进入 Phase C、Phase D、PM Pass、风险关闭、冻结或 Stage 4。保持 P3-141 在同一 Closure Cycle 内返工；新候选完成合同内修正和 review-owned 动态 Evidence 后，必须由新的隔离评审会话重评。
