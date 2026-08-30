# ABF-P3-141-v1 逐行矩阵｜attempt-6

状态定义：`PASS_PHASE_B` 是本轮可复算的 synthetic/offline 或受控 fixture 结果；`PENDING_PHASE_C` 按任务合同保留给真实7日／真实非内容收据，不计为本轮 Phase B 缺陷；`P0_BLOCKED` 为阻止独立 Pass 的硬门禁。

| 行 | 判定 | 本轮依据 | 说明 |
|---|---|---|---|
| ABF-M-001 | P1_REWORK | `candidate_lineage_corrected.json` | 12/12 frozen inputs 与 P3-140 79/79 tree PASS；候选 commit 是 `e4eeb…6ce5`，现树为 79／`290f1e…fae88`。工程 `source_lineage.json` 仍声明旧值 `6a45b…a87e1`，不等于当前候选树。|
| ABF-M-002 | PASS_PHASE_B | review root/type plus 52-test suite | root、DB、file/link/type failure paths在受控临时根写前拒绝。|
| ABF-M-003 | PASS_PHASE_B | `precontact_seal.json` | seal 前未接触任何 Pilot；本轮未访问真实根。|
| ABF-M-004 | PASS_PHASE_B | review profile test；provider fixture tests | 四 Profile 闭集；Custom、second、fallback、background 均被合成负路径拒绝；本轮没有 Provider 启用或发送。|
| ABF-M-005 | PASS_PHASE_B | 52-test suite | request-local 最小 bundle、授权重检和 disclosure receipt 合成复算；真实发送留在 Phase C。|
| ABF-M-006 | PASS_PHASE_B | seal、raw/screenshot 人工检查 | 仅固定合成内容；无真实正文、Health 值、凭据、prompt/response。|
| ABF-M-007 | PASS_PHASE_B | 52-test suite + review Health test | Memory/State身份分离、confirmed Memory≤3、五字段 Health 与写前拒绝覆盖。|
| ABF-M-008 | PENDING_PHASE_C | 合同范围 | 真实7日日期覆盖。|
| ABF-M-009 | PENDING_PHASE_C | 合同范围 | 真实 Person+Today 结果。|
| ABF-M-010 | PASS_PHASE_B | 52-test suite | 预算、domain、receipt 与最小披露合成复算。|
| ABF-M-011 | PASS_PHASE_B | `repeated_request_is_stable_and_feedback_invalidates_only_target_slice`；UI feedback receipt | synthetic stale/recompute PASS；受控 UI confirm 后产生新 Today request。|
| ABF-M-012 | PASS_PHASE_B | `cross_domain_authorization_and_request_removal_are_scoped` | Health 移除为 request-local，后续不继承。|
| ABF-M-013 | PASS_PHASE_B | fixed-scenario/counterfactual suite | Health safety-stop 为非诊断的受控候选；没有医疗或治疗输出。|
| ABF-M-014 | PASS_PHASE_B | review Health/root tests + closure/provider tests | auth/stale/budget/DB/provider 失败写前关闭；sentinel/计数断言成立。|
| ABF-M-015 | PASS_PHASE_B | receipt/restart/provider tests | 无重发、重复写、复活或 request_id 复用。|
| ABF-M-016 | P0_BLOCKED | `actual_tauri_identity.md` | 三 direct PID、receipt、AXWindow、尺寸、截图均新鲜；但 native PID AX 未暴露 AXWebView/AXWebArea。|
| ABF-M-017 | PENDING_PHASE_C | 合同范围 | 用户真实非内容收据。|
| ABF-M-018 | BLOCKED | 本独立评审 | P0 M-016 阻止独立 Pass；不得把 supporting PASS 变成 gate Pass。|
| ABF-M-019 | PASS_PHASE_B | `raw/cleanup_and_retention.json` | 唯一临时根已精确删除；未探测、删除或保留任何 Pilot／真实 DB。|
| ABF-M-020 | PASS_PHASE_B | `FINAL_MANIFEST.json` | attempt-6 非自引用 Manifest 已独立生成并复算 PASS。|

结论：P0=1（M-016），P1=1（M-001），P2=0，Unknown=0，Not Implemented=0；Phase C 三项为合同规定的 `PENDING_PHASE_C`，不与 P0/P1 混同。
