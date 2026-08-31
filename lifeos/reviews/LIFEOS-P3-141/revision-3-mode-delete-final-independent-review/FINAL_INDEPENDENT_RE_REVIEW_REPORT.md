# LifeOS P3-141 Revision 3 mode-delete final independent re-review

## 评审信息

- 对应任务 ID：LIFEOS-P3-141 Revision 3 mode-delete closure。
- 受控能力包：Yes；仅合成／离线 Revision 3 候选，禁止 Pilot-6、真实 DB／文本／Health／Provider／凭据／网络。
- 被评审候选：commit `20a932ff266e74304490fbb1748900ddad082ac2`，路径 `lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate`。
- 启动时 HEAD：`f0c6cc6fc5b01823cb0c2bfabce0eb49d776ea58`；候选为只读输入。
- 独立评审角色：Codex（用户明确指定的新隔离评审会话）。协审／裁决：PM 待处理。
- 评审关卡：L3 mandatory independent re-review。
- 评审路径：本目录；唯一临时根为 `/private/tmp/lifeos-p3-141-revision-3-independent-review-mode-delete-v1`，已精确清理。
- 评审结论：**NOT PASS — REVIEW ATTEMPT INVALIDATED；同一能力包应进入 Rework。**
- 风险等级：L3。
- 独立评审触发事实：Revision 3 mode-delete Closure 后的强制全新隔离复评。

## 独立性与输入边界

- 预接触顺序成立：先写入并 hash `test_design.md`、`write_allowlist.json`、`prohibited_paths.md`、`precontact_seal.json`，再接触候选／工程 Evidence／历史材料。对应 seal hash：`76d90a368c8c6565d1058ca7430cb3f9dda1906f6ea8742fffe9a59298b1712c`。
- 候选只读；评审写入仅发生于本目录和授权临时根。未改候选、PM 台账、冻结资产、风险台账或工程 Evidence。
- 四个 Frozen 输入均独立 hash 匹配，见 `static_verification_pre.json`。
- 候选的预运行快照为 81 个文件、tree SHA-256 `0e8b5b2ef31c100deccc6fb02e95a5011a78672c0dee0e9fcf5608a7116906c5`。P0 发现后按合同停止正向验证，未将后续候选 hash 再包装为通过证据。
- 评审自有 Rust 测试、静态 verifier、六个 mutation、native AX helper 和 cleanup control 均在本包保留；没有导入、调用或复制候选测试作为 review-owned 测试源码。

## 评审摘要

1. 静态 pre-check 曾对 Frozen 输入 4/4 与 review-owned IRV-01～IRV-12 通过；这不足以覆盖实际 UI，也不构成独立 Pass。
2. 在授权临时副本中，候选原有 51 项回归加 1 项 review-owned 生命周期测试为 52 passed / 0 failed；该结果同样被随后的实际 UI P0 覆盖。
3. 六个 review-owned mutation 全部被 verifier 拒绝：draft delete guard、Provider set、session fallback、Cloud/Local cross-use、build root authority、marker binding。
4. actual-Tauri bundle 由直接启动的 PID `5841` 绑定到唯一精确标题 `LifeOS · P3-141 Controlled Pilot Candidate`、`AXWindow`、`AXWebArea` 和 geometry `221,33,1280,949`；相关 JSON 保留在 `gui/desktop-fast-ax-window-webview.json`。
5. 同一实际 Settings UI 显示 session-only API Key 文案和 session 清除动作，直接冲突于 Frozen 的 encrypted-SQLite persistent credential contract，记录为 `IR-P0-01`。
6. macOS 未暴露 `AXWindowNumber`；截图 helper 的 display fallback 意外包含任务外桌面信息。PNG 已精确删除，但该触达自身构成 `IR-P0-02`，本次评审程序性失效。
7. P0 后不再做 UI 操作、候选分析或正向复测；仅做直接 PID 退出、敏感截图删除和 marker-gated 临时根清理。

## 已通过的有限事实（不提升为 Pass）

- Frozen 输入 hash 4/4 一致；review-owned 静态预检 12/12 PASS，详情见 `static_verification_pre.json`。
- `cargo test --locked --offline` 在 task-local clone 中最终为 52 passed / 0 failed，详情见 `cargo_test_review_owned_retry.log`；其中仅 1 项为本评审自有生命周期测试。
- `cargo tauri build --debug --bundles app -- --locked --offline` 成功，日志见 `cargo_tauri_build_review_owned.log`；候选 `src/runtime.rs` 与直接启动 bundle binary hash 见 `native_source_binary_hashes.sha256`。
- 六项候选 mutation 均按预期失败；每项 JSON 在 `mutation-*.json`。
- cleanup control 的 baseline PASS，marker-content bypass 被 verifier 拒绝；错误／缺失 marker 的真实清理也被拒绝。正确 0600 marker 后，唯一临时根精确删除并证明 absent，见 `cleanup-*.json`、`cleanup-root-absence.txt`。

这些只是可保留的负向／诊断事实；它们不能抵消 P0，不能作为产品冻结、PM 验收或阶段推进的依据。

## 关键问题

### IR-P0-01 — 实际 UI 把 API Key 定义为本次会话状态

在直接 PID 绑定的实际 Settings 画面中，审阅到以下产品文案与动作：`本次会话 API Key 已提供；输入可更新`、`API Key 仅保留在本次会话，可随时清除。`、`清除本次会话 API Key`。

