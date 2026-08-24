# LIFEOS-P3-111 Acceptance Basis Freeze｜三页 UI 与本地 Runtime 可真实使用 MVP 闭环

## 冻结信息

- 任务 ID：`LIFEOS-P3-111`
- ABF ID／版本：`ABF-P3-111-v1`
- 生效决策：D-0449
- 冻结时间：2026-08-24（Asia/Shanghai）
- 状态：Frozen
- 是否在专项开始前冻结：Yes

## 本轮唯一用户结果

- 单一结果：以新的三页 UI + 本地 runtime 候选，在用户重新确认的全新专用目录／新 DB／少量手工低敏感文本边界，完成记录、权威 Today 恢复、状态／来源辨识、刷新、导航和关闭重开的有限真实桌面闭环。
- 不冻结需求：本 ABF 不冻结产品长期需求、Schema/API、工程基线或 Stage 4。
- 非范围：导出、权限设置、备份／恢复、Alpha、AI／网络／云、Vault、同步、多设备、外部用户、风险关闭、冻结和阶段切换。

## 授权和能力边界

- 允许项目目录：`lifeos/engineering/LIFEOS-P3-111/` 与本任务交付物。
- 真实目录：仅 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2`。PM 冻结前只读核对目标不存在；祖先 `/Users`、`/Users/xxe`、`/Users/xxe/Documents` 均为真实目录而非链接。
- 真实数据：最多 3 条用户主动手工输入的低敏感短文本。Evidence 禁止记录原文／key／DB 内容；不得读取用户未在当前专项主动提供的文本。
- 允许入口：仅 `capture_record`、`get_today`、`runtime_status` 和 UI 导航／刷新／关闭重开。
- 严格只读：P3-102/103 retained 资产、P3-104、P3-106、P3-110 与全部历史任务／Review／Evidence。
- 禁止：Pilot-1、既有个人文件／DB、clear、export、权限／恢复写入口、新 IPC／Schema／依赖、网络、外部目标。
- 保留／清理：首轮保留专用目录和 `capture.sqlite`；任何清理、删除或 clear 必须取得新的逐次用户确认。
- 投递前额外用户确认：已完成。用户于 2026-08-24 逐项确认新目录、新 DB、最多 3 条低敏感文本、允许动作、禁止动作与 retained 规则。任务卡投递即启动；实际原文仍必须由用户在专项会话主动输入。

## 引用的 L1

L1-1 至 L1-10 全部适用，重点是数据主权、内容身份、生命周期完整、失败关闭、用户控制、审计可信、Evidence 诚实、历史保全、授权不漂移与可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---:|---|---|
| ABF-I-01 | 授权与隔离 | P0 | 新会话、正确模型、真实边界逐项确认、历史零写入 | Blocked/Rework |
| ABF-I-02 | 候选 provenance | P0 | P3-106 正向 allowlist；历史 Evidence／runner／target 复制 0 | Rework |
| ABF-I-03 | IPC／能力最小化 | P0 | 仅三 IPC；新 Schema/API/依赖/网络/capability 0 | New Task |
| ABF-I-04 | 真实路径边界 | P0 | 新专用目录／新 DB；祖先无链接；Pilot-1 与其他路径访问 0 | Blocked/Rework |
| ABF-I-05 | 内容隐私与身份 | P0 | 原文仅 app／DB；Evidence 无原文／key；来源、AI 关闭态可辨 | Rework |
| ABF-I-06 | commit-before-success | P0 | DB 成功提交后才显示 saved；审计与状态一致 | Rework |
| ABF-I-07 | 生命周期 | P0 | 首次、重复、冲突、失败、刷新、导航、关闭重开独立成立 | Rework |
| ABF-I-08 | 失败关闭 | P0 | 路径／类型／sidecar／tamper／注入失败在变更前停止 | Rework |
| ABF-I-09 | 三页体验 | P1 | 冻结骨架、三态、窄屏滚动、键盘、关键动作可达 | Rework |
| ABF-I-10 | Evidence 语义 | P0 | raw payload hash／bytes／missing／extra 重算；真实 disposable mutations 被同一 verifier 检出 | Rework |
| ABF-I-11 | 保留与清理 | P0 | 临时夹具 0；真实目录／DB 仅按确认保留，禁止自动删除 | Rework |
| ABF-I-12 | 风险／冻结／阶段 | P0 | R-0040/R-0052 Open；R-0051 原有限关闭；Not Frozen；Stage 4 未进入 | Rework |

## 冻结验收矩阵

| 行 | 独立动作 | 预期结果 | Evidence |
|---|---|---|---|
| M-001 | 授权、模型、新会话、用户边界确认 | 全匹配；确认前零工程动作 | authorization／boundary |
| M-002 | 启动前 UI 产品走查 | 仅映射本 ABF；无需求扩张 | product gap matrix |
| M-003 | allowlist copy 与 provenance | 禁项 0；hash 可追溯 | copy inventory／hash |
| M-004 | offline locked test/build/bundle | 全 0；网络 0 | logs／results |
| M-005 | 静态 IPC／capability／依赖 scan | 三 IPC；禁项 0 | static results |
| M-006 | 固定非敏感首次／重复／冲突／失败 | commit、幂等、冲突、原子失败正确 | before/after／audit |
| M-007 | 刷新／三态导航／关闭重开 | backend 权威状态恢复 | process／DB／UI |
| M-008 | 路径／类型／sidecar／tamper | 全部变更前拒绝 | negative matrix |
| M-009 | 响应式／键盘／身份／关闭态 | 关键动作可达且来源可辨 | dynamic closure |
| M-010 | 经确认的低敏感实际 capture | 不泄露原文；DB/audit/UI 一致 | redacted real-use evidence |
| M-011 | raw semantic verifier 与真实 mutation | baseline 0；六类真实副本 mutation 非零 | verifier／mutation |
| M-012 | Manifest、历史、临时清理、retained 保留 | hash 可复算；历史不变；临时 0；retained 未删 | Manifest／cleanup |

## Evidence 合同

- runner／测试、逐行结构化结果、before／after、raw logs／快照、source／history hash、payload Manifest、semantic verifier、真实 disposable mutation、复跑命令和精确清理全部必需。
- 真实原文、key、完整 DB、页面正文或可逆内容不得进入 Evidence。
- UI 动态动作必须逐行满足 `UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 的等价字段。

