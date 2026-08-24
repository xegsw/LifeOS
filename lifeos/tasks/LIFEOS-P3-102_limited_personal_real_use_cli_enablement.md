# LIFEOS-P3-102｜CLI-only 有限本人真实使用启用

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已明确确认：只处理其在专项会话主动手工输入的一条低敏感短文本；只创建 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`、其中全新 `capture.sqlite` 和固定 `today.html`；只允许 `capture`、`today`、`render`，禁止 `clear`；首轮保留 DB 和页面，任何删除另行逐次确认。R-0051 保持原有限关闭，R-0052 跟踪真实使用扩展。禁止既有个人 DB、任意路径扫描、Vault、Tauri/IPC、真实文件导出、网络、云／第三方、同步、多设备、L3、外部用户及凭据。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-102`
- 任务名称：CLI-only 有限本人真实使用启用
- 优先级：P0
- 任务类型：真实能力启用前的受控能力包；不适用 P3 Engineering Fast Lane。
- 是否为受控能力包：Yes。
- 唯一风险边界：仅把固定 P3-097 CLI candidate 扩展到一个精确新目录／新 DB 和用户手工输入的低敏感短文本；对应新风险为 R-0052。
- 包内允许工作：只读固定 candidate；在最终确认的精确目录执行获准 CLI 入口；建立首次、重复／幂等、关闭重启、失败关闭、审计、页面与退出状态 Evidence；不得修改 candidate 代码。
- 包内整改授权：仅限 P3-102 自身 runner／Evidence／文案和同一精确目录的受控操作；任何代码修复、入口增加或边界扩大必须停止并新建任务。
- 推荐 Agent：Codex 新建隔离工程／真实能力验证会话。
- 推荐模型／推理强度：`gpt-5.6-terra` / `xhigh`。
- 模型理由：真实个人数据、真实路径、SQLite 生命周期和失败关闭属于 P0 边界。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选不可用则 Blocked。
- 后备模型：None。
- 是否需要后续独立评审：Yes；工程／执行会话不得自评真实能力启用结论。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责：受控本地运行与数据生命周期工程；协审：数据／领域、AI 信任安全、独立 QA、产品体验。
- 关卡：Gate 1、Gate 3、Gate 4；Gate 5 只收集本人使用事实，不作阶段通过。
- 状态：Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery。
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-102-v1`
- ABF SHA-256：`361849606a9164ad0ffc215688084a466dd6495ff5589719591773bcdc40a243`
- 正式 Rework：0/2。

## 已确认边界

- 输入：仅用户主动手工输入的低敏感短文本；不得包含凭据、密钥、身份号码、支付信息、健康／医疗、法律、财务、高敏感关系信息、第三方秘密或其他敏感个人材料。
- 存储：仅一个全新专用目录，以及其中全新 `capture.sqlite` 和固定 `today.html`；不得读取、迁移、复制或连接既有个人 DB。
- 入口：CLI-only；Tauri/IPC 及所有外部能力保持关闭。
- 风险：R-0051 原有限关闭不变；R-0052 作为真实使用扩展风险保持 P0 / Open。
- 不冻结、不恢复工程基线、不进入 Stage 4。

## 已冻结的真实使用边界

- 专用目录：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`；PM 于冻结前只读确认目标不存在，祖先链均为真实目录而非符号链接。
- DB／页面：仅 `<专用目录>/capture.sqlite` 与 `<专用目录>/today.html`，执行前均须不存在。
- CLI：仅 `capture`、`today`、`render`；`clear` 禁止，任何删除或清理必须取得新的逐次用户确认。
- 保留：首轮结束保留精确目录、DB 和页面；不得把保留状态当成待清理临时残留。
- 用户输入：专项会话必须先请求用户主动提供并确认一条低敏感短文本和幂等 key；不得替用户生成“真实输入”，不得把原文写入 Evidence 或摘要。
- 投递授权：用户把本任务卡绝对路径发送至新建隔离 Codex 工程／真实能力验证会话，即授权在上述 Frozen 边界内执行；首个真实 capture 仍必须等用户在该会话主动提供低敏感文本。

## 最小启动包与高风险补读

完整读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、Frozen 后的 ABF、`lifeos/ACCEPTANCE_GOVERNANCE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：真实能力、用户确认、风险与独立评审章节。
- `lifeos/ROLE_MATRIX.md`：PM、工程、数据／领域、AI 信任安全、独立 QA 职责。
- `lifeos/STAGE_GATES.md`：Gate 1、3、4、5 与 Stage 3→4。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- `lifeos/DECISION_LOG.md`：D-0406 至 D-0418。
- `lifeos/reviews/LIFEOS-P3-097_pm_review.md`、`lifeos/reviews/LIFEOS-P3-098_pm_review.md`、`lifeos/reviews/LIFEOS-P3-100_pm_review.md`、`lifeos/reviews/LIFEOS-P3-101/resume-1/pm_review.md`。
- P3-097 固定 candidate 与当前 Engineering/PM Manifest；严格只读。

## 预定交付与 Evidence

- 交付物：`lifeos/deliverables/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md`
- Engineering Evidence：`lifeos/engineering/LIFEOS-P3-102/evidence/`
- Evidence 不得复制或泄露用户输入原文；只允许记录长度区间、用户确认的低敏感分类、内容 hash、状态、计数、时间、路径边界结果及必要的脱敏截图／日志。
- ABF 已 Frozen；执行侧必须逐行完成 12 项矩阵，不得修改或解释扩张。

## 执行与停止条件

- 必须新建隔离 Codex 工程／真实能力验证会话；不得复用 P3-097 工程、P3-098 独立评审、P3-100 风险判断或 P3-101 治理会话。
- 在任务卡投递和用户主动提供低敏感文本前，不得创建专用目录、DB、页面或运行 capture。
- 发现目标已存在、祖先链接、candidate hash 变化、需要 `clear`、Evidence 无法脱敏或任何范围扩大时，必须在变更前停止。
- 不得关闭／重开 R-0040 或 R-0051；R-0052 保持 Open。
- 不得修改 candidate、历史 Evidence、冻结、基线或阶段；完成后必须等待 PM 验收、用户采纳和全新隔离独立复评。
