# LIFEOS-P3-108 PM Review｜initial + rework-1 final

## 验收信息

- 任务 ID：`LIFEOS-P3-108`
- 任务名称：P3-104 + P3-106 组合候选全新隔离独立复评后继
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-108-v1`／`54cbb4a8d302a1dd4007bcdbd7c7844f0d98588f54c51d941e197a8176c1ae10`
- ABF 是否在专项会话开始前 Frozen：Yes。
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-108/independent_review.md`
- 专项 Evidence：`lifeos/reviews/LIFEOS-P3-108/evidence/MANIFEST.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-108/pm_evidence/initial/MANIFEST.md`
- 执行授权：用户将任务卡绝对路径投递至新独立会话；专项记录 2026-08-24 CST 接收，测试设计于 09:14:09 CST 落盘。
- 正式 Rework：2/2，已达到上限。
- 任务验收状态：`User Adopted / Closed — Acceptance Not Met / PM-Adjusted Rework 2/2 / Not Frozen`。
- 是否允许进入下一任务：Yes；用户已采纳并授权创建 P3-109，P3-109 已以新任务、新授权和新 Frozen ABF 登记为 Ready。
- 是否允许进入下一阶段：No。
- 实际执行 Agent：Codex 独立评审；会话独立性成立，`gpt-5.6-terra + xhigh` 由用户／PM 派发元数据确认，不声称从本地运行时独立读取。
- 更新时间：2026-08-24。

## PM 总结

1. 专项将结论写为 Blocked，但 PM 调整为正式 Rework 1/2。M-007 固定视觉比较、M-013 外部路径 actual-app 行及缺失的结构化生命周期 Evidence 都能在原 ABF 内完成，不属于纯外部条件阻断。
2. PM 复算专项 Manifest 31/31、Frozen 快照 21/21、P3-106 Manifest 325/325；P3-104 为 15 项当前匹配加唯一精确 `PASS_TIME_QUALIFIED`。独立测试设计先于 runner，正向 allowlist 未复制提交 Evidence／runner／tools，三个离线 locked build 退出 0。
3. 专项诚实保留 M-007、M-008、M-013、M-015 非通过，但 `matrix-results.json` 又把 M-001、M-009 至 M-012、M-014 写为 PASS，未满足冻结设计与 Evidence 合同。
4. 当前没有确认 P3-104/P3-106 组合候选存在工程 P0/P1。专项实际 app 截图和安全动作只作为 rework-1 的只读历史，不得补写为最终 PASS。
5. PM 调整计数：P0=2、P1=0、P2=0、Unknown=1、Not Implemented=9。

## Findings

### PM-P3-108-INIT-EV-01｜P0｜Open

冻结测试设计要求 M-001 记录实际会话、严格模型配置与 `authorization.json`，并规定“严格模型配置无法证明立即 Blocked”。提交明确称 `gpt-5.6-terra + xhigh` 标签不可观察，Evidence 中也没有 `authorization.json`，但矩阵仍把 M-001 写为 PASS。

该结果违反 L1-7、L1-10、ABF-I-01、I-12 与 M-001。PM 将 M-001 调整为 Unknown；下一轮必须由可记录的用户／PM 派发元数据确认实际配置，并落盘授权结构化记录。

### PM-P3-108-INIT-EV-02｜P0｜Open

测试设计在读取候选前冻结了以下具体 Evidence：`lifecycle/first.json`、三个 repeat/conflict/failure 独立结果、refresh/reopen 结果与日志、`denied.json`、逐类 path before/after、`negative-matrix.json`、a11y 闭环与扫描输出。专项 Manifest 31 项中均不存在这些文件。

`dynamic_closure.md` 的人工摘要和 UI 截图能证明可见页面状态，却不能在夹具已清理后独立证明 DB／audit／sentinel 数量、失败零副作用、进程退出输出与逐类 before/after。M-009 至 M-012、M-014 因此不得标 PASS。该结果违反 L1-3、L1-4、L1-6、L1-7、L1-10、ABF-I-09、I-10、I-12 与对应矩阵行。

