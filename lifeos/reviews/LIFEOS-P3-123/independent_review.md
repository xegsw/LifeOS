# LIFEOS-P3-123｜P3-122 组合候选全新隔离独立复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-123`
- 是否为受控能力包：Yes；本任务只做全新隔离、只读独立复评。
- 被评审候选：P3-122 final candidate，Engineering Final Manifest SHA-256 `b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c`。
- Frozen ABF：`ABF-P3-123-v1`，SHA-256 `7b5f67152c9c50187999d11900d2efc44efe79d2b87e2e33173be0a13dc2302b`。
- 独立评审角色：技术架构／Tauri-IPC／Evidence QA。
- 协审视角：体验设计、数据与来源、AI 信任与安全。
- 评审关卡：启动前授权、独立性、候选谱系、Tauri/IPC、Evidence 诚实与历史保全。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-123/`。
- 评审结论：`Blocked`。
- 正式 Rework：`0/2`；本报告不修改 P3-122，也不宣布 P3-123 Rework、Accepted、Frozen 或阶段推进。

## 会话、授权与隔离

- 执行授权证据：用户于 2026-08-26 将绝对路径 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review.md` 投递至本专项会话。
- 会话类型：New Session；未复用 P3-122 工程执行或 PM 验收会话。
- 在读取 P3-122 历史 runner、测试或结果前已生成并哈希独立测试设计：`test_design.md`，SHA-256 `66c5af61f76b3b33613cb15d151b3c16689494823f3a2e873fb5daa0fd4c6aa2`。
- P3-123 独立 runner：`review_runner.py`，SHA-256 `717e460f60b814be6e8ac0d55ccc4dfa7117bd8bfecb0046e9cff3f1e054f700`；未 import、复制、调用或执行 P3-122 `build_evidence.py`／runner。
- 模型／推理强度：`Unknown`。当前任务本地可见的执行面未暴露可独立核验的实际 model/effort；任务卡的推荐路由不是实际执行的证明。
- 评审根仅保留本任务的测试设计、独立 runner 和预检 Evidence。`/private/tmp/lifeos-p3-123-independent-review-v1` 从启动前到停止后均不存在。
- 过程披露：review root 的 test design 在 hash-level input check 后、allowlist 原始格式语义判定前写入；它是 task-local 授权路径内唯一早期写入，但不能被追溯宣称为“完成 M-001 后才创建”的合规 preflight。因此本报告按 Blocked，而非把该时序写成 PASS。

## 评审摘要

1. Frozen ABF、任务卡、P3-123 授权 Manifest、P3-122 PM Review、Engineering Final Manifest、PM acceptance Manifest 和 final-adoption Manifest 的 SHA-256 均与冻结记录一致。
2. P3-122 Engineering Final Manifest 的 75 个 current-candidate 记录逐个与磁盘 bytes/SHA-256 一致；候选实际文件数为 75，无 extra 或 missing file。此只证明当前候选与 Engineering Manifest 一致，不替代本轮 actual-Tauri 复评。
3. `LIFEOS-P3-123_candidate_source_allowlist.md` 的冻结 hash 也一致，但文件只有一个物理行、零条 Markdown 表格记录，并含字面量 `\\n`。这不构成 ABF 所声明的可直接复核 75/75 allowlist。
4. 将该文件临时按 `\\n → newline` 解码可诊断出 75 条记录，并与 Engineering Manifest 相同；但 Frozen ABF 没有授权由评审方创造这种解码约定。因此不能把诊断性结果写成 M-001 PASS。
5. `ABF-M-001` fail-closed 后，未创建 candidate copy、合成 DB 或 temp root，未 build、启动 actual Tauri App、调用 IPC、产生 screenshot／geometry、执行 mutation 或 cleanup。
6. 因为阻断发生在启动门，本报告没有发现或否定 P3-122 的视觉、Runtime、geometry 或产品缺陷；这些行均诚实标为 Not Implemented，而非 Pass。

## 能力包独立性与回流规则

