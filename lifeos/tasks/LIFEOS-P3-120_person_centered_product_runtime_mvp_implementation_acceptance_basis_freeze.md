# LIFEOS-P3-120 Acceptance Basis Freeze｜以人为主体的产品 Runtime MVP 实现

## 冻结信息

- 任务 ID：`LIFEOS-P3-120`
- ABF ID／版本：`ABF-P3-120-v1`
- 生效决策：`D-0478`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes；尚未投递
- 正式 Rework：0/2

## 本轮唯一用户结果

在全新 task-local 工程和全新合成 SQLite 中，将当前 Person-centered 产品 UI 候选与既有三项窄 Tauri IPC 组合成一个实际可启动的本地 MVP：可导航全部核心页面；以固定 synthetic 短文本完成 capture→Today→刷新→关闭重开；明确区分 runtime 持久化数据、read-only synthetic 产品 fixture、AI 候选与用户确认内容。

本轮不冻结产品需求、IA、视觉、架构、Schema/API、IPC、工程基线、风险或阶段。不证明真实个人使用、模型智能、生产可靠性或 Stage 4 准入。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-120/`、指定 P3-120 交付物、P3-120 本地预检报告、`/private/tmp/lifeos-p3-120-runtime-mvp-v1`。
- 允许数据：固定合成文本 `P3-120 synthetic capture one`、`P3-120 synthetic capture two`，以及固定 Person/Work/Health/Context/Memory fixtures；不得接受真实输入。
- 允许入口／接口：本地 Tauri `.app`；仅 `capture_record`、`get_today`、`runtime_status` 三项 IPC；无 renderer direct DB/file/shell/network。
- 允许工具／环境：本地离线 Rust/Cargo/Tauri 工具链、SQLite task-local DB、代码与单元／集成／actual-app runner；辅助 screenshot 不作为独立功能证明。
- 严格只读：P3-104、P3-111、P3-114、P3-116、P3-119 及其任务、ABF、候选、Review、Evidence；项目账本；Pilot 与历史真实使用资产。
- 禁止能力：真实 DB／路径／文本、clear/export/权限/恢复、Vault/文件导入、模型、网络、云／第三方、同步、多设备、L3、外部用户、通知中心、新 IPC、新 Schema/API、风险／冻结／阶段变化。
- 投递前额外用户确认：Completed。用户已明确确认仅在 `lifeos/engineering/LIFEOS-P3-120/` 与 `/private/tmp/lifeos-p3-120-runtime-mvp-v1` 使用全新合成 DB 和既有三项 Tauri/IPC；不访问 Pilot、真实 DB、真实路径、网络或模型。

## 冻结输入

| 输入 | 当前 SHA-256 |
|---|---|
| `lifeos/reviews/LIFEOS-P3-104_pm_review.md` | `8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795` |
| `lifeos/reviews/LIFEOS-P3-111_pm_review.md` | `e8fc44bcd79b7a2d6fb0ec29f3ff23b22ece0c08fdc260236fb8113f60bb0c10` |
| `lifeos/reviews/LIFEOS-P3-114_pm_review.md` | `72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78` |
| `lifeos/reviews/LIFEOS-P3-119_pm_review.md` | `b1b607642588df2c0f2fc2b3a09d28bb5a9b03e3b1a479c893c8cb8429b26ddb` |
| `lifeos/architecture/LifeOS高保真原型IA-V1.0.md` | `adcc9daf3b8f0fcf27a13176eabb1581c6079d47b48a26ee88cbaba209704243` |
| `lifeos/architecture/LifeOS架构基线V1.0.md` | `2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32` |
| `lifeos/tasks/LIFEOS-P3-120_source_allowlist.md`（P3-111 candidate 72/72 正向源文件） | `4965260513f63f37dd1d5eba969440a30863a9d5574be0ca06464edccef25e94` |
| `lifeos/prototypes/LIFEOS-P3-116/index.html` | `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b` |
| `lifeos/prototypes/LIFEOS-P3-116/app.js` | `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f` |
| `lifeos/prototypes/LIFEOS-P3-116/styles.css` | `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3` |
| `lifeos/prototypes/LIFEOS-P3-116/fixtures.js` | `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93` |
| `lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md` | `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393` |
| `lifeos/prototypes/LIFEOS-P3-116/state_machine.json` | `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc` |
| `lifeos/prototypes/LIFEOS-P3-116/visual_contract.json` | `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49` |

冻结时 PM 已独立复算上述 14 项输入；P3-120 source allowlist 内 72/72 文件的 SHA-256 与 bytes 均匹配。专项仍须在创建工程或临时根前重新复算，并写入 machine-readable `fixed-inputs.json`。

## 引用的 L1 长期原则

- L1-1 数据主权：只允许新 P3-120 工程、唯一临时根和合成 DB；Pilot/真实路径绝对禁止。
- L1-2 内容身份：持久化 capture、read-only fixture、AI Observation/Inference/candidate 与用户确认对象不得混淆。
- L1-3 生命周期完整：首次、重复、刷新、关闭重开和失败后的 DB/UI 语义一致。
- L1-4 失败关闭：IPC/DB/path/type/render 任一失败不得显示成功或留下半提交。
- L1-5 用户控制：无真实动作；合成 capture 仍需显式提交，不静默生成 Context/Action/Decision。
- L1-6 审计可信：command、input identity、DB before/after、UI result 与时间顺序一致。
- L1-7 Evidence 诚实：actual-app launch、IPC、DB 与 UI 状态分别由实际测试证明；辅助 screenshot 不替代功能结果。
- L1-8 历史保全：全部输入只读；只 positive allowlist 复制代码。
- L1-9 授权不漂移：不得继承 P3-111 Pilot、P3-116 browser、P3-119 GUI 注入或其他任务授权。
- L1-10 可复核性：固定 candidate hash、合成 fixture、runner、逐行结果与 Manifest 可重复。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权、模型、输入与 positive allowlist 不漂移 | P0 | 全部完整 hash、目录、会话、模型匹配 | 动作前 Blocked/Not Pass |
| ABF-I-02 | 仅三项 IPC；renderer 无直接敏感能力 | P0 | Rust/JS/capability inventory 精确匹配 | Not Pass |
| ABF-I-03 | 全新合成 DB 与 task-local path/type 边界 | P0 | 路径规范化、祖先链接、DB/sidecar 类型负测全通过 | Not Pass |
| ABF-I-04 | capture→Today 持久化闭环 | P0 | 实际 IPC、DB 与 UI 三层结果一致 | Not Pass |
| ABF-I-05 | 刷新与关闭重开生命周期 | P1 | 两种动作后记录与身份不漂移 | Not Pass |
| ABF-I-06 | 失败先于变更且 UI 不伪成功 | P0 | before/after DB hash/row count、哨兵与 UI 状态不变 | Not Pass |
| ABF-I-07 | Person-centered IA 与内容身份 | P1 | 核心页面/展开态可达；fixture/runtime/AI身份可见 | Not Pass |
| ABF-I-08 | Global AI/Workspace 保持无模型、无执行 | P0 | 明确 disabled/offline；无 network/model/tool calls | Not Pass |
| ABF-I-09 | 禁止能力关闭态 | P0 | clear/export/permissions/recovery/file/network/new IPC 均不存在或拒绝 | Not Pass |
| ABF-I-10 | 历史保全、Evidence 和精确清理 | P0 | 输入 hash 不变；Manifest 完整；唯一临时根不存在 | Not Pass |

## 冻结验收矩阵

每行必须独立生成结构化结果；总测试数、静态扫描或截图不得批量替代。

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | 工程/根不存在 | 复算完整输入、模型、授权、source inventory | 全匹配后才创建 | all history | P120-M001 | fixed inputs + inventory |
| ABF-M-002 | build | positive copy | locked offline test/build/bundle | exit 0；无外部写/网 | history/Pilot | P120-M002 | build logs + lock inventory |
| ABF-M-003 | static boundary | candidate | 扫描 IPC/capability/renderer/URL | 仅三 IPC；无 direct capability/network | candidate semantics | P120-M003 | static results |
| ABF-M-004 | actual app | 空合成 DB | 启动 `.app`，导航所有核心页/态 | 全部可达；无空白/崩溃 | DB empty | P120-M004 | app log + state trace + support images |
| ABF-M-005 | runtime status | app running | 调用 `runtime_status` | local/offline/synthetic/allowed commands 准确 | DB | P120-M005 | IPC result + UI state |
| ABF-M-006 | capture | empty DB | 显式提交 synthetic one | 一次成功；原文身份保存；Today 可见 | fixture content | P120-M006 | IPC + DB + UI before/after |
| ABF-M-007 | repeat | one row | 重复同一提交 | 按冻结幂等合同处理，不双重伪成功 | first row | P120-M007 | repeat result + DB diff |
| ABF-M-008 | second capture | one row | 提交 synthetic two | 第二条独立保存，顺序/身份正确 | first row | P120-M008 | IPC + DB + UI |
| ABF-M-009 | refresh | two rows | UI refresh | 两条仍可见且无重复/身份漂移 | DB hash/rows | P120-M009 | lifecycle trace |
| ABF-M-010 | reopen | two rows | 关闭 app，重开同一合成 DB | 两条仍可见；status 正确 | DB | P120-M010 | process + IPC + UI trace |
| ABF-M-011 | path/type negatives | pristine copies | escape、祖先链接、DB/sidecar link/dir/special、missing parent | 变更前拒绝；哨兵/DB/UI 不变 | canonical copy | P120-M011 | mutation results |
| ABF-M-012 | IPC/DB failure | pristine copies | invalid input、DB open/write/read failure | fail closed；无成功态/半提交 | DB/sentinel | P120-M012 | before/after + error results |
| ABF-M-013 | product identity | running app | 检查 Today/Me/Contexts/Memory/detail/AI states | runtime、fixture、AI candidate、confirmed 身份清晰 | data | P120-M013 | state contract results |
| ABF-M-014 | prohibited capability | candidate + app | 尝试/扫描 clear/export/permission/recovery/file/network/model/new IPC | 不存在或明确拒绝 | DB/files/network | P120-M014 | static + runtime negatives |
| ABF-M-015 | final | completed/failed | 复算 history/candidate/Evidence，关闭 app，精确清理 | Manifest 成立；history unchanged；root absent | all history | P120-M015 | final results + cleanup |

## Evidence 合同

- runner／测试：source inventory、static boundary、Rust/unit/integration、actual-app replay、path/type mutations、failure mutations、Manifest、cleanup。
- 逐行结果：15 行分别记录操作、输入、实际结果、before/after、Evidence path、SHA-256 与结论。
- actual app：保留 launch/stop/reopen、IPC request/result、state trace；辅助 screenshots 可证明页面非空与身份表达，但不证明数据库语义。
- DB：只记录合成 schema/row identity/count/hash 和受控查询结果；不得出现真实路径或内容。
- Manifest：非自指，覆盖 candidate、tests、tools、results、logs、support images、source inventory、cleanup 与交付物引用。
- 复跑：从无 P3-120 工程副本／空唯一临时根开始；使用 task-local caches；结束精确删根。

## 计数与 Pass 公式

- P0：越界数据/目录/能力、错误持久化、失败后变更或成功态、renderer 直接能力、新 IPC/网络/模型、身份混淆、历史/Evidence 漂移或错误清理。
- P1：核心页面/态不可达、刷新/重启失败、Person-centered IA 或响应式可用性未达到本轮完成定义。
- P2：不影响结果的文案/Evidence 可读性；本轮 Pass 仍要求 0。
- Unknown：任一 IPC、DB、路径、生命周期、页面状态、source/candidate lineage 或 cleanup 无法独立复核。
- Not Implemented：任一矩阵行、runner、结果或 Evidence 缺失。
- Pass 公式：I-01～I-10 与 M-001～M-015 全部 PASS；P0/P1/P2/Unknown/Not Implemented 全零；无静默 N/A。
- 允许 N/A：只有明确不适用于当前 OS 的链接／special-file 子类型，且同风险至少有一条实际等价负测；必须逐行说明。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-120 candidate、测试、Evidence、Manifest 或同一 UI/runtime 适配；ABF、目录、数据、三 IPC、Schema/API、风险不变。
- 必须新建任务：改变用户结果、目录、数据类型、IPC/capability、Schema/API、架构、真实路径/DB、模型、网络、clear/export/permissions/recovery、风险/冻结/阶段；ABF 实质修改；两轮正式 Rework 未通过；Evidence/历史污染不可恢复。
- Blocked：冻结工具链离线不可用、系统无法启动 actual Tauri app，且不改变 ABF 无法安全恢复；必须在任何替代入口前停止。

## 候选基线与只读保全

- P3-120 尚无候选；冻结时工程根与唯一临时根均不存在，专项从空目录建立。
- 只读输入以上述 14 项冻结输入及 72/72 source allowlist 为准。
- 允许变化仅限 P3-120 工程、交付物、P3-120 local precheck 和唯一临时根。
- P3-111 的 Pilot/DB/真实内容、P3-116/P3-119 Evidence 和全部历史 Review 不得复制或改写。

## 启动前质疑窗口

- 用户确认：已完成 synthetic-only Tauri/IPC 执行边界确认。
- PM 冻结动作：已复算全部 14 项冻结输入和 72/72 source allowlist；已核对工程根与唯一临时根均不存在；本版本为最终 Frozen v1。
- 执行方启动后不得修改 ABF；任何歧义在创建 P3-120 工程或临时根前停止。
