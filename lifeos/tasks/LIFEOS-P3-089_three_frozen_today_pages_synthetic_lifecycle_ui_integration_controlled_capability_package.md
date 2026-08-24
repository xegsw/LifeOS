# LIFEOS-P3-089｜三张冻结今日页合成生命周期 UI 整合受控能力包

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限指定本地工作区、新建隔离工程目录、固定非敏感合成文本和 task-local 临时副本，用于防御性本地 UI 工程、状态边界验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、拒绝、撤回、恢复、失败与反例术语只用于展示并验证本项目内部的合成 fail-closed UI 状态，不授权扩大范围。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-089
- 优先级：P0
- 任务类型：受控 UI 工程能力包。
- 能力包边界：在纯本地、无持久化、无网络 `file:` 页面中，以固定合成状态将 P3-079 的捕获／明确确认、默认拒绝／grant／revoke、恢复／拒绝／失败披露语义，整合进 P3-087 三张冻结今日页的可操作生命周期演示；不连接或复用 P3-079 真实运行时、CLI、SQLite 或任何真实能力。
- 包内允许工作：仅在新目录完成实现、回归、必要补测、Evidence 整理和文案对齐。
- 包内整改授权：限本任务目录、固定合成文本、页面内存状态与验收矩阵；不得扩展至持久化、真实数据、真实权限、真实恢复、文件／DB、Tauri/IPC、网络或阶段范围。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实 DB／路径／文件／Vault／Tauri/IPC／网络／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 状态：`Ready / Task-card Delivery Authorizes Execution`。
- 执行授权：用户将本任务卡路径发送至新建隔离 Codex 工程会话即授权执行。
- 单独确认例外：None；本卡不授权真实能力或外部访问。

## Agent、模型与会话

- 推荐 Agent：Codex，新建隔离工程会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 选择理由：需同时保持冻结 UI 状态语义、合成生命周期 fail-closed 体验、可访问性与可复查 Chrome Evidence。
- 允许降级：None。
- 禁止降级条件：动态交互、权限／恢复关闭态、Evidence、P0/P1 或范围争议。
- 必须升级／回报：P0/P1、hash／Evidence 冲突、范围扩大、任何真实能力触达或 Chrome 预检失败。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，记录原因）。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后须一次全新隔离独立复评。
- 可修改工程／项目账本：`lifeos/engineering/LIFEOS-P3-089/` / No。

## 会话隔离与最小读取包

- 必须新建会话：Yes；不得复用 P3-079、P3-087／088 的执行、评审或 PM 验收会话。
- 新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`、P3-079 交付物／P3-080 PM Review、P3-087 交付物／PM Review／工程 Evidence Manifest、P3-088 独立 Review／PM Review／Evidence Manifest、`PM_OPERATING_MODEL.md` 的受控能力包、包内自检与 `file:` Chrome 预检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入均只读：`lifeos/engineering/LIFEOS-P3-079/`、`lifeos/engineering/LIFEOS-P3-087/`、上述 Review／Manifest；不得导入或调用其测试 runner 作为本任务主证据。
- 首份会话报告须记录任务卡路径、会话类型与接收时间。

## 实现与验证范围

1. 只在 `lifeos/engineering/LIFEOS-P3-089/` 新建三张可独立 `file:` 打开的 HTML 页面、相对本地 CSS／JS、独立 runner 与 Evidence；不修改冻结设计或任何既有工程。
2. 页面必须明确标示为“合成生命周期演示”，区分用户原文／用户确认行动／合成系统状态／AI 未启用；不得把 UI 演示写成真实保存、真实授权或真实恢复。
3. 覆盖并可操作演示：空输入拒绝→非敏感文本→明确确认→重复确认幂等；默认拒绝→明确 grant→撤回／拒绝后 fail-closed；恢复预览→明确 CONFIRM→重复回执；模拟失败时无成功表述、清理显示状态并披露失败。所有状态仅存在于当前页面 DOM，刷新／关闭重开后清除。
4. 保留并扩展 P3-087 的三态边界：默认恢复、暂无可靠建议、权限受限／离线；导航、skip link、键盘 Tab／Enter、可见焦点、宽／窄屏和 reduced-motion 均可用。
5. 以 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 控制新标签页，先对 task-local 副本执行 `file:` 预检；记录 URL、时间、hash 与加载结果。预检通过后才进行完整动态矩阵。
6. 静态和动态核查关闭态：无远程 URL／HTTP／网络、浏览器持久化、文件 API、真实文件／DB、SQLite、Vault、Tauri/IPC、导出、同步、模型调用或第三方依赖。

## Evidence 与完成定义

- 在干净临时副本验证首次、重复／幂等、拒绝／撤回、恢复确认、失败清理、刷新、关闭重开、键盘路径、三页导航与宽／窄屏。
- 保存独立 runner 源码、逐项结构化结果、操作日志、宽／窄屏视觉记录、hash、Manifest、复跑说明及“验收标准→测试→Evidence”矩阵。
- 核对 P3-079、P3-087、P3-088 的指定只读资产 hash 未被覆盖。
- Chrome 预检失败时，In-app Browser 或 Browser-control 的拒绝仅为工具限制；只有 Computer Use Chrome 正常操作连续两次加载失败且完整记录时，才可提出候选 Blocked。
- P0/P1、明确合同违反、Evidence 冲突、独立性不足、Unknown／Not Implemented、关闭态失效或范围扩大，必须在本能力包内整改后再提交 PM；不得写成通过。

## 非范围与停止条件

不接入 P3-079 Python／SQLite／CLI，不连接或写入任何真实数据、文件或数据库；不修改 P3-079、P3-087、P3-088、冻结设计或项目账本；不启用持久化、网络、HTTP、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不关闭风险、不恢复基线、不冻结资产、不进入 Stage 4。任何需要这些能力的需求立即停止并回报 PM。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-089/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-089_three_frozen_today_pages_synthetic_lifecycle_ui_integration_controlled_capability_package.md`
- Evidence：`lifeos/engineering/LIFEOS-P3-089/evidence/MANIFEST.md`
- 通过条件：合成生命周期各状态可复查、未伪称真实能力、关闭态与可访问性不回退、完整 Evidence 且 P0/P1/Unknown/Not Implemented 为零。
- 会话回复仅使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，输出摘要、交付物路径和是否需要 PM 决策。
