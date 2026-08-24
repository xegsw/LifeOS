# LIFEOS-P3-087｜三张冻结今日页响应式与键盘可达性受控 UI 能力包

## 任务信息

- 任务 ID：LIFEOS-P3-087
- 任务名称：三张冻结今日页响应式与键盘可达性受控 UI 能力包
- 执行 Agent：Codex（实际配置：`gpt-5.6-terra` + high；未降级）
- 任务类型：P3 受控 UI 工程能力包
- 更新时间：2026-08-21

## 修复／验证目标

- 在新隔离目录实现三张可独立 `file:` 打开的纯本地今日页，并保留 P3-085 的三态语义与关闭态。
- 提供 landmark、标题层级、跳过链接、原生键盘可达控件、可见焦点、合理 Tab 顺序，以及宽／窄布局。
- 核对显式确认、重复确认、失败清理、刷新与关闭重开均不保留页面会话输入。
- 静态及 Chrome 动态核对真实能力均保持关闭。

## 修改范围

- 新建 `lifeos/engineering/LIFEOS-P3-087/`：三页 HTML、相对本地 CSS／JS、独立 Node runner、README 与完整 Evidence。
- 新建本交付物；未修改项目账本、P3-085／P3-086 或冻结设计输入。

## 非范围

- 不改变产品定位、V1 范围、冻结设计、技术架构、核心领域模型或 AI 权限边界。
- 不启用真实数据、持久化、网络、真实文件／DB、Vault、Tauri/IPC、云／第三方、导出、同步、多设备、L3 或外部用户。
- 不关闭风险、不恢复工程基线、不冻结资产、不进入 Stage 4。

## 测试摘要

- 静态复跑：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node lifeos/engineering/LIFEOS-P3-087/tests/static_check.mjs lifeos/engineering/LIFEOS-P3-087`
- 干净临时副本：`/private/tmp/lifeos-p3-087.Yvv65U/app`；源与副本五项 hash 一致。
- 静态：61 PASS / 0 FAIL；覆盖结构、相对本地导航、语义、可见焦点／窄屏 CSS、状态、失败清理和禁止能力关闭态。
- Chrome 动态／视觉：12 PASS / 0 FAIL。Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 新标签预检通过后，完成 Tab／Enter 导航、受控路径、确认／重复、失败清理、刷新／关闭重开、宽／窄布局核对。
- 自检：P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0。

## P0／P1／P2 状态

- P0：0。
- P1：0。
- P2：0。
- 原子失败、半成品清理、失败披露、拒绝／阻断与 fail-closed：已覆盖；“审计追溯”不适用，因为本包没有审计或持久化能力，操作日志只作本地 Evidence。

## Evidence

- Manifest：[MANIFEST.md](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-087/evidence/MANIFEST.md)
- 结构化结果：[static_results.json](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-087/evidence/static_results.json)、[dynamic_results.json](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-087/evidence/dynamic_results.json)
- 操作日志与矩阵：[operation_log.md](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-087/evidence/operation_log.md)、[acceptance_matrix.md](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-087/evidence/acceptance_matrix.md)
- P3-085 历史五项 SHA-256 与 P3-086 attempt-3 Manifest 对照一致，未覆盖。
- 本地预检：[P3-087 Local Precheck](/Users/xxe/Documents/No.2/lifeos/local_prechecks/LIFEOS-P3-087_LIFEOS-P3-087_three_frozen_today_pages_responsive_accessibility_controlled_ui_capability_package_local_precheck.md)；因本地模型不可访问而 Skipped，未参与结论。

## 角色与关卡

- 主责：体验设计负责人（响应式、可读性、键盘路径和状态理解）。
- 协审：技术架构负责人、AI 信任与安全负责人、产品架构负责人。
- Gate 1：Pass（有限 UI 边界）；三态仍服务 Project 恢复，未演化为后台或自动决策。
- Gate 3：Pass（有限 UI 边界）；AI 明确未启用，确认、原文和受限状态未混淆。
- Gate 4：Pass（有限 UI 边界）；纯本地 `file:` 静态壳、Chrome 动态和禁止能力关闭态均可复查。
- Gate 2／5：N/A；不批准数据／来源运行时或外部用户价值验证。

## 剩余风险与后续关卡

- 本结论不等于关键资产冻结、风险关闭、工程基线恢复、真实能力启用或 Stage 4 准入。
- 需要一次全新隔离独立安全／体验复评；本执行会话不得自行完成。

## 用户确认

- 是否触发：No。本包严格停留在用户已授权的静态本地 UI 与固定非敏感文本范围内。
- PM 仍需验收本能力包；PM Pass 后由用户决定是否采纳并创建独立复评。
