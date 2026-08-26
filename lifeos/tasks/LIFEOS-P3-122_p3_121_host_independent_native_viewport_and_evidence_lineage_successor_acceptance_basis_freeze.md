# LIFEOS-P3-122 Acceptance Basis Freeze｜P3-116 实际 UI 强制继承、主机无关原生视口与 Evidence 谱系后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-122`
- ABF ID／版本：`ABF-P3-122-v1`
- 生效决策：`D-0492`；D-0490 原 Draft 与 D-0491 Draft Revision 1 均已只读保全
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes；尚未投递
- ABF 文件 SHA-256：由 PM 冻结后记录在最终任务卡与 D-0492；本文件不使用自指 hash。
- 正式 Rework：0/2

## 本轮唯一用户结果

在全新 P3-122 task-local 工程中，直接以 P3-116 当前 `index.html`、`styles.css`、`app.js`、视觉 Token、页面专属 DOM/class 与 visual/interaction contract 作为强制视觉实现基线，只从 P3-121 承接 Tauri shell、三 IPC Runtime 与最小 adapter；不得概念性重写或以 P3-121 当前 UI 为视觉基线。候选还必须以原生窗口 content bounds、WebView/DOM 逻辑几何、实际 App 状态和当前主机截图联合证明应用适配三档逻辑视口，并以完整、非自指、可变异验证的 Final Manifest 关闭谱系。

本 ABF 不要求用户调整系统显示缩放，也不要求物理屏幕像素等于逻辑内容尺寸；不得降低实际 App、响应式、Evidence 诚实、历史保全或失败关闭标准。

## 待确认的授权和能力边界

- 拟允许目录：`lifeos/engineering/LIFEOS-P3-122/`、指定 P3-122 交付物、P3-122 本地预检报告、`/private/tmp/lifeos-p3-122-native-evidence-v1`。
- 拟允许数据：全新固定非敏感 synthetic DB 与 P3-121 已使用的固定合成 capture；不得接受真实输入。
- 拟允许入口／接口：本地 Tauri `.app`；仅 `capture_record`、`get_today`、`runtime_status`；不新增产品 IPC。
- 拟允许工具：本地离线 Rust/Cargo/Tauri、SQLite、task-local native geometry/DOM/computed-style attestation、原生窗口截图、代码测试与 disposable verifier mutations。
- 严格只读：P3-116/P3-120/P3-121 全部任务、候选、Review、Evidence、授权与账本；Pilot 和历史真实使用资产。
- 禁止：真实 DB／路径／文本、系统显示缩放调整、clear/export/权限/恢复、Vault/文件导入、模型、网络、云／第三方、同步、多设备、L3、外部用户、新 IPC、新 Schema/API、风险／冻结／阶段变化。
- 模型路由：用户取消固定单一模型限制；允许使用 `gpt-5.6-terra`、`gpt-5.6-luna`、`gpt-5.5` 或 `gpt-5.4`，并使用相容推理强度、记录实际配置。不得使用项目白名单外模型；模型变化不改变本 ABF。
- 投递前额外用户确认：**Completed**。用户已确认两个固定根、全新合成 DB、P3-116 visual 与 P3-121 Runtime/Tauri 双只读输入、仅三项 IPC，以及禁止 Pilot／真实 DB／路径／文本／网络／产品模型。授权 Evidence：`lifeos/reviews/LIFEOS-P3-122/pm_evidence/authorization/MANIFEST.md`。

## 冻结输入

PM 已在冻结前复算下列输入；专项仍须在任何工程动作前再次复算：

