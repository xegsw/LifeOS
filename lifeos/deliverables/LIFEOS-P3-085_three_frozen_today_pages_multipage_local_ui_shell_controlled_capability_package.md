# LIFEOS-P3-085｜三张冻结今日页多页本地 UI 壳受控能力包

## 任务、授权与范围

- [事实] 用户于 2026-08-21 20:53:40 CST 将任务卡路径投递到本新建隔离 Codex 工程执行会话；该投递构成任务卡范围内的执行授权。
- [事实] 实际配置为 Codex `gpt-5.6-terra` + high，未降级。
- [事实] 本包只新建 `lifeos/engineering/LIFEOS-P3-085/` 下的静态工程和指定交付物；未改项目账本、冻结 Stitch 原型、P3-082／084 工程、历史 Review／Evidence 或任何真实能力。
- [事实] 三张冻结设计输入仅作只读状态与层级参考。新工程不声称重新冻结原型，也不构成真实数据、保存、权限、AI、导出、同步、Stage 4 或 MVP 准入实现。

## 已实现的本地 UI 壳

- [事实] 已提供三个可独立作为 `file:` 入口的无依赖 HTML 页面：`default-recovery.html`、`no-reliable-suggestion.html`、`restricted-offline.html`。每页均有明确可见、非自动的相对本地导航，可到达另外两页。
- [事实] 默认恢复页将“当前 Project → 从这里继续 → 今日安排”置于主叙事。今日安排只显示“你已确认 · 行动”，并把 AI 明确标为“AI 未启用”。
- [事实] 默认页的快速捕获只保留当前 JavaScript 页面会话内的非敏感手动文本：空文本会拒绝；只有显式确认后的非空文本显示为“你的记录／原文”；模拟失败会清除已显示记录并披露未保留。源码没有使用浏览器持久化，因此刷新或关闭会清除该内容。
- [事实] 无建议页明确显示 Project 与证据缺口，不填充重点或候选；只提供“选择 Project”和“先记录当前停点”两条受控路径。
- [事实] 受限／离线页明确说明网络未使用、不联网不同步、外部来源与处理受限，且不读取来源、不处理内容、不生成建议；仍区分用户已确认行动和 AI 状态。

## 包内自检、Evidence 与异常披露

- [事实] 新写的 `tests/static_check.mjs` 只读取本工程三页、`app.js` 和 `styles.css`，没有导入、调用或复制 P3-082／084 runner。静态结果为 **37 PASS / 0 FAIL**，覆盖三个独立文档、相对本地导航、三态叙事、捕获规则，以及远程 URL、网络 API、浏览器持久化、文件 API、Tauri/IPC、导出、同步和模型标识的关闭态。
- [事实] 已在干净临时副本 `/private/tmp/lifeos-p3-085-i8Kwrv/app` 重跑该 runner，结果仍为 **37 PASS / 0 FAIL**。P3-082 的 `index.html`、`app.js`、`styles.css` 历史 hash 与 P3-082／084 Manifest 一致，未被覆盖。
- [事实] 受控图形浏览器在首次导航前因 URL 安全策略拒绝干净副本的 `file:` 地址，并明确禁止替代浏览器表面、间接执行、CDP 或其他规避。执行侧没有启动 HTTP 服务、访问网络、使用命令行浏览器或伪造动态截图。
- [事实] 因此动态的三页点击导航、首次／重复确认、空文本、模拟失败、无建议路径、刷新、关闭重开和视觉记录均为 **Not Implemented**，而非通过。阻断记录、操作日志、矩阵、静态结构化结果、hash 和复跑命令均已保留。
- [判断] 当前包内自检为 **Not Pass**：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=1。Not Implemented 覆盖任务卡强制要求的干净 `file:` 浏览器端到端演练与视觉 Evidence，影响完成定义，不能提交为 Pass。
- [事实] 已按项目规则调用本地预检；本地模型连接被运行环境拒绝，预检报告为 Skipped / Local Model Unavailable，未参与上述结论。

## 角色检查点与关卡

- [事实] 体验设计负责人视角：三态各自保留“今日从哪里继续”、可无建议与不打扰的降级叙事；未使用运维、KPI 或全局任务墙表达。
- [事实] 产品架构负责人协审：页面保持个人项目恢复入口，未扩大为企业后台或自动决定用户行动。
- [事实] AI 信任与安全负责人协审：AI 在三页均显式关闭；捕获文本仅以用户原文身份显示，且必须经用户确认；受限／离线时 fail-closed。
- [事实] 技术架构负责人视角：本工程是相对本地资源的静态壳，无网络、持久化、真实文件、DB、Vault、Tauri/IPC、外部依赖或服务；静态关闭态可复查。
- [判断] Gate 1／3／4 只在静态、本地 UI 前置范围完成 **Partial** 覆盖；因为动态 `file:` 演练未完成，不可宣称完整通过。Gate 2、Gate 5 不作运行时批准。

## 风险、待确认与建议

- [事实] 未触发风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实数据／路径、真实文件、云／第三方、同步、多设备、L3、外部用户或 Stage 4。
- [建议｜需 PM 确认] 若要完成本能力包，应在不扩大边界的前提下，提供一个被当前执行环境允许、可直接打开 `file:` 干净副本的合规图形浏览器验证表面；随后在同一任务卡范围内重跑完整动态矩阵、视觉记录、hash 和 Manifest。不得以 HTTP 服务、网络、CDP、命令行浏览器或伪造 Evidence 替代。
- [待确认] 本执行会话无权将这一受限浏览器策略视为完成，也无权启动后续或独立评审任务。

## Evidence 入口

- 工程与静态 runner：`lifeos/engineering/LIFEOS-P3-085/`。
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-085/evidence/MANIFEST.md`。
- 阻断记录：`lifeos/engineering/LIFEOS-P3-085/evidence/browser_blocker.md`。
- 验收矩阵：`lifeos/engineering/LIFEOS-P3-085/evidence/acceptance_matrix.md`。
