# LIFEOS-P3-085｜三张冻结今日页多页本地 UI 壳受控能力包

## 授权与安全语境

`N/A — 不涉及双用途安全语义`。

## 任务信息

- 任务 ID：LIFEOS-P3-085
- 优先级：P0
- 任务类型：受控能力包／本地 UI 工程实现与验证
- 能力包边界：将三张已冻结“今日”状态落实为三个可单独以 `file:` 打开的纯本地 HTML 页面壳，并用明确、可见的页面内导航连接它们。仅限非敏感演示文案与当前页面内存交互。
- 包内允许工作：在新隔离目录实现页面、样式、少量无依赖脚本、自动静态检查、干净副本浏览器演练、Evidence 整理与文案对齐。
- 包内整改授权：仅限本任务工程目录、测试、Evidence 与交付物；同范围问题在包内修正，不另建微型 Rework。
- 必须独立处理：真实个人数据／真实 DB／真实文件或路径／Vault／Tauri/IPC／网络／云／第三方／同步／多设备／L3／外部用户、风险关闭或重开、工程基线恢复、Schema/API 或关键资产冻结、Stage 4 准入。
- 建议篇幅：1500–3000 字
- 是否适用 P3 Engineering Fast Lane：No（P0 能力包）。

## Agent、模型与授权

- 推荐执行 Agent：Codex
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`
- 选择理由：需要保持冻结原型表达、纯本地边界、可运行页面和完整可复核 Evidence。
- 允许降级模型：None
- 禁止降级条件：P0 能力包、Evidence／hash 冲突、范围扩大、真实能力触达、无法完整执行交付前自检。
- 必须升级条件：发现 P0/P1、真实数据／文件／网络／持久化／Tauri/IPC 触达、冻结原型冲突或无法保持能力边界时停止并回报 PM。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，必须记录原因）。
- 是否需要后续独立评审：Yes；PM 验收通过并由用户采纳后，须一轮全新隔离独立安全／体验复评。
- 是否允许修改工程文件：Yes，仅 `lifeos/engineering/LIFEOS-P3-085/`。
- 是否允许修改项目账本：No。
- 主责角色：体验设计负责人／技术架构负责人。
- 协审角色：产品架构负责人、AI 信任与安全负责人。
- 必须通过的关卡：Gate 1／3／4（仅纯本地 UI 前置范围）；Gate 2、Gate 5 不作运行时批准。
- 状态：`Ready / Task-card Delivery Authorizes Execution`。
- 执行授权方式：用户将本任务卡路径投递至新建隔离 Codex 工程会话即授权执行。
- 投递前仍需单独用户确认的例外：None；本卡不授权真实能力或外部访问。
- 授权证据：首份会话报告记录本卡路径、会话类型与接收时间。

## 会话路由与读取

- 是否建议新建会话：Yes。
- 会话类型：Codex 工程执行。
- 隔离理由：P3-082／084 是已完成的执行与独立评审链；P3-085 是新的工程目录和 UI 形态，需避免历史 Evidence 混淆。
- 必须重新读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅格式参考）、P3-082 交付物／PM Review／工程 Manifest、P3-084 PM Review 与 Rework 独立 Review、P1-004／P1-009／P1-011 的三张冻结设计输入、`PM_OPERATING_MODEL.md` 的受控能力包和包内自检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 可复用既有读取结果：无（新会话）。

## 实现范围

1. 在 `lifeos/engineering/LIFEOS-P3-085/` 新建独立、无依赖的静态页面壳：默认恢复、暂无可靠建议、权限受限／离线；每页可独立以 `file:` 打开。
2. 每页提供清晰的、非自动的状态导航，保留“今日从哪里继续”的主叙事、无建议时不虚构建议、受限／离线时 AI 未启用和网络未使用的边界。
3. 默认恢复页保留当前页面会话内的非敏感手动捕获演示：空文本拒绝、显式确认后才显示、模拟失败不展示记录；刷新或关闭清除。
4. 页面不得读取、导入、写入任何用户文件、DB、浏览器持久化、网络、服务、Tauri/IPC、Vault、导出、同步、模型或第三方依赖。
5. 不修改冻结原型或 P3-082；仅把其状态／层级作为只读设计输入，新工程不得声称原型或资产已重新冻结。

## 包内交付前自检与 Evidence

- 在干净临时副本以 `file:` 端到端演练：首次、重复确认、刷新、关闭重开；三页互相导航；空文本、模拟失败、无建议两条路径、受限／离线与 AI 关闭。
- 运行新写的静态 runner；不得导入、调用或复制 P3-082／084 runner 作为主验证实现。
- 逐项保存 runner 源码、结构化结果、操作日志、视觉记录、hash、Manifest、复跑说明、验收标准→测试→Evidence 矩阵。
- 核对 P3-082／084 历史只读资产 hash 未被覆盖；静态检查全部禁止能力仍关闭。
- 本地预检默认执行；不可用时如实写 Skipped，不阻断。
- 交付物必须声明包内自检结论和 P0/P1/P2/Unknown/Not Implemented 数量。若 P0/P1、明确合同违反、Evidence 冲突、范围扩大、关闭态失效或影响完成定义的 Unknown／Not Implemented，必须回包内整改，不得写成通过。

## 非范围与停止条件

- 不启动 HTTP 服务、不访问网络、不使用浏览器持久化；不使用真实文本、真实文件、真实 DB、Vault、Tauri/IPC、云、导出、同步、多设备、L3 或外部用户。
- 不关闭／重开风险，不恢复工程基线，不冻结资产，不进入 Stage 4，不自行创建后续任务。
- 出现任何需要上述能力的需求，立即停止并回报 PM。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-085/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-085_three_frozen_today_pages_multipage_local_ui_shell_controlled_capability_package.md`
- 自检 Evidence：`lifeos/engineering/LIFEOS-P3-085/evidence/MANIFEST.md`
- 通过条件：三个独立页面均可本地打开和导航；状态／交互／关闭态与任务卡一致；自检、矩阵与 Evidence 可复核；无 P0/P1、Unknown 或 Not Implemented。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，仅输出摘要、路径和是否需要 PM 决策。
