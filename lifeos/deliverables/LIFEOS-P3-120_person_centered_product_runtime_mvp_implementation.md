# LIFEOS-P3-120｜以人为主体的产品 Runtime MVP 实现｜专项会话报告

## 任务与执行结论

- 任务卡投递／执行授权：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md` 的绝对路径投递；本会话按其 Frozen `ABF-P3-120-v1` 执行。
- 会话类型：全新 Codex 工程执行会话；未复用 P3-111、P3-116 或 P3-119 的执行上下文，未创建子任务或独立评审。
- 本包状态：`Rework 2/2 / User Adopted / Final Manifest Closure Evidence Ready / Awaiting PM Re-Acceptance`。
- 初次包内自检曾报告 ABF-M-001 至 ABF-M-015 `PASS`，但 PM Review 判定其中 M-004 与 M-006–M-010 的动态 Evidence 存在 P0/P1 缺口；该初次自检不再作为这两组行的验收依据。
- Rework-1 包内 Evidence 自检：通过。实际 app 手动闭环覆盖 M-001、M-004–M-010 与 M-015；`P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0`（仅指本轮整改 Evidence 自检，不是 PM Pass）。
- 本结论不是 PM Pass、User Adopted、独立复评 Pass、冻结、风险关闭或 Stage 4 准入。

## 已完成的受控实现

在 `lifeos/engineering/LIFEOS-P3-120/candidate/` 建立了新的合成数据 Tauri MVP。工程创建前，重新核验 Frozen ABF、14 项固定输入与 P3-111 positive source allowlist；72/72 个允许的技术源文件逐项校验 bytes/SHA-256 后才被复制。没有递归复制 P3-111/P3-116 根，没有读取、复制或定位 P3-111 Pilot、历史 Evidence、原始日志、真实 DB 或真实内容。

Runtime 保留且只暴露三项既有 IPC：`capture_record`、`get_today`、`runtime_status`。唯一运行时 DB 是 `/private/tmp/lifeos-p3-120-runtime-mvp-v1/capture.sqlite`；输入只允许两条冻结的非敏感合成原文。SQLite schema 维持继承合同（含 `PRAGMA user_version = 104`），写入使用候选副本、验证、原子 rename；路径逃逸、祖先链接、DB/sidecar/hardlink、残留 shadow、非法参数、额外字段、篡改 schema/content 和注入提交失败均 fail-closed。

页面层实现 Today、Me、Contexts、Context Detail、Memory、Memory Detail、Global AI Side Panel、AI Workspace 与弱化 Settings。Today 只通过 `get_today` 呈现 Runtime 数据；Me/Contexts/Memory 与详情明确为 read-only synthetic fixture；Observation、AI candidate、用户确认与持久化用户原文有可见身份区分。Global AI 与 Workspace 明确显示模型、网络、工具执行和 AI 写入均未启用。没有自由文本、文件、导入、clear、export、permission、recovery、Vault、同步、多设备或外部入口。

## PM Rework 1｜实际 App Evidence 闭环

本轮仅新增 `lifeos/engineering/LIFEOS-P3-120/evidence/rework-1/` 和本交付更新；candidate、初次 `evidence/`、Frozen ABF、三项 IPC、Schema/API 及项目账本均未改变。`preflight.json` 在启动前复算初次 Engineering Manifest、初次 matrix、任务卡和 ABF 的冻结 hash，并记录 PM 已确认的实际会话配置 `gpt-5.6-terra + xhigh`。

用户在前台打包 `.app` 中实际完成 Today 空态、Me、Contexts、Context Detail、Memory、Memory Detail、Global AI、AI Workspace 和 Settings 导航；随后手动完成 synthetic one 首次写入、同一条重复幂等、synthetic two 写入、Today 刷新、窗口关闭及同一 bundle 重开。每一步均包含用户操作说明、进程／SQLite 快照、stdout 日志快照、直接窗口截图和 SHA-256。重开后 Today 显示两条固定原文，SQLite 与日志均为 2 records／3 audit events。

`DYNAMIC_CLOSURE.json` 为逐动作机器可读闭环表；`rework-results.json` 的 post-cleanup verifier 对 M-001、M-004–M-010、M-015 均为 `PASS`。此 verifier 只读取已记录的实际 app Evidence，拒绝以源码状态合同、Rust unit test、P3-119 helper 或任何 GUI／浏览器自动化替代动态操作。最终用户手动关闭应用后，精确清除了唯一临时根 `/private/tmp/lifeos-p3-120-runtime-mvp-v1`，见 `cleanup.json`。

## PM Rework 2｜Final Manifest Closure

PM 在 Rework-1 复验中确认实际 App 闭环与模型记录均已通过，但初次 Engineering Manifest 仍把初次交付物的旧 hash `ef644706…` 作为其 101 行历史快照；本报告更新后，该旧值不能被伪称为当前交付物 hash。Rework-2 因此只新增 `evidence/final-manifest-closure/`，不重跑应用、不访问临时 Runtime 根，也不修改 candidate、初次 Evidence 或 `evidence/rework-1/`。

该目录的非自指 `FINAL_MANIFEST.json` 同时覆盖当前交付物、current candidate inventory、初次 101 行 historical layer、Rework-1 Manifest 及其 59 个 payload、PM Review 授权输入，以及本轮测试设计、verifier、draft payload、verification results 和 mutation results。历史层的旧交付物 hash 被明确标记为 historical；current-delivery layer 单列并复算本报告的当前 bytes/SHA-256。

Rework-2 verifier 对普通文件类型、bytes/SHA-256、candidate missing/extra、initial historical 100/101 仍匹配且旧交付物仅作历史快照、Rework-1 retained payload、PM authority、final-closure missing/extra 逐项 fail closed。独立 disposable mutation control 通过，并分别证明遗漏当前交付物、改变 candidate payload hash、加入额外 closure 文件和混淆 historical/current lineage 都会失败。该自检关闭 M-015 的 Manifest lineage 缺口，但仍不是 PM 重新验收、资产冻结、风险关闭或 Stage 4 结论。

## 自检与 Evidence 摘要

- Frozen 输入与 allowlist：15 项固定 hash（含 ABF）和 72/72 source rows 复算通过，见 `evidence/fixed-inputs.json`；当前候选清单见 `evidence/candidate-inventory.json`。
- 离线构建：locked/offline `cargo test`、release build 和 macOS `.app` bundle 均 exit 0，见 `evidence/build-results.json` 与三份 build log。
- Runtime：结构化 trace 覆盖空 DB、capture one、重复幂等、capture two、刷新、关闭重开、DB SHA-256 与原子失败前后 DB/哨兵不变，见 `evidence/runtime-results.json`。
- 负向：路径/链接/sidecar、篡改、非法输入和额外 IPC 字段均由独立测试名映射，见 `evidence/negative-results.json`。
- 初次 Actual app Evidence：最终 bundle 曾被启动、停止、再启动；但该启动存活检查不能替代完整实际操作链。PM-P0-001／PM-P1-001 已由本交付中的 `evidence/rework-1/` 人工动态闭环补足。
- 初次 Person-centered source-state contract：仍保留为候选自检资料，但不再替代实际导航、capture、刷新或重开 Evidence；本轮以 `evidence/rework-1/` 的人工动态闭环为准。
- 最终逐行结果：`evidence/matrix-results.json` 对 ABF 的 15 行分别列出动作、结论、Evidence 路径与 SHA-256。

唯一临时根已按精确路径删除，最终不存在：`/private/tmp/lifeos-p3-120-runtime-mvp-v1`。记录见 `evidence/cleanup.json`。本次没有改动 ABF、任务登记、决策／风险／冻结／阶段账本，且未声称关闭 `R-0040`、`R-0051` 或 `R-0052`。

## 角色与关卡

主责 Codex 工程、Runtime/IPC、前端集成与 QA 自检已完成。产品架构、技术架构、数据安全、AI 信任、体验与 Evidence QA 的任务内检查点已完成 Rework-1 自检：固定输入／positive allowlist、三项 IPC、合成数据和路径边界、离线 build/test、实际导航、实际生命周期、失败关闭、IA／内容身份、禁止能力与精确清理。

任务卡要求的下一关仍是 PM 验收；若 PM Pass，仍需用户采纳后才能新建全新隔离的独立复评。该独立复评不得由本执行会话承担。

## 本地预检与 PM 决策

本次未调用局域网本地模型预检。原因是本包涉及 Tauri/IPC、SQLite 路径与持久化的 P0 边界；本地模型输出不能安全代替或辅助最终风险判断。可复跑的机器检查、日志、hash 和逐行矩阵已完整保留。

需要 PM 决策：是。请仅决定是否按同一 Frozen ABF 对该 `Rework 1/2 / User Adopted` 包进行 PM 重新验收；本会话不请求也不执行风险关闭、资产冻结、真实数据启用或 Stage 4 推进。
