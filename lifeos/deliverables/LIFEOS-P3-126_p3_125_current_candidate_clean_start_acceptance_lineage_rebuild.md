# LIFEOS-P3-126｜P3-125 当前技术候选清洁启动与验收链重建

## 任务启动记录（P126-M001）

- 任务卡投递：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md`
- 会话类型：全新 Codex 工程执行会话；未复用 P3-125 会话。
- 接收日期：2026-08-26（Asia/Shanghai）。
- 追加用户确认：用户在本会话明确回复“执行吧，我能确认模型匹配”；按任务卡唯一允许的匹配配置记录为 `gpt-5.6-terra + xhigh`。
- 平台暴露说明：本会话终端／环境未提供独立的模型或推理强度字段；以上配置的可复核来源是用户的明确确认，而非伪造的平台元数据。
- Frozen task SHA-256：`467468d8a8a7a2c5c49c40b6388ab37398a8ec8a4457012caa0c616eb686671e`（已复算匹配）。
- Frozen ABF SHA-256：`8e98f4d874d3925bdad308f800f01d7c44b02c3016e71f19083cad4fc13fb908`（已复算匹配）。
- Frozen allowlist SHA-256：`2c4a1a40310adb833f42d935a017fe3fdc8fe5c26c9a2c21b30ba94f7b4a06b9`（已复算匹配；75 个物理数据行）。
- User-confirmation SHA-256：`c89db8f6d7ccfdad383d31af7ec07e13a8b2783a625b8eac10d197f1cb124c26`（已复算匹配）。
- Freeze Manifest SHA-256：`6175a06a81e79d5f52356e94312c461ce922c6828d6adec0f3361ade7497e94c`（已复算匹配）。
- 新授权工程根和唯一临时根均已确认不存在；尚未读取 P3-125 candidate，尚未创建 P3-126 engineering/temp root。

### 已冻结命令计划

1. 在 P3-126 engineering root 内生成独立 runner、结构化结果与 Manifest 工具；不导入、复制或调用 P3-125 runner。
2. 仅通过 P3-126 physical multiline allowlist 将 75 个只读源文件复制到 P3-126 candidate，并逐个重算 bytes/SHA-256。
3. 只在唯一 P3-126 temp root 内创建 `run-a/`、`run-b/`、disposable negatives 与 task-owned caches；每次构建仅设置 `LIFEOS_RUNTIME_ROOT` 为对应新子根。
4. 全部 shell／runner 路径白名单仅包含 P3-126 允许根、P3-125 明列只读输入、项目内 Rust 工具和离线依赖；不含任何旧 Runtime-root existence、metadata、hash、create 或 cleanup 操作。
5. 使用实际 Tauri App 的 UI、IPC、SQLite、审计、进程、日志和原生窗口／截图对每项动态动作交叉取证；失败负向先记录 sentinel／DB before，再确认零变更。
6. 先运行 pristine verifier；随后在 disposable copies 做 root、fallback、derive、order、history、extra、path、omission mutations；最后精确删除唯一 P3-126 temp root并生成排除自身的 Final Manifest。

### 启动门结论

用户的明确确认授权了本任务继续执行；但 Frozen ABF 要求的是“平台暴露”的 actual model/effort。平台元数据未暴露，因此 `P126-M001` 的模型来源保留为 `Unknown`，而不是把用户确认伪写为平台事实。其余 Frozen hashes、物理 allowlist、会话隔离和两根初始不存在均匹配。

本记录已在 candidate read 或 P3-126 execution-root creation 前写入唯一允许的 task deliverable 路径。

## 任务信息

- 任务 ID：LIFEOS-P3-126
- 任务名称：P3-125 当前技术候选清洁启动与验收链重建
- 执行 Agent：Codex
- 当前状态：Partial（所有工程／Evidence 行已执行；Frozen 公式因一个 `Unknown` 不成立）
- 需要 PM 决策：Yes
- 任务类型：受控能力包内的清洁启动、actual-Tauri 生命周期与 Evidence 重建；不修改 production candidate。
- Acceptance Basis Freeze 路径：`lifeos/tasks/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild_acceptance_basis_freeze.md`
- ABF ID／版本／PM 记录 SHA-256：`ABF-P3-126-v1` / `8e98f4d874d3925bdad308f800f01d7c44b02c3016e71f19083cad4fc13fb908`
- ABF 是否在任何工程动作前核对为 Frozen：Yes
- 是否在启动前发现验收依据歧义：Yes；模型来源未由平台暴露。用户确认仅授权继续执行，未修改 Frozen ABF。
- 当前正式 Rework 次数／上限：0/1
- 交付物篇幅是否在建议范围内：Yes

## 执行摘要

- P3-125 Rework-1 当前候选按 physical multiline allowlist 复制并逐文件复算：`75/75`、无 extra、无 production source change。
- 两个新授权根的实际打包 Tauri 生命周期已完成。Run-A 依次观测 `0/0 → 1/1 → 1/2 → quit/reopen 1/2`；Run-B 独立得到 `0/0 → 1/1`。UI 截图、三项 IPC、SQLite、审计、进程及原生窗口几何均有对应 Evidence。
- 配置负向、串行 Rust 测试、失败关闭、边界检查、P3-125 history before/after 和八类 disposable 变异均通过或被正确拒绝。
- 唯一临时根 `/private/tmp/lifeos-p3-126-clean-closure-v1` 已在实际 app 关闭后精确删除；无旧 P3-122 Runtime root 访问、stat、hash、创建或清理操作。
- `Final Manifest` 和可重跑 verifier 已生成；其可以验证路径、bytes/SHA-256、角色、遗漏、extra、candidate 与 history 漂移。
- 不调用本地模型预检：本任务涉及 P0 高风险最终判断，任务卡允许跳过；未将本地模型用于任何验收结论。

## 12 行验收矩阵

机器可读闭环：`lifeos/engineering/LIFEOS-P3-126/evidence/DYNAMIC_CLOSURE.json`。其中每行列出冻结动作、测试 ID、实际 Evidence 路径与 SHA-256。

| ABF 行 | 测试 ID | 实际结果 |
| --- | --- | --- |
| M-001 | P126-M001 | `Unknown`：用户确认 `gpt-5.6-terra + xhigh`，但平台未暴露独立 model/effort 元数据。 |
| M-002 | P126-M002 | PASS：候选 `75/75` byte-exact，固定 P3-125 输入完整。 |
| M-003 | P126-M003 | PASS：静态合同九项通过。 |
| M-004 | P126-M004 | PASS：配置负向、测试和 fresh bundle 通过。 |
| M-005 | P126-M005 | PASS：Run-A actual UI／IPC／DB／audit／几何与重启持久化。 |
| M-006 | P126-M006 | PASS：Run-B 独立 root 与 fresh SQLite。 |
| M-007 | P126-M007 | PASS：三项既有 IPC 生命周期闭环。 |
| M-008 | P126-M008 | PASS：失败关闭和零变更证据。 |
| M-009 | P126-M009 | PASS：禁止边界和接口零漂移。 |
| M-010 | P126-M010 | PASS：P3-125 指定直接输入 before/after 一致。 |
| M-011 | P126-M011 | PASS：root、fallback、derive、order、history、extra、path、omission 变异均被拒绝。 |
| M-012 | P126-M012 | PASS：精确清理和可审计 Manifest。 |

计数：`P0=0，P1=0，P2=0，Unknown=1，Not Implemented=0`。按 Frozen ABF 公式，`Unknown=1`，故本专项 Agent 不提交 “PM Pass / Candidate Ready”。

## Evidence 与复跑

- 机器可读结果：`lifeos/engineering/LIFEOS-P3-126/evidence/`（包括 `run-a-results.json`、`run-b-results.json`、`ipc-lifecycle.json`、`failure-closure.json`、`history-integrity.json`、`mutation-results.json`、`cleanup.json` 和 `DYNAMIC_CLOSURE.json`）。
- 视觉 Evidence：`run-a-initial.jpeg`、`run-a-first.jpeg`、`run-a-repeat.jpeg`、`run-a-reopen.jpeg`、`run-b-first.jpeg`，同目录中的结构化运行结果给出对应 SHA-256、数据库、审计、PID 与几何记录。
- 来源／历史完整性：`source-lineage.json` 与 `history-integrity.json`；P3-125 candidate 与指定直接输入均无漂移。
- 可重跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-126/tools/run_p3_126.py --help
python3 -B lifeos/engineering/LIFEOS-P3-126/tools/verify_p3_126.py verify \
  --manifest lifeos/engineering/LIFEOS-P3-126/evidence/FINAL_MANIFEST.json
```

