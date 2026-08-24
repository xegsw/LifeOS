# LIFEOS-P3-108｜独立评审

## 评审信息

- 对应任务 ID：`LIFEOS-P3-108`
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：只读固定 P3-106 高保真 Tauri candidate 与 P3-104 runtime 安全底座；ABF `ABF-P3-108-v1` SHA-256 `54cbb4a8d302a1dd4007bcdbd7c7844f0d98588f54c51d941e197a8176c1ae10`；固定输入快照 21/21 匹配（`snapshot.json`）。
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md`
- 独立评审角色：独立 QA／安全与数据生命周期评审
- 协审视角：体验设计、可访问性、技术架构、数据／领域、AI 信任安全
- 评审关卡：Gate 1、2、3、4；Gate 5 仅固定非敏感内部理解检查
- 独立评审路径：用户直接投递任务卡到全新 Codex 会话；接收在 2026-08-24 CST、测试设计落盘前；设计文件 mtime 为 09:14:09 CST，随后才读候选源码／历史提交资产。
- 评审结论：**Blocked**

## 能力包独立性与回流规则（适用时）

- 执行侧与评审侧是否隔离：Yes。未复用 P3-104/P3-106/P3-107 工程或评审会话；先冻结测试设计，之后才读取候选。
- 是否只评审能力包的最终 Evidence／hash：Yes；候选与 ABF、账本、风险均未改动。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：Yes，见 `evidence/independent_runner.py`、`matrix-results.json`、`dynamic_closure.md`、`final_verifier.py` 与非自指 `evidence/MANIFEST.md`。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes。clean copy 仅正向 allowlist；`copy-inventory.json` 的禁项/额外根目录均为 0。候选 unit tests 仅按 ABF 的 locked build 例外执行。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：候选未发现 P0/P1；最终 verifier 真实发现 4 个 `Not Implemented`：M-007、M-008、M-013、M-015。它们不能被静态扫描或旧 Evidence 抵销。
- 若需整改：不建议对候选创建修复；这是当前环境／授权下无法生成冻结实际视口和 reduced-motion 观察的 Blocked，不是候选 P0/P1 Rework。
- 更新时间：2026-08-24 CST。

## 本地 `file:` 动态 Evidence 预检（仅适用时）

- N/A。本任务明确禁止用 browser/file/HTTP/DOM mock 替代，实际入口是离线 Tauri app；使用 Computer Use 控制 macOS Tauri 窗口。

## 评审摘要

- 固定快照 21/21 匹配；P3-106 Manifest 325/325 重算通过，P3-104 仅存在 ABF 明确允许的单一 `PASS_TIME_QUALIFIED` PM Review 对。
- 正向 allowlist clean copy 成功，`cargo test --locked`、`cargo build --locked`、`cargo tauri build --debug -- --locked` 均离线成功，network token 为 0。
- runtime/IPC/capability 静态反查通过：仅 3 个 IPC、无通用 capability、无 renderer 网络调用，路径与 sidecar fail-closed 逻辑存在。
- 实际 Tauri app 已复核 saved/repeat/conflict/injected-failure/refresh/三态往返/关闭重开/unknown IPC/extra fields；nominal DB 最终为 1 capture、2 audit。
- 实际干净 binary 在目录、链接、硬链接、dangling final/journal/wal/shm 夹具启动前拒绝；内容和 schema 篡改 GUI 均明确拒绝读取且不展示缓存成功态。
- 但任务禁止修改系统显示/偏好，而可用实际窗口未能形成冻结所要求的 1280×1024 与精确 700×760 逐态动态闭环；reduced-motion 也不能在未获用户确认的系统设置变更下实际触发。外部路径也缺少独立 actual-app 行。因此 final verifier fail-closed，不可给 Pass。

## 已通过内容

- `ABF-M-001` 至 `ABF-M-006`、`M-009` 至 `M-012`、`M-014`、`M-016` 成立；清理后全部 P3-108 task-local 路径为缺失，P3-107 的三条保护旧路径仍缺失，受保护 P3-104 临时文件仅 lstat metadata。
- 当前可观察候选没有发现 P0/P1 runtime、IPC、atomic publish、路径类型、sidecar、内容身份或 AI/外部能力关闭态缺陷。
- 风险、冻结、基线与 Stage 4 均未被本评审改变；不形成 Freeze、Accepted 或 Stage 4 准入结论。

## 关键问题

1. `ABF-M-007/M-008` 的精确 viewport 动态 Evidence 在当前实际环境不可获得：基线截图 1036×779，窄窗口动作产生 768×832 截图；任务禁止系统显示设置变更，不能诚实等同为 1280×1024 或 700×760。
2. `ABF-M-015` 需要实际 Tab/Enter/skip/focus/reduced-motion。前两项有真实动作和截图，但 AX 不暴露可审计的焦点顺序/落点；运行时报告系统未请求 reduced motion，未经用户明确确认不得修改系统偏好。
3. `ABF-M-013` 已实际覆盖 path/link/hardlink 与启动前拒绝，但“外部路径”没有独立 actual-app fixture/Evidence 行，不能借 schema 静态检查补写为通过。

## 必须整改项

- 不对 P3-106 候选做修复。PM 必须新建或按治理决定一个环境/ABF 路由：提供可实际控制的 1280×1024 与 700×760 窗口环境、能观察真实焦点与媒体查询的批准工具；或者取得用户对仅本地测试的系统 reduced-motion/显示设置变更的单独、可记录确认，并冻结相应新 ABF。
- 新一轮必须从全新动态闭环重新验证 M-007、M-008、M-013、M-015；不得把本轮 `PARTIAL` 截图或静态扫描升级为 Pass。

## 条件通过项

- 无。结论为 Blocked，不能使用 `Pass with Conditions`。

## 关卡检查

- Gate 1 产品一致性评审：Blocked；实际三态基线积极，但冻结精确视觉/响应式矩阵未闭合。
- Gate 2 数据与来源评审：Blocked；核心内容身份、生命周期与失败关闭通过，但外部路径 actual-app 独立行未闭合。
- Gate 3 AI 权限与信任评审：通过本轮可观察范围；AI/外部能力关闭态、unknown IPC 和 extra fields 均实际拒绝；不构成冻结。
- Gate 4 技术可行性评审：Blocked；clean build/runtime 边界通过，但正式 ABF 16 行未全绿。
- Gate 5 用户价值验证评审：N/A；只使用固定非敏感内部演示，不作阶段 Pass。

## 风险

- 未新增或关闭 `R-0019`、`R-0040`、`R-0051`、`R-0052`；当前结论不更新风险账本。
- PM 应关注“冻结动态 Evidence 对可控显示/媒体偏好环境的依赖”这一治理阻断；它是本任务的环境可达性问题，不应误标为已证实的候选工程缺陷。

## 需要 PM 决策

1. 是否为未完成的动态矩阵新建后继任务与新 ABF（本任务的 Rework 计数保持 0/2），或提供冻结的受控 GUI 环境。
2. 若要切换系统 reduced-motion 或显示尺寸，需先取得用户单独、明确且可记录的确认；本评审没有该授权。
3. 是否将本轮候选的已通过安全/生命周期 Evidence 仅作为只读输入，而非验收或冻结结论。

## 最终建议

不要冻结、不要进入 Stage 4、不要标记 Accepted。保留本轮 Evidence 和 Blocked 结论；在新的授权与 ABF 下完成缺失的实际视口、a11y/reduced-motion 和外部路径动态闭环后，再进行全新独立复评。

本轮跳过本地模型预检：P0 独立复评的最终判断依赖实际 Tauri/IPC/本地文件边界与可复核动态 Evidence，按任务卡许可不让本地模型介入最终结论。
