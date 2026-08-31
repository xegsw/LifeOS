# P3-141 Revision 3：bundle lineage 与原生窗口 Evidence Closure v5

## 任务信息

- 任务 ID：LIFEOS-P3-141
- 任务名称：Revision 3 model-settings bundle lineage 与 native capture Closure v5
- 执行 Agent：Codex
- 当前状态：Completed（仅工程侧 synthetic/offline Closure）
- 需要 PM 决策：Yes
- 任务类型：L3 工程实现、离线回归、actual-Tauri 原生 Evidence 与精确清理
- 风险等级：L3
- Task Contract 路径／章节：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md`
- L3/Gate ABF 路径／版本：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md`
- 是否在启动前发现合同歧义：No
- 当前状态：Completed
- 交付物篇幅是否在建议范围内：Slightly Over；L3 所需 Evidence、反例、PID/window 绑定与 cleanup 需要完整可复核指针。

## 执行摘要

1. v4 已按用户授权保留为只读 Blocked 历史；v5 在接触 Candidate 前创建并 hash 了 test design、write allowlist、prohibited-path 声明与 precontact seal。seal 明确 v5 之前无 Candidate／历史接触。
2. 仅修改 `candidate/build.rs` 与 `candidate/src/runtime.rs`：在既有严格 fail-closed 根名 allowlist 中增添精确字面量 `bundle-lineage-v5`。重建 v3 tree 后，82 文件 Candidate 的差异恰为这两条允许路径；无 DOM/CSS/Provider/凭据/IPC/runtime 业务语义改动。
3. 离线回归通过：串行、并行 Rust 均为 52 passed / 0 failed；`bundle-lineage-contract` 和 `mode-delete-ui-contract` 均 PASS；Tauri `.app` bundle 成功（仅 dead-code warnings）。
4. source → clean build input → debug binary → `.app` binary 绑定通过；debug 与 App 二进制 SHA-256 均为 `4e932ac8b8e34a4901a787f226ac474ab195320a9217229350bde10921720233`。
5. 静态合同 PASS，且 8 个反例（session wording、DeepSeek/Kimi、mode guard、credential IPC、encryption、resource binding、wrong tree）全部被拒绝。
6. 三次独立 direct launch 均完成 direct PID → 唯一精确标题 AXWindow → AXWebArea → Settings 点击 → 再验证 → 仅该窗口框截图：desktop PID 27051、compact PID 27189、narrow PID 27378。三张图均人工复核为实际“模型设置”页面，且每张像素几何匹配其 AXWindow frame 与 backing scale。
7. macOS desktop 的实际 AXWindow 可用 frame 为 1280×949 pt，而 v5 runtime 请求的 desktop evidence viewport 是 1280×1024；此平台 frame 约束已在 Manifest 明示，没有以 fullscreen 或整屏截图掩盖。compact 1160×768 与 narrow 700×760 的实际 AXWindow frame 均精确匹配请求。
8. marker-gated cleanup 的缺 marker、错 payload 与 symlink marker 均拒绝；正确 marker 后只删除 `/private/tmp/lifeos-p3-141-revision-3-engineering-bundle-lineage-v5`，最终 absence 已由只读 verifier 复核。

## 角色与关卡

- 主责角色：工程执行／Evidence 整理（Codex）
- 协审角色：N/A；本任务没有自行进行独立评审。
- Evidence 等级与已覆盖关卡：L3 工程侧 precontact、allowlist、源码差异、离线回归、mutation、source→bundle→PID、三档 actual-Tauri 目标窗口 Evidence、精确 cleanup、非自指 Manifest 与只读 verifier。
- 是否触发独立评审及理由：Yes，后续必须由隔离会话执行；当前 Agent 不能独立评审自己刚完成的 L3 结果。
- 仍需 PM/后续任务确认的关卡：独立评审、PM 验收，以及任何 Phase C／Pilot／真实 Provider／真实凭据／风险关闭或阶段结论。

## 会话与上下文

- 本任务执行方式：Reused Session
- 执行授权证据：用户明确授权先完成 v4 归档与 marker-gated cleanup，随后以固定唯一根新建并执行同一 Task Contract 的 v5；并精确限定可改 Candidate 的两条路径与 fail-closed 不变量。
- 若复用会话，上一任务是否已结束：Yes；v4 已归档 Blocked，且只读保留。
- 是否发现旧任务授权或范围被错误继承：No。
- 已重新读取的关键文件：根目录 `AGENTS.md`、`lifeos/CURRENT_STATUS.md`、P3-141 Revision 3 任务卡与 ABF、Model Settings baseline、v3 deliverable/Manifest、v3 invalidated PM review、会话回复模板。
- 复用既有读取结果的稳定文件：无会影响本 v5 范围／权限判断的未核对结论。
- 是否发生工具输出截断或补读：Yes；`CURRENT_STATUS.md` 与一次 source 定位输出截断后只补读了本任务所需段落，未把截断内容作为结论依据。

## Agent 自评提示

- 本任务是否适合当前 Agent：High
- 如果不适合，建议后续交给：WorkBuddy / PM
- 原因：下一步是对本工程 Evidence 的独立反例审查与 PM 验收，须与当前执行会话隔离。

## 交付物

- 完整交付物路径：
  - 本报告：`lifeos/deliverables/LIFEOS-P3-141_revision-3_bundle-lineage-and-native-capture-closure-v5_report.md`
  - 非自指 Manifest：`lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/BUNDLE_LINEAGE_CLOSURE_V5_FINAL_MANIFEST.json`
  - 只读 verifier：`lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/verify_bundle_lineage_closure_v5.py`
  - verifier PASS：`lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/evidence/bundle-lineage-closure-v5/BUNDLE_LINEAGE_CLOSURE_V5_VERIFIER_RESULT.json`
  - native visual review：`lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/evidence/bundle-lineage-closure-v5/native_visual_review.md`
- 文件状态：Created / Updated

## 需要 PM 决策

1. 是否接受此 synthetic/offline 工程 Closure 并安排全新隔离的独立评审。该决定不得被解释为 Pilot、Phase C、真实 Provider、真实凭据、风险关闭或阶段准入。
2. 是否把 desktop 1280×949 pt 的 macOS 可用 AXWindow frame（已保留其 1280×1024 runtime 请求与 target-only capture）作为本机环境的可接受实际 frame，或要求在具备 1024 pt 可用 frame 的受控环境中重采。需 PM 确认。

## 后续任务建议

- 若 PM 接受工程闭环，创建一个全新隔离的 L3 独立评审任务；其应先 seal 自有 test design/allowlist，禁止复用本次 PID、root、截图、fixture、结论或 verifier PASS 作为独立证明。

## 阻塞或异常

- 无工程阻塞。已保留但未掩盖的异常：最初 desktop/compact 交易的 footer 使用 bash `PIPESTATUS` 于 zsh，未写出 exit footer；实际 launch、pre/post AX probe、target click、目标窗口截图与几何已完成，随后只补写不重启/不重截的 PID-exited recovery record。narrow 使用修正后的状态写法并完整记录。
- 本报告的 Engineering Pass 仅指上述受控 synthetic/offline 工程合同；不构成独立评审、PM Acceptance、真实自用、风险关闭、产品冻结、Phase C 或 Stage 4 结论。
