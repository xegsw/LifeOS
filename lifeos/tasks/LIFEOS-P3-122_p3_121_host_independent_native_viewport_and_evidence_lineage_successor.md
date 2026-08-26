# LIFEOS-P3-122｜P3-116 实际 UI 强制继承、主机无关原生视口与 Evidence 谱系后继

## 授权与安全语境

N/A — 不涉及双用途安全语义。LifeOS 是用户本人拥有并授权维护的本地项目。本任务拟直接继承 P3-116 当前只读高保真原型的实际 DOM、CSS、视觉 Token 与页面专属结构，并仅从 P3-121 当前只读候选承接最小 Runtime 接线；全部工作限于全新 task-local 工程、固定 `/private/tmp` 根和全新非敏感合成 DB。不访问 Pilot、真实个人数据、真实 DB／路径／文件、真实文本、网络、模型、云、第三方、凭据或外部目标。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-122`
- 任务名称：P3-116 实际 UI 强制继承、主机无关原生视口与 Evidence 谱系后继
- 优先级：P0
- 任务类型：受控本地 Tauri 视口验证＋Evidence lineage 能力包
- 是否为受控能力包：Yes
- 唯一用户结果：在不重新设计、不改变 Runtime 边界的前提下，把 P3-116 当前 `index.html`、`styles.css`、`app.js` 及其视觉／交互合同直接作为实际 Tauri UI 实现基线，只注入 P3-121 的最小三 IPC adapter；形成视觉上与 P3-116 同源、在目标逻辑视口与当前系统屏幕上自适应，并具备完整 Final Manifest 谱系的组合候选。
- 唯一风险边界：P3-116 当前原型与 P3-121 Runtime 均只读；P3-122 全新 task-local 工程；全新合成 SQLite；仅既有 `capture_record`、`get_today`、`runtime_status` 三项 IPC；离线单进程。
- 包内允许：从两个待冻结 positive allowlist 逐文件建立新候选；直接复用 P3-116 DOM/CSS/Token/page-specific components；以最小 adapter 将 P3-121 Runtime 回执注入 P3-116 已有 UI slot；task-local viewport／geometry attestation、离线 build/test、实际 Tauri App 三档逻辑视口回放、视觉回归、Evidence、Manifest、mutation 与精确清理。
- 包内禁止：以 P3-121 当前视觉替代 P3-116；重新设计、简化或概念性重写 P3-116 UI；改变布局 Token、IA、内容密度、交互、Runtime、IPC、Schema/API、capability 或产品语义；修改任何历史资产。
- 是否适用 P3 Engineering Fast Lane：No；涉及关键 Tauri/IPC、原生窗口 Evidence 与历史谱系，按 P0 高风险执行。
- 推荐执行 Agent：Codex，全新工程执行会话。
- 推荐理由：需要把原生窗口、WebView/DOM 几何、截图与历史 lineage 做机器可复核绑定，并避免旧执行上下文自证。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：仅作 PM 路由建议，不构成单一模型硬限制；用户已明确取消本任务的固定模型限制。实际执行仍须使用项目白名单模型并记录模型与推理强度。
- 允许降级模型：`gpt-5.6-luna`、`gpt-5.5`、`gpt-5.4`；实际推理强度可使用所选模型支持的任一兼容档位，并须记录，不得因此缩减 ABF。
- 禁止降级条件：所选模型无法完整读取 Frozen ABF、无法保持 P3-116 直接继承边界、无法复核 Tauri/IPC／SQLite／Evidence P0 时不得继续；不得使用项目白名单外模型。
- 必须升级条件：执行方在启动前质疑窗口判断所选配置无法可靠处理视觉差异、原生 geometry 或 lineage；此时升级到 `gpt-5.6-terra + xhigh`，而非缩减验收。
- 后备模型：`gpt-5.5`
- 是否需要后续独立评审：Yes；仅在本任务 PM Pass 且用户采纳后，另建全新隔离独立复评任务。本轮不创建。
- 是否允许修改工程文件：Yes；仅待确认的 P3-122 自有目录。
- 是否允许修改项目账本：No。
- 主责角色：Tauri/macOS Runtime、前端响应式、QA 与 Evidence。
- 协审角色：产品体验、技术架构、数据安全、无障碍与 Evidence QA。
- 必须通过关卡：启动前授权、只读候选继承、主机无关视口证明、实际屏幕适配、三 IPC 生命周期不退化、失败关闭、历史保全、完整 Final Manifest 与精确清理。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/2 / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-122_p3_121_host_independent_native_viewport_and_evidence_lineage_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-122-v1`
- ABF SHA-256：`2aacd353ad50e5d00c92f168e3f508f5e6488336ebcc8385aba56437e70b0a42`
- ABF 状态：Frozen
- 正式 Rework 上限：2；当前 0/2。
- 生效决策：`D-0492`；D-0490 原 Draft 与 D-0491 Draft Revision 1 已只读保全。
- 执行授权方式：用户将本最终任务卡绝对路径投递至全新合格 Codex 工程会话即启动 Frozen 范围；只在 PM 主会话查看路径或转述不启动。
- 投递前额外用户确认：**Completed**。用户已明确确认 `lifeos/engineering/LIFEOS-P3-122/`、`/private/tmp/lifeos-p3-122-native-evidence-v1`、全新合成 DB、P3-116 visual 与 P3-121 Runtime/Tauri 双只读输入、仅三项 IPC，并禁止 Pilot、真实 DB、真实路径、真实文本、网络和产品模型。授权 Evidence：`lifeos/reviews/LIFEOS-P3-122/pm_evidence/authorization/MANIFEST.md`，SHA-256 `d88495bd47e8df104952bd0c92e4ac498741eb5c75440f927c4e4359da805f8a`。

