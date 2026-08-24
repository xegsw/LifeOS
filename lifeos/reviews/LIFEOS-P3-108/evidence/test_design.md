# P3-108 独立测试设计（候选读取前冻结）

## 冻结元数据

- 任务：`LIFEOS-P3-108`；ABF：`ABF-P3-108-v1`。
- 设计时间：2026-08-24 CST；设计者：本全新 Codex 独立评审会话。
- 设计依据：已投递任务卡、Frozen ABF、`ACCEPTANCE_GOVERNANCE.md` 的 L1-1 至 L1-10，以及任务卡所载的用户结果和非范围。
- 独立性声明：截至本文件落盘，未读取、复制、导入或执行 P3-104/P3-106/P3-107 的 runner、tests、tools、结构化结论或 Evidence；未读取 P3-106 候选源码。后续仅允许把候选作为只读被测对象。
- 固定临时 token：`p3108a1`。全部临时路径须逐个在台账登记，创建前 `lstat` 目标缺失并检查每级祖先不是链接；只可精确删除台账中的路径。
- 动态原则：每个动态用例都以实际离线 Tauri app 为被测入口；需记录动作前置、操作、可观察结果、唯一 ID、日志／截图、SHA-256。静态扫描、旧截图和 AX 属性均不可替代真实动作。

## 执行顺序与独立边界

1. 先计算 ABF／任务卡 hash，记录实际会话、模型配置、授权和固定快照；任何不可证实的严格模型配置、ABF hash 或固定输入漂移立即停止为 `Blocked`。
2. 以独立脚本对 ABF 的固定快照、两层历史 Manifest、旧 P3-107 残留及受保护旧临时文件的 `lstat` metadata 做只读核验。P3-104 PM Review 只能接受 ABF 指定的一次 `PASS_TIME_QUALIFIED`，不能扩展豁免。
3. 只用 ABF 正向 allowlist 从空目录组装构建副本；先检查禁项零个，再离线 `--locked` test/build/bundle。不得复制 Evidence、runner、tools、tests、缓存或隐藏状态。
4. 在独立评审侧新写 runner、fixture 和结果格式；生成的源码必须具有唯一 `P3108-` 测试／执行 ID，且不从提交资产导入或执行测试逻辑。
5. 仅用全新、固定非敏感文本和 task-local SQLite 夹具启动实际 app。每个动态动作结束后记录 app 可观察状态、DB/audit/sentinel 的允许范围结果及 Evidence。所有失败夹具必须在变更前拒绝，并核验零副作用。
6. 在清理前核验 Evidence 负门、网络／隐私和历史保护；清理仅作用于台账列出的 P3-108 路径。清理后再复算受保护输入、确认 P3-107 旧路径缺失、检查 P3-108 残留为零，并生成不自指 Manifest。

## 16 行独立矩阵

