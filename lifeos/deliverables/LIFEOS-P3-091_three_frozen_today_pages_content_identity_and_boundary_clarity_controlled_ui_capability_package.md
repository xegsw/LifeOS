# LIFEOS-P3-091｜三张冻结今日页内容身份与处理边界可见性受控 UI 能力包

## 任务信息与授权

- 任务卡：`lifeos/tasks/LIFEOS-P3-091_three_frozen_today_pages_content_identity_and_boundary_clarity_controlled_ui_capability_package.md`
- 执行授权：用户于 2026-08-21 将任务卡路径投递至本新建隔离 Codex 工程会话。
- 实际写入：`lifeos/engineering/LIFEOS-P3-091/`、本交付物与本地预检输出；未修改项目账本、P3-089 或 P3-090 只读资产。
- 实际模型：`gpt-5.6-terra` + `high`。

## 交付事实

新建三张独立 `file:` 今日页（默认恢复、暂无可靠建议、权限受限／离线）及相对本地 CSS／JS。每一页均在首屏可见地分开说明：固定非敏感演示文本、用户明确确认动作、合成系统状态与 AI 未启用；且明确未发生真实保存、授权、恢复或处理。

保留页面内存的合成生命周期与 fail-closed 行为：空输入拒绝、明确与重复确认、默认拒绝／grant／revoke、恢复预览、精确 `CONFIRM`、重复回执、模拟失败清理、刷新清除、三页导航、skip link、可见焦点、响应式与 reduced-motion。未连接真实数据、文件、DB、网络、Tauri/IPC、模型、第三方依赖或浏览器持久化。

## 包内自检

**通过。**

- 当前工程与干净 task-local 副本静态 runner 均为 **97 PASS / 0 FAIL**。
- Google Chrome (`com.google.Chrome`) 经 Computer Use `@oai/sky` 在新标签页 `file:` 预检通过后，动态／视觉矩阵 **15 PASS / 0 FAIL**。
- 覆盖首次、重复／幂等、拒绝／撤回、恢复确认、原子失败与半成品清理、失败披露、刷新、关闭重开语义、键盘路径、三页导航与宽／窄屏。持久审计不适用：任务明确禁止持久化和审计运行时；操作日志只作为 Evidence。
- P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。

## Evidence 与只读完整性

- Manifest：`lifeos/engineering/LIFEOS-P3-091/evidence/MANIFEST.md`
- 结构化结果：`evidence/static_results.json`、`evidence/dynamic_results.json`
- 操作与验收：`evidence/operation_log.md`、`evidence/acceptance_matrix.md`
- 视觉：5 个 Chrome `file:` 宽／窄视图 JPEG；hash 均在 Manifest 中。
- 历史核对：P3-089 五项工程和 P3-090 attempt-2 Manifest hash 已复算并保留在 `evidence/historical_input_hashes.txt`，未被覆盖。

## 角色与关卡

- 主责：体验设计负责人；协审：AI 信任与安全负责人、技术架构负责人、产品架构负责人。
- Gate 1／3／4：有限合成 `file:` UI 范围内通过。Gate 2／5：N/A（未运行数据／来源能力，未接触外部用户）。
- 资产继续 **Not Frozen**；不关闭／重开风险、不恢复工程基线、不冻结资产、不进入 Stage 4。

## PM 决策

本包未触发新的用户确认或真实能力边界变化。需要 PM 按既定流程验收；若 PM Pass 且用户采纳，仍须创建一次全新隔离独立安全／体验复评。

## D-0370 窄 Rework｜动态 Evidence 闭环

初始提交的 UI 工程和静态检查未改动。本轮只在新的 task-local Chrome 副本补齐两项缺失的实际动态操作：

- 先建立已确认的合成页面状态，再关闭该标签页并在新标签页打开同一副本；重开后恢复为默认拒绝，输入、已确认显示、预览与回执均清除。
- 从页面起点实际按 `Tab` 聚焦 skip link，并按 `Enter`；本地 `file:` URL 变为 `#main-content`，页面仍保持默认拒绝和空输入关闭态。

闭环表与每项结构化结果、操作日志、视觉记录及 SHA-256 均位于 `evidence/rework/attempt-2/`；专用自检 runner 为 **2 PASS / 0 FAIL**。本轮计数：P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0。
