# LIFEOS-P3-083｜三张冻结今日页最小本地 UI 全新隔离独立安全／体验复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-082 当前 hash 的只读工程资产、只读 Evidence、非敏感固定文本与新建临时副本中进行防御性代码审查、独立体验／安全验证和本地回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、离线、失败与边界术语仅用于核验本项目内部防御性体验，不授权扩大范围。

## 状态、隔离与模型

- 状态：`Ready / Task-card Delivery Authorizes Execution`。用户将本任务卡路径发送到新建隔离 Codex 独立评审会话，即授权本卡范围内执行。
- 主责：新建隔离 Codex 独立安全／体验评审会话；不得复用 P3-082 工程执行、P3-082 PM 验收、P3-079／080 或 P3-081 的任何会话。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`high`。
- 允许降级：`gpt-5.6-luna` + `high`；后备：`gpt-5.5` + `xhigh`，须记录原因。
- 禁止降级／必须回报：P0/P1、Evidence 冲突、独立性不足、真实能力／数据范围扩大、网络／持久化／文件访问、Tauri/IPC、风险／冻结／基线／Stage 4 问题。

## 目标、输入与边界

独立核验 P3-082 当前 UI hash 是否在纯本地、无持久化、无网络、无文件访问的受控边界内正确实现：默认恢复、暂无可靠建议、权限受限／离线三态；显式确认保存、失败不伪报、刷新清除、AI 未启用，以及冻结原型的关键状态与信息层级。

- 只读输入：`lifeos/engineering/LIFEOS-P3-082/`、P3-082 交付物、PM Review、PM Evidence、P1-004／P1-009／P1-011 冻结设计输入、`CURRENT_STATUS.md`、`FREEZE_STATUS.md`、R-0013／R-0014／R-0015／R-0019／R-0021／R-0040、D-0337–D-0338 与独立评审模板。
- 允许写入：仅 `lifeos/reviews/LIFEOS-P3-083/`、本任务独立交付物、task-local 临时副本和本地预检报告。
- 禁止：修改 P3-082／冻结原型／历史工程、Review、Evidence 或账本；不得使用用户实际文本、真实个人文件／DB、浏览器持久存储、HTTP／WebSocket、网络、Tauri/IPC、Vault、云、导出、同步、多设备、L3 或外部用户；不得关闭／重开风险、恢复基线、冻结资产或进入 Stage 4。

## 独立验证与 Evidence

1. 新建独立浏览器检查脚本或手工验证矩阵；不得导入、调用或复制 P3-082 的 `tests/static_check.mjs` 作为主验证实现。
2. 在新的浏览器会话，以 `file:` 打开临时副本，使用固定非敏感文本独立覆盖：三态切换、确认保存、空文本、失败回执、无建议两条路径、权限受限／离线、AI 未启用与刷新清除。
3. 独立静态检查远程 URL、网络 API、HTTP 服务、Tauri/IPC、文件 API、`localStorage`／`indexedDB`／Cookie、导出、同步、模型调用和依赖安装均未实现。
4. 保留独立 runner／矩阵、逐项结构化结果、操作日志、视觉检查结论、hash、Manifest、复跑说明及“验收标准 → 反例 → Evidence”矩阵；核对 P3-082 当前 hash 和冻结设计输入未被覆盖。
5. 明确 P0、P1、P2、Unknown、Not Implemented 数量。若发现 P0/P1、明确合同违反、Evidence 冲突、独立性不足、越权、关闭态失效或影响完成定义的 Unknown／Not Implemented，必须判为 Rework 或 Blocked。

## 交付与关卡

- 交付物：`lifeos/deliverables/LIFEOS-P3-083_three_frozen_today_pages_minimal_local_ui_fresh_isolated_independent_re_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-083/independent_review.md`；Evidence Manifest：`lifeos/reviews/LIFEOS-P3-083/evidence/MANIFEST.md`。
- 首份会话报告必须记录任务卡路径、会话类型与接收时间，作为 D-0319 授权证据。
- Gate 1／3／4 仅检查有限 UI 前置边界；Gate 5 不在范围。即使 Pass，P3-082 仍 Not Frozen，不自动启用真实耐久、真实 AI／导出、网络、Tauri/IPC 或进入 Stage 4。
