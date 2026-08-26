# LIFEOS-P3-127 Acceptance Basis Freeze｜P3-126 清洁启动候选独立复评

## 冻结信息

- 任务 ID：`LIFEOS-P3-127`
- ABF ID／版本：`ABF-P3-127-v1`
- 生效决策：D-0515。
- 创建时间：2026-08-26 CST (+0800)
- 状态：Frozen / Executable only after final task-card delivery
- 本文件是否在专项会话开始前冻结：是。
- 正式 Rework：0/1。

## 本轮唯一用户结果

- 由与 P3-126 工程执行及 PM 验收隔离的全新 Codex 会话，使用自写 runner、全新 review/temp 根和全新合成 DB，对 P3-126 已获 PM Pass 的最终候选执行一次 offline actual-Tauri 独立复评，并给出 Pass、Rework 或 Blocked。
- 不冻结产品需求、视觉、Runtime、架构、Schema/API 或工程基线。
- 非范围：修改候选、真实使用、Pilot、真实 DB／路径／文本、网络、产品模型、新 IPC、clear/export/权限/恢复、风险关闭和 Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/reviews/LIFEOS-P3-127/`、指定交付物、本地预检、`/private/tmp/lifeos-p3-127-independent-review-v1`。
- 允许数据：全新固定非敏感合成 DB，最多两条任务内固定短文本。
- 允许入口：P3-126 final candidate/build 的只读输入；构建时 `LIFEOS_RUNTIME_ROOT`；仅 `capture_record`、`get_today`、`runtime_status`。
- 允许工具：本地离线 Rust/Cargo/Tauri、SQLite、native/WebView/DOM geometry、actual-App screenshot、只读 hash 与 disposable mutation。
- 严格只读：P3-126 task/ABF/allowlist/candidate/Evidence/delivery/Review/PM Evidence及全部上游历史。
- 绝对禁止：旧 P3-122 Runtime root 的任何 access/stat/hash/create/cleanup；历史 runner 复用；Pilot、真实 DB／路径／文本；网络、模型、云／第三方；新 IPC/capability/Schema/API；系统设置变更；风险、冻结或阶段变化。
- 投递前额外用户确认：Completed in PM main session on 2026-08-26；证据见 `lifeos/tasks/LIFEOS-P3-127_authorization/user_confirmation.md`。

## 引用的 L1 长期原则

- L1-1 数据主权；L1-3 生命周期完整；L1-4 失败关闭；L1-6 审计可信；L1-7 Evidence 诚实；L1-8 历史保全；L1-9 授权不漂移；L1-10 可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 新会话、新 runner、新根、固定输入与授权独立 | P0 | model/effort、75 行 allowlist、hash、roots 与授权全匹配后才行动 | Blocked |
| ABF-I-02 | P3-126 candidate 全程只读且来源绑定 | P0 | 75/75 bytes/hash 与 Frozen source 一致 | Rework |
| ABF-I-03 | `LIFEOS_RUNTIME_ROOT` 是唯一 Runtime 根权威 | P0 | 两个全新授权子根独立工作，无 task-ID/旧根依赖 | Rework |
| ABF-I-04 | 三 IPC actual-Tauri 生命周期成立 | P0 | status/capture/today 的首次、重复、刷新、关闭重开与 DB/audit/UI 一致 | Rework |
| ABF-I-05 | 非法根与文件/DB失败在任何变更前关闭 | P0 | path normalization、symlink chain、file type、DB failure 均保持 DB/sentinel/history | Rework |
| ABF-I-06 | 禁止能力与旧 P3-122 根完全未触达 | P0 | 无探测、创建、hash、cleanup、网络、模型或额外 IPC | Blocked/Rework |
| ABF-I-07 | Evidence lineage 与历史保全完整 | P0 | task/ABF/source/candidate/results/reviews/cleanup 全绑定且历史 hash不变 | Rework |
| ABF-I-08 | 独立 mutation 与精确清理 | P0 | pristine PASS、冻结变异全拒绝、唯一 temp root absent | Rework |

## 冻结验收矩阵

| 行 ID | 入口 | 操作／失败点 | 预期结果 | 测试 ID | Evidence |
|---|---|---|---|---|---|
| ABF-M-001 | startup | 核对 actual model/effort、授权、ABF、allowlist、固定 hashes和两根 absent | 全匹配后才可读 candidate或建根 | P127-M001 | preflight.json |
| ABF-M-002 | independence | 检查 runner 未 import/复制/调用 P3-126 runner | 独立实现 | P127-M002 | independence.json |
| ABF-M-003 | lineage | 独立复算 75-file source/candidate tree | 75/75 byte-exact | P127-M003 | source-lineage.json |
| ABF-M-004 | build | isolated copy 中 locked offline test/build/bundle | exit 0且无网／外部写 | P127-M004 | build logs |
| ABF-M-005 | root A/B | 分别构建并运行 actual Tauri | 两根独立且 Runtime路径全部派生 | P127-M005 | roots/results/screenshots |
| ABF-M-006 | lifecycle | status、first、repeat、refresh、close/reopen | 三 IPC/DB/audit/UI 一致 | P127-M006 | runtime-results.json |
| ABF-M-007 | failures | path/type/symlink/DB/atomic failure | 失败先于任何变更 | P127-M007 | negatives.json |
| ABF-M-008 | prohibited | 静态与运行态 inventory | 仅三 IPC且旧根零触达 | P127-M008 | boundary.json |
| ABF-M-009 | history | 复算 P3-126 固定资产 hashes | 全部不变 | P127-M009 | history.json |
| ABF-M-010 | mutations | pristine pass 后逐类变异 | 全部 fail closed | P127-M010 | mutation-results.json |
| ABF-M-011 | cleanup | App 关闭后精确删除唯一 temp root | root absent；review evidence/history保留 | P127-M011 | cleanup.json |
| ABF-M-012 | final | 生成逐行闭环、Manifest、Review和五类计数 | 可复核结论 | P127-M012 | independent_review.md/MANIFEST |

## Evidence 合同

- 保存 P3-127 自写 runner；禁止复制、import 或 subprocess 调用历史 runner。
- 每行独立记录 frozen action、test ID、actual Evidence、hash 与结论。
- actual-Tauri 动作绑定 UI/screenshot、IPC result、DB/process/log 与 attestation。
- Final Manifest 非自指，覆盖授权、ABF、inputs、runner、results、review与cleanup。
- 仅精确清理待确认的唯一 temp root；禁止 glob、`find` 或宽前缀删除。

## 计数与 Pass 公式

- Pass：I-01～I-08、M-001～M-012 全 PASS；P0/P1/P2/Unknown/Not Implemented 全零；silent N/A 为零。
- model/effort 不可直接确认、固定输入不可解析、授权冲突或 offline actual Tauri 不可启动：在 candidate read/root creation 前 Blocked。
- 任一实际状态、DB、lineage、history或cleanup无法复核：Unknown，不得推断 Pass。

## Rework 预算与退出规则

- 正式 Rework 上限：1；当前 0/1。
- 同任务 Rework：仅 P3-127 自有 runner、Evidence、Manifest或Review，且 Frozen ABF和P3-126 candidate不变。
- 必须新建任务：需修改 P3-126 candidate、Frozen ABF、目录、数据、IPC、架构、真实边界、风险/冻结/阶段，或一轮耗尽。

## 启动前质疑窗口

- 执行方是否提出歧义：N/A；尚未投递。
- PM 处理：用户已完成精确 Tauri/IPC 边界确认；PM 已复算 75 行、hash、roots 与授权并冻结。
- 最终冻结版本：`ABF-P3-127-v1`，D-0515。专项会话开始后不得实质修改；如需修改，当前任务关闭并新建任务。
