# LIFEOS-P3-111｜三页 UI 与本地 Runtime 有限真实使用闭环

## 任务信息

- 任务 ID：`LIFEOS-P3-111`
- 执行 Agent：Codex 工程执行专项会话（新会话）
- 当前状态：Completed — 包内工程／Evidence 自检通过，待 PM 正式验收与 P3-112 全新隔离独立复评
- 需要 PM 决策：Yes
- 任务类型：P0 受控能力包；有限本人真实使用闭环
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-111-v1`／`24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395`
- ABF 是否在工程动作前核对为 Frozen：Yes（D-0449，2026-08-24 Asia/Shanghai）
- 正式 Rework：0／2

## 执行摘要

- 从 P3-106 rework-1 正向 allowlist 创建了隔离 candidate；source Manifest SHA-256 为 `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe`。未复制历史 Evidence、runner、tests 或 target，未修改历史资产。
- candidate 保持仅 `capture_record`、`get_today`、`runtime_status` 三项 IPC；无新增 Schema、API、依赖、capability、网络或外部能力。静态合同通过。
- 固定非敏感自检完成 8 个 Rust 测试：首次、幂等、冲突、原子失败、路径／类型／sidecar／tamper、未知 IPC 与额外参数拒绝均为关闭态；夹具与 shadow 残留为 0。
- native unsigned Tauri app 实测三页、导航、刷新、关闭重开与实际 Tab／Enter。你在 app 内主动保存的实际低敏感内容未被本会话读取、复制或写入 Evidence；安全状态页观察到 2 条记录／2 条审计，均在最多 3 条的授权范围内。
- Pilot-2 retained DB 仍保留：metadata 仅验证目录／文件类型／sidecar，不读取 DB 内容，不执行 raw SQL／shell／process；未触及 Pilot-1 或其他个人路径。
- Payload Manifest、独立语义 verifier 与六种真实 disposable mutation 均已复跑；最终冻结、风险关闭／重开、Stage 4 准入及 P3-112 独立复评均不由本会话作结论。

## 范围、授权与会话

- 执行授权证据：用户于 2026-08-24（Asia/Shanghai）向本新建专项会话投递 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md`；D-0449 已覆盖精确新目录、新 DB、最多三条主动低敏感输入、允许动作及 retained 规则。
- 启动前只读确认：Pilot-2 不存在，`/Users`、`/Users/xxe`、`/Users/xxe/Documents` 均为真实目录而非链接；之后仅 app 的成功用户保存创建 `capture.sqlite`。
- 允许写入仅为 `lifeos/engineering/LIFEOS-P3-111/`、本交付物及经确认的 Pilot-2。未修改 ABF、项目账本、风险、冻结或历史候选。
- 当前执行环境未向 Agent 暴露可独立核验的精确模型标识；未执行模型切换或降级。PM 应在其任务路由记录中核验 task card 所列 `gpt-5.6-terra / xhigh` 配置，不能将本项披露替代路由证据。

## ABF 不变量与矩阵自检

| ABF 不变量 | 包内自检结论 | 主要 Evidence |
|---|---|---|
| I-01 授权与隔离 | 新会话、Frozen ABF、用户主动输入边界已记录；模型路由由 PM 记录待核验。 | 本节；task card／ABF |
| I-02 provenance | 仅 P3-106 正向 allowlist，禁复制项为 0。 | `candidate_provenance.md` |
| I-03 IPC／能力最小化 | 三 IPC、空 permissions、无网络／新增依赖。 | `raw/static-results.json` |
| I-04 真实路径 | 仅 Pilot-2；祖先预检无链接；未访问 Pilot-1。 | `raw/actual-pilot-metadata.json` |
| I-05 隐私与身份 | Evidence 无原文／key／DB 内容；来源与关闭态可辨。 | `UI_DYNAMIC_EVIDENCE_CLOSURE.md` |
| I-06 commit-before-success | 固定原子失败及成功后状态测试通过；真实保存后安全页状态一致。 | `raw/fixed-lifecycle.json`；`raw/m005-user-save-redacted.json` |
| I-07 生命周期 | 首次、重复、冲突、失败、刷新、三页导航、关闭重开均有独立证据。 | `raw/fixed-lifecycle.json`；动态闭环表 |
| I-08 失败关闭 | 路径、类型、sidecar、tamper 与额外参数／未知 IPC 均拒绝。 | `raw/negative-results.json`；测试日志 |
| I-09 三页体验 | 三页 native 截图、响应式结构、实际 Tab／Enter 逐项记录。 | `UI_DYNAMIC_EVIDENCE_CLOSURE.md` |
| I-10 Evidence 语义 | payload 重算与六种真实 disposable mutation 由同一 verifier 检出。 | `PAYLOAD_MANIFEST.json`；`mutation-results.json` |
| I-11 保留与清理 | fixture／shadow／build temp 均为 0；Pilot-2 保留。 | `raw/cleanup.json`；`raw/actual-pilot-metadata.json` |
| I-12 风险／冻结／阶段 | 未修改账本；不主张冻结、风险关闭／重开或 Stage 4。 | 本交付物 |

