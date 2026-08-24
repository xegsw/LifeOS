# LIFEOS-P3-087｜三张冻结今日页响应式与键盘可达性受控 UI 能力包

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务只在指定本地工作区、新建隔离工程目录、固定非敏感文本和 task-local 临时副本中进行防御性本地 UI 工程、可访问性验证与回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、离线、失败与边界术语只用于验证本项目内部的防御性体验，不授权扩大范围。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-087
- 优先级：P0
- 任务类型：受控 UI 工程能力包
- 能力包边界：P3-085 三张冻结今日页在纯本地、无持久化、无网络 `file:` UI 范围内的响应式布局、键盘可达性、焦点可见性和状态切换可用性。
- 包内允许工作：实现、回归、必要补测、Evidence 整理和文案对齐；仅限新目录。
- 包内整改授权：限本任务目录、固定非敏感文本、上述能力和验收矩阵；不扩大为真实数据、保存、权限、AI、导出、同步或桌面运行时。
- 必须独立处理：风险关闭／重开、工程基线恢复、冻结、真实 DB／路径／文件／Vault／Tauri/IPC／网络／云／第三方／同步／多设备／L3／外部用户、Stage 4。
- 状态：`Ready / Task-card Delivery Authorizes Execution`。
- 执行授权：用户将本任务卡路径发送至新建隔离 Codex 工程会话即授权执行。
- 单独确认例外：None；本卡不授权真实能力或外部访问。

## Agent、模型与会话

- 推荐 Agent：Codex，新建隔离工程会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 选择理由：需要在不触及真实能力的前提下，完成多页面 UI、键盘交互、响应式状态与可复查 Chrome Evidence。
- 允许降级：`gpt-5.6-luna` + `high`（仅静态文案／样式整理且完整动态矩阵仍可复核时）。
- 禁止降级：动态交互、可访问性、Evidence、P0/P1、关闭态或范围争议。
- 必须升级／回报：P0/P1、hash/Evidence 冲突、范围扩大、任何真实能力触达或 Chrome 预检失败。
- 后备：`gpt-5.5` + `xhigh`（首选不可用时，记录原因）。
- 后续独立评审：Yes；本能力包 PM Pass 和用户采纳后，必须一次全新隔离独立复评。
- 可修改工程／账本：`lifeos/engineering/LIFEOS-P3-087/` / No。

## 最小读取包与直接输入

新会话必须读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`、P3-085 交付物／PM Review／工程 Evidence Manifest、P3-086 attempt-3 独立 Review／Evidence Manifest、P1-004／P1-009／P1-011 的冻结设计输入、`PM_OPERATING_MODEL.md` 的受控能力包、包内自检和本地 `file:` 浏览器预检章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。

必须新建会话，且不得复用 P3-085 执行、P3-086 任一评审或 PM 验收会话；首份报告记录任务卡路径、会话类型与接收时间。

## 实现范围

1. 仅在 `lifeos/engineering/LIFEOS-P3-087/` 新建三张可独立 `file:` 打开的页面、相对本地 CSS／JS、独立 runner 与 Evidence。
2. 保留 P3-085 的三种状态语义、显式非自动导航、AI 未启用、无可靠建议不虚构、受限／离线 fail-closed、页面会话内固定非敏感输入与刷新／关闭清除。
3. 提供语义化 landmark／标题层级、可见焦点、键盘可达的导航和按钮、合理 Tab 顺序、移动窄屏与桌面宽屏布局；不得以仅视觉隐藏方式丢失状态或边界文案。
4. 以 Google Chrome（`com.google.Chrome`）通过 Computer Use `@oai/sky` 控制新标签页，先对 task-local 副本执行 `file:` 预检并记录 URL、时间、hash 与加载结果；预检通过后，动态验证键盘 Tab／Enter、三页导航、关键交互、窄屏／宽屏视觉与刷新／关闭重开清除。
5. 静态检查并动态核对：无远程 URL／网络、浏览器持久化、文件 API、真实文件／DB、Vault、Tauri/IPC、导出、同步、模型调用或第三方依赖。

## Evidence 与完成定义

- 干净临时副本覆盖首次、重复确认、键盘路径、刷新、关闭重开、失败披露和关闭态。
- 保存可运行 runner 源码、逐项结构化结果、操作日志、宽／窄屏视觉记录、hash、Manifest、复跑说明及“验收标准→测试→Evidence”矩阵。
- 核对 P3-085／P3-086 历史资产 hash 未被覆盖。
- Chrome 预检失败时，In-app Browser 或 Browser-control 的拒绝仅为工具限制；只有 Computer Use Chrome 正常操作连续两次加载失败且完整记录时，才可提出候选 Blocked。
- P0/P1、合同违反、Evidence 冲突、独立性不足、Unknown／Not Implemented、关闭态失效或范围扩大，必须在本能力包内整改后再提交 PM；不得写成通过。

## 非范围与停止条件

不修改 P3-085／P3-086、冻结设计或项目账本；不读取真实个人数据／文件，不使用真实 DB、持久化、网络、HTTP、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不关闭风险、不恢复基线、不冻结资产、不进入 Stage 4。任何需要这些能力的需求立即停止并回报 PM。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-087/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-087_three_frozen_today_pages_responsive_accessibility_controlled_ui_capability_package.md`
- Evidence：`lifeos/engineering/LIFEOS-P3-087/evidence/MANIFEST.md`
- 通过条件：三页可独立本地打开；键盘与响应式路径可复查；状态／关闭态不变；完整 Evidence、无 P0/P1/Unknown/Not Implemented。
- 仅使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 简短回报。