- 执行侧与评审侧是否隔离：Yes。
- 是否只评审能力包的最终 Evidence／hash：Yes；P3-122 全部资产保持只读。
- 独立 runner、逐项结构化结果、Manifest 与可复跑入口：已保留本任务的 test design、runner 和 `evidence/preflight.json`；完整矩阵未获启动资格。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes；runner 的唯一用途是读取固定输入、P3-122 Final Manifest 与 candidate bytes/hash，不含 P3-122 tool path、import 或 subprocess 调用。
- 是否发现需回包内整改的 P0/P1、Unknown／Not Implemented、Evidence 冲突或独立性不足：发现 P0 冻结输入可复核性失败、模型实际配置 Unknown，且后续矩阵 Not Implemented。问题发生在 P3-123 Frozen input／启动门；不能要求改 P3-122 candidate。
- 若需整改：修复 allowlist 表示方式或可核验模型路由将改变本任务 Frozen inputs／ABF，故不属于当前 P3-123 的同任务 Rework。

## 本地 `file:` 动态 Evidence 预检

- 不适用：本任务冻结为 offline actual-Tauri 复评，不以 Chrome `file:` 作为替代。
- actual-Tauri 启动：未执行。启动前 `ABF-M-001` 已失败，浏览器、静态自证、旧 screenshot 或配置均不能替代本轮原生运行态。

## 逐行矩阵与实际 Evidence

| 行 ID | 冻结动作 | 测试 ID | 实际 Evidence（含 SHA-256） | 结论 |
|---|---|---|---|---|
| ABF-M-001 | 复算授权、ABF、P3-122 final hash、模型与 75/75 allowlist 后才创建执行根 | P123-M001 | `evidence/preflight.json` / `5497ce5adbf00b92d5f8f008c0c6d0c3d38fa0872b767aeefc75309e85e9d499`：allowlist 为 1 physical line、0 raw rows、字面 `\\n`；model/effort Unknown | **FAIL / Blocked** |
| ABF-M-002 | 证明不导入／调用／复制 P3-122 runner | P123-M002 | `test_design.md` / `66c5af61…c6aa2`；`review_runner.py` / `717e460f…f700`；`preflight.json` | PASS |
| ABF-M-003 | 复算 visual 8/8、Runtime 65/65 与 candidate tree | P123-M003 | `preflight.json` 只完成 75/75 P3-122 candidate-to-Final-Manifest bytes/hash 静态核对；未获复制／执行资格 | NOT IMPLEMENTED |
| ABF-M-004 | isolated copy 的 locked offline test/build/bundle | P123-M004 | 无；冻结启动门失败，未创建 temp root | NOT IMPLEMENTED |
| ABF-M-005 | actual Tauri 六页面／状态 × 三档 | P123-M005 | 无；未启动 App、无 screenshot 或 geometry | NOT IMPLEMENTED |
| ABF-M-006 | native/content/WebView/DOM/DPR/display geometry | P123-M006 | 无；截图或配置不能替代 | NOT IMPLEMENTED |
| ABF-M-007 | 当前 display 下适配与可达性 | P123-M007 | 无；未运行 actual Tauri | NOT IMPLEMENTED |
| ABF-M-008 | fresh DB 的 status/first/repeat/refresh/reopen 三 IPC | P123-M008 | 无；未创建 DB、未调用 IPC | NOT IMPLEMENTED |
| ABF-M-009 | path/type/DB/atomic 失败先于变更 | P123-M009 | 无；未创建 disposable DB 或 sentinel | NOT IMPLEMENTED |
| ABF-M-010 | 禁能／越界 inventory 与静态／运行态扫描 | P123-M010 | 无；完整独立扫描属于启动门后的矩阵操作 | NOT IMPLEMENTED |
| ABF-M-011 | Engineering Final Manifest 与 PM inputs 全谱系复算 | P123-M011 | `preflight.json` 证明指定基线 hash、75 candidate files 与 Final Manifest 一致；完整 lineage matrix 未执行 | NOT IMPLEMENTED |
| ABF-M-012 | pristine control 后 9 类 disposable mutation | P123-M012 | 无；未创建 pristine/disposable copy | NOT IMPLEMENTED |
| ABF-M-013 | exact temp cleanup 与 history复算 | P123-M013 | `preflight.json`：temp root absent，因未创建而非 cleanup PASS；完整行未执行 | NOT IMPLEMENTED |
| ABF-M-014 | 完整 Review、Manifest 与五类计数 | P123-M014 | 本文件与 `preflight.json`；因 M-001 未通过，无法生成 PASS 定义下的 complete manifest | NOT IMPLEMENTED |

## 已通过内容

