# LIFEOS-P3-126 PM Review

## 验收信息

- 任务：`LIFEOS-P3-126`
- Frozen Basis：`ABF-P3-126-v1`，SHA-256 `8e98f4d874d3925bdad308f800f01d7c44b02c3016e71f19083cad4fc13fb908`
- 正式 Rework：`1/1`
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md`
- PM 结论：`Rework 1/1 / Awaiting User Adoption / Acceptance Basis Unchanged / Not Frozen`
- 本地模型预检：跳过；本轮是 P0 路径授权、actual-Tauri/IPC 与模型启动门最终判断。

## PM 总结

P3-126 的 clean-start 技术 Evidence 基本完整：candidate 与 P3-125 Rework-1 75/75 byte-exact，PM 复跑 Final verifier PASS，123-entry Manifest、M-002～M-012、actual-Tauri 双根与三 IPC、失败关闭、八类 mutation、6项直接历史输入 before/after 和精确 cleanup均有可复核结果；固定 P3-126 temp root当前 absent，PM 未探测旧 P3-122 Runtime root。

但 Frozen ABF 的 M-001 与 Evidence 合同要求在任何 candidate read／execution-root创建前记录“平台暴露”的 actual model/effort；无法记录必须 action-before stop。专项明确记录平台未暴露该字段，只取得用户确认，并把 M-001 标为 Unknown，却仍继续读取 candidate、创建根并完成执行。这既留下 Unknown，也违反启动门失败关闭和任务卡的必须升级／停止条件。

该问题映射既有 L1-4、L1-7、L1-9、ABF-I-01、ABF-M-001，不是新增验收要求。因为原 preflight 在动作前已记录用户确认，若能补充与原 P3-126 会话绑定的真实平台 UI 截图或原始 metadata，证明当时实际配置确为 `gpt-5.6-terra / xhigh`，可在不重跑工程、不修改 ABF的情况下补齐事实证明。因此进入唯一一次 Evidence-only `Rework 1/1`，不立即关闭。

## 独立复核摘要

- PM verifier：`PASS / errors=[]`。
- Final Manifest：123 entries，17 roles，repository-relative paths，排除自身。
- Candidate：与 P3-125 Rework-1 candidate `diff -qr` 无差异。
- Dynamic closure：M-001 Unknown，M-002～M-012 PASS。
- History：6/6 current hash匹配，before/after相同。
- Mutation：pristine PASS；root、fallback、derive、order、history、extra、path、omission均拒绝。
- Cleanup：`/private/tmp/lifeos-p3-126-clean-closure-v1` absent。
- 旧 P3-122 Runtime root：PM未做 access/stat/hash/create/cleanup。

## P0／P1／P2／Unknown／Not Implemented

| 类别 | 数量 | 结论 |
|---|---:|---|
| P0 | 1 | M-001 无平台 model/effort Evidence时应在动作前停止，但专项继续读取候选、创建根并执行，违反 Frozen startup fail-closed。 |
| P1 | 0 | 未确认 actual-App 生命周期退化。 |
| P2 | 0 | 无轻微阻断项。 |
| Unknown | 1 | 原 P3-126 会话实际 model/effort只有用户确认，没有平台 UI／原始 metadata证明。 |
| Not Implemented | 0 | 12 行、runner、mutation、Manifest 与 cleanup均已实现；M-001是未知／失败，不是缺失。 |

## Rework 1/1 最终窄整改边界

1. ABF、任务卡、allowlist、P3-125输入、P3-126 candidate、initial Evidence／delivery全部只读；不得重跑 runner、读取 candidate、创建 temp root或改写 initial文件。
2. 唯一允许结果：为“原 P3-126执行会话”提供平台真实 Evidence，明确同时显示／导出该会话身份、模型 `gpt-5.6-terra` 和 effort `xhigh`。用户口头确认、任务卡推荐值或新会话配置不能替代。
3. Evidence须为最小裁剪、非敏感的平台 UI截图或原始平台 metadata；记录采集时间、来源、原会话绑定说明、bytes/SHA-256。不得包含其他聊天、个人数据、凭据或 ambient内容。
4. 新资产只写 P3-126 task-owned `rework-1/` Evidence和新的 Rework deliverable；不得覆盖 initial资产。
5. verifier只验证该平台 Evidence文件存在、hash与原会话绑定字段完整，并把 initial M-001＋补充 Evidence合并为闭环；不得把自述字段当平台证明。
6. 不访问旧 P3-122 Runtime root、Pilot、真实数据／路径、网络或产品模型；不修改风险、冻结、Schema/API、UI、IPC或阶段。
7. 若原 P3-126会话无法提供上述平台证明，立即关闭 `Closed — Acceptance Not Met`；不得再执行工程、不得第二轮 Rework或新建微任务。

## 风险、冻结与下一步

- P3-126 Not Frozen；R-0051保持原有限关闭，R-0040/R-0052及其他风险不变。
- 不创建独立复评，不进入 Stage 4。
- 等待用户采纳并授权唯一 Evidence-only Rework 1/1。

## 最终结论

`REWORK 1/1 / NOT PASS / AWAITING USER ADOPTION`

P0/P1/P2/Unknown/Not Implemented：`1/0/0/1/0`