### PM-P3-108-INIT-COV-03｜Not Implemented｜Open

- M-007：固定 P3-106 1280×1024 actual-app Evidence 与 Stitch 的独立目视比较未执行；该动作不要求改变当前系统显示。
- M-008：实际窄窗口截图为 768×832，不是冻结的 700×760；原工作区三态、滚动和精确窗口闭环未完成。应用窗口尺寸应由测试控制，不得修改系统显示缩放。
- M-013：外部路径没有独立 actual-app 行；静态 schema 拒绝不能替代实际负向动作。
- M-015：D17 截图可见 skip-link focus ring，但完整 Tab 顺序、Enter 后 main 落点、reduced-motion 和 scan 输出未闭环。

## 两层验收治理

- L1 映射：L1-3、L1-4、L1-6、L1-7、L1-10。
- L2 映射：ABF-I-01、I-06、I-07、I-09 至 I-12；M-001、M-007 至 M-015。
- PM 是否新增冻结标准：No；全部来自 Frozen ABF 和候选读取前已冻结的测试设计。
- 是否需实质修改 ABF：No。
- 是否满足同任务 Rework：Yes；用户结果、候选、目录、数据、IPC、依赖、视觉权威输入、风险、冻结与阶段均不变。
- 正式 Rework：1/2，未达上限。
- 初次验收当时终止状态：N/A；当时不创建 P3-109。最终关闭及后继创建以本文件后续章节和 D-0442／D-0443 为准。

## 计数

- P0：2；两项均为独立评审／Evidence 真实性与可复核性问题，不是候选缺陷。
- P1：0。
- P2：0。
- Unknown：1；M-001 实际模型／推理配置未被记录。
- Not Implemented：9；M-007、M-008、M-009、M-010、M-011、M-012、M-013、M-014、M-015。

## Rework-1 冻结范围

同一 P3-108 可在空 `lifeos/reviews/LIFEOS-P3-108/evidence/rework-1/` 全量重跑，初次 Evidence 全部只读。必须：

1. 写入 `authorization.json`，以用户／PM 可记录派发元数据确认 `gpt-5.6-terra + xhigh`、新执行时间、会话和授权。
2. 重新生成独立结构化 lifecycle／denied／path／negative／a11y／scan 结果及 raw app/process logs、before/after；不得从初次 Markdown 反向补写。
3. 独立比较固定 1280×1024 actual-app Evidence 与三张 Stitch；该比较不调整系统显示。
4. 通过应用窗口控制取得精确 700×760 和原工作区动态 Evidence；不得改变 macOS 显示缩放。
5. 增加未创建外部目标的外部路径 actual-app 启动拒绝行，证明变更前 fail-closed。
6. 在用户手工开启 macOS“减少动态效果”后实际运行 reduced-motion；专项不得修改该系统偏好，用户在评审完成后手工恢复。
7. final verifier 必须验证全部 16 行、全部动态 ID、必需文件、hash、清理和负门，不得只信任矩阵状态字段。

## 本地预检

- 跳过。本轮为 P0 独立性、实际 Tauri/IPC、本地文件失败关闭与动态 Evidence 最终判断；本地模型不得代判。

## 资产、风险与阶段

- P3-104/P3-106 组合候选：Not Frozen；未确认工程缺陷，也未取得独立 Pass。
- P3-108 初次 Review／Evidence：只读保全；仅可新建 `evidence/rework-1/`。
- R-0040：Open / Conditional，不变。
- R-0051：Closed / Limited Controlled Boundary，不关闭、不重开、不扩大。
- R-0052：Open / Authorized Controlled Execution Boundary，不变。
- 工程基线、Schema/API、视觉资产：不恢复、不冻结。
- Stage 4：不允许进入。
- 风险事实未变化，`RISK_LOG.md` 不更新。