- P3-123 的任务卡、ABF、授权与 P3-122 PM／Engineering 冻结 hash 未发生漂移。
- P3-122 candidate 的 75 个文件均与其 Engineering Final Manifest 当前候选层的 bytes/hash 一致，且没有候选目录 extra/missing file。
- 本次独立 runner 在设计冻结后才读取 P3-122 结果，未采用 P3-122 runner、测试或汇总结论。
- 未发生 P3-122 或上游资产写入；P3-123 temp root 未创建。

## 关键问题

### P0｜冻结 candidate allowlist 不是可机器复核的 75 行输入

- 映射：L1-7 Evidence 诚实、L1-9 授权不漂移、L1-10 可复核性；ABF-I-01、ABF-I-08、ABF-M-001。
- 事实：冻结文件 SHA-256 `a5b8…437b7` 对应的原始 bytes 只含一条物理行和字面量 `\\n`；原始 Markdown 表格记录为 0，而 ABF／任务卡要求 75/75 source allowlist。
- 影响：若评审方自行反转义，则会引入未被冻结的解析规则；若不反转义，则没有用于创建隔离候选副本的机器可读正向文件清单。两条路径都不能满足 M-001 的“全匹配后才创建”。
- 诊断而非修复：诊断性反转义后出现的 75 条记录与 Engineering Final Manifest 相同，说明当前 P3-122 candidate 没有由此证明的 hash 漂移；它不弥补 Frozen input 的格式失败。

## 计数与状态

- P0：1（上列 Frozen allowlist 可复核性失败）。
- P1：0。
- P2：0。
- Unknown：1（实际 model／reasoning-effort 未在本任务可见执行面独立暴露）。
- Not Implemented：12（ABF-M-003 至 ABF-M-014；M-002 已 PASS）。
- silent N/A：0。
- 结论：`Blocked / Not Pass`。这不是 P3-122 candidate 的 Pass、Rework 或产品质量结论。

## 关卡检查

- Gate 1 产品一致性评审：未裁决；本轮无产品变更。
- Gate 2 数据与来源评审：Blocked；新合成 DB／source lineage 运行态未启动。
- Gate 3 AI 权限与信任评审：未裁决；禁止产品模型／网络保持在 Frozen 范围内，未执行。
- Gate 4 技术可行性评审：Blocked；actual Tauri／IPC／native geometry 不得在 M-001 失败后启动。
- Gate 5 用户价值验证评审：不适用／未裁决；没有外部用户或 Stage 4 活动。
- Stage 3→4：未通过、未评估；本任务不能成为 Stage 4 准入依据。

## 风险

- R-0024、R-0025、R-0040、R-0051 与 R-0052 不改变。本报告没有关闭、重开或扩大任何风险。
- 新发现仅为当前 P3-123 Frozen Evidence input 的可复核性问题；应由 PM 按 L1/L2 和账本治理记录，不能静默写回或“修复”该 Frozen file。

## 输出路径冲突

任务要求的专项摘要路径 `lifeos/deliverables/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review.md` 在本会话开始时已存在未追踪内容，SHA-256 `bd7c155ad04a1735f527a3c7e9a1de14e7ebc69b61b838e37d905f0fa2e0a7eb`。其内容是另一个启动前 Blocked 报告，并声称不同的线程模型元数据；该元数据未在本会话独立可见，故未作为本报告事实或复评依据。为保全用户已有修改，本会话没有覆盖、附加或重命名该文件。

## 需要 PM 决策

1. 记录本次 `Blocked`：P3-123 在 Frozen M-001 启动门失败，P3-122 candidate 未获得本轮 actual-Tauri 复评。
2. 如仍需独立复评，关闭／Supersede 当前 P3-123 并新建任务、重新获取用户授权和 Frozen ABF：新 allowlist 必须在原始 bytes 中真实包含 75 条可解析记录，并规定可复核的实际模型／推理强度证据来源。
3. 处置上述 pre-existing 专项摘要文件后，再由 PM 指定可写的唯一交付路径；本专项不会改写它。

## 最终建议

不建议冻结、采纳 P3-123、关闭风险、恢复基线或进入下一阶段。建议 PM 保全本次 Evidence，并按上述新任务触发条件处理；不得把诊断性 75-row 反转义、P3-122 的旧 PM Pass 或静态 75-file hash 一致性替代本轮 Frozen 独立复评。

## 本地预检

Skipped。原因：这是 P0 Frozen input、Tauri/IPC、native geometry 与 Evidence lineage 的最终治理判断；本地模型不得替代独立评审裁决。
