# LIFEOS-P3-084 Rework｜Chrome `file:` 动态 Evidence 一次性授权重跑

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务只在 P3-082 当前只读 UI 源码、干净 task-local 临时副本、固定非敏感文本和本机 Google Chrome 图形界面内进行防御性本地 UI 验证。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。不得将浏览器操作扩展为服务启动、网络访问或规避安全策略。

## 本次重跑的唯一目标

完成 P3-084 上次遗漏的独立动态验证。**唯一允许的验证表面是本机 Google Chrome 的新图形化窗口／标签页，以 `file:` 打开干净临时副本。**不得再以 Codex In-app Browser 的 `file:` 结果判断环境可用性，也不得启动 HTTP 服务、使用 CDP、命令行浏览器或其他替代路径。

## 状态、隔离与模型

- 状态：`Rework / Task-card Delivery Authorizes Execution`。
- 会话：必须新建隔离 Codex 独立安全／体验评审会话；不得复用 P3-082、P3-083、P3-084 首轮或 PM 会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`；允许降级：None；后备：`gpt-5.5` + `xhigh`，仅首选不可用时记录原因。
- 禁止降级／必须回报：P0/P1、Evidence 冲突、独立性不足、Chrome 无法打开 `file:`、任何网络／持久化／文件 API／Tauri/IPC／真实能力触达。
- 允许写入：仅 `lifeos/reviews/LIFEOS-P3-084/rework/`、rework 交付物、task-local 临时副本与本地预检报告。
- 禁止：修改 P3-082 工程、任何历史 Evidence／Review／账本、冻结资产、关闭／重开风险、恢复基线、启用真实能力或进入 Stage 4。

## 必须读取

`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、P3-084 原任务卡／交付物／独立 Review／PM Review／Evidence、P3-082 PM Review 与工程 Evidence Manifest；并按独立 P0 复评要求读取 `PM_OPERATING_MODEL.md` 的独立评审和受控能力包章节、`ROLE_MATRIX.md`、`STAGE_GATES.md`。

## 动态矩阵与完成定义

1. 先复算 P3-082 `index.html`、`app.js`、`styles.css` hash，并复制到新的干净临时目录。
2. 在新 Chrome 窗口／标签页打开 `file:///…/index.html`；只使用固定非敏感文本。
3. 完整验证并保存逐项结构化结果、操作日志与可复查视觉记录：三态切换；非空文本显式确认；空文本拒绝；模拟失败不展示记录；无建议两条路径；权限受限／离线与 AI 未启用；刷新；关闭后重新打开。
4. 每一步都核对“仅当前页面会话、刷新／关闭清除、不联网、AI 未启用”；不得输入真实用户内容。
5. 新写独立动态／静态核验逻辑；不得导入、调用或复制 P3-082／083／084 首轮 runner 作为主验证。
6. 写入新的 `MANIFEST.md`、验收矩阵、runner、逐项结果、操作日志、视觉记录、hash 与复跑说明。

若 Chrome 的受控 `file:` 页面仍无法打开，记录实际阻断和 Chrome 版本／窗口状态，但不得尝试 HTTP、CDP、命令行或其他绕过；此时可判 Blocked。若 Chrome 可用却任一动态行为失败，判 Rework；不得以静态 PASS 替代动态结果。

## 交付与边界

- 独立 Review：`lifeos/reviews/LIFEOS-P3-084/rework/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-084/rework/evidence/MANIFEST.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-084/rework/three_frozen_today_pages_file_dynamic_evidence_independent_re_review.md`
- 首份会话报告记录本卡路径、会话类型与接收时间；完成后用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 简短回复。
- 即使 Pass，P3-082 仍 Not Frozen；不得自动关闭风险、恢复基线、冻结资产或进入 Stage 4。