## 为什么是新任务

P3-121 已耗尽两轮正式 Rework，不能继续第三轮。旧 ABF 又把 `1280×1024` 写成必须由实际截图像素证明，混淆了“应用逻辑视口”和“宿主屏幕可显示像素”：当前 Mac 可见区域只能得到约 1036×768，继续要求用户调整系统显示缩放，会让系统迁就应用，也违反既定产品方向。

P3-122 重新冻结两个正确的完成定义：第一，视觉忠实必须来自 P3-116 实际 DOM/CSS/Token 的直接继承，而不是把 Icon Rail、卡片和 Global AI 等概念重新实现；第二，应用必须适应不同系统屏幕，目标逻辑尺寸由原生窗口 content bounds、WebView `innerWidth/innerHeight`、DOM layout、build/candidate hash 和实际状态共同证明。当前主机能显示的实际窗口仍用原生截图证明，但不把宿主物理屏幕上限伪装成应用失败或要求用户改变系统设置。

## 冻结前拟确认的唯一用户结果

1. P3-116 当前 `index.html`、`styles.css`、`app.js`、fixtures、visual/interaction contract 与页面专属组件是唯一正式视觉实现基线；P3-121 当前 UI 仅作失败历史和 Runtime adapter 定位参考，不能作为视觉 positive input。
2. P3-122 必须直接复用 P3-116 DOM 结构、CSS rules、视觉 Token、Icon Rail、卡片 chrome、字号／tracking／leading、留白、颜色、material、Global AI 空间关系与逐页密度；禁止用更短的通用组件体系概念性重写。
3. Runtime 只允许通过最小 adapter 更新 P3-116 已有 Today/Recent/runtime status/receipt slot；不得为了工程状态增加新 banner、pill、Dashboard 区块或压缩页面。
4. 目标逻辑视口为 1280×1024、1160×768、700×760；每档必须在实际 Tauri App 中由原生 content bounds、WebView/DOM 几何和状态布局联合证明。
5. 若宿主物理屏幕无法完整显示 1280×1024，允许截图像素与逻辑视口不同，但必须明确记录物理屏幕、窗口外框、content bounds、devicePixelRatio、WebView inner bounds、缩放状态和可见裁剪；不得用浏览器、CSS 缩放图或配置声明替代实际 App。
6. 不调整 macOS 显示缩放；不要求系统适配应用。应用必须在当前可用窗口下仍保持主操作、Global AI、导航和内容可达。
7. Final Manifest 必须分层覆盖：冻结授权、任务／ABF、P3-116 visual source allowlist、P3-121 Runtime source allowlist、全部历史关闭资产、P3-122 current candidate、runner、actual-App Evidence、mutation、current delivery、PM 输入和 cleanup；当前与历史不得混淆。

## 拟允许写入与环境

冻结后拟仅允许：

- `lifeos/engineering/LIFEOS-P3-122/`
- `lifeos/deliverables/LIFEOS-P3-122_p3_121_host_independent_native_viewport_and_evidence_lineage_successor.md`
- `lifeos/local_prechecks/` 中 P3-122 专属报告（如适用）
- `/private/tmp/lifeos-p3-122-native-evidence-v1`

编译 cache、合成 DB、app data、截图、geometry trace 和 disposable mutations 全部位于上述两根。结束时只可精确清理唯一临时根；不得使用宽前缀、glob、`find` 或不确定变量删除。

## 拟只读输入与双 positive allowlist

- `lifeos/tasks/LIFEOS-P3-122_visual_source_allowlist.md`：P3-116 current visual implementation 8/8，SHA-256 `381348fc60a6f8bf703bdd4b93ed430c1cc09a53230133d8c7817723635cb0ac`。
- `lifeos/tasks/LIFEOS-P3-122_runtime_source_allowlist.md`：P3-121 Runtime/Tauri source 65/65，SHA-256 `7deff71878556878b1059fb5a26f5e71b1d636c638d91c659a3fe65d49e00287`；P3-121 `ui/` 明确排除。
- `lifeos/tasks/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md`
- `lifeos/deliverables/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md`
- `lifeos/reviews/LIFEOS-P3-121_pm_final_review.md`
- P3-121 initial、Rework-1、Rework-2 Engineering/PM Evidence 与授权记录，仅作只读历史谱系。
- P3-116 设计合同与 P3-120 Runtime Final Manifest，只通过 P3-121 已固定 lineage 定向复核，不重新递归复制历史根。

