# LIFEOS-P3-117 PM Review｜P3-116 当前候选隔离原生截图动态 Evidence 后继收口

## 验收信息

- 任务 ID：`LIFEOS-P3-117`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor_acceptance_basis_freeze.md`
- ABF ID／版本／PM 记录 SHA-256：`ABF-P3-117-v1` / `57d6016e338103f4f53b5e979d3ec2d5eca708e7622ade33c3ccfd8be1c2b0e0`
- ABF 是否在专项会话开始前 Frozen：Yes
- 本次反例是否全部映射到既有 L1/L2：Yes；见 `PM-CE-001`～`PM-CE-004`
- 正式 Rework 次数／上限：`0/2`；因需实质修改 ABF，不允许以剩余预算继续同任务
- 是否为受控能力包：Yes
- 能力包边界：P3-116 当前候选只读、task-local 临时 Chrome app-mode、原生窗口截图、Evidence／verifier／mutation 与精确清理
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md`
- 专项 Evidence：`lifeos/prototypes/LIFEOS-P3-117/MANIFEST.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/MANIFEST.md`
- 执行授权证据：专项报告记录用户投递绝对任务卡路径、2026-08-25 接收、全新 Codex 本地视觉 Evidence 会话、ABF ID/hash 与写入／只读边界；实际模型标签报告为 Unknown
- 任务验收状态：`Closed — Acceptance Not Met / Blocked User Adopted / Superseded by P3-118 / Read-only`
- 资产冻结状态：Not Frozen
- 是否允许进入下一任务：Yes；仅已获授权并正确重新冻结的 P3-118
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes；当前阻断记录可作为新 ABF 输入
- 实际执行 Agent：Codex
- Agent 与任务匹配度：Medium
- 更新时间：2026-08-25

## PM 总结

1. 任务卡与 `ABF-P3-117-v1` 文件 hash 均匹配，专项提交 Manifest 的 14 项 payload 也全部匹配；唯一临时根当前不存在。
2. 但 Frozen ABF 的 13 项固定输入并不自洽：它把 P3-116 PM Review 固定为采纳前 hash `f698…`，D-0473 与当前只读文件均明确为关闭更新后的 `09d810…`。专项 `fixed_inputs.json` 正确 fail closed。
3. 该冲突源于 PM 创建 P3-117 时错误冻结了旧历史快照；不是 P3-117 runner 可在原 ABF 下修复的问题。修正固定输入需要实质修改 ABF，依 D-0401 必须关闭当前任务并新建任务／新 ABF。
4. 专项没有把静态脚本伪报为动态通过：raw／proof／clean、geometry、46 个动作、三个 viewport、键盘／motion、baseline verifier 与 12 类 mutation 均明确未实现。
5. 专项所述 Computer Use 绑定到既有普通 Chrome 窗口没有保留可独立复核的结构化 Evidence。PM 将该项保持 Unknown，不把隐私保护下的停止叙述外推为已证实第二项 P0。
6. PM 最终计数：**P0=1、P1=0、P2=0、Unknown=2、Not Implemented=12**。结论为 Blocked，不是 Rework、Pass、Accepted 或 Frozen。

## 两层验收治理核对

- `PM-CE-001 / P0`：L1-7 Evidence 诚实、L1-8 历史保全、L1-9 授权不漂移、L1-10 可复核性；ABF 固定输入合同、M-001/M-013/M-015。Frozen PM Review hash 与 D-0473 权威历史冲突。
- `PM-CE-002 / Unknown`：ABF-I-02～I-05、M-002。专用 GUI 窗口身份／入口未形成可独立复核 Evidence。
- `PM-CE-003 / Unknown`：ABF-M-001。实际模型／推理强度标签无法独立确认。
- `PM-CE-004 / Not Implemented`：ABF-M-003～M-014。动态图像链、动作、viewport、键盘／motion、baseline verifier 与 mutation 未执行。
- PM 是否新增无法映射到 L1/L2 的标准：No
- 新发现问题分类：Blocked；必须新建任务
- 是否需要实质修改 ABF：Yes
- 是否仍满足同任务 Rework全部条件：No
- 是否达到两轮正式 Rework 上限：No；但剩余预算不允许修改 Frozen ABF
- 终止状态：`Closed — Acceptance Not Met / Superseded`
- 新任务触发理由：固定输入、取证入口和可复核窗口身份需要重新冻结；当前 ABF 不得原地修订

## PM 复算与 Evidence 摘要

| 项目 | PM 结果 |
|---|---|
| P3-117 任务卡 | SHA-256 `19ea3f…34ec1`，匹配 |
| Frozen ABF | SHA-256 `57d601…2b0e0`，匹配 |
| P3-116 PM Review | ABF 期望 `f698…`；当前及 D-0473 为 `09d810…`；BLOCKED |
| 13 项固定输入 | 12 匹配，1 冲突 |
| 专项 Manifest | 非自指；14/14 payload hash 与 bytes 匹配 |
| 交付物 | Manifest 声明 hash `8530b0…ad39`，实测匹配 |
| 动态 Evidence | 无 raw／proof／clean、geometry、逐行动作或 structured results |
| 临时根 | `/private/tmp/lifeos-p3-117-native-capture-v1` 不存在 |

