# LIFEOS-P3-141｜Phase B Mandatory Independent Review attempt-6

## 评审信息

- 对应任务 ID：LIFEOS-P3-141
- 是否为受控能力包：Yes；Phase B synthetic/offline 与受控 fixture，绝非 Phase C 真实 Pilot。
- 被评审候选：commit `e4eeb73395151955c0b833965979be1806406ce5`，只读；candidate 79 regular files，当前 framed tree SHA-256 `290f1e3a76eea7c73604c6f0068c0b3cf57f5b3f7e9bdf5547a8bfcc164fae88`。
- 工程 Manifest：130/130 文件 hash 独立复算一致，Manifest 自身明确排除，见 `evidence/matrices/candidate_lineage_corrected.json`。
- 独立评审角色：Mandatory Independent Reviewer（Phase B）。
- 协审视角：数据／来源、AI权限与信任、actual-Tauri/PID/AX、Evidence lineage。
- 风险等级：L3 / Gate。
- 独立评审触发事实：ABF-P3-141-v1 的 Mandatory Independent Gate，且 attempt-4 有 viewport/Health UI P0 历史。
- 独立评审路径：本目录；唯一临时根为 `/private/tmp/lifeos-p3-141-controlled-pilot-v1`。
- 评审结论：**Blocked（P0）**；另有 P1 Rework。不是 Pass、不是 PM Accepted、不是 Frozen、不是风险关闭，也不代表 Stage 4。

## 独立性与启动保全

- 本评审在接触候选前自行写入并 SHA-256 固化 `test_design.md`、`write_allowlist.md` 和 `precontact_seal.json`；对应 hash 见 `precontact_hashes.sha256`。
- seal 前仅从 PM 主工作区绝对路径读取治理输入；12/12 fixed inputs 的字节数和 hash 全部一致。
- seal 前没有枚举、读取、hash 或触及当前候选工程根／历史 review／任何 Pilot；没有访问禁止的既有 Pilot、真实 DB／文本／Health、真实 Provider、凭据或网络。
- seal 后，候选固定 commit 精确匹配；candidate 未修改。独立 runner 是 `tools/independent_runtime_tests.rs`，只临时注入审查 clone，未导入、调用或复制执行侧测试作为唯一正 Evidence。
- attempt-4 历史仅在 seal 后以只读方式查看结论，未复用其 test design、fixtures、DB、PID、窗口、截图或结论资产。

## 事实

1. 固定输入 12/12、P3-140 baseline 79/79 tree、候选 79 files、恰好20 IPC、工程 Manifest 130/130 non-self-reference 均已独立复算；见 `evidence/matrices/candidate_lineage_corrected.json`。
2. review-owned mutation/negative tests 在受控 real fixture 下 4/4 PASS；合成全套交叉回归 52/52 PASS。覆盖路径／根类型、日Work额度、provider四闭集、Health五字段及缺字段／free-text／多来源写前拒绝、budget/authorization、Memory cap、feedback stale/recompute、restart/no-repeat 和 provider失败关闭。详情见 `evidence/mutations/mutation_results.md` 与 logs。
3. actual-Tauri 使用本轮新构建的、未签名 release `.app` bundle；每一档皆是自身 direct-launch PID，receipt 的稳定样本与该 PID 的唯一 exact-title AXWindow 尺寸一致：desktop 30637 (1280×949)，compact 30792 (700×760)，narrow 30875 (560×640)。三张独立合成截图经人工视觉检查可用。
4. attempt-4 的两项技术反证均得到正向 supporting evidence：三档 receipt 具有 post-set-size 3-sample metadata，且不复用首档；受控真实 fixture 下 Health UI 成功写入唯一 `source:synthetic:controlled-fixture` 与五字段 SQLite，并触发新的 Today request/feedback audit。
5. 但三档 native AX PID probe 在 exact-title AXWindow 下都没有找到 `AXWebView` 或 `AXWebArea`；属性级最后复核亦未找到。Computer Use 可见 `HTML content` 与 `tauri://localhost`，但它不是同一 PID 的原生 `AXWebView/AXWebArea` binding，不能替代合同节点。
6. 工程 `evidence/source_lineage.json` 中的 P3-141 candidate tree SHA-256 `6a45b656…a87e1` 与本固定 commit 的实际 tree SHA-256 `290f1e3a…fae88` 不一致。工程 Final Manifest 本身可验证，但该 lineage field 在 candidate 修改后仍旧陈旧。

## 逐行结论

完整 ABF-M-001～020 判定在 `evidence/matrices/abf_matrix.md`。

