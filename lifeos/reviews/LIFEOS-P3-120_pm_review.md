# LIFEOS-P3-120 PM Review｜以人为主体的产品 Runtime MVP 实现

## 验收信息

- 任务 ID：`LIFEOS-P3-120`
- Acceptance Basis Freeze 路径：`lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation_acceptance_basis_freeze.md`
- ABF ID／版本／PM 记录 SHA-256：`ABF-P3-120-v1` / `e18c463ffb59f1bb80ba55d48a61009792cbd36190d998867d6f08a7aaebe219`
- ABF 是否在专项会话开始前 Frozen：Yes
- 本次反例是否全部映射到既有 L1/L2：Yes；L1-7/L1-10→I-04/I-05/I-07、M-004/M-006～M-010；L1-9/L1-10→I-01/M-001
- 正式 Rework 次数／上限：`2/2`；用户已采纳并授权最终 Manifest 收口
- 是否为受控能力包：Yes
- 能力包边界与包内整改记录：Rework-1 已补齐真实 App 闭环与模型记录；candidate、ABF、目录、数据、三 IPC、Schema/API 与风险边界均不变。当前只缺最终 retained-asset Manifest 闭环。
- 任务名称：以人为主体的产品 Runtime MVP 实现
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-120_pm_review.md`
- 执行授权证据核验：专项报告记录收到任务卡绝对路径；任务卡已记录用户投递前 synthetic-only Tauri/IPC 单独确认。报告未提供接收时间，不影响范围授权判断。
- 任务验收状态：`Rework 2/2 / User Adopted / Final Manifest Closure Authorized / Acceptance Basis Unchanged`
- 资产冻结状态：`Not Frozen`
- 是否允许进入下一任务：No
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：No；当前仍为活动能力包
- 实际执行 Agent：Codex；用户已确认实际模型／推理强度为 `gpt-5.6-terra + xhigh`
- Agent 与任务匹配度：High（工程与 actual-app 闭环）；最终 Manifest 分层不足
- 更新时间：2026-08-25

## PM 总结

- 任务卡、Frozen ABF、source allowlist 与交付授权边界成立；未发现历史资产、Pilot、真实数据、网络、模型能力或禁止 IPC 被启用。
- Engineering Manifest `101/101` 与 P3-111 positive source allowlist `72/72` 的 bytes/SHA-256 由 PM 独立复算全部匹配。
- PM 在唯一临时根以 Rust/Cargo `1.98.0` 离线复跑 `cargo test --locked --offline`，`9/9` 通过；路径/type/link、原子失败、哨兵、IPC allowlist 和底层生命周期实现具备可复核的正向证据。
- 提交的 `actual_app_replay.sh` 只证明 `.app` 两次启动、五秒存活与终止；没有实际导航核心页面，也没有通过 packaged renderer 执行 capture、repeat、second、refresh、reopen。
- `ui-state-contract-results.json` 是源码状态合同；`runtime-results.json` 来自 Rust unit test。二者不能替代 ABF-M-004/M-006～M-010 冻结要求的实际 App、IPC、DB、UI 三层证据。
- 初次提交资产没有记录实际模型配置；用户在采纳 Rework 时明确确认原工程会话实际使用 `gpt-5.6-terra + xhigh`，M-001 的模型路由 Unknown 已关闭。Rework Evidence 仍应把该确认写入结构化结果，避免再次依赖聊天。
- Rework-1 已实际完成 15 步 packaged-app 手工闭环；PM 视觉抽验、时间／PID／DB／审计序列核对及隔离 verifier 复跑均通过，初次 actual-app P0/P1 已关闭。
- 当前交付物因 Rework 更新为 SHA-256 `0f5ff548…`，初次 Manifest 仍固定旧交付物 `ef644706…`，当前复算为 `100/101`；Rework Manifest `59/59` 匹配但没有包含更新交付物，最终 M-015 Manifest 层未完成。
- 当前：`P0=1、P1=0、P2=0、Unknown=0、Not Implemented=1`，判定 `Rework 2/2 / Awaiting User Adoption`。
- 本轮高风险判断跳过本地模型预检：Tauri/IPC、持久化与 Evidence 真实性不能由本地模型决定；PM 已完成独立 hash、源码、runner 与离线测试复核。

## 两层验收治理核对（D-0401 起）

- 违反或满足的 L1 条款：L1-1/2/3/4/5/6/8/9 的工程与静态结果基本满足；L1-7 Evidence 诚实与 L1-10 可复核性未满足；模型证明同时涉及 L1-9。
- 冻结 L2／ABF 条款与矩阵行：I-01/M-001；I-07/M-004；I-04/I-05/M-006～M-010。
- PM 是否在提交后新增了无法映射到 L1/L2 的标准：No
- 新发现问题分类：当前任务失败；唯一当前缺口为 M-015 final Manifest；视觉差异继续为不阻断本 ABF、但必须后继收口的产品缺口。
- 是否需要实质修改 ABF：No
- 是否仍满足同任务 Rework 全部条件：Yes
- 是否达到两轮正式 Rework 上限：Yes；本轮整改若再次未通过，必须关闭当前任务并新建后继任务／新 ABF。
- 终止状态：N/A
- 新任务触发理由（如适用）：N/A

## 角色与关卡验收

- 主责角色覆盖情况：Rust/Tauri、SQLite、前端集成、路径与失败关闭实现已覆盖。
- 协审角色覆盖情况：产品身份、数据安全、AI 关闭态和 Evidence 已核；真实 App 体验／闭环关卡未通过。
- 已通过关卡：固定输入、positive source allowlist、离线 build/test、三 IPC 静态关闭、底层生命周期、失败关闭、路径/type/link、实际 App 全页导航、renderer→IPC→DB→UI capture/repeat/refresh/reopen、模型记录与精确清理。
- 未通过或需后续确认关卡：最终 retained-asset Manifest 闭环。
- 是否属于关键冻结事项：No；本轮不冻结产品或 runtime。
- 是否需要独立评审：Yes，但仅 PM Pass 且用户采纳后新建；当前不得进入。
- 独立评审路径：N/A
- 独立评审结论：N/A
- 是否允许进入下一任务或下一阶段：No / No

## 验收与冻结区分

- 任务是否验收通过：No
- 对应资产是否冻结：No
- 冻结范围：仅既有 `ABF-P3-120-v1` 与 source allowlist 继续 Frozen，候选不冻结。
- 未冻结内容：P3-120 candidate、产品视觉、IA、runtime、架构、Schema/API、风险与阶段。
- 是否允许进入下一任务：No
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：No
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，更新为 Rework 1/2。

## 受控能力包关卡

- 是否完成交付前包内自检关卡：Rework actual-app 自检完成；最终 Manifest Pass 公式仍不成立。
- 干净副本首次／幂等／重启演练结果：Rust unit/integration 与 actual packaged app 三层闭环均通过。
- 原子失败／清理／拒绝与审计追溯结果：底层测试通过；PM 临时根精确清理。
- 验收标准→测试→Evidence 矩阵是否完整：动态矩阵完整；M-015 最终 Manifest 不完整。
- 测试／runner、逐项结果、日志／快照、hash／Manifest 与复跑入口是否可复核：动态 Evidence 可复核；最终交付物 lineage 未被当前 Manifest 覆盖。
- 历史只读资产及禁止能力关闭态是否已核对：Yes
- 执行侧自检数量与未覆盖项是否如实报告：Rework 动态闭环如实；最终 Manifest 缺口未披露。
- 是否完成包内实现、回归、必要补测、Evidence 与文案对齐：功能与动态 Evidence 完成；Manifest 收口未完成。
- 是否首次正式 PM 验收：No；本次为 Rework-1 复验并触发正式 Rework 2/2。
- 是否需要／已经进入全新隔离独立复评：需要但尚不得进入。
- 是否因 P0/P1、Evidence 冲突、hash 实质变化或独立性不足而必须回包内整改：Yes
- 是否触发新的用户确认：已完成；用户采纳 `Rework 2/2` 并授权仅执行 final Manifest closure，不扩大能力授权。

## 初次发现（已由 Rework-1 关闭）

### PM-P0-001｜实际产品闭环被底层单测替代

- 映射：L1-7、L1-10、I-04、I-05、M-006～M-010。
- 证据：`tests/actual_app_replay.sh` 不执行 UI 动作；`tools/run_runtime_evidence.py` 只运行 Rust lifecycle test；`tools/build_matrix.py` 据此把 M-006～M-010 写为 PASS。
- 结论：P0。candidate 可能实现了能力，但当前没有证明 packaged renderer、Tauri IPC、DB 与 UI 三层一致。

### PM-P1-001｜核心页／态实际导航未执行

- 映射：L1-7、L1-10、I-07、M-004。
- 证据：actual-app runner 仅启动、等待、结束；M-004 把源码状态合同和单张 Today screenshot 合并为 PASS。
- 结论：P1。源代码包含页面状态不等于实际 `.app` 中全部可达。

### PM-U-001｜实际模型路由不可独立确认（已由用户确认关闭）

- 映射：L1-9、L1-10、I-01、M-001。
- 证据：专项报告只写“全新 Codex 工程执行会话”；`fixed-inputs.json` 无实际模型与推理强度字段。
- 初次结论：Unknown。用户已明确确认原工程会话使用 `gpt-5.6-terra + xhigh`，当前 Unknown 关闭；Rework 结构化 Evidence 仍须记录该确认。

### 数量

- 初次 P0/P1、模型 Unknown 与 M-004/M-006～M-010 Not Implemented 均已关闭。

## Rework-1 复验发现与当前计数

### PM-R1-P0-001｜更新交付物未进入最终 Manifest

- 映射：L1-7、L1-8、L1-10、I-10、M-015。
- 证据：初次 Manifest 共 101 行，当前 `100/101` 匹配；唯一 mismatch 为交付物从 `ef644706…` 更新为 `0f5ff548…`。Rework Manifest 自身 `59/59` 匹配，但未包含当前交付物。
- 结论：P0 / Not Implemented。历史 Manifest 可以保留旧 hash，但必须有新的最终 Manifest 明确覆盖更新后的交付物和 Rework 资产，不能让整体候选处于无当前完整 lineage 状态。

### 当前数量

- P0：`1`
- P1：`0`
- P2：`0`
- Unknown：`0`
- Not Implemented：`1`（M-015）

## 整改建议

1. 不重跑 `.app`，不修改 candidate、ABF、初次 Evidence 或 `evidence/rework-1/` 现有文件，不触碰任何临时 Runtime/Pilot/真实资产。
2. 仅在 P3-120 自有 Evidence 下新增 `final-manifest-closure/`（或结构等价目录），生成当前非自指总 Manifest，至少覆盖：当前交付物、candidate/current inventory、initial Manifest 作为历史层、Rework-1 Manifest、DYNAMIC_CLOSURE、rework-results、PM Review 授权输入和新增 verifier/mutation Evidence。
3. 明确标记 initial Manifest 中旧交付物 hash 是历史提交快照，不伪称其当前仍为 101/101；由 final Manifest 提供当前交付物 hash。
4. verifier 必须复算 bytes/SHA-256、missing/extra、普通文件类型，并以 disposable copy mutation 证明：更新交付物遗漏、任一 payload 改动、额外文件和 historical/current lineage 混淆均 fail closed。
5. 这是 Rework 2/2；若再次未通过，不得继续第三轮同任务 Rework，必须关闭 P3-120 并创建新任务／新 ABF。

## 可接受内容

- P3-120 candidate、三 IPC 静态边界、synthetic-only DB、offline/model-disabled UI、路径/type/link 负测与原子失败测试可保留为同一能力包整改基础。
- Engineering Manifest、source lineage 与 PM 独立 Rust 9/9 结果可信。
- 当前 Today 截图只可作为页面非空与视觉方向辅助材料，不作为功能闭环证明。

## 不接受或需谨慎内容

- 不接受当前 `matrix-results.json` 的 15/15 总体 PASS。
- 不接受 source-state contract 替代 actual app navigation。
- 不接受 Rust lifecycle test 替代 packaged app 的 renderer→IPC→DB→UI 操作。
- 不因本次 Rework 推断 candidate 必然无法使用；结论是 Evidence／actual-app 完成定义未达到。

## 视觉差异的正式治理判断

P3-120 当前界面与 P3-116 已确定的设计方向明显不一致，不能把当前 P3-120 UI 表述为“已忠实实现 P3-116 高保真设计”。具体缺口包括视觉层级、页面空间关系、卡片／内容组织和整体产品气质没有形成可复核的一一继承合同。这是明确的产品一致性缺口，不是无关紧要的美化项。

但 `ABF-P3-120-v1` 明确写明“本轮不冻结视觉”，本轮 L2 只冻结 Icon Rail、Person 主体、页面集合、身份语义和 runtime 闭环，没有精确组件映射、布局规则或视觉差公式。依 D-0401，PM 不能在提交后把新的高保真一致性标准追溯加入本轮 Pass 公式，因此该缺口不计入当前 P3-120 的 P0/P1/P2，也不得塞入本次 Evidence-only Rework。

治理约束：P3-120 即使完成 runtime Rework，也只能作为“Person-centered runtime 技术候选”，不得据此宣称 P3-116 视觉实现完成、不得冻结组合产品候选、不得进入 Stage 4。后续应新建独立的“P3-116 设计忠实继承与 P3-120 runtime 组合收口”任务，以 P3-116 当前设计资产和 P3-120 runtime candidate 为固定输入，在启动前冻结页面／组件／状态／响应式映射及允许差异；完成后再对组合候选做全新隔离独立复评。

## 对项目文件的更新

- 更新：`CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`DECISION_LOG.md`、`FREEZE_STATUS.md`。
- 不更新：`RISK_LOG.md`；风险事实未改变，`R-0051` 维持原有限关闭，`R-0052` 维持 Open。
- 不更新：产品背景、架构、开放问题和 Agent scorecard。

## 下一步任务建议

- 用户已采纳 `Rework 2/2`。
- 现在回到原 P3-120 工程会话，仅执行 final Manifest closure；不重跑 actual app，不创建新任务。
- 再次提交后由 PM 复验；若仍未通过，关闭 P3-120 并新建任务／新 ABF。
- 鉴于已确认的视觉一致性缺口，PM 建议不要直接对当前视觉候选做最终组合独立复评；应先由用户授权创建新的设计忠实继承任务，再对完成后的 UI＋runtime 组合候选统一独立复评。

## PM Evidence

- `lifeos/reviews/LIFEOS-P3-120/pm_evidence/initial/assessment.json`
- `lifeos/reviews/LIFEOS-P3-120/pm_evidence/initial/rework_assessment.md`
- `lifeos/reviews/LIFEOS-P3-120/pm_evidence/initial/MANIFEST.md`
