# LIFEOS-P3-091｜三张冻结今日页内容身份与处理边界可见性受控 UI 能力包

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限指定本地工作区、新建隔离工程目录、固定非敏感合成文本和 task-local 临时副本，用于防御性本地 UI 工程、内容身份可见性与关闭态验证。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。任务中的权限、撤回、恢复、失败与反例术语只用于验证本项目的合成 fail-closed UI，不授权扩大范围。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-091
- 优先级：P0
- 任务类型：受控 UI 工程能力包。
- 能力包边界：在 P3-089 已验收的三张纯本地、无持久化、无网络 `file:` 页面基础上，新增一致、可访问的**内容身份与处理边界可见性**；仅覆盖固定非敏感合成演示，不连接运行时或真实数据。
- 包内允许工作：仅在本任务新目录完成实现、回归、必要补测、Evidence 整理和文案对齐。
- 包内整改授权：限本任务工程目录、固定合成文本、页面内存与验收矩阵；不得扩大目录、风险、真实能力、冻结或阶段范围。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实 DB／路径／文件／Vault／Tauri/IPC／网络／云或第三方／同步／多设备／L3／外部用户、Stage 4。
- 状态：`Accepted / PM Pass / Awaiting User Adoption`。
- 执行授权：用户将本任务卡路径发送至新建隔离 Codex 工程会话即授权执行。
- 单独确认例外：None；本卡不授权真实能力或外部访问。

## Agent、模型与会话

- 推荐 Agent：Codex，新建隔离工程会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 选择理由：需要保持冻结页面信息架构、合成／真实能力边界、可访问性和可复核 Chrome Evidence 一致。
- 允许降级：None。
- 禁止降级条件：内容身份／边界文案、动态关闭态、Evidence、P0/P1 或范围争议。
- 必须升级／回报：P0/P1、hash／Evidence 冲突、范围扩大、任何真实能力触达或 Chrome 预检失败。
- 后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，记录原因）。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后须一次全新隔离独立复评。
- 可修改工程／项目账本：`lifeos/engineering/LIFEOS-P3-091/` / No。

## 会话隔离与最小读取包

- 必须新建会话：Yes；不得复用 P3-089 工程执行、P3-090 独立复评或 PM 验收会话。
- 新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`、P3-089 任务卡／交付物／PM Review／工程 Evidence Manifest、P3-090 attempt-2 独立 Review／Evidence Manifest／PM Review、`PM_OPERATING_MODEL.md` 的受控能力包、包内自检与 `file:` Chrome 预检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入均只读：`lifeos/engineering/LIFEOS-P3-089/` 和上述 Review／Evidence；不得导入或调用其 runner／测试作为本任务主证据。
- 首份会话报告须记录任务卡路径、会话类型与接收时间。

## 实现与验证范围

1. 仅在 `lifeos/engineering/LIFEOS-P3-091/` 创建三张独立 `file:` 页面、相对本地 CSS／JS、独立 runner 与 Evidence；不修改 P3-089、冻结设计或项目账本。
2. 保留 P3-089 的三张页面、合成生命周期和全部关闭态；新增统一、可访问、页面内可见的身份说明，明确区分：固定非敏感演示文本、用户明确确认动作、合成系统状态、AI 未启用、以及未发生真实保存／授权／恢复／处理。
3. 在默认恢复、暂无可靠建议、权限受限／离线三页均展示与该页面状态一致的边界说明；不得以成功 toast、模糊状态或“已处理”暗示真实能力。
4. 保留并验证空输入拒绝、明确／重复确认、默认拒绝、grant／revoke、精确 `CONFIRM`、重复回执、模拟失败清理、刷新／关闭重开清除、三页导航、skip link、Tab／Enter、可见焦点、宽／窄屏和 reduced-motion。
5. 使用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 在新标签页直接打开 task-local `file:` 副本；先记录 URL、时间、hash 与加载结果，预检通过后执行动态／视觉矩阵。不得使用 In-app Browser、Browser-control、HTTP、网络、CDP、命令行浏览器或策略绕过替代。
6. 静态和动态核查关闭态：无远程 URL／HTTP／网络、浏览器持久化、文件 API、真实文件／DB、SQLite、Vault、Tauri/IPC、导出、同步、模型调用或第三方依赖。

## Evidence 与完成定义

- 在干净临时副本验证首次、重复／幂等、拒绝／撤回、恢复确认、失败清理、刷新、关闭重开、键盘路径、三页导航与宽／窄屏。
- 保存独立 runner、逐项结构化结果、操作日志、宽／窄屏视觉记录、hash、Manifest、复跑说明及“验收标准→测试→Evidence”矩阵。
- 核对 P3-089 和 P3-090 attempt-2 指定只读资产 hash 未被覆盖。
- 执行侧提交时必须报告自检是否通过以及 P0/P1/P2/Unknown/Not Implemented 数量；同范围问题先在本包整改，不另建任务号。
- P0/P1、明确合同违反、Evidence 冲突、独立性不足、Unknown／Not Implemented、关闭态失效或范围扩大，必须在本能力包内整改后再提交 PM；不得写成通过。

## 非范围与停止条件

不接入 P3-079 Python／SQLite／CLI，不连接或写入真实数据、文件或数据库；不修改 P3-089、P3-090、冻结设计或项目账本；不启用持久化、网络、HTTP、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不关闭风险、不恢复基线、不冻结资产、不进入 Stage 4。任何需要这些能力的需求立即停止并回报 PM。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-091/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-091_three_frozen_today_pages_content_identity_and_boundary_clarity_controlled_ui_capability_package.md`
- Evidence：`lifeos/engineering/LIFEOS-P3-091/evidence/MANIFEST.md`
- 通过条件：三页内容身份与处理边界清楚、一致且可访问；不伪称真实能力；生命周期与关闭态不回退；完整 Evidence；P0/P1/Unknown/Not Implemented 为零。
- 会话回复仅使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，输出摘要、交付物路径和是否需要 PM 决策。

## D-0370 窄 Rework 补充（已获用户确认）

- 原因：D-0368 发现初始提交缺少两项任务卡明确要求的动态 Evidence；不代表内容身份／边界 UI 存在工程缺陷。
- 仅允许：在原 P3-091 工程会话、同一工程目录与干净 task-local 副本内补齐 Evidence；不得改变 UI 范围或引入任何真实能力。
- 必须新增并在 `evidence/dynamic_evidence_closure.md` 或等价 JSON 中逐项记录：
  1. 关闭已确认状态的 task-local Chrome 标签页，再以新标签页打开同一副本；默认拒绝、输入、预览与回执均清除。
  2. 从页面起点实际执行 Tab 至 skip link／主要控件，并以 Enter 触发一个无害的已有页面内动作；记录可见焦点、触发结果与关闭态未回退。
- 每项均须有结构化结果 ID、视觉／日志 Evidence、SHA-256，且 runner／自检脚本须验证闭环表无缺项；缺项不得报 Pass。
- 新 Evidence 可写入 `lifeos/engineering/LIFEOS-P3-091/evidence/rework/attempt-2/`，不得覆盖初次 Evidence。工程、P3-089／P3-090、风险、冻结、基线、阶段和项目账本仍不得修改。