- Phase B supporting PASS：M-002～007、M-010～015、M-019～020。
- Phase C contract-pending：M-008、M-009、M-017。它们是 `PENDING_PHASE_C`，不应被写成 Phase B 缺陷或 Pass。
- P1：M-001（candidate `source_lineage.json` 的当前树 hash 不一致）。
- P0：M-016（同 direct PID 的 AXWebView/AXWebArea binding 未证明）。因此 M-018 不能是独立 Pass。

## 关键问题

### P0-IR-AX-001｜native PID AX identity chain 缺少 AXWebView/AXWebArea

- 事实：每个 direct PID 均有唯一 exact-title AXWindow，尺寸与稳定 receipt 一致；然而 `raw/desktop_bundle_ax_pid.json`、`raw/compact_bundle_ax_pid.json`、`raw/narrow_bundle_ax_pid.json` 和属性级 `raw/ax_attribute_probe_final.json` 都报告 `has_ax_web_area:false` 与 `has_ax_web_view:false`。
- 影响：不满足 ABF-M-016“direct PID/AX/WebView”强制身份链。截图、app-level semantic `HTML content` 或全局 app 搜索均不能补替。
- 判定：P0，Blocked；本 attempt 不可产生 independent Pass。

### P1-IR-LINEAGE-001｜P3-141 source lineage 的 current candidate tree hash 陈旧

- 事实：`evidence/source_lineage.json` 声明 P3-141 candidate 为 79／`6a45b656…a87e1`；本固定 commit 的 review-owned framed tree 是 79／`290f1e3a…fae88`。
- 影响：当前 candidate 的 Evidence lineage 不能由该声明单独复核。工程 Final Manifest 的 per-file hash 仍通过，故这不是文件内容篡改结论。
- 判定：P1 Rework；必须由执行侧在同一 Task Contract 内重建并说明谱系，再由新的隔离 attempt 复核。

## 已通过的有限内容

- 仅限 Phase B synthetic/offline 与受控 fixture：固定输入、20 IPC、provider闭集、结构化 Health 写入／拒绝、root/type/budget/authorization/DB 的写前失败关闭、Work限制、Memory cap、feedback/restart 等 supporting evidence 可作为 Closure Cycle 输入。
- 三档窗口的 receipt 稳定性和同 PID AXWindow 尺寸对照解决了 attempt-4 的“首档旧几何／AX尺寸不一致”问题。
- 受控 Health UI 使用了正确的唯一 fixture source，解决了 attempt-4 的 source mismatch；它不代表真实 Health 录入、真实 Provider 或真实 Pilot。

## Closure List

1. 执行侧需使 direct PID 的原生 accessibility 链可复算地暴露或证明 `AXWebView/AXWebArea`，并在全新隔离 review 中对每档从 PID→exact title AXWindow→Web node 采集新证据。不得复用本 attempt PID、截图、窗口或 receipt。
2. 执行侧需重建 P3-141 current candidate `source_lineage.json`，使候选树 hash 与固定 commit 一致，并保留新 Evidence/Manifest 关系。
3. 两项都在原 P3-141 Task Contract 内，进入同一 Closure Cycle；修复后由 PM 重新安排全新独立复评。不得把本 attempt 的 supporting PASS 直接提升为 gate Pass。

## 条件通过项

无。P0/P1 均非“Pass with Conditions”可接受条件。

## 关卡检查

- Gate 1 产品一致性：未在本评审作最终产品冻结判断。
- Gate 2 数据与来源：P1 Rework（current source lineage tree hash 陈旧）。
- Gate 3 AI 权限与信任：Phase B supporting checks PASS；真实 Provider/Phase C 未启用，不能判完成。
- Gate 4 技术可行性：Failed/Blocked（P0-IR-AX-001）。
- Gate 5 用户价值验证：PENDING_PHASE_C；不作真实 N=1 价值结论。

## 风险与状态边界

- P3-141 已有真实 Pilot 风险保持 Open；本评审无权关闭风险。
- Phase C 的真实日数、真实非内容收据与用户真实发送仍 `PENDING_PHASE_C`。它们没有发生，本评审也没有触碰其根或数据。
- P0=1，P1=1，P2=0，Unknown=0，Not Implemented=0（Phase C 用显式 Pending，而非 Unknown/Not Implemented）。按 ABF Pass 公式，本 attempt 不通过。

## 需要 PM 决策

1. 接受本 attempt 的 `Blocked`，将 P0-IR-AX-001 和 P1-IR-LINEAGE-001 回流同一 P3-141 Closure Cycle。
2. 在执行侧修复后，安排新的、全新隔离的 Mandatory Independent Review；不得复用 attempt-6 任何 runtime/PID/window/screenshot/DB/test design。

## 最终建议

不建议冻结、PM Accepted、风险关闭、Phase C 启动或 Stage 切换。建议先完成同合同 Closure Cycle，再进行新隔离独立复评。