| ABF 行 | 包内自检结论 | Evidence |
|---|---|---|
| M-001 | 授权、边界与 ABF 已核对；模型精确标识留 PM 路由核验。 | task card／ABF；本节 |
| M-002 | 仅完成既有闭环缺口映射，无产品扩张。 | `product_gap_matrix.md` |
| M-003 | allowlist source hash 与 candidate hash 可追溯。 | `candidate_provenance.md`；`raw/static-results.json` |
| M-004 | offline locked Rust test 与 Tauri app bundle 均退出 0。 | `raw/cargo-test.log`；`raw/cargo-tauri-bundle.log` |
| M-005 | 三项 IPC 和禁止能力静态扫描通过。 | `raw/static-results.json` |
| M-006 | 固定非敏感首次／重复／冲突／原子失败通过。 | `raw/fixed-lifecycle.json`；`raw/cargo-test.log` |
| M-007 | 刷新、三态导航、关闭重开分别实测恢复。 | `UI_DYNAMIC_EVIDENCE_CLOSURE.md` |
| M-008 | 路径／类型／sidecar／tamper 在变更前拒绝。 | `raw/negative-results.json`；测试日志 |
| M-009 | 三页、键盘、身份、关闭态逐项闭环。 | `UI_DYNAMIC_EVIDENCE_CLOSURE.md` |
| M-010 | 用户实际 native capture 已发生；Evidence 已脱敏。 | `raw/m005-user-save-redacted.json`；`raw/actual-pilot-metadata.json` |
| M-011 | baseline verifier 通过；六类 disposable mutation 均被检出。 | `semantic-verifier-result.json`；`mutation-results.json` |
| M-012 | payload 可重算；临时残留为 0；retained DB 未删。 | `PAYLOAD_MANIFEST.json`；`raw/cleanup.json` |

### 包内自检计数

- 工程／测试／动态／语义 Evidence：P0 0；P1 0；P2 0；Unknown 0；Not Implemented 0。
- 路由管理披露：本会话无法查看精确模型 ID，未把它计入工程结果；PM 必须在正式验收前核验 M-001 的模型路由记录。若无法核验，应按 ABF 的正确模型停止条件处理，而非将本交付物标记 Accepted。
- 本轮没有本地模型预检：P0 联合边界的提交结论避免由本地模型造成误导；这不替代 PM／独立复评。

## Evidence 与保留

- Evidence 根目录：`lifeos/engineering/LIFEOS-P3-111/evidence/`；动态逐项表：`evidence/UI_DYNAMIC_EVIDENCE_CLOSURE.md`。
- 最终 payload Manifest SHA-256：`0c8f1fcea3fb756c1974243d3d20315854ceada28fd73bd4c65652d3afd3bb7b`；最终 verifier SHA-256：`52a75c16a8b56d2fa03340d13b5a581d31d7982ce7263c4e02aaa7827546fb2a`；六类 mutation 结果 SHA-256：`c5df02374827f1ca2dd21076fdeb4f5b8d123df43e45763a824e4c462003390c`。
- 动态视觉 Evidence：`screenshots/m001-default-empty.png`、`m002-no-suggestion-empty.png`、`m003-restricted-empty.png`、`m007-no-suggestion-after-user-save.png`、`m009-no-suggestion-after-reopen.png`、`m010-restricted-after-reopen.png`；逐项 hash 见闭环表。
- retained 实际目录：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2/capture.sqlite`。事实：当前保存 2 条实际记录与 2 条审计，DB 为普通文件、无 WAL／journal／SHM sidecar；推断：刷新／重开页面所显示的权威计数与该 retained 状态一致；未读取其 DB 内容，不能从 Evidence 推导任何原文。
- 清理仅针对 candidate 固定夹具、disposable Evidence 副本及 `/private/tmp/lifeos-p3-111-build-output`；三者均已不存在。真实目录／DB 未删。

## 角色与关卡

- 主责角色：本地 MVP 工程与数据生命周期。
- 协审检查点：产品／体验（冻结骨架与三态）、数据与来源（内容不入 Evidence、Today backend 恢复）、AI 信任安全（AI／网络／外部能力关闭）、可访问性（Tab／Enter）、独立 QA（留给 P3-112）。
- 已覆盖：Gate 1、Gate 3、Gate 4 的执行侧自检；Gate 5 仅收集本人的有限使用观察，未主张通过。
- 仍需：PM 正式验收、用户采纳决定、P3-112 全新隔离独立复评；其后仍不得自动推导风险关闭、冻结、其余 Stage 4 硬门或 Stage 4 准入。

## 需要 PM 决策

1. 核验本任务执行的模型路由是否满足 `gpt-5.6-terra / xhigh`，并决定是否接受本项工程／Evidence 提交进入 PM 验收。
2. 在不改变 retained 目录的前提下，决定是否发起 P3-112 全新隔离独立复评；本会话不得自评最终通过。

## 后续任务建议

- 唯一推荐下一条工作线：PM 核验本 P3-111 提交并在用户采纳后创建／投递 P3-112 全新隔离独立复评；不得将其并入导出、权限、恢复、风险、冻结或 Stage 4 工作。