## 用户确认与下一步

- 用户已采纳 `PM-Adjusted Rework 1/2`，同一 P3-108 的 rework-1 授权生效。
- 用户已确认 rework-1 使用 `gpt-5.6-terra + xhigh`；`authorization.json` 必须记录本次用户确认与实际会话元数据。
- 用户已明确回复“已开启”，确认 macOS“减少动态效果”环境就绪；同一 P3-108 可复用独立评审会话执行 rework-1。若原会话无法可靠保持边界，可新建隔离会话，但任务与 ABF 不变。
- 取证结束后由用户手工恢复“减少动态效果”；全过程不调整系统显示缩放。

---

## Rework-1 执行回报｜待 PM 验收（非 PM 最终结论）

### 授权与边界

- 执行授权：用户于 2026-08-24 CST 再次明确指示“按 D-0440/D-0441 执行同一 P3-108 rework-1，使用 `gpt-5.6-terra + xhigh`，在空 `evidence/rework-1/` 全量重跑；不得调整系统显示缩放”。该确认已写入 `evidence/rework-1/authorization.json`。模型／推理标签由用户授权记录支持；本地界面并不声称能独立读取该运行标签。
- 环境事实：用户已在操作前手工开启 macOS“减少动态效果”。本轮未执行任何 macOS 偏好或显示缩放命令；实际 app 诊断面板显示“减少动态偏好：系统已启用”。
- 隔离与保全：候选、ABF、账本、风险和历史 Evidence 均未修改。受保护旧结果仅以 `lstat` 元数据核验，未读取其内容；三条 P3-107 保护临时路径保持缺失。

### 全新重跑结果

- 新 Evidence 根目录：`lifeos/reviews/LIFEOS-P3-108/evidence/rework-1/`。初次动态 Evidence 未用于本轮 PASS。
- 固定输入前／后快照均通过，21 个允许输入的 SHA-256 无差异：`snapshot-before.json`、`snapshot-after.json`。
- 历史 Manifest、正向 allowlist clean copy、静态反查与三个离线 locked build 全部通过；候选 renderer 未检出网络 API，capability 为空，CSS 含 reduced-motion 规则。
- 独立唯一 bundle 的实际 UI 与新 DB fixture 完成首存、重复幂等、冲突拒绝、注入原子失败、刷新、关闭重启、三态导航、禁用控件、未知 IPC／额外字段拒绝、Tab／Enter skip-link、reduced-motion、窄窗口交互及 schema 篡改拒绝。
- 八个启动前边界 probe（目录、软链、硬链、悬挂 final、journal、wal、shm、外部路径）全部 fail-closed；外部目标没有被创建。逐项 raw stdout/stderr、DB／fixture 前后状态和 actual-app AX／截图已保留。
- 本轮 test harness 曾产生一条早期结构化快照错误，原始 `runner-error.json` 保留；修正的是本轮新 runner 的排序处理与 renderer 扫描范围，随后全部受影响步骤在新隔离副本重跑。该修正没有改动候选，也没有将失败动作转写为通过。

### 验收矩阵与诚实结论

- `M-001`–`M-006`、`M-009`–`M-016`：PASS。
- `M-007`：UNKNOWN。三态实际 app 与三张 Stitch 权威图均已保留，但 Computer Use 输出为缩放后的 app capture，无法独立量测原生 1280×1024 窗口框；不以配置文件或视觉近似替代实际尺寸事实。
- `M-008`：UNKNOWN。已实际拖动至目标坐标并留存窄窗口／滚动／可操作控件证据，但同样无法从 CUA 取得可独立核验的原生窗口 rect，以证明“原工作区”及精确 700×760；全程未改系统显示缩放。
- 动态闭环 `D01`–`D03`、`D14`–`D15` 对应上述限制为 UNKNOWN；其余 `D04`–`D13`、`D16`–`D20` 为 PASS。
- 最终 verifier 直接读取 16 行矩阵、20 个动态动作、必需文件和 cleanup，结果为 `pass=false`，原因仅为 M-007／M-008 的两个 UNKNOWN；不得将本轮写为 Accepted、Frozen、风险关闭或 Stage 4 准入。
- 本轮包内自检计数：P0=0，P1=0，P2=0，Unknown=2，Not Implemented=0。未发现候选工程 P0/P1；这不是 PM 的正式验收或风险结论。