PM 未启动 Chrome、未读取现有浏览器状态、未执行 GUI 动态取证，也未覆盖专项 Evidence。固定输入冲突在只读复算阶段已经触发停止。

## 视觉与交互审查

本轮使用 `apple-design` 原则作为视觉／交互 Evidence 完成度检查，但没有合格动态图像可供产品视觉判断。静态计划不能证明空间一致性、反馈、键盘焦点、reduced-motion 或三个 viewport 的实际结果；这些均按 Frozen ABF 计入 Not Implemented，不新增产品设计缺陷。

## 本地模型预检

跳过。此次是 Frozen ABF 冲突、浏览器隐私边界与 P0 最终治理判断，本地模型不得决定；任务同时禁止网络。PM 已直接完成 hash、Manifest 与清理状态复核。

## 角色与关卡验收

- 主责角色：Evidence QA 的 fail-closed 披露成立，但完整 Evidence 未交付
- 协审角色：隐私停止边界有诚实报告；体验、视觉、可访问性与技术闭环均未完成
- 已通过关卡：任务／ABF 文件身份、12/13 固定输入、Manifest payload、P3-116 八项候选／合同只读 hash、精确清理
- 未通过关卡：ABF 固定输入一致性、唯一 GUI 窗口身份、原生图像链、全量动态矩阵、三个 viewport、键盘／motion、verifier baseline、mutation
- 是否属于关键冻结事项：Yes；当前不冻结
- 是否需要独立评审：PM Pass 且用户采纳后才需要；当前禁止创建

## 受控能力包关卡

- 包内自检：No，专项诚实报告 Blocked
- 干净副本首次／幂等／重启：未执行完整闭环
- 原子失败／清理／拒绝与审计：固定输入 fail closed、临时根精确清理成立；GUI 阻断缺少独立 Evidence
- 验收标准→测试→Evidence：计划存在，实际动作 Evidence 缺失
- runner／结果／日志／快照／hash／Manifest：静态 runner 与预检可审计；动态必填资产缺失
- 历史只读资产：P3-116 八项候选／合同与其余匹配项未见漂移
- 是否首次正式 PM 验收：Yes
- 是否进入独立复评：No
- 是否回包整改：No；修改固定输入需要新 ABF
- 是否触发用户确认：Yes；采纳 Blocked、授权关闭及是否创建后继

## 资产与风险状态

- P3-116 继续 `Closed — Acceptance Not Met / Superseded / Read-only / Not Frozen`。
- P3-117 为 `Closed — Acceptance Not Met / Blocked User Adopted / Superseded / Read-only / Not Frozen`；提交资产和 PM Evidence 只读保全。
- R-0024、R-0025、R-0040、R-0052 保持 Open；R-0051 原 `Closed / Limited Controlled Boundary` 不变；本轮不更新风险事实。
- 不恢复工程基线、不冻结产品／原型／架构、不创建独立评审、不进入 runtime 或 Stage 4。

## 用户确认结果

1. 用户已采纳 P3-117 的 `Blocked / Not Pass / Acceptance Basis Conflict` 结论。
2. 用户已授权关闭 P3-117 为 `Closed — Acceptance Not Met / Superseded / Read-only`。
3. 用户已授权创建全新后继任务与新 ABF。PM 已创建 P3-118，正确冻结 D-0473 后的 `09d810…` P3-116 PM Review，并把窗口身份入口收窄为专用 Chrome 主 PID、PID 过滤唯一原生窗口和每动作前后 attestation。

## Agent 分派与适配度

- 推荐／实际 Agent：Codex / Codex
- 是否符合推荐：Yes
- 匹配度：Medium
- 优势：发现并诚实披露 Frozen 输入冲突；遇到疑似现有浏览器窗口时 fail closed；没有伪造动态 Evidence
- 主要问题：启动前质疑窗口未发现 ABF 冲突；实际模型和 GUI 阻断缺少可独立留存的非 ambient 结构化 Evidence
- 后续适合：新 ABF 下的隔离取证执行
- 不适合：自行修订 ABF、验收自身结果或进行后续独立评审
- 是否更新 Agent Routing Scorecard：No

## 下一步边界

- P3-117 已关闭，全部资产只读；不允许继续、同任务 Rework、独立评审、冻结、runtime 或 Stage 4。
- P3-118 与 `ABF-P3-118-v1` 已创建；只有用户将 P3-118 任务卡绝对路径投递至全新合格 Codex 会话才启动执行。新任务不追溯改写 P3-116/P3-117 历史。
