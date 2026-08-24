# LIFEOS-P3-103｜P3-102 有限真实使用全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-102 PM Pass，授权创建本全新隔离独立复评，并同意仅对精确 retained DB 做只读、内存内原文 SHA-256 比对。任务仅用于验证本人项目的本地数据身份、生命周期、失败关闭、路径约束、Evidence 隐私和保留边界。不得输出原文、幂等 key、内容 hash、DB hash、DB／页面副本或页面正文；不得访问网络、云、第三方、凭据、外部目标或其他个人文件，不扩大攻击能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-103`
- 任务名称：P3-102 有限真实使用全新隔离独立复评
- 优先级：P0
- 任务类型：全新隔离独立安全／数据生命周期／Evidence 复评
- 是否为受控能力包：Yes；唯一风险边界是对 P3-102 精确 retained 资产作最小只读核验，并以固定非敏感夹具独立复跑同一 CLI 生命周期。
- 包内允许工作：独立测试设计、只读核验、固定非敏感复跑、失败／路径反例、Evidence／Manifest 和独立 Review。
- 包内整改授权：仅限 P3-103 自身 runner、Evidence、Review 和交付文案；不得修改候选、P3-102、真实资产、项目账本或 ABF。
- 必须拆分：候选修复、真实资产清理、页面正文读取、key 读取、路径／数据／入口扩大、Tauri/IPC、风险关闭／重开、基线恢复、Schema/API／资产冻结和 Stage 4。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 独立评审。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型理由：涉及真实个人低敏感数据、SQLite 只读核验、失败关闭、路径边界、Evidence 隐私和 P0 最终判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选配置不可用时停止并回报 PM。
- 后备模型：None。
- 是否需要后续独立评审：No；本任务本身即独立复评，完成后仍须 PM 验收和用户采纳。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／安全与数据生命周期评审。
- 协审角色：数据／领域模型、AI 信任安全、受控本地运行、产品体验。
- 评审关卡：Gate 1、Gate 3、Gate 4；Gate 5 仅核对既有本人目视确认，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-103_p3_102_limited_real_use_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-103-v1`
- ABF SHA-256：`45a74cd9496cea0576ccd0257115e7e9e54821ee0d3be0639eda57f35e9e52f0`
- 正式 Rework：0/2。
- 生效决策：D-0421。

## 会话路由与执行授权

- 必须新建全新隔离 Codex 独立评审会话。
- 禁止复用 P3-102 工程／真实能力验证会话、本 PM 主会话，以及任何参与 P3-102 runner、Evidence 或 PM 验收设计的会话。
- 用户将本任务卡绝对路径投递至符合隔离条件的新会话时，即授权执行本卡 Frozen ABF 范围，无需重复口令。
- 用户已在 D-0421 完成投递前真实 retained DB 最小只读核验授权；投递不授权任何额外真实读取或写入。
- 首份会话报告必须记录任务卡路径、ABF 路径／ID／hash、会话类型、接收时间、实际模型／推理强度、独立性声明和是否存在歧义。
- 无法证明独立性、需要扩大真实读取、固定 hash 漂移或 ABF 有歧义时，必须在读取真实 DB 或创建夹具前停止。

## 最小启动包与高风险定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. Frozen ABF
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
7. `lifeos/ACCEPTANCE_GOVERNANCE.md`
8. `lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md`
9. `lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement_acceptance_basis_freeze.md`
10. `lifeos/deliverables/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md`
11. `lifeos/reviews/LIFEOS-P3-102_pm_review.md`
12. `lifeos/engineering/LIFEOS-P3-102/evidence/MANIFEST.md`
13. `lifeos/reviews/LIFEOS-P3-102/pm_evidence/initial/MANIFEST.md`

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：P0、真实能力、用户确认、独立评审、两层验收和 Evidence 章节。
- `lifeos/ROLE_MATRIX.md`：PM、独立 QA、工程、数据／领域和 AI 信任安全职责。
- `lifeos/STAGE_GATES.md`：Gate 1、3、4、5 与 Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0414、D-0417 至 D-0421。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- P3-097 固定 candidate、P3-102 Engineering/PM Evidence 与其引用的历史资产，严格只读。

仅在发现账本冲突时定向补读，不全文重读无关历史。

## 独立性顺序

1. 只根据任务卡、Frozen ABF、交付物合同和提交结果形成独立测试设计。
2. 将测试设计、fixture 规范和预期断言写入 P3-103 Evidence 并固定 SHA-256。
3. 之后才可定向读取 P3-097 candidate 源码作静态反查。
4. P3-102 `runner.py` 只允许复算 hash；不得导入、执行、复制、改写或据其内部实现设计测试。
5. 不得用 P3-102 的 12/12 或 PM 的 6/6 替代独立动作。

## 真实 retained 资产访问规则

- 先 lstat 唯一目录、全部祖先、DB 和页面，确认路径／类型／权限／nlink 与 ABF 一致；只允许列出精确目录中的固定文件名。
- 在任何真实 DB 查询前记录目录／DB／页面 lstat metadata、允许文件名、sidecar 不存在和非内容结构事实；不得读取或哈希 DB 文件整体。
- 仅通过 SQLite URI `mode=ro&immutable=1` 打开 DB，并立即设置 `PRAGMA query_only=ON`；不得使用普通读写连接，不得执行会写入或可能生成 journal/WAL 的语句。
- 原文只允许在单个最小作用域内短暂存在，用于内存 SHA-256；只把 `match=true/false` 与记录数写入 Evidence，不得记录期望值或实际 hash。
- 不得选择、读取、输出或哈希幂等 key；SQL、异常和日志不得携带原文或 key。
- Schema/source/audit/count/time 核验必须只选择非内容字段；禁止 SQL dump、数据库副本、备份或页面读取。
- 页面只核对 lstat metadata、固定文件名、提交 Evidence 和既有用户目视确认；不得打开、截图、哈希或解析正文。
- 查询结束立即关闭连接、丢弃原文对象并核对无 journal/WAL/SHM/sidecar。
- 核验结束比较 metadata、文件名和非内容结构事实；必须不变。Evidence 只写 `unchanged=true/false`。

## 固定非敏感独立复跑

- 仅在全新 `/private/tmp/lifeos-p3-103-*` 目录使用固定、显著非敏感文本和全新 SQLite／HTML／哨兵。
- 新写 runner 独立覆盖：首次 saved、同 key 同文本 repeat、同 key 异文本冲突、关闭重启 today、render、注入失败。
- 独立覆盖：路径规范化、祖先／最终符号链接、hardlink、FIFO／目录、外部输出和失败前后哨兵／DB／页面不变。
- 不调用 `clear`；不得访问真实内容或把真实输入复制到夹具。
- runner 必须对缺行、重复 ID、缺断言、泄密字段和不可复核结果作负门并非零退出。
- 所有临时目录在 Evidence 落盘后精确清理；不得把 SQLite、HTML、pyc、缓存或临时 DB 带入 Evidence。

## 允许修改

只允许新建并修改：

- `lifeos/deliverables/LIFEOS-P3-103_p3_102_limited_real_use_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-103/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-103/evidence/`

不得创建 `lifeos/engineering/LIFEOS-P3-103/`；全部项目账本和 P3-097/P3-102 资产只读。

## 交付与 Evidence

- 独立 Review：`lifeos/reviews/LIFEOS-P3-103/independent_review.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-103_p3_102_limited_real_use_fresh_isolated_independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-103/evidence/MANIFEST.md`
- 至少保存：冻结后的独立测试设计、独立 runner 源码、12 行结构化矩阵、唯一 test／fixture／execution ID、真实 retained 脱敏核验、固定非敏感生命周期／边界结果、Evidence 负门、hash 保全、隐私扫描、关闭能力、清理结果、操作日志、复跑说明和非自指 Manifest。
- Evidence 不得含真实原文、key、内容 hash、DB hash、页面正文／hash、DB／HTML 副本、SQL dump、截图或真实内容衍生片段。
- 本地模型预检可因 P0 真实数据最终判断跳过；必须在 Review 写明理由。

## 验收结论与回退

- 结论只可为 Pass / Rework / Blocked；不得以条件性措辞掩盖 Unknown 或 Not Implemented。
- Pass 条件：Frozen ABF 12 项不变量和 12 行矩阵及全部子项独立通过；P0/P1/P2/Unknown/Not Implemented 全零；固定输入／Manifest 前后一致；真实 retained 资产不变；隐私扫描和临时残留均为零。
- 评审自身 Evidence 缺陷可在不改变 ABF、独立性、读取边界、固定输入、候选或真实资产的前提下原任务 Rework，最多两轮。
- 发现候选／真实执行 P0/P1、Evidence 冲突、隐私泄露或完成定义缺口：结论 Rework，将 P3-102 返回同一能力包；评审会话不得修复。
- 独立性不足、固定 hash 不明漂移、授权内无法安全读取或环境不可执行：Blocked。
- 即使 Pass，也不关闭 R-0052、不冻结、不恢复基线、不创建三页运行时整合任务、不进入 Stage 4；必须先等待 PM 验收和用户采纳。

## 聊天回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出：独立结论；ABF/hash；真实 retained 核验与隐私摘要；固定非敏感复跑；P0/P1/P2/Unknown/Not Implemented；资产与 R-0052 状态；下一步许可；Review／Evidence 路径；需要 PM 确认事项。