这与 ABF-P3-141-v3 的 encrypted SQLite persistent credential、restart persistence、store/update/delete 和“没有 session/env 产品选项”冲突。该观察的最小非敏感记录在 `P0_OBSERVATION.md`；原 PNG 因第二个 P0 已删除，不能作为 retained positive Evidence。

### IR-P0-02 — display screenshot fallback 触达任务外桌面信息

由于没有可用的 `AXWindowNumber`，helper 用 display capture fallback 取得截图。它包含目标窗口之外的桌面信息，违反零真实文本边界。该 PNG 已立即精准删除，见 `gui/screenshot-sanitization.md`；但删除不能消除已经发生的越界触达。因此本次独立评审 attempt 失效，后续控制不能恢复其独立性。

## 计数与异常

- 候选／产品 finding：P0=1（IR-P0-01），P1=0，P2=0，Unknown=0，Not Implemented=0。
- 评审程序 finding：P0=1（IR-P0-02，attempt invalidated），P1=0，P2=2，Unknown=0，Not Implemented=0。
- P2 仅为已留痕且无候选写入的评审环境操作：初次 Cargo 测试的 task-local `TMPDIR` 未创建；首次 cleanup 调用漏传脚本必填参数，均在同一授权根内停止／修正。它们不改变 P0 结论。
- 合并报告计数：P0=2，P1=0，P2=2，Unknown=0，Not Implemented=0。

## Closure List

1. 回到同一 P3-141 Revision 3 capability package，修复 Cloud Settings 的 API Key 文案、状态与删除动作，使其只表达 encrypted SQLite persistent store/update/delete，不得出现 session 或 environment credential 语义。
2. 工程侧需重新完成同范围动态 Evidence，并将最终 source／binary／PID／exact-title window／WebArea 绑定到可裁剪为目标窗口的原生 capture 路径；不得再回退到整屏 capture。
3. 之后必须在全新隔离评审会话、全新预接触 seal 和全新授权临时根中重做 mandatory independent re-review。不得复用本 attempt 的任何 positive conclusion；本包只读保留为失败历史。

## 关卡检查

- Gate 1 产品一致性评审：Rework；实际 UI 文案与冻结产品契约冲突。
- Gate 2 数据与来源评审：未推进；未触达真实数据。
- Gate 3 AI 权限与信任评审：Rework；session credential 语义违反权限与存储边界。
- Gate 4 技术可行性评审：Rework；静态／合成结果存在，但不能覆盖 actual-Tauri P0，且本评审程序失效。
- Gate 5 用户价值验证：未适用／未推进。

## 风险与需要 PM 决策

- PM 必须将本轮处理为 `Independent Re-Review: Invalidated / Rework`，保留本目录为失败历史。
- PM 需决定何时在原 Task Contract 内安排工程 Closure Cycle；该决定不需要也不获得 Phase C、Pilot-6、真实 Provider、风险关闭、产品冻结或 Stage 4 的授权。
- 不更新 PM 台账、不关闭风险、不恢复 Phase C，均由本专项评审会话明确保留给 PM。

## 会话报告（SESSION_REPORT_TEMPLATE V2）

### 任务信息

- 任务 ID：LIFEOS-P3-141 Revision 3 mode-delete final independent re-review。
- 执行 Agent：Codex。
- 当前状态：Partial / Rework / review attempt invalidated。
- 需要 PM 决策：Yes。
- 任务类型：L3 mandatory independent re-review。
- 风险等级：L3。
- Task Contract：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md`。
- ABF：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md`（ABF-P3-141-v3）。
- 启动前合同歧义：No。
- 交付物篇幅：Slightly Over；需要保留 P0、独立性、动态 PID 链和精确清理的可复核事实。

### 角色与关卡

- 主责角色：独立技术／Evidence 复评。
- 协审角色：PM 复核与工程 Closure Cycle 裁决待处理。
- Evidence：预接触 seal、review-owned verifier／mutation／lifecycle test、direct PID AX 记录、failed-history preservation、marker-gated cleanup；actual visual screenshot 因越界已删除且不能作正证。
- 触发独立评审：Yes，任务与 ABF 明确为 mandatory L3 re-review。

### 会话与上下文

- 本任务执行方式：New Session。
- 执行授权：用户投递完整 Task Contract，授权合同内只读独立评审、测试、Evidence、清理和提交。
- 错误继承旧授权：No。
- 已读取：根 `AGENTS.md`、`lifeos/CURRENT_STATUS.md`、Task Contract、ABF、Revision 3 fixed input inventory、当前 PM engineering gate、`ACCEPTANCE_GOVERNANCE.md`、相关 PM／角色／阶段规则章节及两份模板。
- 稳定文件重读：上下文整理后重读了本轮所需的模板。
- 工具输出截断／补读：Yes；`CURRENT_STATUS.md` 的大段历史输出发生截断，按行段补读；不影响本任务当前 P3-141 结论。

### Agent 自评、交付物与后续

- 当前 Agent 适配度：Medium；用户明确指定 Codex，具备只读验证与 actual-Tauri AX 能力；下一次强制独立复评宜由 PM 另派新隔离会话。
- 完整交付物：本目录，Created。
- 后续任务建议：仅原能力包内工程 Closure Cycle 与其后的全新隔离 independent re-review。
- 阻塞／异常：存在两项 P0；本 attempt 已失效，不能完成 Pass。

## 最终建议

不建议冻结、验收、恢复 Phase C、启动 Pilot-6、授权真实 Provider、关闭风险或进入 Stage 4。建议 PM 将当前 P3-141 Revision 3 退回同一能力包的 Closure Cycle；修复完成后，再由全新隔离评审会话从新的 precontact seal 开始。