### Evidence 与清理

- 非自引用 Manifest：`evidence/rework-1/MANIFEST.md`，SHA-256 `76ffc3157e05f3eed3a68ce573b3f9aac6616f227e522a8e3d750f3199ef9493`。清理后的独立复算为 181/181 个非 Manifest 文件存在、大小和 SHA-256 均匹配。
- 清理记录：`evidence/rework-1/cleanup.json`，SHA-256 `92d1b1d3186b2e8f47da3ca0b91406c850850f579c8e16c5ed6f5b7c353413ea`。所有任务卡列举的本轮工作副本和 fixture 均已逐路径清除。
- Final verifier：`evidence/rework-1/final-verifier.json`，SHA-256 `a1f9e183937beeaf4129328cb31d7d91c3d0220729ed57826246c54f84665b99`。
- 本地预检：跳过。该回报涉及独立复评、文件失败关闭、实际 Tauri/IPC 与 P0 Evidence 真实性，按项目规则不让本地模型代判。

### 请求 PM 的下一步

本专项会话不作 PM 验收结论。请 PM 仅依据既有 L1/L2／ABF 处理两个可复核的 UNKNOWN：若仍坚持原生精确窗口尺寸为本轮硬性 PASS 条件，应在不改系统缩放的前提下指定可记录的原生窗口测量机制，或按验收治理决定是否需要新任务／新 ABF；不得把当前缩放截图提升为 PASS。取证已完成，用户现在可以自行恢复 macOS“减少动态效果”。

---

## PM 最终验收｜rework-1

### 结论

- PM 结论：`Closed — Acceptance Not Met`。
- 本次构成正式 Rework 2/2；两轮预算已用尽，同一 P3-108 不得继续 rework。
- Frozen ABF 未修改，新增判断均映射到既有 L1／L2；没有移动验收终点。
- 未确认 P3-104/P3-106 组合候选存在工程 P0/P1。关闭的是未完成独立复评闭环的 P3-108，不是把候选判定为工程失败。

### PM 复核成立的 Evidence

- rework-1 非自引用 Manifest 由 PM 独立复算为 181/181，路径、bytes、SHA-256 全匹配，无 missing／extra。
- 21 项固定输入前后快照无差异；P3-106 Manifest 325/325 与 P3-104 唯一 `PASS_TIME_QUALIFIED` 规则记录成立。
- 授权、测试设计先行、正向 allowlist、离线 locked test/build/bundle、静态 runtime／IPC／capability 检查均有结构化记录。
- lifecycle、denied、boundary、negative、a11y、reduced-motion 与 scan 的原始日志、AX、截图和 DB／fixture 状态资产均存在并进入 Manifest。
- PM 当前逐条核对 16 条 P3-108 精确临时路径与 3 条 P3-107 受保护路径，全部不存在；未执行 broad cleanup，未覆盖专项 Evidence。

### Findings

#### PM-P3-108-R1-EV-01｜P0｜Open

`finalize_rework.py` 的 `final_verify()` 只检查必需文件是否存在，并直接信任 `make_actions()`／`make_matrix()` 预赋的状态字符串。它没有独立验证 closure 资产 hash、DB／audit／sentinel 语义、cleanup 内容、负门真实非零或最终稳定 Manifest；而且 `final-verifier.json` 写入后 Manifest 又被重新生成。

