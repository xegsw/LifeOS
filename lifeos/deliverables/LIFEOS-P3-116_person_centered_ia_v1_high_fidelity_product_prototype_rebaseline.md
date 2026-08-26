# LIFEOS-P3-116｜Person-centered IA V1.0 与高保真产品原型重基线

## 当前状态与执行边界

**执行侧结论：Candidate Ready，等待 PM 验收；不是 PM Pass、用户采纳、冻结、风险结论或 Stage 4 准入。** 本包仅交付原型、fixture、合同和 Evidence；无 runtime。

- 执行授权：用户于 2026-08-25（Asia/Shanghai）交付任务卡绝对路径 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-116_person_centered_ia_v1_high_fidelity_product_prototype_rebaseline.md`；本会话为全新 Codex 产品设计／前端原型会话，与 P3-113、P3-114、P3-115 及 PM 主会话隔离。
- 实际路由：`gpt-5.6-terra` + `xhigh`（由宿主请求元数据读取）；未降级、未切换后备模型。任务卡的首选、禁止降级条件与当前配置一致。
- ABF：`ABF-P3-116-v1`，Frozen hash `220d3d73ef7a54f6be689bf2cdb05fb85c25d8118562fbb4788ef6a48a4d63cf`；所有工程动作前已核对。七项固定输入均由 `tests/verify_static.py` 重算并写入 `evidence/fixed_inputs.json`，结果为 PASS。
- 标准质疑窗口：已关闭。唯一需要调和的表述是“Project 是 Core Domain object”与“Project 是一种 Context 类型”；本候选采用分层解释：Project 的领域身份仍是 Core Domain object，在 person-first 产品 IA 中以 Context 类型被用户浏览和恢复。两层不互相覆盖，无需新增 PM 产品决策。
- 写入边界：只写入 P3-116 原型、本报告和本地预检目录；历史候选、IA／架构输入、工程、账本、风险与冻结资产均未修改。

## 继承原则与本轮调和

本候选把 Person 置为一级主体，而非把用户组织成项目、任务、领域卡或账户 Profile。Today 先分配一个人整体的注意力；Me 呈现可纠正的当下理解；Contexts 承接正在经历、推进、持续关注或已结束的事；Memory 是可回溯的长期记忆与 Evidence Browser。Settings 仅为底部弱辅助入口。

Domain 仍是长期生活视角，但 MVP 1.0 只对 Work 与 Health/Fitness 展示深度智能。其他人生数据可被承接、记录和回看，却不被伪装成可推断、可主动策略的深度领域。尝试启用第三领域时，界面明确展示数据、价值、反馈与安全四项 Gate 均未满足，并保持关闭。Health 仅出现为保守、可停止、非诊断的合成观察；没有真实健康建议。

Context 不是 Kanban 或 Domain 分栏：它有 Active、Watching、Past 关系，覆盖 Project、Period/Program、Goal-related、Life Event、Observed Context 等类型。系统只能提出 Context 候选，名称、范围、状态和创建都等待用户确认。Memory 保留七类身份：用户原文、确认事实、AI Observation、AI Inference、Decision、Derivation、External Source；每一类的确认状态、适用范围、来源和可回溯性都独立显示。External Source 不可达时会披露“来源未读取／仅作为指针”，不会被当作已读取内容或可靠建议的依据。

Global AI 是全局但上下文可见的交互层，不是独立聊天产品。它展示 Person／Page／Selection Context，可临时移除 Health Context；移除会改变本轮候选可使用的范围，但不会改写任何原始对象。复杂 Work + Health 问题渐进展开为 AI Workspace：中区是 Conversation + Work，右侧是 Context Inspector；Future Agent Task 只作诚实占位，明确当前没有 Agent、工具或真实执行。

## 相比 P3-115 的实质变化

| 维度 | P3-115 历史候选 | P3-116 当前候选 | 本轮处置 |
|---|---|---|---|
| 入口重心 | 项目／工作优先的 Today 参考 | Person-first Today、Me、Contexts、Memory | 只在新目录实现；历史候选只读保全 |
| Today | 历史 ABF 下的建议卡组织 | 正常／合法空／证据不足三态，Focus 为 0–1 | noticed 与已确认安排分离，Why 可回溯 |
| 主导航 | 旧原型参考 | 窄 Icon Rail；默认只显示图标与 hover 提示 | 禁止宽 Sidebar、通知／铃铛和账户 Profile |
| Project 语义 | 核心领域对象 | Core Domain 身份不变，同时是 Context 类型 | 已写入 `ia_reconciliation.md` |
| AI 形态 | 历史原型交互 | Global AI + 可渐进展开的 AI Workspace | 明示使用范围、临时移除与无真实执行 |
| Evidence | 旧候选证据 | 7 类 Memory 身份与 Derivation→Evidence→Source 链 | 断链／不足 fail-open 文案被禁止 |

因此，P3-115 的 PM Pass 仍只是其原 Frozen ABF 下的历史事实；P3-116 不回写、不否定或替代它，也未冻结任何新资产。

## 原型交付与核心交互

原型根目录为 `lifeos/prototypes/LIFEOS-P3-116/`，入口为 `index.html`，无构建依赖、远程字体、图标、图片、网络请求、Storage、真实模型、数据库、文件接口、Tauri 或 IPC。`fixtures.js` 只含固定非敏感合成内容；刷新、关闭或重新打开都会丢弃临时演示状态。

已编码并动态覆盖的视图／状态包括：Global Shell；Today（正常、合法空、证据不足与 Focus Why）；Me（Current Self、关注、Domain 与可纠正理解）；Contexts（三组状态、候选创建确认）；Context Detail（现在、Next、最近、理解、Related/Evidence）；Memory 与筛选；Memory Detail 的理解链和断链披露；Global AI 的 Context 差异；AI Workspace；Quick Capture 的原文优先、建议关联、确认／忽略；Settings 的低动态预览。交互合同见 `interaction_contract.md`，状态转移见 `state_machine.json`，视觉／可访问性约束见 `visual_contract.json`。

视觉采用系统字体、低饱和纸白、半透明 chrome 与充足留白，不下载资源。语义 HTML、skip link、可见焦点、真实 Tab／Shift+Tab／Enter／Escape 和三项偏好媒体查询均存在；低动态只作用于原型。

### 2026-08-25 用户要求的 Today 视觉校准

在原候选完成后，用户以参考图明确要求调整 Today 视觉。此次只改写正常 Today 状态的组成、色彩／留白与响应式呈现：以“早上好”为先、单一 Today's Focus 为主、Noticed／已确认日程／Day Overview／Recent 为弱辅助卡片，并把底部 Global AI composer 调整为更轻量的固定入口。一级 IA、Focus 0–1、Why／Context 行为、Synthetic／非持久化边界及所有禁止能力均未改变；Day Overview 明确只是固定合成摘要，不是评分、诊断或建议，日程不是外部日历。

视觉差量复核记录在 `evidence/results/visual_delta_20260825.json`，包含隔离 `file:` Chrome 桌面截图与 SHA-256、10/10 静态回归、现有关键 action binding 及 source hash。它是对这次视觉版本的补充核对，**不替代**本节下方原候选的 44-action 动态闭环；若要以该视觉版本重新提交正式 PM 验收，应按 Frozen ABF 再捕获完整动态闭环。

### 2026-08-25 Global AI 入口纠正

依据 `lifeos/architecture/LifeOS高保真原型IA-V1.0.md` 第 4 节，底部常驻条是 **Global AI Bar**，简单对话应从右侧渐进展开。此前视觉校准错误地将其提交行为接成 Quick Capture；现已改为“点击或提交底部条 → 打开同一 Global AI 侧栏”，并把 Quick Capture 保留为明确的 `+` 次级动作。该修正不改变一级 IA、Person/Page/Selection Context、AI Workspace、原文保护、Synthetic／非持久化或无 runtime 边界。

本次纠正的静态行为 Evidence 位于 `evidence/results/global_ai_entry_correction_20260825.json`；新增 Global AI 入口合同检查后，最新静态回归为 11/11 PASS。该记录不替代历史动态闭环。

### 2026-08-25 Me、Memory 与 AI Workspace 视觉统一

用户提供三张高保真参考图后，本候选将 Me、Memory 与 AI Workspace 对齐为同一 Shell：统一日期 chrome、纸白材质、低饱和身份色、圆角卡片与克制留白。Me 保留可纠正的 Person 理解、Contexts、Work／Health 边界与 Memory 追溯；Memory 保留身份、来源、适用范围、Detail 和 Derivation 路径；AI Workspace 保留 Global AI 深度展开、Context Inspector、临时移除 Health 与 Future Agent Task 的诚实占位。没有新增一级导航、账户 Profile、外部日历或真实能力。

本次差量核对见 `evidence/results/multi_page_visual_alignment_20260825.json`；新增视觉 Shell 合同检查后，最新静态回归为 12/12 PASS。该记录是静态／解析／source-hash Evidence，不替代历史动态闭环。

## Evidence、自检与复跑

Chrome 预检在**首个记录尝试**通过：在新标签页地址栏直接加载 `file:///private/tmp/lifeos-p3-116-prototype-v1/index.html`，没有使用 In-app Browser、HTTP、localhost、CDP 或命令行浏览器。最终动态闭环保留 44 个逐动作、带 raw AX 日志与截图 SHA-256 的 PASS 行；两条早期尺寸输入未提交的尝试如实排除在闭环外，随后以 Chrome 内置响应式工具栏的粘贴输入重新获得 ABF 所需三组实际回读：700×760（D-043）、1160×768（D-044）、1280×1024（D-045）。