## 最小启动包与定向补读

正式冻结后的专项会话必须读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与正式 Frozen ABF
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. P3-116 实际 visual source/contract、P3-121 最终 PM Review、最终交付物、Final Engineering Manifest、PM Final Manifest、P3-122 双 positive allowlist 与授权 Manifest

高风险定向补读：`PM_OPERATING_MODEL.md` 的 Tauri/IPC、P0、Evidence、会话隔离章节；`ROLE_MATRIX.md` 的 Codex 工程、技术架构、体验与 QA；`STAGE_GATES.md` 的关键原型独立评审与 Stage 3→4 区分；`TASK_REGISTRY.md` P3-116/P3-120/P3-121/P3-122；`DECISION_LOG.md` D-0483～D-0491；`RISK_LOG.md` R-0024/R-0025/R-0040/R-0051/R-0052。

## 实现与 Evidence 合同

1. 在任何工程动作前复算正式 Frozen ABF、授权、模型、positive allowlist、目录不存在性与固定输入；冲突即停止。
2. 只从双 positive allowlist 逐文件建立 P3-122 候选；visual 层来自 P3-116，Runtime/Tauri 层来自 P3-121；不得原地修改任一历史任务。
3. 必须保留 P3-116 DOM/CSS/Token/page-specific class 及其可见组合；只允许为 Tauri IPC 增加最小非视觉 adapter。若需要删改 P3-116 visual rule、改写 page DOM、合并专属组件或新增可见 Runtime chrome，立即停止回 PM。
4. 每个逻辑视口分别记录：requested logical size、native outer/content bounds、WebView inner bounds、DOM root/client/scroll bounds、devicePixelRatio、OS display bounds、candidate/build hash、页面／状态、截图／trace hash。
5. 证明应用适配，而非截图凑尺寸：无主操作裁切、无不可恢复横向溢出、Icon Rail／Global AI／标题可达；窗口受宿主限制时必须诚实披露，不可标成 exact screenshot。
6. 对 Today、Me、Contexts、Memory、Global AI、AI Workspace 分别生成“P3-116 source DOM/CSS rule → P3-122 actual DOM/computed style → actual-App screenshot”的逐页映射；不得只用人工观感或单张首屏判断。
7. 复跑三项 IPC 的最小合成生命周期和关键失败关闭，确认 adapter 与 geometry instrumentation 没有改变 Runtime、DB 或禁止能力边界。
8. Final Manifest verifier 必须在 pristine control 通过后，对遗漏当前授权、遗漏 PM Evidence、visual source drift、P3-121 UI 误入 visual layer、错 logical viewport、错 screenshot 语义、candidate drift、extra file 和历史 hash 漂移逐类 fail closed。
9. 提交 Final Manifest 后不得再修改 candidate；Manifest 不包含自身 hash，但必须覆盖其 verifier 输出、当前交付物、授权输入和 cleanup attestation。

## 非范围与停止条件

- 不调整系统显示缩放，不修改系统辅助功能设置，不要求用户更换屏幕。
- 不使用 Chrome/In-app Browser、HTTP/CDP/WebDriver、CSS 缩放图、静态配置或旧截图替代实际 Tauri App。
- 不访问、定位、stat、hash、打开、复制或清理 Pilot、真实用户目录、真实 DB／文件／文本。
- 不新增或改变 IPC、capability、Schema/API、架构、核心语义、P3-116 UI 设计、clear/export/权限/恢复、模型、网络、云／第三方、同步、多设备、L3 或外部用户。
- 不修改 P3-116/P3-120/P3-121 任何历史资产；不恢复已删除污染文件。
- 如主机无关 geometry attestation 必须新增产品 IPC、改变 capability 或引入系统权限，立即停止；不得在本任务内扩大范围。
- 不冻结产品／Runtime／架构，不关闭／重开风险，不恢复工程基线，不创建独立复评，不进入 Stage 4。

## 交付与治理边界

- 拟交付物：`lifeos/deliverables/LIFEOS-P3-122_p3_121_host_independent_native_viewport_and_evidence_lineage_successor.md`
- 拟工程／Evidence：`lifeos/engineering/LIFEOS-P3-122/`
- 专项只可报告 Candidate Ready / Not Pass / Blocked，并明确 P0/P1/P2/Unknown/Not Implemented。
- 本地模型预检可因关键 Tauri/IPC、原生几何和 Evidence 高风险最终判断跳过，但必须说明；不得替代 PM 判断。
- PM Pass 后仍须用户采纳；随后才可另建全新隔离独立复评任务与新 ABF。

## 当前启动状态

用户已完成精确 synthetic-only Tauri/IPC 执行确认。PM 已验证 P3-116 visual allowlist 8/8、P3-121 Runtime/Tauri allowlist 65/65，确认两根不存在并冻结 `ABF-P3-122-v1`。固定单一模型限制已取消，但项目模型白名单与实际配置记录要求继续有效。用户现在可将本任务卡绝对路径投递至全新合格 Codex 工程会话启动；专项必须先完成启动前质疑窗口，且不得越出 Frozen 边界。