这违反 L1-7、L1-10、ABF-I-12、M-016，以及本 PM Review 已冻结的 rework-1 第 7 项要求。即使本轮 verifier 诚实返回 `pass=false`，它仍不能证明 Evidence 完整性门本身成立。

#### PM-P3-108-R1-COV-02｜Not Implemented｜Open

ABF-M-007 要求“独立比较三张 1280×1024 Evidence 与 Stitch”。这里的三张 1280×1024 Evidence 是固定只读的 P3-106 输入，并不要求在当前机器重新量测一个 1280×1024 原生窗口。

rework-1 改为捕获当前新窗口并因 CUA 无原生 rect 报 UNKNOWN，却没有提交对固定 P3-106 三张 Evidence 的逐态结构比较判断。因此 M-007 应调整为 Not Implemented，而不是外部环境 Unknown；完成该行不需要修改显示设置。

#### PM-P3-108-R1-UNK-03｜Unknown｜Open

M-008 的窄窗口交互、滚动和可达性资产已保留，但没有可复核的 native window／content rect，无法证明 Frozen ABF 指定的精确 700×760。缩放后的 CUA 图片不能升级为精确几何事实，M-008 保持 Unknown。

#### PM-P3-108-R1-DOC-04｜P2｜Open

冻结 Evidence 合同指定的 `lifeos/reviews/LIFEOS-P3-108/independent_review.md` 仍停留在初次 Blocked 结论，没有记录 rework-1；执行侧把回报附在 PM Review 内。证据可追踪，但 Review 链未在指定路径规范收口。

### 最终计数

- P0：1。
- P1：0。
- P2：1。
- Unknown：1。
- Not Implemented：1。

### 两层治理与退出判断

- L1：L1-7 Evidence 诚实、L1-10 可复核性。
- L2：ABF-I-06、I-07、I-12；M-007、M-008、M-016 与既有 Evidence 合同。
- ABF 是否变化：No。
- 本次是否为正式 Rework：Yes，记为 2/2。
- 是否允许同任务继续：No；D-0401 与本 ABF 的两轮上限已触发。
- 是否自动创建后继：No。若用户采纳并决定继续，须由 PM 另建任务、新授权和新 ABF；不得把 P3-108 恢复为活动任务。

### 资产、风险、阶段与环境

- P3-104/P3-106 组合候选：Not Frozen；尚未取得合格的全新隔离独立 Pass。
- P3-108 初次及 rework-1 Review／Evidence：全部转只读历史保全。
- R-0040：Open / Conditional，不变。
- R-0051：Closed / Limited Controlled Boundary，不关闭、不重开、不扩大。
- R-0052：Open / Authorized Controlled Execution Boundary，不变。
- 不恢复工程基线、不冻结资产、不进入 Stage 4。
- 动态取证已经结束；用户可手工恢复 macOS“减少动态效果”，不得调整系统显示缩放。
- 风险事实未变化，`RISK_LOG.md` 不更新。

### PM Evidence 与本地预检

- PM Evidence：`lifeos/reviews/LIFEOS-P3-108/pm_evidence/rework-1/MANIFEST.md`。
- 本地预检跳过：本轮是 Tauri/IPC、本地文件失败关闭、独立性和 Evidence 真实性的高风险最终判断，本地模型不得代判。

## 用户采纳与后继授权

- 用户于 2026-08-24 明确采纳本次关闭结论，并授权创建全新后继独立复评任务。
- P3-108 保持永久关闭和只读，不因后继任务创建而恢复或改写为 Accepted。
- 后继任务为 `LIFEOS-P3-109`；使用独立任务卡、独立授权、全新会话与启动前 Frozen `ABF-P3-109-v1`。
- 本授权不修改候选、风险、冻结、工程基线或阶段，也不授权真实数据、retained pilot、系统显示设置修改或网络／外部能力。