| 输入 | Frozen SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-122_visual_source_allowlist.md`（8/8） | `381348fc60a6f8bf703bdd4b93ed430c1cc09a53230133d8c7817723635cb0ac` |
| `lifeos/tasks/LIFEOS-P3-122_runtime_source_allowlist.md`（65/65；排除 P3-121 current UI） | `7deff71878556878b1059fb5a26f5e71b1d636c638d91c659a3fe65d49e00287` |
| `lifeos/reviews/LIFEOS-P3-122/pm_evidence/draft-revision-1/MANIFEST.md` | `15c2b8124e824d0eab80c6fca2ebbfef0eaf6a2072009fe05a7e8d7fc7be1c88` |
| `lifeos/reviews/LIFEOS-P3-116_pm_review.md` | `09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa` |
| `lifeos/deliverables/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md` | `60a08c50d9557fa3adc4c0402fd72279a7e7faa4aed58cc14fa6896073d4d2f3` |
| `lifeos/reviews/LIFEOS-P3-121_pm_final_review.md` | `be8cbbc1009cbf38a10e7dd2c346aa5e74107b8fc1ad4eeb8ab9416bdcd3d05e` |
| `lifeos/engineering/LIFEOS-P3-121/evidence/rework-2/manifest/final-lineage-manifest.json` | `efd27d96b9831edf60fc6bbe46beebf841ac77d06f60c085da4b615ed63c4516` |
| `lifeos/reviews/LIFEOS-P3-121/pm_evidence/rework-2/FINAL_PM_MANIFEST.md` | `bc1a62b80fcccb1a22958411adadbd14443e78959959394bc9fc5ffc78489652` |
| `lifeos/reviews/LIFEOS-P3-121/pm_evidence/final-adoption/MANIFEST.md` | `ba432241235a090ec471f61dc46212b840d49b8c3b411f7bd0a44a90053370c6` |
| `lifeos/reviews/LIFEOS-P3-122/pm_evidence/authorization/MANIFEST.md` | `d88495bd47e8df104952bd0c92e4ac498741eb5c75440f927c4e4359da805f8a` |

P3-116 visual allowlist 之外的旧空白／污染 screenshot、AX、Evidence 不属于 visual positive source。P3-121 current `ui/` 不属于 visual positive source；其 build cache、历史临时 DB、截图、runner 或 Evidence 仅作为只读 lineage 输入。

## 引用的 L1 长期原则

- L1-1 数据主权：仅新 P3-122 根、唯一临时根与合成 DB。
- L1-3 生命周期完整：最小三 IPC 生命周期与视口 instrumentation 前后不退化。
- L1-4 失败关闭：geometry、窗口、DB、path/type 或 Manifest 失败不得留下伪成功或持久化。
- L1-6 审计可信：逻辑尺寸、物理屏幕、窗口外框、content bounds、WebView/DOM、截图和状态语义必须一致。
- L1-7 Evidence 诚实：不得把截图像素、配置或旧 Evidence 冒充逻辑内容尺寸。
- L1-8 历史保全：P3-121 及上游全部只读。
- L1-9 授权不漂移：不继承 P3-121 的执行授权；P3-122 必须重新确认。
- L1-10 可复核性：固定 visual/Runtime source、candidate/build、computed style、geometry trace、state、screenshot、Manifest 和 mutation可重跑。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 新任务授权、模型、输入和目录不漂移 | P0 | 正式 Frozen 输入和新确认全部匹配后才创建 | 动作前 Blocked |
| ABF-I-02 | P3-116 actual visual source 强制直接继承 | P0 | DOM/CSS/Token/page-specific components 逐文件／逐规则保留；无概念性重写 | Not Pass |
| ABF-I-03 | 应用适配系统，而非系统适配应用 | P1 | 不改显示缩放；当前屏幕可用，主操作和 Global AI 可达 | Not Pass |
| ABF-I-04 | 三档逻辑内容尺寸可独立证明 | P1 | native content + WebView/DOM bounds 共同达到目标；宿主限制诚实披露 | Not Pass/Unknown |
| ABF-I-05 | 截图与逻辑视口不混淆 | P0 | 物理、outer、content、inner、DPR、裁剪和 screenshot 分栏记录 | Not Pass |
| ABF-I-06 | P3-116 视觉、IA、Token、密度与交互不再设计 | P1 | 六个核心页面／展开态的 DOM、computed style、空间关系与 actual screenshot 同源 | Not Pass |
| ABF-I-07 | P3-121 仅提供三 IPC synthetic Runtime | P0 | visual layer 不取自 P3-121 UI；Runtime inventory 精确且生命周期无退化 | Not Pass |
| ABF-I-08 | 失败先于变更、禁止能力关闭 | P0 | DB/sentinel/UI 不变；无 network/model/new IPC | Not Pass |
| ABF-I-09 | Evidence 与 build/state/geometry 真实绑定 | P0 | 逐档、逐页结果及 screenshot/trace hash 可复核 | Not Pass |
| ABF-I-10 | Final Manifest 谱系完整且 fail closed | P0 | current/history/auth/PM/delivery/cleanup 全覆盖，mutation 均拒绝 | Not Pass |
| ABF-I-11 | 精确清理 | P0 | 固定临时根 absent；无越界删除 | Not Pass |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | 两根不存在 | 复算授权、ABF、模型、allowlist | 全匹配后才创建 | P122-M001 | fixed inputs + authorization |
| ABF-M-002 | source | dual positive allowlists | P3-116 visual＋P3-121 Runtime 分层逐文件复制 | source 分层精确，history 不变 | P122-M002 | dual source/candidate inventory |
| ABF-M-003 | visual inheritance | fresh candidate | 验证 DOM/class/CSS rule/Token/page component 来源 | P3-116 直接继承；P3-121 UI 未替代 | P122-M003 | source map + computed style |
| ABF-M-004 | build | fresh candidate | locked offline test/build/bundle | exit 0，无网／外部写 | P122-M004 | logs + inventory |
| ABF-M-005 | visual pages | actual Tauri app | Today/Me/Contexts/Memory/Global AI/Workspace 逐页比较 | P3-116 layout、type、color、spacing、material、density 成立 | P122-M005 | page matrix + screenshots |
| ABF-M-006 | geometry | actual Tauri app | 记录 OS display、outer/content、WebView/DOM、DPR | 字段同时存在且语义一致 | P122-M006 | native + renderer traces |
| ABF-M-007 | 1280×1024 logical | target requested | 设置并复核逻辑 content viewport | 逻辑目标成立；宿主可见限制单独披露 | P122-M007 | state + geometry + screenshot |
| ABF-M-008 | 1160×768 logical | target requested | 同上 | 逻辑目标成立，当前屏幕可用 | P122-M008 | state + geometry + screenshot |
| ABF-M-009 | 700×760 logical | target requested | 同上 | 逻辑目标成立，窄屏无关键裁切 | P122-M009 | state + geometry + screenshot |
| ABF-M-010 | host available sizes | current display | 最大化、常用及窄窗口抽样 | 应用适配；主操作／导航／Global AI 可达 | P122-M010 | responsive trace |
| ABF-M-011 | runtime adapter | fresh synthetic DB | status、capture、today、repeat、refresh、reopen | 三 IPC 生命周期无退化，视觉 chrome 未新增 | P122-M011 | IPC/DB/UI trace |
| ABF-M-012 | failure/prohibited | pristine disposable | geometry/path/type/DB failure及禁能扫描 | 失败先于变更；禁止能力关闭 | P122-M012 | before-after + negatives |
| ABF-M-013 | evidence integrity | completed states | 绑定 visual source/candidate/build/state/geometry/screenshot | 无重写、错绑、复用冒充或旧图替代 | P122-M013 | verifier + mutations |
| ABF-M-014 | final lineage | completed/failed | 验证完整分层 Manifest | 无 visual/Runtime source、授权、PM、delivery 遗漏 | P122-M014 | final manifest + mutations |
| ABF-M-015 | cleanup | app closed | 精确清理唯一临时根并复算 history | root absent，history unchanged | P122-M015 | cleanup + final hashes |

## Evidence 合同

- 每个核心页面必须保存 P3-116 source DOM/class/CSS rule/Token 到 P3-122 actual DOM/computed style/screenshot 的逐项映射；不得用“整体相似”或结构扫描替代。
- 每个 viewport 必须独立保存 structured result，字段至少包括 requested logical size、native outer/content bounds、WebView inner bounds、DOM client/scroll bounds、DPR、display bounds、visual/Runtime source hash、candidate/build hash、page/state、screenshot/trace path/hash、结论。
- actual screenshot 证明当前主机上的可见真实 App；geometry trace 证明逻辑内容尺寸。两者不得相互冒充，也不得要求 screenshot 像素必须等于逻辑 content bounds。
- Runtime 只需证明继承未退化，但仍必须是实际 renderer→IPC→DB→UI；源码或 unit test 不单独构成 Pass。
- Final Manifest 非自指并分层覆盖 authorization、task/ABF、P3-116 visual source、P3-121 Runtime source、history、current candidate、tools/tests、results/logs/screenshots、current delivery、PM inputs 与 cleanup。
- pristine control 先 PASS；P3-116 CSS/DOM drift、P3-121 UI 误作 visual input、遗漏授权、遗漏 PM Evidence、错 logical viewport、错 screenshot 语义、candidate mismatch、extra file、history drift 任一 mutation 必须 fail closed。

## 计数与 Pass 公式

- P0：P3-116 actual UI 未直接继承却声称继承、P3-121 UI 误作视觉基线、越界数据／目录／能力、历史修改、Evidence 语义伪造、逻辑/物理尺寸混淆、谱系遗漏、失败后变更或错误清理。
- P1：三档逻辑视口或当前主机适配未满足、关键 UI／交互退化。
- P2：不影响冻结结果的轻微表现差异；本轮 Pass 仍要求 0。
- Unknown：任一 geometry、viewport、Runtime、lineage、history 或 cleanup 无法独立复核。
- Not Implemented：任一不变量、矩阵行、runner、Evidence、mutation 或清理缺失。
- Pass 公式：I-01～I-11、M-001～M-015 全部 PASS；P0/P1/P2/Unknown/Not Implemented 全零；无静默 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-122 自有 P3-116 direct-inheritance integration、Runtime adapter、candidate instrumentation、runner、Evidence、Manifest；ABF、用户结果、目录、数据、P3-116 visual source、三 IPC、Schema/API 与风险不变。
- 必须新建任务：改变 UI／Runtime、目录、数据、IPC/capability、Schema/API、架构、真实路径/DB、系统权限、模型、网络、风险／冻结／阶段；ABF 实质修改；两轮正式 Rework 未通过；历史污染不可恢复。
- Blocked：不新增 product IPC/capability 就无法取得原生 content geometry，或离线工具链／actual Tauri App 无法启动；不得退回浏览器／静态配置替代。

## 启动前质疑窗口

- 执行方是否提出歧义：N/A；尚未投递。
- PM 当前处理：用户已确认新的两根、全新合成 DB、双 source、仅三 IPC 和严格禁止边界。PM 已验证 visual allowlist 8/8、Runtime allowlist 65/65，确认两根不存在，并冻结本文件。
- 最终冻结版本：`ABF-P3-122-v1`。
- 专项会话开始后不得实质修改正式 ABF；如需修改，关闭 P3-122 并新建任务。
