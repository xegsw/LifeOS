# LIFEOS-P3-115｜人本双领域自用 MVP 高保真原型与交互合同

## 交付结论

**Candidate Ready（待 PM 验收；非 PM Pass、非 Frozen）**。

已在受控目录交付一个完全本地、代码原生的 Chrome `file:` 高保真原型。它把 P3-113/P3-114 已采纳的人本双领域结果表达为可操作的 Today、Memory、Domains 界面及状态机：Person 为一级主体；工作和健康／健身并列；Project 仅为工作项“产品演示准备”的语境。所有内容都是固定合成 fixture，页面不含真实数据、网络、模型、持久化、Tauri/IPC、数据库或文件能力。

执行授权证据：用户于 2026-08-24 将任务卡绝对路径投递至本全新 Codex 产品设计／前端原型专项会话。启动前重新读取 `ABF-P3-115-v2`（SHA-256 `3dee373444132933bb927a6b8bf39550981663d3f9420d4bdbce5eb7a620f9f2`）及任务定向材料；D-0466 的固定输入谱系已复算匹配。会话未发生模型降级或后备切换，按任务卡路由 `gpt-5.6-terra / xhigh` 执行。P3-113/P3-114、工程、账本、风险、冻结和 retained Pilot 均保持只读。

## 原型与合同

- 原型入口：[index.html](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/index.html)
- 固定合成内容：[fixtures.json](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/fixtures.json)
- 交互合同：[interaction_contract.md](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/interaction_contract.md)
- 可机读状态机：[state_machine.json](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/state_machine.json)
- 视觉／响应式合同：[visual_contract.json](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/visual_contract.json)

关键实现边界如下。

| 合同项 | 可见行为 | 明确不宣称／不执行 |
|---|---|---|
| 健康门槛 | 未答、跳过、警示均关闭或降级训练型建议；只有“无警示”出现低强度、可停止的固定合成候选 | 诊断、治疗、保证、真实健康建议 |
| 身份 | Source、Artifact、Derivation、Advice、Feedback、EXE、RES、Memory candidate 可区分 | 将建议、反馈、执行或结果互相推定 |
| 生命周期 | 认可、修改后接受、拒绝、延后；修改后才可分别报告未执行／执行／结果；结果只形成待确认候选 | 自动 Action、排程、跨日偏好或真实长期写入 |
| 来源异常 | missing、stale、conflict、unauthorized 四种固定合成情境全部 fail-closed | 把缺口伪装成可靠个性化建议 |
| 捕获与导航 | Today／Memory／Domains 为 Person IA；“记录”明确为原型入口且不保存／发送 | Project 管理后台、真实捕获成功回执 |

视觉采用系统字体、低饱和浅色层次、清晰身份标签、可见焦点、非颜色单独传达状态和克制动效；`prefers-reduced-motion` 与原型内“低动态预览”均关闭位移式长过渡。历史截图只用作克制、空间与可读性参考，未复制其 Project-first 结构。

## 动态 Evidence 与自检

动态测试只用 `com.google.Chrome` 由 Computer Use 正常操作。首次预检即在新标签页成功直接加载：

`file:///private/tmp/lifeos-p3-115-prototype-v1/index.html`

未使用 In-app Browser、HTTP、localhost、CDP、命令行浏览器或绕过安全策略。随后在 Chrome 内置响应式工具栏中实际设为 1280×1024、1160×768、700×760，并保留页面可见的实时 viewport 读数与完整 Chrome 截图；该工具栏仍是同一 Chrome `file:` 页面，不引入服务或外部环境。

矩阵和动态闭环由 raw AX 日志、实际 Chrome 截图及 SHA-256 逐项复算：

- 16/16 Frozen ABF matrix 行 PASS。
- 44/44 逐动作 closure 行 PASS，覆盖默认/依据详情、三种健康回答、四种反馈、EXE/RES、Memory 候选拒绝与确认、四种来源异常、撤销、刷新、关闭重开、全局导航/捕获、三个 viewport，以及 Tab/Shift+Tab/Enter/Escape/低动态。
- 静态关闭扫描 PASS：无远程 URL、fetch/XHR/WebSocket、storage/cookie、整页图片或背景图片伪实现。
- mutation verifier PASS：篡改 Matrix 状态后退出码 `1`；篡改 raw Evidence 后因 SHA-256 不匹配退出码 `1`。
- 非自指 Manifest 覆盖源码、fixture、合同、runner、raw 日志、截图、结构化结果与清理证明。

证据入口：

- [动态闭环](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/dynamic_closure.json)
- [逐行矩阵](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/results/matrix_results.json)
- [固定输入复算](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/fixed_inputs.json)
- [变异校验结果](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/results/mutation_results.json)
- [精确清理证明](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/results/cleanup.json)
- [非自指 Manifest](/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-115/evidence/MANIFEST.md)

本地预检已按规则调用，但本地模型不可用（`<urlopen error [Errno 1] Operation not permitted>`），因此记录为 **Skipped / Local Model Unavailable**，不影响人工／PM 复核流程：[预检记录](/Users/xxe/Documents/No.2/lifeos/local_prechecks/LIFEOS-P3-115_LIFEOS-P3-115_human_centered_dual_domain_self_use_mvp_high_fidelity_prototype_and_interaction_contract_local_precheck.md)。

可复跑顺序（只在 Frozen 范围内）：

```bash
python3 lifeos/prototypes/LIFEOS-P3-115/tests/verify_static.py
python3 lifeos/prototypes/LIFEOS-P3-115/tests/build_results.py
python3 lifeos/prototypes/LIFEOS-P3-115/tests/build_manifest.py
python3 lifeos/prototypes/LIFEOS-P3-115/tests/verify_evidence.py
```

动态重跑必须先从空的精确临时根复制候选，再仅用 Chrome 新标签页直接打开上述 `file:` URL；mutation 校验在清理前运行，随后仅删除精确根并运行 `record_cleanup.py`，最后重建结果、Manifest 与 verifier。

## 关卡、边界与计数

- Gate 1（产品中心与信息架构）：通过包内自检；Person-first 与双领域可见。
- Gate 2（身份、反馈、健康安全）：通过包内自检；建议、反馈、EXE、RES、Memory 与 fail-closed 均分离。
- Gate 3（动态 Evidence／无障碍／响应式）：通过包内自检；Chrome `file:`、三 viewport、键盘与 reduced-motion 均有逐动作证据。
- Gate 4（技术可实现性边界）：仅核对原型边界；未实现 runtime，也未预授权任何工程能力。
- Gate 5（真实价值）：未判定；固定合成原型不能证明真实用户价值。

最终包内计数：**P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0**。

唯一临时根 `/private/tmp/lifeos-p3-115-prototype-v1` 已在动态、mutation 证据完成后精确删除；清理记录确认路径不存在。未修改 `lifeos/engineering/`、风险日志、冻结状态、阶段、任务登记或任何历史资产。R-0040 与 R-0052 仍为 Open，R-0051 保持既有有限关闭；本任务仍为 Not Frozen，Stage 4 未准入。

## PM 待确认

请 PM 依据 Frozen ABF 复核本候选。若 PM 验收通过，仍须用户采纳后另建全新隔离的关键原型独立评审；独立评审、PM 验收和用户明确决定之前，不得将本候选写作 Frozen、runtime 已实现、风险已关闭或 Stage 4 准入。