| 证据项目 | 实际结果 | 主要路径 |
|---|---:|---|
| 静态／边界校验 | 10/10 PASS | `evidence/results/static_results.json` |
| 动态闭环 | 44/44 PASS | `evidence/raw/dynamic_actions.json`、`evidence/dynamic_closure.json` |
| ABF 矩阵 | 18/18 PASS | `evidence/results/matrix_results.json` |
| `file:` Chrome 首轮预检 | 1/1 PASS | `evidence/results/chrome_preflight.json` |
| fail-closed 变异 | 6/6 预期非零 PASS | `evidence/results/mutation_results.json` |
| 临时目录清理 | 0 残留 PASS | `evidence/results/cleanup.json` |
| 非自指 Manifest | 118 entries | `evidence/MANIFEST.md` |

本地预检：`Skipped / Local Model Unavailable`（`<urlopen error [Errno 1] Operation not permitted>`），不作为验收结论。

复跑命令：

```bash
python3 -B lifeos/prototypes/LIFEOS-P3-116/tests/verify_static.py
python3 -B lifeos/prototypes/LIFEOS-P3-116/tests/verify_evidence.py
python3 -B lifeos/prototypes/LIFEOS-P3-116/tests/run_mutations.py
python3 -B lifeos/prototypes/LIFEOS-P3-116/tests/record_cleanup.py
python3 -B lifeos/prototypes/LIFEOS-P3-116/tests/build_manifest.py
```

自检计数：**P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0**。结论只说明执行侧候选与本地边界；不外推为真实价值、风险关闭、PM 接受或阶段推进。

## 角色、关卡与后续判断

主责“产品架构负责人 + 体验设计负责人”已覆盖 person-first IA、页面层次和视觉／交互合同；协审检查点以身份分层、用户控制、四 Gate、无障碍、无 runtime、闭环／mutation 覆盖。Gate 1、2、3 的执行侧自检通过；Gate 4 只做架构调和核对；Gate 5 只形成未来可测试假设。

没有尚未调和的产品语义问题，也没有请求修改一级 IA、架构、Schema/API、风险、冻结或阶段。需要 PM 主会话做的唯一动作是依据 Frozen ABF 对此 **Candidate Ready** 候选进行正式验收；若 PM Pass，仍须用户采纳，之后才可在另一个全新隔离会话创建关键原型独立评审与新的 ABF。当前不得开始 runtime／工程、不得冻结产品／原型、不得进入 Stage 4。