- Final Manifest：`lifeos/engineering/LIFEOS-P3-126/evidence/FINAL_MANIFEST.json`（排除自身，其他声明项均受 SHA-256 保护）。

## 角色与关卡

- 主责角色：路径安全、Rust/Tauri Runtime、Evidence QA。
- 协审角色：数据主权、授权不漂移、生命周期、历史保全。
- 已覆盖评审关卡：Gate 2 与 Gate 4；Gate 1/3 的产品／接口零漂移核对。
- 不适用：Gate 5；本任务不触及风险关闭、Freeze、Schema/API、真实能力或 Stage 4。
- 仍需 PM/后续任务确认的关卡：Frozen ABF 的 M-001 平台 model/effort 来源。不得由本专项会话修改 ABF 或自行将用户确认等同于平台证据。

## 会话与上下文

- 本任务执行方式：New Session。
- 执行授权证据：用户投递的最终任务卡绝对路径；全新 Codex 工程会话；2026-08-26（Asia/Shanghai）接收。用户另行确认模型匹配，并已在 preflight 中按其实际来源披露。
- 若复用会话，上一任务是否已结束：N/A。
- 是否发现旧任务授权或范围被错误继承：No。
- 已重新读取的关键文件：根 `AGENTS.md`、`CURRENT_STATUS.md`、任务卡、Frozen ABF、Acceptance Governance、两份 Evidence 模板、任务卡指定的 PM／Role／Stage 章节、P3-125 明列只读输入与相关账本行。
- 是否发生工具输出截断或补读：Yes；按项目规则对 `CURRENT_STATUS.md` 补读至 EOF，未将截断输出当作证据。

## Agent 自评提示

- 本任务是否适合当前 Agent：High。
- 如果不适合，建议后续交给：PM（仅 M-001 治理判断）和全新隔离 Independent Review（若 PM 另行启动）。
- 原因：工程和 Evidence 属于 Codex 范围；Frozen ABF 的治理变更或最终验收不属于本专项会话权限。

## 交付物

- 完整交付物路径：本文件。
- 文件状态：Created。

## 需要 PM 决策

PM 需判断：在不追溯修改 `ABF-P3-126-v1` 的前提下，用户确认是否可作为 M-001 的可接受来源。当前 Evidence 不能证明“平台暴露”，因此若坚持 Frozen 原文，本任务应保持 `Partial / Not Pass`；如需不同依据，必须按 Acceptance Governance 新建或治理性处理，不能由本专项会话改写 ABF。

## 后续任务建议

若 PM 需形成 Pass 候选，建议由 PM／独立评审在具备原始平台配置记录的环境内做只读核验；不得重写或污染本次 P3-126 Evidence。

## 阻塞或异常

唯一阻塞是 M-001 的平台来源不可直接观测。其余范围内操作均已完成；不存在 P0/P1/P2 或 Not Implemented 项。