| ABF 行 | 独立测试 ID | 方法与断言 | 预期 Evidence |
|---|---|---|---|
| M-001 | `P3108-M001-identity` | hash ABF／任务卡；核对冻结、会话独立性、当前快照与严格配置记录 | `authorization.json`、`snapshot.json` |
| M-002 | `P3108-M002-design` | 本设计先于任何提交 runner/tests/tools 的读取落盘，记录时间与 SHA-256 | 本文件 hash、读取顺序日志 |
| M-003 | `P3108-M003-manifests` | 独立解析并复算 P3-106 325 条，复算 P3-104 全部条目；只接受指定 PM Review 的成对旧／新 hash | `manifest-verification.json` |
| M-004 | `P3108-M004-copy` | 空目录正向 allowlist 复制；inventory 必须无 Evidence／runner／tools／tests／隐藏构建状态 | `copy-inventory.json` |
| M-005 | `P3108-M005-build` | 空 target、`CARGO_NET_OFFLINE=true`、`--locked` 的 test/build/bundle 均退出 0；日志无 network | `build/*.log` |
| M-006 | `P3108-M006-static` | 审计副本 runtime/main/capability/Cargo/路径；仅三项 IPC，无 generic 权限／联网依赖；与 P3-104 同文件字节一致 | `static-results.json` |
| M-007 | `P3108-M007-visual` | 在 1280×1024 实际 app 中逐页比较三张冻结 Stitch 的共享骨架与专属锚点；截图不是被测 UI | 三张 app 截图、目视比较表 |
| M-008 | `P3108-M008-responsive` | 原工作区及 700×760 实际 app：滚动、无遮挡、三页往返、关键控件可达；不改显示设置 | 三组截图、动作日志 |
| M-009 | `P3108-M009-first-capture` | nominal app 首次 capture；只在成功回执后检查 DB/audit/sentinel 一致 | `lifecycle/first.json`、截图 |
| M-010 | `P3108-M010-repeat-conflict-failure` | repeat 幂等；conflict 不覆写；注入失败原子、无半成品 | 三个独立 fixture 结果 |
| M-011 | `P3108-M011-refresh-reopen` | refresh、三页导航、关闭后重新启动；后端权威状态一致且无陈旧 UI | 日志、截图、结果 |
| M-012 | `P3108-M012-denied` | 未实现 UI 控件、unknown IPC、额外字段均明确拒绝且零副作用 | `denied.json`、日志 |
| M-013 | `P3108-M013-path-boundary` | 本地路径、外部路径、链接、hardlink、异常类型均在任何变更前 fail-closed | 每类 fixture 结果与 before/after |
| M-014 | `P3108-M014-tamper-boundary` | dangling final/journal/wal/shm、content/schema tamper 均分别 fail-closed、零副作用 | `negative-matrix.json` |
| M-015 | `P3108-M015-a11y-privacy` | 实际 Tab／Enter／skip／focus／reduced-motion；扫描 remote URL、网络调用、真实数据、截图复用 | a11y 闭环、扫描输出 |
| M-016 | `P3108-M016-cleanup` | 精确清理后 P3-108 残留 0，P3-107 旧路径缺失，保护历史与旧临时 metadata 不变；final verifier 对缺项/FAIL/泄密真实非零 | cleanup、final verifier、非自指 Manifest |

## 动态闭环用例清单

下列每个 ID 必须在闭环表中有各自的操作、可观察结果、结构化结果、日志／截图与 SHA-256；禁止由相邻动作代替。

| 动作 ID | 前置与实际操作 | 可观察通过条件 |
|---|---|---|
| `P3108-D01` | default-recovery 页面初启 | 目标结构、原文／系统／AI／来源身份清晰，未实现控件无副作用 |
| `P3108-D02` | no-reliable-suggestion 页面初启 | 目标结构与关闭态诚实 |
| `P3108-D03` | restricted-offline 页面初启 | 离线／权限边界可见，无外部触发 |
| `P3108-D04` | nominal 首次 capture | 仅成功后出现 saved、DB/audit/sentinel 一致 |
| `P3108-D05` | repeat capture | 幂等，数量与审计不重复增加 |
| `P3108-D06` | conflict capture | 认知冲突回执，无覆写／半成品 |
| `P3108-D07` | injected failure capture | 失败披露，DB/audit/sentinel 无新增 |
| `P3108-D08` | refresh 后检查 | 真实 backend 状态重新呈现 |
| `P3108-D09` | 三页往返 | 页面状态和关键操作均可达 |
| `P3108-D10` | app 关闭并重启 | 不依赖旧前端缓存，权威状态一致 |
| `P3108-D11` | 未实现 UI 控件 | 明确拒绝／无副作用 |
| `P3108-D12` | unknown IPC | 明确拒绝／无副作用 |
| `P3108-D13` | IPC extra field | 明确拒绝／无副作用 |
| `P3108-D14` | 1280×1024 三态比较 | 与各自 Stitch 共享骨架与专属锚点成立 |
| `P3108-D15` | 原工作区三态与滚动 | 无裁切遮挡、操作可达 |
| `P3108-D16` | 700×760 三态与滚动 | 无裁切遮挡、操作可达 |
| `P3108-D17` | skip link + Tab 顺序 | 真正键盘焦点可见、顺序合理 |
| `P3108-D18` | Enter 激活 | 实际触发预期安全动作，不只验证可聚焦 |
| `P3108-D19` | reduced-motion | 实际减少运动且页面仍可用 |
| `P3108-D20` | path/link/hardlink/type/dangling/tamper 夹具 | 每一类在变更前拒绝，before/after 无副作用 |

## 判定规则

- 任一 P0/P1/P2、Unknown、Not Implemented，或任一矩阵行／动态动作没有独立 Evidence，结论不得为 Pass。
- 固定输入漂移、严格模型配置无法证明、正常 GUI app 控制连续两次不可用、或离线锁定工具不可用，才可为 Blocked；不能使用旧 Evidence 代替。
- 发现候选 P0/P1 或 ABF/L1 违反时记为 Rework，评审只报告且不修复候选。