## 计数与 Pass 公式

- P0：授权、真实路径／数据、IPC、生命周期、失败关闭、Evidence、历史、风险／阶段。
- P1：三页体验、响应式、a11y、关键动作可达。
- P2：非阻断清洁项；Pass 仍要求 0。
- Unknown：有 Evidence 但关键事实不可复核。
- Not Implemented：任一矩阵行、子动作或必需 Evidence 缺失。
- Pass：I-01–I-12、M-001–M-012 与全部子动作通过；P0/P1/P2/Unknown/Not Implemented 全 0；临时残留 0；retained 资产仅按确认保留；Manifest 可独立复算。
- N/A：不得用于授权、真实使用、生命周期、失败关闭、动态体验、verifier、mutation、清理或历史保全。

## Rework 与退出

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅候选实现、runner、Evidence、UI 文案在本 ABF、目录和真实边界均不变时。
- 必须新任务：用户结果、ABF、真实目录／数据、IPC、Schema/API、依赖、领域语义、导出／权限／恢复、风险、冻结或阶段变化，或两轮用尽。
- Blocked：用户边界未确认、目标存在／祖先链接、正确模型或离线工具不可用、真实 app 无法启动、Evidence 无法脱敏。

## 候选与只读保全

- 候选输入：P3-106 rework-1 Manifest，当前 SHA-256 `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe`；最终 Frozen ABF 还须逐项记录 allowlist source hash。
- P3-110 PM Review 与 PM Evidence只读作为 verifier 反例输入；不得复制其 Pass 结论。
- 允许变化：仅 P3-111 工程／交付物／Evidence 和最终确认的全新真实目录／DB。

## 启动前质疑窗口

- 执行方必须在任何工程动作前核对本 ABF、任务卡、目标不存在事实、祖先目录类型和全部真实使用边界；有歧义立即停止。
- PM 处理：用户边界已逐项确认，ABF 冻结为 `ABF-P3-111-v1`。
- 最终冻结版本：`ABF-P3-111-v1`。
- 专项会话开始后不得实质修改 Frozen ABF；如需修改，关闭并新建任务。
